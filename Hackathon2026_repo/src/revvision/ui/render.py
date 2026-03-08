from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from revvision.constants import SBQQ_TO_RCA_OBJECT_MAP
from revvision.services.blueprints import build_blueprint, build_portfolio_blueprint
from revvision.services.testing import build_migration_test_plan


def _risk_hex(risk: str) -> str:
    return {
        "LOW": "#3fb950",
        "MODERATE": "#d29922",
        "HIGH": "#f0883e",
        "CRITICAL": "#f85149",
        "STABLE": "#3fb950",
    }.get(str(risk).upper(), "#8b949e")


def _risk_icon(risk: str) -> str:
    return {
        "LOW": "🟢",
        "MODERATE": "🟡",
        "HIGH": "🟠",
        "CRITICAL": "🔴",
    }.get(str(risk).upper(), "⚪")


def _card(label: str, value: str, sub: str = "", color: str = "#58a6ff") -> str:
    return f"""
    <div style='background:linear-gradient(135deg,#161b22,#1c2128);border:1px solid #30363d;
         border-radius:12px;padding:18px 20px;margin-bottom:4px;'>
      <div style='font-size:0.72rem;color:#8b949e;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px;'>{label}</div>
      <div style='font-size:1.7rem;font-weight:700;color:{color};font-family:"JetBrains Mono",monospace;line-height:1;'>{value}</div>
      {f'<div style="font-size:0.78rem;color:#8b949e;margin-top:4px;">{sub}</div>' if sub else ''}
    </div>"""


def _section(title: str, icon: str = "") -> None:
    st.markdown(
        f"""
    <div style='display:flex;align-items:center;gap:8px;margin:24px 0 12px 0;border-bottom:1px solid #21262d;padding-bottom:8px;'>
      <span style='font-size:1.1rem;'>{icon}</span>
      <span style='font-size:1.1rem;font-weight:700;color:#e6edf3;'>{title}</span>
    </div>""",
        unsafe_allow_html=True,
    )


def _insight_card(insight: str, severity: str = "info") -> str:
    colors = {
        "error": ("#f85149", "#2d0f0f", "#da3633"),
        "warning": ("#d29922", "#2a1f00", "#9e6a03"),
        "success": ("#3fb950", "#0d2818", "#238636"),
        "info": ("#58a6ff", "#0d1f33", "#1f6feb"),
    }
    text_c, bg_c, border_c = colors.get(severity, colors["info"])
    icon = {"error": "❌", "warning": "⚠️", "success": "✅", "info": "ℹ️"}.get(severity, "ℹ️")
    return (
        f"<div style='background:{bg_c};border:1px solid {border_c};border-radius:8px;"
        f"padding:10px 14px;margin-bottom:8px;display:flex;gap:10px;align-items:flex-start;'>"
        f"<span style='font-size:0.9rem;margin-top:1px;'>{icon}</span>"
        f"<span style='font-size:0.88rem;color:{text_c};line-height:1.5;'>{insight}</span></div>"
    )


def _phase_card(phase_num: int, title: str, files_df: pd.DataFrame, description: str, color: str) -> None:
    count = len(files_df)
    weeks = float(files_df["est_weeks"].sum()) if not files_df.empty else 0.0
    st.markdown(
        f"""
    <div style='background:linear-gradient(135deg,#161b22,#1c2128);border:1px solid #30363d;
         border-left:4px solid {color};border-radius:10px;padding:16px 20px;margin-bottom:12px;'>
      <div style='display:flex;justify-content:space-between;align-items:center;'>
        <div>
          <div style='font-size:0.72rem;color:#8b949e;text-transform:uppercase;letter-spacing:.1em;'>Phase {phase_num}</div>
          <div style='font-size:1.05rem;font-weight:700;color:#e6edf3;margin-top:2px;'>{title}</div>
          <div style='font-size:0.82rem;color:#8b949e;margin-top:4px;'>{description}</div>
        </div>
        <div style='text-align:right;'>
          <div style='font-size:1.6rem;font-weight:700;color:{color};font-family:"JetBrains Mono",monospace;'>{count}</div>
          <div style='font-size:0.75rem;color:#8b949e;'>files</div>
          <div style='font-size:0.88rem;color:#c9d1d9;margin-top:2px;'>{weeks:.1f}w</div>
        </div>
      </div>
    </div>""",
        unsafe_allow_html=True,
    )


