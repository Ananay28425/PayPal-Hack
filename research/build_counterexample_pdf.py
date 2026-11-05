"""Build and structurally verify the 20-page Counterexample proposal."""
from __future__ import annotations

import html
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from pypdf import PdfReader, PdfWriter

from counterexample_report_content import PAGES, SOURCES

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "tmp" / "pdfs" / "counterexample"
OUT = ROOT / "output" / "pdf" / "Counterexample_Payment_Reliability_Lab_20_Pages.pdf"
TMP.mkdir(parents=True, exist_ok=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
for name, file in [("CE", "DejaVuSans.ttf"), ("CE-Bold", "DejaVuSans-Bold.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(Path(r"C:\Windows\Fonts") / file)))
pdfmetrics.registerFontFamily("CE", normal="CE", bold="CE-Bold")
W, H = A4
M = 43
CW = W - 2*M
NAVY = colors.HexColor("#12283B")
TEAL = colors.HexColor("#087C80")
INK = colors.HexColor("#243B4D")
MUTED = colors.HexColor("#5B6F7C")
LINE = colors.HexColor("#D2DEE6")
PALE = colors.HexColor("#EEF6F6")
BG = colors.HexColor("#FBFCFE")
BODY = ParagraphStyle("body", fontName="CE", fontSize=9.8, leading=13.6, textColor=INK)
LEAD = ParagraphStyle("lead", parent=BODY, fontSize=10.8, leading=15.3, textColor=MUTED)
TITLE = ParagraphStyle("title", fontName="CE-Bold", fontSize=21, leading=25, textColor=NAVY)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=8.3, leading=11.5)
LAYOUT = []


def para(c: Canvas, text: str, y: float, style=BODY, width=CW, x=M, gap=8, markup=False) -> float:
    p = Paragraph(text if markup else html.escape(text), style)
    _, h = p.wrap(width, H)
    p.drawOn(c, x, y-h)
    return y-h-gap


def base(c: Canvas, index: int, page: dict) -> float:
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(0, H-7, W, 7, fill=1, stroke=0)
    c.setFont("CE-Bold", 7.8)
    c.setFillColor(NAVY)
    c.drawString(M, H-28, "COUNTEREXAMPLE / PAYMENT RELIABILITY LAB")
    c.setFont("CE", 7.4)
    c.setFillColor(MUTED)
    c.drawRightString(W-M, H-28, "RESEARCH BRIEF / 26 OCT 2026")
    c.setStrokeColor(LINE)
    c.line(M, H-39, W-M, H-39)
    c.line(M, 47, W-M, 47)
    c.drawString(M, 32, page["section"].upper())
    c.drawRightString(W-M, 32, f"{index:02d} / 20")
    c.bookmarkPage(f"page-{index}")
    c.addOutlineEntry(f"{index:02d} {page['title']}", f"page-{index}")
    c.setFont("CE-Bold", 8)
    c.setFillColor(TEAL)
    c.drawString(M, H-64, page["section"].upper())
    y = para(c, page["title"], H-80, style=TITLE, gap=12)
    return para(c, page["lead"], y, style=LEAD, gap=15)


def table(c: Canvas, rows: list[list[str]], y: float) -> float:
    count = len(rows[0])
    widths = {2: [CW*.29, CW*.71], 3: [CW*.21, CW*.40, CW*.39],
              4: [CW*.14, CW*.28, CW*.30, CW*.28]}[count]
    cell = ParagraphStyle("cell", parent=SMALL, fontSize=8.4, leading=11.5)
    head = ParagraphStyle("head", parent=cell, fontName="CE-Bold", textColor=colors.white)
    parts = [[Paragraph(html.escape(str(t)), head if i==0 else cell) for t in row]
             for i, row in enumerate(rows)]
    t = Table(parts, colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, PALE]),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), .4, LINE),
        ("LEFTPADDING", (0,0), (-1,-1), 7), ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    _, ht = t.wrap(CW, H)
    t.drawOn(c, M, y-ht)
    return y-ht-16


def architecture(c: Canvas, y: float) -> float:
    bw = (CW-28)/3
    bh = 40
    labels = [
        ("Reviewed contract", "Rules and allowed actions"),
        ("AI proposer", "Untrusted candidate scenario"),
        ("Schema / DAG check", "Accepted immutable plan"),
        ("Owned storefront", "Browser and local fault hooks"),
        ("Bounded runner", "Operation IDs and checkpoints"),
        ("PayPal Sandbox", "Real provider observations"),
        ("Durable trace", "Postgres; redacted evidence"),
        ("Independent oracle", "Frozen rules; explicit verdict"),
        ("Reduced regression", "Manifest + API/browser steps"),
    ]
    tops = [y, y-59, y-118]
    for idx, (title, sub) in enumerate(labels):
        row, col = divmod(idx, 3)
        x, top = M+col*(bw+14), tops[row]
        c.setFillColor(NAVY if idx in (4,7) else PALE)
        c.setStrokeColor(LINE)
        c.roundRect(x, top-bh, bw, bh, 5, fill=1, stroke=1)
        color = colors.white if idx in (4,7) else INK
        pstyle = ParagraphStyle("box", parent=SMALL, fontSize=8.8, leading=10.7, alignment=1, textColor=color, fontName="CE-Bold")
        para(c, title, top-7, pstyle, bw-8, x+4, gap=0)
        sstyle = ParagraphStyle("sub", parent=SMALL, fontSize=7.1, leading=8.5, alignment=1, textColor=color)
        para(c, sub, top-23, sstyle, bw-8, x+4, gap=0)
        if col < 2:
            c.setStrokeColor(TEAL)
            c.line(x+bw+2, top-20, x+bw+12, top-20)
            c.line(x+bw+9, top-23, x+bw+12, top-20)
            c.line(x+bw+9, top-17, x+bw+12, top-20)
    c.setStrokeColor(TEAL)
    mid = W/2
    # Only the validated scenario reaches the runner; no AI-to-executor shortcut.
    right_mid = M + 2*(bw+14) + bw/2
    gap_y = y-49
    c.line(right_mid, y-bh-1, right_mid, gap_y)
    c.line(right_mid, gap_y, mid, gap_y)
    c.line(mid, gap_y, mid, y-58)
    c.line(mid-3, y-55, mid, y-58)
    c.line(mid+3, y-55, mid, y-58)
    top = tops[1]
    c.line(mid, top-bh-1, mid, top-58)
    c.line(mid-3, top-55, mid, top-58)
    c.line(mid+3, top-55, mid, top-58)
    return y-176


