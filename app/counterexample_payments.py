
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
    purchase = make_purchase()

    cases = [
        (
            "Wrong PayPal order ID",
            "A capture belonging to another provider order must be rejected.",
            lambda: verified_capture(
                make_capture_order(order_id="ORDER-OTHER"), purchase
            ) is None,
        ),
        (
            "Wrong purchase reference",
            "An order referencing another purchase must be rejected.",
            lambda: verified_capture(
                make_capture_order(reference_id="purchase-other"), purchase
            ) is None,
        ),
        (
            "Pending capture",
            "A pending capture must not count as completed payment.",
            lambda: verified_capture(
                make_capture_order(status="PENDING"), purchase
            ) is None,
        ),
        (
            "Missing capture ID",
            "A capture without an identifier must be rejected.",
            lambda: verified_capture(
                make_capture_order(capture_id=None), purchase
            ) is None,
        ),
        (
            "Incorrect capture amount",
            "A mismatched capture amount must be rejected.",
            lambda: verified_capture(
                make_capture_order(amount="811.00"), purchase
            ) is None,
        ),
        (
            "Multiple purchase units",
            "An ambiguous order with multiple purchase units must be rejected.",
            lambda: not verified_order_amount(
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
        ),
    ]

    report = []

    for scenario, rationale, check in cases:
        rejected = check()

        report.append({
            "scenario": scenario,
            "category": "PAYMENT INTEGRITY ATTACK",
            "rationale": rationale,
            "expected": "REJECT",
            "observed": "REJECT" if rejected else "ACCEPT",
            "passed": rejected,
        })

    return report
