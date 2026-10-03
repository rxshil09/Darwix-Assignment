# 🏥 ApexCare Health — AI Voice Agent & Production Knowledge Base
> **Darwix AI Engineer Assessment — Implementation for Question 1 & Question 2**

This repository provides an end-to-end, production-ready implementation of **Question 2 (Production-Ready Knowledge Base)** and **Question 1 (Knowledge-Grounded Voice Agent)** for health insurance lead qualification and policy advisory.

---

## 🌟 Key Highlights & Evaluation Criteria

| Assessment Area | Implementation & Evidence |
|---|---|
| **Question 2: Knowledge Base** | • Raw ingestion across HTML, TXT policy contracts, JSON underwriting rules, dirty forms.<br>• **PII Sanitization**: Redacted SSNs, phone numbers, emails, and credit cards.<br>• **Deduplication**: Exact hash (SHA256) and token-set containment deduplication (filtered 3 duplicate sections).<br>• **Hybrid Retrieval**: BM25 sparse keyword search + Vector Cosine + Reciprocal Rank Fusion (RRF).<br>• **5/5 Benchmark Queries**: Product, Policy, Qualification, FAQ, and Objection evaluated with 100% accuracy. |
| **Question 1: Voice Agent** | • **AI Engine**: Google Gemini (`gemini-3.5-flash-lite` via `google.genai` SDK) with resilient fallback dialogue manager.<br>• **Dynamic RAG Grounding**: Every response searches Q2 KB and returns verified `record_id` and provenance citations (no hardcoded FAQ prompts).<br>• **Safe Fallback**: Zero-hallucination blocker for out-of-scope queries (e.g. pet insurance, cosmetic procedures).<br>• **Human Escalation**: Automatic transfer workflow for explicit requests or senior applicants (age 66+).<br>• **Business Action**: Mock CRM lead creation and automated premium quotation (`LEAD-2026-xxxx`).<br>• **Web Calling Interface**: Callable browser interface with live mic, animated sound visualizer, real-time diarized transcript, and citation HUD.<br>• **Recorded Audio**: 5 recorded test calls with neural speech audio (`.mp3`) and diarized transcripts. |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      RAW UNSTRUCTURED DATA (data/raw/)                      │
│  • apexcare_plans_web.html (HTML markup, navigation, marketing banners)     │
│  • policy_terms_exclusions.txt (Contract terms, 24-mo PEC, room caps)       │
│  • underwriting_rules.json (Age 18-65 limits, smoker loading, BMI limits)   │
│  • customer_intake_forms_pii.txt (Messy customer inquiries containing PII)  │
│  • faq_objection_guide.txt (Official objection handling responses)          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   CLEANING & SANITIZATION (src/kb/cleaner.py)               │
│  • BeautifulSoup HTML stripping (removes header, footer, nav, promo tags)   │
│  • PII Redactor: regex scrubber -> [REDACTED_SSN], [REDACTED_PHONE], etc.   │
│  • Content Deduplicator: SHA256 exact match + token overlap containment     │
│  • Terminology Standardizer: canonical dictionary normalization             │
│  • Semantic Chunking with rich metadata (source, record_id, category)      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 HYBRID RETRIEVAL ENGINE (src/kb/retriever.py)               │
│  • Sparse Keyword Search: BM25 (rank-bm25)                                   │
│  • Dense Semantic Search: TF-IDF Cosine / Vector Embeddings                 │
│  • Reciprocal Rank Fusion (RRF): Score = 1/(60+rank_bm25) + 1/(60+rank_vec) │
│  • Strict Provenance Citations: record_id, source, category, score, snippet │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                 Dynamic Tool Calling  │ search_policy_kb(query)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  QUESTION 1 — VOICE AGENT (src/agent/)                      │
│  • Agent: "Sarah", Healthcare Advisor at ApexCare                          │
│  • Conversation State Machine: Greeting -> Qualification -> RAG -> CRM     │
│  • LLM Engine: Google Gemini 3.5 Flash Lite (google.genai SDK)              │
│  • Fallback Guardrail: Refuses out-of-scope inquiries without inventing info │
│  • Business Action: Mock CRM Lead Generation & Premium Calculation         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│            CALLABLE WEB INTERFACE & SPEECH PIPELINE (src/web/)              │
│  • FastAPI Backend (REST & Static Asset Server)                             │
│  • Neural TTS Synthesis: Edge-TTS (en-US-JennyNeural)                       │
│  • Browser Calling HUD: Waveform visualizer, live diarized transcript,      │
│    clickable citation badges, and real-time CRM Lead card                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
d:\PROJECTS\Darwix Assignment\
├── data/
│   ├── raw/                              # Uncleaned messy input files
│   │   ├── apexcare_plans_web.html       # Web brochure with noise & duplicate copy
│   │   ├── policy_terms_exclusions.txt   # Official policy contract & exclusions
│   │   ├── underwriting_rules.json       # Eligibility criteria & underwriting rules
│   │   ├── customer_intake_forms_pii.txt # Customer intake records containing PII
│   │   └── faq_objection_guide.txt       # Objection handling guidelines
│   └── processed/                        # Structured & sanitized knowledge base
│       ├── kb_records.json               # 32 normalized KB records with schemas
│       ├── kb_chunks.json                # Chunked passages for hybrid search
│       ├── pipeline_stats.json           # PII redaction and deduplication metrics
│       └── mock_crm_leads.json           # Persisted mock CRM leads from calls
├── src/
│   ├── kb/
│   │   ├── cleaner.py                    # BeautifulSoup parser, PII redactor, deduplicator
│   │   ├── schema.py                     # Pydantic models for records, chunks, citations
│   │   ├── indexer.py                    # Pipeline orchestrator
│   │   ├── retriever.py                  # Hybrid BM25 + Vector RRF search engine
│   │   └── evaluate.py                   # 5-query benchmark evaluation runner
│   ├── agent/
│   │   ├── prompts.py                    # Persona, qualification rules, grounding prompts
│   │   ├── crm.py                        # Mock CRM & premium quote calculator
│   │   └── voice_bot.py                  # Multi-turn state machine & Gemini RAG integration
│   ├── speech/
│   │   └── tts.py                        # Edge-TTS neural speech synthesis
│   └── web/
│       ├── app.py                        # FastAPI web application
│       └── static/                       # Sleek Web Calling UI
│           ├── index.html                # Dark-mode calling interface
│           ├── style.css                 # Glassmorphism aesthetic & animations
│           └── app.js                    # Web audio, speech recognition & HUD updates
├── test_runs/
│   ├── call_1_cooperative/               # Audio recordings (.mp3) + transcript.md + json
│   ├── call_2_objection/                 # Price objection audio + transcripts
│   ├── call_3_conflicting/               # Conflict (age 67) audio + transcripts
│   ├── call_4_outofscope/                # Zero-hallucination safe fallback audio + transcripts
│   ├── call_5_escalation/                # Human supervisor escalation audio + transcripts
│   ├── q1_test_calls_summary_report.md   # Full audit report for the 5 test calls
│   └── q2_retrieval_benchmark_report.md  # Full audit report for Question 2 benchmark
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quickstart & Setup Instructions

