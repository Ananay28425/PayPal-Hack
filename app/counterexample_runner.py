
"""Unified runner for Assembly Proof adversarial scenarios."""

from app.counterexamples import run_configuration_cases
from app.counterexample_payments import run_payment_cases


def run_all_counterexamples() -> dict:
    configuration_cases = run_configuration_cases()
    payment_cases = run_payment_cases()

    all_cases = configuration_cases + payment_cases

    passed = sum(
        1 for case in all_cases if case["passed"]
    )

    return {
        "summary": {
            "total": len(all_cases),
            "passed": passed,
            "failed": len(all_cases) - passed,
        },
        "groups": {
            "configuration": {
                "total": len(configuration_cases),
                "passed": sum(
                    1 for case in configuration_cases if case["passed"]
                ),
                "cases": configuration_cases,
            },
            "payment_integrity": {
                "total": len(payment_cases),
                "passed": sum(
                    1 for case in payment_cases if case["passed"]
                ),
                "cases": payment_cases,
            },
        },
        "cases": all_cases,
    }
