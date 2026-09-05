# ⚖️ CLAUSECLEAR — AI-Powered Legal Tech Contract Analyzer

> **"Understand before you sign."**  
> *A patient, knowledgeable friend who reads legal contracts, explains them in plain English, highlights unfair or dangerous clauses, reveals missing protections, and helps you negotiate better terms.*

🏆 **Built for:** **Srijan Hackathon**  
🏛️ **Organized by:** **GH Raisoni College of Engineering and Management, Pune** & **Computer Society of India (CSI)**  
🏷️ **Domain:** Legal Tech / Generative AI / Public Good  

---

## 📌 Problem Statement

Every day, millions of **renters, fresh graduates, freelancers, and small business owners** in India and across the world sign complex legal contracts without understanding the fine print. 

- **Legal Jargon:** Agreements are filled with archaic legalese ("indemnify", "unilateral forfeiture", "in perpetuity").
- **Unfair & Punitive Clauses:** Sneaky terms like 24-hour eviction, 3-year non-compete restraints, or infinite free revisions are buried deep inside agreements.
- **Missing Protections:** Signers don't know what *should* be in a contract (e.g., deposit refund timelines, maintenance responsibilities).
- **Prohibitive Costs:** Traditional legal review costs thousands of rupees and takes days, making it inaccessible for routine agreements.

---

## 💡 The ClauseClear Solution

**ClauseClear** democratizes legal understanding by providing an instant, educational contract review assistant:

1. **📄 Multi-Format Ingestion:** Drag-and-drop support for **PDF**, **Word (.docx)**, and **Plain Text (.txt)**.
2. **🧩 Semantic Clause Segmentation:** Intelligently breaks contracts into logical legal provisions (Payment, Termination, Non-Compete, Liability, etc.).
3. **🗣️ Plain-English Translation:** Explains complex legal obligations in accessible **8th-grade language**.
4. **🚦 Traffic-Light Risk Badges:**
   - 🟢 **GREEN (Safe/Standard):** Balanced, low-risk, customary terms.
   - 🟡 **YELLOW (Caution/Ambiguous):** Needs attention, vague, or one-sided terms.
   - 🔴 **RED (High Risk/Punitive):** Harmful, severe financial/operational liability, or unfair terms.
5. **✍️ Negotiation-Ready Alternative Wording:** Provides balanced, ready-to-copy counter-proposals to push back against red/yellow clauses.
6. **🎯 Transparent Fairness Score (0–100):** Weighted scoring engine accounting for clause severity, risk ratios, and missing protections.
7. **🛡️ Missing Protections Detector:** Automatically identifies contract type (*Rental*, *Employment*, *Freelance*, *Generic*) and checks against industry safeguard checklists.
8. **💬 Grounded RAG Chatbot (ChromaDB):** Conversational Q&A assistant strictly grounded on the uploaded contract with clause citations. **Never hallucinates outside legal rules as facts.**
9. **📄 Executive PDF Report:** One-click downloadable summary report generated using ReportLab for offline negotiation.
10. **⚡ 100% Offline Demo Mode:** Built-in fallback engine allowing judges and users to test the entire pipeline without requiring paid API keys.

---

## 🏗️ Architecture & Technology Stack

```text
       ┌────────────────────────────────────────────────────────┐
       │                   Streamlit Frontend                   │
       │  (Glassmorphism UI • Filters • Chat • PDF Download)     │
       └───────────────────────────┬────────────────────────────┘
                                   │ HTTP / JSON
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                    FastAPI Backend                     │
       │    (REST Endpoints: /upload, /analyze, /chat, /report)  │
       └─────┬─────────────────────┬──────────────────────┬─────┘
             │                     │                      │
             ▼                     ▼                      ▼
┌────────────────────────┐ ┌────────────────┐ ┌────────────────────────┐
│    Document Service    │ │ Scoring Engine │ │     ReportLab PDF      │
│ (PyMuPDF, python-docx) │ │(Fairness & MPs)│ │   (Executive Brief)    │
└────────────┬───────────┘ └────────────────┘ └────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      LLM & RAG Pipeline Layer                        │
│   • Multi-Provider LLM: OpenAI (GPT-4o) / Anthropic (Claude 3.5)     │
│   • Vector Embeddings & Storage: ChromaDB (HNSW Cosine Search)       │
│   • Grounded Retrieval & Citation Generation                         │
│   • Local Rule-Based Mock Fallback for Demo Mode                     │
└──────────────────────────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    SQLite Database Persistence                       │
│    (Sessions, Contracts, Segmented Clauses, Analyses, Chats)         │
└──────────────────────────────────────────────────────────────────────┘
```