### 1. Prerequisites
- Python 3.10+
- Internet access (for Edge-TTS neural voices and Gemini API)

### 2. Environment Setup
```bash
# Clone or open project directory
cd "d:\PROJECTS\Darwix Assignment"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys
Copy `.env.example` to `.env` and add your Google Gemini API key:
```ini
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
TTS_VOICE=en-US-JennyNeural
PORT=8000
HOST=0.0.0.0
```
*(Note: If no API key is set, the system seamlessly uses the local deterministic grounded dialogue manager with zero downtime).*

---

## 🧪 Running the Evaluations & Tests

### Step 1: Run Question 2 Knowledge Base Indexing & Benchmark
```bash
.\venv\Scripts\python.exe -m src.kb.evaluate
```
- Ingests, sanitizes PII, standardizes terminology, and deduplicates all raw sources.
- Runs the **5 required test queries** (Product, Policy, Qualification, FAQ, Objection).
- Generates `test_runs/q2_retrieval_benchmark_report.md` with 100% correct verdicts.

### Step 2: Run Question 1 Automated Test Calls & Audio Recording
```bash
.\venv\Scripts\python.exe test_runs\run_test_calls.py
```
- Executes and records the **5 required conversational scenarios**:
  1. *Cooperative Customer Lead Qualification* (`QUALIFIED`, quote generated)
  2. *Price Objection & Benefit Differentiation* (`QUALIFIED`, Gold benefit matrix)
  3. *Incomplete & Conflicting Details* (`ESCALATED`, Age 67 cutoff per UW_RULE_AGE_01)
  4. *Out-of-Scope Queries & Safe Fallback* (Zero Hallucination)
  5. *Human Assistance Escalation* (`ESCALATED`)
- Synthesizes neural audio clips for each turn into `test_runs/call_x/audio/`.
- Exports diarized transcripts (`transcript.md` and `transcript.json`).
- Updates `test_runs/q1_test_calls_summary_report.md`.

### Step 3: Launch the Interactive Web Calling Interface
```bash
.\venv\Scripts\uvicorn.exe src.web.app:app --port 8000 --reload
```
Open your browser at **`http://localhost:8000`** to experience:
- 🎙️ Interactive voice calling with browser microphone or quick-test buttons.
- 👩‍⚕️ Real-time neural voice playback for Sarah.
- 🌊 Animated canvas soundwave visualizer.
- 💬 Live diarized conversation transcript.
- 🔗 Clickable Knowledge Base citation pills showing `record_id` and provenance.
- 📋 Live CRM Lead Qualification Card updating in real-time.

---

## 📊 Benchmark & Evaluation Results Summary

### Question 2 Retrieval Accuracy (5/5 Correct)
| Query | Category | Top Retrieved Record | Source | Verdict |
|---|---|---|---|---|
| *"What benefits are included in Gold compared to Silver?"* | `product` | `kb_product_001` | `apexcare_plans_web.html#tier-comparison-matrix` | ✅ **Correct** |
| *"What is the waiting period for pre-existing hypertension?"* | `policy` | `kb_objection_003` | `faq_objection_guide.txt#OBJECTION_3` | ✅ **Correct** |
| *"Can a 67-year-old retired applicant qualify for Standard?"* | `qualification` | `kb_qualification_001` | `underwriting_rules.json#UW_RULE_AGE_01` | ✅ **Correct** |
| *"How do I file a cashless claim at a network hospital?"* | `faq` | `kb_faq_001` | `apexcare_plans_web.html#cashless-claims` | ✅ **Correct** |
| *"Why is your monthly premium higher than basic plans?"* | `objection` | `kb_objection_001` | `faq_objection_guide.txt#OBJECTION_1` | ✅ **Correct** |

### Question 1 Test Calls Coverage
- **5 Full Audio Call Folders**: Located in [`test_runs/`](file:///d:/PROJECTS/Darwix%20Assignment/test_runs/) with `.mp3` recordings.
- **Traceable Grounding**: All policy statements link to `record_id` (e.g. `kb_qualification_001`).
- **Safe Fallback**: Out-of-scope questions (Call 4) return exact grounded fallback without inventing answers.
- **Business Action**: Verified mock CRM leads stored in [`data/processed/mock_crm_leads.json`](file:///d:/PROJECTS/Darwix%20Assignment/data/processed/mock_crm_leads.json).
