"use strict";

const state = { catalogue: [], configuration: null, check: null, purchase: null, mode: null };
const $ = id => document.getElementById(id);
const token = () => $("token").value.trim();
const money = cents => `$${(cents / 100).toFixed(2)}`;

function toast(message, error = false) {
  const el = $("toast");
  el.textContent = message;
  el.className = error ? "error" : "";
  el.style.display = "block";
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { el.style.display = "none"; }, 5500);
}

async function api(path, method = "GET", body = undefined) {
  const headers = { "Content-Type": "application/json" };
  if (token()) headers["X-Demo-Token"] = token();
  const response = await fetch(path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  const data = await response.json();
  if (!response.ok && response.status !== 202) {
    const detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail || data);
    throw new Error(detail);
  }
  return data;
}

function currentConfig() {
  const selections = state.catalogue.map(product => ({
    product_id: product.id,
    quantity: Number($("qty-" + product.id).value)
  })).filter(item => item.quantity > 0);
  return {
    requirements: { people: Number($("people").value), budget_cents: Math.round(Number($("budget").value) * 100), currency: "USD" },
    selections
  };
}

function setConfig(config) {
  $("people").value = config.requirements.people;
  $("budget").value = config.requirements.budget_cents / 100;
  for (const product of state.catalogue) $("qty-" + product.id).value = 0;
  for (const line of config.selections) $("qty-" + line.product_id).value = line.quantity;
  invalidateCheck();
}

function invalidateCheck() {
  state.check = null;
  $("result").textContent = "Run the check to verify these exact selections.";
  updateActions();
}

function renderCatalogue() {
  const root = $("catalogue");
  root.replaceChildren();
  for (const product of state.catalogue) {
    const row = document.createElement("div"); row.className = "product";
    const info = document.createElement("div");
    const name = document.createElement("strong"); name.textContent = product.name;
    const detail = document.createElement("small"); detail.textContent = `${product.kind.toUpperCase()} · ${money(product.price_cents)} · INVENTED DEMO OFFER`;
    info.append(name, detail);
    const quantity = document.createElement("input");
    quantity.type = "number"; quantity.min = "0"; quantity.max = "16"; quantity.value = "0";
    quantity.id = "qty-" + product.id;
    quantity.setAttribute("aria-label", `Quantity of ${product.name}`);
    quantity.addEventListener("input", invalidateCheck);
    row.append(info, quantity); root.append(row);
  }
}

function renderCheck(result) {
  const root = $("result"); root.replaceChildren();
  const summary = document.createElement("div"); summary.className = "summary";
  const badge = document.createElement("span"); badge.className = "pill " + (result.ready ? "pass" : "fail");
  badge.textContent = result.ready ? "COMPATIBLE" : "NEEDS REPAIR";
  const total = document.createElement("span"); total.textContent = `Total ${money(result.total_cents)} / ${result.currency}`;
  summary.append(badge, total);
  const checks = document.createElement("div"); checks.className = "checks";
  for (const item of result.checks) {
    const card = document.createElement("div"); card.className = "check " + item.status;
    const title = document.createElement("strong"); title.textContent = `${item.status.toUpperCase()} · ${item.code.replaceAll("_", " ")}`;
    const detail = document.createElement("p"); detail.textContent = item.detail;
    card.append(title, detail);
    if (item.status !== "pass" && item.repair) {
      const repair = document.createElement("small"); repair.textContent = "Repair: " + item.repair; card.append(repair);
    }
    checks.append(card);
  }
  root.append(summary, checks);
}

function renderPurchase() {
  const root = $("purchase"); root.replaceChildren();
  const purchase = state.purchase;
  if (!purchase) { root.textContent = "A compatible kit can be prepared for checkout."; return; }
  const facts = document.createElement("div"); facts.className = "facts";
  for (const [label, value] of [["STATE", purchase.status], ["EXACT TOTAL", `${money(purchase.total_cents)} ${purchase.currency}`], ["OFFER EXPIRES", new Date(purchase.expires_at).toLocaleTimeString()]]) {
    const box = document.createElement("div"); box.className = "fact";
    const name = document.createElement("span"); name.textContent = label;
    const text = document.createElement("b"); text.textContent = value;
    box.append(name, text); facts.append(box);
  }
  root.append(facts);
  const digest = document.createElement("div"); digest.className = "digest";
  digest.textContent = `Merchant: ${purchase.snapshot.merchant_id} · Frozen terms SHA-256: ${purchase.digest}`;
  root.append(digest);
  const frozen = document.createElement("p"); frozen.className = "hint";
  frozen.textContent = "This purchase remains frozen if you edit the kit above. Start a new purchase for changed terms.";
  root.append(frozen);
  if (purchase.approval_url && purchase.status === "AWAITING_BUYER" && state.mode === "sandbox") {
    const link = document.createElement("a"); link.href = purchase.approval_url; link.textContent = "Open PayPal Sandbox approval";
    link.target = "_self"; link.className = "paypal-approval-link"; root.append(document.createElement("br"), link);
  }
  if (purchase.last_error) {
    const issue = document.createElement("p"); issue.textContent = purchase.last_error; issue.className = "purchase-error"; root.append(issue);
  }
}

