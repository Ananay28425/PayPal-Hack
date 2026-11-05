"""Author and render the two Assembly Proof reference architectures.

Diagrams are proposals, not deployed infrastructure or measured capacity.
Graphviz renders the same reviewed node/edge model to SVG and PNG.
"""
from __future__ import annotations

import html
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "architecture" / "assembly-proof-2026-11-01"
DOT = Path(r"D:\Anaconda\Library\bin\dot.exe")
COLORS = {
    "core": "#E3EFF8", "ai": "#FFF2D9", "async": "#E6F4EF",
    "test": "#EEE9FA", "risk": "#FCE8E6", "plain": "#FFFFFF",
}
GRAPHS: list[Graph] = []


class Graph:
    def __init__(self, slug: str, title: str, caption: str, direction="LR"):
        self.slug, self.title, self.caption = slug, title, caption
        self.direction = direction
        self.nodes: dict[str, dict] = {}
        self.edges: list[dict] = []
        self.groups: dict[str, list[str]] = {}
        self.ranks: list[list[str]] = []
        GRAPHS.append(self)

    def n(self, key: str, label: str, kind="plain", shape="box", group=None):
        assert key not in self.nodes
        self.nodes[key] = dict(label=label, kind=kind, shape=shape)
        if group:
            self.groups.setdefault(group, []).append(key)
        return key

    def e(self, a: str, b: str, label="", dashed=False):
        self.edges.append(dict(a=a, b=b, label=label, dashed=dashed))

    def render(self):
        for edge in self.edges:
            assert edge["a"] in self.nodes and edge["b"] in self.nodes, edge
        q = json.dumps
        lines = ["digraph G {",
                 f'graph [rankdir={self.direction}, bgcolor="#F8FBFD", pad="0.32", nodesep="0.35", ranksep="0.62", splines=polyline, fontname="Segoe UI", fontsize=21, labelloc=t, label={q(self.title)}];',
                 'node [shape=box, style="rounded,filled", fillcolor="white", color="#ADC4D2", penwidth=1.0, fontname="Segoe UI", fontsize=12, fontcolor="#132E44", margin="0.16,0.12"];',
                 'edge [color="#54778D", penwidth=1.15, arrowsize=0.7, fontname="Segoe UI", fontsize=10, fontcolor="#355B70"];']
        def node_line(key):
            item = self.nodes[key]
            return f'{q(key)} [label={q(item["label"])}, shape={item["shape"]}, fillcolor={q(COLORS[item["kind"]])}];'
        grouped = {key for group in self.groups.values() for key in group}
        for idx, (group, keys) in enumerate(self.groups.items()):
            lines += [f'subgraph cluster_{idx} {{ label={q(group)}; fontsize=14; color="#CBDCE6"; style="rounded";']
            lines += [node_line(k) for k in keys]
            lines.append("}")
        lines += [node_line(k) for k in self.nodes if k not in grouped]
        for edge in self.edges:
            lines.append(f'{q(edge["a"])} -> {q(edge["b"])} [label={q(edge["label"])}, style={"dashed" if edge["dashed"] else "solid"}];')
        for rank in self.ranks:
            lines.append("{ rank=same; " + "; ".join(q(k) for k in rank) + "; }")
        lines.append("}")
        dot = "\n".join(lines)
        target = OUT / "source" / f"{self.slug}.dot"
        target.write_text(dot, encoding="utf-8")
        mermaid = [f"flowchart {'LR' if self.direction=='LR' else 'TD'}"]
        for key, item in self.nodes.items():
            label = html.escape(item["label"], quote=True).replace("\n", "<br/>")
            if item["shape"] == "diamond":
                mermaid.append(f'    {key}{{"{label}"}}')
            else:
                mermaid.append(f'    {key}["{label}"]')
        for edge in self.edges:
            arrow = "-.->" if edge["dashed"] else "-->"
            label = html.escape(edge["label"], quote=True).replace("\n", "<br/>")
            mermaid.append(f'    {edge["a"]} {arrow}{"|"+label+"|" if label else ""} {edge["b"]}')
        (OUT / "source" / f"{self.slug}.mmd").write_text("\n".join(mermaid)+"\n", encoding="utf-8")
        logs = []
        for fmt in ("svg", "png"):
            result = subprocess.run([str(DOT), f"-T{fmt}", "-Gdpi=130", str(target), "-o", str(OUT/"diagrams"/f"{self.slug}.{fmt}")], capture_output=True, text=True, check=True)
            logs.append(result.stderr)
        assert not any("warning" in s.lower() or "error" in s.lower() for s in logs), logs
        root = ET.parse(OUT/"diagrams"/f"{self.slug}.svg").getroot()
        assert root.tag.endswith("svg")
        with Image.open(OUT/"diagrams"/f"{self.slug}.png") as im:
            assert im.width > 200 and im.height > 150
            dimensions = [im.width, im.height]
        return dict(id=self.slug, title=self.title, caption=self.caption,
                    nodes=len(self.nodes), edges=len(self.edges), png_pixels=dimensions)


