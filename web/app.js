"use strict";

const state = {
  catalogue: [], check: null, purchase: null, mode: null, revision: 0, busy: false, repairGrid: null
};
let gridLibrary;
const $ = id => document.getElementById(id);
const token = () => $("token").value.trim();
const money = cents => `$${(cents / 100).toFixed(2)}`;

const sponsorRoles = {
  "AG Grid": "Compare repairs and their blockers",
  APIMatic: "Ground the PayPal timeout contract",
  Bryntum: "Visualize delivery and recording dates",
  Channel3: "Discover reference product variants",
  Postman: "Exercise checkout and replay",
};
api("/api/sponsors").then(status => {
  for (const [name, role] of Object.entries(sponsorRoles)) {
    const item = document.createElement("li");
    item.textContent = `${name} · ${role} · ${status[name]}`;
    $("sponsor-status").append(item);
  }
}).catch(error => { $("sponsor-status").textContent = error.message; });

for (const button of document.querySelectorAll("[data-evidence]")) {
  button.addEventListener("click", async () => {
    button.disabled = true;
    $("sponsor-result").textContent = "Checking reference evidence…";
    try {
      const { result } = await api(`/api/sponsors/evidence/${button.dataset.evidence}`, "POST");
      $("sponsor-result").textContent = Array.isArray(result) && !result.length
        ? "No matching reference evidence." : JSON.stringify(result, null, 2);
    } catch (error) {
      $("sponsor-result").textContent = error.message;
    } finally {
      button.disabled = false;
    }
  });
}

let setupScheduler;
$("show-schedule").addEventListener("click", async event => {
  const button = event.currentTarget;
  const arrival = $("arrival-day").valueAsNumber;
  const recording = $("setup-day").valueAsNumber;
  const output = $("schedule-status");
  setupScheduler?.destroy();
  setupScheduler = undefined;
  if (!Number.isFinite(arrival) || !Number.isFinite(recording)) {
    output.textContent = "Choose both dates.";
    return;
  }
  const day = 86400000;
  const localDate = value => {
    const date = new Date(value);
    return new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
  };
  const readiness = arrival + day <= recording ? "Ready for recording." : "Allow one day after delivery to set up.";
  output.textContent = readiness;
  button.disabled = true;
  try {
    const { Scheduler } = await import("/vendor/bryntum/scheduler.module.js");
    for (const file of ["scheduler.css", "stockholm-light.css"]) {
      const url = "/vendor/bryntum/" + file;
      if (document.querySelector(`link[href="${url}"]`)) continue;
      const theme = document.createElement("link");
      theme.rel = "stylesheet";
      theme.href = url;
      document.head.append(theme);
    }
    setupScheduler = new Scheduler({
      appendTo: $("setup-schedule"), height: 235, readOnly: true, viewPreset: "dayAndWeek",
      startDate: localDate(Math.min(arrival, recording) - day),
      endDate: localDate(Math.min(Math.max(arrival, recording) + 2 * day, Math.min(arrival, recording) + 31 * day)),
      columns: [{ text: "Milestone", field: "name", width: 130 }],
      resources: [{ id: 1, name: "Recording kit" }],
      events: [
        { id: 1, resourceId: 1, name: "Setup after delivery", startDate: localDate(arrival), endDate: localDate(arrival + day) },
        { id: 2, resourceId: 1, name: "First recording", startDate: localDate(recording), endDate: localDate(recording + day) }
      ]
    });
  } catch {
    output.textContent = readiness + " Bryntum Scheduler assets or trial activation are unavailable.";
  } finally {
    button.disabled = false;
  }
});

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
  state.revision++;
  state.check = null;
  $("result").textContent = "Run the check to verify these exact selections.";
  clearRepair();
  updateActions();
}

