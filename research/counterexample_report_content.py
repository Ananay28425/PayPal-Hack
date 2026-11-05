"""Reviewed proposal content. Hypotheses, published capabilities and results stay separate."""

SOURCES = [
 ("S01", "PayPal AI Hackathon official rules", "https://paypalaihackathon.devpost.com/rules", "Requirements, equal judging criteria, deadline and judging access."),
 ("S02", "PayPal hackathon resources", "https://paypalaihackathon.devpost.com/resources", "Published PayPal capabilities and developer resources."),
 ("S03", "PayPal REST negative testing", "https://developer.paypal.com/negative-testing/request-headers", "Supported request-header simulations; not internal fault control."),
 ("S04", "PayPal idempotency", "https://developer.paypal.com/api/rest/reference/idempotency", "Endpoint-specific support, retention and concurrent-request caveats."),
 ("S05", "PayPal webhook integration", "https://developer.paypal.com/api/rest/webhooks/rest/", "Delivery, message verification and mock-event limitations."),
 ("S06", "PayPal Orders v2 capture", "https://developer.paypal.com/api/orders/v2/orders-capture", "Buyer approval and server capture contract."),
 ("S07", "PayPal Payments v2 refund", "https://developer.paypal.com/api/payments/v2/captures-refund", "Capture-linked full/partial refunds and permission requirements."),
 ("S08", "Rystic PayPal simulator", "https://www.rystic.ai/docs/simulators/paypal", "Vendor describes deterministic local PayPal simulation and faults; not independently tested."),
 ("S09", "Antithesis product documentation", "https://antithesis.com/product/", "Vendor describes deterministic whole-system testing, fault injection and debugging."),
 ("S10", "Microsoft RESTler source and documentation", "https://github.com/microsoft/restler-fuzzer", "Stateful API fuzzing, checkers, bug buckets and replay logs already exist."),
 ("S11", "RESTifAI: reusable LLM API tests", "https://doi.org/10.1145/3774748.3787598", "Published abstract and retrieved workflow description; no replication conducted."),
 ("S12", "APITestGenie (Pereira et al., 2026)", "https://doi.org/10.1145/3793654.3793743", "Undermind metadata/abstract: requirement-to-API-test generation is established."),
 ("S13", "LLM-generated oracles (Ma and Eisty, 2026)", "https://doi.org/10.48550/arXiv.2607.10277", "Undermind abstract: preliminary evaluation reports substantial oracle variability."),
 ("S14", "Narvar agentic post-purchase products", "https://corp.narvar.com/agentic-ai-post-purchase", "Published commercial overlap for generic delivery rescue and exchanges."),
 ("S15", "AG Grid / AG Studio sponsor brief", "https://paypalaihackathon.devpost.com/details/aggrid", "Analytics, custom product presentation and agent-driven dashboard capabilities."),
 ("S16", "APIMatic sponsor brief", "https://paypalaihackathon.devpost.com/details/apimatic", "PayPal Context Plugin contributes to integration development."),
 ("S17", "Astropods sponsor brief", "https://paypalaihackathon.devpost.com/details/astropods", "Agent deployment, tools and observability; actual account access untested."),
 ("S18", "Bryntum sponsor brief", "https://paypalaihackathon.devpost.com/details/bryntum", "Scheduler/Gantt interactions; our runner would enforce execution semantics."),
 ("S19", "Channel3 sponsor brief", "https://paypalaihackathon.devpost.com/details/channel3", "Product discovery, variants and enrichment; meaningful API use required for its prize."),
 ("S20", "Elastic sponsor brief", "https://paypalaihackathon.devpost.com/details/elastic", "Search and analytics, trial and local options."),
 ("S21", "Kernel sponsor brief", "https://paypalaihackathon.devpost.com/details/kernel", "Cloud browser operation and session observation; no deterministic system replay implied."),
 ("S22", "Postman sponsor brief", "https://paypalaihackathon.devpost.com/details/postman", "API testing, documentation and collaboration."),
 ("S23", "Render sponsor brief", "https://paypalaihackathon.devpost.com/details/render", "Web services, databases, workers and optional workflows."),
 ("S24", "Zapier sponsor brief", "https://paypalaihackathon.devpost.com/details/zapier", "Connected app actions; account permissions and plan access need verification."),
]

