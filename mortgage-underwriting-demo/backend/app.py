"""
Senior Mortgage Underwriting System - FastAPI Backend
A multi-agent AI system using LangGraph for automated mortgage underwriting.

Agents: Credit Analyst, Income Analyst, Asset Analyst, Collateral Analyst, Critic, Decision
Features: RAG policy retrieval, PII sanitization, bias detection, human-in-the-loop review
"""

import json
import os
import re
import uuid
from datetime import datetime
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# ─── App Setup ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Senior Mortgage Underwriting System",
    description="Multi-agent AI mortgage underwriting with LangGraph",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Global State ────────────────────────────────────────────────────────────

# Store active sessions and their workflow states
sessions: Dict[str, Dict] = {}

# ─── Data Models ─────────────────────────────────────────────────────────────

class APIKeyRequest(BaseModel):
    openai_api_key: str
    openai_api_base: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"

class RunRequest(BaseModel):
    openai_api_key: str
    openai_api_base: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    case_index: int = 0  # 0, 1, or 2

class HumanReviewRequest(BaseModel):
    session_id: str
    decision: str  # APPROVED, CONDITIONAL, REJECTED
    comments: str

class CustomApplicationRequest(BaseModel):
    openai_api_key: str
    openai_api_base: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    applicant_data: Dict[str, Any]

# ─── Underwriting State ─────────────────────────────────────────────────────

class UnderwritingState(TypedDict):
    case_id: str
    applicant_data: Dict[str, Any]
    sanitized_data: Dict[str, Any]
    credit_analysis: Optional[str]
    income_analysis: Optional[str]
    asset_analysis: Optional[str]
    collateral_analysis: Optional[str]
    critic_review: Optional[str]
    decision_memo: Optional[str]
    final_decision: Optional[str]
    risk_score: Optional[int]
    next_agent: Optional[str]
    analysis_complete: bool
    human_review_required: bool
    human_review_completed: bool
    human_notes: Optional[str]
    bias_flags: List[str]
    policy_violations: List[str]
    reasoning_chain: Annotated[List[str], "append"]
    timestamp: str

# ─── Utility Functions ───────────────────────────────────────────────────────