def render_dashboard(
    df: pd.DataFrame,
    org_risk: str,
    readiness: dict[str, object],
    coverage: pd.DataFrame,
    pricing_signals: dict[str, int],
    roi: dict[str, object],
    low_threshold: int,
    moderate_threshold: int,
    high_threshold: int,
) -> None:
    if df.empty:
        st.info("Upload artifacts to view the dashboard.")
        return

    assessed = df[~df["excluded_from_assessment"]] if "excluded_from_assessment" in df.columns else df
    high_crit = len(assessed[assessed["risk"].isin(["HIGH", "CRITICAL"])])
    risk_color = _risk_hex(org_risk)
    total_score = int(assessed["score"].sum()) if not assessed.empty else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(_card("Files Uploaded", str(len(df)), f"{len(assessed)} assessed"), unsafe_allow_html=True)
    with c2:
        st.markdown(_card("Total Risk Score", str(total_score), "portfolio sum"), unsafe_allow_html=True)
    with c3:
        st.markdown(_card("Org Risk", org_risk, f"{high_crit} high/critical files", risk_color), unsafe_allow_html=True)
    with c4:
        st.markdown(_card("QCP Files", str(int(assessed["qcp"].sum())), "require rebuild"), unsafe_allow_html=True)
    with c5:
        st.markdown(_card("Est. Effort", f"{assessed['est_weeks'].sum():.1f}w", "total migration weeks"), unsafe_allow_html=True)
    with c6:
        st.markdown(_card("ROI", f"${roi['cost_saved']}", f"{roi['efficiency_gain_pct']}% efficiency"), unsafe_allow_html=True)

    _section("Risk Score Ranges (Per File: 0-1000)", "📏")
    st.table(
        pd.DataFrame(
            [
                {"Risk": "LOW", "Per-file score range": f"0 to {low_threshold - 1}"},
                {"Risk": "MODERATE", "Per-file score range": f"{low_threshold} to {moderate_threshold - 1}"},
                {"Risk": "HIGH", "Per-file score range": f"{moderate_threshold} to {high_threshold - 1}"},
                {"Risk": "CRITICAL", "Per-file score range": f"{high_threshold} to 1000"},
            ]
        )
    )

    left, right = st.columns(2)
    with left:
        _section("Risk Distribution", "📊")
        risk_counts = assessed["risk"].value_counts().reindex(["CRITICAL", "HIGH", "MODERATE", "LOW"], fill_value=0)
        fig = go.Figure(
            go.Bar(
                x=risk_counts.index.tolist(),
                y=risk_counts.values.tolist(),
                marker_color=[_risk_hex(x) for x in risk_counts.index],
                text=risk_counts.values.tolist(),
                textposition="outside",
            )
        )
        fig.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        _section("Artifact Type Breakdown", "🗂️")
        type_counts = assessed["type_label"].value_counts()
        pie = go.Figure(go.Pie(labels=type_counts.index.tolist(), values=type_counts.values.tolist(), hole=0.5))
        pie.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(pie, use_container_width=True)

    _section("Artifact Summary", "📋")
    display_cols = ["file_name", "type_label", "risk", "score", "est_weeks", "hardcoded_ids", "soql_hits"]
    if "duplicate_reason" in df.columns:
        display_cols.append("duplicate_reason")
    display = df[[c for c in display_cols if c in df.columns]].sort_values("score", ascending=False)
    display.columns = [c.replace("_", " ").title() for c in display.columns]
    st.dataframe(display, use_container_width=True, hide_index=True)


