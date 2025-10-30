import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ─────────────────────────────────────────────
#  PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(page_title="Axcendia FX Macro Dashboard", layout="wide")
st.title("💹 Axcendia FX Macro Dashboard")

# ─────────────────────────────────────────────
#  GOOGLE SHEETS CONNECTION (using Streamlit Secrets)
# ─────────────────────────────────────────────
try:
    SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_json = st.secrets["gcp_service_account"]
    CREDS = Credentials.from_service_account_info(creds_json, scopes=SCOPE)
    CLIENT = gspread.authorize(CREDS)
    SHEET_URL = "https://docs.google.com/spreadsheets/d/17fNArRGZNbmRhTq_jPR7zab6O6-Edr5_IYzT5l1tZUE/edit"
    SHEET = CLIENT.open_by_url(SHEET_URL).sheet1
except Exception as e:
    st.error(f"❌ Could not connect to Google Sheets. Please check permissions and secrets setup.\n\nError: {e}")
    st.stop()

# ─────────────────────────────────────────────
#  LOAD AND SAVE FUNCTIONS
# ─────────────────────────────────────────────
def load_data():
    try:
        records = SHEET.get_all_records()
        return pd.DataFrame(records) if records else pd.DataFrame(
            columns=[
                "Instrument", "Macro Outlook", "Technical Summary",
                "Supply Zone", "Demand Zone", "CVD Delta",
                "Bias", "Confidence", "Notes"
            ]
        )
    except Exception as e:
        st.error(f"⚠️ Unable to load data from Google Sheets: {e}")
        st.stop()

def save_data(df):
    try:
        SHEET.clear()
        SHEET.update([df.columns.values.tolist()] + df.values.tolist())
    except Exception as e:
        st.error(f"⚠️ Unable to save data to Google Sheets: {e}")
        st.stop()

# Load the current data
df = load_data()

# ─────────────────────────────────────────────
#  SIDEBAR ENTRY PANEL
# ─────────────────────────────────────────────
st.sidebar.header("📥 Add / Update Instrument Data")

instrument = st.sidebar.selectbox(
    "Select instrument",
    ["GBPAUD", "AUDCAD", "EURUSD", "DXY", "GOLD", "BTCUSD", "US500"]
)
macro = st.sidebar.text_area("Macro Outlook")
technical = st.sidebar.text_area("Technical Summary")
supply = st.sidebar.text_input("Key Supply Zone")
demand = st.sidebar.text_input("Key Demand Zone")
cvd = st.sidebar.text_input("CVD Delta Trend")
bias = st.sidebar.slider("Bias (-10 = bearish, +10 = bullish)", -10, 10, 0)
confidence = st.sidebar.slider("Confidence (%)", 0, 100, 50)
notes = st.sidebar.text_area("Desk Notes / Trade Plan")

if st.sidebar.button("💾 Save / Update"):
    new_entry = pd.DataFrame([{
        "Instrument": instrument,
        "Macro Outlook": macro,
        "Technical Summary": technical,
        "Supply Zone": supply,
        "Demand Zone": demand,
        "CVD Delta": cvd,
        "Bias": bias,
        "Confidence": confidence,
        "Notes": notes
    }])

    df = pd.concat([df, new_entry], ignore_index=True)
    save_data(df)
    st.sidebar.success(f"{instrument} entry saved to Google Sheets ✅")

st.sidebar.download_button(
    "⬇️ Export all data as CSV",
    df.to_csv(index=False).encode(),
    "axcendia_dashboard.csv",
    "text/csv"
)

# ─────────────────────────────────────────────
#  MAIN DASHBOARD DISPLAY
# ─────────────────────────────────────────────
st.subheader("📊 Current Instrument Data")
if df.empty:
    st.info("No data found yet. Add your first instrument from the sidebar.")
else:
    st.dataframe(df, use_container_width=True)

    # Summary metrics
    avg_bias = df["Bias"].mean()
    avg_conf = df["Confidence"].mean()
    st.metric("Average Bias", round(avg_bias, 2))
    st.metric("Average Confidence", f"{round(avg_conf, 1)}%")

st.caption("🔄 Synced live with Google Sheets — updates appear instantly.")

