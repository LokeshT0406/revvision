from __future__ import annotations

import pandas as pd
import streamlit as st

from revvision.services.analyzer import (
    RISK_PRESETS,
    analyze_uploaded_files,
    compute_roi,
    coverage_table,
    org_risk,
    pricing_signal_summary,
    readiness_context,
    upload_requirements_report,
)
from revvision.ui.render import (
    render_blueprint_studio,
    render_dashboard,
    render_file_analysis,
    render_readiness,
    render_remediation,
    render_roadmap,
    render_test_lab,
)
from revvision.ui.styles import CSS

st.set_page_config(
    page_title="RevVision Pro | CPQ to RCA Readiness",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.markdown(
        """
        <div style='padding:8px 0 18px 0;'>
          <div style='font-size:1.4rem;font-weight:800;letter-spacing:-0.5px;'>⚡ RevVision Pro</div>
          <div style='font-size:0.78rem;opacity:0.55;margin-top:2px;'>CPQ → Revenue Cloud Advanced</div>
        </div>
        <hr style='margin-bottom:16px;'/>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("**⚙️ Analysis Settings**")
    st.selectbox("OpenAI Model", ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1"], index=0)
    threshold_mode = st.selectbox("Risk Threshold Profile", ["Balanced", "Strict", "Custom"], index=0)
    thresholds_valid = True

    if threshold_mode == "Custom":
        low_threshold = int(st.number_input("Low → Moderate max", min_value=1, value=250, step=1))
        moderate_threshold = int(st.number_input("Moderate → High max", min_value=1, value=500, step=1))
        high_threshold = int(st.number_input("High → Critical max", min_value=1, value=750, step=1))
        if not (low_threshold < moderate_threshold < high_threshold):
            thresholds_valid = False
            st.error("Thresholds must follow: Low < Moderate < High.")
    else:
        low_threshold, moderate_threshold, high_threshold = RISK_PRESETS[threshold_mode]

    st.caption(
        f"🟢 LOW <{low_threshold}  🟡 MOD <{moderate_threshold}  🟠 HIGH <{high_threshold}  🔴 CRIT ≥{high_threshold}"
    )
    st.markdown("<hr/>", unsafe_allow_html=True)

    with st.expander("📋 Upload Guide", expanded=False):
        st.markdown(
            """
**Minimum:** 1 artifact to start · **Recommended:** 10+

**Supported types:**
- `*.cls` / `*.apex` — Apex Classes
- `*.trigger` — Apex Triggers
- `*.flow` / `*.flow-meta.xml` — Flows
- `*.js` / `*.resource` — QCP Scripts
- `*PriceRule*.xml` — Price Rules
- `*ProductRule*.xml` — Product Rules
- `*LookupTable*.xml` — Lookup Tables
- `*SummaryVariable*.xml` — Summary Variables
- `*.object-meta.xml` — Object Metadata

*Duplicates are automatically excluded from scoring.*
        """
        )

    st.markdown("<br/>", unsafe_allow_html=True)
    st.caption("RevVision Pro v2.0 · Hackathon 2025")

st.markdown(CSS, unsafe_allow_html=True)

st.markdown(
    """
<div style='margin-bottom:8px;display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;'>
  <span style='font-size:1.9rem;font-weight:800;letter-spacing:-1px;'>RevVision Pro</span>
  <span style='font-size:0.88rem;opacity:0.45;'>CPQ → Revenue Cloud Advanced Readiness Assessment</span>
</div>""",
    unsafe_allow_html=True,
)

uploaded_files = st.file_uploader(
    "Upload CPQ Artifacts",
    type=["xml", "resource", "cls", "trigger", "flow", "js", "apex"],
    accept_multiple_files=True,
    help="Upload Salesforce CPQ artifacts (Apex, Flows, Price Rules, QCP scripts, metadata) to begin assessment.",
)

df = (
    analyze_uploaded_files(uploaded_files, low_threshold, moderate_threshold, high_threshold)
    if uploaded_files and thresholds_valid
    else pd.DataFrame()
)
risk = org_risk(df, low_threshold, moderate_threshold, high_threshold)
readiness = readiness_context(df)
coverage = coverage_table(df)
pricing_signals = pricing_signal_summary(df)
upload_report = upload_requirements_report(df)
roi = compute_roi(df)

if uploaded_files and thresholds_valid:
    st.success(f"✅ {len(uploaded_files)} artifact(s) uploaded.")

t1, t2, t3, t4, t5, t6 = st.tabs(
    [
        "📊 Dashboard",
        "🔍 File Analysis",
        "✅ Readiness",
        "🔧 Remediation",
        "📐 Blueprint Studio",
        "🧪 Test Lab",
    ]
)

with t1:
    render_dashboard(
        df,
        risk,
        readiness,
        coverage,
        pricing_signals,
        roi,
        low_threshold,
        moderate_threshold,
        high_threshold,
    )
with t2:
    render_file_analysis(df)
with t3:
    render_readiness(df, readiness, coverage, pricing_signals, upload_report, roi)
    render_roadmap(df)
with t4:
    render_remediation(df, readiness)
with t5:
    render_blueprint_studio(df)
with t6:
    render_test_lab(df)
