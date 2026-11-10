"""Narrow PayPal Orders v2 adapter. No production endpoint is accepted."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, DecimalException
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


def purchase_unit(purchase) -> dict:
    """Translate the stored offer into the one purchase unit sent to Orders v2."""
    def amount(cents: int) -> dict:
        return {"currency_code": purchase.currency, "value": f"{Decimal(cents) / 100:.2f}"}

    total = amount(purchase.total_cents)
    unit = {
        "reference_id": purchase.id,
        "amount": {**total, "breakdown": {"item_total": total}},
        "items": [
            {"name": line.get("name", line["product_id"]), "sku": line["product_id"],
             "quantity": str(line["quantity"]), "unit_amount": amount(line["unit_cents"])}
            for line in purchase.snapshot["lines"]
        ],
    }
    if "proof_version" in purchase.snapshot:
        unit["custom_id"] = purchase.snapshot_digest
    return unit


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
        if response.status_code >= 500 or response.status_code in {408, 429}:
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
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [purchase_unit(purchase)],
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


def _matching_unit(order: ProviderOrder, purchase) -> dict | None:
    if order.id != purchase.provider_order_id:
        return None
    units = order.raw.get("purchase_units")
    if not isinstance(units, list) or len(units) != 1:
        return None
    unit = units[0]
    if not isinstance(unit, dict) or unit.get("reference_id") != purchase.id:
        return None
    return unit


def _matches_amount(amount, currency: str, cents: int) -> bool:
    if not isinstance(amount, dict) or amount.get("currency_code") != currency:
        return False
    try:
        return Decimal(str(amount.get("value"))) * 100 == cents
    except (DecimalException, TypeError, ValueError):
        return False


def verified_order_amount(order: ProviderOrder, purchase) -> bool:
    unit = _matching_unit(order, purchase)
    if unit is None or not _matches_amount(unit.get("amount"), purchase.currency, purchase.total_cents):
        return False
    if "proof_version" not in purchase.snapshot:
        return True
    items = unit.get("items")
    expected = {line["product_id"]: line for line in purchase.snapshot["lines"]}
    if unit.get("custom_id") != purchase.snapshot_digest or not isinstance(items, list) or len(items) != len(expected):
        return False
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("sku"), str):
            return False
        line = expected.pop(item["sku"], None)
        if (line is None or item.get("name") != line["name"] or str(item.get("quantity")) != str(line["quantity"])
                or not _matches_amount(item.get("unit_amount"), purchase.currency, line["unit_cents"])):
            return False
    return True


def verified_capture(order: ProviderOrder, purchase) -> str | None:
    """Recognize one matching completed capture for the original order."""
    unit = _matching_unit(order, purchase)
    if unit is None or order.status != "COMPLETED":
        return None
    payments = unit.get("payments")
    captures = payments.get("captures") if isinstance(payments, dict) else None
    if not isinstance(captures, list) or len(captures) != 1:
        return None
    capture = captures[0]
    if not isinstance(capture, dict) or capture.get("status") != "COMPLETED":
        return None
    if not _matches_amount(capture.get("amount"), purchase.currency, purchase.total_cents):
        return None
    if "proof_version" in purchase.snapshot:
        # Capture responses may omit custom_id. The pre-capture Order read
        # requires it. Reject any conflicting reference returned afterwards.
        if any("custom_id" in part and part["custom_id"] != purchase.snapshot_digest
               for part in (unit, capture)):
            return None
    capture_id = capture.get("id")
    return capture_id if isinstance(capture_id, str) and capture_id else None


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
        return ProviderOrder(order_id, status, None, {"purchase_units": [purchase_unit(purchase)]})

    async def capture(self, order_id: str, request_id: str, purchase) -> ProviderOrder:
        raw = {
            "purchase_units": [{"reference_id": purchase.id,
                                "payments": {"captures": [{"id": f"MOCK-CAP-{purchase.id}",
                                    "status": "COMPLETED", "amount": {"currency_code": purchase.currency,
                                    "value": f"{Decimal(purchase.total_cents) / Decimal(100):.2f}"}}]}}]}
        self.captures[order_id] = raw
        return ProviderOrder(order_id, "COMPLETED", None, raw)
