
"""Counterexample: purchase integrity attack tests."""

from datetime import timedelta
from pathlib import Path
import os
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TOKEN = "counterexample-test-token"

os.environ["ASSEMBLY_DEMO_TOKEN"] = TOKEN
os.environ["ASSEMBLY_PAYMENT_MODE"] = "mock"
os.environ["ASSEMBLY_DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient

from app.domain import REPAIRED_EXAMPLE
from app.main import create_app
from app.store import Purchase, AuditEvent, utcnow


@pytest.fixture
def integrity_client(tmp_path: Path):
    app = create_app(
        database_url=f"sqlite:///{tmp_path / 'integrity.db'}",
        payment_mode="mock",
        demo_token=TOKEN,
    )
    with TestClient(app) as client:
        yield client


def auth():
    return {"X-Demo-Token": TOKEN}


def test_expired_purchase_cannot_be_approved(integrity_client):
    # Arrange: create a valid purchase.
    response = integrity_client.post(
        "/api/purchases",
        headers=auth(),
        json={
            "configuration": REPAIRED_EXAMPLE.model_dump(),
            "intent_key": "counterexample-expiry-attack",
        },
    )

    assert response.status_code == 200, response.text
    purchase_id = response.json()["id"]
    digest = response.json()["digest"]

    # Attack: move the purchase expiry into the past.
    with integrity_client.app.state.factory() as db:
        purchase = db.get(Purchase, purchase_id)
        assert purchase is not None
        purchase.expires_at = utcnow() - timedelta(minutes=1)
        db.commit()

    # Act: attempt approval using the original valid digest.
    approval = integrity_client.post(
        f"/api/purchases/{purchase_id}/approve",
        headers=auth(),
        json={"digest": digest},
    )

    # Assert: expiry check blocks approval.
    assert approval.status_code == 409
    assert "expired" in approval.json()["detail"].lower()

    # Verify no state transition or approval audit event occurred.
    with integrity_client.app.state.factory() as db:
        purchase = db.get(Purchase, purchase_id)
        assert purchase.status == "DRAFT"

        approval_events = (
            db.query(AuditEvent)
            .filter_by(
                purchase_id=purchase_id,
                event_type="terms_approved",
            )
            .count()
        )
        assert approval_events == 0