def define_graphs():
    g=Graph("A1-deployment", "A1 | Buildable single-region architecture", "Render compute with managed synchronous Multi-AZ PostgreSQL. Render Postgres asynchronous HA is only a separately disclosed sandbox shortcut.", "TB")
    g.n("buyer","Buyer / merchant\nTypeScript + React\nAG Studio + Bryntum")
    g.n("edge","CDN / WAF / rate limits\nOIDC session validation")
    g.n("api","FastAPI modular domain service\nAssembly + PayGuard\nversioned offers and approval", "core", group="Render: one region")
    g.n("db","Managed PostgreSQL primary\nversions / consent / operation intents\ninbox / outbox / fulfillment", "core", "cylinder", group="Financial durability: one region")
    g.n("worker","Bounded worker\npayment dispatch + reconciliation\nevidence / downstream jobs", "core", group="Render: one region")
    g.n("hook","Webhook ingress\nraw signature verification\ntenant binding and deduplication", "core", group="Render: one region")
    g.n("standby","Synchronous standby in another AZ\nmanaged failover; write-latency cost\nnot a read-scaling replica", "core", group="Financial durability: one region")
    g.n("backup","Encrypted PITR / backups\nrestore drills and restricted keys\nregional disaster is a separate recovery event", "async", group="Financial durability: one region")
    g.n("ai","Astropods\nread-only extraction proposals\nno payment credentials", "ai", group="Scoped external capabilities")
    g.n("facts","Channel3 + Kernel\nproduct candidates / permitted pages\nuntrusted until checked", "ai", group="Scoped external capabilities")
    g.n("search","Elastic\nrebuildable evidence index", "async", group="Scoped external capabilities")
    g.n("zap","Zapier\napproved setup-task handoff", "async", group="Scoped external capabilities")
    g.n("pp","PayPal Sandbox\ncreate / buyer approval / capture\nresource read-back", "core")
    g.n("tests","Isolated Counterexample\nAPIMatic development context\nPostman regressions", "test")
    g.e("buyer","edge");g.e("edge","api");g.e("api","db","commit")
    g.e("db","worker","outbox",True);g.e("worker","pp","PayPal API")
    g.e("pp","hook","signed events",True);g.e("hook","db","verified inbox")
    g.e("db","standby","synchronous replication")
    g.e("db","backup","WAL / restore points",True)
    g.e("api","ai","extract");g.e("worker","facts","retrieve")
    g.e("facts","db","accepted facts",True);g.e("db","search","projection",True)
    g.e("worker","zap","consented task",True)
    g.e("tests","api","owned test environment only",True)

    g=Graph("A2-purchase-flow", "A2 | Purchase, approval and payment flow", "Internal approval and PayPal buyer approval are separate. Remote calls occur outside database transactions.", "TB")
    for key,label,kind,shape in [
        ("intent","1. Buyer supplies outcome, budget and deadline","plain","box"),
        ("facts","2. AI proposes requirements and product facts\nretain provenance and critical unknowns","ai","box"),
        ("check","3. Deterministic configuration and readiness checks","core","box"),
        ("valid","Critical constraints satisfied?","core","diamond"),
        ("revise","Show conflict / unknown / useful repair\nuser or trusted evidence resolves it","risk","box"),
        ("offer","4. Freeze merchant offer and material manifest\nmerchant / variant / quantity / total / currency / expiry","core","box"),
        ("approve","5. Authenticated user accepts exact terms\nstore consent and policy version","core","box"),
        ("create","6. Persist order-create intent, then call PayPal\nstable create key; store provider order ID","core","box"),
        ("buyerpp","7. Buyer approves the order at PayPal\nbrowser callback is a signal, not payment evidence","plain","box"),
        ("commit","8. Recheck material version and authority\natomic budget / inventory reservation + capture intent","core","box"),
        ("send","9. Worker dispatches capture outside DB transaction\noriginal order / body hash / stable capture key","core","box"),
        ("result","Trusted outcome?","core","diamond"),
        ("unknown","Unknown: retain reservation and operation\nread back / exact retry under provider contract\nnever mint replacement authority on timeout","risk","box"),
        ("declined","Terminal no-effect outcome\nrecord refusal; release only justified reservations\nshow next action without fulfillment","risk","box"),
        ("confirmed","10. Record verified completed capture\nmatch merchant, amount and currency","core","box"),
        ("outbox","11. Commit fulfillment outbox atomically\nunique purchase commitment + replay-safe consumer","async","box"),
        ("task","12. Approved external setup task\nindependent from financial success","async","box")]:g.n(key,label,kind,shape)
    for a,b in [("intent","facts"),("facts","check"),("check","valid"),("valid","offer"),("offer","approve"),("approve","create"),("create","buyerpp"),("buyerpp","commit"),("commit","send"),("send","result"),("result","confirmed"),("confirmed","outbox"),("outbox","task")]:g.e(a,b)
    g.e("valid","revise","no");g.e("revise","facts","new version");g.e("result","unknown","ambiguous");g.e("unknown","result","resource evidence")
    next(e for e in g.edges if e["a"]=="result" and e["b"]=="confirmed")["label"]="completed capture"
    g.e("result","declined","terminal no effect")

    g=Graph("A3-capture-state", "A3 | Capture-operation state machine", "State applies to one logical capture operation. Refunds are separate capture-linked operations; they do not rewind this machine.", "TB")
    for key,label,kind in [
        ("prepared","PREPARED\nbuyer-approved provider order + manifest","core"),
        ("invalid","INVALIDATED / EXPIRED\npre-dispatch cancellation or terms changed","risk"),
        ("dispatch","DISPATCHING\nintent and reservation durable before call","core"),
        ("complete","COMPLETED\nverified provider evidence","async"),
        ("failed","TERMINAL_NO_EFFECT\nprovider contract establishes no capture","plain"),
        ("unknown","UNKNOWN\noutcome unresolved; reserve remains","risk"),
        ("reconcile","RECONCILING\nread authoritative resource / supported exact retry","core"),
        ("review","REVIEW_REQUIRED\nretention expired or result cannot be established","risk"),
        ("fulfill","Fulfillment outbox / status projection\nindependent idempotent effect boundary","async")]:g.n(key,label,kind)
    g.e("prepared","dispatch","atomic final checks / reserve")
    g.e("prepared","invalid","revoked, expired or changed")
    g.e("dispatch","complete","verified success");g.e("dispatch","failed","conclusive refusal")
    g.e("dispatch","unknown","timeout / crash / response loss")
    g.e("unknown","reconcile");g.e("reconcile","complete","capture confirmed")
    g.e("reconcile","failed","terminal no-effect evidence")
    g.e("reconcile","unknown","still ambiguous")
    g.e("reconcile","review","cannot safely determine outcome")
    g.e("complete","fulfill","commit with result",True)

    g=Graph("A4-data-model", "A4 | Authoritative data model", "Tenant-scoped keys and immutable versions. Relationship labels describe cardinality; all foreign keys also carry tenant identity.", "TB")
    records={
        "tenant":"TENANT / ACTOR / POLICY\ntenant_id + actor_id + policy_version",
        "config":"CONFIGURATION_VERSION\nrequirements / accepted facts / rule results",
        "evidence":"EVIDENCE\nsource / exact variant / retrieved_at / digest",
        "offer":"OFFER_VERSION\ncanonical material manifest / expiry\namount_minor NUMERIC(38,0) + currency + scale",
        "approval":"APPROVAL\nactor / offer_version / policy_version\naccepted_at / revoked_at / expires_at",
        "purchase":"PURCHASE\nbusiness_intent_id UNIQUE per tenant\ncurrent operation / committed manifest",
        "budget":"BUDGET_RESERVATION\npolicy scope + operation identity\nno release on timeout alone",
        "inventory":"INVENTORY_RESERVATION\nmerchant SKU + quantity + operation\nreserve stock atomically; retain while ambiguous",
        "operation":"PAYMENT_OPERATION\nkind / request_key / body_hash / state\nprovider_order_id / capture_id / version",
        "inbox":"PROVIDER_INBOX\nmerchant_app + event_id UNIQUE\nsignature result / raw payload reference",
        "outbox":"OUTBOX + EFFECT_COMMITMENT\npurchase + effect_kind UNIQUE\ndelivery attempts / remote receipt ID",
        "audit":"AUDIT / OBSERVATIONS\nappend-only events / rule versions\nredacted payload reference + correlation IDs",
        "test":"TEST_RUN + SCENARIO\ncode revision / independent oracle version\nsynthetic or real-sandbox provenance"}
    for k,v in records.items():g.n(k,v,"test" if k=="test" else "core","box")
    for a,b,l in [("tenant","config","1 : many"),("config","evidence","many : many via fact refs"),("config","offer","1 : many"),("offer","approval","1 : many"),("approval","purchase","accepted authority"),("purchase","operation","1 : many operation kinds"),("purchase","budget","reservations"),("purchase","inventory","stock commitments"),("operation","inbox","correlated provider evidence"),("operation","outbox","atomic result + outbox"),("operation","audit","1 : many"),("test","audit","isolated evidence IDs")]:g.e(a,b,l)

    g=Graph("A5-security-boundaries", "A5 | Trust and authority boundaries", "OWASP-aligned control design, not a security certification. External content never grants authority.", "TB")
    g.n("human","Buyer / merchant / operator\nOIDC session; step-up for sensitive roles")
    g.n("web","Public edge\nWAF / request limits / CSRF / CSP",group="Internet-facing boundary")
    g.n("auth","Domain authorization\nobject + property + function checks\ntenant-scoped queries and RLS defense", "core",group="Trusted financial boundary")
    g.n("policy","PayGuard\nversion-bound approval\nbudget / expiry / material-term checks", "core",group="Trusted financial boundary")
    g.n("egress","Payment adapter / secrets\nfixed PayPal hosts and scoped credentials\nno model or test-runtime access", "core",group="Trusted financial boundary")
    g.n("vault","Secrets manager / KMS\nrotation / access audit", "core",group="Trusted financial boundary")
    g.n("db","Authoritative SQL\nleast-privilege roles / encryption\nbackup and restore checks", "core","cylinder",group="Trusted financial boundary")
    g.n("untrusted","Product pages / API output / uploads\nallowlisted acquisition + size limits\nSSRF defenses and malware checks", "risk",group="Untrusted evidence boundary")
    g.n("model","Astropods model stage\nstructured proposals only\nno credentials or arbitrary execution", "ai",group="Untrusted evidence boundary")
    g.n("validator","Fact and constraint validation\ncritical unknowns stay unresolved\naccepted evidence retains provenance", "ai",group="Untrusted evidence boundary")
    g.n("pp","PayPal\nprovider authentication + payment")
    g.n("hook","Webhook verifier\nraw bytes / app binding / inbox dedupe", "core")
    g.n("test","Counterexample environment\nseparate secrets / DB / namespace\nsandbox-only endpoint policy", "test")
    g.e("human","web");g.e("web","auth");g.e("auth","policy");g.e("policy","db")
    g.e("policy","egress","approved durable operation");g.e("vault","egress","scoped secret")
    g.e("egress","pp");g.e("untrusted","model","data only");g.e("model","validator")
    g.e("validator","auth","proposed facts, never permission")
    g.e("pp","hook","signed event",True);g.e("hook","db","verified durable inbox")
    g.e("test","web","owned test target only",True)

    g=Graph("A6-counterexample", "A6 | Independent verification harness", "Production rules may be shared across UI/server. The test oracle must not simply call those same production checks and certify itself.", "TB")
    g.n("spec","Reviewed business contract\nindependently labeled expected outcomes", "test")
    g.n("proposal","Bounded scenario proposal\nAI or fixed templates\npinned prompt / seed / budget", "ai")
    g.n("runner","Typed legal-scenario runner\ncontrolled local scheduler\nno arbitrary generated code", "test")
    g.n("target","Owned vulnerable / corrected fixture\nAssembly + PayGuard + merchant worker", "core")
    g.n("fault","Local fault hooks\nresponse drop / crash / event redelivery\nconcurrent dispatch / stale offer", "risk")
    g.n("provider","Mode explicitly chosen\nsynthetic model / recorded adapter\nor real PayPal Sandbox", "core")
    g.n("trace","Observed event history\nsource provenance and causal IDs", "test")
    g.n("oracle","Independent oracle\nhistory properties + reference expectations\npass / fail / invalid / inconclusive", "test")
    g.n("reduce","Trace reducer\npreserve prerequisites and same failure\nno global-minimum claim", "test")
    g.n("export","Postman + runner manifest\ncode and contract versions\nfails before / passes after fix", "async")
    g.e("spec","proposal");g.e("proposal","runner");g.e("runner","target");g.e("fault","target")
    g.e("target","provider");g.e("target","trace");g.e("provider","trace","independent resource observations");g.e("spec","oracle")
    g.e("trace","oracle");g.e("oracle","reduce","verified failure");g.e("reduce","runner","controlled rerun",True)
    g.e("reduce","export")

    g=Graph("B1-global-cells", "B1 | Regional cells and separate financial durability", "Reference production design. Repeat cells by tenant/authority scope; do not interpret three drawn cells as a capacity benchmark.", "TB")
    g.n("users","Global buyers / merchants\nCDN content + localized UI")
    g.n("edge","Edge WAF / bot controls / admission\nread routing differs from financial routing")
    g.n("routing","Strong ownership directory\ncell_id + epoch + tenant scope\nversioned routing; stale writers rejected", "core")
    for k,region in [("c1","Region A"),("c2","Region B"),("c3","Region C")]:
        g.n(k,f"{region}: Render services\nstateless domain API + worker pools\nlocal queues, quotas and circuit breakers", "core",group="Regional compute cells")
    g.n("financial","Per-cell financial SQL cluster\nCockroachDB reference profile\nSERIALIZABLE; region-survival topology", "core","cylinder")
    g.n("replica","Synchronous quorum across 3 permitted regions\nregion-survival replica placement\nadditional write RTT is accepted", "core")
    g.n("reads","Regional catalogue / Elastic projections\nCDN + disposable caches\nversioned bounded-stale reads", "async")
    g.n("provider","PayPal\nquota-aware regional egress\noriginal business operation identity", "core")
    g.n("control","Release / identity / secrets / telemetry\nAPIMatic + Postman + Counterexample\ncontrol-plane outage does not rewrite payments", "test")
    g.e("users","edge");g.e("edge","routing","financial commands")
    for k in ["c1","c2","c3"]:g.e("routing",k,"current owner");g.e(k,"financial","strong SQL")
    g.e("financial","replica","quorum commit")
    g.e("edge","reads","browse / compare")
    g.e("financial","reads","redacted projection",True)
    for k in ["c1","c2","c3"]:g.e(k,"provider","API quota")
    g.e("control","routing","reviewed config",True)

    g=Graph("B2-consistency-ownership", "B2 | Consistency, budgets and ownership", "CAP is selected per operation. Serializable transactions do not atomically include PayPal or a fulfillment provider.", "TB")
    g.n("command","Authenticated financial command\nmerchant + purchase + authority scope")
    g.n("owner","Resolve authority owner\ntenant / budget / cell / epoch", "core")
    g.n("quorum","Current owner and quorum reachable?", "core","diamond")
    g.n("tx","Short SERIALIZABLE transaction\ncheck material version + live policy\nreserve budget + unique operation + outbox", "core")
    g.n("reject","Pause financial command\n503 / explicit pending\nnever authorize from stale cache", "risk")
    g.n("adapter","Commit first; call PayPal afterward\nfixed operation key and body hash\nretry DB-only code separately", "core")
    g.n("budget","One owner for each shared budget\nco-locate budget and purchases\nno eventually consistent global spend counter", "core")
    g.n("browse","Browsing / search\nregional cache and projections\nshow evidence version and age", "async")
    g.n("partition","Network partition\nmajority may progress\nminority cannot dispatch", "risk")
    g.e("command","owner");g.e("owner","quorum");g.e("quorum","tx","yes");g.e("quorum","reject","no")
    g.e("budget","tx","same authority scope");g.e("tx","adapter","durable intent")
    g.e("partition","quorum","financial consistency first")
    g.e("partition","browse","available with bounded staleness",True)

    g=Graph("B3-traffic-surges", "B3 | Traffic admission and backpressure", "Bounded queues, fair quotas and provider limits control load. More workers do not increase PayPal's contracted capacity.", "TB")
    g.n("traffic","Peak traffic / bot traffic / retries")
    g.n("edge","CDN / WAF / per-tenant quotas\nrequest coalescing and deduplication")
    g.n("classify","Classify work","core","diamond")
    g.n("read","Browse / search\ncache / stale-while-revalidate\nshed costly optional views", "async")
    g.n("ai","AI preparation\nsmall concurrency pool / token budget\ncancel outdated drafts", "ai")
    g.n("pay","Financial commands\nvalidate auth + unique request + current version\nreserve only after bounded admission", "core")
    g.n("queue","Durable bounded queue / outbox\nper-tenant fairness + expiry\n202 means queued, not paid", "core")
    g.n("workers","Independent payment worker pool\nconnection caps + measured scaling\nrevalidate authority before dispatch", "core")
    g.n("pp","PayPal quota / circuit breaker\nRetry-After + jitter + bounded retries", "core")
    g.n("reconcile","Reserved reconciliation capacity\nunknown outcomes cannot starve\nverified webhook inbox processed first", "core")
    g.n("overflow","Reject excess / expire safely\n429 with retry guidance\nno unbounded in-memory backlog", "risk")
    g.n("optional","External tasks / analytics / evidence refresh\nlower priority; isolated quotas", "async")
    g.e("traffic","edge");g.e("edge","classify")
    for k in ["read","ai","pay"]:g.e("classify",k)
    g.e("pay","queue");g.e("queue","workers");g.e("workers","pp")
    g.e("queue","overflow","full or expired");g.e("reconcile","pp","separate budget")
    g.e("queue","optional","nonfinancial pool",True)

    g=Graph("B4-failover", "B4 | Fenced failover and ambiguous payments", "Fencing stops new stale dispatch through our gateway. It cannot cancel a request already accepted by PayPal.", "TB")
    g.n("fault","Region / worker / network failure", "risk")
    g.n("pause","Gate financial dispatch\nold owner loses quorum / authority\nkeep browsing through projections", "core")
    g.n("quorum","Financial journal quorum available?", "core","diamond")
    g.n("stop","No quorum: remain unavailable for money\nno blind promotion from stale backup", "risk")
    g.n("elect","Recover durable state and owner epoch\nnew worker claims using CAS\nold owner rejected by current gateway", "core")
    g.n("inflight","Read unresolved operation intents\nknown provider IDs + original request keys", "core")
    g.n("provider","Query authoritative PayPal resources\nsupported exact retry within retention\nno fresh replacement on ambiguity", "core")
    g.n("outcome","Outcome established?", "core","diamond")
    g.n("complete","Commit observed result + effect outbox\ndeduplicate downstream commitment", "async")
    g.n("review","Hold reservation / operator review\nretain correlation and evidence\nrecovery duration is not guaranteed", "risk")
    g.n("resume","Resume bounded new traffic\ncheck retry backlog and provider quotas", "async")
    g.e("fault","pause");g.e("pause","quorum");g.e("quorum","stop","no")
    g.e("quorum","elect","yes");g.e("elect","inflight");g.e("inflight","provider");g.e("provider","outcome")
    g.e("outcome","complete","yes");g.e("outcome","review","no");g.e("complete","resume")

    g=Graph("B5-funds-reconciliation", "B5 | Funds boundary and reconciliation", "Assembly Proof stores instructions and financial references. PayPal / the licensed provider handles funds; this design is not a custodial wallet.", "TB")
    g.n("payer","Buyer / payment method")
    g.n("payee","Participating merchant")
    g.n("pp","PayPal payment / settlement systems\nactual money movement and provider ledger", "core")
    g.n("app","Assembly Proof\nnoncustodial purchase authority\namount + currency + provider IDs", "core")
    g.n("capture","Capture observations\ncompleted / pending / refused / unknown", "core")
    g.n("refund","Separate refund operations\nsource capture + operation ID\npartial and pending amounts tracked", "core")
    g.n("recon","Reconciliation worker\nprovider facts vs application records\nexceptions retained and assigned", "core")
    g.n("projection","Merchant financial projection\nconfirmed captured / refunded amounts\nnot a spendable wallet balance", "async")
    g.n("currency","Money representation\ninteger minor units + ISO currency + scale\nchecked bounds; no float; no implicit FX", "plain")
    g.n("custody","If customer-fund custody is required\nseparate regulated product, ledger, treasury\nand safeguarding architecture required", "risk")
    g.e("payer","pp","payment rail");g.e("pp","payee","settlement per provider terms")
    g.e("app","pp","approved operations");g.e("pp","capture","resource evidence",True)
    g.e("app","refund","explicit approved refund");g.e("refund","pp")
    g.e("capture","recon");g.e("refund","recon");g.e("recon","projection")
    g.e("currency","app","validated amount model");g.e("custody","app","outside current scope",True)

    g=Graph("B6-security-operations", "B6 | Regional security and operational isolation", "Use versioned OWASP ASVS requirements, API threat tests and GenAI controls. No diagram proves the absence of vulnerabilities.")
    g.n("edge","Public edge\nWAF / auth / abuse prevention\nper-tenant and per-action quotas",group="Public boundary")
    g.n("domain","Domain cells\nobject and field authorization\ntenant-scoped commands", "core",group="Service identity boundary")
    g.n("money","Payment egress\nleast privilege / rotating secrets\nallowlisted destinations / current epoch", "core",group="Financial boundary")
    g.n("sql","Quorum financial SQL\nstrict state reads / encrypted transport\nkey and data residency policy", "core","cylinder",group="Financial boundary")
    g.n("ai","AI / evidence workers\nno financial credentials\noutput validation / SSRF defense", "ai",group="Lower-trust compute")
    g.n("tests","Counterexample cells\nseparate identities and databases\nproduction endpoints blocked", "test",group="Lower-trust compute")
    g.n("ops","Operator / release control\nMFA + privileged approval\nsigned artifacts / dependency inventory", "test")
    g.n("telemetry","Redacted traces and security events\nseparate access-controlled audit sink\nimmutable retention only where supported", "async")
    g.n("backup","Encrypted backups / restore drills\nkey access and deletion policy\nquorum replication does not replace backups", "async")
    g.n("response","Incident response\nkill financial dispatch / isolate tenant\nrotate keys / investigate / reconcile", "risk")
    g.e("edge","domain");g.e("domain","money");g.e("domain","sql")
    g.e("ai","domain","typed proposed data")
    g.e("ops","domain","reviewed release",True)
    g.e("domain","telemetry","redacted events",True);g.e("money","telemetry","operation evidence",True)
    g.e("sql","backup","encrypted backup",True);g.e("telemetry","response","alerts",True)
    g.e("response","money","scoped stop control")

    g=Graph("S1-sponsor-ownership", "S1 | All ten sponsors with bounded responsibilities", "The same ownership split applies to both architectures. A meaningful integration needs a working contribution; these remain proposed.", "LR")
    g.n("product","Assembly Proof\none merchant purchasing outcome", "core")
    tools=[("ag","AG Grid / AG Studio\nlinked evidence and conflict workspace","plain"),
           ("bry","Bryntum\nreadiness and setup dependencies","plain"),
           ("channel","Channel3\nreal candidate and variant discovery","ai"),
           ("astro","Astropods\nbounded extraction stage and traces","ai"),
           ("elastic","Elastic\nrebuildable evidence / incident search","async"),
           ("kernel","Kernel\npermitted pages + owned browser QA","ai"),
           ("render","Render\nregional app and worker deployments","core"),
           ("zap","Zapier\napproved post-payment setup task","async"),
           ("apimatic","APIMatic\nPayPal adapter development context","test"),
           ("postman","Postman\nindependent API regression evidence","test")]
    categories={"interface":["ag","bry"], "evidence_ai":["channel","astro","elastic","kernel"], "delivery":["render","zap"], "engineering":["apimatic","postman"]}
    names={"interface":"Product interface", "evidence_ai":"Evidence and AI", "delivery":"Hosting and follow-through", "engineering":"Development and verification"}
    for category,keys in categories.items():
        g.n(category,names[category],"test" if category=="engineering" else "plain")
        g.e("product",category,"bounded responsibility",category=="engineering")
        for key,label,color in tools:
            if key in keys:
                g.n(key,label,color,group=names[category])
                g.e(category,key,"role",key in ["apimatic","postman","zap","elastic"])
    g.n("authority","PayGuard + SQL + PayPal adapter\nfinancial authority remains here", "core")
    g.e("product","authority","no sponsor may bypass this boundary")

    g=Graph("S2-value-and-measurement", "S2 | Business value and loss guardrails", "Hypotheses to measure in a merchant pilot. No conversion lift, loss reduction, profit or first-prize probability is established.", "TB")
    g.n("goal","Increase verified useful purchases\nsubject to financial safety and operating cost", "core")
    g.n("quality","Assembly\nconfiguration task completion\nfalse-feasible and unknown rates", "ai")
    g.n("authority","PayGuard\nunauthorized effects observed\nlegitimate actions incorrectly blocked", "core")
    g.n("reliability","Counterexample\nverified defects + reproducibility\ntime to useful regression", "test")
    g.n("outcomes","Merchant outcomes\npaid purchase completion / returns\nsupport effort / repeat usage", "async")
    g.n("cost","Operating guardrails\nmodel and browser usage\nprovider calls / infrastructure / support", "plain")
    g.n("net","Merchant contribution measurement\nrevenue less relevant costs, fees and realized losses\nrequires actual cost and cohort data", "core")
    g.n("pilot","Controlled pilot / comparable cohorts\ndefine denominators and observation windows\nmeasure false blocks as well as failures", "plain")
    for k in ["quality","authority","reliability"]:g.e("goal",k)
    for k in ["quality","authority","reliability"]:g.e(k,"outcomes","hypothesized mechanism")
    g.e("outcomes","net");g.e("cost","net");g.e("pilot","net","actual evidence required")


