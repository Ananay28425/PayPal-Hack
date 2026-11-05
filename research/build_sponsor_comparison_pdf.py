"""Create a source-backed sponsor comparison PDF with measured layout bounds.

The report distinguishes documented platform capabilities from proposed roles.
It does not claim any sponsor integration or product result has been executed.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from pypdf import PdfReader, PdfWriter

from sponsor_comparison_content import TOOLS, SOURCES

ROOT = Path(r"E:\PROGRAMMING-2\PayPal-Hack")
TMP = ROOT / "tmp" / "pdfs" / "sponsor-comparison"
OUT = ROOT / "output" / "pdf"
TMP.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
FONT = Path(r"C:\Windows\Fonts")
for name, filename in [("DV", "DejaVuSans.ttf"), ("DV-Bold", "DejaVuSans-Bold.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(FONT / filename)))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-Bold")
W, H = A4
M = 43
CW = W - 2*M
NAVY = colors.HexColor("#14263E")
TEAL = colors.HexColor("#087F83")
INK = colors.HexColor("#203249")
MUTED = colors.HexColor("#586C80")
LINE = colors.HexColor("#D5E1E9")
PALE = colors.HexColor("#EAF5F3")
PAPER = colors.HexColor("#FBFCFE")
AMBER = colors.HexColor("#A45B20")
BODY = ParagraphStyle("body", fontName="DV", fontSize=10.0, leading=14.5, textColor=INK)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=8.7, leading=12.2)
LEAD = ParagraphStyle("lead", parent=BODY, fontSize=11.0, leading=15.9, textColor=NAVY)
TITLE = ParagraphStyle("title", fontName="DV-Bold", fontSize=22, leading=26, textColor=NAVY)
TOTAL = 23
LAYOUT = []


def paragraph(c, text, y, width=CW, x=M, style=BODY, gap=9, markup=False):
    p = Paragraph(text if markup else html.escape(text), style)
    _, ht = p.wrap(width, H)
    p.drawOn(c, x, y-ht)
    return y-ht-gap


def label(c, text, y, x=M):
    c.setFont("DV-Bold", 10.5)
    c.setFillColor(NAVY)
    c.drawString(x, y, text)
    return y-17


def base(c, number, section, title, lead=None):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(TEAL)
    c.rect(0, H-8, W, 8, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("DV-Bold", 7.8)
    c.drawString(M, H-28, "ASSEMBLY / PAYGUARD")
    c.setFillColor(MUTED)
    c.setFont("DV", 7.4)
    c.drawRightString(W-M, H-28, "SPONSOR INTEGRATION REVIEW / 26 OCT 2026")
    c.setStrokeColor(LINE)
    c.line(M, H-38, W-M, H-38)
    c.line(M, 47, W-M, 47)
    c.drawString(M, 32, section.upper())
    c.drawRightString(W-M, 32, f"{number:02d} / {TOTAL}")
    c.setFillColor(TEAL)
    c.setFont("DV-Bold", 8)
    c.drawString(M, H-65, section.upper())
    y = paragraph(c, title, H-82, style=TITLE, gap=15)
    if lead:
        y = paragraph(c, lead, y, style=LEAD, gap=15)
    return y


def finish(c, page, y, refs=()):
    if y < 82:
        raise ValueError(f"Page {page} overflows its safe body: y={y:.1f}")
    if refs:
        c.setFont("DV", 7.3)
        c.setFillColor(MUTED)
        c.drawString(M, 62, "SOURCE IDs: " + ", ".join(refs))
    LAYOUT.append({"page": page, "lowest_body_y": round(y, 1)})
    c.showPage()


def takeaway(c, text, y):
    p = Paragraph(html.escape(text), SMALL)
    _, height = p.wrap(CW-26, 500)
    box_height = height+33
    c.setFillColor(PALE)
    c.roundRect(M, y-box_height, CW, box_height, 7, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.setFont("DV-Bold", 8)
    c.drawString(M+13, y-14, "DESIGN DECISION")
    p.drawOn(c, M+13, y-26-height)
    return y-box_height-13


def body_page(c, page, section, title, lead, blocks, refs=(), decision=None):
    y = base(c, page, section, title, lead)
    for head, paras in blocks:
        y = label(c, head, y)
        for text in paras:
            y = paragraph(c, text, y)
        y -= 5
    if decision:
        y = takeaway(c, decision, y)
    finish(c, page, y, refs)


def table(c, rows, y, widths, font=8.6):
    sty = ParagraphStyle("cell", parent=SMALL, fontSize=font, leading=font+3)
    parsed = [[Paragraph(html.escape(str(cell)), sty) for cell in row] for row in rows]
    # Paragraphs carry their own colors, so set the header text explicitly.
    for j, text in enumerate(rows[0]):
        parsed[0][j] = Paragraph(html.escape(str(text)), ParagraphStyle("header", parent=sty, textColor=colors.white, fontName="DV-Bold"))
    t = Table(parsed, colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F0F5F8")]),
        ("GRID", (0,0), (-1,-1), 0.4, LINE),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    _, height = t.wrap(CW, H)
    t.drawOn(c, M, y-height)
    return y-height-14


def cover(c):
    base(c, 1, "decision report", "")
    c.setFillColor(NAVY)
    c.roundRect(M, 415, CW, 336, 14, fill=1, stroke=0)
    cs = ParagraphStyle("cover", fontName="DV-Bold", fontSize=30, leading=36, textColor=colors.white)
    y = paragraph(c, "Assembly has better sponsor fit, with conditions", 692, CW-44, M+22, cs, gap=24)
    ss = ParagraphStyle("subtitle", parent=LEAD, fontSize=13, leading=19, textColor=colors.HexColor("#C3E4E3"))
    paragraph(c, "A detailed comparison of useful integration, overlap, failure modes and proof of use in Assembly and PayGuard.", y, CW-44, M+22, ss)
    c.setFillColor(colors.HexColor("#7CD2CA"))
    c.setFont("DV-Bold", 9)
    c.drawString(M+22, 444, "TEN VERIFIED OPTIONAL SPONSORS + PAYPAL")
    y = 376
    y = paragraph(c, "The objective is a coherent product in which each selected tool makes an inspectable contribution. A dependency count is not a product benefit.", y, style=LEAD, gap=18)
    y = paragraph(c, "Prepared for the two-person PayPal AI Hackathon team. The original reference to thirteen tools was corrected in chat after checking the official inventory. This report covers all ten listed optional sponsors, plus the required PayPal platform.", y, gap=16)
    y = paragraph(c, "Status: architecture and evidence review. Tool roles, demonstrations and tests are proposals. No sponsor account access, integration success, performance improvement or prize outcome is claimed.", y, style=SMALL)
    finish(c, 1, y, ["S01","S02","S03"])


def inventory(c):
    y = base(c, 3, "inventory and fit", "Every tool gets a role and a limitation", "These classifications are architectural judgments about the current proposals, not measured product results or sponsor-award scores.")
    rows = [["Tool", "Assembly role type", "PayGuard role type"]]
    for t in TOOLS:
        rows.append([t["name"], t["afit"], t["pfit"]])
    y = table(c, rows, y, [132, (CW-132)/2, (CW-132)/2])
    y = paragraph(c, "Direct workflow means a natural task in the stated product. Conditional means a real requirement or evaluation must justify the feature. Engineering contribution means substantive development or verification use, without a deployed customer dependency. Runtime and delivery labels describe platform choices, not exclusivity.", y, style=SMALL)
    y = takeaway(c, "The biggest differences are Channel3 and Bryntum. Eight other optional sponsors have broadly comparable role types in both proposals; tool coverage alone is not a decisive proof of product quality.", y)
    finish(c, 3, y, ["S01","S02","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13"])


def flow(c, y, steps):
    for i, (title, detail) in enumerate(steps, 1):
        c.setFillColor(PALE if i%2 else colors.HexColor("#F0F4F8"))
        c.setStrokeColor(LINE)
        c.roundRect(M, y-55, CW, 55, 6, fill=1, stroke=1)
        c.setFillColor(TEAL)
        c.setFont("DV-Bold", 11)
        c.drawString(M+12, y-20, f"{i:02d}")
        p = Paragraph(html.escape(title), ParagraphStyle("flowhead", parent=BODY, fontName="DV-Bold", fontSize=10.2, leading=13))
        _, ht = p.wrap(CW-62, 100)
        p.drawOn(c, M+43, y-9-ht)
        paragraph(c, detail, y-29, CW-62, M+43, SMALL, gap=0)
        y -= 68
    return y


def architecture(c, page, project, steps, paragraphs, refs):
    y = base(c, page, "architecture", f"{project}: one authority for business state", "All paths below are proposed. The durable domain service mediates vendor calls and validates every transition into a business side effect.")
    y = flow(c, y, steps)
    for text in paragraphs:
        y = paragraph(c, text, y)
    finish(c, page, y, refs)


def tool_page(c, page, t):
    y = base(c, page, t["stage"], t["name"])
    y = paragraph(c, f"Assembly: {t['afit']}  |  PayGuard: {t['pfit']}", y, style=SMALL, gap=11)
    y = paragraph(c, t["cap"], y, gap=14)
    gap = 22
    col = (CW-gap)/2
    ys = []
    for title, paras, x in [("ASSEMBLY", t["a"], M), ("PAYGUARD", t["p"], M+col+gap)]:
        yy = label(c, title, y, x)
        for text in paras:
            yy = paragraph(c, text, yy, col, x, BODY, gap=9)
        ys.append(yy)
    y = min(ys)-5
    c.setStrokeColor(LINE)
    c.line(M, y+6, W-M, y+6)
    for title, key in [("What proves substantial use", "proof"), ("Removal test", "remove"), ("Ownership and failure boundary", "boundary")]:
        y = label(c, title, y-6)
        y = paragraph(c, t[key], y, style=SMALL, gap=8)
    y = takeaway(c, t["verdict"], y-3)
    finish(c, page, y, t["sources"])


def reference_page(c, page, start, stop, title, note):
    y = base(c, page, "references and provenance", title, note)
    for sid, name, url in SOURCES[start:stop]:
        text = f"<b>[{sid}] {html.escape(name)}</b><br/><link href='{html.escape(url, quote=True)}' color='#087F83'>{html.escape(url)}</link>"
        y = paragraph(c, text, y, style=SMALL, gap=9, markup=True)
    finish(c, page, y)


def build():
    stage = TMP / "stage.pdf"
    c = Canvas(str(stage), pagesize=A4, pageCompression=1)
    c.setTitle("Assembly vs PayGuard: sponsor value and integration complexity")
    c.setAuthor("Codex research for PayPal AI Hackathon")
    cover(c)
    body_page(c, 2, "executive judgment", "Assembly fits the broader toolset more naturally",
      "The recommendation remains Assembly, but the earlier statement that all ten fit reasonably well needs explicit conditions. Their usefulness is not established merely by assigning a plausible label.", [
        ("What actually changes the comparison", ["Channel3 is a natural candidate-discovery input for Assembly. Bryntum fits when Assembly must deliver a working outcome by a real deadline. In a general PayGuard firewall, catalogue discovery and staffed review scheduling expand the product beyond its minimal authority gate.", "The other eight optional sponsors can serve broadly similar role types in both. AG Studio supports meaningful investigation in either product. APIMatic and Postman belong to engineering. Astropods and Render need a clean deployment boundary. Elastic, Kernel and Zapier require a demonstrated retrieval, browsing or connected-workflow need."]),
        ("The coherent all-ten version", ["Assembly's selected scenario is a complete, compatible equipment setup by a stated date, with inspectable evidence and an optional approved workspace handoff. Each tool contributes to that scenario or to its reproducible engineering trail. Conditional branches stay outside the payment-critical path.", "If the buyer has no timing requirement, no missing specification evidence and no connected workspace need, do not claim scheduling, browsing and task creation are essential. A simpler product may be the better entry even when the user has asked for all-ten coverage."]),
        ("How to read this report", ["Page 3 gives the full role matrix; page 4 defines the evidence standard; pages 5-6 show ownership; pages 7-17 audit PayPal and each sponsor; pages 18-21 cover redundancy, failures, validation and delivery. Sources are on pages 22-23."])
      ], ["S01","S02","S03"], "Useful integration means an actual input changes a relevant output, or a development/verification artifact improves the build. The current report is a plan for proving that use, not proof it has happened.")
    inventory(c)
    body_page(c, 4, "comparison method", "Use an observable contribution test",
      "Assess the same user task in both projects. A sponsor name, imported package or one ceremonial API call is not sufficient evidence of meaningful use.", [
        ("Five questions for every integration", ["Identify the actual input, the output another component consumes, the owner of that output, the failure behavior and the evidence a judge can inspect. The per-tool pages answer these questions through proposed roles, removal tests, proofs and boundaries.", "Compare against the smallest reasonable replacement. A table can replace a dashboard; PostgreSQL search can replace a second index at small scale; a timestamp can replace a scheduling board. The added capability must improve the selected task enough to justify its extra lifecycle."]),
        ("Runtime necessity and engineering value", ["PayPal is a required runtime platform. APIMatic can be used substantially without appearing in production. Postman can provide the regression and judge handoff. Treating either as a mandatory customer request hop would manufacture coupling.", "A tool can be replaceable yet meaningfully used. The question is whether the selected deployment, extraction trace, comparison interaction or regression collection makes a concrete contribution. Reserve claims of essentiality for a requirement that truly cannot be met without that behavior."]),
        ("Evidence levels and uncertainty", ["The sponsor pages and technical docs establish published capabilities. Roles in this report are architectural proposals. Actual account access, integration behavior, user benefit, latency, cost and product outcomes require execution. No fit rating is a measured score or award probability.", "A fixed catalogue and simulated delivery assumptions can support a bounded prototype when labelled. They cannot substantiate claims of live retailer fulfillment, universal compatibility, reduced returns or platform-wide transaction-loss reduction."])
      ], ["S01","S03"], "Keep the all-ten requirement visible, but do not turn a failed usefulness test into an invented reason that the product needs a tool.")
    architecture(c, 5, "Assembly", [
      ("Discover and acquire bounded evidence", "Channel3 candidates; Kernel only for permitted missing-specification inspection."),
      ("Propose typed requirements and facts", "One read-only Astropods stage; schema, evidence references and uncertainty are explicit."),
      ("Check, schedule and approve a version", "Render domain API + PostgreSQL + checker; AG Studio comparison and Bryntum time view."),
      ("Execute and verify the accepted purchase", "PayPal buyer approval, server capture, resource status and verified events."),
      ("Complete the approved external handoff", "Durable outbox; Zapier fixed action only after payment verification and user consent."),
    ], ["Elastic is a rebuildable evidence-search projection, read through the domain service. APIMatic informs development of the payment adapter; Postman verifies APIs and handoff artifacts. Neither becomes a live checkout dependency.", "Keep payment state in one authoritative database. Browser widgets, the model runtime, a search index and an external task board cannot consume approval or change the authoritative offer. A Rust/Wasm checker is optional supporting technology, not an additional sponsor."], ["S04","S06","S07","S08","S09","S10","S12","S13","S16","S20"])
    architecture(c, 6, "PayGuard", [
      ("Compile an explicit proposed intent", "Astropods proposes limits, exceptions and ambiguities from authorized user instructions."),
      ("Decide authority and obtain approval", "Render domain service checks current policy and version; AG Studio explains the decision."),
      ("Execute the existing business operation", "PayPal adapter uses durable operation IDs, provider request IDs and server-held credentials."),
      ("Reconcile and inspect the outcome", "Authoritative state and verified events drive the incident view; Elastic can aid retrieval."),
    ], ["Kernel inspection and Channel3 enrichment are conditional inputs for a shopping-specific proposal. They add little to a generic refund/payout gate unless that scenario needs external page or catalogue evidence. Neither supplies payment authority.", "Bryntum requires a staffed case queue, deadlines and reviewer resources to contribute more than an expiry timestamp. Zapier can hand an approved incident into the merchant's existing task system. These are defensible scope choices, but they create additional workflows to validate.", "APIMatic, Postman and Render have the same engineering/delivery roles as in Assembly. The all-ten version of PayGuard therefore carries a greater risk of widening into a shopping, case-management and payment-control suite."], ["S05","S06","S07","S08","S09","S10","S11","S12","S13"])
    for number, tool in enumerate(TOOLS, 7):
        tool_page(c, number, tool)
    body_page(c, 18, "overlap and simplification", "Assign one owner to each responsibility",
      "All-ten coverage can coexist with a small architecture if tools occupy different boundaries. Repeated agents, stores and workflow engines create ambiguity about who decides and retries.", [
        ("Astropods, Render and Zapier", ["Astropods owns one bounded extraction/explanation stage. Render owns the domain API, authoritative database and durable business jobs. Zapier owns one approved action in a connected external app. A failed external task is not a failed payment.", "Using Astropods orchestration, Render Workflows, a separate agent framework and Zapier to manage the same operation would create redundant retry and state machines. Choose one business-operation owner. Render hosting alone is already meaningful use; Workflows is not mandatory."]),
        ("Channel3, Kernel and Elastic", ["Channel3 discovers structured candidates and offers. Kernel acquires a missing fact from an allowed page only when needed. Elastic retrieves stored evidence and cases. PostgreSQL owns accepted facts and business versions. Avoid re-searching the live web during capture.", "If structured data covers the facts, the browser branch can be skipped. If a small collection searches well in PostgreSQL, be honest about Elastic's marginal benefit and measure the evidence task before expanding the index."]),
        ("AG Studio, Bryntum, APIMatic and Postman", ["AG Studio owns comparison/investigation. Bryntum owns time and resource dependencies. They read common domain records and submit versioned changes through the same API. Two independent dashboards must not maintain competing product or order state.", "APIMatic supplies development context; Postman supplies independent verification and documentation. Keep both outside production availability calculations. A single package with clear modules is preferable to one service per sponsor."])
      ], ["S04","S05","S06","S07","S08","S09","S10","S11","S12","S13"], "The target topology is a product UI, one authoritative backend/database, one bounded AI stage and conditional integrations. Ten sponsor contributions do not require ten always-on application services.")
    body_page(c, 19, "failure and operating cost", "A nonessential outage must not corrupt a payment",
      "Classify dependency failures by what they prevent. Keep payment-critical checks strict, and degrade optional evidence or follow-through explicitly.", [
        ("Stop safely at the authority boundary", ["If a critical product fact is unknown, an offer has changed or approval is stale, hold the proposed purchase. If the model runtime is unavailable, preserve the draft and report the failed stage. Do not silently switch to an unvalidated generated result.", "If PayPal's capture result is ambiguous, record the provider resource and operation identity and reconcile. If the search index is down but accepted facts are durable, the backend may still inspect that accepted record; a stale search result cannot authorize a newer offer."]),
        ("Degrade side branches independently", ["Kernel failure leaves an unknown or a source-confirmation request. Zapier failure leaves a paid purchase with an incomplete external task, not an invitation to charge again. A delayed verified event must not regress a later refund or reconciliation state.", "APIMatic and Postman outages do not affect deployed checkout. AG Studio or Bryntum interface errors must not change authoritative records. Expose a usable error state rather than presenting a stale success badge."]),
        ("Measure cost and preserve judge access", ["Record calls, model tokens, browser-session time, index/worker resources and external actions per completed scenario. Set bounds on retries, page inspections and candidate searches. Report p50/p95 and warm/cold runs only after actual measurement; no cost or speed result is assumed here.", "Judging continues through December 15. A 14-day trial started October 26 can expire before submission; a 45-day trial can expire before judging ends. Check actual account terms, extensions, paid resource settings and open-source redistribution rights. Sponsor credit is not proof that service access will last."])
      ], ["S03","S07","S09","S13","S16","S19","S22","S23"], "Fail closed on missing authority or critical evidence. Preserve the verified financial state when nonfinancial follow-through fails.")
    body_page(c, 20, "verification and proof of use", "Prove a contribution by changing the input",
      "Use held-out cases and independently authored expected outcomes. Test runtime roles, engineering roles and cross-tool failures with different kinds of evidence.", [
        ("Ablation and negative cases", ["For Assembly, remove Channel3 discovery and compare with a curated baseline; disable the evidence index and assess source lookup; remove the schedule and check whether a deadline decision disappears. A test counts only if it exercises the behavior claimed for that tool.", "For PayGuard, test the same optional removals without weakening the central authority gate. If Channel3 or Bryntum removal changes nothing in the selected user journey, report the role as conditional or unnecessary for that scope."]),
        ("Evidence bundle for every sponsor", ["Keep one redacted trace or artifact per tool: AG Studio interaction and widget; APIMatic context-to-code provenance; Astropods deployed trace; Bryntum changed dependency; Channel3 response linked to a selected variant; Elastic query/source result; Kernel session/evidence; Postman collection/report; Render deployment/recovery; Zapier approved action/read-back.", "Join artifacts with scenario, requirement/configuration version, purchase ID, provider ID and external action ID where applicable. Redact secrets. Save expected outcomes before running the final scenario so the same model cannot invent the case and award itself a pass."]),
        ("Cross-tool tests that expose integration mess", ["Change a critical fact after approval; submit two purchase attempts; delay an index refresh; return malformed AI output; deny a browser source; lose the local response after capture; replay a verified event; and repeat a post-payment task dispatch. State exactly which faults are injected into our own application.", "Require the same authoritative result in the API, evidence workspace, time view and payment record. A video can help inspect the run, but durable state and provider responses establish payment outcome. No universal exactly-once claim follows from a single successful demo."])
      ], ["S11","S18","S21","S22","S23"], "Publish a useful evidence trail, not a wall of logos. The current report defines proposed gates; none of these execution results is claimed as completed.")
    body_page(c, 21, "build sequence and presentation", "Keep the demonstration centered on one decision",
      "Commit to a narrowly bounded Assembly workflow only if its evidence, checking and payment path work. All-ten coverage must serve that workflow or its engineering trail.", [
        ("Build in dependency order", ["First establish a genuine sandbox create/approve/capture/read-back and a small source-backed catalogue. Then implement typed facts, unknown handling, one conflict/repair and versioned approval. Add the bounded Astropods stage only through a supported authenticated invocation.", "Next connect the evidence workspace and a real readiness deadline. Add retrieval and missing-fact browser inspection where the cases require them. After verified capture, implement the explicitly approved connected task. Record APIMatic use while building and maintain Postman regressions throughout."]),
        ("A proposed video under three minutes", ["Open with the customer outcome and deadline. Show the initial configuration's real conflict, its supporting evidence and an acceptable repair. Change a requirement and show the dependent compatibility or readiness decision update. Approve the exact controlled merchant offer and verify a genuine sandbox capture.", "Use one relevant missing-specification branch or source view, then show the approved task handoff. Put engineering proof and sponsor details in the public repository and concise submission text. The video should not spend ten equal segments touring ten products."]),
        ("Decision gates and submission honesty", ["Retain Assembly's lead only if held-out cases, comprehensible user decisions and reliable payment execution support it. Do not rescue a weak core by adding languages, agents or more external writes. If a conditional sponsor feature fails its usefulness test, disclose that conflict with the all-ten objective.", "Document setup, license obligations, actual models/tools, account prerequisites and judge access through the review period. Public source code can coexist with separately obtained sponsor credentials and permitted commercial dependencies; verify each license before distributing assets or trial packages."])
      ], ["S01","S03","S05","S07","S08","S11","S12","S13"], "My recommendation remains Assembly for more natural breadth, with explicit validation gates. No sponsor count, stack choice or architecture guarantees the overall first prize.")
    reference_page(c, 22, 0, 13, "Official inventory and sponsor briefs", "Reviewed through public retrieval on October 26, 2026. The official inventory names ten optional sponsor tools plus the required PayPal platform; it does not require every optional sponsor.")
    reference_page(c, 23, 13, len(SOURCES), "Technical references and evidence limits", "Published capability is distinct from enabled account access and working integration. The report's role assignments and removal tests are proposed methodology, not measured outcomes.")
    c.save()
    reader = PdfReader(stage)
    if len(reader.pages) != TOTAL:
        raise ValueError(f"Expected {TOTAL} pages, received {len(reader.pages)}")
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    data = {"as_of": "2026-10-26", "status": "Proposed integrations, not executed", "optional_sponsors": 10, "required_platform": "PayPal", "tools": TOOLS, "sources": SOURCES}
    writer.add_attachment("comparison-evidence.json", json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
    writer.add_metadata({"/Title": "Assembly vs PayGuard: sponsor value and integration complexity", "/Author": "Codex", "/ResearchAsOf": "2026-10-26"})
    target = OUT / "Assembly_vs_PayGuard_Sponsor_Integration_Comparison.pdf"
    with target.open("wb") as stream:
        writer.write(stream)
    (TMP / "layout-checks.json").write_text(json.dumps(LAYOUT, indent=2), encoding="utf-8")
    print(target)
    print(f"Pages: {len(reader.pages)}; sponsor tools: {len(TOOLS)-1}; lowest body point: {min(x['lowest_body_y'] for x in LAYOUT)}")


if __name__ == "__main__":
    build()
