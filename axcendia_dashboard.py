import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

# Page setup
st.set_page_config(page_title="Quantanalyser Dashboard", layout="wide")

# ---- AUTHENTICATION ----
CREDENTIALS_FILE = "service_account.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def load_credentials():
    """Safely load and re-encode service account key to handle hidden line breaks."""
    with open(CREDENTIALS_FILE, "r") as f:
        creds_json = json.load(f)
    # Clean key for invalid padding / control characters
    key = creds_json["private_key"].replace("\r", "").replace("\n", "\\n")
    creds_json["private_key"] = key
    return Credentials.from_service_account_info(creds_json, scopes=SCOPES)

try:
    creds = load_credentials()
    client = gspread.authorize(creds)
    SHEET = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/17fNArRGZNbmRhTq_jPR7zab6O6-Edr5_IYzT5l1tZUE/edit#gid=0"
    ).sheet1
except Exception as e:
    st.error(f"❌ Could not connect to Google Sheets.\n\nError: {e}")
    st.stop()

# ---- LOAD DATA ----
@st.cache_data(ttl=60)
def load_data():
    records = SHEET.get_all_records()
    return pd.DataFrame(records)

try:
    df = load_data()
except Exception as e:
    st.error(f"⚠️ Could not load sheet data.\n\nError: {e}")
    st.stop()

# ---- DASHBOARD DISPLAY ----
st.title("📊 Quantanalyser – Macro & Instrument Dashboard")

if df.empty:
    st.warning("No data found in the Google Sheet yet.")
else:
    instruments = df["Instrument"].unique().tolist()
    selection = st.sidebar.selectbox("Select Instrument", instruments)
    st.subheader(f"Instrument: {selection}")

    selected = df[df["Instrument"] == selection]

    st.markdown("### 🧭 Macro Summary")
    st.write(selected["Macro_Outlook"].iloc[-1] if "Macro_Outlook" in selected else "No summary available.")

    st.markdown("### 💡 Institutional Commentary")
    st.write(selected["Institutional_Commentary"].iloc[-1] if "Institutional_Commentary" in selected else "No commentary yet.")

    st.markdown("### 🧩 Technical Outlook")
    st.write(selected["Technical_Outlook"].iloc[-1] if "Technical_Outlook" in selected else "No technical outlook yet.")

st.sidebar.markdown("---")
st.sidebar.info("✅ Connected to Google Sheets successfully. Data auto-refreshes every 60 seconds.")

