# axcendia_dashboard.py
import streamlit as st
import pandas as pd
import sqlite3
import datetime
import io

# ---------- Config ----------
DB_FILE = "axcendia_dash.db"
INSTRUMENTS = ["GBPAUD", "AUDCAD", "EURUSD", "DXY", "GOLD"]  # extendable

# ---------- DB helpers ----------
def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS instruments (
        id INTEGER PRIMARY KEY,
        symbol TEXT,
        last_update TEXT,
        macro_summary TEXT,
        tech_summary TEXT,
        key_supply TEXT,
        key_demand TEXT,
        cvd_delta TEXT,
        bias INTEGER,
        confidence INTEGER,
        notes TEXT
    )
    """)
    conn.commit()
    return conn

def load_all(conn):
    df = pd.read_sql_query("SELECT * FROM instruments", conn)
    return df

def load_instrument(conn, symbol):
    cur = conn.cursor()
    cur.execute("SELECT * FROM instruments WHERE symbol = ?", (symbol,))
    row = cur.fetchone()
    if row:
        return {
            "id": row[0],
            "symbol": row[1],
            "last_update": row[2],
            "macro_summary": row[3],
            "tech_summary": row[4],
            "key_supply": row[5],
            "key_demand": row[6],
            "cvd_delta": row[7],
            "bias": row[8],
            "confidence": row[9],
            "notes": row[10]
        }
    else:
        return None

def upsert_instrument(conn, payload):
    cur = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    existing = load_instrument(conn, payload["symbol"])
    if existing:
        cur.execute("""
            UPDATE instruments SET last_update=?, macro_summary=?, tech_summary=?, key_supply=?, 
                                    key_demand=?, cvd_delta=?, bias=?, confidence=?, notes=?
            WHERE symbol=?
        """, (now, payload["macro_summary"], payload["tech_summary"], payload["key_supply"],
              payload["key_demand"], payload["cvd_delta"], payload["bias"], payload["confidence"],
              payload["notes"], payload["symbol"]))
    else:
        cur.execute("""
            INSERT INTO instruments (symbol, last_update, macro_summary, tech_summary, key_supply, 
                                    key_demand, cvd_delta, bias, confidence, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (payload["symbol"], now, payload["macro_summary"], payload["tech_summary"], payload["key_supply"],
              payload["key_demand"], payload["cvd_delta"], payload["bias"], payload["confidence"],
              payload["notes"]))
    conn.commit()

# ---------- UI helpers ----------
def bias_gauge(value):
    # simple text gauge
    st.metric(label="Bias (–10 bearish → +10 bullish)", value=str(value))

def export_csv(conn):
    df = load_all(conn)
    csv = df.to_csv(index=False)
    return csv

# ---------- Main App ----------
def main():
    st.set_page_config(page_title="Axcendia FX Macro Dashboard", layout="wide", initial_sidebar_state="expanded")
    st.title("Axcendia FX Macro Dashboard — Prototype")
    conn = init_db()

    # sidebar instrument selector
    with st.sidebar:
        st.header("Instruments")
        symbol = st.selectbox("Select instrument", INSTRUMENTS)
        st.markdown("---")
        st.write("Quick actions")
        if st.button("Export all to CSV"):
            csv = export_csv(conn)
            st.download_button("Download CSV", csv, file_name="axcendia_instruments.csv", mime="text/csv")
        st.markdown("Persistence: SQLite (local). For cloud persistence integrate Google Sheets / Postgres.")

    # load instrument
    data = load_instrument(conn, symbol)
    col1, col2 = st.columns([2,1])

    with col1:
        st.subheader(f"{symbol} — Macro & Technical Summary")
        macro = st.text_area("Macro summary", value=(data["macro_summary"] if data else ""), height=150)
        tech = st.text_area("Technical summary", value=(data["tech_summary"] if data else ""), height=120)

    with col2:
        st.subheader("Quick metrics")
        key_supply = st.text_input("Key supply zone(s)", value=(data["key_supply"] if data else ""))
        key_demand = st.text_input("Key demand zone(s)", value=(data["key_demand"] if data else ""))
        cvd = st.text_input("CVD / Delta reading", value=(data["cvd_delta"] if data else ""))
        bias = st.slider("Bias (–10 to +10)", -10, 10, value=(data["bias"] if data else  -6))
        confidence = st.slider("Confidence (0–100%)", 0, 100, value=(data["confidence"] if data else 75))
        st.markdown("**Last update:**")
        st.write(data["last_update"] if data else "Not set")

    st.markdown("---")
    st.subheader("Desk Notes")
    notes = st.text_area("Notes & trade plan", value=(data["notes"] if data else ""), height=160)

    save_col1, save_col2 = st.columns([1,1])
    with save_col1:
        if st.button("Save/Update"):
            payload = {
                "symbol": symbol,
                "macro_summary": macro,
                "tech_summary": tech,
                "key_supply": key_supply,
                "key_demand": key_demand,
                "cvd_delta": cvd,
                "bias": bias,
                "confidence": confidence,
                "notes": notes
            }
            upsert_instrument(conn, payload)
            st.success("Saved ✅")

    with save_col2:
        if st.button("Download Instrument PDF (summary)"):
            # create a simple PDF export using pandas -> html or simple text
            df = pd.DataFrame([{
                "Symbol": symbol,
                "Macro": macro,
                "Tech": tech,
                "Supply": key_supply,
                "Demand": key_demand,
                "CVD": cvd,
                "Bias": bias,
                "Confidence": confidence,
                "Notes": notes,
                "Updated": datetime.datetime.utcnow().isoformat()
            }])
            csv = df.to_csv(index=False)
            st.download_button("Download CSV of this instrument", csv, file_name=f"{symbol}_summary.csv", mime="text/csv")
            st.info("PDF export (fancier styling) can be added — ask me and I’ll integrate ReportLab export.")

    st.markdown("---")
    st.subheader("Dashboard snapshot")
    all_df = load_all(conn)
    if not all_df.empty:
        st.dataframe(all_df[["symbol", "last_update", "bias", "confidence"]].sort_values("symbol").reset_index(drop=True))
    else:
        st.info("No instruments saved yet. Fill fields and press Save/Update.")

    st.markdown("----")
    st.write("Notes on persistence: this prototype uses a local SQLite DB in the app directory. For reliable long-term cloud storage, connect Google Sheets or a managed DB.")

if __name__ == "__main__":
    main()
