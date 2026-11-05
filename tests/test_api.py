import os
from pathlib import Path
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

os.environ.setdefault("ASSEMBLY_DEMO_TOKEN", "test-only-demo-token")
os.environ.setdefault("ASSEMBLY_PAYMENT_MODE", "mock")
os.environ.setdefault("ASSEMBLY_DATABASE_URL", "sqlite://")

from fastapi.testclient import TestClient
import pytest

from app.domain import REPAIRED_EXAMPLE, evaluate
from app.main import create_app
from app.paypal import MockPayPal, ProviderUncertain


@pytest.fixture
def client(tmp_path: Path):
    app = create_app(database_url=f"sqlite:///{tmp_path / 'test.db'}", payment_mode="mock",
                     demo_token="test-only-demo-token")
    with TestClient(app) as test_client:
        yield test_client


def auth():
    return {"X-Demo-Token": "test-only-demo-token"}


def prepared(client: TestClient, key="business-intent-1"):
    response = client.post("/api/purchases", headers=auth(), json={
        "configuration": REPAIRED_EXAMPLE.model_dump(), "intent_key": key})
    assert response.status_code == 200, response.text
    return response.json()


def test_auth_and_approval_digest(client):
    assert client.get("/api/purchases").status_code == 401
    purchase = prepared(client)
    mismatch = client.post(f"/api/purchases/{purchase['id']}/approve", headers=auth(), json={"digest": "0" * 64})
    assert mismatch.status_code == 409
    assert client.get(f"/api/purchases/{purchase['id']}", headers=auth()).json()["status"] == "DRAFT"


def test_full_mock_payment_and_no_duplicate_capture(client):
    purchase = prepared(client)
    url = f"/api/purchases/{purchase['id']}"
    order = client.post(url + "/approve", headers=auth(), json={"digest": purchase["digest"]})
    assert order.status_code == 200
    assert order.json()["status"] == "AWAITING_BUYER"
    assert order.json()["mock_buyer_approved"] is False
    assert client.post(url + "/capture", headers=auth()).status_code == 409
    buyer_approval = client.post(url + "/mock-buyer-approve", headers=auth())
    assert buyer_approval.json()["mock_buyer_approved"] is True
    captured = client.post(url + "/capture", headers=auth())
    assert captured.status_code == 200
    assert captured.json()["status"] == "CAPTURED"
    assert captured.json()["provider_capture_id"].startswith("MOCK-CAP-")
    again = client.post(url + "/capture", headers=auth())
    assert again.json()["provider_capture_id"] == captured.json()["provider_capture_id"]
    events = client.get(url + "/audit", headers=auth()).json()
    assert [e["type"] for e in events].count("capture_verified") == 1


def test_business_intent_key_cannot_change_terms(client):
    first = prepared(client)
    assert prepared(client)["id"] == first["id"]
    changed = REPAIRED_EXAMPLE.model_copy(deep=True)
    changed.requirements.budget_cents += 100
    response = client.post("/api/purchases", headers=auth(), json={
        "configuration": changed.model_dump(), "intent_key": "business-intent-1"})
    assert response.status_code == 409


class LostCaptureResponse(MockPayPal):
    def __init__(self):
        super().__init__()
        self.calls = 0

    async def capture(self, order_id, request_id, purchase):
        self.calls += 1
        await super().capture(order_id, request_id, purchase)
        raise ProviderUncertain("simulated lost response after capture")


def test_ambiguous_capture_reconciles_original_without_repeat(tmp_path):
    provider = LostCaptureResponse()
    app = create_app(database_url=f"sqlite:///{tmp_path / 'uncertain.db'}", payment_mode="mock",
                     demo_token="test-only-demo-token", provider=provider)
    with TestClient(app) as client:
        purchase = prepared(client, "uncertain-intent")
        url = f"/api/purchases/{purchase['id']}"
        client.post(url + "/approve", headers=auth(), json={"digest": purchase["digest"]})
        client.post(url + "/mock-buyer-approve", headers=auth())
        ambiguous = client.post(url + "/capture", headers=auth())
        assert ambiguous.status_code == 202
        assert ambiguous.json()["status"] == "CAPTURE_UNKNOWN"
        assert client.post(url + "/capture", headers=auth()).status_code == 409
        assert provider.calls == 1
        resolved = client.post(url + "/reconcile", headers=auth())
        assert resolved.status_code == 200
        assert resolved.json()["status"] == "CAPTURED"
        assert provider.calls == 1


