# Assembly Proof

Assembly Proof checks whether a proposed shopping cart can deliver the outcome a buyer asked for. A four-person recording kit can include four microphones and still fail if the interface has only two inputs. Assembly Proof explains the mismatch, compares repairs within budget, and binds the buyer's approval to the exact items and price sent to PayPal Sandbox.

The recording demo uses invented merchant data. Custom kits use facts entered by the buyer. Channel3 displays live reference products and merchant offers in a separate discovery panel. The local prototype supports simulated payments and PayPal Sandbox test orders.

[Run locally](#run-locally) · [Demo walkthrough](#demo-walkthrough) · [Architecture](#system-architecture) · [API](#api-reference) · [Tests](#verification) · [Sponsor tools](#sponsor-tools)

## Run locally

Use Python 3.12+ and Node.js 22, the versions used by CI. From the repository root in PowerShell:

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
npm ci --ignore-scripts
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
~~~

Set a unique demo token of at least 12 characters in the local configuration file. Start with mock mode and launch the server:

~~~powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
~~~

Open [Assembly Proof](http://127.0.0.1:8010/#workspace). On Linux or macOS, activate the virtual environment with `source .venv/bin/activate`, copy the example only if you have no local file, and use the same Uvicorn command.

The web server and the reconciliation worker load the repository root `.env` at startup. Existing environment variables take precedence. Restart the process after editing the file, and use a fresh terminal if it still contains values from a previous run. The browser receives configuration status through the API. Provider credentials stay on the server. The local file is ignored by Git and excluded from Docker builds.

| Setting | Purpose |
| --- | --- |
| `ASSEMBLY_DEMO_TOKEN` | Shared access token for protected demo actions. Enter the same value in the app. |
| `ASSEMBLY_PAYMENT_MODE` | `mock` for local payment simulation or `sandbox` for PayPal test orders. |
| `ASSEMBLY_DATABASE_URL` | SQLAlchemy database URL. Use SQLite for the local demo and a separate database when switching between mock and Sandbox. |
| `ASSEMBLY_PUBLIC_URL` | Browser origin used for PayPal return and cancel links. Enter a plain URL that matches the server address, such as `http://127.0.0.1:8010`. |
| `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET` | Sandbox merchant REST app credentials for the server. |
| `OPENROUTER_API_KEY`, `ASSEMBLY_OPENROUTER_MODEL` | Optional AI provider key and model. The example pins `baidu/ernie-5.5-flash-preview:free`. The app accepts OpenRouter's free router or a `:free` variant. |
| `OPENAI_API_KEY`, `ASSEMBLY_AI_MODEL` | Optional direct OpenAI path when OpenRouter is absent. Leave the direct OpenAI key unset for an OpenRouter-only demo. |
| `CHANNEL3_API_KEY` | Enables live reference product discovery. |
| `ASSEMBLY_RECONCILE_SECONDS` | Optional Sandbox worker polling interval. Defaults to 15 seconds. |

### PayPal Sandbox setup

1. In the [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/), select **Sandbox → Apps & Credentials** and open or create a Merchant REST app. Put its client ID and secret into the local file.
2. Under **Testing Tools → Sandbox Accounts**, open a **Personal** buyer account and use **View/Edit Account** to find its test email and password. The buyer signs in at PayPal Sandbox. The merchant app credentials stay in the server configuration.
3. Set `ASSEMBLY_PAYMENT_MODE=sandbox`, choose a separate database such as `sqlite:///./assembly-sandbox.db`, set the callback origin, and restart. Check that the app header says **PayPal Sandbox**. The [health endpoint](http://127.0.0.1:8010/api/health) reports payment mode and whether AI is configured.
4. For a hosted demo, use the actual HTTPS origin. Run the optional worker against the same database and Sandbox account as the web process.

For setup details, see [PayPal Sandbox accounts](https://developer.paypal.com/sandbox-testing/accounts) and [Orders v2](https://developer.paypal.com/api/orders/v2/).

## Demo walkthrough

1. **Ask AI for a kit.** Enter the demo token and ask for a four-person podcast setup with four XLR microphones and headphones under $1,000. The planner proposes items from the fixture catalogue and the rule checker reports whether they fit. If AI is unavailable, the manual example still works.
2. **Show a predictable failure.** Select **Check flawed example**. The $610 cart has two microphone inputs and insufficient headphone outputs for four people.
3. **Compare and apply the repair.** Select **Find compatible repair** and open **Compare checked alternatives**. Inspect a blocked row, then choose **Apply and recheck kit**. The $810 repair uses an eight-input interface and a four-output headphone amplifier.
4. **Approve the purchase.** Select **Prepare purchase**, review the frozen items and total, then select **Approve exact terms**. In Sandbox mode, open the PayPal approval link and sign in as the test buyer. In mock mode, select **Approve as mock buyer**.
5. **Verify the outcome.** Back in Assembly Proof, select **Capture and verify**. Show the verified amount, capture ID, and audit trail. If the outcome is uncertain, select **Reconcile outcome**. Once captured, select **Start new purchase** to begin another checkout.

For a custom example, select **Custom kit**, set a $150 budget, and request 12 workshop seats. Enter one bench at $40 with four seats per unit. The check reports four of 12 seats, and the quantity repair proposes three benches for $120. Custom inspection checks capacity and budget using the facts supplied by the buyer. Both modes use the same purchase and approval pipeline.

## System architecture

### Runtime components

~~~mermaid
flowchart LR
    Browser["Browser UI<br/>Recording or custom kit"]
    API["FastAPI<br/>Planning, checking, checkout and audit"]
    Rules["Deterministic rules<br/>Capacity, compatibility and budget"]
    AI["OpenRouter or OpenAI<br/>Structured proposals"]
    Discovery["Channel3<br/>Reference products and offers"]
    DB[("SQLAlchemy<br/>SQLite or PostgreSQL")]
    Provider["Payment adapter<br/>PayPal Sandbox Orders v2 or local mock"]
    Worker["Optional Sandbox reconciliation worker"]
    Config["Process environment<br/>and local configuration file"]

    Browser -->|Same-origin API| API
    API --> Rules
    API --> AI
    API --> Discovery
    API --> DB
    API --> Provider
    Browser -->|Buyer approval in Sandbox mode| Provider
    Config --> API
    Config --> Worker
    Worker --> DB
    Worker -->|Read original Sandbox order| Provider
~~~

The FastAPI server serves the static browser UI and assets from the same origin. AG Grid presents repair candidates and counterexample results. Bryntum Scheduler presents delivery and setup dates when its optional assets are available.

The AI provider returns structured output. The server validates quantities and product IDs, then evaluates the result using deterministic rules. Channel3 discovery is independent of that catalogue and cannot supply payable items or prices. The purchase service and PayPal adapter handle payment state.

### Sandbox checkout and reconciliation

~~~mermaid
sequenceDiagram
    actor Buyer
    participant App as Assembly Proof
    participant DB as SQL database
    participant PayPal as PayPal Sandbox

    Buyer->>App: Check kit and prepare purchase
    App->>App: Recheck exact configuration and digest
    App->>DB: Save frozen snapshot, total and expiry
    Buyer->>App: Approve exact digest
    App->>DB: Commit CREATE operation and request ID
    App->>PayPal: Create itemized order
    PayPal-->>App: Order ID and approval URL
    App-->>Buyer: PayPal Sandbox approval link
    Buyer->>PayPal: Sign in and approve
    PayPal-->>Buyer: Return to Assembly Proof
    Buyer->>App: Capture and verify
    App->>PayPal: Read original order
    PayPal-->>App: Approval status and order terms
    App->>App: Verify approval and match frozen terms
    App->>DB: Commit CAPTURE operation and request ID
    App->>PayPal: Capture original order
    alt Completed capture matches
        PayPal-->>App: Capture ID and amount
        App->>DB: Mark CAPTURED and record audit event
        App-->>Buyer: Verified result
    else Timeout or outcome cannot be verified
        App->>DB: Keep CAPTURE_UNKNOWN
        Buyer->>App: Reconcile outcome
        App->>PayPal: Read original order again
        App->>DB: Confirm only if a matching capture is found
    end
~~~

The buyer approves twice for different purposes. **Approve exact terms** authorizes the app to create an order from the frozen snapshot. PayPal then records the buyer`s approval of that order. The return URL only brings the browser back. The server reads PayPal`s order before capture and verifies the resulting capture against the stored purchase.

### Purchase lifecycle

~~~mermaid
stateDiagram-v2
    [*] --> DRAFT: Prepare passing kit
    DRAFT --> ORDER_PENDING: Approve matching digest
    ORDER_PENDING --> AWAITING_BUYER: Order and approval URL confirmed
    ORDER_PENDING --> ORDER_UNKNOWN: Create outcome uncertain
    ORDER_PENDING --> REJECTED: Create rejected
    AWAITING_BUYER --> CAPTURE_UNKNOWN: Capture operation committed
    CAPTURE_UNKNOWN --> CAPTURED: Matching response or reconciliation
    CAPTURE_UNKNOWN --> CAPTURE_UNKNOWN: Verification incomplete
    CAPTURED --> [*]
~~~

An uncertain create without a PayPal order ID needs manual review. An uncertain capture keeps the original operation for reconciliation. Capture replays on a completed purchase return the recorded result. A new purchase is a separate record with its own approved terms.

### Storage model

~~~mermaid
erDiagram
    PURCHASE ||--o{ PAYMENT_OPERATION : records
    PURCHASE ||--o{ AUDIT_EVENT : records
    PURCHASE {
        string id PK
        string actor_id
        string intent_key
        json snapshot
        string snapshot_digest
        int total_cents
        string currency
        string status
        datetime expires_at
        string provider_order_id
        string provider_capture_id
    }
    PAYMENT_OPERATION {
        string id PK
        string purchase_id FK
        string kind
        string request_id UK
        string body_digest
        string state
    }
    AUDIT_EVENT {
        int id PK
        string purchase_id FK
        string event_type
        json data
        datetime created_at
    }
~~~

The snapshot freezes the merchant, line items, quantities, unit prices, currency, configuration facts, and rules version. A SHA-256 digest ties the snapshot to the buyer's approval. The database enforces a unique purchase intent per demo actor and one operation of each kind per purchase. Operation records are committed before dispatch to PayPal. Audit records show when the app approved, dispatched, verified, or reconciled an action.

## API reference

Interactive API documentation is available at [localhost:8010/docs](http://127.0.0.1:8010/docs) while the server is running. Protected endpoints accept the configured token in the `X-Demo-Token` header.

| Area | Endpoints |
| --- | --- |
| Configuration | `GET /api/health`, `GET /api/catalogue`, `GET /api/examples` |
| AI planning | `POST /api/plan`, `POST /api/interpret` |
| Checks and repair | `POST /api/check`, `POST /api/repair` |
| Discovery and sponsor evidence | `GET /api/products/search?q=…`, `GET /api/sponsors`, `POST /api/sponsors/evidence/channel3` |
| Purchase preparation and audit | `POST /api/purchases`, `GET /api/purchases/{id}`, `GET /api/purchases/{id}/audit` |
| Purchase actions | `POST /api/purchases/{id}/approve`, `/mock-buyer-approve`, `/capture`, `/reconcile` |
| Counterexamples | `GET /api/counterexamples`, `GET /api/counterexamples/all` |

## Repository map

| Path | Responsibility |
| --- | --- |
| [app/main.py](app/main.py), [app/\_\_init\_\_.py](app/__init__.py) | HTTP routes, integration boundaries, and configuration loading |
| [app/domain.py](app/domain.py) | Catalogue, configuration models, checks, repair search, and snapshot digest |
| [app/paypal.py](app/paypal.py), [app/worker.py](app/worker.py) | PayPal and mock adapters, outcome verification, and the separate Sandbox reconciliation process |
| [app/store.py](app/store.py) | Purchase, operation, and audit persistence |
| [app/sponsors.py](app/sponsors.py), [web/](web/) | Channel3 search and the browser experience |
| [app/counterexample_runner.py](app/counterexample_runner.py), [tests/](tests/) | Demo counterexamples and regression tests |
| [postman/](postman/), [src/spec/](src/spec/) | Postman collections and the API definition used by the APIMatic project |
| [Dockerfile](Dockerfile), [CI workflow](.github/workflows/ci.yml) | Container packaging and automated checks |

The [architecture design pack](output/architecture/final-overall-designs/FINAL-DESIGN.md) documents the proposed deployment and scale designs. The diagrams above describe the current implementation.

## Verification

~~~powershell
python -m pytest tests -q
~~~

The suite exercises catalogue compatibility, custom capacity, unknown facts, budget limits, stale proofs, exact approval, provider response validation, and uncertain capture reconciliation. The browser's counterexample lab combines configuration and payment integrity fixtures. To run the optional two-instance capture race, set `ASSEMBLY_TEST_POSTGRES_URL` to a disposable PostgreSQL database URL using `postgresql+psycopg://`.

To exercise mock checkout over HTTP, run the checked-in Postman collection through Newman with the demo server already running in mock mode:

~~~powershell
$demoToken = [System.Net.NetworkCredential]::new('', (Read-Host 'Assembly demo token' -AsSecureString)).Password
npx --yes newman@6.2.1 run postman/Assembly-Proof-Mock.postman_collection.json --env-var "baseUrl=http://127.0.0.1:8010" --env-var "demoToken=$demoToken" --bail
~~~

CI runs the isolated Python suite and the mock Postman contract. Local checks have exercised OpenRouter planning, mock capture and replay, and PayPal Sandbox order creation. A live Sandbox capture requires buyer approval and a verified capture response. The health endpoint only reports configuration and does not call providers.

## Sponsor tools

| Tool | Role |
| --- | --- |
| **AG Grid** | Compare repairs and inspect configuration or payment integrity counterexamples. |
| **Bryntum Scheduler** | Visualize delivery, the setup buffer, and the target recording date. Install the optional trial assets using the [sponsor walkthrough](SPONSORS.md). |
| **Channel3** | Search live products and merchant offers for reference. Enable it with a server-side key. |
| **APIMatic** | PayPal API development context and API project assets. |
| **Postman** | Repeatable checkout, consent, stale terms, and capture replay checks in CI. |

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| The AI button is disabled | The health endpoint should report AI configured. Check the server configuration and restart from a fresh terminal. |
| PayPal Sandbox login rejects a regular PayPal account | Use the personal test buyer shown under **Sandbox Accounts** in the Developer Dashboard. |
| Checkout returns to the wrong page | Match the callback origin and port to the exact address in the browser. |
| Only **Start new purchase** is available | The displayed purchase is complete. Start a new purchase and run a passing check to enable preparation. |
| Channel3 search is unavailable | Confirm the configured key belongs to Channel3 and that the server was restarted after changing it. |
| Capture outcome is uncertain | Use **Reconcile outcome** to read the original order. Review the audit events before starting a separate purchase. |

## Deployment boundaries

For a local mock demo, run one process. Mock payment state is process-local. For a Sandbox deployment, run the container with environment variables injected by the host and a shared SQL database. If you want background reconciliation, start `python -m app.worker` as a second process with the same Sandbox credentials and database. The worker reads the original provider order and records matching completed captures.

The demo uses a shared token and one synthetic merchant. Public production use would require buyer identity and tenant isolation, merchant onboarding, stock and fulfillment integration, database migrations and recovery, operational limits, and a security review. PayPal handles the funds. Assembly Proof tracks approval, order, and capture state.
