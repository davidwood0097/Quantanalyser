import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Axcendia Quant Analyser", layout="wide")

st.title("📊 Axcendia Quant Analyser Dashboard")
st.write("Connecting to Google Sheets...")

# Define the scopes for Google API access
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Attempt connection using service account info from Streamlit secrets
try:
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    SHEET = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/17fNArRGZNbmRhTq_jPR7zab6O6-Edr5_IYzT5l1tZUE/edit?gid=0#gid=0"
    ).sheet1

    # Pull all data from the first sheet
    records = SHEET.get_all_records()
    df = pd.DataFrame(records)

    st.success("✅ Connected to Google Sheets successfully!")

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("⚠️ Connected successfully, but the sheet is empty.")

except Exception as e:
    st.error(f"❌ Could not connect to Google Sheets.\n\nError: {e}")
    st.stop()

st.markdown("---")
st.caption("© 2025 Axcendia Quantitative Research")


