# PayPal AI Hackathon: opportunity decision notes

Research date: October 23, 2026. Audience: a two-person team seeking the overall first prize. Scope: product discovery and build selection, not implementation. PayGuard is a starting hypothesis, not the committed project. No award outcome can be guaranteed.

## Decision

Investigate **RecoverPlan**, a commerce recovery product that preserves a user's business goal after a multi-step AI purchase partially fails. Keep **ReservePilot**, an obligation-aware merchant cash planner, as the fallback. Give **ClearFX** a short access probe because real PayPal FX APIs exist, but onboarding may rule it out.

This recommendation is provisional. None of these has been validated with users or a working prototype. The ranking considers a two-person delivery window, observable PayPal actions, substantive AI work, public overlap, and the ability to explain the complete product in under three minutes. It does not establish that a competitor lacks a feature.

The broad idea bank contains 100 hypotheses across 25 domains. It is not possible to enumerate every future fintech idea or prove originality from public search. The project descriptions found during this pass are evidence of overlap, not verified claims of technical quality or proof that all are entered in this hackathon.

## Rules that control the strategy

- Submission deadline: **November 12, 2026 at 12:00 p.m. PST**, equivalent to **November 13 at 1:30 a.m. IST**. Plan to finish submission by November 11 IST. From October 23 there are about 20 build days, depending on the current hour.
- Required: meaningful PayPal developer platform use in the free sandbox environment, meaningful AI, a working build, a public open-source repository with a detectable license, a text description, and a public YouTube video under three minutes.
- Hosted deployment is optional if complete setup and run instructions let judges run the project. A static mockup is insufficient.
- Five criteria are equally weighted: technological implementation, design, potential impact, innovation/idea, presentation. Tie-breaking starts with implementation, then follows the listed criteria.
- New projects and significantly advanced existing projects qualify. Explain work completed during the submission period.
- Sponsor tools are optional. The rules include PayPal group services such as Braintree, Venmo, Xoom and Hyperwallet, but inclusion in the rules does not grant API access.
- The rules specify judging through December 15, 2026. Maintain the submitted working build and access through that period. Keep secrets on the server; provide a dedicated sandbox test experience or clear instructions rather than committing credentials.
- The overview displayed **18,716 participants** during this pass. That is a registration count, not completed submissions. There is no basis to treat the user's 30,000 forecast as a fact or derive win probability from registrations.
- The event's official project gallery is unpublished. Public project discovery used Devpost's broader PayPal technology gallery and individual project pages. The overview and rules also display some inconsistent prize labels/totals; the unambiguous overall first-prize amount is $12,000. Avoid building strategy around an ambiguous special-award label.