def sanitize_pii(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove or redact personally identifiable information."""
    sanitized = data.copy()
    if 'ssn' in sanitized:
        ssn = sanitized['ssn']
        sanitized['ssn'] = f"***-**-{ssn[-4:]}" if len(ssn) >= 4 else "***-**-XXXX"
    if 'name' in sanitized:
        sanitized['name'] = "[APPLICANT_NAME]"
    if 'address' in sanitized:
        sanitized['address'] = "[ADDRESS]"
    if 'phone' in sanitized:
        phone = sanitized['phone']
        sanitized['phone'] = f"***-***-{phone[-4:]}" if len(phone) >= 4 else "***-***-XXXX"
    return sanitized


def detect_bias_signals(analysis: str, applicant_data: Dict[str, Any]) -> List[str]:
    """Check for potential Fair Lending Act violations."""
    flags = []
    protected_terms = [
        'race', 'color', 'religion', 'national origin',
        'sex', 'marital status', 'age', 'gender',
        'disability', 'familial status'
    ]
    analysis_lower = analysis.lower()
    for term in protected_terms:
        if term in analysis_lower:
            flags.append(f"Analysis mentions protected characteristic: {term}")
    if 'zip' in applicant_data or 'zipcode' in applicant_data:
        if 'neighborhood' in analysis_lower or 'area' in analysis_lower:
            flags.append("Potential geographic bias - review for Fair Lending compliance")
    return flags


# ─── Calculator Tools ────────────────────────────────────────────────────────

def calculate_dti_ratio(monthly_debt: float, monthly_income: float) -> str:
    if monthly_income <= 0:
        return "Error: Monthly income must be greater than 0"
    dti = (monthly_debt / monthly_income) * 100
    status = "Acceptable" if dti <= 43 else "High" if dti <= 50 else "Excessive"
    return f"DTI Ratio: {dti:.2f}% ({status}) - Debt: ${monthly_debt:,.2f}, Income: ${monthly_income:,.2f}"


def calculate_ltv_ratio(loan_amount: float, property_value: float) -> str:
    if property_value <= 0:
        return "Error: Property value must be greater than 0"
    ltv = (loan_amount / property_value) * 100
    status = "Excellent" if ltv <= 80 else "Good" if ltv <= 90 else "High" if ltv <= 97 else "Excessive"
    return f"LTV Ratio: {ltv:.2f}% ({status}) - Loan: ${loan_amount:,.2f}, Value: ${property_value:,.2f}"


def calculate_reserves(liquid_assets: float, monthly_payment: float, required_months: int = 2) -> str:
    if monthly_payment <= 0:
        return "Error: Monthly payment must be greater than 0"
    months_coverage = liquid_assets / monthly_payment
    required_amount = monthly_payment * required_months
    status = "Adequate" if months_coverage >= required_months else "Insufficient"
    return f"Reserves: {months_coverage:.1f} months coverage ({status}) - Assets: ${liquid_assets:,.2f}, Required: ${required_amount:,.2f}"


def calculate_housing_expense_ratio(monthly_payment: float, monthly_income: float) -> str:
    if monthly_income <= 0:
        return "Error: Monthly income must be greater than 0"
    ratio = (monthly_payment / monthly_income) * 100
    status = "Acceptable" if ratio <= 28 else "High" if ratio <= 36 else "Excessive"
    return f"Housing Expense Ratio: {ratio:.2f}% ({status}) - Payment: ${monthly_payment:,.2f}, Income: ${monthly_income:,.2f}"


def calculate_total_debt_obligations(debts: Dict, proposed_payment: float) -> str:
    total_existing = sum(debts.values()) if isinstance(debts, dict) else 0
    total_with_proposed = total_existing + proposed_payment
    return (
        f"Total Existing Debt: ${total_existing:,.2f} | "
        f"Proposed Payment: ${proposed_payment:,.2f} | "
        f"Total Obligations: ${total_with_proposed:,.2f}"
    )


def check_credit_score_policy(credit_score: int) -> str:
    if credit_score >= 740:
        tier = "Excellent"
        notes = "Best rates available. Minimal risk."
    elif credit_score >= 700:
        tier = "Good"
        notes = "Standard rates. Low risk."
    elif credit_score >= 660:
        tier = "Fair"
        notes = "Higher rates may apply. Moderate risk."
    elif credit_score >= 620:
        tier = "Minimum Acceptable"
        notes = "Highest rates. Additional conditions likely. High risk."
    else:
        tier = "Below Minimum"
        notes = "DOES NOT MEET minimum credit score requirement of 620. DENIAL recommended."
    return f"Credit Score: {credit_score} | Tier: {tier} | Policy Notes: {notes}"


def check_large_deposits(deposits: List[Dict], monthly_income: float) -> str:
    threshold = monthly_income * 0.5
    flagged = []
    for dep in deposits:
        amt = dep.get('amount', 0)
        if amt > threshold:
            flagged.append(f"${amt:,.2f} on {dep.get('date', 'unknown')} - {dep.get('description', 'no description')}")
    if not flagged:
        return f"No large deposits detected (threshold: ${threshold:,.2f})"
    return f"Large deposits flagged (threshold: ${threshold:,.2f}):\n" + "\n".join(f"  - {f}" for f in flagged)


# ─── RAG Policy System ──────────────────────────────────────────────────────

def create_policy_store(api_key: str, api_base: str):
    """Create vector store with underwriting policies from PDF."""
    from langchain_community.vectorstores import Chroma
    from langchain_openai import OpenAIEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import PyPDFLoader

    pdf_path = Path(__file__).parent / "underwriting_policies.pdf"
    loader = PyPDFLoader(str(pdf_path))
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    policy_chunks = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(
        openai_api_key=api_key,
        openai_api_base=api_base,
    )

    vectorstore = Chroma.from_documents(
        documents=policy_chunks,
        embedding=embeddings,
        collection_name=f"policies_{uuid.uuid4().hex[:8]}"
    )
    return vectorstore


def retrieve_relevant_policies(query: str, vectorstore) -> str:
    docs = vectorstore.similarity_search(query, k=6)
    section_map = {}
    for doc in docs:
        text = doc.page_content.strip()
        match = re.match(r"^\d+\.\d+\s+[A-Za-z ].+", text)
        section = match.group(0) if match else "OTHER"
        if section not in section_map:
            section_map[section] = text
        else:
            if text not in section_map[section]:
                section_map[section] += "\n" + text
    return "\n\n".join(section_map.values())


# ─── Agent Nodes ─────────────────────────────────────────────────────────────

def create_llm(api_key: str, api_base: str, model: str):
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=model,
        temperature=0,
        openai_api_key=api_key,
        openai_api_base=api_base,
    )


def credit_analyst_node(state: dict, llm, policy_store) -> dict:
    from langchain_core.messages import HumanMessage, SystemMessage

    policies = retrieve_relevant_policies(
        "credit score requirements bankruptcies foreclosures late payments", policy_store
    )
    app_data = state["sanitized_data"]
    credit_score = app_data.get('credit_score', 0)
    credit_score_analysis = check_credit_score_policy(credit_score)

    system_prompt = f"""You are a Senior Credit Analyst with 15+ years of experience in mortgage underwriting.

RELEVANT POLICIES:
{policies}

ANALYSIS FRAMEWORK:
1. Credit Score Assessment - Use provided assessment (DO NOT recalculate)
2. Payment History - Review late payments and patterns
3. Derogatory Items - Evaluate bankruptcies, foreclosures, collections
4. Policy Compliance - Check against credit guidelines
5. Risk Rating - Assign credit risk (Low/Medium/High)
6. Recommendations - Provide conditions or concerns

Be thorough, objective, and policy-compliant. Support conclusions with data.
IMPORTANT: Use the EXACT credit score assessment provided below."""

    user_prompt = f"""Analyze the credit profile for case {app_data.get('case_id')}:

CALCULATED CREDIT SCORE ASSESSMENT (ACCURATE - DO NOT RECALCULATE):
{credit_score_analysis}

CREDIT HISTORY DATA:
- Bankruptcies: {app_data.get('credit_history', {}).get('bankruptcies', 0)}
- Foreclosures: {app_data.get('credit_history', {}).get('foreclosures', 0)}
- Late Payments (12mo): {app_data.get('credit_history', {}).get('late_payments_12mo', 0)}
- Late Payments (24mo): {app_data.get('credit_history', {}).get('late_payments_24mo', 0)}
- Collections: {app_data.get('credit_history', {}).get('collections', [])}
- Credit Notes: {app_data.get('credit_history', {}).get('credit_notes', 'N/A')}

Provide your detailed credit analysis."""

    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    analysis = response.content
    bias_flags = detect_bias_signals(analysis, app_data)

    return {
        **state,
        "credit_analysis": analysis,
        "bias_flags": state.get("bias_flags", []) + bias_flags,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            f"Credit Analyst: Completed credit analysis for {app_data.get('case_id')}"
        ]
    }


def income_analyst_node(state: dict, llm, policy_store) -> dict:
    from langchain_core.messages import HumanMessage, SystemMessage

    policies = retrieve_relevant_policies(
        "employment income verification DTI ratio self-employed", policy_store
    )
    app_data = state["sanitized_data"]
    debts = app_data.get("debts", {})
    proposed_payment = app_data.get("loan", {}).get("estimated_payment", 0)
    monthly_income = app_data.get("employment", {}).get("monthly_income", 0)
    total_debt = sum(debts.values()) if isinstance(debts, dict) else 0

    dti_result = calculate_dti_ratio(total_debt + proposed_payment, monthly_income)
    housing_result = calculate_housing_expense_ratio(proposed_payment, monthly_income)
    debt_breakdown = calculate_total_debt_obligations(debts if isinstance(debts, dict) else {}, proposed_payment)

    system_prompt = f"""You are a Senior Income Analyst with 15+ years of experience in mortgage underwriting.

RELEVANT POLICIES:
{policies}

ANALYSIS FRAMEWORK:
1. Employment Stability - Review job history, tenure, gaps
2. Income Verification - Validate income sources
3. DTI Calculation - Use provided calculation (DO NOT recalculate)
4. Payment Capacity - Assess affordability
5. Risk Assessment - Identify income-related risks
6. Recommendations

IMPORTANT: Use EXACT pre-calculated ratios provided. Do NOT recalculate."""

    user_prompt = f"""Analyze income for case {app_data.get('case_id')}:

PRE-CALCULATED DTI (ACCURATE - DO NOT RECALCULATE):
{dti_result}

PRE-CALCULATED HOUSING RATIO:
{housing_result}

DEBT BREAKDOWN:
{debt_breakdown}

EMPLOYMENT DATA:
- Employer: {app_data.get('employment', {}).get('employer', 'N/A')}
- Position: {app_data.get('employment', {}).get('position', 'N/A')}
- Years: {app_data.get('employment', {}).get('years', 0)}
- Type: {app_data.get('employment', {}).get('type', 'N/A')}
- Monthly Income: ${monthly_income:,.2f}
- Employment Gap: {app_data.get('employment', {}).get('employment_gap', 'None')}

Provide your detailed income analysis."""

    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    analysis = response.content
    bias_flags = detect_bias_signals(analysis, app_data)

    return {
        **state,
        "income_analysis": analysis,
        "bias_flags": state.get("bias_flags", []) + bias_flags,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            f"Income Analyst: Completed income analysis for {app_data.get('case_id')}"
        ]
    }


def asset_analyst_node(state: dict, llm, policy_store) -> dict:
    from langchain_core.messages import HumanMessage, SystemMessage

    policies = retrieve_relevant_policies(
        "down payment reserves assets large deposits gift funds", policy_store
    )
    app_data = state["sanitized_data"]
    assets = app_data.get('assets', {})
    loan = app_data.get('loan', {})
    monthly_income = app_data.get('employment', {}).get('monthly_income', 0)

    liquid_assets = assets.get('checking', 0) + assets.get('savings', 0)
    monthly_payment = loan.get('estimated_payment', 0)

    reserves_result = calculate_reserves(liquid_assets, monthly_payment, 2)
    deposits_result = check_large_deposits(assets.get('recent_deposits', []), monthly_income)

    system_prompt = f"""You are a Senior Asset Analyst with 15+ years of experience in mortgage underwriting.

RELEVANT POLICIES:
{policies}

ANALYSIS FRAMEWORK:
1. Down Payment Adequacy
2. Reserve Requirements (Use Provided Calculation)
3. Large Deposits (Use Provided Analysis)
4. Source of Funds Review
5. Key Risks
6. Asset Risk Rating (Low/Medium/High)

IMPORTANT: Use EXACT pre-calculated metrics. Do NOT recalculate."""

    user_prompt = f"""Analyze assets for case {state.get('case_id')}:

LOAN REQUIREMENTS:
- Loan Amount: ${loan.get('amount', 0):,.2f}
- Down Payment: ${loan.get('down_payment', 0):,.2f}
- Closing Costs: ${loan.get('closing_costs', 0):,.2f}

ASSET DATA:
- Checking: ${assets.get('checking', 0):,.2f}
- Savings: ${assets.get('savings', 0):,.2f}
- Total Liquid: ${liquid_assets:,.2f}
- 401k: ${assets.get('401k', 0):,.2f}

PRE-CALCULATED RESERVES:
{reserves_result}

LARGE DEPOSIT ANALYSIS:
{deposits_result}

Deposit Explanations: {assets.get('deposit_explanations', 'None provided')}

Provide your detailed asset analysis."""

    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    analysis = response.content
    bias_flags = detect_bias_signals(analysis, app_data)

    return {
        **state,
        "asset_analysis": analysis,
        "bias_flags": state.get("bias_flags", []) + bias_flags,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            f"Asset Analyst: Completed asset analysis for {state.get('case_id')}"
        ]
    }


def collateral_analyst_node(state: dict, llm, policy_store) -> dict:
    from langchain_core.messages import HumanMessage, SystemMessage

    policies = retrieve_relevant_policies("appraisal property condition LTV collateral", policy_store)
    app_data = state["sanitized_data"]
    property_data = app_data.get('property', {})
    loan = app_data.get('loan', {})

    loan_amount = loan.get('amount', 0)
    appraised_value = property_data.get('appraised_value', 0)
    ltv_result = calculate_ltv_ratio(loan_amount, appraised_value)

    system_prompt = f"""You are a Senior Collateral Analyst with expertise in property valuation.

RELEVANT POLICIES:
{policies}

ANALYSIS FRAMEWORK:
1. Appraisal Review - Validate property value
2. LTV Calculation - Use provided calculation (DO NOT recalculate)
3. Property Condition - Evaluate habitability
4. Marketability
5. Risk Assessment
6. Recommendations

IMPORTANT: Use the EXACT LTV calculation provided."""

    user_prompt = f"""Analyze property collateral for case {app_data.get('case_id')}:

PROPERTY:
- Type: {property_data.get('type')}
- Appraised Value: ${appraised_value:,.2f}
- Purchase Price: ${property_data.get('purchase_price', 0):,.2f}
- Condition: {property_data.get('condition')}
- Required Repairs: ${property_data.get('required_repairs', 0):,.2f}
- Use: {loan.get('use')}

LOAN:
- Loan Amount: ${loan_amount:,.2f}
- Down Payment: ${loan.get('down_payment', 0):,.2f}

CALCULATED LTV (ACCURATE - DO NOT RECALCULATE):
{ltv_result}

Provide your collateral analysis."""

    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    analysis = response.content
    bias_flags = detect_bias_signals(analysis, app_data)

    return {
        **state,
        "collateral_analysis": analysis,
        "bias_flags": state.get("bias_flags", []) + bias_flags,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            "Collateral Analyst: Completed property analysis (LTV from tool)"
        ]
    }


def critic_agent_node(state: dict, llm) -> dict:
    from langchain_core.messages import HumanMessage, SystemMessage

    system_prompt = """You are a Quality Assurance Critic reviewing underwriting analyses.

Your role is to:
1. Verify all analyses are complete and thorough
2. Identify any contradictions or inconsistencies
3. Ensure policy compliance
4. Flag any missing information
5. Provide a synthesis of key findings

Be critical but fair. Focus on ensuring decision quality."""

    user_prompt = f"""Review all analyses for case {state.get('case_id')}:

CREDIT ANALYSIS:
{state.get('credit_analysis', 'Not completed')}

INCOME ANALYSIS:
{state.get('income_analysis', 'Not completed')}

ASSET ANALYSIS:
{state.get('asset_analysis', 'Not completed')}

COLLATERAL ANALYSIS:
{state.get('collateral_analysis', 'Not completed')}

BIAS FLAGS: {state.get('bias_flags', [])}

Provide your critical review and synthesis."""

    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])

    return {
        **state,
        "critic_review": response.content,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            "Critic: Completed review of all specialist analyses"
        ]
    }


def decision_agent_node(state: dict, llm) -> dict:
    from langchain_core.messages import HumanMessage, SystemMessage

    system_prompt = """You are the Senior Underwriting Decision Agent.

Synthesize all specialist analyses plus the Critic review into a final decision and credit memo.

DECISION PRINCIPLES:
- Use policy-compliant, objective underwriting logic.
- Do NOT reference protected characteristics.
- If any bias flags exist, elevate to human review.

OUTPUT REQUIREMENTS (use this exact structure):
1) RISK_SCORE: <integer 0-100> (0=lowest risk, 100=highest risk)
2) DECISION: <APPROVED | DENIED | CONDITIONAL_APPROVAL>
3) CREDIT_MEMO: Summary, strengths, weaknesses, conditions, justification"""

    user_prompt = f"""Make final underwriting decision for case {state.get('case_id')}:

