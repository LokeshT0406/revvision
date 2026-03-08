from __future__ import annotations

import json
from typing import Any

from revvision.constants import SBQQ_TO_RCA_OBJECT_MAP


def _safe(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    return str(value)


def _pricing_procedure_json(file_name: str, hooks: list[str]) -> str:
    steps = []
    for idx, hook in enumerate(hooks, start=1):
        steps.append(
            {
                "sequence": idx * 10,
                "name": f"{file_name}:{hook}",
                "inputContext": "SalesTransaction, SalesTransactionItem",
                "actionType": "ApexAction",
                "className": "RcaPricingHookService",
                "methodName": hook,
            }
        )
    if not steps:
        steps.append(
            {
                "sequence": 10,
                "name": f"{file_name}:DefaultPricingStep",
                "inputContext": "SalesTransaction, SalesTransactionItem",
                "actionType": "ApexAction",
                "className": "RcaPricingHookService",
                "methodName": "execute",
            }
        )
    return json.dumps({"pricingProcedure": file_name, "steps": steps}, indent=2)


def _apex_hook_stub() -> str:
    return """public with sharing class RcaPricingHookService {
    public static void execute() {
        // Placeholder: invoke RCA pricing adjustments.
    }

    public static void onBeforeCalculate() {
        execute();
    }

    public static void onCalculate() {
        execute();
    }

    public static void onAfterCalculate() {
        execute();
    }
}"""


def _mapping_table_markdown() -> str:
    rows = ["| CPQ | RCA |", "|---|---|"]
    for cpq_obj, rca_obj in SBQQ_TO_RCA_OBJECT_MAP.items():
        rows.append(f"| {cpq_obj} | {rca_obj} |")
    return "\n".join(rows)


def build_blueprint(row: dict[str, Any]) -> str:
    file_name = _safe(row.get("file_name"), "Artifact")
    type_key = _safe(row.get("type_key"), "unknown")
    score = _safe(row.get("score"), "0")
    risk = _safe(row.get("risk"), "LOW")
    hooks = row.get("extra", {}).get("qcp_hooks", [])

    sections: list[str] = [
        f"# Migration Blueprint: {file_name}",
        f"Type: `{type_key}` | Risk: `{risk}` | Score: `{score}`",
        "",
        "## Object Mapping",
        _mapping_table_markdown(),
        "",
    ]

    if type_key == "qcp":
        sections.extend(
            [
                "## Pricing Procedure JSON",
                "```json",
                _pricing_procedure_json(file_name, hooks),
                "```",
                "",
                "## Apex Hook Stub",
                "```apex",
                _apex_hook_stub(),
                "```",
                "",
                "## Migration Notes",
                "- Replace each QCP hook with a Pricing Procedure step.",
                "- Move inline SOQL to Apex service classes with test coverage.",
                "- Externalize constants and IDs to Custom Metadata.",
            ]
        )
    elif type_key in {"apex_class", "apex_trigger"}:
        sections.extend(
            [
                "## Apex Refactor Pattern",
                "```apex",
                _apex_hook_stub(),
                "```",
                "",
                "## Migration Notes",
                "- Replace SBQQ object references with RCA objects.",
                "- Isolate pricing logic into stateless service methods.",
                "- Add unit tests for each conditional path.",
            ]
        )
    elif type_key in {"price_rule", "product_rule"}:
        sections.extend(
            [
                "## Pricing Procedure JSON",
                "```json",
                _pricing_procedure_json(file_name, []),
                "```",
                "",
                "## Migration Notes",
                "- Convert rule conditions into Decision Table rows.",
                "- Convert actions into procedure steps with clear sequence.",
                "- Validate pricing parity with golden quote scenarios.",
            ]
        )
    else:
        sections.extend(
            [
                "## Migration Notes",
                "- Review all SBQQ references and remap to RCA schema.",
                "- Standardize custom logic in Apex services and flow actions.",
                "- Include this artifact in the phased cutover checklist.",
            ]
        )

    sections.extend(
        [
            "",
            "## Test Cases",
            "- Baseline quote pricing parity against current CPQ output.",
            "- Bulk quote recalculation behavior under RCA pricing service.",
            "- Amendment and renewal pricing parity for existing subscriptions.",
        ]
    )

    return "\n".join(sections)


def build_portfolio_blueprint(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "# Migration Blueprint Portfolio\n\nNo artifacts available."

    total = len(rows)
    high_critical = len([r for r in rows if str(r.get("risk", "")).upper() in {"HIGH", "CRITICAL"}])
    qcp_count = len([r for r in rows if str(r.get("type_key", "")) == "qcp"])

    sections: list[str] = [
        "# Migration Blueprint Portfolio",
        "",
        "## Portfolio Summary",
        f"- Artifacts: {total}",
        f"- High/Critical artifacts: {high_critical}",
        f"- QCP artifacts: {qcp_count}",
        "",
        "## Artifact Blueprints",
    ]

    for row in rows:
        sections.extend(["", "---", "", build_blueprint(row)])

    return "\n".join(sections)