function updateActions() {
  $("prepare").disabled = !state.check?.ready || !!state.purchase;
  $("approve").disabled = !state.purchase || state.purchase.status !== "DRAFT";
  $("buyer").disabled = state.mode !== "mock" || !state.purchase || state.purchase.status !== "AWAITING_BUYER" || state.purchase.mock_buyer_approved;
  $("capture").disabled = !state.purchase || state.purchase.status !== "AWAITING_BUYER" || (state.mode === "mock" && !state.purchase.mock_buyer_approved);
  $("reconcile").disabled = !state.purchase || !["ORDER_UNKNOWN", "CAPTURE_UNKNOWN", "AWAITING_BUYER"].includes(state.purchase.status);
  renderPurchase();
}

async function refreshAudit() {
  if (!state.purchase) return;
  const events = await api(`/api/purchases/${state.purchase.id}/audit`);
  const root = $("audit"); root.replaceChildren();
  for (const event of events) {
    const row = document.createElement("p"); row.textContent = `${new Date(event.at).toLocaleTimeString()} · ${event.type}`;
    root.append(row);
  }
}

async function action(work) {
  try { await work(); updateActions(); await refreshAudit(); }
  catch (error) { toast(error.message, true); }
}

$("token").value = sessionStorage.getItem("assembly-token") || "";
$("token").addEventListener("change", () => sessionStorage.setItem("assembly-token", token()));
for (const id of ["people", "budget"]) $(id).addEventListener("input", invalidateCheck);
$("restart").addEventListener("click", () => {
  state.purchase = null;
  state.check = null;
  sessionStorage.removeItem("assembly-purchase");
  history.replaceState(null, "", "/");
  $("audit").replaceChildren();
  $("result").textContent = "Run the check to see specific conflicts and repairs.";
  updateActions();
});
$("interpret").addEventListener("click", () => action(async () => {
  const data = await api("/api/plan", "POST", { text: $("prompt").value });
  setConfig(data.proposal);
  state.check = data.check;
  renderCheck(data.check);
  $("ai-state").textContent = data.needs_confirmation
    ? "The agent filled missing requirements. Review the fields and kit before payment."
    : "The agent proposed this kit. The separate checker evaluated it; review every item.";
  toast(data.check.ready ? "Agent proposal passed the configuration check." : "Agent proposal needs repair before checkout.");
}));
$("check").addEventListener("click", () => action(async () => {
  state.configuration = currentConfig(); state.check = await api("/api/check", "POST", state.configuration);
  renderCheck(state.check);
}));
$("prepare").addEventListener("click", () => action(async () => {
  const config = currentConfig();
  const latest = await api("/api/check", "POST", config);
  if (!latest.ready || latest.digest !== state.check.digest) throw new Error("Kit changed; check it again.");
  state.purchase = await api("/api/purchases", "POST", { configuration: config, intent_key: crypto.randomUUID() });
  sessionStorage.setItem("assembly-purchase", state.purchase.id);
  toast("Exact purchase terms frozen for approval.");
}));
$("approve").addEventListener("click", () => action(async () => {
  state.purchase = await api(`/api/purchases/${state.purchase.id}/approve`, "POST", { digest: state.purchase.digest });
  toast(state.purchase.status === "AWAITING_BUYER" ? "Order created. Buyer approval is next." : "Order outcome needs review.");
}));
$("buyer").addEventListener("click", () => action(async () => {
  state.purchase = await api(`/api/purchases/${state.purchase.id}/mock-buyer-approve`, "POST");
  toast("Mock buyer approved. This is not a real PayPal payment.");
}));
$("capture").addEventListener("click", () => action(async () => {
  state.purchase = await api(`/api/purchases/${state.purchase.id}/capture`, "POST");
  toast(state.purchase.status === "CAPTURED" ? "Exact capture verified." : "Capture outcome unresolved. Reconcile it.");
}));
$("reconcile").addEventListener("click", () => action(async () => {
  state.purchase = await api(`/api/purchases/${state.purchase.id}/reconcile`, "POST");
  toast(state.purchase.status === "CAPTURED" ? "Capture verified." : "No verified capture yet.");
}));
$("counterexamples").addEventListener("click", () => action(async () => {
  const report = await api("/api/counterexamples");
  const root = $("counterexample-results"); root.replaceChildren();
  for (const item of report.cases) {
    const row = document.createElement("p");
    row.textContent = `${item.passed ? "PASS" : "FAIL"} · ${item.scenario} · ${JSON.stringify(item.observed)}`;
    row.className = item.passed ? "case-pass" : "case-fail";
    root.append(row);
  }
  toast(`${report.cases.filter(item => item.passed).length}/${report.cases.length} independent expectations met.`);
}));

(async () => {
  try {
    const [health, catalogue, examples] = await Promise.all([
      api("/api/health"), api("/api/catalogue"), api("/api/examples")]);
    state.mode = health.payment_mode; state.catalogue = catalogue.products;
    $("mode").textContent = health.payment_mode === "mock" ? "MOCK CHECKOUT" : "PAYPAL SANDBOX";
    $("interpret").disabled = !health.ai_configured;
    if (!health.ai_configured) $("ai-state").textContent = "AI planning needs OPENAI_API_KEY. Manual examples remain available.";
    renderCatalogue(); setConfig(examples.broken);
    $("broken").addEventListener("click", () => setConfig(examples.broken));
    $("repaired").addEventListener("click", () => setConfig(examples.repaired));
    const previous = new URLSearchParams(location.search).get("purchase") || sessionStorage.getItem("assembly-purchase");
    if (previous && token()) {
      state.purchase = await api(`/api/purchases/${previous}`);
      updateActions(); await refreshAudit();
      if (location.search.includes("paypal_return")) toast("PayPal returned. Capture only after server verifies buyer approval.");
    }
  } catch (error) { toast(error.message, true); }
})();
