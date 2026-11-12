
"""Independent adversarial payment verification scenarios."""

from types import SimpleNamespace

from app.paypal import (
    ProviderOrder,
    verified_capture,
    verified_order_amount,
)


def make_purchase():
    return SimpleNamespace(
        id="purchase-1",
        provider_order_id="ORDER-1",
        total_cents=81000,
        currency="USD",
    )


def make_capture_order(
    order_id="ORDER-1",
    reference_id="purchase-1",
    capture_id="capture-1",
    status="COMPLETED",
    currency="USD",
    amount="810.00",
):
    return ProviderOrder(
        order_id,
        "COMPLETED",
        None,
        {
            "purchase_units": [{
                "reference_id": reference_id,
                "payments": {
                    "captures": [{
                        "id": capture_id,
                        "status": status,
                        "amount": {
                            "currency_code": currency,
                            "value": amount,
                        },
                    }]
                },
            }]
        },
    )


def run_payment_cases() -> list[dict]:
    """Run bounded payment-verification attack fixtures."""

    purchase = make_purchase()

    cases = [
        {
            "scenario": "Wrong PayPal order ID",
            "rationale": "A capture belonging to another provider order must be rejected.",
            "run": lambda: verified_capture(
                make_capture_order(order_id="ORDER-OTHER"), purchase
            ) is None,
        },
        {
            "scenario": "Wrong purchase reference",
            "rationale": "A provider order referencing another purchase must be rejected.",
            "run": lambda: verified_capture(
                make_capture_order(reference_id="purchase-other"), purchase
            ) is None,
        },
        {
            "scenario": "Pending capture",
            "rationale": "A pending capture must not be treated as completed payment.",
            "run": lambda: verified_capture(
                make_capture_order(status="PENDING"), purchase
            ) is None,
        },
        {
            "scenario": "Missing capture ID",
            "rationale": "A capture without an identifier must not be accepted.",
            "run": lambda: verified_capture(
                make_capture_order(capture_id=None), purchase
            ) is None,
        },
        {
            "scenario": "Incorrect capture amount",
            "rationale": "A capture amount different from the approved purchase total must be rejected.",
            "run": lambda: verified_capture(
                make_capture_order(amount="811.00"), purchase
            ) is None,
        },
        {
            "scenario": "Multiple purchase units",
            "rationale": "An ambiguous order containing multiple purchase units must be rejected.",
            "run": lambda: not verified_order_amount(
                ProviderOrder(
                    "ORDER-1",
                    "APPROVED",
                    None,
                    {
                        "purchase_units": [
                            {
                                "reference_id": "purchase-1",
                                "amount": {
                                    "currency_code": "USD",
                                    "value": "810.00",
                                },
                            },
                            {
                                "reference_id": "another-purchase",
                                "amount": {
                                    "currency_code": "USD",
                                    "value": "10.00",
                                },
                            },
                        ]
                    },
                ),
                purchase,
            ),
        },
    ]

    report = []

    for case in cases:
        rejected = case["run"]()

        report.append({
            "scenario": case["scenario"],
            "category": "PAYMENT INTEGRITY ATTACK",
            "rationale": case["rationale"],
            "expected": "REJECT",
            "observed": "REJECT" if rejected else "ACCEPT",
            "passed": rejected,
        })

    return report
