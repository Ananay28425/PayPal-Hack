# Assembly Proof

Assembly Proof is a bounded agentic-commerce prototype for a complete four-person recording setup. When configured, AI proposes catalogue items from a natural-language goal. A separate deterministic checker exposes incompatible components, and PayGuard binds the exact accepted kit to a PayPal Sandbox order. Counterexample is a small visible fixture lab plus the fault and regression test suite.

This repository now contains a working **local MVP**, not a production payment platform. Its catalogue and prices are invented fixtures for an owned demo merchant. Mock checkout proves application flow without PayPal. Sandbox checkout uses the real PayPal Orders v2 API when merchant test credentials are supplied.

## Run locally

Python 3.12+ is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
$env:ASSEMBLY_DEMO_TOKEN='choose-a-long-random-token'
$env:ASSEMBLY_PAYMENT_MODE='mock'
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. Enter the same demo token in the UI. Load **flawed kit**, run check, then load **repaired kit** and run check. Prepare purchase, approve exact terms, approve as mock buyer, and capture. The audit trail records each transition. A new purchase starts from the button in the payment panel.

Linux/macOS: activate `.venv/bin/activate`, use `export` for environment variables, and run the same Uvicorn command.

## Use PayPal Sandbox

Create a sandbox REST app and a sandbox buyer account in the [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/). Set `ASSEMBLY_PAYMENT_MODE=sandbox`, `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, and `ASSEMBLY_PUBLIC_URL` to the actual public HTTPS origin. Restart the server. The UI provides the PayPal approval URL after internal approval. Return to the application and select **Capture and verify**. A browser return alone is never treated as a captured payment.

```powershell
$env:ASSEMBLY_PAYMENT_MODE='sandbox'
$env:PAYPAL_CLIENT_ID='your-sandbox-client-id'
$env:PAYPAL_CLIENT_SECRET='your-sandbox-secret'
$env:ASSEMBLY_PUBLIC_URL='https://your-public-demo.example'
```

The sandbox adapter has **not** yet been exercised with this team's credentials. Its create, read, and capture calls follow the [Orders v2 API](https://developer.paypal.com/api/orders/v2) and [idempotency guidance](https://developer.paypal.com/api/rest/reference/idempotency). Test it with owned sandbox accounts before any public demo. If a provider response is ambiguous, the original operation remains unresolved; reconciliation reads the original order. The app never creates a replacement capture automatically.

For a hosted sandbox demo, `render.yaml` defines a web service and a bounded reconciliation worker. It expects an external managed PostgreSQL URL using SQLAlchemy's `postgresql+psycopg://` scheme. Populate each unsynced environment variable in Render, including the exact HTTPS `ASSEMBLY_PUBLIC_URL`. This blueprint has not been deployed or validated against a Render account. It does not provision the synchronous Multi-AZ database from Architecture A.

## Enable AI

Set `OPENAI_API_KEY` on the server and restart it. **Ask AI to propose a kit** calls `/api/plan`: a bounded planner extracts people and budget, selects items only from the invented merchant catalogue, and returns a proposed configuration. The server validates the product IDs and quantities, then runs the deterministic checker before showing the result. The buyer can review and edit every field and item. AI cannot authorize spending, certify compatibility, create or capture an order, or declare payment success. The existing `/api/interpret` endpoint remains available for requirements-only clients. Without a key, the AI button is disabled and the manual presets and payment simulation remain usable; that mode does not demonstrate an AI call.

## Tests

```powershell
python -m pytest tests -q
```

The suite covers capacity errors, unknown facts, connector and budget conflicts, bounded AI catalogue proposals, digest stability, approval mismatch, intent-key conflict, buyer approval, exact mock capture, duplicate capture, and a simulated lost response after capture. The latter reconciles the original captured order without issuing a second capture. On restricted Windows sandboxes, Python's event-loop socketpair can be blocked; run tests in a normal terminal.

The local browser flow has also been exercised: flawed kit reports input and headphone failures; repaired kit passes at $810; mock approval and capture reach `CAPTURED` with an audit trail. This is evidence for the simulated path only.

## Architecture and boundaries

The app is one FastAPI process, one SQL database, a static web client, and an optional bounded reconciliation worker. In Sandbox mode, run the worker in a second process with `python -m app.worker`. It reads the original PayPal order for unresolved captures; it never issues another capture. SQLite is for local demo. `ASSEMBLY_DATABASE_URL` also accepts a SQLAlchemy PostgreSQL URL with `psycopg`; production transaction behavior, migrations, managed failover, full dispatch/outbox processing, auth, webhook ingestion, and load limits remain to be built and tested. The detailed [Architecture A](output/architecture/final-overall-designs/FINAL-DESIGN.md) is the target. Architecture B is a later scale design.

Every purchase freezes an exact merchant, configuration, price, currency, and expiry under a SHA-256 digest. Internal approval creates a durable PayPal order operation. Buyer approval is checked from PayPal before capture. The capture operation is committed before the external call. Capture success requires matching order, purchase reference, amount, currency, and completed capture. Timeouts keep the original operation unresolved. The app stores no customer money or payment credentials.

Security limits: the shared demo token is not user authentication, tenant isolation, or authorization for a public financial product. The demo merchant catalogue is synthetic. This version uses no stock reservation or fulfillment, no verified webhooks, no key rotation, and no real merchant onboarding. Do not deploy it as a production payment service.

## Sponsor status

The project requirement is meaningful use of all ten sponsors. Current implementation has a Render-ready container and executable Postman collection. The remaining sponsor roles are mapped in [SPONSORS.md](SPONSORS.md). They are **not implemented**. We will not count configuration stubs or logos as completed integrations. The PayPal Sandbox and AI flows also require credentials before an end-to-end live claim.
