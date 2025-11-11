import streamlit as st
import base64
import os

# --- Helper function to load images for CSS ---
@st.cache_data
def get_base64_of_bin_file(bin_file):
    """ Reads a binary file and returns its Base64 encoded string. """
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        print(f"Image file not found: {bin_file}")
        return None

# --- Page Configuration (Set first) ---
# This MUST be the first Streamlit command
st.set_page_config(
    page_title="Flash Narrative - Login",
    page_icon="fn logo.jpeg", # <-- 1. SETS BROWSER TAB ICON
    layout="wide",
    initial_sidebar_state="collapsed" # Hide sidebar on login page
)

# --- Brand Colors & Custom CSS ---
GOLD = "#FFD700"
BLACK = "#000000"
BEIGE = "#F5F5DC"
DARK_BG = "#1E1E1E"
LIGHT_TEXT = "#EAEAEA"

# --- 2. LOAD BACKGROUND IMAGE ---
# This path is correct because app.py is in the root folder
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
        z-index: -1; /* Put it behind all content */
    }}
    /* --- END Watermark --- */
"""

custom_css = f"""
<style>
    {bg_image_css if bg_image_base64 else "/* Background image not found */"}

    /* Main App Background */
    .stApp {{
        background-color: transparent; /* Show watermark */
        color: {LIGHT_TEXT};
    }}
    /* Make main content area dark again */
    [data-testid="stAppViewContainer"] > .main {{
        background-color: {DARK_BG};
    }}
    
    /* Hide the sidebar on the login page */
    [data-testid="stSidebar"] {{
        display: none;
    }}

    /* Style the login container */
    .login-container {{
        background-color: {BLACK};
        border: 1px solid {GOLD};
        border-radius: 10px;
        padding: 2.5rem 2rem;
        margin-top: 5rem;
        box-shadow: 0px 4px 15px rgba(255, 215, 0, 0.1);
    }}

    /* Main Content Headers */
    .stApp h1, .stApp h2, .stApp h3 {{
        color: {GOLD};
        text-align: center;
    }}
    .stApp h3 {{
        color: {BEIGE};
        font-weight: 300;
    }}

    /* Buttons */
    .stButton>button {{
        width: 100%;
        background-color: {GOLD};
        color: {BLACK};
        border: 1px solid {GOLD};
        border-radius: 5px;
        font-weight: bold;
        font-size: 1.1em;
    }}
    .stButton>button:hover {{
        background-color: {BLACK};
        color: {GOLD};
        border: 1px solid {GOLD};
    }}

    /* Inputs */
    .stTextInput input, .stTextArea textarea {{
        background-color: {DARK_BG};
        color: {LIGHT_TEXT};
        border: 1px solid {BEIGE};
    }}
    .stTextInput label, .stCheckbox label {{
        color: {LIGHT_TEXT} !important;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

def login_form():
    """Creates and handles the login form, centered on the page."""
    
    # --- 3. USE YOUR LOGO IMAGE ---
    # This path is correct because app.py is in the root
    st.image("fn full.jpeg", width=200) 
    st.header("Flash Narrative")
    st.subheader("AI-Powered PR Intelligence")
    
    with st.form(key="login_form"):
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        st.empty() # Add a little space
        submit_button = st.form_submit_button(label="Login")
        
        if submit_button:
            # --- Hardcoded credentials for the Zecathon demo ---
            if username == "zenith" and password == "pass":
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun() # Rerun the script to trigger the redirect
            else:
                st.error("Invalid username or password")

def main():
    """Main app router."""
    
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # Check login status
    if st.session_state["logged_in"]:
        # If logged in, show success and redirect
        st.success("Login Successful! Redirecting to dashboard...")
        st.switch_page("pages/dashboard.py")
    else:
        # If not logged in, show the login form
        # We use columns to center the form nicely
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        with col2:
            # Apply the custom container class
            with st.container():
                st.markdown('<div class="login-container">', unsafe_allow_html=True)
                login_form()
                st.markdown('</div>', unsafe_allow_html=True)
        with col1: st.empty()
        with col3: st.empty()

if __name__ == "__main__":
    main()