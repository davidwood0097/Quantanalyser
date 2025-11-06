# ==============================================================
# Axcendia Quant Macro Dashboard
# ==============================================================

import os
import glob
import json
import streamlit as st
from datetime import datetime
from typing import Any, Dict, List

# ==============================================================
# 1️⃣ Verify folder structure and JSON integrity
# ==============================================================

def verify_json_structure():
    base_path = "data"
    required_paths = [
        "schema/axcendia_macro_schema.json",
        "templates/axcendia_dashboard_template.json",
        "daily",
        "changes",
    ]

    st.sidebar.markdown("### 🔍 Folder Verification")
    for p in required_paths:
        full_path = os.path.join(base_path, p)
        if os.path.exists(full_path):
            st.sidebar.success(f"Found: {full_path}")
        else:
            st.sidebar.error(f"Missing: {full_path}")

    try:
        with open("data/schema/axcendia_macro_schema.json", "r") as f:
            schema = json.load(f)
        with open("data/templates/axcendia_dashboard_template.json", "r") as f:
            template = json.load(f)
        st.sidebar.success(f"✅ JSON loaded ({len(template)} modules). First entity: {template[0]['entity']}")
    except Exception as e:
        st.sidebar.error(f"❌ JSON load error: {e}")


# ==============================================================
# 2️⃣ Loader Functions
# ==============================================================

@st.cache_data
def load_template(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_latest_json(folder: str):
    files = sorted(glob.glob(os.path.join(folder, "*.json")))
    if not files:
        return None
    with open(files[-1], "r", encoding="utf-8") as f:
        return json.load(f)

# ==============================================================
# 3️⃣ Renderer Functions
# ==============================================================

def _table(data: List[dict], headers: List[str]):
    if not data:
        st.info("No data available yet.")
        return
    st.dataframe([{h: row.get(h, "") for h in headers} for row in data], use_container_width=True)

def render_module(m: Dict[str, Any]):
    s = m["sections"]
    st.header(f"{m['entity']} — {m['category']}  |  Last update: {m['last_updated']}")
    st.markdown("---")

    st.subheader("1️⃣ Monetary Policy / Policy Summary")
    st.write(s["policy_summary"] or "—")

    st.subheader("2️⃣ Inflation & Growth")
    st.write(s["inflation_growth"] or "—")

    st.subheader("3️⃣ Political & Fiscal")
    st.write(s["political_fiscal"] or "—")

    st.subheader("4️⃣ Positioning Overview")
    _table(s["positioning_overview"], headers=["instrument", "recent_level", "bias", "notes"])

    st.subheader("5️⃣ Trading Implications (Scenarios)")
    scenarios = s["trading_implications"].get("scenarios", [])
    if not scenarios:
        st.info("No scenarios yet.")
    else:
        for sc in scenarios:
            st.markdown(f"**{sc['name']}** — Prob: {int(sc['probability'] * 100)}%")
            st.write(sc["narrative"])
            _table(sc["positions"], headers=["instrument", "bias", "entry", "target", "stop"])
            st.markdown("---")

    st.subheader("6️⃣ Summary Table")
    _table(
        s["summary_table"],
        headers=["scenario", "probability", "bias", "trade_plan", "target_window", "key_drivers"],
    )

    st.subheader("7️⃣ Tactical Notes")
    notes = s.get("tactical_notes", [])
    if notes:
        for n in notes:
            st.markdown(f"- {n}")
    else:
        st.write("—")


# ==============================================================
# 4️⃣ Main App
# ==============================================================

def main():
    st.set_page_config(page_title="Axcendia Quant Macro Dashboard", layout="wide")
    st.title("📊 Axcendia Quant Macro Dashboard")

    # Run verification
    verify_json_structure()

    # Load template + optional latest update files
    template_path = "data/templates/axcendia_dashboard_template.json"
    template = load_template(template_path)

    latest_daily = load_latest_json("data/daily")
    latest_changes = load_latest_json("data/changes")

    modules = latest_daily if latest_daily else template
    entities = [m["entity"] for m in modules]

    # Sidebar selector
    st.sidebar.markdown("### Select Entity")
    entity = st.sidebar.selectbox("Choose Currency / Asset:", entities, index=entities.index("JPY") if "JPY" in entities else 0)
    module = next(m for m in modules if m["entity"] == entity)

    # Show data file status
    st.sidebar.markdown("### Data Status")
    if latest_daily:
        st.sidebar.success(f"Latest macro update loaded ✅")
    else:
        st.sidebar.warning("Using template data ⚠️")

    if latest_changes:
        st.sidebar.info("Change log detected")
    else:
        st.sidebar.warning("No change log yet")

    # Top 3 Overnight Themes
    if latest_changes and latest_changes.get("top_themes"):
        st.markdown("## 📰 Top 3 Overnight Themes")
        for t in latest_changes["top_themes"][:3]:
            st.write(f"• {t}")
        st.divider()

    # Diff summary for selected entity
    if latest_changes:
        st.markdown("## Δ Changes Since Yesterday")
        for a in latest_changes.get("assets", []):
            if a["entity"] == entity:
                for d in a.get("diffs", []):
                    st.write(f"{d['tag']} {d['field']}: {d['dir']} {d['magnitude']} — {d['comment']}")
                st.write(f"**Market Impact:** {a.get('market_impact', '—')}")
                st.write(f"**Positioning:** {a.get('positioning_implication', '—')}")
                break
        st.divider()

    # Render the module
    render_module(module)

    # Quant Desk Outlook
    if latest_changes and latest_changes.get("quant_desk_outlook"):
        st.divider()
        st.markdown("## 🎯 Quant Desk Outlook")
        st.write(latest_changes["quant_desk_outlook"])


# ==============================================================
# 5️⃣ Run app
# ==============================================================

if __name__ == "__main__":
    main()


