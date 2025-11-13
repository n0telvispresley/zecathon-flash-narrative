# ✨ Flash Narrative (Zecathon 2025 Build)

**AI-Powered Reputation Intelligence Dashboard for Banking**

> _“From reactive crisis response to proactive narrative control.”_

This is a **high-fidelity, fully functional prototype** built in **72 hours** for the **Zenith Bank Hackathon 2025** [[A]](https://zecathon2025.devpost.com), [[B]](https://github.com/n0telvispresley/zecathon-flash-narrative).  
It delivers a **faster, smarter, and proactive** approach to brand reputation management in the high-stakes financial sector.

---

## 🚀 LIVE DEMO

Test the **fully interactive, styled, and offline-first** prototype here:  
[https://zecathon-flash-narrative.streamlit.app/dashboard](https://zecathon-flash-narrative.streamlit.app/dashboard)

- **Login**: `zenith`
- **Password**: `pass`

> **Note**: Per the hackathon rule — _"no live APIs allowed"_ [[D]](#references) — this demo runs in **100% reliable Offline-First mode**. See ["Hackathon Strategy"](#our-hackathon-strategy-reliability-first) below.

---

## 1. The Problem: A Reactive Reputation

In banking, **reputation is capital**. Yet PR teams face systemic bottlenecks:

| Challenge                | Impact                                                                   |
| ------------------------ | ------------------------------------------------------------------------ |
| **Data Overload**        | Manual tracking of news, blogs, and social media is impossible           |
| **Delayed Insights**     | Negative stories escalate before detection                               |
| **Superficial Analysis** | Tools report “positive/negative” but miss **Anger** vs. **Appreciation** |
| **No Measurable ROI**    | PR value unproven — no SOV, MPI, or campaign attribution                 |

---

## 2. Our Solution: Flash Narrative

**Flash Narrative** transforms reputation management from **reactive** to **proactive**.

Instead of _showing data_, it **delivers answers**.

### Core Capabilities

| Feature                   | Value                                                                                              |
| ------------------------- | -------------------------------------------------------------------------------------------------- |
| **Nuanced Sentiment**     | Detects **Anger** (high-risk) vs. **Negative** (mild)                                              |
| **Thematic Intelligence** | Auto-categorizes articles: _Corporate, CSR/ESG, Product/Service, Legal/Risk_                       |
| **PR-Specific KPIs**      | Tracks **Share of Voice (SOV)**, **Message Penetration Index (MPI)**, **Media Impact Score (MIS)** |
| **One-Click Reporting**   | Generates **PDF, Excel, and Email-ready** reports with **AI-driven summaries & recommendations**   |

---

## 3. Our Hackathon Strategy: Reliability First

> **Rule**: _“No access to live banking or production APIs”_ [[D]](#references)

We turned this constraint into a **strength**.

An app that crashes during demo due to Wi-Fi is **not feasible**.  
So we built **Flash Narrative** in **100% reliable Offline-First mode**:

| Component                | Implementation                                                                             |
| ------------------------ | ------------------------------------------------------------------------------------------ |
| **Real Dataset**         | `demo_data.csv` — 600+ real Zenith & competitor media mentions (manually curated)          |
| **Live Local Engine**    | On “Run Analysis”, the app **processes all 600+ rows in real-time** using:                 |
|                          | → Sentiment engine (`analysis.py`)                                                         |
|                          | → Thematic categorization                                                                  |
|                          | → Brand extraction (SOV)                                                                   |
|                          | → KPI calculations (MIS, MPI, Reach)                                                       |
| **Simulated AI Summary** | `demo_ai_summary.txt` — pre-written, professional-grade LLM output to prove report quality |

> **Result**: A **fully working, fast, and demo-proof** system — no API timeouts, no latency.

---

## 4. Tech Stack

| Layer             | Technology                                             |
| ----------------- | ------------------------------------------------------ |
| **Core**          | Python 3.11                                            |
| **Frontend**      | Streamlit + **custom Zenith-branded CSS**              |
| **Analysis**      | Pandas, NLTK (keyword/phrase extraction)               |
| **Visualization** | Plotly Express                                         |
| **Reports**       | ReportLab (PDF), Matplotlib (charts), Openpyxl (Excel) |
| **Email/Alerts**  | SMTPlib (email), ServiceNow (simulated)                |
| **Environment**   | Conda                                                  |

---

## 5. Evaluation Criteria: How We Excel [[E]](#references)

| Criteria        | Our Response                                                                                                                                                                  |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Innovation**  | • **Nuanced Sentiment**: Anger vs. Appreciation <br>• **MPI**: Rare KPI for message landing <br>• **Thematic Audit**: Inspired by Fidelity’s media reports [[F]](#references) |
| **Feasibility** | • **100% functional now** <br>• Live analysis engine proven <br>• API integration = plug-and-play                                                                             |
| **Impact**      | • **Crisis prevention** (e.g., app downtime anger detection) <br>• **90% automation** of PR workflows <br>• **Executive-ready reports**                                       |
| **Scalability** | **Phase 1**: Streamlit prototype (now) <br>**Phase 2**: FastAPI backend <br>**Phase 3**: React frontend + PostgreSQL + live APIs (NewsAPI, X Pro, Brandwatch)                 |

---

## 6. Presentation & UX

- **Branded UI**: Gold, black, and beige — **Zenith Bank identity**
- **Logical Flow**: KPIs → Charts → Tables → Reports
- **Professional Outputs**: PDF/Excel reports **ready for C-suite**

---

## 7. How to Run Locally

```bash
# 1. Clone
git clone https://github.com/n0telvispresley/zecathon-flash-narrative.git
cd zecathon-flash-narrative

# 2. Create environment
conda create -n zecathon python=3.11
conda activate zecathon

# 3. Install
pip install -r requirements.txt

# 4. Run
streamlit run app.py
```
