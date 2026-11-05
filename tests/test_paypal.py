from types import SimpleNamespace

from app.paypal import ProviderOrder, verified_capture, verified_order_amount


def purchase():
    return SimpleNamespace(id="purchase-1", provider_order_id="ORDER-1", total_cents=81000, currency="USD")


def test_rejects_wrong_provider_amount_and_fractional_cent():
    order = ProviderOrder("ORDER-1", "APPROVED", None, {"purchase_units": [{
        "reference_id": "purchase-1", "amount": {"currency_code": "USD", "value": "810.001"}}]})
    assert not verified_order_amount(order, purchase())
    order.raw["purchase_units"][0]["amount"]["value"] = "811.00"
    assert not verified_order_amount(order, purchase())


def test_capture_needs_matching_reference_currency_and_completed_status():
    order = ProviderOrder("ORDER-1", "COMPLETED", None, {"purchase_units": [{
        "reference_id": "purchase-1", "payments": {"captures": [{
            "id": "capture-1", "status": "COMPLETED", "amount": {"currency_code": "USD", "value": "810.00"}}]}}]})
    assert verified_capture(order, purchase()) == "capture-1"
    order.raw["purchase_units"][0]["payments"]["captures"][0]["amount"]["currency_code"] = "EUR"
    assert verified_capture(order, purchase()) is None