# Each section is deliberately one page. Tables/figures replace prose where useful.
PAGES = [
 dict(section="Decision brief", title="Counterexample", lead="An AI-assisted payment reliability lab for PayPal integrations.",
      blocks=[
       ("The proposition", "Find a payment-workflow defect, show the exact sequence that caused it, reduce that sequence, and turn it into a regression test. Confirm the relevant behavior with genuine PayPal Sandbox evidence."),
       ("Executive judgment", "Assembly remains a credible customer-facing project. It is not established as the most original or strongest entry in an unseen field. Counterexample is my strongest alternative for demonstrating systems engineering and a potential PayPal developer-tool pilot. It has greater implementation risk and a less natural fit for two of the ten sponsors."),
       ("Why this is a conditional recommendation", "The project must demonstrate additional defect discovery or faster reproduction against a strong simple baseline. A polished dashboard around a scripted bug would not justify switching. No available evidence supports a first-prize probability, unanimous judge enthusiasm, or immediate global deployment."),
       ("Origin and evidence status", "This develops our earlier independently proposed Checkout Wind Tunnel seed. The new emphasis is a reviewable payment contract, independent oracle, shortened counterexample, and portable regression package. It is not claimed to be a new invention of testing or a globally unique product. This report includes a tiny executed local experiment; the proposed AI, PayPal and sponsor integrations remain unbuilt.")
      ], note="Prepared 26 October 2026. Exactly 20 pages. Research and architecture proposal, with explicitly bounded local evidence.", refs=["S01","S08","S09","S10","S12"]),
 dict(section="Assembly reassessment", title="Assembly is credible; superiority is unproven", lead="A strong idea needs a demonstrated advantage. The number or reputation of future competitors cannot supply that evidence.",
      table=[
       ["Question", "Honest assessment"],
       ["Strongest?", "Best full-ten-sponsor product fit among our developed options; not proven best across the hackathon."],
       ["Most credible?", "A bounded catalogue and genuine sandbox flow are feasible. Reliable product evidence is still an untested dependency."],
       ["Most original?", "Goal-based shopping and constraint configuration are established families. Differentiation would be workflow and verified behavior."],
       ["Most likely to win?", "No calibrated estimate exists. Participant count is not the count of eligible, strong final submissions."],
       ["Globally deployable?", "Neither Assembly nor Counterexample has production, privacy, operational or adoption evidence."]
      ], blocks=[
       ("What would make Assembly excellent", "A user changes a real requirement; the system exposes a non-obvious configuration failure, traces it to trustworthy evidence, repairs it, and completes the approved purchase. Judges can vary the input and obtain a defensible result. That remains a strong product story."),
       ("Where it could disappoint", "If the catalogue is hand-curated around one rehearsed conflict, the solver checks trivial rules, and the LLM only writes explanations, the apparent depth exceeds the real contribution. The ten-sponsor requirement also raises delivery risk. A new project name would not solve either problem."),
       ("What changes in this recommendation", "My earlier Assembly recommendation compared it mainly with PayGuard. This report compares it with a deeper infrastructure alternative. Counterexample has the stronger technical thesis if its experiment succeeds; Assembly retains the clearer consumer experience and sponsor coherence.")
      ], refs=["S01"]),
 dict(section="Alternative selection", title="Choose a mechanism, then earn the novelty claim", lead="I evaluated different directions before selecting this narrower reliability product. These are qualitative judgments, not numerical rankings or win probabilities.",
      table=[
       ["Direction", "Attraction", "Reason to reject or qualify"],
       ["Assembly", "Visible customer benefit; coherent discovery-to-purchase flow", "Product facts and demonstrated reasoning advantage remain uncertain."],
       ["Post-purchase rescue", "Clear delivery/refund problem; attractive live demo", "Narvar already describes automated resolution and exchanges. Broad rescue is not enough."],
       ["Generic payment simulator", "Deterministic tests; useful infrastructure", "Rystic already documents a PayPal simulator. Building another alone has a weak novelty case."],
       ["General AI test generator", "Broad developer demand", "RESTler, RESTifAI and APITestGenie establish substantial overlap."],
       ["Counterexample", "Payment-specific contract to reproducible failure to repair evidence", "Worth testing only if the integrated workflow adds measurable value beyond those foundations."]
      ], blocks=[
       ("The selected wedge", "Serve developers shipping AI-assisted checkout in a controlled merchant application. Relate the customer's approved purchase, actual payment resource, application database and fulfillment action in one failure witness. A successful HTTP response does not by itself establish that those facts agree."),
       ("What original means here", "The proposal is our synthesis for this team and hackathon. The reviewed sources do not establish exclusivity. Search cannot prove that nobody has built the same combination; a competitor's undocumented feature may overlap. The defensible claim is the precise capability we implement and compare."),
       ("What we are not changing", "The target remains the overall first prize. Sponsor use supports implementation and presentation; it does not replace a coherent user problem or create extra weight under the overall rubric.")
      ], refs=["S01","S08","S09","S10","S11","S12","S14"]),
 dict(section="Customer problem", title="The payment can succeed while the purchase fails", lead="The initial customer is a small integration team, agency, or merchant developer whose automated tests pass but whose checkout can still violate business expectations.",
      blocks=[
       ("A concrete incident", "A buyer approves one $125 purchase in our synthetic demo storefront. PayPal capture completes, but the application's response is lost. Recovery reads the payment and creates a fulfillment job. A delayed capture event then creates a second fulfillment job. The payment provider may have behaved correctly throughout; the merchant still ships twice."),
       ("Why ordinary signals can be insufficient", "An API smoke test sees valid responses. A browser test sees a thank-you screen. A queue test sees eventual delivery. None necessarily checks the shared rule: one accepted purchase must produce no more than one fulfillment commitment. That rule belongs to the merchant workflow, not to a generic HTTP status checker."),
       ("Why AI could help", "Requirements, API descriptions, product variants and UI behavior contain different parts of the intended purchase. AI can propose scenario sequences and input variations from that context. Deterministic execution and independent checks must decide whether the sequence violates a reviewed rule."),
       ("Product boundary", "Start with one owned storefront, one sandbox seller, one currency and a small instrumented application. Do not advertise arbitrary URL scanning or inference of every merchant's policy. A real customer must approve the rules and integration permissions. Payment testing and fulfillment testing remain distinguishable."),
       ("Impact hypothesis", "The immediate benefit to measure is reduced time to a valid reproducer and more distinct workflow defects found per testing budget. Fewer production incidents or support cases would require subsequent pilot evidence. This project has no measured share of PayPal's aggregate transaction losses.")
      ], refs=["S03","S04","S05"]),
 dict(section="Competition and research", title="The foundations already exist", lead="Counterexample must add a valuable payment-specific workflow. It cannot claim novelty for simulation, replay, fuzzing, LLM tests, or fault injection in isolation.",
      table=[
       ["Prior work", "Established overlap", "What our prototype must add"],
       ["Rystic PayPal twin", "Local deterministic payment resources and fault controls", "Cross-layer business invariants and separately identified live sandbox confirmation."],
       ["Antithesis", "Systematic fault exploration, deterministic execution and debugging", "A small PayPal-specific onboarding and evidence workflow; no claim to beat its general engine."],
       ["RESTler", "Stateful API sequences, checkers, bug buckets, replay", "Approval/fulfillment/payment correlations and browser-to-backend cases."],
       ["RESTifAI / APITestGenie", "LLM-generated reusable API tests from specifications or requirements", "Independent frozen business rules, schedule perturbation and failure reduction."],
       ["Ma and Eisty", "Preliminary evidence of variable LLM oracle quality", "A human-reviewed oracle boundary and measured false-positive behavior."]
      ], blocks=[
       ("The honest differentiation statement", "Counterexample would produce a portable evidence package linking an approved purchase to a specific violated merchant rule, a shortened causal trace, observed sandbox resources and a regression case. Whether that package improves developer work is an experiment, not a fact established by this report."),
       ("Evidence quality", "Vendor documentation establishes advertised capabilities, not independent product performance. The two Undermind papers were reviewed through metadata and abstracts; this is not a full-text systematic review or a replication. No reviewed competitor was installed or benchmarked."),
       ("Do not weaken the baseline", "A strong Postman test pack with the same invariants and a randomized legal scheduler is a meaningful starting comparison. Beating a happy-path-only toy suite would not show much.")
      ], refs=["S08","S09","S10","S11","S12","S13"]),
 dict(section="User experience", title="One investigation, from requirement to regression", lead="The product should feel like a focused debugging workbench. The user should understand the financial consequence before seeing the infrastructure.",
      blocks=[
       ("1. Define and review", "The developer selects the owned demo application, imports its API contract and states the purchase rules. AI proposes structured scenarios and asks for missing meanings. The developer reviews the invariant catalogue before the run. Each rule has an ID, version, applicability and a human explanation."),
       ("2. Explore within a budget", "The developer chooses a bounded run: maximum scenarios, sandbox calls, time and concurrency. The runner displays valid executions, rejected proposals, inconclusive cases and real failures separately. It must not turn a timeout into a green pass or inflate the defect count with repeats."),
       ("3. Inspect the counterexample", "A linked view shows buyer approval, application operations, provider observations and fulfillment. Selecting a failing rule highlights the events that support it. A plain-language explanation cites those events. The developer can inspect original redacted records and compare the buggy and corrected versions."),
       ("4. Reduce, verify and export", "The reducer removes irrelevant actions while preserving prerequisites and the same failure. The developer reruns the case after a reviewed patch. Export includes the scenario, rule version, application revision, reset instructions, artifacts and Postman regression collection. Browser steps that cannot run in Postman remain in the runner manifest."),
       ("5. Hand off with consent", "An approved Zapier action can create an issue in a connected tracker with the redacted reproducer. Show destination and content first. The issue's creation is independent of payment state and cannot trigger a payment or alter the test verdict."),
       ("Interaction principle", "One primary action per stage: review, run, investigate, reproduce. AG Studio presents evidence; Bryntum edits selected local event ordering. The same backend validates every change. Neither interface becomes a second source of business truth.")
      ], refs=["S15","S18","S22","S24"]),
 dict(section="Architecture", title="Separate proposals, execution and judgment", lead="Use a small modular application. Sponsor tools occupy bounded roles around one authoritative run record.", diagram="architecture",
      blocks=[
       ("Authority", "PostgreSQL stores approved contracts, scenario versions, operation intents, run leases, observations and export manifests. The runner executes only allowlisted actions. An independent oracle reads observations; it cannot issue payments. AI never receives the payment secret or authority to edit a passing threshold."),
       ("Isolation", "The application under test and the testing control plane use separate identities, schemas and sandbox runs. Fault switches exist only in an owned test environment. No test-control route is enabled in a merchant production deployment. Recorded and live modes have distinct credentials, resource IDs and visible labels."),
       ("Traceability", "Each event carries run_id, scenario_version, purchase_intent_id, actor, operation_id, provider resource ID when present, and observation provenance. A manifest hash detects accidental changes to exported material; it does not prove that the underlying assertions are true."),
       ("Minimal topology", "One Python API, one runner/worker, PostgreSQL, a TypeScript interface and one bounded Astropods AI stage. Add a Rust reducer only after the Python implementation works and profiling or portability justifies it. Elastic is a rebuildable search projection.")
      ], refs=["S17","S20","S21","S23"]),
 dict(section="Executable contract", title="Make the economic rules inspectable", lead="The hardest component is the oracle: a trustworthy decision about what should have happened. LLM-generated assertions alone are insufficient.",
      table=[
       ["Rule", "Proposed check and scope"],
       ["Approved identity", "For a fulfilled purchase, the accepted SKU/variant/quantity and approved offer version equal the fulfillment commitment."],
       ["Paid before fulfillment", "A fulfillment commitment requires a verified completed capture with matching merchant, amount and currency, under this prepaid demo's policy."],
       ["No duplicate fulfillment", "At most one fulfillment commitment per purchase intent. Explicit split shipments require a different, reviewed rule."],
       ["Refund consistency", "Successful recorded refunds do not exceed the corresponding captured amount; a delayed capture event cannot erase a confirmed refund."],
       ["Ambiguity is visible", "A request with an unknown outcome remains unresolved until evidence establishes its state; the UI cannot label it definitively failed or paid without support."]
      ], blocks=[
       ("Formal enough to test", "For a prepaid purchase i, require fulfill_count(i) <= 1 and fulfilled(i) implies verified_capture(i, approved_amount, approved_currency). Compare immutable approved_manifest(i) with fulfilled_manifest(i). Store integer minor units using the currency's declared precision; use only USD in the MVP."),
       ("Applicability matters", "Some merchants ship before capture or deliberately split orders. These are policy choices, not universal bugs. Each oracle declares the workflow it applies to. A finite test can witness a safety violation but cannot prove an eventual outcome will never occur; bounded recovery deadlines produce an explicit timeout verdict."),
       ("Independent review", "Freeze rules before scoring generated scenarios. The model may propose a new rule, but it requires review and a new benchmark version. Preserve unknown and invalid outcomes rather than coercing them into pass/fail.")
      ], refs=["S04","S06","S07","S13"]),
 dict(section="AI method", title="Use AI to search the problem space", lead="The model earns its place by proposing useful, legal scenarios that a fixed template pack misses under the same execution budget.",
      blocks=[
       ("Inputs and retrieval", "Supply the owned application's OpenAPI contract, approved business rules, allowlisted UI actions, a small product-variant catalogue and redacted prior traces. Retrieve relevant failures from Elastic by operation and rule IDs before semantic similarity. Restrict corpus size and exclude the held-out fault definitions."),
       ("Typed scenario proposal", "Astropods hosts a bounded proposal stage. Output is a JSON scenario with actors, preconditions, step dependencies, product fixtures and permitted fault points. Validate its schema and dependencies before execution. An unsupported operation is rejected; generated shell, SQL or arbitrary code is never executed."),
       ("Controlled iteration", "Run a legal proposal, then return a compact observation summary: reached states, violated rule IDs, novelty of the failure signature and rejected preconditions. Permit a fixed number of revisions. Pin model identifier, prompt version, retrieval snapshot and sampling settings. LLM output need not be deterministic; the accepted scenario becomes immutable."),
       ("What remains deterministic", "The runner resolves dependencies, the checker evaluates frozen rules, and the reducer evaluates candidate traces. A natural-language failure summary must cite observed event IDs. The model cannot invent a provider result, waive buyer approval, expand the sandbox budget or declare a test passed."),
       ("Ablations", "Compare fixed templates, random legal schedules and AI proposals using the same oracle and operation budget. Disable retrieval separately. Measure valid-scenario rate, distinct verified defects, false positives, cost and time to a reproducer. If the LLM adds no value, the product may remain useful testing software, but its hackathon AI case becomes weak."),
       ("Security boundary", "Retrieved product text and pages are untrusted data. They cannot alter destinations, credentials, test permissions or contracts. The model sees only redacted observations and scoped tool definitions.")
      ], refs=["S10","S11","S12","S13","S17","S20"]),
 dict(section="Reproduction semantics", title="Replay what we control; verify what we do not", lead="A live payment service cannot be rewound. Treat simulation, recorded replay and live sandbox execution as separate kinds of evidence.",
      table=[
       ["Mode", "Guarantee available", "Cannot establish"],
       ["Local synthetic model", "Controlled state, clock and event order; exact local repeatability", "PayPal behavior, real browser timing or production correctness"],
       ["Recorded adapter replay", "Known responses under a versioned application schedule", "That a new sequence would produce those responses remotely"],
       ["Live Sandbox confirmation", "Actual fresh sandbox resource observations for the executed path", "Deterministic remote timing, exhaustive behavior or live-money reliability"]
      ], blocks=[
       ("Legal fault points", "Drop a response after the owned adapter has received it; pause a local worker before committing application state; redeliver an internal normalized event after authentic ingress verification; change an owned offer between review and use. Do not forge provider signatures or claim to inject faults into PayPal."),
       ("Reduction algorithm", "Remove blocks or individual steps, preserve producer-consumer dependencies and reset the owned state. Retain a candidate only if the same independent failure reappears. Record rejected candidates and evaluation count. A greedy fixed point is deletion-irreducible under that strategy, not necessarily the globally shortest counterexample."),
       ("Failure fidelity", "A shorter trace that triggers a different assertion is not a valid reduction of the original failure. Keep the purchase identity, required provider observations and violated rule fixed. Reconfirm a relevant reduced case in live sandbox with new resources; report an inconclusive result if remote behavior differs."),
       ("What the timeline means", "Bryntum edits local scheduler constraints, not PayPal's clock. Kernel records a browser session for inspection; the video is not an executable replay specification. Causal order comes from operation dependencies, not unsynchronized wall-clock sorting.")
      ], refs=["S08","S09","S10","S18","S21"]),
 dict(section="PayPal integration", title="Genuine payment evidence is central", lead="The core demonstration must include a real PayPal Sandbox transaction. A simulator alone would weaken both the proof and the hackathon integration.",
      blocks=[
       ("Lifecycle", "The controlled merchant creates an order for the frozen approved offer. A sandbox buyer approves it through the supported checkout flow. The backend captures the order and stores capture/order IDs, amount, currency and returned status. Read back the relevant resource when resolving ambiguity. An application approval record does not replace PayPal buyer approval."),
       ("Retries and ambiguity", "Persist an operation intent and stable request key before the call. Retry only according to the endpoint's documented idempotency behavior and retention window. A lost response is not evidence that capture failed. New business attempts must not silently receive fresh keys while the original outcome is unknown. Application-level uniqueness remains necessary."),
       ("Webhooks", "Verify actual incoming messages using the documented method, persist the inbox record durably, deduplicate and process asynchronously. Fault injection operates after trusted ingestion. Mock simulator events and real sandbox events must carry different provenance. Reconcile by resource state when event ordering or a response is ambiguous."),
       ("Negative testing and refunds", "Use PayPal-Mock-Response only for documented REST operations and supported error cases; record it as an intentionally simulated provider error. For refund tests, use a genuine capture-linked sandbox refund and inspect its status. A submitted or pending refund is not a completed refund. Do not import legacy NVP error-trigger tricks into Orders v2."),
       ("Two demonstration fixtures", "Fixture A loses the application's capture response and then redelivers its normalized capture event, exposing duplicate fulfillment. Fixture B changes a product variant at the same total after approval, exposing a manifest mismatch. These are intentionally seeded merchant defects, never allegations about PayPal."),
       ("Centrality test", "Remove PayPal and the live evidence path disappears: the system can no longer establish what the selected provider actually returned. Remove the independent rule checker and the live transaction alone says nothing about merchant correctness.")
      ], refs=["S03","S04","S05","S06","S07"]),
 dict(section="Data and operations", title="Durable state prevents the tester becoming the bug", lead="Build the control plane as carefully as the system it evaluates. Retrying a run must not silently create another business operation.",
      table=[
       ["Record", "Identity and purpose"],
       ["Contract / scenario", "Immutable version and hash; review actor; approved rule set; prerequisites"],
       ["Run / checkpoint", "Run ID, isolated fixture namespace, mode, lease expiry, bounded progress"],
       ["Operation intent", "Unique run + logical operation; request key, body hash, provider IDs, outcome state"],
       ["Observation / inbox", "Run sequence, source, causal parents, verified-event ID, redacted payload reference"],
       ["Failure / export", "Rule ID + normalized signature, evidence links, code revision and reproducibility manifest"]
      ], blocks=[
       ("Consistency and query shape", "Use PostgreSQL transactions and uniqueness constraints for operation identity and event consumption. Index observations on (run_id, sequence) and failures on (rule_id, signature). Search reads a rebuildable Elastic projection, while capture/recovery decisions use the authoritative database. Begin with one worker and bounded parallel browser sessions."),
       ("Crash recovery", "Lease-based worker ownership prevents abandoned jobs from remaining invisible. On restart, inspect unresolved operation intents before retrying. Use a durable outbox for exports or external handoffs. An outbox can deliver more than once; the receiving action also needs deduplication or explicit reconciliation. Preserve failed and inconclusive runs."),
       ("Security and retention", "Keep sandbox secrets server-side, block production endpoints and allow only owned target origins. Redact tokens, payer details and browser recordings before model access or export. Validate URLs and certificate-fetch destinations against provider guidance. Use per-run storage isolation, expiry, quotas and an authenticated test-control API."),
       ("Schema evolution and recovery", "Version the scenario and trace schemas; do not reinterpret old runs under new semantics. Add migrations with backward-readable exports. Test a database backup/restore and runner restart before submission; an evidence package must still explain which code and contract produced it.")
      ], refs=["S04","S05","S20","S23"]),
 dict(section="Sponsor design 1 / 2", title="Give the first five sponsors distinct jobs", lead="All ten sponsors remain a user requirement. Meaningful use includes runtime, development and verification; it does not mean ten services on the payment path.",
      table=[
       ["Tool", "Substantial proposed contribution", "Evidence and boundary"],
       ["AG Grid / AG Studio", "Linked coverage matrix, failure details and custom approval/payment/fulfillment comparison widgets", "Click a rule to filter events and rerun a case. Views cannot change verdicts or grant authority."],
       ["APIMatic", "Use PayPal Context Plugin while implementing the typed adapter and handling documented errors", "Preserve a real development example and resulting tests. No invented runtime firewall role."],
       ["Astropods", "Deploy the bounded scenario-proposal stage with versioned prompts and traces", "Show invocation, validated output and generated case. No payment secret or unrestricted tool execution."],
       ["Bryntum", "Interactive local event schedule for worker, browser and normalized inbox lanes", "A drag changes a legal schedule and a test outcome. Backend enforces dependencies; remote clocks remain outside control."],
       ["Channel3", "Generate realistic product-variant fixtures and coverage obligations for the merchant test storefront", "Actual API response influences a case such as same-total variant drift. Catalogues do not authorize retailer payments."]
      ], blocks=[
       ("The weak fit that must be acknowledged", "Channel3 is less fundamental here than in Assembly. To earn its place, the product must help a merchant generate test coverage from real variant structure, not fetch a decorative product card. Use IDs and permitted metadata to create explicitly synthetic seller offers. If a small manually authored fixture pack performs equally well, its incremental value is limited."),
       ("A second integration risk", "Bryntum becomes substantial only when editing a schedule changes execution. A passive timeline duplicates the log viewer. Keep the scheduler domain small enough to implement in two days, and make impossible schedules visibly invalid. Do not add a general distributed simulation language solely to justify a component.")
      ], refs=["S15","S16","S17","S18","S19"]),
 dict(section="Sponsor design 2 / 2", title="Finish the workflow without duplicating control", lead="The remaining tools support evidence acquisition, retrieval, verification, hosting and approved handoff.",
      table=[
       ["Tool", "Substantial proposed contribution", "Evidence and boundary"],
       ["Elastic", "Retrieve relevant redacted failures and group similar symptoms by rule/operation", "Query changes scenario context or investigation. Postgres remains authoritative; report baseline search comparisons."],
       ["Kernel", "Run owned storefront browser journeys and capture session evidence", "Show a browser-to-backend defect and linked session. Recordings are observational; they are not deterministic replay."],
       ["Postman", "Run the baseline API suite and export regression calls/assertions from the reduced case", "Independent rerun fails on the buggy version and passes after correction. Browser/scheduler steps stay in a companion runner."],
       ["Render", "Host API, PostgreSQL and worker with persistent run/checkpoint recovery", "Judge can run a case; restart resumes visibly. Use hosting meaningfully without adding redundant workflow engines."],
       ["Zapier", "Create an approved issue in a connected tracker containing a redacted reproducer", "Actual remote issue ID and readable artifact. Ambiguous creation is reconciled, not blindly retried."]
      ], blocks=[
       ("Removal tests", "For each sponsor, record the lost user capability or engineering evidence when removed. Elastic and Channel3 may be replaceable with simpler local implementations; that is an honest trade-off. Sponsor value is judged by a working contribution and usefulness, not by claiming the vendor is indispensable."),
       ("Complexity budget", "Astropods proposes scenarios; the Render-hosted domain worker owns runs; Zapier performs one approved downstream action. Kernel supplies browser evidence; Postman verifies API behavior. They share IDs but not competing state machines. No payment waits for a tracker write or a search index refresh."),
       ("Access and licensing", "Verify account credentials, plan features, commercial component distribution and credit expiry early. Maintain judge access through December 15. A 14-day trial started October 26 can expire before submission; a 45-day trial can expire before judging finishes. Do not promise an extension before it is confirmed.")
      ], refs=["S01","S20","S21","S22","S23","S24"]),
 dict(section="Implementation trade-offs", title="Favor a working engine over a language showcase", lead="A technical judge can inspect correctness and trade-offs. Extra languages without measurable benefit dilute the contribution.",
      blocks=[
       ("Recommended stack", "Python with FastAPI, typed schemas, AsyncIO and PostgreSQL for the control plane and initial runner; TypeScript for the interface. Start the reducer as a pure Python library. The schema is the boundary between model proposals and allowed actions. Use Docker for repeatable local setup and a small deployment topology."),
       ("When Rust earns a place", "A Rust trace validator or reducer could provide a compact independently packaged checking core, or native/Wasm reuse. First measure reduction CPU time and serialization overhead. Keep it pure, with no provider credentials. If remote calls and browser waits dominate, rewriting a fast local function will barely change end-to-end latency."),
       ("Bound the search", "For n legal steps, candidate schedules can grow rapidly even before fault choices are added. Use dependency pruning, one fault per initial scenario, a finite step vocabulary and a strict run budget. Minimize in the local model first; perform a small number of selected live confirmations. Avoid high-rate fuzzing of PayPal or third-party sites."),
       ("Cost model", "Cost per investigation equals model calls plus browser-session minutes plus runner/DB/search allocation plus storage and any priced actions. Record provider usage rather than inventing dollar estimates. Report live sandbox calls separately from local test steps. A cheap local reducer cannot compensate for an unbounded AI or browser loop."),
       ("Observability", "Track accepted/rejected scenarios, queue depth, unresolved operations, error class, provider call count, model tokens, reduction attempts, distinct failure signatures and artifact completeness. Use structured logs and one trace ID. Exclude secrets and avoid collecting unnecessary buyer identity."),
       ("Trade-off to accept", "A deliberately small scenario language limits coverage but improves explainability and replay. That is appropriate for a two-person hackathon. A broad autonomous testing agent that cannot explain or reproduce its findings is the less credible product.")
      ], refs=["S04","S09","S10","S23"]),
 dict(section="Evaluation and actual evidence", title="A tiny kernel works; the product hypothesis is untested", lead="One local experiment was executed while preparing this report. Its narrow scope matters more than its passing assertions.",
      table=[
       ["Executed synthetic experiment", "Observed result"],
       ["Authored scenario", "14 steps; duplicate normalized event causes duplicate fulfillment"],
       ["Greedy deletion reducer", "6-step failing trace after 41 candidate checks"],
       ["Independent history oracle", "2 fulfillment effects in buggy model; 1 in corrected model"],
       ["Replay", "10 identical local executions; every single-step deletion loses legality or the same violation"],
       ["Not executed", "AI discovery, PayPal calls, real concurrency, browser flows or any sponsor integration"]
      ], blocks=[
       ("Interpretation", "The experiment verifies only an authored in-memory model, an independent duplicate-fulfillment check and a simple reducer. Its correction uses an in-memory set, which is neither durable nor concurrency safe. It does not establish discovery, novelty, saved money, production reliability or advantage over a baseline. The script and exact result are embedded in this PDF."),
       ("Proposed comparative study", "Create 18 development fixtures and 12 held-out fixtures across six failure families, plus six clean controls. This is a proposed workload, not a result or power calculation. Hold out combinations and application variants; forbid the model from reading hidden defects. Use equal execution budgets and five recorded proposal seeds per condition."),
       ("Metrics and decision rule", "Count distinct independently verified defect signatures, not error messages. Report valid-scenario rate, false alarms on controls, inconclusive runs, reproduction rate, time to first reproducer and full cost. Compare templates, random legal schedules and AI proposals. A practical go/no-go target is at least two held-out defects missed by the strong baseline, with no unexplained clean-control failures and an independently repeatable export. This threshold is a team decision, not statistical proof.")
      ], refs=["S10","S12","S13"]),
 dict(section="Demo and judging", title="Show one failure so clearly that the mechanism matters", lead="Target a 2 minute 50 second video. The proposed sequence is a script to implement, not footage or results that already exist.",
      table=[
       ["Time", "On-screen action", "Claim supported"],
       ["0:00-0:20", "One approved purchase, one intended shipment; ordinary smoke tests pass", "A precise merchant problem and baseline limitation"],
       ["0:20-0:45", "AI proposes a legal response-loss/event-redelivery scenario", "AI contributes a scenario; reviewed rule is visible"],
       ["0:45-1:15", "Real sandbox capture, local fault, duplicated merchant fulfillment commitment", "PayPal evidence plus a clearly identified integration defect"],
       ["1:15-1:40", "Reduce the trace and move one local event; highlight the violated rule", "Reproduction and causal inspection, not only explanation"],
       ["1:40-2:15", "Apply the reviewed fix; rerun; export and execute regression", "Correction against the same contract"],
       ["2:15-2:50", "Judge changes an input; show new run, limits and approved issue handoff", "Interactive product, honest scope and useful follow-through"]
      ], blocks=[
       ("The five-criterion case", "Implementation: real execution, oracle and reducer. Design: one understandable investigation. Impact: developer reproduction time and defect coverage. Innovation: payment-specific evidence and a demonstrated advantage. Presentation: a visible before/after story. None is earned by a stack diagram alone."),
       ("Avoid staged certainty", "Call seeded bugs seeded. Do not label a prepared patch AI-discovered. Label condensed waits and recorded segments. Maintain a genuine interactive judge path with fresh runs. If the sandbox is unavailable, show the outage and a clearly marked recorded example; never pass a replay off as a live capture."),
       ("What belongs outside the video", "Put all ten sponsor roles, API documentation, complete benchmarks, licenses and setup instructions in the repository and submission. Ten equal sponsor tours would consume the story. Include a bounded judge control that changes a fault schedule or product variant.")
      ], refs=["S01","S03","S06"]),
 dict(section="Delivery plan", title="Use the remaining calendar to falsify the idea early", lead="Plan from October 26 to the November 12, 2026 noon Pacific deadline. The schedule assumes two available developers; actual hours and current implementation maturity are unverified.",
      table=[
       ["Dates", "Developer A", "Developer B", "Exit evidence"],
       ["Oct 26-28", "Sandbox lifecycle, durable intents and two fault hooks", "Oracle, local reducer, baseline tests and sponsor access", "One real defect, replay and correction; decide whether to switch"],
       ["Oct 29-31", "Owned storefront, Kernel journey and live confirmation", "Astropods proposal stage, schemas and frozen fixtures", "AI case reaches a meaningful rule under bounded execution"],
       ["Nov 1-3", "AG Studio evidence views and Bryntum schedule editing", "Channel3 fixture generator and Elastic retrieval", "Every runtime integration has a removal test"],
       ["Nov 4-6", "Render recovery, credentials and judge flow", "Postman export, approved Zapier handoff, held-out runs", "Runnable package and honest comparison results"],
       ["Nov 7-9", "Failure handling and UX fixes", "Independent reruns, docs and licensing review", "Feature freeze; no unexplained critical failures"],
       ["Nov 10-12", "Demo recording and hosted smoke checks", "Submission, public license and setup verification", "Submit with buffer and retain access through judging"]
      ], blocks=[
       ("48-hour gate", "Do not spend the remaining schedule on the new direction without a genuine sandbox trace, independent violation, reduced reproducer and corrected rerun. Confirm Astropods service access and the required sponsor accounts in parallel. The local toy experiment on page 16 does not satisfy this gate."),
       ("Second gate", "By November 6, require a credible AI advantage and meaningful use of all ten tools. If Channel3 or Bryntum remains ceremonial, this concept has not met the user's constraint. Return to Assembly only if its feasibility and implementation status justify the remaining time; do not assume a pivot is free."),
       ("Scope cuts", "Exclude multi-provider support, arbitrary merchant onboarding, automatic production patches, generalized model checking and extra systems languages. Keep necessary recovery and truthful evidence even when reducing scope.")
      ], refs=["S01","S15","S16","S17","S18","S19","S20","S21","S22","S23","S24"]),
 dict(section="Adoption and final decision", title="Pitch a developer pilot; earn broader deployment", lead="A credible path to PayPal use begins outside the live money path. The prototype should prove that developers can find and repair integration defects more effectively.",
      blocks=[
       ("First potential adopter", "A PayPal developer-experience or merchant-integration team could evaluate a sandbox starter kit and a reproducible failure library. This is a proposed audience, not a statement of internal demand or agreement. Offer an open-source harness, a small adapter, reviewed example contracts and redacted evidence packages."),
       ("Pilot measurement", "Recruit a small number of consenting integration teams and test their owned staging applications. Measure time to obtain a valid reproducer, independently confirmed additional defects, onboarding effort, false alarms and maintainer usefulness. Compare with their existing workflow. Define the unit as a defect or investigation, not a count of log errors."),
       ("Conditions for broader use", "Support versioned PayPal API contracts, tenancy isolation, secrets handling, regional data requirements, retention, maintained adapters and controlled test traffic. Establish what is uploaded, who can see it and how a result is reproduced without exposing customer data. Production testing would require separate authorization and engineering."),
       ("Material limitations", "An incorrect oracle can accuse correct code. A synthetic payment model can disagree with PayPal. Faults can be overfitted to our fixtures. Browser steps can be flaky. Reduction can be expensive. Sandbox correctness does not establish production readiness. AI-generated coverage does not prove the absence of untested failures."),
       ("My decision", "Counterexample is the alternative I would test first for technical distinction and a plausible developer-tool pilot. I would not call it categorically stronger than Assembly today. Assembly wins on natural ten-tool breadth and customer clarity; Counterexample must earn the switch with the 48-hour gate and baseline comparison. If it passes those gates, I would choose it for this team's infrastructure strengths."),
       ("What cannot honestly be promised", "No research can certify first place against an unseen future field, universal judge enthusiasm, or immediate global adoption. The best controllable result is a complete, independently testable product with a specific advantage and an excellent three-minute explanation.")
      ], refs=["S01","S04","S05","S08","S09","S13"]),
 dict(section="References and reproducibility", title="Source register and evidence boundaries", lead="Sources retrieved on October 26, 2026. Links support published capabilities; architecture choices and evaluation targets are this report's proposals.", references=True)
]
