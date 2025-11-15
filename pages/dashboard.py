import streamlit as st
import pandas as pd
import plotly.express as px
import traceback
import io
from collections import Counter
import os
import base64 # Import Base64

# --- Helper function to load images for CSS ---
@st.cache_data
def get_base64_of_bin_file(bin_file):
    """ Reads a binary file and returns its Base64 encoded string. """
    try:
        # The path must be relative to the root of the project
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        print(f"Image file not found: {bin_file}")
        return None
    except Exception as e:
        print(f"Error loading image {bin_file}: {e}")
        return None

# --- Page Config (MUST be first Streamlit command) ---
st.set_page_config(
    page_title="Dashboard | Flash Narrative",
    page_icon="fn logo.jpeg", # Browser tab icon
    layout="wide"
)

# --- Imports (Relative imports) ---
try:
    from .. import analysis
    from .. import report_gen
    from .. import demo_loader # Use our offline loader
    from .. import servicenow_integration # For alert simulation
except ImportError:
    # Fallback for local testing
    import analysis, report_gen, demo_loader, servicenow_integration
except Exception as e:
    st.error(f"Failed to import modules: {e}")
    st.stop()


# --- Brand Colors & Custom CSS ---
GOLD = "#FFD700"; BLACK = "#000000"; BEIGE = "#F5F5DC"
DARK_BG = "#1E1E1E"; LIGHT_TEXT = "#EAEAEA"
GREEN_BG = "#28a745"; RED_BG = "#dc3545"

# --- Load Background Image ---
bg_image_base64 = get_base64_of_bin_file("fn text.jpeg") 

bg_image_css = f"""
    /* --- NEW: Semi-Transparent Watermark --- */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100vw;
        height: 100vh;
        background-image: url("data:image/jpeg;base64,{bg_image_base64}");
        background-position: center;
        background-repeat: no-repeat;
        background-size: cover; 
        opacity: 0.05; /* 5% transparent */
        z-index: -1; 
    }}
"""

