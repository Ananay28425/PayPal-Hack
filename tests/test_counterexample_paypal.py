
"""Counterexample: adversarial PayPal response tests.

These tests challenge the payment verification boundary using
independently specified expected outcomes.
"""

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


def test_wrong_order_id_is_rejected():
    assert verified_capture(
        make_capture_order(order_id="ORDER-OTHER"),
        make_purchase(),
    ) is None


def test_wrong_purchase_reference_is_rejected():
    assert verified_capture(
        make_capture_order(reference_id="purchase-other"),
        make_purchase(),
    ) is None


def test_pending_capture_is_not_treated_as_success():
    assert verified_capture(
        make_capture_order(status="PENDING"),
        make_purchase(),
    ) is None


def test_missing_capture_id_is_rejected():
    assert verified_capture(
        make_capture_order(capture_id=None),
        make_purchase(),
    ) is None


def test_wrong_capture_amount_is_rejected():
    assert verified_capture(
        make_capture_order(amount="811.00"),
        make_purchase(),
    ) is None


def test_multiple_purchase_units_are_rejected():
    order = ProviderOrder(
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
    )

    assert not verified_order_amount(order, make_purchase())
