import pandas as pd

from revvision.services.testing import build_migration_test_plan


def test_migration_test_plan_contains_scope():
    df = pd.DataFrame([{"qcp": True, "risk": "HIGH", "est_weeks": 2.0}])
    plan = build_migration_test_plan(df)
    assert "Scope Summary" in plan
    assert "Mandatory Pricing Parity Scenarios" in plan
