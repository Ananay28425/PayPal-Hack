"use strict";

const state = {
  catalogue: [],
  configuration: null,
  check: null,
  purchase: null,
  mode: null,
  revision: 0,
  busy: false,
  repairGrid: null
  inspection: "recording", catalogue: [], check: null, purchase: null, mode: null, revision: 0, busy: false, repairGrid: null
};
let counterexampleGridApi = null;
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

function selectInspection(mode) {
  state.inspection = mode;
  const custom = mode === "custom";
  document.querySelector(`input[name="inspection"][value="${mode}"]`).checked = true;
  $("recording-goal").hidden = custom;
  $("recording-inspection").hidden = custom;
  $("custom-inspection").hidden = !custom;
  invalidateCheck();
}

function addCustomItem(item = {}) {
  const root = $("custom-items");
  if (root.children.length >= 20) return;
  const row = document.createElement("fieldset");
  row.className = "custom-item";
  row.dataset.productId = item.product_id ?? `custom-${crypto.randomUUID()}`;
  const fields = [
    ["name", "Item name", "text", item.name ?? "", {maxLength: 100}],
    ["quantity", "Quantity", "number", item.quantity ?? 1, {min: 1, max: 16, step: 1}],
    ["price", "Unit price (USD)", "number", item.unit_cents == null ? "" : item.unit_cents / 100, {min: 0.01, max: 20000, step: 0.01}],
    ["capacity", "Units provided per item", "number", item.capacity ?? "", {min: 0, max: 1000, step: 1}],
  ];
  for (const [key, title, type, value, limits] of fields) {
    const label = document.createElement("label");
    label.textContent = title;
    const input = document.createElement("input");
    Object.assign(input, {type, value, ...limits});
    input.dataset.field = key;
    input.addEventListener("input", invalidateCheck);
    label.append(input);
    row.append(label);
  }
  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "preset-button";
  remove.textContent = "Remove item";
  remove.addEventListener("click", () => { row.remove(); invalidateCheck(); });
  row.append(remove);
  root.append(row);
}

for (const option of document.querySelectorAll('input[name="inspection"]')) {
  option.addEventListener("change", () => selectInspection(option.value));
}
$("add-custom-item").addEventListener("click", () => { addCustomItem(); invalidateCheck(); });
for (const id of ["custom-requirement", "custom-required-units"]) {
  $(id).addEventListener("input", invalidateCheck);
}

function currentConfig() {
  const budget = $("budget");
  if (!budget.value || !budget.checkValidity()) throw new Error("Enter a valid USD budget.");
  const budgetCents = Math.round(Number(budget.value) * 100);
  if (state.inspection === "custom") {
    const requirement = $("custom-requirement").value.trim();
    const units = $("custom-required-units");
    if (!requirement || !units.value || !units.checkValidity()) {
      throw new Error("Enter a requirement name and a valid number of required units.");
    }
    const items = Array.from($("custom-items").children, row => {
      const field = key => row.querySelector(`[data-field="${key}"]`);
      const name = field("name").value.trim();
      const quantity = field("quantity"), price = field("price"), capacity = field("capacity");
      if (!name || !quantity.value || !price.value || !quantity.checkValidity() ||
          !price.checkValidity() || !capacity.checkValidity()) {
        throw new Error("Enter a name, valid quantity, and positive USD price for every item.");
      }
      return {product_id: row.dataset.productId, name, quantity: Number(quantity.value),
        unit_cents: Math.round(Number(price.value) * 100),
        capacity: capacity.value === "" ? null : Number(capacity.value)};
    });
    if (!items.length) throw new Error("Add at least one item.");
    return {requirements: {people: 1, budget_cents: budgetCents, currency: "USD"},
      selections: [], custom: {requirement, required_units: Number(units.value), items}};
  }
  const selections = state.catalogue.map(product => ({
    product_id: product.id,
    quantity: Number($("qty-" + product.id).value)
  })).filter(item => item.quantity > 0);
  return {
    requirements: { people: Number($("people").value), budget_cents: budgetCents, currency: "USD" },
    selections
  };
}

function setConfig(config) {
  if (config.custom) {
    $("budget").value = config.requirements.budget_cents / 100;
    $("custom-requirement").value = config.custom.requirement;
    $("custom-required-units").value = config.custom.required_units;
    $("custom-items").replaceChildren();
    config.custom.items.forEach(addCustomItem);
    selectInspection("custom");
    return;
  }
  selectInspection("recording");
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


function channel3Money(value, currency) {
  if (value === null || value === undefined || value === "") {
    return "Price not listed";
  }

  const amount = Number(value);
  if (!Number.isFinite(amount)) {
    return `${String(value)}${currency ? " " + currency : ""}`;
  }

  try {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency: currency || "USD"
    }).format(amount);
  } catch {
    return `${amount.toFixed(2)} ${currency || ""}`.trim();
  }
}

