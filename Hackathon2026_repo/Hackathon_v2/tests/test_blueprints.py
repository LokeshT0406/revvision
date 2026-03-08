from revvision.services.blueprints import build_blueprint, build_portfolio_blueprint


def test_build_blueprint_qcp_contains_pricing_json():
    row = {
        "file_name": "QcpCalculator.js",
        "type_key": "qcp",
        "risk": "HIGH",
        "score": 180,
        "extra": {"qcp_hooks": ["onBeforeCalculate", "onCalculate"]},
    }
    output = build_blueprint(row)
    assert "Pricing Procedure JSON" in output
    assert "RcaPricingHookService" in output


def test_build_portfolio_blueprint_includes_all_artifacts():
    rows = [
        {"file_name": "A.cls", "type_key": "apex_class", "risk": "LOW", "score": 25, "extra": {}},
        {"file_name": "B.js", "type_key": "qcp", "risk": "HIGH", "score": 180, "extra": {"qcp_hooks": ["onCalculate"]}},
    ]
    output = build_portfolio_blueprint(rows)
    assert "Migration Blueprint Portfolio" in output
    assert "A.cls" in output
    assert "B.js" in output
