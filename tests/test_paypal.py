import asyncio
from types import SimpleNamespace

import httpx
import pytest

from app.paypal import ProviderOrder, ProviderUncertain, SandboxPayPal, verified_capture, verified_order_amount


def purchase():
    return SimpleNamespace(id="purchase-1", provider_order_id="ORDER-1", total_cents=81000, currency="USD", snapshot={})


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


def test_sandbox_http_timeout_is_uncertain_and_sends_capture_once(monkeypatch):
    requests = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/v1/oauth2/token":
            return httpx.Response(200, json={"access_token": "fixture-only"})
        return httpx.Response(408)

    async_client = httpx.AsyncClient
    transport = httpx.MockTransport(respond)
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: async_client(transport=transport, **kwargs))
    provider = SandboxPayPal("fixture-client-id", "fixture-client-secret")

    with pytest.raises(ProviderUncertain, match="408"):
        asyncio.run(provider.capture("ORDER-1", "c2ac714b-ff06-452b-80db-1f85f70e7744"))

    token, capture = requests
    assert token.url.path == "/v1/oauth2/token"
    assert capture.url.host == "api-m.sandbox.paypal.com"
    assert capture.method == "POST"
    assert capture.url.path == "/v2/checkout/orders/ORDER-1/capture"
    assert capture.headers["PayPal-Request-Id"] == "c2ac714b-ff06-452b-80db-1f85f70e7744"
    assert capture.headers["Prefer"] == "return=representation"
