"""Small, explicit product model and configuration checker.

The catalogue is an invented merchant fixture. None of these entries represents
a live retailer offer or a verified manufacturer's specification.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, Field


class Requirements(BaseModel):
    people: int = Field(ge=1, le=8)
    budget_cents: int = Field(ge=100, le=2_000_000)
    currency: Literal["USD"] = "USD"


class Selection(BaseModel):
    product_id: str = Field(min_length=1, max_length=80)
    quantity: int = Field(ge=1, le=16)


class Configuration(BaseModel):
    requirements: Requirements
    selections: list[Selection] = Field(min_length=1, max_length=20)


CATALOGUE: dict[str, dict] = {
    "mic-xlr": {"name": "Studio XLR microphone", "kind": "microphone", "price_cents": 6500, "connector": "XLR"},
    "mic-usb": {"name": "USB podcast microphone", "kind": "microphone", "price_cents": 4500, "connector": "USB"},
    "interface-2": {"name": "Two-input audio interface", "kind": "interface", "price_cents": 15000, "mic_inputs": 2, "headphone_outputs": 1, "line_output": True},
    "interface-8": {"name": "Eight-input audio interface", "kind": "interface", "price_cents": 26000, "mic_inputs": 8, "headphone_outputs": 2, "line_output": True},
    "interface-unknown": {"name": "Interface with unpublished input count", "kind": "interface", "price_cents": 18000, "mic_inputs": None, "headphone_outputs": 2, "line_output": True},
    "headphones": {"name": "Closed-back headphones", "kind": "headphones", "price_cents": 5000},
    "amp-4": {"name": "Four-output headphone amplifier", "kind": "amplifier", "price_cents": 9000, "headphone_outputs": 4},
}

PROOF_VERSION = "recording-kit-v1"
CATALOGUE_SOURCE = "invented_demo_fixture"


def catalogue() -> list[dict]:
    return [{"id": key, **value, "source": CATALOGUE_SOURCE, "merchant_id": "assembly-demo-merchant"}
            for key, value in CATALOGUE.items()]


def canonical_configuration(config: Configuration) -> dict:
    quantities: dict[str, int] = {}
    for item in config.selections:
        if item.product_id not in CATALOGUE:
            raise ValueError(f"Unknown product: {item.product_id}")
        if item.product_id in quantities:
            raise ValueError(f"Duplicate product: {item.product_id}")
        quantities[item.product_id] = item.quantity
    lines = []
    for key, quantity in sorted(quantities.items()):
        product = CATALOGUE[key]
        lines.append({
            "product_id": key,
            "quantity": quantity,
            "unit_cents": product["price_cents"],
            "name": product["name"],
            "facts": {field: value for field, value in product.items() if field not in {"name", "price_cents"}},
        })
    return {
        "merchant_id": "assembly-demo-merchant",
        "requirements": config.requirements.model_dump(),
        "proof_version": PROOF_VERSION,
        "catalogue_source": CATALOGUE_SOURCE,
        "lines": lines,
    }


def digest(value: dict) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def evaluate(config: Configuration) -> dict:
    snapshot = canonical_configuration(config)
    counts: dict[str, int] = {}
    items: dict[str, list[dict]] = {}
    total = 0
    for line in snapshot["lines"]:
        product = line["facts"]
        count = line["quantity"]
        counts[product["kind"]] = counts.get(product["kind"], 0) + count
        items.setdefault(product["kind"], []).append({"id": line["product_id"], "quantity": count, **product})
        total += count * line["unit_cents"]

    checks: list[dict] = []

    def check(code: str, status: str, detail: str, repair: str = "") -> None:
        checks.append({"code": code, "status": status, "detail": detail, "repair": repair})

    people = config.requirements.people
    check("microphones", "pass" if counts.get("microphone", 0) >= people else "fail",
          f"Need {people} microphones; selected {counts.get('microphone', 0)}.", "Add microphones.")
    check("headphones", "pass" if counts.get("headphones", 0) >= people else "fail",
          f"Need {people} headphones; selected {counts.get('headphones', 0)}.", "Add headphones.")
    interfaces = items.get("interface", [])
    check("one_interface", "pass" if len(interfaces) == 1 and interfaces[0]["quantity"] == 1 else "fail",
          f"Need exactly one interface; selected {counts.get('interface', 0)}.", "Choose one interface.")
    interface = interfaces[0] if len(interfaces) == 1 and interfaces[0]["quantity"] == 1 else None
    microphones = items.get("microphone", [])
    check("connector", "pass" if microphones and all(x.get("connector") == "XLR" for x in microphones) else "fail",
          "This demo's audio interfaces accept XLR microphones; USB microphones cannot use their XLR inputs.",
          "Select XLR microphones.")
    if interface is None:
        check("input_capacity", "unknown", "Choose exactly one interface to establish input capacity.")
        check("listening_capacity", "unknown", "Choose exactly one interface to establish headphone routing.")
    else:
        capacity = interface.get("mic_inputs")
        required_inputs = max(people, counts.get("microphone", 0))
        check("input_capacity", "unknown" if capacity is None else "pass" if capacity >= required_inputs else "fail",
              "Interface microphone input count is unknown." if capacity is None else
              f"Interface has {capacity} microphone inputs; need {required_inputs}.",
              "Choose an interface with enough inputs.")
        outputs = interface.get("headphone_outputs")
        amps = items.get("amplifier", [])
        if amps and not interface.get("line_output"):
            check("listening_capacity", "fail", "Selected interface lacks a line output for the amplifier.")
        elif outputs is None or any(a.get("headphone_outputs") is None for a in amps):
            check("listening_capacity", "unknown", "Headphone output capacity is unknown.")
        else:
            # An amplifier connected to a line output supplies separate outputs.
            available = max([outputs] + [a["headphone_outputs"] * a["quantity"] for a in amps])
            check("listening_capacity", "pass" if available >= people else "fail",
                  f"Can supply {available} separate headphone outputs; need {people}.",
                  "Add a headphone amplifier with enough outputs.")
    check("budget", "pass" if total <= config.requirements.budget_cents else "fail",
          f"Total ${total / 100:.2f}; budget ${config.requirements.budget_cents / 100:.2f}.",
          "Reduce cost or explicitly raise budget.")
    return {"ready": all(x["status"] == "pass" for x in checks), "total_cents": total,
            "currency": "USD", "checks": checks, "snapshot": snapshot, "digest": digest(snapshot),
            "catalogue_notice": "Invented demo merchant offers and specifications; no live stock or retailer claims."}


def repair(config: Configuration) -> dict:
    """Find the smallest passing change in the demo's supported wiring layouts."""
    original = evaluate(config)
    if original["ready"]:
        return {"original": original, "proposal": None, "reason": "already_compatible"}

    before = {line["product_id"]: line["quantity"] for line in original["snapshot"]["lines"]}
    people = config.requirements.people
    candidates = []
    alternatives = []
    # The fixture supports one XLR microphone and one headphone per listener,
    # one interface, and up to two four-output amplifiers.
    for interface_id, product in CATALOGUE.items():
        if product["kind"] != "interface":
            continue
        layouts = []
        for amps in range(3):
            quantities = {"mic-xlr": people, "headphones": people, interface_id: 1}
            if amps:
                quantities["amp-4"] = amps
            proposal = Configuration(
                requirements=config.requirements,
                selections=[Selection(product_id=key, quantity=qty) for key, qty in quantities.items()],
            )
            checked = evaluate(proposal)
            blockers = [check for check in checked["checks"] if check["status"] != "pass"]
            changes = [
                {"product_id": key, "name": CATALOGUE[key]["name"],
                 "before": before.get(key, 0), "after": quantities.get(key, 0)}
                for key in sorted(before.keys() | quantities.keys())
                if before.get(key, 0) != quantities.get(key, 0)
            ]
            rank = (
                len(blockers),
                sum(abs(change["after"] - change["before"]) for change in changes),
                checked["total_cents"],
                checked["digest"],
            )
            layouts.append((rank, proposal, checked, changes, blockers))
        best_layout = min(layouts, key=lambda layout: layout[0])
        _, layout, checked, _, blockers = best_layout
        alternatives.append({
            "name": product["name"],
            "amplifiers": next((line.quantity for line in layout.selections if line.product_id == "amp-4"), 0),
            "total_cents": checked["total_cents"],
            "ready": checked["ready"],
            "blockers": blockers,
        })
        if checked["ready"]:
            candidates.append(best_layout)
    if not candidates:
        return {"original": original, "proposal": None, "reason": "no_compatible_kit",
                "alternatives": alternatives}

    _, proposal, checked, changes, _ = min(candidates, key=lambda candidate: candidate[0])
    return {
        "original": original,
        "proposal": proposal.model_dump(),
        "check": checked,
        "changes": changes,
        "price_delta_cents": checked["total_cents"] - original["total_cents"],
        "reason": "repair_found",
        "alternatives": alternatives,
    }


BROKEN_EXAMPLE = Configuration(requirements=Requirements(people=4, budget_cents=100_000), selections=[
    Selection(product_id="mic-xlr", quantity=4), Selection(product_id="interface-2", quantity=1),
    Selection(product_id="headphones", quantity=4),
])
REPAIRED_EXAMPLE = Configuration(requirements=Requirements(people=4, budget_cents=100_000), selections=[
    Selection(product_id="mic-xlr", quantity=4), Selection(product_id="interface-8", quantity=1),
    Selection(product_id="headphones", quantity=4), Selection(product_id="amp-4", quantity=1),
])