### Core Technologies
- **Frontend:** Streamlit, Custom Responsive CSS (Glassmorphism, Badges, Metrics)
- **Backend API:** FastAPI, Uvicorn, Pydantic v2
- **Document Parsers:** PyMuPDF (`fitz`), `python-docx`
- **Vector Database & RAG:** ChromaDB, Dense Embeddings
- **AI / LLMs:** OpenAI API (`gpt-4o-mini`, `text-embedding-3-small`), Anthropic API (`claude-3-5-sonnet`)
- **PDF Generation:** ReportLab
- **Storage:** SQLite3
- **Testing:** Pytest, HTTPX

---

## 🚀 Quickstart & Installation

### 1. Clone & Navigate to Repository
```bash
git clone https://github.com/ayushh1302/Requiem-Srijan.git
cd Requiem-Srijan
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` (optional for live OpenAI/Claude mode):
```ini
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEMO_MODE=true
```
*(Note: With `DEMO_MODE=true`, the app works out-of-the-box offline with realistic sample analyses!)*

---

## 🏃 Running the Application

### Option A: Unified Launcher (Recommended)
Start both FastAPI backend (port 8000) and Streamlit frontend (port 8501) with a single command:
```bash
python run.py
```

### Option B: Separate Terminals

**Terminal 1 — FastAPI Backend:**
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Streamlit Frontend:**
```bash
streamlit run frontend/app.py
```

Access the UI at: **`http://localhost:8501`**  
Access the API Docs at: **`http://127.0.0.1:8000/docs`**  

---

## 🧪 Running Automated Tests

Run the automated pytest test suite covering parser validation, fairness scoring, missing protections, and API routes:
```bash
python -m pytest tests/ -v
```

Output:
```text
============================= test session starts =============================
tests/test_api.py::test_health_endpoint PASSED                           [  7%]
tests/test_api.py::test_upload_and_analyze_flow PASSED                   [ 15%]
tests/test_document_service.py::test_normalize_text PASSED               [ 23%]
tests/test_document_service.py::test_validate_unsupported_format PASSED  [ 30%]
tests/test_document_service.py::test_validate_empty_file PASSED          [ 38%]
tests/test_document_service.py::test_extract_txt_file PASSED             [ 46%]
tests/test_missing_protections.py::test_detect_rental_type PASSED        [ 53%]
tests/test_missing_protections.py::test_detect_employment_type PASSED    [ 61%]
tests/test_missing_protections.py::test_missing_protections_rental PASSED [ 69%]
tests/test_schemas.py::test_clause_item_schema PASSED                    [ 76%]
tests/test_schemas.py::test_clause_analysis_schema PASSED                [ 84%]
tests/test_scoring.py::test_fairness_score_all_green PASSED              [ 92%]
tests/test_scoring.py::test_fairness_score_with_red_and_missing PASSED   [100%]
======================== 13 passed in 7.39s =========================
```

---

## 📁 Project Structure