def test_worker_reconciles_lost_capture_response(tmp_path):
    import asyncio
    from app.worker import reconcile_once

    provider = LostCaptureResponse()
    app = create_app(database_url=f"sqlite:///{tmp_path / 'worker.db'}", payment_mode="mock",
                     demo_token="test-only-demo-token", provider=provider)
    with TestClient(app) as client:
        purchase = prepared(client, "worker-intent")
        url = f"/api/purchases/{purchase['id']}"
        client.post(url + "/approve", headers=auth(), json={"digest": purchase["digest"]})
        client.post(url + "/mock-buyer-approve", headers=auth())
        assert client.post(url + "/capture", headers=auth()).status_code == 202
        result = asyncio.run(reconcile_once(app.state.factory, provider, payment_mode="mock"))
        assert result == {"inspected": 1, "resolved": 1, "unresolved": 0}
        assert client.get(url, headers=auth()).json()["status"] == "CAPTURED"
        assert provider.calls == 1


def test_failed_configuration_cannot_be_purchased(client):
    from app.domain import BROKEN_EXAMPLE
    response = client.post("/api/purchases", headers=auth(), json={
        "configuration": BROKEN_EXAMPLE.model_dump(), "intent_key": "flawed-intent"})
    assert response.status_code == 409
    assert any(x["code"] == "input_capacity" and x["status"] == "fail" for x in response.json()["detail"]["checks"])


def test_static_application_served(client):
    page = client.get("/")
    assert page.status_code == 200
    assert "Assembly Proof" in page.text
    assert client.get("/app.js").status_code == 200


def test_ai_proposal_never_creates_or_approves_purchase(client, monkeypatch):
    from types import SimpleNamespace
    import openai
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-key")

    class FakeResponses:
        async def create(self, **kwargs):
            assert "Never infer payment permission" in kwargs["instructions"]
            return SimpleNamespace(output_text='{"people":4,"budget_usd":1000,"needs_confirmation":false}')

    class FakeClient:
        def __init__(self, **kwargs):
            self.responses = FakeResponses()

    monkeypatch.setattr(openai, "AsyncOpenAI", FakeClient)
    result = client.post("/api/interpret", headers=auth(), json={
        "text": "Four-person recording kit under one thousand US dollars"})
    assert result.status_code == 200
    assert result.json()["proposal"]["people"] == 4
    assert result.json()["source"] == "ai_proposal"
    assert client.get("/api/purchases", headers=auth()).json() == []


def test_ai_catalogue_plan_is_checked_without_creating_purchase(client, monkeypatch):
    from types import SimpleNamespace
    import json
    import openai

    monkeypatch.setenv("OPENAI_API_KEY", "test-only-key")

    class FakeResponses:
        async def create(self, **kwargs):
            assert "Never infer authorization" in kwargs["instructions"]
            assert kwargs["text"]["format"]["strict"] is True
            return SimpleNamespace(output_text=json.dumps({
                "people": 4, "budget_usd": 1000, "needs_confirmation": False,
                "selections": REPAIRED_EXAMPLE.model_dump()["selections"],
            }))

    class FakeClient:
        def __init__(self, **kwargs):
            self.responses = FakeResponses()

    monkeypatch.setattr(openai, "AsyncOpenAI", FakeClient)
    response = client.post("/api/plan", headers=auth(), json={
        "text": "Build a four-person podcast kit under one thousand dollars"})
    assert response.status_code == 200, response.text
    assert response.json()["check"]["ready"] is True
    assert response.json()["proposal"] == REPAIRED_EXAMPLE.model_dump()
    assert client.get("/api/purchases", headers=auth()).json() == []


def test_ai_catalogue_plan_rejects_unknown_product(client, monkeypatch):
    from types import SimpleNamespace
    import openai

    monkeypatch.setenv("OPENAI_API_KEY", "test-only-key")

    class FakeResponses:
        async def create(self, **kwargs):
            return SimpleNamespace(output_text=(
                '{"people":4,"budget_usd":1000,"needs_confirmation":false,'
                '"selections":[{"product_id":"not-in-catalogue","quantity":1}]}'
            ))

    class FakeClient:
        def __init__(self, **kwargs):
            self.responses = FakeResponses()

    monkeypatch.setattr(openai, "AsyncOpenAI", FakeClient)
    response = client.post("/api/plan", headers=auth(), json={
        "text": "Build a four-person podcast kit under one thousand dollars"})
    assert response.status_code == 503
    assert client.get("/api/purchases", headers=auth()).json() == []
