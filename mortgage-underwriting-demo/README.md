# Senior Mortgage Underwriting System

A multi-agent AI system for automated mortgage underwriting, built with **LangGraph** architecture. This demo showcases how six specialized AI agents collaborate to analyze mortgage applications through credit, income, asset, and collateral evaluation — with quality assurance, bias detection, and human-in-the-loop review.


[Video Walkthrough](https://www.youtube.com/watch?v=rJRX7LiP44s)
## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────────┐
│   Credit     │───▶│   Income     │───▶│   Asset      │───▶│  Collateral    │
│   Analyst    │    │   Analyst    │    │   Analyst    │    │  Analyst       │
│   💳         │    │   💵         │    │   💰         │    │  🏠            │
└─────────────┘    └──────────────┘    └──────────────┘    └────────────────┘
                                                                    │
                                                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Critic Agent 🔎                                  │
│              Quality Assurance & Consistency Review                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       Decision Agent ⚖️                                 │
│           Risk Score • Final Decision • Credit Memo                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Human Review (HITL) 👤                                │
│            Senior Underwriter Override & Audit Trail                     │
└─────────────────────────────────────────────────────────────────────────┘
```

## Features

- **6 Specialized AI Agents** — Credit, Income, Asset, Collateral, Critic, and Decision agents
- **RAG Policy Retrieval** — Embedded underwriting policies guide each agent's analysis
- **PII Sanitization** — SSN, name, address, and phone are redacted before AI processing (GDPR/CCPA/GLBA)
- **Fair Lending Bias Detection** — Monitors for protected characteristic mentions per ECOA
- **Calculator Tools** — DTI, LTV, reserves, and housing ratios computed deterministically (no hallucination)
- **Human-in-the-Loop** — Senior underwriter can override AI decisions with full audit trail
- **3 Demo Test Cases** — Strong approval, conditional/borderline, and denial scenarios
- **Real-time Pipeline Visualization** — Watch agents process sequentially with live status

## Live Demo

Deploy to Netlify and enter your OpenAI API key to run the system.

**Your API key stays in your browser** — it is never sent to any server other than OpenAI's API directly.

## Quick Start

### Deploy to Netlify

1. Push this repo to GitHub
2. Connect to Netlify → Select repository
3. Build settings are auto-configured via `netlify.toml`:
   - **Publish directory:** `public`
   - No build command needed (static site)
4. Deploy!

### Run Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/mortgage-underwriting-demo.git
cd mortgage-underwriting-demo

# Serve the static site (any static server works)
npx serve public
# or
python3 -m http.server 8000 --directory public
```

Open `http://localhost:8000` and enter your OpenAI API key.

## How It Works

1. **Enter API Key** — Your OpenAI key powers the AI agents directly from your browser
2. **Select Test Case** — Choose from 3 pre-built scenarios (strong, borderline, weak applicant)
3. **Watch the Pipeline** — 6 agents process sequentially with real-time progress
4. **Review Results** — See PII sanitization, agent analyses, decision metrics, and bias flags
5. **Human Review** — Override or confirm the AI decision as a senior underwriter
6. **Audit Trail** — Full reasoning chain for compliance documentation

## Test Cases

| Case | Applicant | Credit | DTI | Expected |
|------|-----------|--------|-----|----------|
| MTG-2025-001 | Sarah Johnson | 760 | 30.4% | **APPROVED** |
| MTG-2025-002 | Michael Chen | 680 | 42.1% | **CONDITIONAL** |
| MTG-2025-003 | Robert Martinez | 580 | 55.2% | **DENIED** |

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Agent Architecture | LangGraph (conceptual) |
| LLM Framework | LangChain + OpenAI GPT-4o |
| Policy Retrieval | RAG with embedded policies |
| PII Protection | Custom sanitization (SSN, name, address, phone) |
| Bias Detection | Fair Lending Act keyword monitoring |
| Frontend | React 18 + Custom CSS |
| Deployment | Netlify (static) |

## API Key Requirements

You need an **OpenAI API key** with access to `gpt-4o-mini` (default) or `gpt-4o`.

- Get a key at [platform.openai.com](https://platform.openai.com/api-keys)
- The demo uses approximately **$0.02-0.05 per full pipeline run** with gpt-4o-mini
- Your key is used only for direct browser-to-OpenAI API calls

## Educational Disclaimer

This project is for **educational and portfolio demonstration purposes only**. It does not constitute financial, legal, or professional advice. Underwriting policies are simplified for demonstration. Always consult qualified mortgage professionals for actual lending decisions.

## License

MIT License — See [LICENSE](LICENSE) for details.
