"""Authored analysis pages for the two PDF briefs.

Citations use source IDs resolved on the final reference page.
All project claims remain proposed or explicitly marked as research findings.
"""
from __future__ import annotations

def section(label, title, lead, blocks, note, sources, diagram=None):
    item = dict(label=label, title=title, lead=lead, blocks=blocks,
                note=note, sources=sources)
    if diagram:
        item["diagram"] = diagram
    return item

PAYGUARD = [
section("Executive judgment", "PayGuard's real question",
"Can an AI agent move money while preserving the authority a person actually gave it?",
[
{"head":"The original thesis","text":[
"The chat proposal places an intelligent layer between an agent and PayPal. It turns a request into explicit constraints, checks a proposed purchase, obtains exact approval, executes a sandbox transaction and verifies the result. That is a coherent safety workflow, especially when untrusted product content can influence a model.",
"The stronger problem is cross-stage consistency. The user request, selected merchant, product, amount, approval version, PayPal order and final capture must refer to the same commercial action. A payment can be technically successful while the agent exceeded its authority. Existing protocol research identifies this kind of mismatch as an important design concern [S08]."]},
{"head":"Decision for a two-person entry","text":[
"PayGuard can be a credible prototype if it demonstrates an actual unauthorized proposal blocked before payment, a changed offer requiring fresh consent, and an ambiguous capture reconciled without a second purchase. A dashboard of invented risk scores or a chatbot that says 'safe' would not establish the thesis.",
"Public project descriptions already overlap with generic payment firewalls and human-approval gates. Its first-prize case depends on a narrower, demonstrable contribution and a polished end-to-end experience [S09]."]}
],
"Treat winning potential as a conditional judgment. No defensible probability follows from a forecast of 30,000 participants.",["S01","S08","S09"]),
section("Problem statement", "The gap between intent and execution",
"A user describes a goal in natural language. An AI agent turns that goal into actions involving changing merchants, product pages, prices and payment state.",
[
{"head":"Target user and job","text":[
"Start with a consumer who delegates product selection but wants control over the resulting purchase. A second plausible buyer is a small merchant allowing an AI procurement assistant to prepare recurring orders. In both cases, the person needs confidence that the executed charge matches their conditions.",
"The original example is a laptop purchase with a 70,000-rupee ceiling and no accessories without asking. The exact amount, product category, currency and accessory rule are distinct constraints. 'Best laptop' remains a preference that requires interpretation; the ceiling and approval requirement are hard conditions."]},
{"head":"Observable failure","bullets":[
"An agent adds an accessory because the merchant page recommends it.",
"A variant changes after the user approves a different configuration.",
"A capture succeeds but its response is lost, and the agent retries as a new order.",
"A product page instructs the model to ignore the user's limit."
]},
{"text":["A strong prototype makes these failures visible and shows exactly which rule blocks or escalates each one. It does not claim to replace PayPal's own fraud controls."]}
],
"Scope the first build to one buyer, one controlled seller and a few deliberately chosen policy types.",["S01","S03"]),
section("Proposal fidelity", "What the initial PayGuard proposal said",
"The original concept in the user-pasted material is an AI payment-intent and execution safety layer.",
[
{"head":"Six-step flow in the supplied proposal","bullets":[
"Interpret natural-language intent as amount, product, currency and approval requirements.",
"Check authority and policy against spending, merchant and action rules.",
"Inspect duplicates, price changes, amount mismatches and prompt-injection attempts.",
"Present the exact purchase when approval is required.",
"Create and capture an approved PayPal Sandbox order.",
"Verify actual status and record the decision trail."
]},
{"head":"Core design choice","text":[
"The proposal explicitly puts the language model in a planning role. Deterministic code retains authority for permissions, state changes and payment execution. That remains the right core boundary.",
"This brief develops that same initial idea; it does not silently redefine PayGuard as a different product. The original wording is embedded as a separate UTF-8 attachment named original-user-payguard-proposal.txt because the supplied PDF file was not available at its given path."]
}
],
"Original concept is a proposal supplied in chat. The analysis that follows distinguishes documented capabilities from suggested architecture.",["S03","S04"]),
section("Business context", "A real payment problem, carefully bounded",
"PayPal reported $1,337 million of transaction losses in 2025 and $1,114 million in 2024. That is about a 20.0% increase.",
[
{"head":"What the disclosure establishes","text":[
"The SEC segment schedule reports those figures as transaction losses [S02]. They support the broader point that payment safety matters at PayPal's scale. They do not measure losses caused by AI agents, nor prove PayGuard would reduce the total by any amount.",
"The product opportunity is narrower: prevent unauthorized agent proposals, avoid accidental duplicate business orders and make an agent's payment outcome inspectable to a user and merchant. These are hypotheses until user studies and a prototype produce evidence."]},
{"head":"What to measure later","bullets":[
"Rate of unauthorized proposed payments blocked before PayPal is called.",
"False blocks on legitimate purchases in a held-out scenario set.",
"Duplicate application purchases under retries and concurrent requests.",
"Time and user effort needed to understand why a payment was blocked.",
"Accuracy of the final status shown against PayPal resource read-back."
]}
],
"Never use PayPal's total transaction loss figure as the addressable market for this prototype.",["S02"]),
section("Existing capabilities", "PayPal already covers important pieces",
"An entrant should build around the platform's current capabilities rather than imply they do not exist.",
[
{"head":"Documented platform surface","text":[
"PayPal publishes agent tools for payment and merchant operations [S03]. Its agent-commerce materials describe signed intent and payment mandates through AP2 [S04]. Orders v2 provides creation and approval; Payments v2 documents captures, voids and refunds [S05].",
"PayPal-Request-Id supports idempotent retries on applicable endpoints for the provider's retention period. It does not create a permanent exactly-once guarantee for an entire application workflow [S06]. Signed webhooks need verification and may be retried [S07]."]},
{"head":"Implication for uniqueness","text":[
"PayGuard should prove a specific gap at the junction of user instructions, product content, changing offers and trusted payment state. Public project descriptions for Warden and AGENT GATE already cover payment firewall or approval-gate language [S09]. Their public pages are evidence of concept overlap, not verified implementation quality.",
"The claim to test is whether PayGuard's versioned intent binding and state reconciliation provide a useful, observable difference."]
}
],
"Do not present agent checkout, human approval or signed mandates as inventions unique to PayGuard.",["S03","S04","S05","S06","S07","S09"]),
section("Threat model", "Four trust boundaries matter most",
"The person supplies authority. Product pages and merchant messages supply evidence. The model interprets. Only the payment service may execute.",
[
{"head":"Adversaries and accidents","bullets":[
"Merchant content tries to override the user's rules or promote another product.",
"A benign listing has incomplete or contradictory variant and price fields.",
"The agent applies an old approval after a material offer change.",
"A repeated tool call creates a second business order after a timeout.",
"A signed event arrives late or more than once, causing application state regression."
]},
{"head":"Required responses","text":[
"Separate instruction authority from retrieved content in both the data model and tool permissions. A suspicious page can be quoted as evidence; it cannot change the policy. Bind every approval to an exact version of the seller, item, variant, amount, currency and relevant terms.",
"An ambiguous provider response becomes a pending verification state. The service reads the provider resource and resolves the operation before it permits a new payment attempt. The user interface must show uncertainty truthfully."]
}
],
"The threat list is a design model for this prototype; it is not a claim that PayPal currently suffers these failures.",["S06","S07","S08"]),
section("Architecture", "Keep payment authority out of the model",
"A bounded intent compiler proposes structured data; a versioned policy service decides whether it may become a payment.",
[
{"head":"Service shape","text":[
"Use a Python/FastAPI service for APIs and durable workflow logic, PostgreSQL for intent versions, approvals and payment operations, and a small AI component for extraction and explanation. A single service with clear modules is preferable to several microservices for this deadline.",
"The model receives a capability-scoped read interface. It never holds PayPal credentials or arbitrary write tools. Only the payment module creates or captures a PayPal order. A separate verification routine reads trusted provider state and signed events. An audit projection supports the merchant and user views."]},
{"head":"Boundaries to diagram","text":[
"A chat or shopping agent can propose an intent. The policy engine validates it against durable user rules and a fresh offer. The person reviews a structured confirmation. The payment service executes a provider operation under a stable operation ID and records the outcome."]
}
],
"The boundary between planning and spending must be enforced by code and credentials, not only by prompt wording.",["S03","S05","S06"],["User rule","AI proposal","Policy check","Approval","PayPal + verify"]),
section("Data model", "A payment needs a versioned intent record",
"Loose natural-language memory is insufficient to decide whether a later charge matches an earlier approval.",
[
{"head":"Minimum durable records","bullets":[
"Principal, policy version, delegated scope, validity window and revocation status.",
"Intent version with product category, exact item/variant when known, seller, maximum and exact amount, currency and conditions.",
"Offer snapshot with retrieval time, source evidence and terms relevant to approval.",
"Approval record bound to one intent and offer version, with actor and expiry.",
"Payment operation with logical purchase ID, PayPal IDs, request ID, state and reconciliation timestamps."
]},
{"head":"Consistency rule","text":[
"One logical purchase ID links the accepted intent to provider orders. A material change creates a new intent or offer version and invalidates prior approval. Relational unique constraints protect the one-purchase invariant at the application layer.",
"Use integer minor units or exact decimal arithmetic with a currency exponent table. Keep product interpretation separate from monetary calculation. A policy decision has an explainable rule ID, not just a model confidence value."]
}
],
"Exact approval cannot survive a changed seller, amount or product variant without a review rule explicitly allowing that change.",["S05","S06"]),
section("Payment method", "Approval and provider status are separate facts",
"The demonstration must exercise actual sandbox order creation, buyer approval, capture and read-back.",
[
{"head":"Proposed lifecycle","text":[
"The server persists a pending logical operation before calling PayPal. It creates an order with the accepted amount and controlled merchant. The user follows PayPal's buyer approval flow. The server rechecks the approved offer and then captures through the documented endpoint [S05].",
"Capture success comes from the provider response or later trusted read-back, not a browser message. Failed, pending and unknown outcomes remain distinct. Refund and void are separate operations with their own IDs and final status. An authorization is not escrow."]},
{"head":"Operational constraints","bullets":[
"Keep credentials on the server and use sandbox accounts only.",
"Use a stable PayPal request ID when the specific endpoint supports it.",
"Never treat a timeout as evidence that no charge occurred.",
"Keep synthetic orders and genuine sandbox resources visibly distinct."
]}
],
"The exact account, country, funding method and endpoint permissions require a live sandbox spike.",["S05","S06","S07"]),
section("Failure handling", "Retries require a business-level decision",
"Provider idempotency helps, but duplicate prevention also depends on a durable application identity.",
[
{"head":"Ambiguous response example","text":[
"The capture request times out after PayPal commits it. The application should retain the operation as unresolved, retry or read with the same supported request ID when appropriate, and check the provider resource. It should not issue a new order with a new logical identity [S06].",
"A webhook can arrive after the response or be delivered repeatedly. Verify its signature against the raw body, deduplicate by event identity and apply guarded state transitions. PayPal documents retries and simulator limitations [S07]."]},
{"head":"Recovery design","text":[
"Use a transactional outbox for follow-up indexing and notifications. Every external side effect has an operation ID and recorded attempt. An operator-facing reconciliation view shows what is known, which source established it and what remains unresolved.",
"Test worker termination between database commit and provider call, between provider success and local commit, and during webhook handling. Finite successful tests establish only the cases executed."]
}
],
"A refund request, completed refund and renewed spending capacity are different states.",["S06","S07"]),
section("AI method", "Model uncertainty must be visible",
"AI adds value where user instructions and commercial content are irregular, but the model does not decide final authority.",
[
{"head":"Pipeline","text":[
"Parse the user's goal into a strict schema. Identify hard limits, preferences, exceptions and missing information. Extract product and offer claims with the exact passage or field used. Generate a purchase proposal with explicit assumptions. Independently validate every hard condition before payment.",
"When information is missing, ask a focused question or stop at a proposed purchase. The system can still explain its reason in ordinary language after the deterministic decision is recorded. Never let a model-generated explanation substitute for evidence."]},
{"head":"Evaluation cases","bullets":[
"Benign paraphrases of the same spending rule.",
"Conflicting currency or variant information.",
"Accessory upsell hidden in merchant text.",
"A prompt injection attempting to rewrite the user's approval requirement.",
"An offer change between proposal and execution."
]}
],
"Measure extraction accuracy and payment decisions separately; a persuasive explanation is not a correct transaction.",["S08","S10"]),
section("Security and privacy", "Least privilege is a product feature",
"Sensitive financial authority, merchant content and model context must remain distinct across the stack.",
[
{"head":"Concrete controls","bullets":[
"Authenticate the user; authorize every intent and approval against that identity.",
"Use scoped payment credentials only in the payment service.",
"Constrain browser and retrieval tools to permitted sources and bounded content.",
"Validate structured output, URL destinations, currency codes and amounts.",
"Protect webhook raw-body verification; redact secrets and payment data in logs.",
"Record revocation, policy edits, approvals, blocked attempts and reconciliations."
]},
{"head":"Limits","text":[
"A rule engine cannot confirm that a merchant's description is truthful, prevent all social engineering, or replace PayPal's existing fraud and dispute systems. It can enforce the user-granted constraints that it actually represents.",
"False-positive blocks can make the product unusable. The user needs a short, precise explanation and a route to revise the intent without letting a single untrusted page change authority."]
}
],
"Treat external text as task data. Instruction hierarchy must survive every retrieval and tool response.",["S07","S10"]),
section("Evaluation method", "Prove a safety gain against baselines",
"Winning claims need measured behavior on held-out cases, not numbers invented for the pitch.",
[
{"head":"Compare three systems","bullets":[
"A plain AI agent with direct PayPal tool access in a controlled test environment.",
"A deterministic form and rule workflow with no AI extraction.",
"PayGuard's AI extraction plus deterministic authority and verification."
]},
{"head":"Measures and test design","text":[
"Create labelled cases: valid purchases, budget overages, merchant substitutions, changed variants, injected instructions, stale approvals, simultaneous retries and unknown capture responses. Hold out paraphrases and unseen combinations. Run equivalent cases and report counts and denominators.",
"Measure unauthorized executions, valid purchases incorrectly blocked, approval comprehension, duplicate business orders, unresolved outcomes, latency and cost. A zero observed safety violation across a finite suite is an empirical result with a stated sample, not a universal guarantee.",
"Add a small number of target-user sessions. Observe whether people can understand and approve the precise charge. Do not infer demand from press coverage or total PayPal losses."]
}
],
"Publish fixtures, expected results and repeatable test commands in the repository.",["S01","S02","S08"]),
section("Grand-prize case", "PayGuard needs a sharper demonstration",
"Against a hypothetical 30,000 registrations, this concept cannot be assigned a credible probability of first place.",
[
{"head":"Strengths and weaknesses","text":[
"Strengths: an important payment boundary, clear AI plus PayPal coupling, measurable safety invariants and a high-stakes live sandbox flow. Weaknesses: generic guardrail language already appears in public projects, the strongest security claims need careful proof, and ten sponsor integrations can consume the schedule.",
"The contest's five criteria are equally weighted [S01]. A strong codebase alone will not win if judges cannot see the user problem, the forbidden purchase blocked and the approved purchase completed within three minutes. Sponsor count has no stated overall-prize score."]},
{"head":"All-ten-sponsor plan, if retained","text":[
"AG Studio shows the approval and audit view; APIMatic supplies development context; Astropods hosts the AI intent compiler; Bryntum shows expiring approvals and deadlines; Channel3 provides exact product variants; Elastic retrieves decision evidence; Kernel inspects permitted merchant pages; Postman runs lifecycle tests; Render hosts the API and database; Zapier sends an approved post-payment action. Each needs a visible proof of use.",
"Two-person plan: first prove a genuine sandbox lifecycle and one blocked policy case; next build durable state and recovery; then connect sponsor roles; finally run held-out tests, polish the interface and record the video. Keep the build accessible through December 15 judging [S01]."]
}
],
"First-prize thesis: demonstrate a precise failure PayPal tools alone do not solve for an agent, then prove the boundary end to end.",["S01","S09"])
]

