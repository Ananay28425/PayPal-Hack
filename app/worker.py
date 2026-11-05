"""Bounded reconciliation worker for ambiguous PayPal captures.

It never creates or repeats a capture. It reads the original provider order and
records a matching completed capture. Run as a separate service for Sandbox.
"""
from __future__ import annotations

import asyncio
import os
from sqlalchemy import select

from app.paypal import MockPayPal, ProviderRejected, ProviderUncertain, SandboxPayPal, verified_capture
from app.store import PaymentOperation, Purchase, make_session_factory, record


async def reconcile_once(factory, provider, *, payment_mode: str = "sandbox", limit: int = 10) -> dict:
    if limit < 1 or limit > 100:
        raise ValueError("Worker limit must be between 1 and 100")
    with factory() as db:
        ids = db.scalars(select(Purchase.id).where(Purchase.status == "CAPTURE_UNKNOWN",
            Purchase.provider_order_id.is_not(None)).order_by(Purchase.created_at).limit(limit)).all()
    result = {"inspected": 0, "resolved": 0, "unresolved": 0}
    for purchase_id in ids:
        with factory() as db:
            purchase = db.get(Purchase, purchase_id)
            if purchase is None or purchase.status != "CAPTURE_UNKNOWN" or not purchase.provider_order_id:
                continue
            db.expunge(purchase)
        result["inspected"] += 1
        try:
            order = await (provider.get_order(purchase.provider_order_id, purchase) if payment_mode == "mock"
                           else provider.get_order(purchase.provider_order_id))
        except (ProviderRejected, ProviderUncertain):
            result["unresolved"] += 1
            continue
        capture_id = verified_capture(order, purchase)
        if not capture_id:
            result["unresolved"] += 1
            continue
        with factory.begin() as db:
            current = db.get(Purchase, purchase_id, with_for_update=True)
            if current is None or current.status != "CAPTURE_UNKNOWN" or current.provider_order_id != purchase.provider_order_id:
                continue
            current.provider_capture_id = capture_id
            current.status = "CAPTURED"
            current.last_error = None
            operation = db.scalar(select(PaymentOperation).where(PaymentOperation.purchase_id == purchase_id,
                PaymentOperation.kind == "CAPTURE"))
            if operation:
                operation.state = "CONFIRMED"
            record(db, purchase_id, "capture_reconciled_by_worker", {"capture_id": capture_id})
            result["resolved"] += 1
    return result


async def main() -> None:
    mode = os.getenv("ASSEMBLY_PAYMENT_MODE", "sandbox")
    if mode != "sandbox":
        raise RuntimeError("Separate worker supports PayPal Sandbox only; mock provider state is process-local")
    factory = make_session_factory(os.getenv("ASSEMBLY_DATABASE_URL", "sqlite:///./assembly-demo.db"))
    provider = SandboxPayPal(os.getenv("PAYPAL_CLIENT_ID", ""), os.getenv("PAYPAL_CLIENT_SECRET", ""))
    interval = int(os.getenv("ASSEMBLY_RECONCILE_SECONDS", "15"))
    if interval < 5 or interval > 3600:
        raise ValueError("ASSEMBLY_RECONCILE_SECONDS must be between 5 and 3600")
    while True:
        result = await reconcile_once(factory, provider)
        print(f"reconciliation inspected={result['inspected']} resolved={result['resolved']} unresolved={result['unresolved']}", flush=True)
        await asyncio.sleep(interval)


if __name__ == "__main__":
    asyncio.run(main())
