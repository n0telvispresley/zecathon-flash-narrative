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
    except Exception as e:
        print(f"Error loading image {bin_file}: {e}")
        return None

# --- Page Configuration (Set first) ---
st.set_page_config(
    page_title="Flash Narrative - Login",
    page_icon="fn logo.jpeg", # Browser tab icon
    layout="wide",
    initial_sidebar_state="collapsed" # Hide sidebar on login page
)

# --- Brand Colors & Custom CSS ---
GOLD = "#FFD700"
BLACK = "#000000"
BEIGE = "#F5F5DC"
DARK_BG = "#1E1E1E"
LIGHT_TEXT = "#EAEAEA"

# --- Load Background Image ---
bg_image_base64 = get_base64_of_bin_file("fn text.jpeg")

bg_image_css = f"""
    /* Semi-Transparent Watermark */
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
        opacity: 0.05;
        z-index: -1;
    }}
"""

custom_css = f"""
<style>
    {bg_image_css if bg_image_base64 else "/* Background image not found */"}

    .stApp {{ background-color: transparent; color: {LIGHT_TEXT}; }}
    [data-testid="stAppViewContainer"] > .main {{ background-color: {DARK_BG}; }}
    [data-testid="stSidebar"] {{ display: none; }}

    /* This centers the login box vertically */
    .st-emotion-cache-1jicfl2 {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 80vh;
    }}

    .login-container {{
        background-color: {BLACK};
        border: 1px solid {GOLD};
        border-radius: 10px;
        padding: 2.5rem 2rem;
        box-shadow: 0px 4px 15px rgba(255, 215, 0, 0.1);
    }}
    
    /* This rule was bad and has been removed. We will center the image with columns. */

    .login-container h1, .login-container h2, .login-container h3 {{
        color: {GOLD};
        text-align: center;
    }}
    .login-container h3 {{ color: {BEIGE}; font-weight: 300; }}

    .stButton>button {{
        width: 100%; background-color: {GOLD}; color: {BLACK};
        border: 1px solid {GOLD}; border-radius: 5px;
        font-weight: bold; font-size: 1.1em;
        margin-top: 1.5rem; /* <-- THIS REPLACES st.empty() */
    }}
    .stButton>button:hover {{ background-color: {BLACK}; color: {GOLD}; border: 1px solid {GOLD}; }}
    .stTextInput input {{ background-color: {DARK_BG}; color: {LIGHT_TEXT}; border: 1px solid {BEIGE}; }}
    .stTextInput label, .stCheckbox label {{ color: {LIGHT_TEXT} !important; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

def login_form():
    """Creates and handles the login form, centered on the page."""
    
    # --- THIS IS THE FIX for CENTERING THE IMAGE ---
    # We use columns to force the image into the middle
    img_col1, img_col2, img_col3 = st.columns([1, 1, 1])
    with img_col2:
        st.image("fn full.jpeg", width=200) 
    # --- END OF FIX ---

    st.header("Flash Narrative")
    st.subheader("AI-Powered PR Intelligence")
    
    with st.form(key="login_form"):
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        # --- THIS IS THE FIX for the "frame" ---
        # st.empty() has been REMOVED.
        # --- END OF FIX ---
        
        submit_button = st.form_submit_button(label="Login")
        
        if submit_button:
            if username == "zenith" and password == "pass":
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("Invalid username or password")

def main():
    """Main app router."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        st.success("Login Successful! Redirecting to dashboard...")
        st.switch_page("pages/dashboard.py")
    else:
        # Columns to center the form horizontally
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        with col2:
            # We must wrap the login_form() call *inside* the st.markdown
            # to apply the .login-container style
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            login_form()
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()