function clearRepair() {
  state.repairGrid?.destroy();
  state.repairGrid = null;
  $("repair-result").replaceChildren();
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

async function checkCurrentKit() {
  const revision = state.revision;
  const result = await api("/api/check", "POST", currentConfig());
  if (revision !== state.revision) return;
  state.check = result;
  clearRepair();
  renderCheck(result);
  $("proof").scrollIntoView();
}

function loadGrid() {
  if (!gridLibrary) {
    gridLibrary = new Promise(resolve => {
      const script = document.createElement("script");
      script.src = "/vendor/ag-grid-community.min.js";
      script.onload = () => resolve(window.agGrid);
      script.onerror = () => resolve(null);
      document.head.append(script);
    });
  }
  return gridLibrary;
}

function comparisonPanel(alternatives) {
  const details = document.createElement("details");
  const summary = document.createElement("summary");
  summary.textContent = "Compare checked alternatives";
  const grid = document.createElement("div");
  grid.className = "candidate-grid";
  const evidence = document.createElement("p");
  evidence.className = "candidate-evidence";
  evidence.setAttribute("aria-live", "polite");
  evidence.textContent = "Select a row to see why it passes or is blocked.";
  const rows = alternatives.map(option => ({
    ...option,
    layout: option.name + (option.amplifiers ? ` + ${option.amplifiers} headphone amp${option.amplifiers > 1 ? "s" : ""}` : ""),
    decision: option.ready ? "Compatible" : "Blocked",
  }));

  function showEvidence(row) {
    const reason = row.ready ? "All checks passed for this layout."
      : row.blockers.map(check => check.detail).join(" ");
    evidence.textContent = `${row.name}: ${reason}`;
  }

  // Keep the evidence readable if the optional local bundle isn't installed.
  for (const row of rows) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "preset-button";
    button.textContent = `${row.layout} · ${money(row.total_cents)} · ${row.decision}`;
    button.addEventListener("click", () => showEvidence(row));
    grid.append(button);
  }
  details.addEventListener("toggle", async () => {
    if (!details.open || state.repairGrid) return;
    const library = await loadGrid();
    if (!library || !details.open || !details.isConnected || state.repairGrid) return;
    grid.replaceChildren();
    state.repairGrid = library.createGrid(grid, {
      rowData: rows,
      columnDefs: [
        { field: "layout", headerName: "Interface and monitoring", minWidth: 165, flex: 2, wrapText: true, autoHeight: true },
        { field: "total_cents", headerName: "Total", width: 105, filter: "agNumberColumnFilter", valueFormatter: ({value}) => money(value) },
        { field: "decision", headerName: "Result", width: 115, filter: "agTextColumnFilter" },
      ],
      domLayout: "autoHeight",
      onRowClicked: event => showEvidence(event.data),
      onCellKeyDown: event => {
        if (event.event.key === "Enter") showEvidence(event.data);
      },
    });
  });
  details.append(summary, grid, evidence);
  return details;
}