function renderChannel3Products(products) {
  const root = $("channel3-results");
  root.replaceChildren();

  if (!Array.isArray(products) || products.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent =
      "No matching products were returned. Try a broader search.";
    root.append(empty);
    return;
  }

  for (const product of products) {
    const card = document.createElement("article");
    card.className = "channel3-card";

    const imageUrl =
      product.image_url ||
      product.image ||
      product.images?.[0]?.url ||
      product.images?.[0]?.cleaned_url;

    if (typeof imageUrl === "string" && /^https:\/\//i.test(imageUrl)) {
      const image = document.createElement("img");
      image.src = imageUrl;
      image.alt = product.title
        ? `${product.title} product image`
        : "Product image";
      image.loading = "lazy";
      image.referrerPolicy = "no-referrer";
      image.addEventListener("error", () => image.remove(), { once: true });
      card.append(image);
    }

    const content = document.createElement("div");
    content.className = "channel3-card-content";

    const title = document.createElement("h4");
    title.textContent = product.title || "Untitled product";
    content.append(title);

    if (product.description) {
      const description = document.createElement("p");
      description.textContent = product.description;
      content.append(description);
    }

    const price = document.createElement("p");
    price.className = "channel3-price";
    price.textContent = product.price !== undefined
      ? channel3Money(product.price, product.currency)
      : "Price varies by offer";
    content.append(price);

    const offers = Array.isArray(product.offers) ? product.offers : [];

    if (offers.length) {
      const offerList = document.createElement("div");
      offerList.className = "channel3-offers";

      for (const offer of offers.slice(0, 3)) {
        if (
          !offer ||
          typeof offer.url !== "string" ||
          !/^https:\/\//i.test(offer.url)
        ) continue;

        const offerRow = document.createElement("div");
        offerRow.className = "channel3-offer";

        const merchant = document.createElement("span");
        merchant.textContent = offer.domain || "Merchant offer";

        const offerPrice = document.createElement("span");
        offerPrice.textContent = offer.price !== undefined
          ? channel3Money(offer.price, offer.currency || product.currency)
          : (offer.availability || "View offer");

        const link = document.createElement("a");
        link.href = offer.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = "VIEW OFFER ↗";

        offerRow.append(merchant, offerPrice, link);
        offerList.append(offerRow);
      }

      if (offerList.childElementCount) {
        content.append(offerList);
      }
    }

    card.append(content);
    root.append(card);
  }
}

async function searchChannel3(query) {
  const status = $("channel3-status");
  const button = $("channel3-search");
  const cleaned = query.trim();

  if (!cleaned || cleaned.length > 200) {
    status.textContent = "Enter a search between 1 and 200 characters.";
    return;
  }

  button.disabled = true;
  status.textContent = "Searching Channel3…";
  $("channel3-results").replaceChildren();

  try {
    const params = new URLSearchParams({
      q: cleaned,
      limit: "8"
    });

    const data = await api(
      `/api/products/search?${params.toString()}`
    );

    renderChannel3Products(data.products);

    status.textContent =
      `${data.products.length} result${data.products.length === 1 ? "" : "s"} from ${data.source || "Channel3"}. Discovery results are not checkout-authoritative.`;

  } catch (error) {
    status.textContent =
      `Channel3 search unavailable: ${error.message}`;
  } finally {
    button.disabled = false;
  }
}

$("channel3-search-form").addEventListener("submit", event => {
  event.preventDefault();
  searchChannel3($("channel3-query").value);
});


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
        { field: "layout", headerName: "Option", minWidth: 165, flex: 2, wrapText: true, autoHeight: true },
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
    heading.textContent = repair.reason === "missing_capacity"
      ? "Enter missing item capacities to find a repair"
      : "No compatible adjustment found within this budget";
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
  const report = await api("/api/counterexamples/all");
  const summaryRoot = $("counterexample-summary");
  const gridRoot = $("counterexample-grid");

  summaryRoot.replaceChildren();
  if (counterexampleGridApi) {
    counterexampleGridApi.destroy();
    counterexampleGridApi = null;
  }

  const cases = report.cases || [];
  const passed = cases.filter(item => item.passed).length;
  const total = cases.length;
  const failed = total - passed;

  const badge = document.createElement("span");
  badge.className = "pill " + (failed === 0 ? "pass" : "fail");
  badge.textContent = `${passed}/${total} EXPECTATIONS MET`;

  const description = document.createElement("span");
  description.textContent = `${total} scenarios · ${failed} failed · Configuration + Payment Integrity`;
  summaryRoot.append(badge, description);

  // AG Grid 32's UMD build may expose the community module registry.
  // Register once when available; otherwise the bundled legacy API can run directly.
  if (agGrid.ModuleRegistry && agGrid.AllCommunityModule && !window.__assemblyAgGridRegistered) {
    agGrid.ModuleRegistry.registerModules([agGrid.AllCommunityModule]);
    window.__assemblyAgGridRegistered = true;
  }

  const columnDefs = [
    { headerName: "SCENARIO", field: "scenario", minWidth: 210, flex: 1.5, filter: "agTextColumnFilter" },
    { headerName: "CATEGORY", field: "category", minWidth: 170, flex: 1, filter: "agTextColumnFilter" },
    { headerName: "EXPECTED", field: "expected", minWidth: 125, valueFormatter: params => JSON.stringify(params.value) },
    { headerName: "OBSERVED", field: "observed", minWidth: 125, valueFormatter: params => JSON.stringify(params.value) },
    {
      headerName: "STATUS", colId: "status", minWidth: 105, maxWidth: 115,
      valueGetter: params => params.data.passed ? "PASS" : "FAIL",
      cellClassRules: {
        "counterexample-status-pass": params => params.value === "PASS",
        "counterexample-status-fail": params => params.value === "FAIL"
      },
      filter: "agTextColumnFilter"
    },
    { headerName: "RATIONALE", field: "rationale", minWidth: 260, flex: 2, filter: "agTextColumnFilter", wrapText: true, autoHeight: true }
  ];

  counterexampleGridApi = agGrid.createGrid(gridRoot, {
    columnDefs,
    rowData: cases,
    defaultColDef: { sortable: true, resizable: true, filter: true, floatingFilter: true },
    pagination: true,
    paginationPageSize: 10,
    paginationPageSizeSelector: [10, 20, 50],
    animateRows: true
  });

  toast(`${passed}/${total} counterexample expectations met.`);
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
    addCustomItem();
    $("inspection-options").disabled = false;
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
