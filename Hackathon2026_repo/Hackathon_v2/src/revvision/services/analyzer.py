from __future__ import annotations

import hashlib
import re
from typing import Any, Iterable

import pandas as pd

from revvision.detection import detect_file_type
from revvision.parsers import parse_apex, parse_flow, parse_generic, parse_qcp, parse_xml_rule, parse_discount_schedule
from revvision.types import ParseResult

RISK_PRESETS: dict[str, tuple[int, int, int]] = {
    "Strict": (150, 350, 600),
    "Balanced": (250, 500, 750),
}

TYPE_BASE_WEIGHTS: dict[str, int] = {
    "qcp": 95,
    "apex_trigger": 75,
    "apex_class": 62,
    "flow": 52,
    "product_rule": 45,
    "price_rule": 40,
    "lookup_table": 24,
    "summary_variable": 20,
    "object_metadata": 16,
    "xml_generic": 14,
    "unknown": 10,
}

MANDATORY_COMPONENT_GROUPS: list[dict[str, object]] = [
    {"id": "pricing_logic", "label": "Pricing logic (Price Rule / Product Rule / QCP)", "keys": {"price_rule", "product_rule", "qcp"}},
    {"id": "automation", "label": "Quote automation (Flow / Apex)", "keys": {"flow", "apex_class", "apex_trigger"}},
    {"id": "pricing_data", "label": "Pricing data inputs (Lookup / Summary / Price Rule)", "keys": {"lookup_table", "summary_variable", "price_rule"}},
    {"id": "customization", "label": "Org customization layer (Object metadata or Apex)", "keys": {"object_metadata", "apex_class", "apex_trigger"}},
]

MIN_SUPPORTED_FILES = 6
RECOMMENDED_SUPPORTED_FILES = 10

UPLOAD_REQUIREMENTS: list[dict[str, object]] = [
    {"label": "Pricing logic artifacts (QCP, Price Rule, Product Rule)", "keys": {"qcp", "price_rule", "product_rule"}, "minimum": 2, "recommended": 3},
    {"label": "Quote automation artifacts (Flow, Apex Class/Trigger)", "keys": {"flow", "apex_class", "apex_trigger"}, "minimum": 1, "recommended": 2},
    {"label": "Pricing data artifacts (Lookup, Summary, Price Rule)", "keys": {"lookup_table", "summary_variable", "price_rule"}, "minimum": 1, "recommended": 2},
    {"label": "Customization artifacts (Object Meta or Apex)", "keys": {"object_metadata", "apex_class", "apex_trigger"}, "minimum": 1, "recommended": 1},
]


def _get_col(df: pd.DataFrame, col: str, default: Any) -> pd.Series:
    if col in df.columns:
        return df[col]
    return pd.Series([default] * len(df), index=df.index)


def _assessment_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    view = df.copy()
    if "excluded_from_assessment" in view.columns:
        view = view[~view["excluded_from_assessment"]]
    return view


