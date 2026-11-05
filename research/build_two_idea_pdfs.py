"""Build two 20-page, source-backed PayPal hackathon decision PDFs.

The visible transcript pages preserve the wording of prior Codex replies.
The PDFs also embed exact UTF-8 source replies for byte-level verification.
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from pypdf import PdfReader, PdfWriter
from pdf_sections import PAYGUARD, ASSEMBLY

ROOT = Path(r"E:\PROGRAMMING-2\PayPal-Hack")
TMP = ROOT / "tmp" / "pdfs"
OUT = ROOT / "output" / "pdf"
TMP.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
FONT_DIR = Path(r"C:\Windows\Fonts")
pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_DIR / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(FONT_DIR / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DejaVuMono", str(FONT_DIR / "DejaVuSansMono.ttf")))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold")
W, H = A4
NAVY = colors.HexColor("#11233A")
TEAL = colors.HexColor("#087E82")
INK = colors.HexColor("#18283B")
MUTED = colors.HexColor("#586B7D")
PAPER = colors.HexColor("#FBFCFE")
LINE = colors.HexColor("#D8E3EB")
PALE = colors.HexColor("#EAF6F5")
AMBER = colors.HexColor("#B66322")

STYLE = ParagraphStyle("body", fontName="DejaVu", fontSize=9.3, leading=14.1, textColor=INK, alignment=TA_LEFT)
STYLE_LEAD = ParagraphStyle("lead", parent=STYLE, fontSize=10.7, leading=16.0, textColor=NAVY)
STYLE_SMALL = ParagraphStyle("small", parent=STYLE, fontSize=8.3, leading=11.5, textColor=MUTED)
STYLE_BULLET = ParagraphStyle("bullet", parent=STYLE, leftIndent=12, firstLineIndent=-10, spaceAfter=4)

def draw_para(c: canvas.Canvas, text: str, x: float, y: float, width: float,
              style: ParagraphStyle = STYLE, after: float = 9) -> float:
    para = Paragraph(text, style)
    _, h = para.wrap(width, 900)
    para.drawOn(c, x, y - h)
    return y - h - after

def rule(c: canvas.Canvas, y: float, x: float = 44, width: float = W-88) -> None:
    c.setStrokeColor(LINE)
    c.setLineWidth(0.65)
    c.line(x, y, x + width, y)

def base(c: canvas.Canvas, name: str, page: int, section: str) -> None:
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(0, H-9, W, 9, fill=1, stroke=0)
    c.setFont("DejaVu-Bold", 8)
    c.setFillColor(NAVY)
    c.drawString(44, H-29, name.upper())
    c.setFont("DejaVu", 7.5)
    c.setFillColor(MUTED)
    c.drawRightString(W-44, H-29, "26 OCT 2026  /  RESEARCH BRIEF")
    rule(c, H-37)
    rule(c, 48)
    c.setFont("DejaVu", 7.4)
    c.drawString(44, 33, section.upper())
    c.drawRightString(W-44, 33, f"{page:02d} / 20")

def section_page(c: canvas.Canvas, project: str, number: int, item: dict) -> None:
    base(c, project, number, item["label"])
    y = H - 69
    c.setFont("DejaVu-Bold", 8)
    c.setFillColor(TEAL)
    c.drawString(44, y, item["label"].upper())
    y -= 31
    title = Paragraph(html.escape(item["title"]), ParagraphStyle(
        "title", fontName="DejaVu-Bold", fontSize=21, leading=25, textColor=NAVY))
    _, h = title.wrap(W-88, 200)
    title.drawOn(c, 44, y-h)
    y -= h+17
    y = draw_para(c, html.escape(item["lead"]), 44, y, W-88, STYLE_LEAD, 15)
    for block in item["blocks"]:
        if "head" in block:
            c.setFont("DejaVu-Bold", 10.3)
            c.setFillColor(NAVY)
            c.drawString(44, y, block["head"])
            y -= 15
        for text in block.get("text", []):
            y = draw_para(c, html.escape(text), 44, y, W-88, STYLE, 8)
        for bullet in block.get("bullets", []):
            y = draw_para(c, "• " + html.escape(bullet), 53, y, W-97, STYLE_BULLET, 2)
        y -= 8
    if "diagram" in item:
        y -= 2
        y = draw_diagram(c, item["diagram"], y)
    if y < (160 if item.get("note") else 101):
        raise ValueError(f"{project} page {number} content overflow: {y:.1f}")
    if item.get("note"):
        note = item["note"]
        box_h = 62
        c.setFillColor(PALE)
        c.roundRect(44, 86, W-88, box_h, 8, fill=1, stroke=0)
        c.setFont("DejaVu-Bold", 8.3)
        c.setFillColor(TEAL)
        c.drawString(56, 131, "DECISION POINT")
        yy = draw_para(c, html.escape(note), 56, 123, W-112, STYLE_SMALL, 0)
        if yy < 91:
            raise ValueError(f"{project} page {number} note overflow")
    if item.get("sources"):
        c.setFont("DejaVu", 7.2)
        c.setFillColor(MUTED)
        c.drawString(44, 62, "EVIDENCE: " + ", ".join(item["sources"]))
    c.showPage()

def draw_diagram(c: canvas.Canvas, labels: list[str], y: float) -> float:
    n = len(labels)
    gap = 10
    bw = (W-88-gap*(n-1))/n
    bh = 49
    for idx, label in enumerate(labels):
        x = 44 + idx*(bw+gap)
        c.setFillColor(PALE if idx % 2 == 0 else colors.HexColor("#F1F4F8"))
        c.setStrokeColor(LINE)
        c.roundRect(x, y-bh, bw, bh, 6, fill=1, stroke=1)
        p = Paragraph(html.escape(label), ParagraphStyle(
            f"diagram-{idx}", parent=STYLE_SMALL, fontSize=8, leading=10,
            textColor=NAVY, alignment=1))
        _, ph = p.wrap(bw-10, 50)
        p.drawOn(c, x+5, y-(bh-ph)/2-ph)
        if idx < n-1:
            c.setFillColor(TEAL)
            c.setFont("DejaVu-Bold", 11)
            c.drawCentredString(x+bw+gap/2, y-bh/2-3, ">")
    return y-bh-14

def cover(c: canvas.Canvas, project: str, subtitle: str, thesis: str,
          source_text: str, art: str) -> None:
    base(c, project, 1, "decision brief")
    c.setFillColor(NAVY)
    c.roundRect(44, 435, W-88, 319, 15, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#76D4CF"))
    c.setFont("DejaVu-Bold", 9)
    c.drawString(67, 718, "PAYPAL + AI / FIRST-PRIZE RESEARCH")
    c.setFillColor(colors.white)
    t = Paragraph(html.escape(project), ParagraphStyle(
        "cover-title", fontName="DejaVu-Bold", fontSize=34, leading=40,
        textColor=colors.white))
    _, th = t.wrap(W-140, 120)
    t.drawOn(c, 67, 650-th)
    st = Paragraph(html.escape(subtitle), ParagraphStyle(
        "cover-sub", fontName="DejaVu", fontSize=15, leading=21,
        textColor=colors.HexColor("#C8E5E5")))
    _, sh = st.wrap(W-140, 120)
    st.drawOn(c, 67, 590-sh)
    rule(c, 508, 67, W-134)
    c.setFillColor(colors.HexColor("#D4E5EF"))
    c.setFont("DejaVu", 9)
    c.drawString(67, 477, "20 pages  |  Analysis + exact earlier chat output")
    y = 394
    y = draw_para(c, html.escape(thesis), 44, y, W-88, STYLE_LEAD, 22)
    y = draw_para(c, "Prepared 26 October 2026. The 30,000-participant figure is the team's competition scenario, not a confirmed count of eligible submissions.", 44, y, W-88, STYLE, 14)
    y = draw_para(c, "Pages 16-19 reproduce an earlier Codex reply. The PDF also embeds that reply as exact UTF-8 text. The SHA-256 below identifies those source bytes.", 44, y, W-88, STYLE, 14)
    digest = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    c.setFont("DejaVuMono", 7.5)
    c.setFillColor(MUTED)
    c.drawString(44, y-4, "SHA-256  " + digest)
    c.showPage()

def transcript_lines(text: str, width: int = 107) -> list[str]:
    output = []
    wrapper = textwrap.TextWrapper(width=width, break_long_words=True,
        break_on_hyphens=False, replace_whitespace=False, drop_whitespace=False)
    for source_line in text.split("\n"):
        if source_line == "":
            output.append("")
            continue
        expanded = source_line.expandtabs(4)
        output.extend(wrapper.wrap(expanded) or [""])
    return output

def transcript_pages(c: canvas.Canvas, project: str, source: str, text: str) -> None:
    lines = transcript_lines(text)
    count = math.ceil(len(lines)/4)
    if count > 78:
        raise ValueError(f"Transcript exceeds 4 pages: {len(lines)} display lines")
    for idx in range(4):
        page = idx+16
        base(c, project, page, "verbatim earlier Codex output")
        c.setFillColor(TEAL)
        c.setFont("DejaVu-Bold", 8)
        c.drawString(44, H-65, f"VERBATIM CHAT RECORD  /  PART {idx+1} OF 4")
        c.setFont("DejaVu", 8)
        c.setFillColor(MUTED)
        c.drawString(44, H-81, source)
        rule(c, H-90)
        y = H-106
        chunk = lines[idx*count:(idx+1)*count]
        c.setFont("DejaVuMono", 7.05)
        c.setFillColor(INK)
        for line in chunk:
            # Private-use UI glyphs are shown as escapes in the visible rendering.
            # The embedded attachment preserves every original UTF-8 byte.
            safe = "".join((f"\\u{ord(ch):04x}" if "\ue000" <= ch <= "\uf8ff" else ch)
                           for ch in line)
            c.drawString(44, y, safe)
            y -= 8.45
        if y < 63:
            raise ValueError(f"Transcript page {page} overflow")
        c.showPage()

def references_page(c: canvas.Canvas, project: str, sources: list[tuple[str,str,str]],
                    limits: list[str]) -> None:
    base(c, project, 20, "references and provenance")
    c.setFillColor(TEAL)
    c.setFont("DejaVu-Bold", 8)
    c.drawString(44, H-67, "SOURCE REGISTER")
    c.setFillColor(NAVY)
    c.setFont("DejaVu-Bold", 21)
    c.drawString(44, H-96, "Evidence and limits")
    y = H-121
    y = draw_para(c, "Sources below support factual context and API capabilities. Project architecture, impact and prize prospects are proposals until implemented and tested.", 44, y, W-88, STYLE, 13)
    for key, title, url in sources:
        line = f"<b>[{html.escape(key)}] {html.escape(title)}</b><br/><link href='{html.escape(url, quote=True)}' color='#087E82'>{html.escape(url)}</link>"
        y = draw_para(c, line, 44, y, W-88, STYLE_SMALL, 6)
    y -= 3
    rule(c, y)
    y -= 13
    c.setFont("DejaVu-Bold", 9)
    c.setFillColor(NAVY)
    c.drawString(44, y, "PROVENANCE NOTES")
    y -= 16
    for note in limits:
        y = draw_para(c, "• "+html.escape(note), 44, y, W-88, STYLE_SMALL, 6)
    if y < 61:
        raise ValueError(f"{project} references overflow {y:.1f}")
    c.showPage()

def build(project: str, subtitle: str, thesis: str, sections: list[dict],
          sources: list[tuple[str,str,str]], limits: list[str],
          source_json: Path, filename: str, extra_attachment: Path|None = None) -> Path:
    if len(sections) != 14:
        raise ValueError(f"{project}: expected 14 analysis pages, got {len(sections)}")
    record = json.loads(source_json.read_text(encoding="utf-8"))
    raw = record["text"]
    stage = TMP / ("stage-"+filename)
    c = canvas.Canvas(str(stage), pagesize=A4, pageCompression=1)
    c.setTitle(f"{project}: twenty-page research and exact chat record")
    c.setAuthor("Codex research for PayPal AI Hackathon")
    cover(c, project, subtitle, thesis, raw, filename)
    for number, item in enumerate(sections, start=2):
        section_page(c, project, number, item)
    transcript_pages(c, project, record["source"], raw)
    references_page(c, project, sources, limits)
    c.save()
    reader = PdfReader(str(stage))
    if len(reader.pages) != 20:
        raise ValueError(f"{project}: built {len(reader.pages)} pages")
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.add_attachment("exact-earlier-codex-output.txt", raw.encode("utf-8"))
    if extra_attachment is not None:
        rec = json.loads(extra_attachment.read_text(encoding="utf-8"))
        writer.add_attachment("original-user-payguard-proposal.txt", rec["text"].encode("utf-8"))
    writer.add_metadata({
        "/Title": f"{project}: twenty-page research and exact chat record",
        "/Author": "Codex",
        "/ChatOutputSHA256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "/ResearchAsOf": "2026-10-26",
    })
    final = OUT / filename
    with final.open("wb") as fp:
        writer.write(fp)
    return final


PAYGUARD_SOURCES = [
    ("S01", "Official rules and judging criteria", "https://paypalaihackathon.devpost.com/rules"),
    ("S02", "PayPal 2025 transaction losses (SEC filing)", "https://www.sec.gov/Archives/edgar/data/1633917/000163391726000024/R133.htm"),
    ("S03", "PayPal agent tools", "https://developer.paypal.com/ai-tools/agent-tools"),
    ("S04", "PayPal and Agent Payments Protocol", "https://developer.paypal.com/community/blog/PayPal-Agent-Payments-Protocol/"),
    ("S05", "PayPal Orders v2 create order", "https://developer.paypal.com/api/orders/v2/orders-create"),
    ("S06", "PayPal idempotency guidance", "https://developer.paypal.com/reference/guidelines/idempotency/"),
    ("S07", "PayPal webhooks", "https://developer.paypal.com/api/rest/webhooks/rest/"),
    ("S08", "A Formal Analysis of Agent Payment Protocols", "https://arxiv.org/abs/2609.00060"),
    ("S09", "Public Warden agent-payment project", "https://devpost.com/software/warden-a-paypal-firewall-for-ai-agents"),
    ("S10", "Beyond the Mandate, research paper", "https://arxiv.org/abs/2608.23858"),
]

ASSEMBLY_SOURCES = [
    ("S01", "Official rules and judging criteria", "https://paypalaihackathon.devpost.com/rules"),
    ("S02", "Channel3 product-data response overview", "https://docs.trychannel3.com/guides/response-overview"),
    ("S03", "Neuro-symbolic AI for Industrial Configuration", "https://arxiv.org/abs/2609.29947"),
    ("S04", "Ontology-Mediated Neurosymbolic Constraint Acquisition", "https://arxiv.org/abs/2609.29876"),
    ("S05", "PayPal Orders v2 create order", "https://developer.paypal.com/api/orders/v2/orders-create"),
    ("S06", "PayPal idempotency guidance", "https://developer.paypal.com/reference/guidelines/idempotency/"),
    ("S07", "PayPal webhooks", "https://developer.paypal.com/api/rest/webhooks/rest/"),
    ("S08", "Astropods frontend agents guide", "https://docs.astropods.com/frontend-agents.md"),
    ("S09", "Official hackathon sponsor resources", "https://paypalaihackathon.devpost.com/resources"),
    ("S10", "Kernel observe documentation", "https://github.com/kernel/docs/blob/main/introduction/observe.mdx"),
]

if __name__ == "__main__":
    results = [
        build("PayGuard AI", "Payment authority and execution safety for AI agents",
              "A narrowly scoped payment authority layer can be technically impressive, but PayGuard's broad premise now faces substantial existing-platform and competitor overlap. This brief tests the idea as a first-prize contender without assuming novelty or a win.",
              PAYGUARD, PAYGUARD_SOURCES,
              ["The transcript on pages 16–19 is the exact earlier Codex reply rendered for reading; the UTF-8 attachment preserves source bytes.",
               "The separate original PayGuard text was supplied by the user and is embedded as a second attachment.",
               "Papers are cited for conceptual support, not independent replication; API behavior and judging remain subject to the current official documentation."],
              TMP / "exact-payguard.json", "PayGuard_AI_Research_20_Pages.pdf",
              TMP / "exact-payguardProposal.json"),
        build("Assembly", "Outcome-to-purchase reasoning for complex products",
              "Assembly treats a purchase as a dependency-constrained configuration decision. It couples source-grounded AI interpretation with deterministic feasibility checks and a verified PayPal sandbox purchase; the novelty and winning case depend on proving that chain live.",
              ASSEMBLY, ASSEMBLY_SOURCES,
              ["Pages 16–19 render the exact earlier Codex reply; the UTF-8 attachment preserves source bytes.",
               "Product feeds and extracted specifications may be incomplete. The prototype must expose unknowns and only assert compatibility when evidence supports it.",
               "The 30,000-participant figure is the user's scenario, not a verified count of judged projects or an estimable win probability."],
              TMP / "exact-assembly.json", "Assembly_Research_20_Pages.pdf"),
    ]
    for result in results:
        print(result)