def render_file_analysis(df: pd.DataFrame) -> None:
    _section("Per-File Analysis", "🔍")
    if df.empty:
        st.info("Upload artifacts to analyse individual files.")
        return

    selected = st.selectbox("Select artifact to inspect", df["file_name"].tolist(), label_visibility="collapsed")
    row = df[df["file_name"] == selected].iloc[0]
    risk = str(row.get("risk", "LOW"))
    risk_color = _risk_hex(risk)

    st.markdown(
        f"""
    <div style='background:linear-gradient(135deg,#161b22,#1c2128);border:1px solid #30363d;
         border-left:4px solid {risk_color};border-radius:10px;padding:16px 20px;margin-bottom:16px;'>
      <div style='font-size:1rem;font-weight:700;color:#e6edf3;margin-bottom:10px;'>📄 {row['file_name']}</div>
      <div style='display:flex;gap:20px;flex-wrap:wrap;'>
        <div><span style='color:#8b949e;font-size:0.75rem;'>TYPE</span><br/><span style='color:#c9d1d9;font-weight:600;'>{row.get('type_label','—')}</span></div>
        <div><span style='color:#8b949e;font-size:0.75rem;'>RISK</span><br/><span style='color:{risk_color};font-weight:700;'>{_risk_icon(risk)} {risk}</span></div>
        <div><span style='color:#8b949e;font-size:0.75rem;'>SCORE</span><br/><span style='color:#58a6ff;font-weight:700;font-family:"JetBrains Mono",monospace;'>{row.get('score',0)}</span></div>
        <div><span style='color:#8b949e;font-size:0.75rem;'>EFFORT</span><br/><span style='color:#d2a8ff;font-weight:600;'>{row.get('est_weeks',0):.1f} weeks</span></div>
        <div><span style='color:#8b949e;font-size:0.75rem;'>HARDCODED IDs</span><br/><span style='color:#ffa657;font-weight:600;'>{row.get('hardcoded_ids',0)}</span></div>
        <div><span style='color:#8b949e;font-size:0.75rem;'>SOQL HITS</span><br/><span style='color:#39c5cf;font-weight:600;'>{row.get('soql_hits',0)}</span></div>
      </div>
    </div>""",
        unsafe_allow_html=True,
    )

    insights = row.get("insights", [])
    _section("Issues & Recommendations", "⚠️")
    if insights:
        for insight in insights:
            st.markdown(_insight_card(str(insight), "info"), unsafe_allow_html=True)
    else:
        st.markdown(_insight_card("No specific issues detected.", "success"), unsafe_allow_html=True)

    _section("Migration Action Items", "🎯")
    actions: list[tuple[str, str]] = []
    if int(row.get("hardcoded_ids", 0)) > 0:
        actions.append(("error", "Replace hardcoded Salesforce IDs with metadata/config references."))
    if int(row.get("soql_hits", 0)) > 0:
        actions.append(("warning", "Refactor SOQL-heavy logic into service classes."))
    if int(row.get("qcp", 0)) > 0:
        actions.append(("warning", "Rebuild QCP logic as RCA pricing procedure + Apex actions."))
    if not actions:
        actions.append(("success", "No critical action items detected."))
    for sev, msg in actions:
        st.markdown(_insight_card(msg, sev), unsafe_allow_html=True)


