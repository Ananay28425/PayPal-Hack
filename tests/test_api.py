import os
from pathlib import Path
import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock
from uuid import uuid4

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

os.environ.setdefault("ASSEMBLY_DEMO_TOKEN", "test-only-demo-token")
os.environ.setdefault("ASSEMBLY_PAYMENT_MODE", "mock")
os.environ.setdefault("ASSEMBLY_DATABASE_URL", "sqlite://")

from fastapi.testclient import TestClient
import pytest

from app.domain import BROKEN_EXAMPLE, CATALOGUE, REPAIRED_EXAMPLE, evaluate
from app.main import create_app
from app.paypal import MockPayPal, ProviderUncertain, SandboxPayPal


@pytest.fixture
def client(tmp_path: Path):
    app = create_app(database_url=f"sqlite:///{tmp_path / 'test.db'}", payment_mode="mock",
                     demo_token="test-only-demo-token")
    with TestClient(app) as test_client:
        yield test_client


def auth():
    return {"X-Demo-Token": "test-only-demo-token"}


def test_sponsor_status_and_evidence_boundaries(client, monkeypatch):
    from app import sponsors

    monkeypatch.delenv("CHANNEL3_API_KEY", raising=False)
    status = client.get("/api/sponsors").json()
    assert set(status) == {"AG Grid", "APIMatic", "Bryntum", "Channel3", "Postman"}
    endpoint = "/api/sponsors/evidence/channel3"
    assert client.post(endpoint).status_code == 401
    assert client.post(endpoint, headers=auth()).status_code == 503
    monkeypatch.setenv("CHANNEL3_API_KEY", "fixture-secret")

    async def search():
        return [{"id": "fixture-variant", "title": "Reference interface"}]

    monkeypatch.setattr(sponsors, "channel3", search)
    assert client.post(endpoint, headers=auth()).json()["result"][0]["id"] == "fixture-variant"
    assert client.post("/api/sponsors/evidence/unknown", headers=auth()).status_code == 404


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


def test_repair_preserves_budget_and_checkout_rejects_stale_proof(client):
    config = BROKEN_EXAMPLE.model_dump()
    response = client.post("/api/repair", json=config)
    assert response.status_code == 200
    result = response.json()
    assert result["original"]["ready"] is False
    assert result["check"]["ready"] is True
    assert result["proposal"]["requirements"] == config["requirements"]
    assert result["price_delta_cents"] == 20_000
    assert {item["product_id"]: (item["before"], item["after"]) for item in result["changes"]} == {
        "amp-4": (0, 1), "interface-2": (1, 0), "interface-8": (0, 1),
    }

    payload = {"configuration": result["proposal"], "intent_key": "reviewed-kit-01",
               "expected_digest": result["original"]["digest"]}
    assert client.post("/api/purchases", headers=auth(), json=payload).status_code == 409
    payload["expected_digest"] = result["check"]["digest"]
    prepared = client.post("/api/purchases", headers=auth(), json=payload)
    assert prepared.status_code == 200
    assert prepared.json()["digest"] == result["check"]["digest"]
    assert prepared.json()["status"] == "DRAFT"

    config["requirements"]["budget_cents"] = 75_000
    blocked = client.post("/api/repair", json=config).json()
    assert blocked["proposal"] is None
    assert blocked["reason"] == "no_compatible_kit"


def test_changed_specs_invalidate_proof_even_with_same_total(client, monkeypatch):
    config = REPAIRED_EXAMPLE.model_dump()
    checked = client.post("/api/check", json=config).json()
    monkeypatch.setitem(CATALOGUE["interface-8"], "mic_inputs", 6)
    revised = client.post("/api/check", json=config).json()
    assert revised["ready"] and revised["total_cents"] == checked["total_cents"]
    assert revised["digest"] != checked["digest"]
    response = client.post("/api/purchases", headers=auth(), json={
        "configuration": config, "intent_key": "changed-facts", "expected_digest": checked["digest"],
    })
    assert response.status_code == 409


def test_itemized_sandbox_order_accepts_payer_action_required(tmp_path, monkeypatch):
    provider = SandboxPayPal("fixture-client-id", "fixture-client-secret")
    calls = []

    async def provider_request(method, path, *, request_id=None, body=None):
        calls.append((method, path, request_id, body))
        return {
            "id": "ORD-FIXTURE-1",
            "status": "PAYER_ACTION_REQUIRED",
            "links": [{"rel": "payer-action", "href": "https://www.sandbox.paypal.com/checkoutnow?token=ORD-FIXTURE-1"}],
        }

    monkeypatch.setattr(provider, "_request", provider_request)
    app = create_app(database_url=f"sqlite:///{tmp_path / 'sandbox-contract.db'}",
                     payment_mode="sandbox", demo_token="test-only-demo-token", provider=provider)
    with TestClient(app) as client:
        purchase = prepared(client)
        response = client.post(f"/api/purchases/{purchase['id']}/approve", headers=auth(),
                               json={"digest": purchase["digest"]})
    assert response.status_code == 200
    assert response.json()["status"] == "AWAITING_BUYER"
    [(method, path, request_id, payload)] = calls
    assert (method, path) == ("POST", "/v2/checkout/orders")
    assert len(request_id) == 36
    [unit] = payload["purchase_units"]
    assert unit["custom_id"] == purchase["digest"]
    assert unit["reference_id"] == purchase["id"]
    assert unit["amount"]["breakdown"]["item_total"] == {"value": "810.00", "currency_code": "USD"}
    assert {item["sku"]: item["quantity"] for item in unit["items"]} == {
        "mic-xlr": "4", "headphones": "4", "interface-8": "1", "amp-4": "1",
    }


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


@pytest.mark.skipif(not os.getenv("ASSEMBLY_TEST_POSTGRES_URL"),
                    reason="requires an isolated PostgreSQL test database")
def test_two_api_instances_dispatch_one_capture():
    class RacingProvider(MockPayPal):
        def __init__(self):
            super().__init__()
            self.preflight = Barrier(2)
            self.lock = Lock()
            self.calls = 0

        async def get_order(self, order_id, purchase):
            order = await super().get_order(order_id, purchase)
            await asyncio.to_thread(self.preflight.wait, 10)
            return order

        async def capture(self, order_id, request_id, purchase):
            with self.lock:
                self.calls += 1
            return await super().capture(order_id, request_id, purchase)

    provider = RacingProvider()
    settings = {"database_url": os.environ["ASSEMBLY_TEST_POSTGRES_URL"], "payment_mode": "mock",
                "demo_token": "test-only-demo-token", "provider": provider}
    with TestClient(create_app(**settings)) as first, TestClient(create_app(**settings)) as second:
        purchase = prepared(first, key=f"postgres-race-{uuid4()}")
        url = f"/api/purchases/{purchase['id']}"
        assert first.post(f"{url}/approve", headers=auth(), json={"digest": purchase["digest"]}).status_code == 200
        assert first.post(f"{url}/mock-buyer-approve", headers=auth()).status_code == 200
        with ThreadPoolExecutor(max_workers=2) as pool:
            attempts = [pool.submit(client.post, f"{url}/capture", headers=auth()) for client in (first, second)]
            assert sorted(attempt.result(timeout=20).status_code for attempt in attempts) == [200, 409]
        captured = second.get(url, headers=auth()).json()
        assert captured["status"] == "CAPTURED"
        assert provider.calls == 1
        assert first.post(f"{url}/capture", headers=auth()).json()["provider_capture_id"] == captured["provider_capture_id"]


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
