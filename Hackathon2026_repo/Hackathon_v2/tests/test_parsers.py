from revvision.parsers import parse_apex, parse_flow, parse_qcp


def test_parse_apex_flags_sbqq_refs():
    result = parse_apex("public class A { void x(){ SBQQ__Quote__c q; [SELECT Id FROM Account]; } }")
    assert result.extra["sbqq_refs"] >= 1
    assert result.score > 0


def test_parse_qcp_sets_qcp_true():
    result = parse_qcp("export function onBeforeCalculate(q, lines, conn) { return conn.query('SELECT Id FROM Account'); }")
    assert result.qcp is True
    assert "Detected hooks" in " ".join(result.insights)


def test_parse_flow_handles_namespaced_metadata():
    flow_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
  <decisions/>
  <loops/>
  <actionCalls/>
  <recordLookups/>
</Flow>"""
    result = parse_flow(flow_xml)
    assert result.conditions == 1
    assert result.actions == 1
    assert result.lookups == 1