def render_readiness(
    df: pd.DataFrame,
    readiness: dict[str, object],
    coverage: pd.DataFrame,
    pricing_signals: dict[str, int],
    upload_report: dict[str, object],
    roi: dict[str, object],
) -> None:
    _section("Migration Readiness", "✅")
    if df.empty:
        st.info("Upload artifacts to view readiness assessment.")
        return

    assessed = df[~df["excluded_from_assessment"]] if "excluded_from_assessment" in df.columns else df
    total = max(1, len(assessed))
    high_crit = int(assessed["risk"].isin(["HIGH", "CRITICAL"]).sum())
    status_raw = str(readiness.get("status", "INCOMPLETE")).upper()
    status_text = {
        "READY": "Ready to Start",
        "PARTIAL": "Partially Ready",
        "INCOMPLETE": "Needs More Input",
    }.get(status_raw, status_raw.title())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_card("Assessment Status", status_text, status_raw), unsafe_allow_html=True)
    with c2:
        st.markdown(_card("Confidence", f"{readiness.get('confidence_score', 0)}%", str(readiness.get("confidence", "LOW"))), unsafe_allow_html=True)
    with c3:
        st.markdown(
            _card(
                "Required Areas Covered",
                f"{readiness.get('mandatory_met', 0)}/{readiness.get('mandatory_total', 0)}",
                "pricing, automation, pricing data, customization",
            ),
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(_card("High/Critical", str(high_crit), f"{high_crit}/{total} files"), unsafe_allow_html=True)

    if not coverage.empty:
        _section("Coverage", "📋")
        st.dataframe(coverage, use_container_width=True, hide_index=True)

    _section("Pricing Signals", "💹")
    st.markdown(
        _insight_card(
            f"Conditions: {pricing_signals['conditions']} | Actions: {pricing_signals['actions']} | "
            f"Lookups: {pricing_signals['lookups']} | QCP files: {pricing_signals['qcp_files']}",
            "info",
        ),
        unsafe_allow_html=True,
    )


def render_roadmap(df: pd.DataFrame) -> None:
    _section("Phased Roadmap", "🗺️")
    if df.empty:
        st.info("Upload artifacts to generate a roadmap.")
        return

    assessed = df[~df["excluded_from_assessment"]] if "excluded_from_assessment" in df.columns else df
    phase1 = assessed[assessed["risk"].isin(["LOW", "MODERATE"])]
    phase2 = assessed[assessed["risk"] == "HIGH"]
    phase3 = assessed[assessed["risk"] == "CRITICAL"]

    if len(phase1):
        _phase_card(1, "Quick Wins", phase1, "Start with low/moderate complexity artifacts.", "#3fb950")
    if len(phase2):
        _phase_card(2, "Core Migration", phase2, "Migrate high-risk core business logic.", "#d29922")
    if len(phase3):
        _phase_card(3, "Complex Assets", phase3, "Architect-led execution for critical customizations.", "#f85149")


def render_remediation(df: pd.DataFrame, readiness: dict[str, object]) -> None:
    _section("Remediation", "🔧")
    if df.empty:
        st.info("Upload artifacts to view remediation guidance.")
        return

    assessed = df[~df["excluded_from_assessment"]] if "excluded_from_assessment" in df.columns else df
    total_hardcoded = int(assessed["hardcoded_ids"].sum()) if not assessed.empty else 0
    total_soql = int(assessed["soql_hits"].sum()) if not assessed.empty else 0
    total_qcp = int(assessed["qcp"].sum()) if not assessed.empty else 0

    st.markdown(_insight_card(f"Hardcoded IDs detected: {total_hardcoded}", "warning" if total_hardcoded else "success"), unsafe_allow_html=True)
    st.markdown(_insight_card(f"SOQL-heavy spots detected: {total_soql}", "warning" if total_soql else "success"), unsafe_allow_html=True)
    st.markdown(_insight_card(f"QCP files requiring rebuild: {total_qcp}", "warning" if total_qcp else "success"), unsafe_allow_html=True)

    missing = readiness.get("missing_mandatory", [])
    if missing:
        for m in missing:
            st.markdown(_insight_card(f"Missing mandatory component: {m}", "error"), unsafe_allow_html=True)


def render_blueprint_studio(df: pd.DataFrame) -> None:
    _section("Blueprint Studio", "📐")
    if df.empty:
        st.info("Upload files first to generate migration blueprints.")
        return

    mode = st.radio("Blueprint mode", ["Single artifact", "Portfolio (all artifacts)"], horizontal=True)

    _section("SBQQ → RCA Object Mapping", "🔗")
    type_keys_present = set(df["type_key"].tolist())
    relevant_objects = {
        "qcp": {"SBQQ__Quote__c", "SBQQ__QuoteLine__c", "SBQQ__Subscription__c"},
        "price_rule": {"SBQQ__PriceRule__c", "SBQQ__QuoteLine__c"},
        "product_rule": {"SBQQ__ProductOption__c", "SBQQ__QuoteLine__c"},
        "apex_class": {"SBQQ__Quote__c", "SBQQ__QuoteLine__c", "SBQQ__Subscription__c", "SBQQ__ProductOption__c", "SBQQ__PriceRule__c"},
        "apex_trigger": {"SBQQ__Quote__c", "SBQQ__QuoteLine__c"},
        "flow": {"SBQQ__Quote__c", "SBQQ__QuoteLine__c"},
    }
    shown_objects: set[str] = set()
    for type_key in type_keys_present:
        shown_objects.update(relevant_objects.get(type_key, set()))
    filtered_map = {k: v for k, v in SBQQ_TO_RCA_OBJECT_MAP.items() if k in shown_objects}

    if filtered_map:
        mapping_lines = [f"- `{cpq}` -> `{rca}`" for cpq, rca in filtered_map.items()]
        st.markdown("\n".join(mapping_lines))
    else:
        st.caption("No direct SBQQ → RCA mappings detected for current uploaded migration scope.")

    st.markdown("<br/>", unsafe_allow_html=True)

    if mode == "Single artifact":
        selected = st.selectbox("Select artifact", df["file_name"].tolist(), key="bp_select")
        row = df[df["file_name"] == selected].iloc[0].to_dict()
        blueprint = build_blueprint(row)

        risk_color = _risk_hex(str(row.get("risk", "")))
        st.markdown(
            f"""
        <div style='background:linear-gradient(135deg,#161b22,#1c2128);border:1px solid #30363d;
             border-left:4px solid #58a6ff;border-radius:10px;padding:14px 18px;margin-bottom:12px;'>
          <div style='font-size:0.95rem;font-weight:700;color:#e6edf3;margin-bottom:6px;'>📄 {selected}</div>
          <div style='display:flex;gap:16px;flex-wrap:wrap;'>
            <span style='font-size:0.78rem;'><span style='color:#8b949e;'>Type:</span> <span style='color:#79c0ff;'>{row.get('type_label','—')}</span></span>
            <span style='font-size:0.78rem;'><span style='color:#8b949e;'>Risk:</span> <span style='color:{risk_color};font-weight:600;'>{row.get('risk','—')}</span></span>
            <span style='font-size:0.78rem;'><span style='color:#8b949e;'>Score:</span> <span style='color:#58a6ff;'>{row.get('score',0)}</span></span>
            <span style='font-size:0.78rem;'><span style='color:#8b949e;'>Effort:</span> <span style='color:#d2a8ff;'>{row.get('est_weeks',0):.1f}w</span></span>
          </div>
        </div>""",
            unsafe_allow_html=True,
        )

        st.code(blueprint, language="markdown")
        st.download_button("⬇️ Download Blueprint", data=blueprint, file_name=f"{selected}_blueprint.md", mime="text/markdown")
    else:
        rows = df.to_dict(orient="records")
        portfolio = build_portfolio_blueprint(rows)
        st.caption(f"Portfolio blueprint for {len(rows)} artifact(s)")
        st.code(portfolio, language="markdown")
        st.download_button("⬇️ Download Portfolio Blueprint", data=portfolio, file_name="cpq_to_rca_portfolio_blueprint.md", mime="text/markdown")


def render_test_lab(df: pd.DataFrame) -> None:
    _section("Migration Test Lab", "🧪")
    if df.empty:
        st.info("Upload artifacts to generate a test plan tailored to your migration scope.")
        return

    assessed = df[~df["excluded_from_assessment"]] if "excluded_from_assessment" in df.columns else df
    total = len(assessed)
    qcp = int(assessed["qcp"].sum()) if "qcp" in assessed.columns and not assessed.empty else 0
    high = int(assessed["risk"].isin(["HIGH", "CRITICAL"]).sum()) if "risk" in assessed.columns and not assessed.empty else 0
    weeks = float(assessed["est_weeks"].sum()) if "est_weeks" in assessed.columns and not assessed.empty else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_card("Artifacts In Scope", str(total), "unique assessed files"), unsafe_allow_html=True)
    with c2:
        st.markdown(_card("QCP-Dependent", str(qcp), "requires pricing rebuild", "#d2a8ff" if qcp else "#3fb950"), unsafe_allow_html=True)
    with c3:
        st.markdown(_card("High/Critical", str(high), "needs parity focus", "#f85149" if high else "#3fb950"), unsafe_allow_html=True)
    with c4:
        st.markdown(_card("Effort Window", f"{weeks:.1f}w", "estimated migration effort"), unsafe_allow_html=True)

    _section("Downloadable Migration Test Plan", "📄")
    plan = build_migration_test_plan(assessed)
    st.code(plan, language="markdown")
    st.download_button(
        "⬇️ Download Test Plan",
        data=plan,
        file_name="cpq_to_rca_migration_test_plan.md",
        mime="text/markdown",
    )