def references(c: Canvas, y: float) -> float:
    for sid, title, url, detail in SOURCES:
        line = f'<b>{sid}</b>  <link href="{html.escape(url, quote=True)}" color="#087C80">{html.escape(title)}</link>'
        y = para(c, line, y, style=SMALL, gap=4.1, markup=True)
    y -= 10
    for head, text in [
        ("Research method", "Exa supported targeted overlap, official capability and sponsor searches; Undermind supplied paper abstracts and metadata. The search was a focused challenge to the proposal, not an exhaustive literature review, patent search or review of all entrants. Vendor performance claims were not independently tested."),
        ("Reproducibility", "Embedded files: complete report content and source register, the synthetic kernel experiment, its measured result, and a provenance note. Run the Python experiment to reproduce the page 16 counts. No credentials, payment data or downloaded vendor code are embedded."),
        ("Evidence cutoff", "Capabilities reflect public pages retrieved on October 26, 2026. Account access and commercial terms can differ. Only the clearly labeled local experiment was executed; all pilot targets and proposed integrations require validation.")
    ]:
        y = para(c, f"<b>{head}.</b> {html.escape(text)}", y, style=SMALL, markup=True, gap=8)
    return y


def build() -> None:
    assert len(PAGES) == 20
    stage = TMP / "stage.pdf"
    c = Canvas(str(stage), pagesize=A4, pageCompression=1)
    c.setTitle("Counterexample: a payment reliability lab - 20-page assessment")
    c.setAuthor("Codex")
    for index, page in enumerate(PAGES, 1):
        y = base(c, index, page)
        if page.get("table"):
            y = table(c, page["table"], y)
        if page.get("diagram"):
            y = architecture(c, y)
        if page.get("references"):
            y = references(c, y)
        for head, text in page.get("blocks", []):
            y = para(c, head, y, style=ParagraphStyle("blocktitle", parent=BODY, fontName="CE-Bold", textColor=NAVY), gap=4)
            y = para(c, text, y, gap=11)
        if page.get("note"):
            y = para(c, page["note"], y-10, style=SMALL, gap=0)
        LAYOUT.append({"page": index, "body_bottom": round(y, 2), "title": page["title"]})
        if y < 81:
            raise ValueError(f"Page {index} overflow: {y:.1f}")
        if page.get("refs"):
            c.setFont("CE", 7)
            c.setFillColor(MUTED)
            c.drawString(M, 61, "SOURCE IDs: " + ", ".join(page["refs"]))
        c.showPage()
    c.save()
    reader = PdfReader(stage)
    assert len(reader.pages) == 20
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    evidence = {"as_of":"2026-10-26", "status":"Proposal plus a synthetic local experiment", "pages":PAGES, "sources":SOURCES}
    writer.add_attachment("report-content-and-sources.json", json.dumps(evidence, ensure_ascii=False, indent=2).encode("utf-8"))
    for filename in ["counterexample_kernel_experiment.py", "counterexample_kernel_results.json"]:
        writer.add_attachment(filename, (ROOT / "research" / filename).read_bytes())
    writer.add_attachment("evidence-scope.txt", b"Only the authored local Python experiment was executed. No PayPal, AI, browser, or sponsor integration was run. Vendor and paper capabilities were reviewed from public documentation and abstracts. Proposed metrics are not measured results.")
    writer.add_metadata({"/Title":"Counterexample: Payment Reliability Lab - 20-page assessment", "/Author":"Codex", "/ResearchAsOf":"2026-10-26"})
    with OUT.open("wb") as f:
        writer.write(f)
    (TMP / "layout-checks.json").write_text(json.dumps(LAYOUT, indent=2), encoding="utf-8")
    final = PdfReader(OUT)
    assert len(final.pages) == 20
    assert len(final.attachments) == 4
    for index, page in enumerate(final.pages, 1):
        assert f"{index:02d} / 20" in page.extract_text()
    print(json.dumps({"path":str(OUT), "pages":len(final.pages), "words":sum(len(p.extract_text().split()) for p in final.pages), "bytes":OUT.stat().st_size, "minimum_body_y":min(x["body_bottom"] for x in LAYOUT), "embedded_files":list(final.attachments)}, indent=2))


if __name__ == "__main__":
    build()