custom_css = f"""
<style>
    {bg_image_css if bg_image_base64 else "/* Background image not found */"}

    /* Main App Background */
    .stApp {{ background-color: transparent; color: {LIGHT_TEXT}; }}
    [data-testid="stAppViewContainer"] > .main {{ background-color: {DARK_BG}; }}
    
    /* Sidebar */
    [data-testid="stSidebar"] > div:first-child {{ background-color: {BLACK}; border-right: 1px solid {GOLD}; }}
    [data-testid="stSidebar"] .st-emotion-cache-16txtl3 {{ color: {BEIGE}; }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{ color: {GOLD}; }}
    /* Main Content Headers */
    .stApp h1, .stApp h2, .stApp h3 {{ color: {GOLD}; }}
    /* Buttons */
    .stButton>button {{ background-color: {GOLD}; color: {BLACK}; border: 1px solid {GOLD}; border-radius: 5px; padding: 0.5em 1em; }}
    .stButton>button:hover {{ background-color: {BLACK}; color: {GOLD}; border: 1px solid {GOLD}; }}
    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {{ background-color: {DARK_BG}; color: {LIGHT_TEXT}; border: 1px solid {BEIGE}; border-radius: 5px; }}
    /* Selectbox */
    .stSelectbox div[data-baseweb="select"] > div {{ background-color: {DARK_BG}; color: {LIGHT_TEXT}; border: 1px solid {BEIGE}; }}
    /* Dataframes */
    .stDataFrame {{ border: 1px solid {BEIGE}; border-radius: 5px; }}
    .stDataFrame thead th {{ background-color: {BLACK}; color: {GOLD}; }}
    .stDataFrame tbody tr {{ background-color: {DARK_BG}; color: {LIGHT_TEXT}; }}
    .stDataFrame tbody tr:nth-child(even) {{ background-color: #2a2a2a; }}
    /* Expander */
    .streamlit-expanderHeader {{ background-color: {BLACK}; color: {GOLD}; border: 1px solid {GOLD}; border-radius: 5px; }}
    /* KPI Boxes */
    .kpi-box {{ border: 1px solid {BEIGE}; border-radius: 5px; padding: 15px; text-align: center; margin-bottom: 10px; background-color: {DARK_BG}; }}
    .kpi-box .label {{ font-size: 0.9em; color: {BEIGE}; margin-bottom: 5px; text-transform: uppercase; line-height: 1.2; height: 2.4em; display: flex; align-items: center; justify-content: center; }}
    .kpi-box .value {{ font-size: 1.5em; font-weight: bold; color: {LIGHT_TEXT}; }}
    .kpi-box.good {{ background-color: {GREEN_BG}; border-color: {GREEN_BG}; }}
    .kpi-box.good .label, .kpi-box.good .value {{ color: {BLACK}; }}
    .kpi-box.bad {{ background-color: {RED_BG}; border-color: {RED_BG}; }}
    .kpi-box.bad .label, .kpi-box.bad .value {{ color: {LIGHT_TEXT}; }}
    
    /* --- NEW: Make Title Logo Round --- */
    div[data-testid="stHorizontalBlock"]:first-of-type [data-testid="stImage"] img {{
        border-radius: 50%; /* Make it a circle */
        border: 2px solid {GOLD}; /* Add gold border */
        box-shadow: 0 0 10px {GOLD}; /* Add a glow */
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


def run_analysis_from_demo(brand, competitors, campaign_messages):
    """
    Runs the full analysis using ONLY the local demo CSV file.
    """
    try:
        with st.spinner("Loading demo data..."):
            full_data = demo_loader.load_data_from_csv()
        if not full_data:
            st.error("Demo data file 'demo_data.csv' is missing or empty!"); st.stop()

        with st.spinner("Analyzing data and calculating KPIs..."):
            kpi_results = analysis.compute_kpis(
                full_data=full_data,
                campaign_messages=campaign_messages,
                brand=brand,
                competitors=competitors
            )
        
        st.session_state.kpis = kpi_results
        st.session_state.full_data = kpi_results.get('analyzed_data', [])
        all_text = " ".join([item.get("text", "") for item in st.session_state.full_data])
        
        # Safely update stopwords and extract keywords
        if hasattr(analysis, 'stop_words') and isinstance(analysis.stop_words, set):
            temp_stop_words = analysis.stop_words.copy()
            temp_stop_words.add(brand.lower())
            for c in competitors:
                temp_stop_words.add(c.lower())
            
            original_stopwords = analysis.stop_words
            analysis.stop_words = temp_stop_words
            st.session_state.top_keywords = analysis.extract_keywords(all_text, brand, competitors)
            analysis.stop_words = original_stopwords
        else:
            st.session_state.top_keywords = analysis.extract_keywords(all_text, brand, competitors)

        st.success("Analysis Complete!")

        sentiment_ratio = st.session_state.kpis.get('sentiment_ratio', {})
        neg_pct = sentiment_ratio.get('negative', 0) + sentiment_ratio.get('anger', 0)
        if neg_pct > 30:
            alert_msg = f"SIMULATED ALERT: High negative sentiment ({neg_pct:.1f}%) detected for {brand}."
            st.error(alert_msg)
            alert_email = os.getenv("ALERT_EMAIL", 'alerts@yourcompany.com')
            servicenow_integration.send_alert(alert_msg, channel='#alerts', to_email=alert_email)
            servicenow_integration.create_servicenow_ticket(f"PR Crisis Alert: {brand}", alert_msg, urgency='1', impact='1')

    except Exception:
        st.error(f"An error occurred during analysis:\n{traceback.format_exc()}")


def display_dashboard(brand, competitors, time_range_text, thresholds):
    """ Displays KPIs with conditional styling, charts, tables, and reports. """
    if not st.session_state.kpis:
        st.info("Click 'Run Analysis' to load your brand data."); return

    st.subheader("Key Performance Indicators")
    kpis = st.session_state.kpis
    mis_val = kpis.get('mis', 0); mpi_val = kpis.get('mpi', 0)
    eng_val = kpis.get('engagement_rate', 0); reach_val = kpis.get('reach', 0)
    
    # Get thresholds from the passed dictionary
    mis_threshold = thresholds.get('mis_good', 100)
    mpi_threshold = thresholds.get('mpi_good', 30) # Use new default
    eng_threshold = thresholds.get('eng_good', 1000) # Use new default
    reach_threshold = thresholds.get('reach_good', 10000000) # Use new default

    # Determine CSS classes
    mis_class = "good" if mis_val >= mis_threshold else "bad"
    mpi_class = "good" if mpi_val >= mpi_threshold else "bad"
    eng_class = "good" if eng_val >= eng_threshold else "bad"
    reach_class = "good" if reach_val >= reach_threshold else "bad"
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f'<div class="kpi-box {mis_class}"><div class="label">Media Impact (MIS)</div><div class="value">{mis_val:.0f}</div></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="kpi-box {mpi_class}"><div class="label">Msg Penetration (MPI)</div><div class="value">{mpi_val:.1f}%</div></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="kpi-box {eng_class}"><div class="label">Avg Social Engagement</div><div class="value">{eng_val:.1f}</div></div>', unsafe_allow_html=True)
    with col4: st.markdown(f'<div class="kpi-box {reach_class}"><div class="label">Total Reach</div><div class="value">{reach_val:,}</div></div>', unsafe_allow_html=True)
    st.caption(f"Thresholds (Good ≥) MIS: {mis_threshold} | MPI: {mpi_threshold}% | Engagement: {eng_threshold} | Reach: {reach_threshold:,}")

    st.subheader("Visual Analysis")
    sentiment_ratio = kpis.get("sentiment_ratio", {})
    if sentiment_ratio:
        pie_data = pd.DataFrame({'Sentiment': list(sentiment_ratio.keys()), 'Percent': list(sentiment_ratio.values())})
        color_map = {'positive': 'green', 'appreciation': 'blue', 'neutral': 'grey', 'mixed': 'orange', 'negative': 'red', 'anger': 'darkred'}
        fig_pie = px.pie(pie_data, names='Sentiment', values='Percent', title="Sentiment Distribution", color='Sentiment', color_discrete_map=color_map, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    else: st.write("No sentiment data.")

    all_brands = kpis.get("all_brands", [brand] + competitors)
    sov_values = kpis.get("sov", [])
    if len(sov_values) != len(all_brands):
        st.warning(f"SOV data mismatch. Brands: {len(all_brands)}, Values: {len(sov_values)}. Chart may be incomplete.")
    sov_df = pd.DataFrame({'Brand': all_brands, 'Share of Voice (%)': sov_values})
    fig_sov = px.bar(sov_df, x='Brand', y='Share of Voice (%)', title="Share of Voice (SOV)", color='Brand')
    st.plotly_chart(fig_sov, use_container_width=True)
    
    theme_ratio = kpis.get("theme_ratio", {})
    if theme_ratio:
        theme_data = pd.DataFrame({'Theme': list(theme_ratio.keys()), 'Percent': list(theme_ratio.values())})
        theme_data = theme_data.sort_values(by='Percent', ascending=False)
        fig_theme = px.bar(theme_data, x='Theme', y='Percent', title="Top Mention Themes", color='Theme')
        st.plotly_chart(fig_theme, use_container_width=True)
    else: st.write("No theme data.")

    st.subheader("Detailed Mentions")
    st.markdown("**Top Keywords & Phrases**")
    top_keywords = st.session_state.top_keywords
    if top_keywords: st.dataframe(pd.DataFrame(top_keywords, columns=['Keyword/Phrase', 'Frequency']), use_container_width=True)
    else: st.write("- No keywords/phrases.")

    st.markdown("**Recent Mentions (All Brands)**")
    if st.session_state.full_data:
        display_data = [{'Sentiment': item.get('sentiment', 'N/A'), 'Theme': item.get('theme', 'N/A'), 'Source': item.get('source', 'N/A'), 'Mention': item.get('text', '')[:150]+"...", 'Link': item.get('link', '#')} for item in st.session_state.full_data[:30]]
        st.dataframe(pd.DataFrame(display_data), column_config={"Link": st.column_config.LinkColumn("Link", display_text="Source Link")}, use_container_width=True, hide_index=True)
    else: st.write("No mentions.")

    st.subheader("Generate & Send Report")
    recipient_email = st.text_input("Enter Email to Send Reports To:", placeholder="your.email@example.com", key="recipient_email_input")

    if st.button("Generate Reports for Email/Download", use_container_width=True, key="generate_reports"):
        if not st.session_state.kpis or not st.session_state.full_data:
            st.warning("Please run analysis first."); st.session_state.report_generated = False
        else:
            st.session_state.report_generated = False; pdf_generated = False; excel_generated = False
            with st.spinner("Building AI Report Summary..."):
                ai_summary = demo_loader.load_ai_summary() 
                st.session_state.ai_summary_text = ai_summary
            with st.spinner("Building PDF report..."):
                try:
                    md, pdf_bytes = report_gen.generate_report(kpis=st.session_state.kpis, top_keywords=st.session_state.top_keywords, full_articles_data=st.session_state.full_data, brand=brand, competitors=competitors, timeframe_hours=time_range_text, include_json=False)
                    st.session_state.pdf_report_bytes = pdf_bytes; pdf_generated = True
                except Exception as e: st.error(f"Failed PDF generation: {e}\n{traceback.format_exc()}")
            with st.spinner("Building Excel mentions file..."):
                try:
                    excel_data = [{'Date': item.get('date', 'N/A'), 'Sentiment': item.get('sentiment', 'N/A'), 'Theme': item.get('theme', 'N/A'), 'Source': item.get('source', 'N/A'), 'Mention Text': item.get('text', ''), 'Link': item.get('link', '#'), 'Likes': item.get('likes', 0), 'Comments': item.get('comments', 0), 'Reach': item.get('reach', 0)} for item in st.session_state.full_data]
                    df_excel = pd.DataFrame(excel_data); output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer: df_excel.to_excel(writer, index=False, sheet_name='Mentions')
                    st.session_state.excel_report_bytes = output.getvalue(); excel_generated = True
                except Exception as e: st.error(f"Failed Excel generation: {e}")
            if pdf_generated and excel_generated:
                st.session_state.report_generated = True; st.success("Reports Generated!")
                with st.expander("View AI Summary & Recommendations", expanded=True): st.markdown(st.session_state.ai_summary_text)
            else: st.error("Report generation failed.")

    if st.session_state.get('report_generated', False):
        st.markdown("---")
        col_dl_pdf, col_dl_excel, col_email = st.columns(3)
        with col_dl_pdf:
            if st.session_state.get('pdf_report_bytes'): st.download_button("Download PDF", st.session_state.pdf_report_bytes, f"{brand}_Report.pdf", "application/pdf", use_container_width=True, key="pdf_dl")
            else: st.button("Download PDF", disabled=True, use_container_width=True, help="PDF failed.")
        with col_dl_excel:
            if st.session_state.get('excel_report_bytes'): st.download_button("Download Excel", st.session_state.excel_report_bytes, f"{brand}_Mentions.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key="excel_dl")
            else: st.button("Download Excel", disabled=True, use_container_width=True, help="Excel failed.")
        with col_email:
            email_to_send = st.session_state.get("recipient_email_input", "")
            files_ready = st.session_state.get('pdf_report_bytes') and st.session_state.get('excel_report_bytes')
            if not email_to_send: st.button("Email Reports", disabled=True, use_container_width=True, help="Enter email.")
            elif not files_ready: st.button("Email Reports", disabled=True, use_container_width=True, help="Files not ready.")
            elif st.button("Email Reports", use_container_width=True, key="email_reports"):
                with st.spinner(f"Sending to {email_to_send}..."):
                    try:
                        attachments = [(f"{brand}_Report.pdf", st.session_state.pdf_report_bytes, 'application/pdf'), (f"{brand}_Mentions.xlsx", st.session_state.excel_report_bytes, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')]
                        subject = f"FlashNarrative Report: {brand} ({time_range_text})"
                        # Use simple body text
                        body = f"Hello!\n\nPlease find attached the requested reports for {brand}.\n\nKind regards,\nThe Flash Narrative Team"
                        sent = servicenow_integration.send_report_email_with_attachments(email_to_send, subject, body, attachments)
                        if sent: st.toast(f"✅ Reports emailed to {email_to_send}!", icon="🎉"); st.success(f"Emailed to {email_to_send}!")
                        else: st.toast("❌ Email failed. Check logs/settings.", icon="🔥"); st.error("Email failed. Check logs & .env (Use App Password?).")
                    except Exception as e:
                        st.error(f"Email failed. Is 'servicenow_integration.py' missing? Error: {e}")


def main():
    """ Main function to run the Streamlit app. """
    # --- Page Config is now at the top ---
    
    if not st.session_state.get('logged_in', False):
        st.error("You must be logged in..."); st.page_link("app.py", label="Login", icon="🔒"); st.stop()

    # --- NEW: Title with Logo ---
    logo_col, title_col = st.columns([0.1, 0.9])
    with logo_col:
        st.image("fn logo.jpeg", width=60) # Small logo
    with title_col:
        st.title("Flash Narrative AI Dashboard")
    st.markdown("Monitor brand perception in real-time.")
    # --- END NEW: Title with Logo ---

    # Init State
    if 'full_data' not in st.session_state: st.session_state.full_data = []
    if 'kpis' not in st.session_state: st.session_state.kpis = {}
    if 'top_keywords' not in st.session_state: st.session_state.top_keywords = []
    if 'report_generated' not in st.session_state: st.session_state.report_generated = False
    if 'pdf_report_bytes' not in st.session_state: st.session_state.pdf_report_bytes = None
    if 'excel_report_bytes' not in st.session_state: st.session_state.excel_report_bytes = None
    if 'ai_summary_text' not in st.session_state: st.session_state.ai_summary_text = ""

    # --- KPI Threshold Inputs ---
    with st.sidebar:
        st.image("fn logo.jpeg", width=100) # Logo at top of sidebar
        
        st.header("⚙️ Settings")
        st.subheader("KPI Thresholds (Good ≥)")
        # --- UPDATED DEFAULTS ---
        mis_thresh = st.number_input("Media Impact Score (MIS)", min_value=0, value=100, step=10, key="mis_thresh_input")
        mpi_thresh = st.number_input("Message Penetration (%)", min_value=0, max_value=100, value=30, step=5, key="mpi_thresh_input")
        eng_thresh = st.number_input("Avg. Social Engagement", min_value=0.0, value=1000.0, step=10.0, format="%.1f", key="eng_thresh_input")
        reach_thresh = st.number_input("Total Reach", min_value=0, value=10000000, step=10000, key="reach_thresh_input")
        # --- END UPDATED DEFAULTS ---
        
        thresholds = {
            "mis_good": mis_thresh, "mpi_good": mpi_thresh,
            "eng_good": eng_thresh, "reach_good": reach_thresh
        }
        
        st.divider()
        # --- NEW: Logout Button ---
        if st.button("Logout", use_container_width=True, key="logout_button"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            # Clear all session data on logout
            st.session_state.full_data = []
            st.session_state.kpis = {}
            st.session_state.top_keywords = []
            st.session_state.report_generated = False
            st.session_state.pdf_report_bytes = None
            st.session_state.excel_report_bytes = None
            st.session_state.ai_summary_text = ""
            st.rerun() # Rerun to force redirect to login page
        # --- END NEW: Logout Button ---


    # Inputs
    st.subheader("Monitoring Setup")
    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1: brand = st.text_input("Brand Name", value="Zenith Bank", key="brand_input")
    with col_i2:
        # --- UPDATED DEFAULTS ---
        competitors_input = st.text_input("Competitors (comma-separated)", value="Fidelity Bank,GT Bank,Opay", key="comp_input")
        competitors = [c.strip() for c in competitors_input.split(",") if c.strip()]
    with col_i3: industry = st.selectbox("Industry", ['finance', 'default', 'Personal Brand', 'tech', 'healthcare', 'retail'], index=0, help="Affects RSS feed selection.", key="industry_select")

    # --- UPDATED DEFAULTS ---
    campaign_input = st.text_area("Campaign Messages (one per line)", value="Zecathon\nZecathon 5.0", height=100, key="campaign_input")
    campaign_messages = [c.strip() for c in campaign_input.split("\n") if c.strip()]
    
    time_range_text = st.selectbox("Time Frame", ["Last 30 days (Demo)", "Last 7 days", "Last 24 hours"], index=0, key="time_select")
    time_map = {"Last 24 hours": 24, "Last 7 days": 168, "Last 30 days (Demo)": 720}
    hours = time_map[time_range_text]

    # Run Button
    if st.button("Run Analysis", type="primary", use_container_width=True, key="run_analysis_button"):
        st.session_state.full_data = []; st.session_state.kpis = {}; st.session_state.top_keywords = []
        st.session_state.report_generated = False; st.session_state.pdf_report_bytes = None
        st.session_state.excel_report_bytes = None; st.session_state.ai_summary_text = ""
        run_analysis_from_demo(brand, competitors, campaign_messages)

    # Display Results
    display_dashboard(brand, competitors, time_range_text, thresholds)

if __name__ == "__main__":
    main()