"""Build the hackathon opportunity bank and inspectable planning assessment."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AS_OF = "2026-10-23"

# Each domain contains four distinct product hypotheses, not established gaps.
# Common fields state the likely integration and the evidence still required.
DOMAINS = [
    ("Agent authority", "Orders, Payments, restricted MCP tools", "Compile user intent into a reviewed policy", "Existing mandates and payment firewalls create heavy overlap", ["S04", "S05", "S08", "S13"], [
        ("Exact purchase consent", "Bind approval to merchant, items, currency, total and expiry; reject a changed cart."),
        ("Delegation chain inspector", "Show which human or service delegated each capability; refuse scope amplification."),
        ("Revocation-aware agent checkout", "Cancel unused local authority across running jobs when a user revokes a mission."),
        ("Commercial terms diff", "Identify changed delivery, cancellation or renewal terms before asking for fresh approval."),
    ]),
    ("Agent coordination", "Orders, authorizations, captures, refunds and webhooks", "Construct dependencies and propose recovery alternatives", "Saga middleware already exists; distinguish business-goal recovery", ["S11", "S19", "S20", "S21"], [
        ("RecoverPlan", "Repair a partially completed multi-purchase mission within budget, deadline and accepted-loss limits."),
        ("Shared mission commitment ledger", "Reserve one organization budget across several agents before any creates an obligation."),
        ("Irreversible action planner", "Sequence dependent purchases so irreversible commitments happen only when prerequisites hold."),
        ("Mission cancellation desk", "Coordinate merchant-permitted cancellation, void and refund requests; keep unresolved cases visible."),
    ]),
    ("Paid AI services", "Invoicing, Orders, Subscriptions; optional separate PYUSD testnet", "Select tools and map task outcomes to metered service evidence", "Existing machine-payment and usage-billing products; do not imply cost-free micropayments", ["S04", "S23", "S29"], [
        ("ToolMeter", "Aggregate signed service-usage records into an approved PayPal invoice with spending caps."),
        ("Data quality purchase contract", "Buy a dataset subject to explicit schema and coverage checks, with a human acceptance gate."),
        ("Compute run acceptance", "Link an inference or training run receipt to a payment and verify agreed output checks."),
        ("Paid API substitution planner", "Choose a replacement paid API after an outage while preserving task quality and remaining budget."),
    ]),
    ("Payment reliability", "Orders, Payments, Request-Id, webhooks", "Investigate evidence and propose typed recovery actions", "Ordinary idempotency is existing PayPal functionality, not an invention", ["S10", "S11", "S12", "S18"], [
        ("Unknown capture investigator", "Resolve a lost capture response before deciding whether any retry is safe."),
        ("Fulfilment gap repair", "Find paid-but-unfulfilled orders and resume the merchant workflow without charging again."),
        ("Webhook incident desk", "Explain missing, duplicated or reordered events using verified records and replay-safe state."),
        ("Refund completion watcher", "Distinguish requested, pending, failed and completed refunds and propose the next permitted step."),
    ]),
    ("Developer infrastructure", "Sandbox APIs, OpenAPI, Postman, restricted MCP", "Generate tests, identify integration misuse and summarize counterexamples", "APIMatic, official tooling and public adversarial harnesses already cover parts", ["S03", "S04", "S06", "S14"], [
        ("Payment workflow conformance lab", "Compare a merchant integration against a pinned lifecycle contract and reproducible traces."),
        ("AI payment regression testing", "Replay held-out semantic and stateful cases when a model, prompt or tool schema changes."),
        ("Migration evidence assistant", "Map legacy payment behavior to Orders v2 and validate approval, capture and webhook semantics."),
        ("Minimal failing payment trace", "Reduce an integration incident to the smallest reproducible sandbox sequence."),
    ]),
    ("Merchant fraud", "Orders, shipment tracking, disputes, merchant order data", "Extract evidence and rank cases for review", "No representative fraud labels; cannot claim production fraud detection", ["S04", "S07", "S15"], [
        ("Order review copilot", "Explain unusual order and delivery facts without making a definitive fraud accusation."),
        ("Supplier payment change review", "Compare a claimed payee change with trusted supplier records and require independent confirmation."),
        ("Refund abuse case linker", "Link repeated refund narratives to existing orders while preserving legitimate customer appeals."),
        ("Account takeover response assistant", "Triage merchant-provided suspicious activity and prepare account-recovery steps, without platform privileges."),
    ]),
    ("Consumer scams", "App-controlled checkout or invoice review", "Analyze social-engineering language and surface evidence", "Cannot intercept arbitrary PayPal consumer transfers; sensitive false positives", ["S04", "S13"], [
        ("Invoice scam explainer", "Explain suspicious invoice context before a user opens the payment flow."),
        ("Trusted contact approval", "Route an app-originated high-risk proposed payment to a trusted reviewer without exposing credentials."),
        ("Impersonation payment review", "Compare a claimed business identity with independently supplied trusted details."),
        ("Pressure-resistant checkout", "Slow coercive payment requests and show the user the actual recipient and obligation."),
    ]),
    ("Disputes", "Disputes API, Orders, tracking", "Build cited evidence timelines and identify missing documents", "Braintree automation, Chargeflow and multiple projects already exist", ["S07", "S15", "S16"], [
        ("Evidence completeness desk", "Identify missing receipts, tracking and customer communications before a response is drafted."),
        ("Agent authorization evidence pack", "Connect what the buyer approved to what the agent ordered and what the merchant delivered."),
        ("Dispute deadline workflow", "Prioritize cases by confirmed deadline and available evidence instead of fabricated win probability."),
        ("Fair resolution planner", "Compare contesting, replacement and voluntary refund using policy and case facts."),
    ]),
    ("Returns and refunds", "Payments refunds, tracking, merchant catalogue", "Interpret return reasons and propose eligible replacements", "Crowded returns market; do not promise instant final refunds or force merchant refunds", ["S13", "S17", "S19"], [
        ("ReturnRouter", "Compare replacement, partial refund and return shipping while preserving the customer's stated preference."),
        ("Repair before return", "Offer a documented troubleshooting or repair path with an approved partial refund when appropriate."),
        ("Consolidated return planner", "Combine eligible returns into fewer shipments and show payment adjustments explicitly."),
        ("Refund promise reconciliation", "Compare support commitments with verified refund amounts, currencies and completion status."),
    ]),
    ("Accounts receivable", "Invoicing, Orders, webhooks", "Extract scope and explain receivables", "Invoicing agents and contract-to-cash projects already exist", ["S04", "S09"], [
        ("Milestone invoice assistant", "Generate reviewable invoices from explicit agreed milestones and accepted work."),
        ("Scope change billing", "Compare an agreed brief with requested changes and price approved extras."),
        ("Receivables prioritizer", "Rank overdue invoices by actionable evidence and prepare human-approved reminders."),
        ("Short payment resolver", "Explain why a payment does not satisfy an invoice, including fees, credits and agreed deductions."),
    ]),
    ("Procurement and accounts payable", "Orders or sandbox Payouts after access validation", "Read purchase orders, delivery records and invoices", "Three-way-match and cash-cap demos already exist; merchant access is required", ["S04", "S22"], [
        ("Three-way match payment desk", "Compare a purchase order, delivery note and supplier invoice before payment."),
        ("Supplier quote normalizer", "Compare package sizes, tax, delivery and payment terms before selecting a supplier."),
        ("Discount deadline planner", "Select approved early payments without consuming money needed for earlier obligations."),
        ("Substitution acceptance", "Detect changed supplier products or quantities and obtain approval before adjusted payment."),
    ]),
    ("Treasury and working capital", "PayPal reports, captures, refunds; optional Payouts", "Extract obligations and propose cash-allocation plans", "Fresh balance and reserve visibility must be verified; never imply control over PayPal reserves", ["S24", "S25", "S26"], [
        ("ReservePilot", "Keep incoming funds, provider holds, internal buffers, refunds and committed supplier payments separate."),
        ("Refund shock simulator", "Stress-test which approved payments remain affordable after a declared refund scenario."),
        ("Obligation deadline calendar", "Explain upcoming cash obligations and propose approved deferrals without predicting guaranteed inflows."),
        ("Capital lockup optimizer", "Sequence expiring authorizations and cancellable orders to reduce unnecessary committed capital."),
    ]),
    ("Cross-border and FX", "Multi-currency Orders, Invoicing; FXaaS only if enabled", "Read contracts and explain currency and fee obligations", "FXaaS requires eligibility and contract onboarding; quotes are not trading APIs", ["S27", "S28", "S30"], [
        ("ClearFX", "Trace the invoice currency, payer quote, merchant receivable and refund currency across one payment."),
        ("Quote expiry consent", "Detect an expired quote and request new approval when the economic terms change."),
        ("Net receipt agreement", "Explain who bears conversion and fee differences before parties agree a payable amount."),
        ("Cross-currency refund desk", "Reconcile original and refunded amounts without inventing an executable exchange rate."),
    ]),
    ("Accounting and reconciliation", "Transaction Search, balance reports, Orders and Payments", "Map ambiguous records and explain deterministic findings", "PayPal accounting sync and reconciliation projects exist; reporting can lag", ["S18", "S25", "S31"], [
        ("Invoice to settlement bridge", "Match invoice, capture, fee, refund and payout records with source citations."),
        ("Accounting exception inbox", "Cluster unmatched records and request the specific evidence needed to resolve each."),
        ("Duplicate expense review", "Link repeated receipts and payments before a bookkeeper approves corrections."),
        ("Close checklist assistant", "Prepare a reviewable period-close checklist without silently posting journals."),
    ]),
    ("Subscriptions and recurring payments", "Merchant-owned Subscriptions, catalogue and webhooks", "Read plan changes and explain renewal obligations", "Cannot manage every consumer subscription through merchant credentials", ["S32", "S33"], [
        ("Renewal change consent", "Highlight material renewal terms or price changes before user approval."),
        ("Subscription migration desk", "Plan a permitted same-product plan transition and verify resulting subscription state."),
        ("Failed renewal recovery", "Explain supported recovery choices without bypassing funding-source or consent requirements."),
        ("Entitlement payment reconciliation", "Detect where access and verified subscription state disagree."),
    ]),
    ("Marketplaces and gig work", "Orders, Invoicing, Payouts; multiparty approval where needed", "Match work, evidence and payment obligations", "Authorizations are not regulated escrow; onboarding and split settlement may be gated", ["S03", "S19", "S34"], [
        ("Task acceptance marketplace", "Tie an agreed acceptance checklist to a reviewed payment decision."),
        ("Marketplace exception resolver", "Explain mismatches between buyer payments, seller balances and platform obligations."),
        ("Gig earnings statement", "Turn completed-task and payment records into a cited statement with missing payments visible."),
        ("Royalty allocation review", "Extract an agreed revenue-share contract and validate allocations before payouts."),
    ]),
    ("Identity and financial operations", "Merchant onboarding workflows and app permissions", "Extract documents and explain missing evidence", "No privileged KYC, AML or sanctions determination; sensitive data and regional scope", ["S03", "S04"], [
        ("Onboarding completeness assistant", "Identify missing business documents and prepare a human-reviewed application packet."),
        ("Entity record reconciliation", "Link merchant-supplied entity records while requiring confirmation of uncertain matches."),
        ("Payment purpose evidence", "Attach a minimized purpose and source-document trail to an app payment."),
        ("Permission audit assistant", "Explain what each integration can do and recommend narrower app capabilities."),
    ]),
    ("Accessibility and inclusion", "Accessible Orders or Invoicing checkout", "Translate and explain terms through supported interaction modes", "Voice-first shopping projects exist; evaluate comprehension and accessibility with users", ["S02", "S04", "S08"], [
        ("Screen-reader payment review", "Make recipient, amount, fees and approval state easy to verify without sight."),
        ("Low-literacy merchant assistant", "Explain invoices and refunds in plain language with confirmation of critical values."),
        ("Multilingual invoice acceptance", "Translate descriptions while preserving original currency, price and contractual terms."),
        ("Caregiver-supported purchase", "Support explicit roles and consent for app purchases without sharing account passwords."),
    ]),
    ("Consumer financial organization", "App payments, user-provided exports and subscriptions", "Categorize records and explain commitments", "No arbitrary consumer-account scraping or universal read access", ["S04", "S25", "S32"], [
        ("Commitment budget", "Include already approved obligations in a user's view of money remaining."),
        ("Receipt bill splitting", "Read a receipt and propose shares, followed by separately approved supported payments."),
        ("Purchase affordability explainer", "Show the consequence of a proposed purchase under explicit user-provided budget assumptions."),
        ("Family purchase accountability", "Show who approved and received each app purchase under explicit family permissions."),
    ]),
    ("Commerce discovery", "Channel3 or bounded catalogue plus Orders", "Find relevant products and explain constraint matches", "Shopping is heavily represented; catalogue data is untrusted and prices need revalidation", ["S03", "S05", "S08"], [
        ("Compatibility-aware bundle", "Buy components only after checking their documented compatibility and complete bundle cost."),
        ("Repair-versus-replace purchase", "Compare a supported repair item with a replacement using transparent assumptions."),
        ("Landed-cost shopping", "Compare item, shipping and supplied taxes rather than ranking sticker price alone."),
        ("Accessible local merchant checkout", "Help a small merchant publish a usable catalogue and app-controlled checkout."),
    ]),
    ("Trade and logistics", "Invoicing, Orders, tracking and refunds", "Extract delivery and commercial terms from documents", "Shipping evidence does not prove quality; no letter-of-credit or customs authority", ["S04", "S19", "S22"], [
        ("Delivery shortfall adjustment", "Compare agreed and documented received quantities before a payment adjustment."),
        ("Incoterm cost explainer", "Explain supplied responsibility and cost clauses for merchant review without giving binding legal advice."),
        ("Late delivery recovery", "Compare merchant-supported reshipment, replacement and refund alternatives against a customer deadline."),
        ("Shipment payment evidence chain", "Connect dispatch, delivery and payment records without treating tracking as proof of all obligations."),
    ]),
    ("Donations and community finance", "Orders or donation checkout; approved Payouts where enabled", "Match documented needs and explain allocation proposals", "Charity verification and custody are real dependencies; no fabricated impact evidence", ["S02", "S03"], [
        ("Aid invoice verification", "Match an approved aid budget with vendor invoices before a reviewer pays."),
        ("Restricted donation ledger", "Track donor-stated restrictions and flag incompatible allocation proposals."),
        ("Community purchase coordination", "Prepare a transparent shared purchase after contributions and approvals are confirmed."),
        ("Nonprofit payout evidence", "Link approved beneficiary disbursements with recipient confirmation and unresolved items."),
    ]),
    ("Credit and BNPL", "Pay Later presentment or approved merchant financing products", "Explain terms and build transparent affordability scenarios", "No new underwriting model without representative data and legal authority", ["S03", "S04"], [
        ("Repayment terms explainer", "Explain an offered financing schedule without inventing eligibility or promised approval."),
        ("Merchant borrowing readiness", "Organize merchant-provided cash records and missing documents for an existing lender."),
        ("Invoice financing evidence", "Detect conflicting invoice claims in a synthetic workflow; never offer unlicensed funding."),
        ("BNPL reconciliation desk", "Explain merchant-side transaction records and adjustments around existing Pay Later payments."),
    ]),
    ("Tax, healthcare, education and insurance", "Invoices, Orders or Subscriptions for bounded payments", "Extract statements and explain documented billing discrepancies", "Domain-specific privacy, tax and insurance rules; no diagnosis, legal filing or underwriting", ["S03", "S04"], [
        ("Education fee reconciliation", "Explain instalments, concessions and refunds against a school's verified billing records."),
        ("Healthcare billing clarification", "Identify duplicated or inconsistent billing lines before a patient approves payment."),
        ("Insurance premium evidence", "Compare a supplied policy schedule with recurring payment records and flag changes."),
        ("Tax evidence organizer", "Group transaction and fee records for accountant review without claiming tax-return correctness."),
    ]),
    ("PYUSD, quantitative finance and HFT-adjacent infrastructure", "Separate PYUSD testnet plus an actual PayPal Sandbox core flow", "Forecast bounded scenarios and explain control decisions", "No assumed fiat bridge, internal liquidity access, exchange matching engine or profitable trading strategy", ["S23", "S29", "S30"], [
        ("TreasuryLab", "Stress-test a synthetic merchant's fiat and PYUSD obligations under settlement delays and wallet outages."),
        ("Quote staleness supervisor", "Detect stale or expired quotes and stop execution instead of predicting arbitrage profits."),
        ("Inventory and exposure limits", "Borrow pre-trade limits and kill switches for simulated payment-rail inventory management."),
        ("Settlement netting laboratory", "Compare gross and net funding requirements on synthetic obligations and demonstrate a separate testnet settlement."),
    ]),
]

SOURCES = {
    "S01": ("Official hackathon rules", "https://paypalaihackathon.devpost.com/rules"),
    "S02": ("Hackathon overview and judging criteria", "https://paypalaihackathon.devpost.com/"),
    "S03": ("Hackathon resources and sponsor list", "https://paypalaihackathon.devpost.com/resources"),
    "S04": ("PayPal agent tools reference", "https://developer.paypal.com/ai-tools/agent-tools"),
    "S05": ("Agent Ready overview", "https://developer.paypal.com/agent-ready/overview"),
    "S06": ("Agentic commerce services access and Store Sync", "https://developer.paypal.com/agentic-commerce-services/about"),
    "S07": ("PayPal 2025 segment report and transaction loss definition", "https://www.sec.gov/Archives/edgar/data/1633917/000163391726000024/R133.htm"),
    "S08": ("Public PayPal technology project gallery, not the hackathon entry list", "https://devpost.com/software/built-with/paypal"),
    "S09": ("Clause-to-Cash project description", "https://devpost.com/software/clause-to-cash-contracts-that-collect"),
    "S10": ("PayPal idempotency", "https://developer.paypal.com/reference/guidelines/idempotency"),
    "S11": ("ACTC Saga coordinator README", "https://github.com/Jack-Li-Npu/ACTC"),
    "S12": ("PayPal webhook delivery and verification", "https://developer.paypal.com/api/rest/webhooks/rest/"),
    "S13": ("Warden project description", "https://devpost.com/software/warden-a-paypal-firewall-for-ai-agents"),
    "S14": ("BossAgent description in public PayPal project gallery", "https://devpost.com/software/built-with/paypal"),
    "S15": ("Dispute Defender project description", "https://devpost.com/software/dispute-defender"),
    "S16": ("Chargeflow PayPal integration, vendor claims", "https://www.chargeflow.io/integrations/paypal"),
    "S17": ("Return Loop project description", "https://devpost.com/software/return-loop"),
    "S18": ("Caseproof project description", "https://devpost.com/software/caseproof-5gmdck"),
    "S19": ("Payments v2 authorizations, captures and refunds", "https://developer.paypal.com/api/payments/v2"),
    "S20": ("PayPal authorization and honor periods", "https://developer.paypal.com/docs/checkout/standard/customize/authorization-honor/"),
    "S21": ("Temporal Saga pattern", "https://docs.temporal.io/design-patterns/saga-pattern"),
    "S22": ("Supplora Pay project description", "https://devpost.com/software/supplora-pay"),
    "S23": ("Mastercard Agent Pay for Machines, October 20 2026", "https://www.mastercard.com/global/en/news-and-trends/press/2026/october/Mastercard-Agent-Pay-for-Machines-in-action.html"),
    "S24": ("PayPal reserves", "https://www.paypal.com/us/cshelp/article/what-are-reserves-help393"),
    "S25": ("PayPal balance report", "https://developer.paypal.com/reports/financial-reports/balance-report"),
    "S26": ("PayPal negative balances", "https://www.paypal.com/us/cshelp/article/what-should-i-do-if-my-balance-is-negative-help389"),
    "S27": ("Currency Exchange quote endpoint", "https://developer.paypal.com/api/pricing/v2/quote-exchange-rates"),
    "S28": ("FXaaS integration and eligibility", "https://developer.paypal.com/v5/checkout/fx/integrate"),
    "S29": ("PYUSD testnet faucet documentation", "https://developer.paypal.com/community/blog/testnet-pyusd/"),
    "S30": ("PayPal treasury interview, July 1 2026", "https://flow.db.com/case-studies/inside-paypal-s-treasury-transformation"),
    "S31": ("Transaction Search scope and reporting lag", "https://developer.paypal.com/docs/transaction-search/"),
    "S32": ("Subscription plan revision and consent", "https://developer.paypal.com/api/subscriptions/v1/subscriptions-revise"),
    "S33": ("PayPal AI subscription management session", "https://paypalevents.swoogo.com/Developer_Day25/session/3026336/building-an-ai-powered-subscription-management-app-with-paypal-apis-agentic-ai"),
    "S34": ("ProofPay project description", "https://devpost.com/software/proofpay-n8iom2"),
    "S35": ("PayPal AP2 support and mandates", "https://developer.paypal.com/community/blog/PayPal-Agent-Payments-Protocol/"),
    "S36": ("Official hackathon gallery unavailable", "https://paypalaihackathon.devpost.com/project-gallery"),
    "S37": ("PayPal Braintree payment orchestration", "https://developer.paypal.com/braintree/docs/guides/orchestration/overview/"),
    "S38": ("ClearLedger AI project description", "https://devpost.com/software/paypal-ai-reconciliation"),
    "S39": ("AGENT GATE project description", "https://devpost.com/software/agent-gate-human-controlled-ai-payments"),
    "S40": ("ZeroRace project; another hackathon and no implemented PayPal rail evidenced", "https://devpost.com/software/zerorace"),
    "S41": ("Formal analysis of agent payment protocols, preprint", "https://arxiv.org/abs/2609.00060"),
    "S42": ("Whispers of Wealth AP2 red-teaming paper", "https://doi.org/10.1109/IMNS67862.2026.11655291"),
    "S43": ("Agentic Commerce World, preprint", "https://arxiv.org/abs/2608.02441"),
    "S44": ("Between Promise and Pain: microservice failure analysis", "https://doi.org/10.1145/3725783.3764388"),
    "S45": ("PaySentinel project description", "https://devpost.com/software/paysentinel-p5inec"),
    "S46": ("Stripe Workbench production debugging", "https://stripe.dev/blog/resolving-production-issues-in-your-aws-stripe-integration-using-workbench"),
    "S47": ("AutoRescue project description", "https://devpost.com/software/autorescue-agentic-post-purchase-rescue"),
    "S48": ("Official agent toolkit quickstart", "https://developer.paypal.com/ai-tools/toolkit"),
    "S49": ("PayPal Currency Exchange Postman announcement", "https://developer.paypal.com/community/blog/currency-exchange-apis-new-notebooks-more-now-live-in-postman/"),
    "S50": ("PayPal PYUSD Solana quickstart", "https://developer.paypal.com/community/blog/pyusd-quick-start-guide/"),
}

# These ordinal judgments assess a tightly scoped concept's potential if built
# well. They are neither measured product quality nor predicted judge scores.
CRITERIA = ["Implementation", "Design", "Impact", "Innovation", "Presentation"]
ASSESSMENTS = [
    ("RecoverPlan", [4, 4, 4, 4, 5], "Medium", "Prove business-goal repair beyond existing Saga middleware."),
    ("ReservePilot", [4, 4, 4, 3, 4], "Medium", "Prove fresh obligation accounting beyond cash caps and AP scheduling."),
    ("ClearFX", [3, 4, 4, 3, 4], "Access-dependent", "Verify FXaaS permissions before promising live quotes or guarantees."),
    ("ReturnRouter", [4, 4, 4, 2, 4], "Medium", "Crowded returns market; one concrete advantage needs user evidence."),
    ("ToolMeter", [4, 4, 3, 2, 4], "Medium", "Differentiate from existing metering and machine-payment products."),
    ("TreasuryLab", [2, 3, 4, 4, 3], "High", "Synthetic treasury data and separate testnet limit production claims."),
    ("PayGuard baseline", [4, 4, 4, 1, 4], "Lower", "Direct public overlap makes the original broad concept a weak novelty bet."),
]


def build_ideas() -> list[dict[str, object]]:
    """Expand domain hypotheses into complete, uniquely identified records."""
    ideas: list[dict[str, object]] = []
    for domain, paypal, ai, barrier, sources, hypotheses in DOMAINS:
        for name, hypothesis in hypotheses:
            ideas.append({
                "id": f"I{len(ideas) + 1:03d}",
                "domain": domain,
                "name": name,
                "hypothesis": hypothesis,
                "ai_role": ai,
                "paypal_path": paypal,
                "main_constraint": barrier,
                "source_ids": sources,
                "evidence_status": "Generated product hypothesis; not a validated unmet need",
            })
    return ideas


def build_assessments() -> list[dict[str, object]]:
    """Calculate equal-weight ordinal totals and a one-point sensitivity band."""
    rows = []
    for name, values, risk, reason in ASSESSMENTS:
        rows.append({
            "concept": name,
            **dict(zip(CRITERIA, values, strict=True)),
            "total": sum(values),
            "delivery_risk": risk,
            "decision_condition": reason,
            "assessment_type": "Subjective concept potential, not measured results or win probability",
        })
    return sorted(rows, key=lambda row: -int(row["total"]))


def write_bank(ideas: list[dict[str, object]]) -> None:
    """Write the complete idea bank in readable Markdown and structured JSON."""
    parts = [
        "# PayPal + AI opportunity bank",
        f"\nResearch date: {AS_OF}. 100 product hypotheses across 25 domains.",
        "\nThis is a broad, bounded search space, not every possible invention. A source establishes context or a capability, not demand or novelty for each idea. All names are working labels. No project was implemented or benchmarked in this research pass.",
        "\nThe referenced PDF was absent at its supplied path. The pasted proposal was used as user context; document instructions were not adopted.",
        "\nRead `opportunity-research.md` for the decision, access gates, closest alternatives, prototype plan and source registry.",
    ]
    for domain, paypal, ai, barrier, sources, _ in DOMAINS:
        parts += [
            f"\n## {domain}",
            f"\nPayPal path: {paypal}. AI role: {ai}.",
            f"\nConstraint: {barrier}.",
            "\nContext sources: " + ", ".join(f"[{source}]({SOURCES[source][1]})" for source in sources) + ".",
            "\n| ID | Product hypothesis | Observable prototype outcome |",
            "| --- | --- | --- |",
        ]
        for idea in (idea for idea in ideas if idea["domain"] == domain):
            parts.append(f"| {idea['id']} | {idea['name']} | {idea['hypothesis']} |")
    ROOT.joinpath("idea-bank.md").write_text("\n".join(parts) + "\n", encoding="utf-8")
    ROOT.joinpath("idea-bank.json").write_text(json.dumps({
        "as_of": AS_OF,
        "scope": "100 unvalidated product hypotheses across 25 domains",
        "ideas": ideas,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    """Validate research records and generate reproducible local outputs."""
    ideas = build_ideas()
    assert len(ideas) == 100
    assert len({idea["id"] for idea in ideas}) == 100
    assert len({idea["name"] for idea in ideas}) == 100
    assert len({idea["domain"] for idea in ideas}) == 25
    assert set(Counter(idea["domain"] for idea in ideas).values()) == {4}
    assert all(source in SOURCES for idea in ideas for source in idea["source_ids"])
    rows = build_assessments()
    assert all(1 <= int(row[criterion]) <= 5 for row in rows for criterion in CRITERIA)
    assert all(row["total"] == sum(int(row[criterion]) for criterion in CRITERIA) for row in rows)
    write_bank(ideas)
    ROOT.joinpath("concept-assessment.json").write_text(json.dumps({
        "as_of": AS_OF,
        "method": "Five subjective ordinal ratings, 1-5, equally weighted. Sum is a planning aid, not a judge score or win probability.",
        "sensitivity": "A one-point revision to each criterion changes a total by up to five; close concept rankings are not robust.",
        "rows": rows,
    }, indent=2) + "\n", encoding="utf-8")
    registry = "# Source registry\n\nReviewed through public web retrieval on 2026-10-23. Retrieval does not prove implementation claims.\n\n"
    registry += "\n".join(f"- **{key}** [{title}]({url})" for key, (title, url) in SOURCES.items())
    ROOT.joinpath("sources.md").write_text(registry + "\n", encoding="utf-8")
    print(json.dumps({"ideas": len(ideas), "domains": len(DOMAINS), "assessments": len(rows), "sources": len(SOURCES)}))


if __name__ == "__main__":
    main()