ASSEMBLY = [
section("Executive judgment", "Assembly's first-prize thesis",
"Can an AI system turn a customer's desired outcome into a complete, evidence-backed purchase that will actually work as specified?",
[
{"head":"The proposal","text":[
"A buyer describes a capability, budget, existing equipment and deadline. Assembly extracts structured requirements, discovers candidate products, checks physical and logical dependencies, explains conflicts and unknowns, and takes the accepted offer through a genuine PayPal sandbox checkout.",
"The earlier chat named this as my strongest new proposal because its failure is legible: four microphones cannot simultaneously use an interface with only two microphone inputs. That one conflict makes AI interpretation, deterministic reasoning, product design and actual payment meaningful in a short demonstration."]},
{"head":"What is proved and unproved","text":[
"A prototype can prove internal consistency against the recorded facts and show its purchase lifecycle. It cannot prove a seller's claims are truthful, that every real device works as advertised, or that merchants will pay for the product. Technical configuration and user demand remain testable hypotheses.",
"The grand-prize case is conditional: demonstrate a surprising but correct conflict, source-backed explanation, targeted recalculation after a change and verified PayPal payment. A broad shopping assistant would dilute that point."]
}
],
"Keep the first release to one technical category, one controlled seller and one complete customer job.",["S01","S02","S03"]),
section("Problem statement", "People buy components to achieve outcomes",
"A customer wants a working setup, not a collection of individually attractive items.",
[
{"head":"Target user","text":[
"Start with a creator or small studio buying a recording system. The purchaser may know the intended number of speakers, available laptop, spending limit and recording date without knowing the signal-chain details. An online merchant can also use the product to reduce incompatible basket contents, but no reduction has yet been measured.",
"A product search system can find relevant microphones and interfaces. The difficult step is verifying that the chosen combination meets the customer's full requirement. The answer depends on quantities, interface capacity, connectors, power, software support, available adapters and installation time."]},
{"head":"A concrete wrong purchase","text":[
"Four microphones and a two-input interface can fit a price target while failing simultaneous four-person recording. A larger interface might require another cable or arrive after the event. A missing specification should remain an unknown, not an invented compatible fact.",
"The commercial hypothesis is fewer avoidable order mistakes and more confident complex purchases. Validate it with observed customer tasks rather than projecting savings from unrelated retail figures."]
}
],
"Outcome-level completion is the product promise; independent component rankings are only inputs.",["S02","S03"]),
section("Core demonstration", "A four-person recording kit",
"The demo scenario is illustrative. The $900 ceiling and any displayed supplier prices are test fixtures unless shown as actual retrieved offers.",
[
{"head":"Inputs and first proposal","text":[
"The user says: 'Build a four-person podcast setup under $900. I already have a laptop.' Assembly converts that into a goal requiring four simultaneous microphone channels, connection to the user's laptop, a complete set of dependent components and a total within the limit.",
"Channel3 returns product candidates, variants, offer prices and buy links where available. The system keeps each selected variant distinct. It does not infer hidden technical facts from product titles [S02]. The AI proposes candidate attributes with source evidence and uncertainty."]},
{"head":"The visible turn","text":[
"Assembly displays a plausible bundle and highlights that the chosen audio interface supports only two microphone inputs. The customer selects a replacement. The engine checks the new interface, required cables and schedule, then produces an updated exact offer.",
"The user changes one requirement, such as an earlier deadline or existing cable type. Only dependent checks and procurement steps are invalidated. The approved version is paid through a controlled PayPal sandbox merchant. The associated record shows which configuration was accepted."]
}
],
"The demo must clearly distinguish real Channel3 listings from controlled sandbox merchant offers.",["S02","S05"]),
section("Research method", "Use AI to acquire constraints; code checks them",
"Recent research supports investigating hybrid language-model and symbolic configuration, while leaving this product's impact unproved.",
[
{"head":"Relevant technical work","text":[
"Valerio and colleagues describe the challenge of industrial-grade configuration when probabilistic language models must fit explicit rules and manufacturing constraints [S03]. Bischof and colleagues study acquisition of constraints from stakeholders with different authority and show the need to explain conflicts [S04]. Both were reviewed through metadata and abstracts; their reported results were not reproduced for this brief.",
"This motivates a narrow architecture: an AI extractor maps requests and specifications into candidate facts; a typed ontology defines ports, quantities and capacities; a deterministic solver checks complete configurations. A separate verifier recomputes the final candidate's hard rules."]},
{"head":"Evidence discipline","bullets":[
"Record the product ID and exact selected variant.",
"Attach every hard product claim to its source field or page passage.",
"Mark missing data as unknown.",
"Distinguish customer facts from retailer assertions.",
"Expire or recheck time-sensitive price and availability before approval."
]}
],
"None of the cited papers proves that Assembly itself has product-market fit or global novelty.",["S02","S03","S04"]),
section("Existing products", "Where the novelty must be demonstrated",
"Product search, shopping agents and configurators already exist. Assembly needs a precise behavioral distinction.",
[
{"head":"Baseline capability","text":[
"Channel3 already supplies normalized product search, offers and variants [S02]. PayPal already supplies sandbox order and capture flows [S05]. Neurosymbolic product configuration exists as a research area [S03]. Combining these components alone does not establish an original project.",
"The proposed contribution is a buyer-facing, end-to-end 'working outcome' transaction: evidence-backed constraint acquisition, explicit unknowns, explanation of the conflicting set, propagation of a changed requirement and an approved payment bound to the accepted configuration."]},
{"head":"Overlap check still needed","text":[
"The first ideation pass was generated before the latest sponsor-document and paper search, which reduced anchoring on previous project descriptions. That sequence does not prove first-in-world novelty. A focused competitor audit should compare actual task behavior, not names or landing-page claims.",
"Novelty survives only if the configured outcome and its payment record can do something a conventional search/cart experience cannot reproduce with scripted filters."]
}
],
"Show an unscripted configuration change; a fixed two-input example alone can be copied by a simple rule.",["S02","S03","S05"]),
section("User experience", "Make missing facts and conflicts understandable",
"The buyer should see what will work, what fails and what cannot yet be established.",
[
{"head":"Primary flow","text":[
"Collect the requested capability and any existing equipment. Display a proposed system diagram beside an itemized product list. For each requirement, label it satisfied, contradicted or unknown with a short source-backed explanation. Show the smallest practical repair when a conflict appears.",
"The person can replace a component, adjust a budget or answer a missing question. The interface should update the configuration and timeline immediately while explaining which earlier decisions changed. Before checkout, show the exact merchant, items, variants, delivery assumptions, currency and amount."]},
{"head":"Failure and accessibility","text":[
"Never hide unknown compatibility behind a green success badge. A setup with unresolved laptop ports should request the model or input type. Keyboard and screen-reader users need the same conflict explanation and approval details as users of the diagram.",
"The product should expose assumptions in plain language, not force the user to read a solver trace. Expert users can expand the evidence and rule details."]
}
],
"Treat the customer as final authority on changed requirements and payment approval.",["S02"]),
section("System architecture", "One authoritative service, bounded AI components",
"Assembly's technical center is a domain engine that can independently check what AI proposes.",
[
{"head":"Proposed services","text":[
"Use a Python/FastAPI application on Render for authenticated workflow and payment APIs. PostgreSQL stores requirement versions, candidate facts, approvals, operation IDs and payment status. Elasticsearch holds searchable product evidence. An Astropods deployment runs the bounded extraction and clarification agent. The integration between the two must be authenticated and tested [S08].",
"Channel3 supplies structured discovery. Kernel captures permitted missing specification evidence. AG Studio presents comparative evidence; Bryntum presents schedule dependencies. Neither UI library determines payment authority. APIMatic informs development of the PayPal adapter; Postman runs executable tests. Zapier receives an approved, verified post-payment task [S09]."]},
{"head":"Control flow","text":[
"User input reaches AI extraction, then a typed validator and constraint solver. The resulting accepted configuration receives a version. The user approves that version and the controlled seller offer. The payment service creates and verifies a PayPal sandbox order. Background jobs drive indexing and downstream fulfillment after durable success."]
}
],
"Keep one domain and payment service with clear modules; ten sponsors do not justify ten agents.",["S02","S05","S08","S09"],["User goal","AI facts","Constraint check","Exact offer","PayPal state"]),
section("Typed product model", "Represent compatibility as checkable facts",
"An attractive description is not enough to prove a four-person setup works.",
[
{"head":"Minimum entities","bullets":[
"Requirement: capability, threshold, unit, hard-or-preferred flag, source and version.",
"Product variant: exact identity, merchant offer, observed price/currency, availability and evidence timestamp.",
"Port: direction, connector, protocol, quantity, power capability and supported rate when material.",
"Connection: source port, target port, cable or adapter and constraints.",
"System: selected components, external assets, fulfillment steps, total and unresolved facts."
]},
{"head":"Three-valued claims","text":[
"A fact may be supported, contradicted or unknown. A listing without the interface's channel count cannot satisfy a hard four-input rule. AI can search for another source or ask a human, but the solver must not convert missing data into a pass.",
"Keep exact source spans and a rule version on every computed result. Avoid a universal electronics ontology. Define only the attributes required by the one demo domain, then expand when real cases force it."]
}
],
"The semantic model is narrow by design: precision in one category matters more than fabricated generality.",["S02","S03","S04"]),
section("Constraint engine", "Find feasible configurations and explain failures",
"The solver chooses from finite candidate variants and checks every hard requirement before any payment.",
[
{"head":"Algorithm for the first build","text":[
"Use typed filtering and explicit finite-domain constraints for microphone channels, connector compatibility, quantities, budget and schedule. A solver such as Z3 or OR-Tools is warranted when substitutions and interdependent choices exceed simple pairwise filters; otherwise a deterministic search is easier to audit.",
"When no configuration meets the hard requirements, compute a small conflicting set and translate it into a buyer-facing explanation. 'Four simultaneous microphones require four suitable inputs; selected interface exposes two' is more actionable than 'no results'."]},
{"head":"Alternative selection","text":[
"Among feasible sets, rank cost and customer preferences separately. A lower total cannot excuse a failed hard rule. If product evidence is unknown, disclose the unresolved claim and present a request for confirmation or an alternative with supported facts.",
"A final independent checker recalculates the accepted configuration from stored facts. This catches planner or solver integration bugs before checkout."]
}
],
"Do not promise a globally optimal purchase across the entire internet; optimize the bounded candidate set actually evaluated.",["S03","S04"]),
section("Evidence pipeline", "Catalogue data needs provenance and freshness",
"Channel3 supplies a useful product schema, but category-specific technical attributes can be absent or ambiguous.",
[
{"head":"Extraction method","text":[
"Retrieve candidates and exact variants through Channel3. Normalize supported structured attributes and offer fields first [S02]. Only then use AI to extract additional claims from descriptions or permitted source pages. Kernel can open a manufacturer's page for a missing port specification and retain the observed passage [S10].",
"Store product ID, selected variant, merchant domain, observed price, currency, availability and retrieval time. Each derived fact points back to a field or passage and an extraction version. Elastic can retrieve relevant evidence, while PostgreSQL holds the accepted decision."]},
{"head":"Failure modes","text":[
"A retailer may change the listing after the proposal. A product title can refer to a different variant. A page can instruct the model to ignore the user's budget. Treat page content as untrusted evidence. Before approval, refresh material offer details and require a new decision if the version changes.",
"An observed page does not certify manufacturer truth. Human confirmation remains necessary for high-impact missing specifications."]
}
],
"PayPal cannot collect money on behalf of arbitrary Channel3 retailers merely because a listing provides a buy link.",["S02","S10"]),
section("Payment architecture", "Bind purchase to the checked configuration",
"Payment must follow the configuration the customer accepted, not a loosely similar later cart.",
[
{"head":"Controlled sandbox checkout","text":[
"Use one controlled sandbox merchant. Create an Orders v2 resource for the approved offer, obtain the buyer's PayPal approval and capture through the server. Read the order or capture resource to verify status [S05]. Each purchase record retains a hash or version reference to the accepted configuration and offer.",
"Channel3 prices and links support discovery. In the prototype, the actual payable merchant offer is a labelled simulation. A real multi-retailer deployment would require merchant participation, appropriate onboarding and seller agreements."]},
{"head":"State and arithmetic","bullets":[
"Keep exact currency amounts in minor units or decimal types.",
"Persist the logical purchase ID before calling PayPal.",
"Recheck configuration validity and offer freshness before payment.",
"Record provider IDs and unknown outcomes durably.",
"Never call a browser approval screen evidence of successful capture."
]}
],
"The product's key demonstration is a genuine provider payment for the exact accepted version.",["S05","S06"]),
section("Failures and security", "A good configuration can still fail in execution",
"A payment timeout, missing webhook or changed offer must not turn the buyer's accepted plan into an unintended order.",
[
{"head":"Recovery rules","text":[
"Use stable logical purchase IDs and endpoint-specific PayPal request IDs. The application must prevent a second business order when a response is lost. Provider idempotency has bounded support; reconcile uncertain operations with trusted resource reads [S06].",
"Verify webhook signatures using the raw body, deduplicate events and guard state transitions. Simulator events are development tests, not proof of a real paid order [S07]. Downstream Zapier actions should run after verified capture and use an action ID to prevent duplicate tasks."]},
{"head":"AI and browser limits","text":[
"The extraction agent gets read-only evidence tools. Product pages cannot issue instructions to the payment module. Browser URLs are allowlisted; text size and fetch time are bounded. The PayPal credential stays in the payment service, not the model or browser.",
"An unavailable AI model should stop new extraction and leave existing payment state inspectable. An unavailable search index cannot override an accepted PostgreSQL record."]
}
],
"Consistency and recoverability matter more than a visually successful payment animation.",["S06","S07","S10"]),
section("Evaluation method", "Measure compatibility, evidence and payment separately",
"Use a labelled benchmark and a working payment flow. Do not compress all quality into one invented score.",
[
{"head":"Three baselines","bullets":[
"An AI model asked directly to recommend a cart.",
"A small hand-curated configurator with fixed filters.",
"Assembly's evidence extraction plus typed checker."
]},
{"head":"Case design and metrics","text":[
"Build cases labelled feasible, incompatible and unknown. Hold out product variants and paraphrases. Include changed budget, missing laptop port information, wrong interface capacity, late delivery and a price change after approval. Report case counts, provenance and adjudication method.",
"Measure false-feasible decisions, unnecessary rejection, correct unknowns, extraction field accuracy, source support, customer task completion, latency and cost. Test checkout separately for genuine sandbox capture, duplicate prevention and recovery after ambiguous responses. User observation should test whether a non-expert understands and trusts the explanation."]},
{"head":"Competitive evidence","text":[
"Compare against a catalog search and straightforward configuration form under equal task conditions. If Assembly only catches an example hardcoded into those baselines, its claimed advantage has not been demonstrated."]
}
],
"A valid solver result is limited to the product facts represented; separate that from physical-world correctness.",["S02","S03","S04","S05"]),
section("Grand-prize case", "Concentrate the demo around one changed decision",
"A first-place entry must show complete implementation, design, impact, originality and presentation. The rules weight those five criteria equally.",
[
{"head":"Strengths and limitations","text":[
"Assembly has a clear visual conflict, a substantial technical mechanism and a natural PayPal payment outcome. It gives AG Studio a real evidence workspace and Bryntum a schedule that can change the decision. Its weakest assumptions are catalogue specification completeness, merchant payment authority beyond the controlled seller, and unmeasured customer demand.",
"Against a scenario of 30,000 registrations, there is no reliable denominator of eligible projects or distribution of judge scores. The build can improve its position by proving the technical core live, keeping the experience polished and publishing held-out results. No award is guaranteed [S01]."]},
{"head":"All ten and the schedule","text":[
"Use AG Studio for evidence and conflict widgets; APIMatic for PayPal coding context; Astropods for extraction; Bryntum for dependent tasks; Channel3 for product data; Elastic for evidence retrieval; Kernel for permitted page inspection; Postman for API regression; Render for services and workflows; Zapier for approved post-payment setup. Each role needs a real recorded call, UI action or test artifact [S09].",
"First prove the hard conflict and genuine sandbox capture. Then persist versions and failure recovery. Integrate sponsors around that spine. Leave time for user tests and a video under three minutes. The submitted build must remain available through December 15 judging [S01]."]
}
],
"Best pitch: four-person setup, two-input conflict, verified replacement, changed constraint, exact PayPal purchase.",["S01","S09"])
]


