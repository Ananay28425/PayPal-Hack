"""Narrow PayPal Orders v2 adapter. No production endpoint is accepted."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import httpx


SANDBOX_BASE = "https://api-m.sandbox.paypal.com"


class ProviderUncertain(Exception):
    """The provider may have processed the request; preserve its operation ID."""


class ProviderRejected(Exception):
    """The provider explicitly rejected the request."""


@dataclass(frozen=True)
class ProviderOrder:
    id: str
    status: str
    approval_url: str | None
    raw: dict


class SandboxPayPal:
    def __init__(self, client_id: str, client_secret: str):
        if not client_id or not client_secret:
            raise ValueError("Sandbox PayPal client ID and secret are required")
        self.client_id = client_id
        self.client_secret = client_secret

    async def _token(self) -> str:
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                response = await client.post(f"{SANDBOX_BASE}/v1/oauth2/token",
                    auth=(self.client_id, self.client_secret), data={"grant_type": "client_credentials"})
            response.raise_for_status()
            return response.json()["access_token"]
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise ProviderUncertain("PayPal authentication unavailable") from exc

    async def _request(self, method: str, path: str, *, request_id: str | None = None, body: dict | None = None) -> dict:
        token = await self._token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Prefer": "return=representation"}
        if request_id:
            headers["PayPal-Request-Id"] = request_id
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.request(method, SANDBOX_BASE + path, headers=headers, json=body)
        except httpx.RequestError as exc:
            raise ProviderUncertain("PayPal response unavailable; operation outcome unknown") from exc
        if response.status_code >= 500 or response.status_code == 429:
            raise ProviderUncertain(f"PayPal returned HTTP {response.status_code}; operation outcome unknown")
        if response.status_code >= 400:
            raise ProviderRejected(f"PayPal rejected operation: HTTP {response.status_code}")
        try:
            data = response.json()
        except ValueError as exc:
            raise ProviderUncertain("PayPal response was not valid JSON") from exc
        if not isinstance(data, dict):
            raise ProviderUncertain("PayPal response was not an object")
        return data

    @staticmethod
    def _order(data: dict, *, approval: bool = False) -> ProviderOrder:
        order_id = data.get("id")
        status = data.get("status")
        if not isinstance(order_id, str) or not order_id or not isinstance(status, str):
            raise ProviderUncertain("PayPal order response lacks identity or status")
        links = data.get("links", [])
        if not isinstance(links, list):
            links = []
        url = next((link.get("href") for link in links if isinstance(link, dict)
                    and link.get("rel") in ("payer-action", "approve") and isinstance(link.get("href"), str)), None)
        return ProviderOrder(id=order_id, status=status, approval_url=url if approval else None, raw=data)

    async def create_order(self, purchase, request_id: str, return_base: str) -> ProviderOrder:
        amount = f"{Decimal(purchase.total_cents) / Decimal(100):.2f}"
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [{"reference_id": purchase.id,
                                "amount": {"currency_code": purchase.currency, "value": amount}}],
            "payment_source": {"paypal": {"experience_context": {
                "return_url": f"{return_base}/?purchase={purchase.id}&paypal_return=1",
                "cancel_url": f"{return_base}/?purchase={purchase.id}&paypal_cancel=1",
                "user_action": "PAY_NOW"}}},
        }
        data = await self._request("POST", "/v2/checkout/orders", request_id=request_id, body=payload)
        return self._order(data, approval=True)

    async def get_order(self, order_id: str) -> ProviderOrder:
        data = await self._request("GET", f"/v2/checkout/orders/{order_id}")
        return self._order(data)

    async def capture(self, order_id: str, request_id: str) -> ProviderOrder:
        data = await self._request("POST", f"/v2/checkout/orders/{order_id}/capture", request_id=request_id, body={})
        return self._order(data)


def verified_capture(order: ProviderOrder, purchase) -> str | None:
    """Require matching provider order, purchase unit, capture amount and status."""
    if order.id != purchase.provider_order_id or order.status != "COMPLETED":
        return None
    for unit in order.raw.get("purchase_units", []):
        if unit.get("reference_id") != purchase.id:
            continue
        for capture in unit.get("payments", {}).get("captures", []):
            amount = capture.get("amount", {})
            try:
                value = Decimal(str(amount.get("value"))) * 100
                if value != value.to_integral_value():
                    continue
                cents = int(value)
            except (InvalidOperation, TypeError, ValueError):
                continue
            if (capture.get("status") == "COMPLETED" and amount.get("currency_code") == purchase.currency
                    and cents == purchase.total_cents and capture.get("id")):
                return str(capture["id"])
    return None


def verified_order_amount(order: ProviderOrder, purchase) -> bool:
    if order.id != purchase.provider_order_id:
        return False
    units = order.raw.get("purchase_units", [])
    if len(units) != 1 or units[0].get("reference_id") != purchase.id:
        return False
    amount = units[0].get("amount", {})
    try:
        value = Decimal(str(amount.get("value"))) * 100
        if value != value.to_integral_value():
            return False
        cents = int(value)
    except (InvalidOperation, TypeError, ValueError):
        return False
    return amount.get("currency_code") == purchase.currency and cents == purchase.total_cents


class MockPayPal:
    """Local fake for UX and fault testing; never presented as PayPal Sandbox."""
    def __init__(self):
        self.captures: dict[str, dict] = {}

    async def create_order(self, purchase, request_id: str, return_base: str) -> ProviderOrder:
        order_id = f"MOCK-{purchase.id}"
        return ProviderOrder(order_id, "CREATED", f"{return_base}/?purchase={purchase.id}&mock_approve=1", {})

    async def get_order(self, order_id: str, purchase) -> ProviderOrder:
        if order_id in self.captures:
            return ProviderOrder(order_id, "COMPLETED", None, self.captures[order_id])
        status = "APPROVED" if purchase.mock_buyer_approved else "CREATED"
        return ProviderOrder(order_id, status, None, {
            "purchase_units": [{"reference_id": purchase.id,
                                "amount": {"currency_code": purchase.currency,
                                           "value": f"{Decimal(purchase.total_cents) / Decimal(100):.2f}"}}]})

    async def capture(self, order_id: str, request_id: str, purchase) -> ProviderOrder:
        raw = {
            "purchase_units": [{"reference_id": purchase.id,
                                "payments": {"captures": [{"id": f"MOCK-CAP-{purchase.id}",
                                    "status": "COMPLETED", "amount": {"currency_code": purchase.currency,
                                    "value": f"{Decimal(purchase.total_cents) / Decimal(100):.2f}"}}]}}]}
        self.captures[order_id] = raw
        return ProviderOrder(order_id, "COMPLETED", None, raw)