def _strip_comments(content: str) -> str:
    cleaned = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    cleaned = re.sub(r"//.*?$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"<!--.*?-->", "", cleaned, flags=re.DOTALL)
    return cleaned


def _canonical_text(content: str) -> str:
    text = _strip_comments(content).lower()
    return re.sub(r"\s+", "", text)


def _semantic_text(content: str) -> str:
    text = _strip_comments(content).lower()
    text = re.sub(r"'[^']*'|\"[^\"]*\"", "str", text)
    text = re.sub(r"\b\d+\b", "0", text)
    text = re.sub(r"\s+", "", text)
    return text


def _hash_text(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8", errors="ignore")).hexdigest()


def _content_signals(content: str) -> dict[str, int]:
    return {
        "dynamic_soql": len(re.findall(r"\bDatabase\.query\s*\(", content, flags=re.IGNORECASE)),
        "callouts": len(re.findall(r"\bHttp(Request|Response)?\b|\bNamedCredential\b", content, flags=re.IGNORECASE)),
        "pricing_keywords": len(re.findall(r"discount|netprice|listprice|prorat|uplift|bundle", content, flags=re.IGNORECASE)),
    }


def get_risk(score: int, low: int, moderate: int, high: int) -> str:
    if score < low:
        return "LOW"
    if score < moderate:
        return "MODERATE"
    if score < high:
        return "HIGH"
    return "CRITICAL"


def effort_weeks(score: int) -> float:
    return max(0.1, round(score / 1000 * 2.0, 1))


def parse_by_type(type_key: str, content: str) -> ParseResult:
    if type_key in {"apex_class", "apex_trigger"}:
        return parse_apex(content)
    if type_key == "flow":
        return parse_flow(content)
    if type_key == "qcp":
        return parse_qcp(content)
    if type_key == "price_rule":
        return parse_xml_rule(content, is_product_rule=False)
    if type_key == "product_rule":
        return parse_xml_rule(content, is_product_rule=True)
    if type_key == "discount_schedule":
        return parse_discount_schedule(content)
    return parse_generic(content)


def compute_migration_score(type_key: str, parsed: ParseResult, content: str) -> int:
    base = TYPE_BASE_WEIGHTS.get(type_key, TYPE_BASE_WEIGHTS["unknown"])
    sbqq_refs = int(parsed.extra.get("sbqq_refs", 0))
    qcp_hooks = len(parsed.extra.get("qcp_hooks", []))
    signals = _content_signals(content)

    score = (
        base
        + parsed.conditions * 2
        + parsed.actions * 4
        + parsed.lookups * 5
        + parsed.summary_vars * 3
        + parsed.soql_hits * 8
        + parsed.hardcoded_ids * 18
        + sbqq_refs * 6
        + qcp_hooks * 22
        + signals["dynamic_soql"] * 14
        + signals["callouts"] * 10
        + signals["pricing_keywords"] * 2
    )

    if parsed.qcp:
        score += 45
    if type_key == "apex_trigger":
        score += 12
    if type_key == "flow" and parsed.lookups > 0:
        score += 10

    return min(1000, int(score))


def analyze_uploaded_files(
    uploaded_files: Iterable,
    low_threshold: int,
    moderate_threshold: int,
    high_threshold: int,
) -> pd.DataFrame:
    artifacts: list[dict[str, Any]] = []
    exact_seen: dict[str, str] = {}
    canonical_seen: dict[str, str] = {}
    semantic_seen: dict[str, str] = {}

    for file in uploaded_files:
        raw = file.read()
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            content = raw.decode("latin-1")

        detected = detect_file_type(file.name, content)
        parsed = parse_by_type(detected.type_key, content)
        score = compute_migration_score(detected.type_key, parsed, content)
        risk = get_risk(score, low_threshold, moderate_threshold, high_threshold)

        raw_hash = hashlib.sha1(raw).hexdigest()
        canonical_hash = _hash_text(_canonical_text(content))
        semantic_hash = _hash_text(_semantic_text(content))

        duplicate_reason = ""
        duplicate_of = ""
        if raw_hash in exact_seen:
            duplicate_reason = "EXACT_DUPLICATE"
            duplicate_of = exact_seen[raw_hash]
        elif canonical_hash in canonical_seen:
            duplicate_reason = "NORMALIZED_DUPLICATE"
            duplicate_of = canonical_seen[canonical_hash]
        elif semantic_hash in semantic_seen and detected.type_key != "unknown":
            duplicate_reason = "SEMANTIC_DUPLICATE"
            duplicate_of = semantic_seen[semantic_hash]

        if raw_hash not in exact_seen:
            exact_seen[raw_hash] = file.name
        if canonical_hash not in canonical_seen:
            canonical_seen[canonical_hash] = file.name
        if semantic_hash not in semantic_seen:
            semantic_seen[semantic_hash] = file.name

        insights = list(parsed.insights)
        if duplicate_reason:
            insights.append(f"Excluded from scoring: {duplicate_reason} of {duplicate_of}.")

        artifacts.append(
            {
                "file_name": file.name,
                "type_label": detected.label,
                "type_key": detected.type_key,
                "badge": detected.badge,
                "score": 0 if duplicate_reason else score,
                "risk": "LOW" if duplicate_reason else risk,
                "est_weeks": 0.0 if duplicate_reason else effort_weeks(score),
                "qcp": parsed.qcp,
                "conditions": parsed.conditions,
                "actions": parsed.actions,
                "lookups": parsed.lookups,
                "summary_vars": parsed.summary_vars,
                "hardcoded_ids": parsed.hardcoded_ids,
                "soql_hits": parsed.soql_hits,
                "insights": insights,
                "raw": content[:12000],
                "extra": parsed.extra,
                "excluded_from_assessment": bool(duplicate_reason),
                "duplicate_reason": duplicate_reason,
                "duplicate_of": duplicate_of,
            }
        )

    return pd.DataFrame(artifacts)


def org_risk(
    df: pd.DataFrame,
    low_threshold: int = 250,
    moderate_threshold: int = 500,
    high_threshold: int = 750,
) -> str:
    assessed = _assessment_df(df)
    if assessed.empty:
        return "LOW"

    total_score = int(_get_col(assessed, "score", 0).sum())
    # Org risk follows the active threshold profile directly against portfolio score.
    return get_risk(total_score, low_threshold, moderate_threshold, high_threshold)


def coverage_table(df: pd.DataFrame) -> pd.DataFrame:
    assessed = _assessment_df(df)
    if assessed.empty:
        return pd.DataFrame(columns=["Component", "Status", "Artifacts"])

    rows: list[dict[str, object]] = []
    type_col = _get_col(assessed, "type_key", "unknown")
    for group in MANDATORY_COMPONENT_GROUPS:
        keys = set(group["keys"])
        count = int(type_col.isin(keys).sum())
        rows.append({"Component": str(group["label"]), "Status": "OK" if count > 0 else "MISSING", "Artifacts": count})
    return pd.DataFrame(rows)


def readiness_context(df: pd.DataFrame) -> dict[str, object]:
    assessed = _assessment_df(df)
    if assessed.empty:
        return {
            "status": "INCOMPLETE",
            "confidence_score": 0,
            "confidence": "LOW",
            "supported_files": 0,
            "unknown_files": 0,
            "missing_mandatory": [str(item["label"]) for item in MANDATORY_COMPONENT_GROUPS],
            "pricing_artifacts": 0,
            "mandatory_met": 0,
            "mandatory_total": len(MANDATORY_COMPONENT_GROUPS),
            "duplicate_files": int(_get_col(df, "excluded_from_assessment", False).sum()) if not df.empty else 0,
        }

    type_col = _get_col(assessed, "type_key", "unknown")
    unknown_files = int((type_col == "unknown").sum())
    supported_files = int(len(assessed) - unknown_files)
    missing: list[str] = []

    for group in MANDATORY_COMPONENT_GROUPS:
        if int(type_col.isin(set(group["keys"])).sum()) == 0:
            missing.append(str(group["label"]))

    pricing_artifacts = int(type_col.isin({"price_rule", "product_rule", "qcp"}).sum())
    mandatory_total = len(MANDATORY_COMPONENT_GROUPS)
    mandatory_met = mandatory_total - len(missing)
    duplicate_files = int(_get_col(df, "excluded_from_assessment", False).sum()) if not df.empty else 0

    confidence_score = 100
    if supported_files < MIN_SUPPORTED_FILES:
        confidence_score -= 30
    confidence_score -= min(20, unknown_files * 8)
    confidence_score -= len(missing) * 18
    confidence_score -= min(25, duplicate_files * 5)
    if pricing_artifacts < 2:
        confidence_score -= 20
    confidence_score = max(0, confidence_score)

    confidence = "HIGH" if confidence_score >= 75 else "MEDIUM" if confidence_score >= 45 else "LOW"
    status = "READY" if not missing and confidence_score >= 75 else "PARTIAL" if mandatory_met > 0 else "INCOMPLETE"

    return {
        "status": status,
        "confidence_score": confidence_score,
        "confidence": confidence,
        "supported_files": supported_files,
        "unknown_files": unknown_files,
        "missing_mandatory": missing,
        "pricing_artifacts": pricing_artifacts,
        "mandatory_met": mandatory_met,
        "mandatory_total": mandatory_total,
        "duplicate_files": duplicate_files,
    }


def pricing_signal_summary(df: pd.DataFrame) -> dict[str, int]:
    assessed = _assessment_df(df)
    if assessed.empty:
        return {"conditions": 0, "actions": 0, "lookups": 0, "qcp_files": 0, "high_risk_pricing_files": 0}

    type_col = _get_col(assessed, "type_key", "unknown")
    risk_col = _get_col(assessed, "risk", "LOW")
    pricing_mask = type_col.isin({"price_rule", "product_rule", "qcp"})
    pricing_df = assessed[pricing_mask]
    high_risk_pricing = int(_get_col(pricing_df, "risk", "LOW").isin(["HIGH", "CRITICAL"]).sum()) if not pricing_df.empty else 0
    return {
        "conditions": int(_get_col(assessed, "conditions", 0).sum()),
        "actions": int(_get_col(assessed, "actions", 0).sum()),
        "lookups": int(_get_col(assessed, "lookups", 0).sum()),
        "qcp_files": int(_get_col(assessed, "qcp", False).sum()),
        "high_risk_pricing_files": high_risk_pricing,
    }


def upload_requirements_report(df: pd.DataFrame) -> dict[str, object]:
    assessed = _assessment_df(df)
    type_col = _get_col(assessed, "type_key", "unknown") if not assessed.empty else pd.Series(dtype=str)
    supported_files = int((type_col != "unknown").sum()) if not assessed.empty else 0
    unknown_files = int((type_col == "unknown").sum()) if not assessed.empty else 0
    duplicate_files = int(_get_col(df, "excluded_from_assessment", False).sum()) if not df.empty else 0
    duplicate_names = _get_col(df, "file_name", "").loc[_get_col(df, "excluded_from_assessment", False)].tolist() if not df.empty else []

    checklist: list[dict[str, object]] = []
    blockers: list[str] = []
    recommendations: list[str] = []

    if supported_files < MIN_SUPPORTED_FILES:
        blockers.append(f"Upload at least {MIN_SUPPORTED_FILES} unique supported artifacts (currently {supported_files}).")
    if supported_files < RECOMMENDED_SUPPORTED_FILES:
        recommendations.append(f"Upload around {RECOMMENDED_SUPPORTED_FILES}+ unique supported artifacts for stronger confidence.")
    if unknown_files > 0:
        recommendations.append(f"{unknown_files} file(s) are unclassified; include clearer CPQ metadata exports for better scoring.")
    if duplicate_files > 0:
        blockers.append(f"Remove duplicate/near-duplicate artifacts ({duplicate_files} detected) and upload unique files.")

    for req in UPLOAD_REQUIREMENTS:
        keys = set(req["keys"])
        count = int(type_col.isin(keys).sum()) if not assessed.empty else 0
        minimum = int(req["minimum"])
        recommended = int(req["recommended"])
        checklist.append({"Requirement": str(req["label"]), "Current": count, "Minimum": minimum, "Recommended": recommended, "Status": "PASS" if count >= minimum else "FAIL"})
        if count < minimum:
            blockers.append(f"{req['label']}: minimum {minimum}, currently {count}.")
        elif count < recommended:
            recommendations.append(f"{req['label']}: recommended {recommended}, currently {count}.")

    return {
        "supported_files": supported_files,
        "unknown_files": unknown_files,
        "duplicate_files": duplicate_files,
        "duplicate_file_names": duplicate_names,
        "minimum_supported_files": MIN_SUPPORTED_FILES,
        "recommended_supported_files": RECOMMENDED_SUPPORTED_FILES,
        "checklist": checklist,
        "blockers": blockers,
        "recommendations": recommendations,
        "ready_for_assessment": len(blockers) == 0,
    }

def compute_roi(df: pd.DataFrame) -> dict[str, float]:
    # Handle empty or missing columns
    if df.empty or "excluded_from_assessment" not in df.columns:
        return {
            "artifacts": 0,
            "manual_hours": 0,
            "ai_hours": 0,
            "hours_saved": 0,
            "cost_saved": 0,
            "efficiency_gain_pct": 0,
        }

    total = len(df[df["excluded_from_assessment"] == False])

    manual_hours = total * 1.5
    ai_hours = total * 0.1
    hours_saved = manual_hours - ai_hours
    cost_saved = hours_saved * 75

    return {
        "artifacts": total,
        "manual_hours": round(manual_hours, 1),
        "ai_hours": round(ai_hours, 1),
        "hours_saved": round(hours_saved, 1),
        "cost_saved": round(cost_saved, 2),
        "efficiency_gain_pct": round((hours_saved / manual_hours * 100) if manual_hours else 0),
    }