```text
clauseclear/
│
├── frontend/
│   └── app.py                     # Streamlit frontend with rich UI tabs & cards
│
├── backend/
│   ├── main.py                    # FastAPI entrypoint & CORS middleware
│   ├── api/
│   │   ├── routes_health.py       # GET /health
│   │   ├── routes_upload.py       # POST /upload
│   │   ├── routes_analysis.py     # POST /analyze, GET /analysis/{session_id}
│   │   ├── routes_chat.py         # POST /chat (Grounded RAG)
│   │   ├── routes_report.py       # GET /report/{session_id} (PDF generation)
│   │   └── routes_reset.py        # POST /reset/{session_id}
│   ├── services/
│   │   ├── document_service.py    # PyMuPDF/python-docx parsers & normalization
│   │   ├── llm_service.py         # Multi-provider LLM abstraction (OpenAI/Anthropic)
│   │   ├── embedding_service.py   # OpenAI & offline dense embeddings
│   │   ├── rag_service.py         # ChromaDB indexing & grounded retrieval
│   │   ├── scoring_service.py     # Weighted fairness formula & missing protections
│   │   ├── report_service.py      # ReportLab executive PDF generator
│   │   └── mock_data_service.py   # High-fidelity mock engine for Demo Mode
│   ├── models/
│   │   └── schemas.py             # Pydantic data schemas & enums
│   ├── storage/
│   │   └── database.py            # SQLite session & history database
│   └── utils/
│       └── config.py              # Environment configuration loader
│
├── sample_contracts/
│   ├── rental_agreement_sample.txt      # Sample rental lease (Pune)
│   ├── employment_offer_sample.txt      # Sample tech employment contract
│   └── freelance_agreement_sample.txt   # Sample freelance web dev agreement
│
├── tests/
│   ├── test_document_service.py
│   ├── test_scoring.py
│   ├── test_missing_protections.py
│   ├── test_schemas.py
│   └── test_api.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── run.py
```

---

## 🎯 Live Hackathon Demonstration Flow (3–5 Min)

1. **Launch App:** Run `python run.py` and open `http://localhost:8501`.
2. **1-Click Sample:** Click **"🏠 Rental Lease"** in the sidebar.
3. **Inspect Dashboard:**
   - Point out the **Fairness Score: 42/100 (High Risk)**.
   - Show the summary breakdown (3 Red, 1 Yellow, 4 Green, 4 Missing Protections).
4. **Explore Red Flagged Clauses:**
   - Expand `[HIGH RISK] Immediate Unilateral Eviction` (eviction in 24 hours).
   - Review the **Plain-English Explanation** and **Key Concern**.
   - Show the **Negotiation-Ready Alternative Wording**:
     > *"Either party may terminate this agreement by providing at least 30 days prior written notice..."*
5. **Check Missing Protections:**
   - Show missing safeguards like *Deposit Refund Timeline* and *Inspection Notice*.
6. **Ask ClauseClear (RAG Chatbot):**
   - Click the prompt *"Can my deposit be forfeited or deducted?"*.
   - Point out that the chatbot cites **Clause 2 (Security Deposit & Forfeiture)**.
   - Ask an unsupported question (e.g. *"What is the pet policy?"*) to demonstrate grounded refusal:
     > *"The uploaded contract does not clearly address this."*
7. **Download PDF Report:**
   - Switch to **Download Report** tab and click **"📥 Download PDF Analysis Report"**.
   - Open the generated PDF to show the clean executive layout.

---

## 🛡️ Privacy & Security Best Practices

- **Zero Permanent File Exposure:** Files are parsed in memory; uploaded documents are scoped strictly to the user session.
- **Strict Grounding:** Chatbot prompts explicitly disallow hallucinations and enforce strict retrieval constraints.
- **Sanitized Secrets:** `.env` and SQLite files are strictly `.gitignore`d.

---

## ⚖️ Legal Disclaimer

> **ClauseClear provides AI-generated educational information and is NOT a substitute for professional legal advice.** For important legal, financial, or tenancy decisions, always consult a qualified advocate or attorney licensed in your jurisdiction.

---

## 👥 Hackathon Team Placeholder
- **Team Name:** Requiem
- **Hackathon:** Srijan Hackathon 2026 (GHRCEM Pune & CSI)