def render_ai_chat(df: pd.DataFrame, model_choice: str) -> None:
    _section("AI Migration Architect", "🤖")
    st.caption("Powered by local Ollama — ask anything about your CPQ → RCA migration.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        role = msg.get("role", "assistant")
        label = "You" if role == "user" else "Architect AI"
        st.markdown(f"**{label}:** {msg.get('content','')}")

    question = st.text_input("Ask about migration strategy, blockers, or RCA refactoring", key="chat_input")
    if st.button("Send →", key="chat_send") and question and question.strip():
        st.session_state.chat_history.append({"role": "user", "content": question})
        context = "No files uploaded." if df.empty else df[["file_name", "type_label", "risk", "score", "qcp"]].to_string(index=False)
        prompt = f"Context:\n{context}\n\nQuestion:\n{question}"
        try:
            response = run_chat(
                model_choice,
                "You are a Salesforce CPQ to Revenue Cloud Advanced migration architect. Be concrete and actionable.",
                prompt,
            )
        except Exception:
            # Graceful local fallback when Ollama is unavailable.
            if df.empty:
                response = (
                    "Local assistant fallback: upload artifacts to get tailored guidance. "
                    "Then ask for top risks, migration order, or QCP rebuild steps."
                )
            else:
                assessed = df[~df["excluded_from_assessment"]] if "excluded_from_assessment" in df.columns else df
                total = len(assessed)
                high_crit = int(assessed["risk"].isin(["HIGH", "CRITICAL"]).sum()) if "risk" in assessed.columns else 0
                qcp_files = int(assessed["qcp"].sum()) if "qcp" in assessed.columns else 0
                top = assessed.sort_values("score", ascending=False).head(3)[["file_name", "risk", "score"]]
                top_items = "; ".join([f"{r.file_name} ({r.risk}, score {int(r.score)})" for r in top.itertuples(index=False)])
                response = (
                    "Local assistant fallback (Ollama not connected).\n"
                    f"- Artifacts assessed: {total}\n"
                    f"- High/Critical files: {high_crit}\n"
                    f"- QCP files: {qcp_files}\n"
                    f"- Top priority files: {top_items if top_items else 'N/A'}\n"
                    "- Recommended next steps: 1) fix high/critical files first, 2) rebuild QCP logic as pricing procedures, "
                    "3) run pricing parity scenarios before cutover."
                )
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    if st.session_state.chat_history and st.button("Clear Chat", key="chat_clear"):
        st.session_state.chat_history = []
        st.rerun()
