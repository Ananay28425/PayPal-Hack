# Assembly Proof

Assembly Proof checks whether an agent's shopping cart will work as a complete setup before checkout. In the recording-kit demo, four microphones exceed a two-input interface's capacity. The checker explains the failure, computes a repair within the buyer's budget, and shows the exact changes. PayGuard binds the checked offer to buyer approval and an itemized PayPal Sandbox order. Counterexample exercises independently defined failures.

This repository now contains a working **local MVP**, not a production payment platform. Its catalogue and prices are invented fixtures for an owned demo merchant. Mock checkout proves application flow without PayPal. Sandbox checkout uses the real PayPal Orders v2 API when merchant test credentials are supplied.

## Run locally

Python 3.12+ is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
npm ci --ignore-scripts
$env:ASSEMBLY_DEMO_TOKEN='choose-a-long-random-token'
$env:ASSEMBLY_PAYMENT_MODE='mock'
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. Choose **Check flawed example**, then **Find compatible repair**. The $610 cart fails microphone and listening capacity. Open **Compare checked alternatives** and select a row to see why it passes or fails. Choose **Apply and recheck kit** to review the $810 repair. The npm step installs the AG Grid comparison. Without it, the same alternatives remain inspectable as buttons.

Enter the demo token, prepare the purchase, review the frozen items and total, approve exact terms, approve as mock buyer, and capture. The audit trail records each transition. Select **Start new purchase** to clear the active review.

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

For a hosted sandbox demo, `render.yaml` defines a web service and a bounded reconciliation worker. It expects an external managed PostgreSQL URL using SQLAlchemy's `postgresql+psycopg://` scheme. Populate each unsynced environment variable in Render, including the exact HTTPS `ASSEMBLY_PUBLIC_URL`. The container built and passed a local mock smoke test. Render account deployment and the managed database remain pending.

## Enable AI

Set `OPENAI_API_KEY` on the server and restart it. **Ask AI to propose a kit** calls `/api/plan`: a bounded planner extracts people and budget, selects items only from the invented merchant catalogue, and returns a proposed configuration. The server validates the product IDs and quantities, then runs the deterministic checker before showing the result. The buyer can review and edit every field and item. AI cannot authorize spending, certify compatibility, create or capture an order, or declare payment success. The existing `/api/interpret` endpoint remains available for requirements-only clients. Without a key, the AI button is disabled and the manual presets and payment simulation remain usable; that mode does not demonstrate an AI call.

## Tests

```powershell
python -m pytest tests -q
```

The suite covers capacity errors, unknown facts, connector and budget conflicts, a computed repair, stale proofs including same-price changes, the sandbox create response contract, exact mock capture, duplicate capture, and a simulated lost response after capture. The last case reconciles the original captured order. To exercise the two-instance capture race, set `ASSEMBLY_TEST_POSTGRES_URL` to a **disposable** PostgreSQL database URL using `postgresql+psycopg://`. On restricted Windows sandboxes, run Python network tests in a normal terminal.

With the local server in mock mode, run the Postman collection in Newman.

```powershell
npx --yes newman@6.2.1 run postman/Assembly-Proof-Mock.postman_collection.json --env-var "baseUrl=http://127.0.0.1:8000" --env-var "demoToken=$env:ASSEMBLY_DEMO_TOKEN" --bail
```

The browser check covered the failed kit, AG Grid evidence, computed repair, and the frozen buyer review. Newman covered all 12 mock requests and assertions, through capture and replay of the same capture ID. The sandbox adapter still needs a run with merchant test credentials.

## Architecture and boundaries

The app is one FastAPI process, one SQL database, a static web client, and an optional bounded reconciliation worker. In Sandbox mode, run the worker in a second process with `python -m app.worker`. It reads the original PayPal order for unresolved captures; it never issues another capture. SQLite is for local demo. `ASSEMBLY_DATABASE_URL` also accepts a SQLAlchemy PostgreSQL URL with `psycopg`; production transaction behavior, migrations, managed failover, full dispatch/outbox processing, auth, webhook ingestion, and load limits remain to be built and tested. The detailed [Architecture A](output/architecture/final-overall-designs/FINAL-DESIGN.md) is the target. Architecture B is a later scale design.

Every new purchase freezes the merchant, configuration, product facts, rules version, prices, and currency under a SHA-256 digest. The database enforces the separate offer expiry. Internal approval creates a durable PayPal order operation. Before capture the app checks buyer approval and compares the returned line items and terms digest. The capture operation is committed before the external call. Capture success requires a matching order, purchase reference, amount, currency, and completed capture. Timeouts keep the original operation unresolved. PayPal handles funds.

Security limits: the shared demo token is not user authentication, tenant isolation, or authorization for a public financial product. The demo merchant catalogue is synthetic. This version uses no stock reservation or fulfillment, no verified webhooks, no key rotation, and no real merchant onboarding. Do not deploy it as a production payment service.

## Sponsor status

See [the ten-sponsor implementation ledger](SPONSORS.md) for which tools ran, the pending integrations, and the evidence each must produce. See [the submission decision](research/submission-decision-2026-11-06.md) for the project comparison, judging evidence, merchant pilot, and production rollout gates.