Sources: [rules](https://paypalaihackathon.devpost.com/rules), [overview](https://paypalaihackathon.devpost.com/), [resources](https://paypalaihackathon.devpost.com/resources), [unpublished event gallery](https://paypalaihackathon.devpost.com/project-gallery).

## Business facts and their limits

PayPal reported $1.337 billion of transaction losses for 2025 versus $1.114 billion in 2024, a 20.0% increase after rounding. Transaction losses include customer protection programs, fraud and chargebacks. This is not an amount wholly attributable to scams, AI agents, or a problem our product could eliminate. Source: [SEC segment report](https://www.sec.gov/Archives/edgar/data/1633917/000163391726000024/R133.htm).

PayPal documents reserves, unavailable funds and negative balances. These support investigating obligation-aware merchant cash decisions. They do not establish demand for our particular product or give us authority to alter PayPal's holds. Sources: [reserves](https://www.paypal.com/us/cshelp/article/what-are-reserves-help393), [negative balances](https://www.paypal.com/us/cshelp/article/what-should-i-do-if-my-balance-is-negative-help389).

PayPal's treasury interview describes FX pricing/trading activity for over 160 currency pairs, liquidity allocation, risk management and stablecoin exploration. That is a real connection between PayPal and quantitative financial infrastructure. It does not imply public access to PayPal's treasury, internal quotes or trading venues. Source: [July 2026 treasury interview](https://flow.db.com/case-studies/inside-paypal-s-treasury-transformation).

## Existing capabilities: avoid rediscovering them

| Capability | Existing evidence | Consequence |
| --- | --- | --- |
| AI access to payments and merchant operations | Agent Toolkit and MCP expose orders, refunds, invoices, subscriptions, disputes, tracking and reporting tools | A chat interface over tools is a baseline, not a novel product |
| Agent commerce acceptance | Agent Ready documents ACP through Braintree and UCP paths through Braintree or PayPal | Do not claim AI checkout is absent |
| Product discovery and agent distribution | Store Sync and agentic commerce services exist; access is requested through onboarding | Do not make gated access a critical assumption |
| Signed agent authority | PayPal supports AP2; mandates are signed records of intent | Signed budgets are not an original protocol invention |
| Retry protection | PayPal-Request-Id provides supported API idempotency with endpoint-specific retention | Duplicate prevention must build on this rather than claim to invent it |
| Webhook events | Signed verification and retries are documented | Webhooks require deduplication and reconciliation; delivery is not a new event bus invention |
| FX quoting | Currency Exchange v2 and FXaaS document quotes, fx_id and expiry | FX is a genuine candidate, but contract enablement is an access gate |
| Payment routing | Braintree payment orchestration includes PSP connectors and recovery capabilities | A generic smart payment router overlaps an existing PayPal product |
| Dispute automation | Braintree supports automated evidence collection/submission workflows; external vendors integrate PayPal | An evidence-drafting assistant needs an unusually strong, specific workflow |

Sources: S04-S06, S10, S12, S27-S28, S35, S37 in [source registry](sources.md).

## Closest public alternatives

| Initial direction | Public overlap found | Interpretation |
| --- | --- | --- |
| PayGuard payment firewall | Warden, AgentGuard IntentLock, Leash, Fizzl Guard, AGENT GATE | Very crowded concept space; different branding is insufficient |
| Signed mandate plus dispute evidence | Warrant and PayPal AP2 | Much of the supposed deeper idea already exists |
| AI work verification before capture | Rent-A-Bot, PayOnProof, multiple ProofPay projects, AgentEscrow | Reframe only around a defensible acceptance problem; avoid false escrow claims |
| Contract-to-cash | Clause-to-Cash, ScopePay, FairDeal AI, ScopeDiff | Existing prototypes already extract clauses and gate invoices or payments |
| Three-way invoice matching | Supplora Pay, InvoiceGate, Kassa | Need an improvement beyond invoice OCR and cash-cap planning |
| Payment evidence and recovery | Caseproof, ClearLedger AI, PaySentinel, AGENT GATE | A log explainer or safe retry demo alone is too close |
| Saga middleware | ACTC; Temporal Saga pattern | Do not present distributed compensation as a new invention |
| Agent security benchmark | BossAgent; academic protocol benchmarks | A trust-score dashboard is not an unexplored category |
| Concurrent budgets and inventory | ZeroRace and Stub | These are adjacent examples; ZeroRace is from another event and describes real payment-rail adapters as future work |
| Returns recovery | AutoRescue, Return Loop, Refund Desk | Need preference-aware and economically correct execution, not generic outreach |
| Machine service payments | Mastercard Agent Pay for Machines and x402; existing billing systems | PayPal integration can differentiate a workflow, but the category is established |

Public descriptions were read for overlap. Repositories, deployment behavior, performance results and security claims were not independently tested. In particular, words such as immutable, zero failures, escrow and exactly once in project descriptions should not be repeated as verified guarantees.

## Access and feasibility gates

| Integration | What documentation supports | Verify before commitment |
| --- | --- | --- |
| Orders and Payments | Create, approve, authorize/capture, read back; void unused authorization; refund captured payment | Test chosen account, currency and country configuration; use direct buyer approval initially |
| Authorization | Hold valid up to 29 days; recommended three-day honor period; capture still depends on risk and funds | Do not call an authorization escrow; avoid multi-capture assumptions without account enablement |
| Webhooks | Verify signatures, acknowledge durable receipt, process idempotently | Distinguish simulator messages from genuine sandbox events; duplicate local replays are not duplicate network deliveries |
| Transaction Search | Account reporting; transactions may take up to three hours to appear; third-party use requires partner status | Not a real-time ledger; read the specific order/capture/refund when resolving current execution |
| Invoicing | Merchant-owned invoice workflows | Creating an invoice does not prove payment, delivery or borrower eligibility |
| Payouts | Documented PayPal capability and sandbox workflow | Verify app/account permissions and supported country/recipient/currency combinations immediately; live enablement is separate |
| Subscriptions | Merchant subscriptions and buyer-consented revisions | Not universal consumer subscription administration |
| Disputes | Merchant response and evidence operations | Seed a real sandbox dispute workflow if possible; label synthetic case records if that cannot be done |
| Agent Ready / Store Sync | Current agentic commerce products | Published docs do not imply an enabled account; services require contact/onboarding |
| FXaaS | Currency Exchange quotes linked by fx_id into Orders; contract-dependent expiry behavior | Eligibility, contract and account enablement are required. Stop this track quickly if unavailable |
| PYUSD | Testnet tokens and blockchain development supported | Separate network/environment from REST sandbox; no assumed fiat-to-testnet bridge. Confirm hackathon acceptance of a pure testnet submission before relying on it |
| Braintree / multiparty / Hyperwallet / Xoom | In rules or product portfolio, with product-specific access | Do not assume a general retail money-transfer API or universal split settlement access |

No PayPal credentials were supplied and no API execution was performed. This is documented feasibility, not a successful integration test.

## Finalist 1: RecoverPlan

**User:** a small merchant or business using agents to buy an interdependent equipment or event bundle through connected, participating sellers.

**Job:** preserve the business goal when some purchases complete, other steps fail, and cancellation or refund is not immediate or free.

**Example:** an event organizer needs a compatible printer, labels and a scanner by Friday. The printer payment is completed but its response is lost. The label supplier fails. One alternative is cheaper but incompatible; another arrives late. A feasible replacement costs more. RecoverPlan reads trusted payment state, recognizes the existing printer commitment, compares recovery plans, and asks for approval when total cost, accepted loss, seller or deadline constraints change.

**AI work:** extract the user's business constraints; build a typed dependency graph; interpret supplied product compatibility and seller cancellation terms with citations; generate alternative recovery plans. This is substantive planning, not a generic payment-error explanation. Product text and seller messages are untrusted evidence, never authority.

**Deterministic work:** validate graph structure and approved constraints; compute costs; track commitments; reserve budget; enforce payment state transitions; verify evidence ownership and fresh approvals; execute allowlisted actions; reconcile actual results.

**PayPal work:** real sandbox order creation, buyer approval, authorization or capture, read-back, void/refund where permitted, verified webhooks. Start with one buyer and two controlled sandbox seller accounts or clearly label logical suppliers sharing one merchant. The app cannot force arbitrary independent merchants to refund.

**Minimum product:** one vertical, two or three dependent purchases, a small catalogue, one bounded agent planner, one incident/recovery workspace, explicit action approval, a durable state machine, an audit trail and a resettable demo.

**Difference to validate:** ACTC handles cross-protocol transaction state and compensation. RecoverPlan must demonstrate preserving a multi-purchase business goal under compatibility, deadline, pending-refund and irreversible-cost constraints. It is not enough to add a language model to ACTC. Novelty remains a hypothesis until this distinction survives user and competitor review.

**Three-minute story:** show the user's goal, a live sandbox purchase, an injected failure at the application boundary, alternative recovery plans, rejection of an apparently attractive but incompatible plan, explicit approval, actual payment/refund read-back and the final business outcome.

**Critical distinction:** a committed payment, an application timeout, a successful refund request and a completed refund are different facts. Never spend a pending refund as though cash has already returned.

**Delivery risk:** medium. The chief threat is scope: multi-merchant access, real logistics, broad catalogs and protocol compatibility can consume the schedule. Keep logistics and stock failures explicitly simulated while payment actions remain authentic sandbox calls. Do not inject load or faults into PayPal itself.

**Kill conditions:** real create/approve/capture/read-back/void-or-refund is not proven within two days; business recovery reduces to fixed scripted branches; a close public product already demonstrates the same goal-level recovery; or nonfinancial data integration dominates the build.

## Finalist 2: ReservePilot

**User:** a small merchant with supplier invoices, refunds, delayed availability and agent-assisted purchasing.

**Job:** decide what can safely be committed now, rather than treating gross receipts, unavailable funds and future expected inflows as spendable money.

**Example:** a fictional merchant has $1,000 in provider-available funds, a separate $200 internal contingency buffer, $500 already committed to suppliers and $150 of confirmed refund obligations. Free internal commitment capacity is $150. A $200 purchase must be deferred or explicitly re-planned. If the provider's available balance already excludes its own hold, do not subtract that hold again. A pending or unknown payment outcome continues to reserve capacity until reconciled.

**AI work:** extract invoice deadlines, cancellation conditions and operational priorities; ask about uncertain obligations; propose cash-allocation alternatives. The model cannot declare held funds released or invent inflow certainty.

**PayPal work:** real sandbox sales and refunds, transaction/balance report imports with freshness labels, and optionally a verified enabled Payouts path. Model seller obligations locally and expose that limitation.

**Difference to validate:** Supplora Pay already schedules invoices within a cash cap. ReservePilot needs live or accurately labeled availability, concurrent commitments, refund obligations and stress scenarios, with no double-counting. This is a stronger accounting model, not merely a CFO chat UI.

**Measures:** forbidden overcommitments, deadline violations, duplicate payments, plan feasibility, time to complete a payment decision and user comprehension. Show synthetic stress results only as synthetic.

**Kill conditions:** trustworthy availability cannot be supplied even through reviewed statements, the product cannot distinguish stale and current facts, or interviews show merchants already solve the specific problem with existing tooling.

## Finalist 3: ClearFX

**User:** a small cross-border seller or freelancer facing invoice, payer, merchant-receivable and refund currency differences.

**Job:** explain the complete economic terms before payment and trace a later discrepancy to its source.

**AI work:** extract contractual fee/currency obligations, identify ambiguous terms and explain differences with citations. Exact decimal arithmetic and a pinned currency exponent table calculate money.

**PayPal work:** Invoicing/Orders and actual payment records. If enabled, integrate Currency Exchange v2 quotes, expiry and fx_id into the full FXaaS flow. Otherwise an honest invoice-to-record reconciliation remains possible, but its novelty and grand-prize potential are lower.

**Important finding:** real PayPal FX quote APIs exist. It would be incorrect to dismiss all FX ideas because PayPal has no FX API. It would also be incorrect to call these a public HFT exchange API. FXaaS needs eligibility and contractual enablement.

**Demo:** show an approved price, a changed or expired quote, a fresh consent decision and verified receivable/refund records. If a quote is simulated, put that label beside the amount.

**Kill condition:** no FXaaS access within one day if the core pitch relies on live guaranteed quotes. Do not wait a week for onboarding.

## Other finalists and why they rank lower

**ReturnRouter:** a merchant-authorized assistant compares permitted replacement, partial-refund and return options using customer preference, stock and transparent costs. Real refunds plus a good consumer flow create a strong demo. AutoRescue, Return Loop and Refund Desk make broad originality weak. A narrower difficult use case and real merchant evidence are required.

**ToolMeter:** meter a bounded paid AI tool, verify a service receipt, aggregate usage into an approved PayPal invoice and enforce a spend cap. This serves AI infrastructure directly. Existing usage billing, x402 and Mastercard machine payments reduce novelty. Billing must not depend solely on an LLM saying a task succeeded. Do not pretend REST per-request payments are free or sub-cent settlement.

**TreasuryLab:** model a fictional merchant's fiat/PYUSD liquidity and replay settlement delays, quote expiry and wallet/RPC failure. Demonstrate an actual testnet PYUSD transfer separately from an actual PayPal Sandbox merchant payment. Interesting quantitative infrastructure, but inaccessible internal data and split environments weaken the impact story. A pure simulation with a token checkout is a poor fit for the overall first prize.

## HFT: what transfers and what does not

Literal exchange HFT is a weak project choice here. The public surfaces reviewed are payments, merchant operations, FX presentment and blockchain settlement. None establishes a public PayPal exchange order book, colocated execution venue, tick feed or access to its internal trading systems. No current evidence supports a profitable arbitrage claim.

Transfer the useful engineering disciplines instead: pre-trade risk limits, inventory reservations, staleness checks, exposure accounting, bounded retries, kill switches, replay and deterministic reconciliation. Use AI for intent/term extraction, regime hypotheses and explanation. Keep LLM calls outside any latency-critical execution path. Measure latency and failure behavior on a local harness; do not benchmark PayPal with a synthetic trading load.

A credible quantitative thesis is payment liquidity under uncertain settlement, not a claim that a chat model beats a market maker. Costs include fees, FX spreads, funding and capital lockup, network/RPC reliability, approval requirements and irreversibility.

## Research evidence translated into product requirements

Undermind surfaced literature on cross-stage binding, semantic attacks and process-level evaluation. The formal-analysis preprint was also inspected through its arXiv HTML. The other papers were reviewed at metadata/abstract level in this pass; their experiment results were not reproduced.

- [A Formal Analysis of Agent Payment Protocols](https://arxiv.org/abs/2609.00060) studies relationships across intent, authorization, payment and fulfillment. Use its lifecycle framing to test that each locally valid action still belongs to the same approved business purpose. Do not generalize its modeled findings into a claim that PayPal is broken.
- [Whispers of Wealth](https://doi.org/10.1109/IMNS67862.2026.11655291) examines reasoning-layer attacks against an AP2-based agent. Cryptographic consent alone does not prove that a recommendation was unmanipulated. Never cite its controlled attack rate as a universal real-world rate.
- [Agentic Commerce World](https://arxiv.org/abs/2608.02441) motivates process evidence and reproducible environments. Evaluate the action trajectory and the terminal outcome separately.
- [Between Promise and Pain](https://doi.org/10.1145/3725783.3764388) cautions against treating automated root-cause analysis as solved. Diagnosis and recovery should abstain when evidence is insufficient.

## Evaluation plan: targets, not claimed results

Use a held-out matrix spanning normal, adversarial, uncertain and partial-execution cases. Publish per-case results, seeds, traces and limitations. Start with approximately 30 meaningful scenario specifications; expand only where coverage gaps justify it. Separate plan generation cases from actual sandbox mutation runs so the suite does not require hundreds of payment calls.

Required cases for RecoverPlan:

1. Ordinary full success, with exact approval and real capture read-back.
2. Capture succeeds but the application loses the response; reconciliation finds it and creates no new payment.
3. A duplicate webhook and an out-of-order earlier event do not regress state or increase money totals.
4. A changed merchant, total, currency, product dependency or expired approval requires new approval.
5. Cheapest replacement violates compatibility or deadline; the planner/validator rejects it.
6. Cancellation is unavailable after fulfillment begins; the plan preserves the irreversible cost.
7. Refund requested but pending; the budget does not treat it as available cash.
8. A merchant message contains a prompt injection; it cannot alter policy or tool permissions.
9. Worker crashes after an external side effect but before local acknowledgment; replay reconciles before continuing.
10. Two workers propose actions against the same remaining budget; durable reservations prevent local overcommitment.
11. Forged or wrong-tenant webhook evidence is rejected.
12. No feasible recovery exists; the system explains the blockers and stops.
13. Model unavailable or schema-invalid; the system preserves state and offers deterministic status without fabricating a plan.
14. Refund or void fails; the mission remains unresolved, with the actual obligation visible.

Compare three baselines: a plain tool-calling agent, a deterministic predefined recovery workflow, and the full planner-plus-validator product. The AI contribution must improve handling of unseen goals/terms/dependencies compared with the static workflow, while the validator preserves safety. If it does not, simplify the project or change the thesis.

Measure plan constraint satisfaction, unsupported evidence citations, unsafe action proposals and executed actions separately, recovery completion, duplicate external effects in tested runs, unresolved obligations, human task completion and time, and latency/cost per plan. A proposed unsafe action blocked by policy is not an executed unsafe payment. Zero observed violations in a finite test suite is not a universal security guarantee. Measure business success, not only a green payment status.

## Smallest realistic architecture for RecoverPlan

- **Python/FastAPI** transport with typed request and response schemas. Use async HTTPX for PayPal and AI calls. Expose only specific read/plan/approve/execute endpoints.
- **PostgreSQL** holds missions, approved constraints, plan versions, actions, money commitments, provider references, approvals, a webhook inbox and an outbox. Use integer minor units or exact Decimal by supported currency exponent. Never use float for money or assume all currencies have two decimals.
- **One durable worker** processes state transitions. Start with a Postgres-backed work queue and leased jobs; add Redis only for a measured need, not as the authoritative money ledger. If the team already knows a durable workflow engine, it can replace this worker, but learning one is not a requirement.
- **One bounded AI planner** reads a scoped evidence set and returns a typed graph/plan with source IDs. There is no need for a multi-agent system. Maximum tool calls, retries, wall time and tokens are explicit.
- **Deterministic validator** checks action ownership, current PayPal state, approved constraints, arithmetic, dependencies, seller permission and fresh consent. Version approvals against a canonical plan digest. Payment credentials stay in the execution service.
- **PayPal adapter** persists endpoint-specific idempotency keys before mutation; treats unknown outcomes as unknown; queries actual resources; applies exponential backoff with jitter only where retry semantics allow it. No database lock stays open during a remote API call.
- **Evidence layer** stores minimized provider facts, source ownership, model proposals, validation decisions and action results. Hash chaining can detect edits within its threat model; it is not magic immutability.
- **Frontend** presents one mission, its actual commitments, alternatives and the exact approval. A coherent product needs readable failure and unresolved states, keyboard access and responsive layouts.

Useful indexes: unique `(tenant_id, action_key)` for local operations, unique provider event ID within its valid provider/app scope, lookup indexes on mission/status and provider resource references. Use an explicit action state machine with compare-and-set/version checks. Outbox consumers remain idempotent; do not claim a local SQL transaction atomically commits PayPal. Scheduled reconciliation closes gaps.

Migrations should be versioned and additive during the build. Back up Postgres and test restoration of an in-progress mission before freezing the demo. Define retention for minimized audit data and keep secrets and customer PII out of exported fixtures. Logs include tenant-safe correlation IDs, latency, outcome and failure class without credentials. Operational costs are database/worker hosting, AI calls, evidence storage and webhook availability.

## Sponsor tools: roles, not a shopping list

| Tool | Useful role | Decision |
| --- | --- | --- |
| Render | Host the API, worker and demo | Good default if the team can operate it reliably |
| Postman | Publish reproducible sandbox lifecycle and failure-case collections | High value for independent judge verification |
| AG Grid | Inspect a real evidence/action table | Use only when the table is central; design is still the team's responsibility |
| APIMatic | Current SDK context and client scaffolding | Useful integration aid, not the product's innovation |
| Elastic | Search larger evidence sets and retrieve cited records | Add only if a real retrieval problem exceeds Postgres needs |
| Bryntum | Visualize dependency/deadline scheduling | Potential RecoverPlan fit; avoid a large scheduling integration |
| Channel3 | Product discovery for a real commerce use case | Optional; a bounded seeded catalogue is enough for the first proof |
| Kernel | Browser access where no supported API exists | Avoid browser-driven payment entry; keep PayPal execution through supported APIs |
| Astropods | Agent deployment/orchestration | Alternative infrastructure, not a necessary second orchestration layer |
| Zapier | Connect a merchant workflow for an optional demonstration | Keep the source of truth and payment authority in the backend |

Choose two or three only when they improve the core product. Overall first prize does not require collecting sponsor integrations. Sponsor eligibility and current terms should be checked separately if pursuing a special prize.

## Twenty-day delivery sequence

| Dates, IST | Concrete result | Decision gate |
| --- | --- | --- |
| Oct 23-24 | Two candidate storyboards, access probes, sandbox lifecycle proof and a small user interview plan | Kill inaccessible APIs and ideas that only rename existing projects |
| Oct 25-26 | Working RecoverPlan vertical slice plus a simple ReservePilot flow; ask 3-5 relevant users to attempt tasks | Commit to one after observing task difficulty and usefulness; do not fabricate interviews |
| Oct 27-30 | Complete real payment lifecycle, durable state, approvals and one useful AI recovery planner | A fresh clone must run the main flow |
| Oct 31-Nov 3 | Failure injection, held-out scenarios, baseline comparison and unresolved-state handling | If AI adds no measurable benefit, adjust scope immediately |
| Nov 4-6 | Product polish, accessibility, error copy, demo reset and minimized evidence | A new tester completes the scenario without live narration |
| Nov 7-8 | Reproducible evidence collection, docs, license, public repo preparation and hosted stability | Every performance or safety claim links to measured evidence |
| Nov 9-10 | Record a 2:40-2:55 video, review the submission and test judge access | Show actual operation and at least one meaningful failure/recovery |
| Nov 11 | Freeze the demonstrated version, rehearse setup and submit with a buffer | Preserve the submitted build through judging |
| Nov 12 | Contingency only | Do not spend this day adding speculative architecture |

Suggested split: one person owns payment state, DB and execution; the other owns planner, evidence UX and evaluation. Both review action authority and rehearse the product story. These are role assignments, not a request to spawn autonomous development agents.

## Research limitations and what would change the decision

- The supplied file `E:\PayPal_AI_Hackathon_Problem_Research_and_PayGuard_AI.pdf` was not found. The pasted proposal was available. No claims about the PDF's contents or layout are made.
- No production PayPal incident telemetry, fraud labels, customer data or internal roadmap was accessed.
- No sandbox credentials were supplied; documented API capabilities were not verified against the team's account.
- Public project descriptions are not implementation audits. The event gallery is unpublished, and search cannot discover private entries.
- Broad product hypotheses are not market validation. Three to five short interviews and observed tasks can falsify a candidate; they cannot establish a market size or adoption forecast.
- Concept ratings are transparent planning judgments on an ordinal scale. Differences of a few points are not statistically meaningful or probabilities. A one-point change in each of five ratings can move a total by five points.
- Choose a different finalist if user evidence, exact competitor behavior, available integrations or the first prototype contradict this recommendation. The objective is a better entry, not defending the first idea.

## Files

- [Full 100-idea bank](idea-bank.md)
- [Structured idea records](idea-bank.json)
- [Planning assessment inputs](concept-assessment.json)
- [Source registry](sources.md)
- [Reproducible record builder](build_research.py)
