#Flash Narrative ✨

AI-Powered Real-Time Public Relations Monitoring & Analysis

This prototype was built in 72 hours for the Zenith Bank Hackathon 2025 [cite: A, B]. It is a high-fidelity, functional prototype of a SaaS platform designed to help bank reputation managers proactively monitor media, analyze sentiment, and track competitors.

###1. The Problem (Banking Reputation)Banks face intense public scrutiny. Reputation management teams struggle to track mentions across vast news, blog, and social landscapes, often missing critical real-time sentiment shifts concerning products (app downtime, card issues), services (customer support), or executive actions.Standard tools lack nuanced sentiment (e.g., 'anger' vs. 'negative') and cannot measure PR-specific KPIs like Message Penetration or Share of Voice against competitors, delaying crisis response and hindering proactive reputation management.

##2. Our Solution (The "Offline-First" Demo)To ensure a fast, reliable, and 100% functional prototype that adheres to the hackathon's "no access to live... production APIs" [cite: D] rule, we built this app in "Demo Mode."Instead of risking a live API call on event Wi-Fi, our app:Loads a Pre-Analyzed Dataset: Ingests a demo_data.csv file containing real (but "canned") mentions for Zenith Bank and its competitors.Runs Live Local Analysis: The app does not just display static data. It runs its own Python analysis engine (analysis.py) live to:Perform nuanced Sentiment Analysis (e.g., 'anger', 'positive') using a custom keyword engine.Perform Thematic Categorization (e.g., 'CSR/ESG', 'Corporate', 'Legal/Risk').Identify all Mentioned Brands for SOV.Calculate all KPIs (MIS, MPI, SOV, etc.) in real-time.Simulates AI Reporting: Instantly loads a pre-written, professional AI summary (demo_ai_summary.txt) to simulate a live LLM's output.This approach proves our core analysis engine is functional, fast, and ready for integration with live APIs.

###3. Key Features (What you'll see)Styled KPI Dashboard: 4 key metrics (MIS, MPI, Engagement, Reach) that are styled red or green based on custom thresholds set in the sidebar.Sentiment Analysis: A doughnut chart breaking down all mentions by 6 nuanced sentiments.Thematic Analysis: A bar chart (inspired by the Fidelity report [cite: 565-576]) showing the percentage of mentions related to Corporate, CSR/ESG, Product/Service, etc.Share of Voice (SOV): A bar chart comparing Zenith Bank's media presence against its key competitors.Keyword Extraction: An NLTK-powered table showing the top 10 trending keywords and phrases.Automated Reporting:PDF Report: Generates a multi-page PDF report with all charts, KPIs, and the full professional AI summary.Excel Export: Generates a detailed .xlsx file of all analyzed mention data.Email Sending: Integrates with SMTP to email both reports to any stakeholder.

###4. Tech Stack (Hackathon Build)Core: PythonFrontend & UI: Streamlit, Plotly ExpressData Analysis: Pandas, NLTKReport Generation: ReportLab, Matplotlib, OpenpyxlAlerting (Simulation): SMTPlib, ServiceNow API (via requests)Environment: Conda

###5. How to Run This Demo:

Clone the Repo:git clone [https://github.com/n0telvispresley/zecathon-flash-narrative.git](https://github.com/n0telvispresley/zecathon-flash-narrative.git)
cd zecathon-flash-narrative
Create & Activate Conda Environment:conda create -n zecathon python=3.11
conda activate zecathon
Install Dependencies:pip install -r requirements.txt
Run the App:streamlit run app.py

###6. Scalability & Production Roadmap (Beyond the Hackathon)
This Streamlit app is our proven prototype. For "wide-scale adoption" [cite: E], our architecture evolves:

Backend: The core Python logic (analysis.py, report_gen.py) and AI modules (bedrock.py, gemini.py) are exposed as a FastAPI backend.

Frontend: We build a production-grade React or Next.js frontend for a fast, custom, multi-tenant client experience.

Data: The demo_loader.py is replaced with live API clients for NewsAPI, X (Twitter) Pro API, and Brandwatch (for FB/IG).

Database: demo_data.csv is replaced by a scalable PostgreSQL or MongoDB database to store millions of mentions
