
"""Independent expected outcomes for a bounded, reproducible demo lab.

These expectations are authored outside the production checker. The lab
is a confidence signal for specific fixtures, not a general safety proof.
"""

from __future__ import annotations

from app.domain import BROKEN_EXAMPLE, REPAIRED_EXAMPLE, Selection, evaluate


def run_configuration_cases() -> list[dict]:
    missing = REPAIRED_EXAMPLE.model_copy(deep=True)
    missing.selections = [
        Selection(product_id="interface-unknown", quantity=1)
        if item.product_id == "interface-8" else item
        for item in missing.selections
    ]

    over_budget = REPAIRED_EXAMPLE.model_copy(deep=True)
    over_budget.requirements.budget_cents = 50_000

    cases = [
        {
            "scenario": "Two-input interface for four people",
            "category": "COMPATIBILITY ATTACK",
            "rationale": (
                "A four-person setup needs sufficient independent input "
                "capacity. A two-input interface must not pass."
            ),
            "config": BROKEN_EXAMPLE,
            "expected": {
                "input_capacity": "fail",
                "listening_capacity": "fail",
            },
        },
        {
            "scenario": "Repaired four-person kit",
            "category": "VALID CONFIGURATION",
            "rationale": (
                "A compatible configuration should pass its input, "
                "listening and budget checks."
            ),
            "config": REPAIRED_EXAMPLE,
            "expected": {
                "input_capacity": "pass",
                "listening_capacity": "pass",
                "budget": "pass",
            },
        },
        {
            "scenario": "Unpublished input count",
            "category": "UNKNOWN SPECIFICATION",
            "rationale": (
                "An unknown product specification must remain unknown. "
                "The checker must not assume compatibility."
            ),
            "config": missing,
            "expected": {
                "input_capacity": "unknown",
            },
        },
        {
            "scenario": "Kit above stated budget",
            "category": "BUDGET ATTACK",
            "rationale": (
                "A configuration exceeding the buyer's declared budget "
                "must fail the budget check."
            ),
            "config": over_budget,
            "expected": {
                "budget": "fail",
            },
        },
    ]

    report = []

    for case in cases:
        actual = {
            item["code"]: item["status"]
            for item in evaluate(case["config"])["checks"]
        }

        expected = case["expected"]
        observed = {
            code: actual.get(code)
            for code in expected
        }

        report.append({
            "scenario": case["scenario"],
            "category": case["category"],
            "rationale": case["rationale"],
            "expected": expected,
            "observed": observed,
            "passed": observed == expected,
        })

    return report