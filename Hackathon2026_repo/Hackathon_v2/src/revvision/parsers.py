from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from revvision.constants import QCP_HOOKS
from revvision.types import ParseResult

NS = {"ns": "http://soap.sforce.com/2006/04/metadata"}


def _count_hardcoded_ids(content: str) -> int:
    return len(re.findall(r"00[A-Za-z0-9]{12,15}", content))


def _count_soql(content: str) -> int:
    return len(re.findall(r"\bSELECT\b", content, flags=re.IGNORECASE))


def _count_local_tags(root: ET.Element, *local_names: str) -> int:
    names = set(local_names)
    total = 0
    for element in root.iter():
        tag = element.tag
        if not isinstance(tag, str):
            continue
        local = tag.split("}", 1)[-1]
        if local in names:
            total += 1
    return total


def parse_apex(content: str) -> ParseResult:
    methods = len(re.findall(r"\b(public|private|global|protected)\s+\w+\s+\w+\s*\(", content))
    dml_ops = len(re.findall(r"\b(insert|update|delete|upsert|merge)\s", content, flags=re.IGNORECASE))
    soql_hits = len(re.findall(r"\[SELECT\b", content, flags=re.IGNORECASE))
    hardcoded = _count_hardcoded_ids(content)
    sbqq_refs = len(re.findall(r"SBQQ__", content))
    hooks = [h for h in QCP_HOOKS if h in content]

    score = methods * 2 + dml_ops * 4 + soql_hits * 5 + hardcoded * 12 + sbqq_refs * 6 + len(hooks) * 25
    insights = [
        f"{methods} methods, {soql_hits} SOQL, {dml_ops} DML operations",
        f"{sbqq_refs} SBQQ references require object remapping" if sbqq_refs else "No SBQQ references detected",
        f"QCP hook signatures found: {', '.join(hooks)}" if hooks else "No QCP hook signatures found",
    ]
    return ParseResult(
        conditions=methods,
        actions=dml_ops,
        lookups=soql_hits,
        hardcoded_ids=hardcoded,
        soql_hits=soql_hits,
        qcp=bool(hooks),
        score=score,
        insights=insights,
        extra={"sbqq_refs": sbqq_refs, "qcp_hooks": hooks},
    )


def parse_qcp(content: str) -> ParseResult:
    hooks = [h for h in QCP_HOOKS if h in content]
    lookups = len(re.findall(r"conn\.query|\.query\(", content))
    conditions = len(re.findall(r"\bif\s*\(|\bswitch\s*\(", content))
    hardcoded = _count_hardcoded_ids(content)
    score = len(hooks) * 40 + lookups * 10 + conditions * 3 + hardcoded * 15
    return ParseResult(
        conditions=conditions,
        actions=len(hooks),
        lookups=lookups,
        hardcoded_ids=hardcoded,
        soql_hits=lookups,
        qcp=True,
        score=score,
        insights=[
            "No direct RCA equivalent for QCP; rebuild as Pricing Procedure + Apex actions",
            f"Detected hooks: {', '.join(hooks) if hooks else 'none'}",
        ],
        extra={"qcp_hooks": hooks},
    )


def parse_flow(content: str) -> ParseResult:
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        root = ET.Element("Flow")
    decisions = _count_local_tags(root, "decisions")
    loops = _count_local_tags(root, "loops")
    actions = _count_local_tags(root, "actionCalls")
    lookups = _count_local_tags(root, "recordLookups", "recordUpdates", "recordCreates", "recordDeletes")
    sbqq_refs = len(re.findall(r"SBQQ__", content))
    hardcoded = _count_hardcoded_ids(content)
    score = decisions * 5 + loops * 8 + actions * 6 + lookups * 4 + sbqq_refs * 8 + hardcoded * 12
    return ParseResult(
        conditions=decisions,
        actions=actions,
        lookups=lookups,
        hardcoded_ids=hardcoded,
        score=score,
        insights=[
            f"{decisions} decision nodes, {lookups} data operations",
            f"{sbqq_refs} SBQQ references in flow metadata" if sbqq_refs else "No SBQQ references detected",
        ],
        extra={"sbqq_refs": sbqq_refs},
    )


def parse_xml_rule(content: str, is_product_rule: bool) -> ParseResult:
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        root = ET.Element("BrokenXML")

    conditions = len(root.findall(".//ns:conditions", namespaces=NS))
    actions = len(root.findall(".//ns:priceActions", namespaces=NS))
    lookups = len(root.findall(".//ns:lookupQueries", namespaces=NS))
    summary_vars = len(root.findall(".//ns:summaryVariables", namespaces=NS))
    hardcoded = _count_hardcoded_ids(content)
    soql_hits = _count_soql(content)

    score = conditions * 3 + actions * 4 + lookups * 8 + summary_vars * 6 + hardcoded * 12 + soql_hits * 5
    if is_product_rule:
        score += 10

    kind = "Product Rule" if is_product_rule else "Price Rule"
    return ParseResult(
        conditions=conditions,
        actions=actions,
        lookups=lookups,
        summary_vars=summary_vars,
        hardcoded_ids=hardcoded,
        soql_hits=soql_hits,
        score=score,
        insights=[
            f"{kind} with {conditions} conditions, {actions} actions",
            "Map lookups to Decision Tables / Price Matrices" if lookups else "No lookup query dependencies",
        ],
    )


def parse_generic(content: str) -> ParseResult:
    hardcoded = _count_hardcoded_ids(content)
    soql_hits = _count_soql(content)
    sbqq_refs = len(re.findall(r"SBQQ__", content))
    score = hardcoded * 8 + soql_hits * 4 + sbqq_refs * 5
    return ParseResult(
        hardcoded_ids=hardcoded,
        soql_hits=soql_hits,
        score=score,
        insights=[
            f"{sbqq_refs} SBQQ references detected" if sbqq_refs else "No SBQQ references detected",
        ],
        extra={"sbqq_refs": sbqq_refs},
    )

def parse_discount_schedule(content: str) -> ParseResult:
    root = ET.fromstring(content)
    tiers = len(root.findall(".//ns:discountTiers", namespaces=NS))
    hardcoded = _count_hardcoded_ids(content)
    return ParseResult(
        conditions=tiers,
        score=tiers * 3 + hardcoded * 10,
        insights=[f"{tiers} discount tiers detected"],
    )
