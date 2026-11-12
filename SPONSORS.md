# Sponsor implementation ledger

Assembly Proof has one journey. A buyer describes a complete recording setup, compares evidence-backed repairs, approves the exact offer, and can opt into a setup reminder after verified payment. A tool counts when someone can reproduce what it contributed with the real tool. PayPal Sandbox is the required payment platform and sits outside the ten optional sponsors. [Official sponsor resources](https://paypalaihackathon.devpost.com/resources)

| Sponsor | Job and why it matters | Evidence and status |
|---|---|---|
| AG Grid | Sort checked repair candidates by total and select one to inspect its blocker. This explains why the $700 kit fails even though it is cheaper than the $810 repair. | **Exercised locally.** Community grid renders all three computed candidates and row selection reveals the exact rule. Open **Compare checked alternatives** after a repair search. |
| APIMatic | The PayPal Context Plugin's resilience and testing guidance informed a review of ambiguous provider responses. An HTTP 408 now enters reconciliation, and a transport test asserts that exactly one capture POST carries the stored request ID. | **Used in development.** Review the [v0.4.1 context](https://context.apimatic.io/plugins/paypal/), the Python [resilience](https://github.com/context-plugins/plugin-marketplace/blob/main/plugins/paypal/skills/python/python-configuration-resilience/SKILL.md) and [testing](https://github.com/context-plugins/plugin-marketplace/blob/main/plugins/paypal/skills/python/python-testing/SKILL.md) references, and [the regression](tests/test_paypal.py). |
| Astropods | Run the bounded planner that turns the buyer's goal into reviewable requirements and proposed catalogue selections. An execution trace makes a bad proposal diagnosable. | Planner adapter wired. Astropods deployment and trace verification pending. FastAPI validates the proposed data and runs the checker separately. |
| Bryntum | Show when the repaired kit can actually be used. One delivery or setup dependency should make a kit miss the buyer's required date and visibly change the readiness result. | Scheduler trial rendered locally. The advisory timeline compares delivery plus one setup day with the recording date. |
| Channel3 | Discover the exact product variant and retain its identity through candidate selection. A visually similar model can have a different input count. | Discovery wired. API key, live result, and merchant offer mapping pending. |
| Elastic | Retrieve the source passage for a critical attribute using the exact variant and document revision. The buyer can see why an input count was accepted or left unknown. | Exact variant and revision lookup wired. Provisioning and live index check pending. |
| Kernel | Inspect an approved manufacturer's source when a critical fact is missing. Save the URL, excerpt, timestamp, and variant for review before admitting the fact. | Fixed-source browser job wired. API key and live extraction check pending. Observations require review. |
| Postman | Exercise the checkout contract from incompatibility through replay. This gives judges a repeatable test of the behavior behind the video. | **Exercised locally.** Newman ran 12 requests and passed 12 assertions in mock mode, including a stale proof, approval mismatch, pre-approval capture, and replay of the same capture ID. |
| Render | Run the public judge URL and the worker that reconciles uncertain captures. The worker lets buyers leave the page while the original order is checked. | Blueprint present. **Container built and smoke-tested locally** for health, the grid asset, repair, and purchase preparation. Account deployment, public health, real AI call, and PayPal Sandbox smoke test pending. |
| Zapier | Create one opt-in setup reminder after a verified capture. The dependency on confirmed payment prevents reminders for abandoned or failed orders. | Opt-in Catch Hook dispatch wired with one attempt per purchase. Verify the downstream action in Zapier Task History before any manual retry. |

Channel3, Kernel, and Elastic feed evidence discovery. Astropods can propose a kit. AG Grid and Bryntum help the buyer inspect it. Those tools have zero payment permissions. PayGuard owns the SQL state transitions and PayPal adapter. Zapier runs downstream of a verified result. APIMatic and Postman are development and verification tools.

The catalogue today uses invented variants, prices, and capacities. An integration earns its place by changing a decision, resolving an unknown, or detecting a failure. Keep the resulting screenshots, trace IDs, or test outputs with the submission. Review sponsor terms and licensed component availability through judging before selecting a public demo setup.

## Running the sponsor panel

Open **Tools behind this purchase**. All ten rows distinguish installed assets, development evidence, configuration, and hosting. API actions use the existing demo access token. Provider settings belong on the server.

| Integration | Setup |
|---|---|
| Astropods | Deploy a FastAPI planner behind an authenticated Astropods HTTP endpoint. Set `ASTROPODS_PLANNER_URL` and `ASTROPODS_TOKEN`. The endpoint receives `{"text":"buyer goal"}` and returns the same `proposal` shape as Assembly's `POST /api/plan`. To reuse this app as the hosted planner, configure its own OpenAI key and mock mode, omit its Astropods settings, and pass its demo token as ASTROPODS_PLANNER_DEMO_TOKEN on the calling service. The hosted response goes through the local checker. |
| Bryntum | Install the optional trial package with `npm install --no-save --package-lock=false --ignore-scripts @bryntum/scheduler-trial@7.3.8`. Activate a trial if required. Enter delivery and recording dates to see the setup buffer and timeline. |
| Channel3 | Set `CHANNEL3_API_KEY`. Search for the reference interface. Discovery results are reference products. The checkout catalogue still uses synthetic merchant offers. |
| Elastic | Set `ELASTIC_URL` and a read-scoped `ELASTIC_API_KEY`. Create `assembly-evidence` with keyword fields `variant` and `revision`. Index a reviewed passage with `variant=scarlett-2i2-4th-gen`, `revision=manufacturer-reference-v1`, and the exact Focusrite `source` URL in `app/sponsors.py` plus an `excerpt` field. |
| Kernel | Set `KERNEL_API_KEY`. The browser reads one fixed manufacturer page and returns a session ID and excerpt for review. An empty excerpt leaves the specification unresolved. |
| Zapier | Set `ZAPIER_SETUP_HOOK` to a Catch Hook URL connected to the setup action. In Sandbox mode, explicitly send a verified captured purchase from the panel. A unique database operation prevents repeat dispatch. Verify the resulting task in Zapier Task History. |

These paths need live provider acceptance runs. A configured badge means the server has the required settings. It does not attest to credentials, a deployed planner, a successful action, or an authorized merchant offer.

## Submission audit

The local Community grid works. The sponsor's showcase asks for AG Studio capabilities such as custom widgets and its agent framework. Record Community grid usage separately from any Studio award claim. [AG Grid sponsor brief](https://paypalaihackathon.devpost.com/details/aggrid)

The [CI workflow](.github/workflows/ci.yml) installs the locked grid, checks that the app serves its bundle, and runs the Postman collection against a fresh mock service. APIMatic is development evidence. Render requires the same PostgreSQL URL and PayPal Sandbox account on both web and worker, the actual HTTPS origin on web, and a successful hosted smoke run.

Use these checks to finish external acceptance.

| Sponsor | Missing components | Acceptance run |
|---|---|---|
| Astropods | Deployed planner, authenticated endpoint and adapter, trace reference | One typed proposal appears in the UI and has a matching Astropods trace. |
| Bryntum | Licensed Scheduler or Gantt asset, delivery and setup inputs, deadline rule | A setup dependency moved past the deadline changes readiness. |
| Channel3 | API access, variant lookup, mapping to the authorized merchant's offer | Retrieve and identify a real variant and distinguish it from a similar SKU. |
| Elastic | Search service, variant and revision index, evidence retrieval adapter | Retrieve the approved source passage and reject the wrong revision. |
| Kernel | Browser API access, approved-source extraction job, review record | Produce a trace for an exact variant and keep an unresolved fact unknown. |
| Zapier | Connected action, buyer opt-in, durable delivery record and reconciliation | Run the opted-in action after verified capture and prove replay creates one remote task. |