def build():
    for folder in [OUT, OUT/"source", OUT/"diagrams", OUT/"qa"]:folder.mkdir(parents=True,exist_ok=True)
    define_graphs()
    assert len(GRAPHS)==14
    results=[g.render() for g in GRAPHS]
    (OUT/"diagram-manifest.json").write_text(json.dumps({"as_of":"2026-11-01", "status":"Reference designs, not implemented or load-tested", "diagrams":results},indent=2),encoding="utf-8")
    gallery=["# Assembly Proof: two architectures and 14 diagrams", "", "Reference designs dated November 1, 2026. Architecture A is the buildable sandbox profile; Architecture B is a production evolution requiring engineering, security and load validation. See ARCHITECTURES.md for contracts, limitations and sources.", ""]
    for d in results:
        gallery += [f"## {d['title']}","",d["caption"],"",f"![{d['title']}](diagrams/{d['id']}.png)","",f"[Vector SVG](diagrams/{d['id']}.svg) | [Editable Graphviz](source/{d['id']}.dot) | [Mermaid flow source](source/{d['id']}.mmd)",""]
    (OUT/"DIAGRAMS.md").write_text("\n".join(gallery),encoding="utf-8")
    for batch in range(0,len(results),4):
        sheet=Image.new("RGB",(1700,1300),"#DDE7EC")
        draw=ImageDraw.Draw(sheet)
        for offset, item in enumerate(results[batch:batch+4]):
            with Image.open(OUT/"diagrams"/f"{item['id']}.png") as source:
                source=source.convert("RGB");source.thumbnail((820,600))
                col,row=offset%2,offset//2
                x=col*850+(850-source.width)//2;y=row*650+35
                sheet.paste(source,(x,y));draw.text((col*850+14,row*650+12),item["id"],fill="#142D40")
        sheet.save(OUT/"qa"/f"contact-{batch+1:02d}.png")
    print(json.dumps({"directory":str(OUT),"count":len(results),"dimensions":{r['id']:r['png_pixels'] for r in results}},indent=2))


if __name__=="__main__":
    build()
