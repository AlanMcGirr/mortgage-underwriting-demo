window.APP_DATA = {
  TEST_CASES: [
    {
      case_id: "MTG-2025-001",
      name: "Sarah Johnson",
      credit_score: 760,
      employment: {
        employer: "Tech Solutions Inc",
        position: "Senior Software Engineer",
        years: 6.5,
        monthly_income: 12500,
        type: "W2",
        employment_gap: "None",
        gap_explanation: "N/A"
      },
      debts: {
        car_loan: 1200,
        student_loan: 800,
        credit_cards: 1800
      },
      loan: {
        amount: 400000,
        down_payment: 100000,
        closing_costs: 12000,
        estimated_payment: 3200,
        property_type: "Single Family",
        use: "Primary Residence"
      },
      property: {
        purchase_price: 500000,
        appraised_value: 515000,
        condition: "C3 - Average",
        type: "Single Family Home",
        required_repairs: 0
      },
      assets: {
        checking: 85000,
        savings: 100000,
        "401k": 250000,
        reserves_months: 18,
        recent_deposits: [
          { date: "2024-12-15", amount: 22000, description: "Annual bonus" },
          { date: "2024-11-30", amount: 12500, description: "Regular salary" },
          { date: "2024-10-30", amount: 12500, description: "Regular salary" }
        ],
        deposit_explanations: "December bonus of $22,000 documented with pay stub and bonus letter confirming annual bonus structure"
      },
      credit_history: {
        bankruptcies: 0,
        foreclosures: 0,
        late_payments_12mo: 0,
        late_payments_24mo: 0,
        collections: [],
        credit_notes: "Excellent payment history. Multiple credit cards with perfect payment record. Auto loan paid as agreed. No derogatory items."
      },
      ssn: "123-45-6789",
      phone: "555-234-5678",
      address: "1234 Oak Street, San Francisco, CA 94102",
      dti_ratio: 0.304,
      expected_decision: "APPROVED"
    },
    {
      case_id: "MTG-2025-002",
      name: "Michael Chen",
      credit_score: 680,
      employment: {
        employer: "TechStart LLC",
        position: "Product Manager",
        years: 1.5,
        monthly_income: 9500,
        type: "W2",
        employment_gap: "Yes",
        gap_explanation: "3-month gap between jobs during industry transition from retail to tech."
      },
      debts: {
        car_loan: 650,
        student_loan: 450,
        credit_cards: 2890
      },
      loan: {
        amount: 380000,
        down_payment: 20000,
        closing_costs: 11000,
        estimated_payment: 3050,
        property_type: "Townhouse",
        use: "Primary Residence"
      },
      property: {
        purchase_price: 400000,
        appraised_value: 395000,
        condition: "C3 - Average",
        type: "Townhouse",
        required_repairs: 2500
      },
      assets: {
        checking: 25000,
        savings: 18000,
        "401k": 45000,
        reserves_months: 3,
        recent_deposits: [
          { date: "2024-12-20", amount: 15000, description: "Transfer from parents" },
          { date: "2024-11-30", amount: 9500, description: "Regular salary" }
        ],
        deposit_explanations: "December transfer of $15,000 from parents - documentation pending gift letter and source of funds verification"
      },
      credit_history: {
        bankruptcies: 0,
        foreclosures: 0,
        late_payments_12mo: 1,
        late_payments_24mo: 2,
        collections: [{ type: "medical", amount: 3000, status: "unpaid" }],
        credit_notes: "One 30-day late payment 10 months ago on credit card. Another 30-day late 18 months ago during job transition. No major derogatory items."
      },
      ssn: "987-65-4321",
      phone: "(415) 555-9876",
      address: "567 Maple Avenue, Oakland, CA 94601",
      dti_ratio: 0.421,
      expected_decision: "CONDITIONAL_APPROVAL"
    },
    {
      case_id: "MTG-2025-003",
      name: "Robert Martinez",
      credit_score: 580,
      employment: {
        employer: "QuickServe Restaurant",
        position: "Shift Manager",
        years: 0.8,
        monthly_income: 5800,
        type: "W2",
        employment_gap: "Yes",
        gap_explanation: "6-month gap due to industry layoff."
      },
      debts: {
        car_loan: 450,
        student_loan: 350,
        credit_cards: 1800,
        personal_loan: 400
      },
      loan: {
        amount: 290000,
        down_payment: 10500,
        closing_costs: 9000,
        estimated_payment: 2400,
        property_type: "Condo",
        use: "Primary Residence"
      },
      property: {
        purchase_price: 300000,
        appraised_value: 285000,
        condition: "C4 - Fair",
        type: "Condominium",
        required_repairs: 8000
      },
      assets: {
        checking: 12000,
        savings: 5000,
        "401k": 8000,
        reserves_months: 1,
        recent_deposits: [
          { date: "2024-12-01", amount: 3000, description: "Cash deposit" },
          { date: "2024-11-15", amount: 5800, description: "Regular salary" }
        ],
        deposit_explanations: "Cash deposit of $3,000 - source undocumented and unverified"
      },
      credit_history: {
        bankruptcies: 0,
        foreclosures: 0,
        late_payments_12mo: 4,
        late_payments_24mo: 7,
        collections: [
          { type: "utility", amount: 800, status: "unpaid" },
          { type: "medical", amount: 2500, status: "in collections" }
        ],
        credit_notes: "Significant payment issues. 4 late payments in past 12 months. Multiple collection accounts totaling $3,300."
      },
      ssn: "456-78-9012",
      phone: "555-876-5432",
      address: "890 Pine Road, Apt 4B, San Jose, CA 95112",
      dti_ratio: 0.552,
      expected_decision: "DENIED"
    }
  ],

  UNDERWRITING_POLICIES: {
    credit: `CREDIT POLICIES AND GUIDELINES

Credit Score Requirements:
- Conventional loans: Minimum 620 credit score required
- FHA loans: Minimum 580 credit score required
- Credit score tiers for conventional:
  - Excellent (760+): Best rates and terms
  - Good (700-759): Standard favorable terms
  - Fair (660-699): Standard terms with potential rate adjustment
  - Below 660: Higher rates or additional requirements

Bankruptcy History:
- Chapter 7 Bankruptcy: Minimum 4 years must have elapsed since discharge date before approval
- Chapter 13 Bankruptcy: Minimum 2 years must have elapsed since discharge or active payment plan established and no missed payments
- Discharged bankruptcies older than 7 years do not require special consideration

Foreclosure History:
- Conventional loans: Minimum 7 years must elapse since foreclosure completion
- FHA loans: Minimum 3 years must elapse since foreclosure completion
- Non-standard property types may require longer seasoning periods
- Extenuating circumstances (job loss, illness, death) may reduce required waiting period by up to 2 years

Late Payment Rules:
- Maximum 2 late payments (30+ days) permitted in past 12 months for conventional loans
- Maximum 1 late payment in past 12 months for loans under 680 credit score
- No late payments permitted in past 90 days
- Late payments in past 2 months are automatic denial triggers
- Late payments beyond 60 days require written explanation and underwriter review

Collections Accounts:
- Medical collections: $5,000 or less may be excluded from debt-to-income calculations
- Non-medical collections: Must be under $1,000 to exclude from DTI, or require payoff or settlement agreement
- Paid collections: Older than 3 years no longer appear on credit report
- Collections in last 12 months: Require payoff or settlement agreement before approval
- Multiple collection accounts (3+): Automatic underwriter review and possible denial`,

    income: `INCOME VERIFICATION AND EMPLOYMENT POLICIES

Employment Requirements:
- Minimum 2 years continuous employment in current field required
- Current employer employment must exceed 90 days (for FHA, minimum is 30 days but 2-year history in field required)
- Self-employed applicants must provide 2 years of tax returns
- Licensed professionals may use average of past 2 years if income varies by 20% or more

Employment Gap Rules:
- Employment gaps under 30 days do not require explanation
- Employment gaps 30-90 days require brief written explanation
- Employment gaps exceeding 90 days require detailed explanation and verification of income source during gap
- Gap caused by job transition to higher income position may be approved with offer letter
- Gap caused by job loss, furlough, or industry layoff requires minimum 6 months re-employment and income verification

Self-Employment Income:
- Must provide 2 years of complete tax returns (Form 1040 + Schedule C)
- Income calculated from line 31 (net profit) less depreciation
- Must provide business license and proof of self-employment status
- If business less than 2 years old, personal employment history may supplement
- Income must be stable or trending upward; 20% decline year-over-year requires explanation

Bonus and Overtime Income:
- Bonus income may be included if documented for 2+ years with reasonable expectation of continuation
- Bonus must be supported by signed bonus letter or employment contract
- One-time bonuses are excluded; must be recurring
- Overtime income may be included if averaged over 2 years and documented with recent pay stubs
- Declining bonus/overtime trend requires explanation and potential exclusion

Debt-to-Income Ratios (DTI):
- Conventional Front-End Ratio: Maximum 28% (housing expense to gross monthly income)
- Conventional Back-End Ratio: Maximum 43% (total debt to gross monthly income)
- FHA Front-End Ratio: Maximum 31%
- FHA Back-End Ratio: Maximum 50%
- Manual underwriting required for DTI exceeding 50% even with strong compensating factors
- Compensating factors: Strong credit score, large reserves, significant equity in other properties`,

    assets: `ASSET AND DOWN PAYMENT POLICIES

Reserve Requirements:
- Primary residence: Minimum 2 months PITI (Principal, Interest, Taxes, Insurance) in liquid reserves required
- Investment property: Minimum 6 months PITI in liquid reserves
- Non-owner occupied: Minimum 12 months PITI in liquid reserves
- Liquid assets: Checking, savings, money market accounts qualify
- Retirement accounts (401k, IRA): May count at 70% of stated value if non-withdrawn
- Non-liquid assets (real estate equity, stocks): May count at 50-70% depending on type

Down Payment Sources:
- Borrower savings: Documented with bank statements for minimum 2 months seasoning
- Gift funds: Documented with gift letter and verification of donor funds; no repayment obligation
- Sweat equity: May be considered if documented with construction contracts and appraisal support
- Sale of other property: Allowed if documented with executed contract or closing statement

Large Deposit Rules:
- Any single deposit of $1,000 or more OR 25% of monthly income must be explained
- Deposits require written explanation and supporting documentation
- Gift funds must include signed gift letter stating no repayment obligation
- Loan proceeds must be documented with promissory note; only certain sources permitted
- Unexplained or suspicious deposits may result in denial or delayed approval

Gift Fund Rules:
- Gifts must come from family members (spouse, parent, grandparent, sibling, legal guardian)
- Gift letter must state: donor name, relationship, property address, gift amount, date, no repayment obligation
- Donor verification: Bank statements showing availability of gift funds required
- Gifts may cover entire down payment and closing costs for qualified borrowers
- Non-family gifts (friends, employers, non-profits) require special underwriting approval`,

    collateral: `PROPERTY AND COLLATERAL POLICIES

Appraisal Requirements:
- All properties require independent professional appraisal using Uniform Standards of Professional Appraisal Practice (USPAP)
- Appraisal must be ordered through approved vendor and completed by state-licensed or state-certified appraiser
- Appraisal must be completed within 90 days of loan application (or 30 days before closing)
- If appraised value is below purchase price, loan amount adjusts to appraised value or down payment increases
- Appraisal disputes may require second appraisal at borrower's expense

Property Condition Standards:
- Condition Rating C3 (Average): Acceptable for all loan types with no required repairs
- Condition Rating C4 (Fair): Acceptable but may require escrow for repairs or reduced LTV
- Condition Rating C5 (Poor) or below: Requires repairs before approval or FHA 203(k) rehabilitation loan program
- Required repairs greater than 5% of purchase price may trigger additional scrutiny or loan program adjustment
- Major structural defects, foundation issues, or roof repairs needed may result in denial

Loan-to-Value (LTV) Limits:
- Primary residence conventional: Maximum 97% LTV (minimum 3% down)
- Primary residence standard: 95% LTV with standard pricing
- Investment property: Maximum 85% LTV (minimum 15% down)
- Condominiums: Reduced LTV by 5% compared to single-family standards
- Multi-unit properties (2-4 units): Reduced LTV by 5% compared to single-family standards

Acceptable Property Types:
- Single-family detached homes: Full approval
- Townhouses (attached): Full approval with standard guidelines
- Condominiums: Approved if unit in FHA-approved condo project OR meets portfolio guidelines
- Multi-unit properties (2-4 units): Approved with enhanced underwriting
- Investment properties: Full approval with 20% minimum down and enhanced reserves
- Manufactured homes: Approved only if permanently affixed to owned land
- Commercial properties: Not eligible for residential mortgage products

Condo-Specific Requirements:
- Building must be in FHA-approved condo project OR meet portfolio underwriting guidelines
- Maximum 25% of units in foreclosure/default required by FHA guidelines
- Borrower cannot own multiple units in same building
- HOA must be professionally managed (for FHA loans)
- Condo reserves must be minimum 10% of annual budget
- Condo association must have 3-year financial history`
  }
};
