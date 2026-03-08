import pandas as pd

from revvision.services.analyzer import (
    analyze_uploaded_files,
    coverage_table,
    org_risk,
    pricing_signal_summary,
    readiness_context,
    upload_requirements_report,
)


def test_readiness_context_flags_missing_mandatory_components():
    df = pd.DataFrame(
        [
            {"type_key": "price_rule", "qcp": False, "risk": "HIGH", "conditions": 3, "actions": 2, "lookups": 1},
            {"type_key": "unknown", "qcp": False, "risk": "LOW", "conditions": 0, "actions": 0, "lookups": 0},
        ]
    )
    context = readiness_context(df)
    assert context["status"] in {"PARTIAL", "INCOMPLETE"}
    assert context["unknown_files"] == 1
    assert len(context["missing_mandatory"]) >= 1


def test_coverage_table_marks_present_and_missing():
    df = pd.DataFrame([{"type_key": "qcp"}])
    table = coverage_table(df)
    assert "Pricing logic (Price Rule / Product Rule / QCP)" in table["Component"].tolist()
    assert "MISSING" in table["Status"].tolist()


def test_pricing_signal_summary_counts_high_risk_pricing():
    df = pd.DataFrame(
        [
            {"type_key": "qcp", "risk": "HIGH", "conditions": 1, "actions": 2, "lookups": 3, "qcp": True},
            {"type_key": "flow", "risk": "LOW", "conditions": 2, "actions": 1, "lookups": 0, "qcp": False},
        ]
    )
    summary = pricing_signal_summary(df)
    assert summary["high_risk_pricing_files"] == 1
    assert summary["qcp_files"] == 1


def test_upload_requirements_report_fails_when_minimums_missing():
    df = pd.DataFrame([{"type_key": "qcp"}])
    report = upload_requirements_report(df)
    assert report["ready_for_assessment"] is False
    assert len(report["blockers"]) >= 1


def test_upload_requirements_report_passes_with_balanced_mix():
    df = pd.DataFrame(
        [
            {"type_key": "qcp"},
            {"type_key": "price_rule"},
            {"type_key": "flow"},
            {"type_key": "lookup_table"},
            {"type_key": "apex_class"},
            {"type_key": "object_metadata"},
        ]
    )
    report = upload_requirements_report(df)
    assert report["ready_for_assessment"] is True


def test_org_risk_reflects_risk_distribution():
    df = pd.DataFrame(
        [
            {"risk": "LOW"},
            {"risk": "LOW"},
            {"risk": "MODERATE"},
            {"risk": "HIGH"},
            {"risk": "HIGH"},
        ]
    )
    assert org_risk(df) == "HIGH"


class _Upload:
    def __init__(self, name: str, content: str):
        self.name = name
        self._bytes = content.encode("utf-8")

    def read(self):
        return self._bytes


def test_analyze_uploaded_files_flags_normalized_duplicates():
    files = [
        _Upload("A.cls", "public class A { void run(){ System.debug('x'); } }"),
        _Upload("B.cls", "public  class A{void run(){System.debug('x');}}"),
    ]
    df = analyze_uploaded_files(files, 70, 150, 260)
    assert int(df["excluded_from_assessment"].sum()) == 1
    report = upload_requirements_report(df)
    assert report["duplicate_files"] == 1
    assert report["ready_for_assessment"] is False