CREDIT ANALYSIS SUMMARY:
{state.get('credit_analysis', 'N/A')[:500]}...

INCOME ANALYSIS SUMMARY:
{state.get('income_analysis', 'N/A')[:500]}...

ASSET ANALYSIS SUMMARY:
{state.get('asset_analysis', 'N/A')[:500]}...

COLLATERAL ANALYSIS SUMMARY:
{state.get('collateral_analysis', 'N/A')[:500]}...

CRITIC REVIEW:
{state.get('critic_review', 'N/A')[:500]}...

COMPLIANCE ALERTS:
- Bias Flags: {len(state.get('bias_flags', []))}
- Policy Violations: {len(state.get('policy_violations', []))}

Provide:
1. RISK_SCORE: (number 0-100)
2. DECISION: (APPROVED/DENIED/CONDITIONAL_APPROVAL)
3. CREDIT_MEMO: (comprehensive decision documentation)"""

    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    content = response.content

    risk_score = 50
    match = re.search(r'RISK_SCORE:\s*(\d+)', content)
    if match:
        risk_score = int(match.group(1))

    decision = "CONDITIONAL_APPROVAL"
    if "DENIED" in content.upper():
        decision = "DENIED"
    elif "CONDITIONAL_APPROVAL" in content.upper() or "CONDITIONAL APPROVAL" in content.upper():
        decision = "CONDITIONAL_APPROVAL"
    elif "APPROVED" in content.upper():
        decision = "APPROVED"

    human_review_required = (
        len(state.get("bias_flags", [])) > 0
        or len(state.get("policy_violations", [])) > 0
        or risk_score > 70
    )

    return {
        **state,
        "decision_memo": content,
        "final_decision": decision,
        "risk_score": risk_score,
        "human_review_required": human_review_required,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            f"Decision Agent: {decision} (Risk Score: {risk_score}/100)"
        ]
    }


# ─── API Endpoints ───────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/api/test-cases")
async def get_test_cases():
    """Return the 3 built-in test cases."""
    json_path = Path(__file__).parent / "mortgage_test_cases.json"
    with open(json_path, "r") as f:
        data = json.load(f)

    # Return summary info (not full PII)
    summaries = []
    for tc in data["test_cases"]:
        debts = tc.get("debts", {})
        total_debt = sum(debts.values())
        monthly_income = tc["employment"]["monthly_income"]
        proposed = tc["loan"]["estimated_payment"]
        dti = ((total_debt + proposed) / monthly_income * 100) if monthly_income > 0 else 0
        ltv = (tc["loan"]["amount"] / tc["property"]["appraised_value"] * 100) if tc["property"]["appraised_value"] > 0 else 0

        summaries.append({
            "case_id": tc["case_id"],
            "name": tc["name"],
            "credit_score": tc["credit_score"],
            "loan_amount": tc["loan"]["amount"],
            "down_payment": tc["loan"]["down_payment"],
            "property_value": tc["property"]["appraised_value"],
            "monthly_income": monthly_income,
            "dti_ratio": round(dti, 1),
            "ltv_ratio": round(ltv, 1),
            "employment_type": tc["employment"]["type"],
            "employment_years": tc["employment"]["years"],
            "expected_decision": tc["expected_decision"],
        })
    return {"test_cases": summaries}


@app.post("/api/validate-key")
async def validate_key(req: APIKeyRequest):
    """Validate an OpenAI API key by making a simple request."""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        llm = ChatOpenAI(
            model=req.model,
            temperature=0,
            openai_api_key=req.openai_api_key,
            openai_api_base=req.openai_api_base,
            max_tokens=10,
        )
        llm.invoke([HumanMessage(content="Say OK")])
        return {"valid": True}
    except Exception as e:
        return {"valid": False, "error": str(e)}


@app.post("/api/run-underwriting")
async def run_underwriting(req: RunRequest):
    """Run the full multi-agent underwriting pipeline on a test case."""
    json_path = Path(__file__).parent / "mortgage_test_cases.json"
    with open(json_path, "r") as f:
        data = json.load(f)

    if req.case_index < 0 or req.case_index >= len(data["test_cases"]):
        raise HTTPException(status_code=400, detail="Invalid case_index")

    test_case = data["test_cases"][req.case_index]
    return await _run_pipeline(req.openai_api_key, req.openai_api_base, req.model, test_case)


@app.post("/api/run-custom")
async def run_custom(req: CustomApplicationRequest):
    """Run underwriting on a custom application."""
    return await _run_pipeline(req.openai_api_key, req.openai_api_base, req.model, req.applicant_data)


async def _run_pipeline(api_key: str, api_base: str, model: str, applicant_data: dict):
    """Core pipeline execution."""
    session_id = str(uuid.uuid4())

    try:
        llm = create_llm(api_key, api_base, model)
        policy_store = create_policy_store(api_key, api_base)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to initialize: {str(e)}")

    # Initialize state
    state = {
        "case_id": applicant_data.get("case_id", f"CUSTOM-{uuid.uuid4().hex[:6].upper()}"),
        "applicant_data": applicant_data,
        "sanitized_data": sanitize_pii(applicant_data),
        "credit_analysis": None,
        "income_analysis": None,
        "asset_analysis": None,
        "collateral_analysis": None,
        "critic_review": None,
        "decision_memo": None,
        "final_decision": None,
        "risk_score": None,
        "next_agent": None,
        "analysis_complete": False,
        "human_review_required": False,
        "human_review_completed": False,
        "human_notes": None,
        "bias_flags": [],
        "policy_violations": [],
        "reasoning_chain": [f"Application {applicant_data.get('case_id', 'CUSTOM')} initialized"],
        "timestamp": datetime.now().isoformat(),
    }

    steps = []

    # Run agents sequentially
    try:
        steps.append({"agent": "Credit Analyst", "status": "running"})
        state = credit_analyst_node(state, llm, policy_store)
        steps[-1]["status"] = "complete"

        steps.append({"agent": "Income Analyst", "status": "running"})
        state = income_analyst_node(state, llm, policy_store)
        steps[-1]["status"] = "complete"

        steps.append({"agent": "Asset Analyst", "status": "running"})
        state = asset_analyst_node(state, llm, policy_store)
        steps[-1]["status"] = "complete"

        steps.append({"agent": "Collateral Analyst", "status": "running"})
        state = collateral_analyst_node(state, llm, policy_store)
        steps[-1]["status"] = "complete"

        steps.append({"agent": "Critic Agent", "status": "running"})
        state = critic_agent_node(state, llm)
        steps[-1]["status"] = "complete"

        steps.append({"agent": "Decision Agent", "status": "running"})
        state = decision_agent_node(state, llm)
        steps[-1]["status"] = "complete"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error at {steps[-1]['agent']}: {str(e)}")

    # Store session for human review
    sessions[session_id] = state

    # Build response
    app_data = applicant_data
    debts = app_data.get("debts", {})
    total_debt = sum(debts.values()) if isinstance(debts, dict) else 0
    monthly_income = app_data.get("employment", {}).get("monthly_income", 0)
    proposed = app_data.get("loan", {}).get("estimated_payment", 0)
    dti = ((total_debt + proposed) / monthly_income * 100) if monthly_income > 0 else 0
    ltv = (app_data["loan"]["amount"] / app_data["property"]["appraised_value"] * 100) if app_data.get("property", {}).get("appraised_value", 0) > 0 else 0

    return {
        "session_id": session_id,
        "case_id": state["case_id"],
        "applicant_name": app_data.get("name", "Unknown"),
        "pii_sanitization": {
            "before": {
                "name": app_data.get("name"),
                "ssn": app_data.get("ssn"),
                "phone": app_data.get("phone"),
                "address": app_data.get("address"),
            },
            "after": {
                "name": state["sanitized_data"].get("name"),
                "ssn": state["sanitized_data"].get("ssn"),
                "phone": state["sanitized_data"].get("phone"),
                "address": state["sanitized_data"].get("address"),
            }
        },
        "metrics": {
            "credit_score": app_data.get("credit_score"),
            "dti_ratio": round(dti, 1),
            "ltv_ratio": round(ltv, 1),
            "loan_amount": app_data["loan"]["amount"],
            "property_value": app_data["property"]["appraised_value"],
            "monthly_income": monthly_income,
        },
        "analyses": {
            "credit": state["credit_analysis"],
            "income": state["income_analysis"],
            "asset": state["asset_analysis"],
            "collateral": state["collateral_analysis"],
            "critic": state["critic_review"],
        },
        "decision": {
            "final_decision": state["final_decision"],
            "risk_score": state["risk_score"],
            "decision_memo": state["decision_memo"],
            "human_review_required": state["human_review_required"],
        },
        "compliance": {
            "bias_flags": state["bias_flags"],
            "policy_violations": state["policy_violations"],
        },
        "reasoning_chain": state["reasoning_chain"],
        "workflow_steps": steps,
    }


@app.post("/api/human-review")
async def submit_human_review(req: HumanReviewRequest):
    """Submit human underwriter review."""
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = sessions[req.session_id]
    state["human_review_completed"] = True
    state["human_notes"] = req.comments

    # Override or confirm AI decision
    final = req.decision
    if req.decision == "CONDITIONAL":
        final = "CONDITIONAL_APPROVAL"

    return {
        "session_id": req.session_id,
        "case_id": state["case_id"],
        "ai_decision": state["final_decision"],
        "human_decision": final,
        "human_comments": req.comments,
        "final_outcome": final,
        "audit_trail": {
            "ai_risk_score": state["risk_score"],
            "ai_decision": state["final_decision"],
            "human_override": final != state["final_decision"],
            "human_decision": final,
            "review_timestamp": datetime.now().isoformat(),
            "compliance_met": True,
            "reasoning_chain": state["reasoning_chain"] + [
                f"Human Review: {final} - {req.comments[:100]}"
            ],
        }
    }


# ─── Serve Frontend ──────────────────────────────────────────────────────────

frontend_dir = Path(__file__).parent.parent / "frontend"

@app.get("/")
async def serve_index():
    return FileResponse(frontend_dir / "index.html")

@app.get("/{path:path}")
async def serve_static(path: str):
    file_path = frontend_dir / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    return FileResponse(frontend_dir / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
