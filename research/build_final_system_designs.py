"""Consolidate the reviewed A/B designs into two small overall diagrams."""
from pathlib import Path
import json
from zipfile import ZipFile, ZIP_DEFLATED
import build_architecture_pack as render

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "architecture" / "final-overall-designs"
render.OUT = OUT
for directory in (OUT, OUT/"source", OUT/"diagrams"):
    directory.mkdir(parents=True, exist_ok=True)


def common(g):
    g.n("ui", "Buyer / merchant UI\nReact + TypeScript\nAG Studio + Bryntum")
    g.n("edge", "Managed edge + identity\nCDN / WAF / OIDC / quotas")
    g.n("evidence", "Evidence and AI preparation\nChannel3 / Astropods / Kernel / Elastic\nscoped proposals; no payment authority", "ai")
    g.n("pp", "PayPal\nbuyer approval / capture / verification", "core")
    g.n("task", "Approved setup task\nZapier; after verified payment", "async")
    g.n("qa", "Isolated Counterexample\nAPIMatic development context\nPostman independent regressions", "test")
    g.e("ui", "edge")


a = render.Graph("A-final-overall", "A | One application, one worker, one financial database", "Current implementation target. Managed synchronous PostgreSQL protects the specified AZ failure model; regional recovery remains separate.", "TB")
common(a)
a.n("app", "One FastAPI application on Render\nAssembly checks + PayGuard authority\nversioned offers / approvals / webhook ingress", "core")
a.n("sql", "Managed PostgreSQL\nprimary + synchronous AZ standby\npurchases / reservations / inbox / outbox", "core", "cylinder")
a.n("worker", "One worker service on Render\nseparate bounded job pools\npayment dispatch / reconciliation / follow-through", "core")
a.e("edge", "app"); a.e("app", "sql", "short transactions")
a.e("app", "evidence", "prepare")
a.e("sql", "worker", "durable jobs", True)
a.e("worker", "pp", "stable operation identity")
a.e("pp", "app", "signed webhook", True)
a.e("worker", "sql", "confirmed / unknown outcome")
a.e("worker", "task", "explicit consent", True)
a.e("qa", "app", "owned test environment", True)

b = render.Graph("B-final-overall", "B | The same application in regional cells", "Future production evolution. Current authority and financial writes require quorum; region placement and capacity require validation.", "TB")
common(b)
b.n("routing", "Regional request routing\ncurrent owner for money; local reads\nownership metadata in financial SQL", "core")
for key, region in [("cell_a", "Region A"), ("cell_b", "Region B")]:
    b.n(key, f"{region}: Render application cell\nsame FastAPI code + bounded workers\nper-tenant admission and recovery capacity", "core")
b.n("sql", "Managed distributed financial SQL\nexplicit SERIALIZABLE transactions\nregion-survival quorum: 3+ permitted DB regions\nversions / reservations / inbox / outbox", "core", "cylinder")
b.e("edge", "routing", "authenticated application requests")
b.e("routing", "cell_a", "current owner")
b.e("routing", "cell_b", "current owner")
for key in ("cell_a", "cell_b"):
    b.e(key, "evidence", "scoped preparation")
    b.e(key, "sql", "authoritative state")
    b.e(key, "pp", "quota-limited operations")
    b.e(key, "task", "approved downstream job", True)
b.e("pp", "routing", "verified ingress routing", True)
b.e("qa", "cell_a", "isolated release tests", True)

results = [a.render(), b.render()]
(OUT/"manifest.json").write_text(json.dumps({
    "status": "Simplified reference designs, not implemented or benchmarked",
    "basis": "Reviewed Assembly Proof A/B specification dated November 1, 2026",
    "diagrams": results,
    "limits": ["No zero-defect or zero-loss guarantee", "No customer-fund custody", "No measured billion-user capacity", "Mermaid sources were not independently rendered"]
}, indent=2), encoding="utf-8")
print(json.dumps({"directory": str(OUT), "diagrams": results}, indent=2))
