"""Prepare reviewed planning ratings and source receipts for the chat answer."""

from __future__ import annotations

import json
from pathlib import Path

from build_research import CRITERIA, ROOT, SOURCES


VISUAL_ROOT = Path(r"C:\Users\anany\.codex\visualizations\2026\10\22\01a16531-3a9e-7e10-b819-461801d3b80f")


def write_json(name: str, payload: dict[str, object]) -> None:
    """Write bounded, non-sensitive records inside this task's approved surface."""
    VISUAL_ROOT.mkdir(parents=True, exist_ok=True)
    VISUAL_ROOT.joinpath(name).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def source_links(ids: list[str]) -> list[dict[str, str]]:
    """Resolve only reviewed source IDs into reader-facing provenance links."""
    return [{"label": SOURCES[source][0], "href": SOURCES[source][1]} for source in ids]


def main() -> None:
    """Build a concept comparison and narrowly scoped evidence receipts."""
    assessments = json.loads(ROOT.joinpath("concept-assessment.json").read_text(encoding="utf-8"))
    rows = [{key: row[key] for key in ["concept", *CRITERIA, "total"]} for row in assessments["rows"]]
    source = {
        "label": "Subjective planning assessment, October 23, 2026",
        "files": [{"label": "concept-assessment.json"}],
        "links": source_links(["S01", "S11", "S13", "S18", "S22", "S28"]),
        "metricDefinitions": [{
            "label": "Concept potential",
            "definition": "Concept potential sums five subjective 1-5 ratings for implementation, design, impact, innovation and presentation, assuming the scoped product is built well. The maximum total is 25.",
        }],
        "caveats": [
            "These are planning judgments, not measured quality, judge scores or probabilities of winning.",
            "API access and actual prototype execution remain unverified.",
            "A one-point revision to each of five criteria can change a total by five points; close rankings are not robust.",
        ],
        "evidenceFlow": [{
            "kind": "calculation",
            "title": "Equal-weight planning total",
            "detail": "total = Implementation + Design + Impact + Innovation + Presentation. All input ratings and exact sums are retained in the preview.",
        }],
    }
    write_json("paypal-concept-assessment.json", {
        "schemaVersion": 1,
        "id": "paypal-concept-potential",
        "title": "Concept potential before prototyping",
        "description": "Subjective planning totals, 0-25. Not judge scores or win probabilities. Close rankings can reverse.",
        "chart": {"type": "horizontalBar", "x": "concept", "y": "total", "yLabel": "Planning total, maximum 25", "showValues": True, "startAtZero": True},
        "rows": rows,
        "source": source,
        "height": 430,
        "theme": "codex-classic",
    })
    write_json("paypal-concept-assessment-sources.json", {
        "schemaVersion": 1,
        "items": [{
            "id": "concept-potential",
            "title": "How were concept priorities assessed?",
            "queries": [{"id": "concept-assessment", "source": source, "columns": list(rows[0]), "rows": rows}],
        }],
    })
    facts = [
        ("rules", "What controls submission and judging?", ["S01", "S02", "S03", "S36"],
         "The deadline is November 12, 2026 at 12:00 p.m. PST, or November 13 at 1:30 a.m. IST. Five judging criteria are equally weighted. The event gallery is unpublished.",
         ["The displayed participant count is a registration count, not completed submissions."]),
        ("overlap", "How much public overlap was found?", ["S04", "S05", "S06", "S08", "S09", "S11", "S13", "S15", "S18", "S22", "S34", "S35", "S38", "S39", "S45", "S47"],
         "Official products and public project pages already describe agent checkout, mandates, payment firewalls, evidence preparation, work acceptance, cash-cap scheduling and payment-state recovery.",
         ["Public descriptions were not independently tested, and are not all confirmed entries in this hackathon.", "Search cannot establish that a proposed feature is absent from every competitor."]),
        ("access", "Which technical dependencies can rule out a concept?", ["S10", "S12", "S19", "S20", "S24", "S25", "S27", "S28", "S29", "S30", "S31", "S32", "S37"],
         "The reviewed APIs support sandbox payment lifecycles and merchant operations. FXaaS needs eligibility and contractual enablement. Reporting can lag. PYUSD testnet is separate from REST sandbox.",
         ["No credentials were supplied and no PayPal API call was executed in this research pass.", "The public documentation does not establish access to internal treasury or exchange execution systems."]),
        ("research", "What research informed the proposed evaluation?", ["S41", "S42", "S43", "S44"],
         "The literature motivates checking cross-stage payment bindings, semantic manipulation and process-level evidence rather than relying only on terminal payment state.",
         ["The formal-analysis preprint was inspected in HTML. Other papers were reviewed at metadata/abstract level; experiments were not reproduced."]),
    ]
    write_json("paypal-research-sources.json", {
        "schemaVersion": 1,
        "items": [{
            "id": key,
            "title": title,
            "queries": [{
                "id": key,
                "summary": summary,
                "source": {"label": title, "links": source_links(ids), "caveats": caveats},
            }],
        } for key, title, ids, summary, caveats in facts],
    })
    print(json.dumps({"assessment_rows": len(rows), "receipt_findings": len(facts), "visual_root": str(VISUAL_ROOT)}))


if __name__ == "__main__":
    main()
