import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ─────────────────────────────────────────────
#  Google Sheets connection
# ─────────────────────────────────────────────
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
CLIENT = gspread.authorize(CREDS)

# Replace this with your own Google Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
SHEET = CLIENT.open_by_url(SHEET_URL).sheet1

# ─────────────────────────────────────────────
#  Streamlit page config
# ─────────────────────────────────────────────
st.set_page_config(page_title="Axcendia FX Macro Dashboard", layout="wide")
st.title("💹 Axcendia FX Macro Dashboard")

# Load data from Google Sheets
def load_data():
    records = SHEET.get_all_records()
    return pd.DataFrame(records) if records else pd.DataFrame(
        columns=["Instrument","Macro Outlook","Technical Summary",
                 "Supply Zone","Demand Zone","CVD Delta",
                 "Bias","Confidence","Notes"]
    )

# Save to Google Sheets
def save_data(df):
    SHEET.clear()
    SHEET.update([df.columns.values.tolist()] + df.values.tolist())

df = load_data()

# ─────────────────────────────────────────────
#  Sidebar controls
# ─────────────────────────────────────────────
st.sidebar.header("Instrument Entry")
instrument = st.sidebar.selectbox("Select instrument", 
    ["GBPAUD","AUDCAD","EURUSD","DXY","GOLD","BTCUSD","US500"])
macro = st.sidebar.text_area("Macro Outlook")
technical = st.sidebar.text_area("Technical Summary")
supply = st.sidebar.text_input("Key Supply Zone")
demand = st.sidebar.text_input("Key Demand Zone")
cvd = st.sidebar.text_input("CVD Delta Trend")
bias = st.sidebar.slider("Bias (-10 bearish → +10 bullish)", -10, 10, 0)
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

st.sidebar.download_button("⬇️ Export all to CSV", df.to_csv(index=False).encode(), "axcendia_dashboard.csv", "text/csv")

# ─────────────────────────────────────────────
#  Main dashboard
# ─────────────────────────────────────────────
st.subheader("📊 Current Instrument Data")
st.dataframe(df, use_container_width=True)

# Summary metrics
if not df.empty:
    avg_bias = df["Bias"].mean()
    avg_conf = df["Confidence"].mean()
    st.metric("Average Bias", round(avg_bias, 2))
    st.metric("Average Confidence", f"{round(avg_conf, 1)}%")
