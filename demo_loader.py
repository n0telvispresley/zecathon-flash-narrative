import pandas as pd
import streamlit as st
import os

# --- Constants ---
DATA_FILE = "demo_data.csv"
SUMMARY_FILE = "demo_ai_summary.txt"

# --- Main Functions ---

@st.cache_data(ttl=600) # Cache the data for 10 minutes
def load_data_from_csv():
    """
    Loads the pre-compiled demo data from the CSV file.
    This is now CASE-INSENSITIVE and column-order independent.
    It maps known columns and adds defaults for missing KPI columns.
    """
    try:
        # We assume the CSV is in the root folder with the script
        df = pd.read_csv(DATA_FILE)
        
        # --- NEW ROBUST LOADER ---
        # 1. Standardize all column headers: lowercase and stripped of spaces
        original_columns = df.columns
        df.columns = [str(col).lower().strip() for col in df.columns]
        
        # 2. Define all possible user-facing names (lowercase) 
        #    and their internal app names
        column_map = {
            # App Internal Name: [Possible User CSV Names (all lowercase)]
            'date': ['date'],
            'source': ['source'],
            'text': ['text', 'mention text', 'headline', 'content'], # Will map 'Mention Text' to 'text'
            'link': ['link', 'url'],
            'likes': ['likes'],
            'comments': ['comments'],
            'reach': ['reach'],
            'authority': ['authority'],
            'mentioned_brands': ['mentioned_brands', 'mentioned_brand'] # Handles singular/plural
        }

        # 3. Create a new, clean DataFrame to build
        clean_df = pd.DataFrame()
        mapped_internal_names = []

        # 4. Loop through our app's needs and find the first matching column
        for internal_name, possible_user_names in column_map.items():
            for user_name in possible_user_names:
                if user_name in df.columns:
                    clean_df[internal_name] = df[user_name]
                    mapped_internal_names.append(internal_name)
                    break # Found the best match, move to next internal name

        # 5. Check for ABSOLUTE minimum required columns
        required_for_analysis = ['text', 'date', 'source']
        missing_essentials = set(required_for_analysis) - set(clean_df.columns)
        if missing_essentials:
            st.error(f"Demo data CSV is invalid! It MUST contain columns for: {', '.join(required_for_analysis)}")
            return []

        # 6. Add default values for optional KPI columns if they weren't found
        if 'likes' not in clean_df.columns: clean_df['likes'] = 0
        if 'comments' not in clean_df.columns: clean_df['comments'] = 0
        if 'reach' not in clean_df.columns: clean_df['reach'] = 1000 # Default reach
        if 'authority' not in clean_df.columns: clean_df['authority'] = 5 # Default authority
            
        # These columns will be CREATED by analysis.py, so we don't need defaults:
        # - sentiment
        # - theme
        # - mentioned_brands (analysis.py creates this, but we map it just in case)
        
        # --- END OF FIX ---
            
        print("Demo data loaded, columns standardized and mapped successfully.")
        # Convert DataFrame to the dictionary format our app expects
        return clean_df.to_dict('records')
        
    except FileNotFoundError:
        st.error(f"FATAL: '{DATA_FILE}' not found! Please add it to the root folder.")
        print(f"FATAL: '{DATA_FILE}' not found. Please add it to the project's root directory.")
        return []
    except Exception as e:
        st.error(f"An error occurred while loading {DATA_FILE}: {e}")
        print(f"An error occurred while loading {DATA_FILE}: {e}")
        return []

@st.cache_data(ttl=3600) # Cache the summary for 1 hour
def load_ai_summary():
    """
    Loads the pre-written, professional AI summary from a text file.
    This simulates the call to bedrock_llm.generate_llm_report_summary().
    """
    try:
        with open(SUMMARY_FILE, "r") as f:
            summary_text = f.read()
        print("Demo AI summary loaded from .txt file successfully.")
        return summary_text
    except FileNotFoundError:
        st.error(f"FATAL: '{SUMMARY_FILE}' not found! Please add it to the root folder.")
        print(f"FATAL: '{SUMMARY_FILE}' not found. Please add it to the project's root directory.")
        return "**Error:** AI Summary file ('demo_ai_summary.txt') not found. Could not generate report."
    except Exception as e:
        st.error(f"An error occurred while loading {SUMMARY_FILE}: {e}")
        print(f"An error occurred while loading {SUMMARY_FILE}: {e}")
        return f"**Error:** Could not read AI summary file: {e}"

# --- Self-Test (for debugging) ---
if __name__ == "__main__":
    # This allows you to test this file directly
    print("Running demo_loader.py self-test...")
    
    # Test data loading
    data = load_data_from_csv()
    if data:
        print(f"Successfully loaded {len(data)} mentions.")
        print("First mention sample (after renaming):")
        # Print only the keys we expect to be there
        if data[0]:
            print({
                'text': data[0].get('text', 'N/A')[:50] + "...",
                'sentiment': data[0].get('sentiment', 'N/A'),
                'theme': data[0].get('theme', 'N/A'),
                'mentioned_brands': data[0].get('mentioned_brands', 'N/A'),
                'reach': data[0].get('reach', 'N/A')
            })
    else:
        print("Data loading FAILED.")
        
    print("-" * 20)
    
    # Test summary loading
    summary = load_ai_summary()
    if "Error:" not in summary:
        print("Successfully loaded AI summary:")
        print(summary[:150] + "...")
    else:
        print("AI summary loading FAILED.")