"""Independent expected outcomes for a bounded, reproducible demo lab.

These expectations are authored here, outside the production checker. The lab
is a confidence signal for specific fixtures, not a general safety proof.
"""
from __future__ import annotations

from app.domain import BROKEN_EXAMPLE, REPAIRED_EXAMPLE, Selection, evaluate


def run_configuration_cases() -> list[dict]:
    missing = REPAIRED_EXAMPLE.model_copy(deep=True)
    missing.selections = [Selection(product_id="interface-unknown", quantity=1)
                          if item.product_id == "interface-8" else item for item in missing.selections]
    over_budget = REPAIRED_EXAMPLE.model_copy(deep=True)
    over_budget.requirements.budget_cents = 50_000
    cases = [
        ("Two-input interface for four people", BROKEN_EXAMPLE, {"input_capacity": "fail", "listening_capacity": "fail"}),
        ("Repaired four-person kit", REPAIRED_EXAMPLE, {"input_capacity": "pass", "listening_capacity": "pass", "budget": "pass"}),
        ("Unpublished input count", missing, {"input_capacity": "unknown"}),
        ("Kit above stated budget", over_budget, {"budget": "fail"}),
    ]
    report = []
    for name, config, expected in cases:
        actual = {item["code"]: item["status"] for item in evaluate(config)["checks"]}
        observed = {code: actual.get(code) for code in expected}
        report.append({"scenario": name, "expected": expected, "observed": observed,
                       "passed": observed == expected})
    return report