function renderRepair(repair) {
  clearRepair();
  const root = $("repair-result");
  const heading = document.createElement("h3");
  if (!repair.proposal) {
    heading.textContent = "No compatible kit found within this budget";
    root.append(heading);
    if (repair.alternatives?.length) root.append(comparisonPanel(repair.alternatives));
    return;
  }
  heading.textContent = "Review the proposed changes";
  const price = document.createElement("p");
  const delta = repair.price_delta_cents;
  const difference = delta === 0 ? "same price" : `${money(Math.abs(delta))} ${delta > 0 ? "more" : "less"}`;
  price.textContent = `${money(repair.original.total_cents)} before · ${money(repair.check.total_cents)} after (${difference})`;
  const list = document.createElement("ul");
  for (const change of repair.changes) {
    const item = document.createElement("li");
    item.textContent = `${change.name}: ${change.before} → ${change.after}`;
    list.append(item);
  }
  const apply = document.createElement("button");
  apply.type = "button";
  apply.className = "button button-gold";
  apply.textContent = "Apply and recheck kit";
  apply.addEventListener("click", () => action(async () => {
    setConfig(repair.proposal);
    await checkCurrentKit();
  }));
  root.append(heading, price, list, apply);
  if (repair.alternatives?.length) root.append(comparisonPanel(repair.alternatives));
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
  const items = document.createElement("ul");
  items.className = "frozen-items";
  for (const line of purchase.snapshot.lines) {
    const item = document.createElement("li");
    const product = state.catalogue.find(product => product.id === line.product_id);
    item.textContent = `${line.quantity} × ${line.name ?? product?.name ?? line.product_id} · ${money(line.unit_cents)} each`;
    items.append(item);
  }
  root.append(items);
  if (purchase.provider_capture_id) {
    const receipt = document.createElement("p");
    receipt.textContent = `${state.mode === "mock" ? "Simulated capture" : "PayPal capture"}: ${purchase.provider_capture_id}`;
    root.append(receipt);
  }
  const digest = document.createElement("div"); digest.className = "digest";
  const version = purchase.snapshot.proof_version;
  digest.textContent = `Merchant: ${purchase.snapshot.merchant_id} · ${version ? "Rules: " + version + " · " : ""}Frozen terms SHA-256: ${purchase.digest}`;
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
  $("repair").disabled = !state.check || state.check.ready;
  $("review-terms").hidden = !state.check?.ready;
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
  if (state.busy) return;
  state.busy = true;
  try { await work(); updateActions(); await refreshAudit(); }
  catch (error) { toast(error.message, true); }
  finally { state.busy = false; }
}

$("token").value = sessionStorage.getItem("assembly-token") || "";
$("token").addEventListener("change", () => sessionStorage.setItem("assembly-token", token()));
for (const id of ["people", "budget"]) $(id).addEventListener("input", invalidateCheck);
$("restart").addEventListener("click", () => {
  if (state.busy) return;
  state.purchase = null;
  sessionStorage.removeItem("assembly-purchase");
  history.replaceState(null, "", "/");
  $("audit").replaceChildren();
  invalidateCheck();
});
$("interpret").addEventListener("click", () => action(async () => {
  const revision = state.revision;
  const data = await api("/api/plan", "POST", { text: $("prompt").value });
  if (revision !== state.revision) return;
  setConfig(data.proposal);
  state.check = data.check;
  renderCheck(data.check);
  $("proof").scrollIntoView();
  $("ai-state").textContent = data.needs_confirmation
    ? "The agent filled missing requirements. Review the fields and kit before payment."
    : "The agent proposed this kit. The separate checker evaluated it; review every item.";
  toast(data.check.ready ? "Agent proposal passed the configuration check." : "Agent proposal needs repair before checkout.");
}));
$("check").addEventListener("click", () => action(checkCurrentKit));
$("repair").addEventListener("click", () => action(async () => {
  const revision = state.revision;
  const result = await api("/api/repair", "POST", currentConfig());
  if (revision !== state.revision) return;
  state.check = result.original;
  renderCheck(result.original);
  renderRepair(result);
}));
$("prepare").addEventListener("click", () => action(async () => {
  state.purchase = await api("/api/purchases", "POST", {
    configuration: currentConfig(), expected_digest: state.check.digest, intent_key: crypto.randomUUID()
  });
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
    if (!health.ai_configured) $("ai-state").textContent = "Configure OpenAI to use AI planning. Manual examples remain available.";
    renderCatalogue(); setConfig(examples.broken);
    $("broken").disabled = false;
    $("broken").addEventListener("click", () => action(async () => {
      setConfig(examples.broken);
      await checkCurrentKit();
    }));
    const previous = new URLSearchParams(location.search).get("purchase") || sessionStorage.getItem("assembly-purchase");
    if (previous && token()) {
      state.purchase = await api(`/api/purchases/${previous}`);
      updateActions(); await refreshAudit();
      if (location.search.includes("paypal_return")) toast("PayPal returned. Capture only after server verifies buyer approval.");
    }
  } catch (error) { toast(error.message, true); }
})();
