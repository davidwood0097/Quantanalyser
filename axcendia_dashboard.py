import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ==============================
# PAGE CONFIG & HEADER
# ==============================
st.set_page_config(page_title="Axcendia Quant Analyser", layout="wide")
st.title("📊 Axcendia Quant Analyser Dashboard")
st.write("Connecting to Google Sheets...")

# ==============================
# GOOGLE SHEETS CONNECTION
# ==============================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

try:
    # Use service account from Streamlit Secrets (for Cloud deployment)
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    client = gspread.authorize(creds)

    # Connect to your specific sheet
    SHEET = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/17fNArRGZNbmRhTq_jPR7zab6O6-Edr5_IYzT5l1tZUE/edit?gid=0#gid=0"
    ).sheet1

    # Load data
    records = SHEET.get_all_records()
    df = pd.DataFrame(records)

    st.success("✅ Connected to Google Sheets successfully!")

    # Show live dashboard data
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("⚠️ Connected successfully, but the sheet is empty.")

except Exception as e:
    st.error(f"❌ Could not connect to Google Sheets.\n\nError: {e}")
    st.stop()

# ==============================
# ADMIN UPLOADER MODULE
# ==============================
st.markdown("---")
st.subheader("📂 Admin Uploader — Bulk Import Economic Data")

uploaded_file = st.file_uploader("Upload your Excel file (all currencies)", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Read uploaded Excel
        df_upload = pd.read_excel(uploaded_file)
        st.write("### Preview of Uploaded Data")
        st.dataframe(df_upload.head(), use_container_width=True)

        # Optional column mapping (lets you rename columns before upload)
        st.write("### Column Mapping")
        col_mapping = {}
        for col in df_upload.columns:
            new_col = st.text_input(f"Map '{col}' →", col)
            col_mapping[col] = new_col
        df_upload.rename(columns=col_mapping, inplace=True)

        # Append or replace mode
        mode = st.radio("Choose upload mode:", ["Append to existing data", "Replace existing data"])

        if st.button("🚀 Push to Google Sheet"):
            sheet = client.open_by_url(
                "https://docs.google.com/spreadsheets/d/17fNArRGZNbmRhTq_jPR7zab6O6-Edr5_IYzT5l1tZUE/edit?gid=0#gid=0"
            ).sheet1

            # Pull existing data
            existing_records = sheet.get_all_records()
            existing_df = pd.DataFrame(existing_records)

            # Combine or replace
            if mode == "Append to existing data" and not existing_df.empty:
                final_df = pd.concat([existing_df, df_upload], ignore_index=True)
            else:
                final_df = df_upload

            # Write back to Google Sheets
            sheet.update([final_df.columns.values.tolist()] + final_df.values.tolist())
            st.success("✅ Data successfully pushed to Google Sheet!")

    except Exception as e:
        st.error(f"❌ Upload failed. Error: {e}")

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.caption("© 2025 Axcendia Quantitative Research")
