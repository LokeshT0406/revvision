from __future__ import annotations

import pandas as pd


def build_migration_test_plan(df: pd.DataFrame) -> str:
    total = len(df)
    qcp = int(df["qcp"].sum()) if not df.empty else 0
    high = len(df[df["risk"].isin(["HIGH", "CRITICAL"])]) if not df.empty else 0
    weeks = float(df["est_weeks"].sum()) if not df.empty else 0.0

    lines = [
        "# CPQ to Revenue Cloud Advanced Migration Test Plan",
        "",
        "## Scope Summary",
        f"- Artifacts analyzed: {total}",
        f"- QCP-dependent artifacts: {qcp}",
        f"- High/Critical risk artifacts: {high}",
        f"- Estimated effort window: {weeks:.1f} weeks",
        "",
        "## Test Streams",
        "- Unit tests: parsing, scoring, and blueprint generation.",
        "- Integration tests: metadata upload to scoring to report export flow.",
        "- Pricing parity tests: CPQ output vs RCA output for golden scenarios.",
        "- End-to-end business tests: Quote, Amend, Renew, Order.",
        "",
        "## Mandatory Pricing Parity Scenarios",
        "- Net-new quote with bundle, volume discount, and manual override.",
        "- Amendment quote with existing subscription and proration.",
        "- Renewal quote with uplift and contracted pricing.",
        "- Approval-required quote above discount threshold.",
        "- Multi-currency quote with region-specific rules.",
        "",
        "## Exit Criteria",
        "- 100% pass rate on critical pricing parity scenarios.",
        "- No blocking defects in quote calculation, amendments, renewals.",
        "- Signed-off rollback and cutover runbook.",
    ]
    return "\n".join(lines)
