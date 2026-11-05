"""Small synthetic falsification experiment, not a PayPal or AI integration.

The bug, model, scenario and correction are authored fixtures. This verifies only
that a tiny legal-trace reducer can retain an independently detected violation.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class IllegalTrace(ValueError):
    pass


def execute(events: list[str], corrected: bool) -> dict[str, Any]:
    state = {"selected": False, "approved": False, "created": False,
             "provider_captured": False, "event_received": False}
    history: list[dict[str, Any]] = []
    fulfilled: set[str] = set()
    for sequence, event in enumerate(events):
        required = {"approve": "selected", "create": "approved",
                    "capture": "created", "receive": "provider_captured",
                    "duplicate": "event_received"}.get(event)
        if required and not state[required]:
            raise IllegalTrace(f"{event} requires {required}")
        if event == "select":
            state["selected"] = True
        elif event == "approve":
            state["approved"] = True
        elif event == "create":
            state["created"] = True
        elif event == "capture":
            state["provider_captured"] = True
        elif event in {"receive", "duplicate"}:
            state["event_received"] = True
            key = "synthetic-purchase-1"
            if not corrected or key not in fulfilled:
                fulfilled.add(key)
                history.append({"sequence": sequence, "purchase": key,
                                "action": "fulfill", "captured": state["provider_captured"]})
        elif event != "inspect":
            raise IllegalTrace(f"Unknown event {event}")
    return {"state": state, "history": history}


def oracle(result: dict[str, Any]) -> list[str]:
    """Independent trace checks; does not read corrected flag or implementation set."""
    counts: dict[str, int] = {}
    violations: list[str] = []
    for event in result["history"]:
        key = event["purchase"]
        counts[key] = counts.get(key, 0) + 1
        if not event["captured"]:
            violations.append("FULFILLMENT_WITHOUT_CAPTURE")
    if any(count > 1 for count in counts.values()):
        violations.append("DUPLICATE_FULFILLMENT")
    return violations


def fails(events: list[str]) -> bool:
    try:
        return "DUPLICATE_FULFILLMENT" in oracle(execute(events, corrected=False))
    except IllegalTrace:
        return False


def reduce_trace(events: list[str]) -> tuple[list[str], int]:
    """Greedy single-event deletion to a fixed point; no global minimality claim."""
    candidate = list(events)
    attempts = 0
    changed = True
    while changed:
        changed = False
        for i in range(len(candidate)):
            trial = candidate[:i] + candidate[i + 1:]
            attempts += 1
            if fails(trial):
                candidate = trial
                changed = True
                break
    return candidate, attempts


def main() -> None:
    initial = ["inspect", "select", "inspect", "approve", "inspect", "create",
               "inspect", "capture", "inspect", "receive", "inspect", "duplicate",
               "inspect", "inspect"]
    reduced, attempts = reduce_trace(initial)
    buggy = execute(reduced, corrected=False)
    corrected = execute(reduced, corrected=True)
    assert fails(initial) and fails(reduced)
    assert oracle(corrected) == []
    assert len(reduced) == 6
    assert all(not fails(reduced[:i] + reduced[i + 1:]) for i in range(len(reduced)))
    assert [execute(reduced, False) for _ in range(10)] == [buggy] * 10
    report = {
        "scope": "Authored synthetic in-memory model; no PayPal, AI, sponsors, network or concurrent processes",
        "original_event_count": len(initial), "reduced_event_count": len(reduced),
        "reduction_attempts": attempts, "reduced_trace": reduced,
        "buggy_fulfillments": len(buggy["history"]),
        "corrected_fulfillments": len(corrected["history"]),
        "buggy_violations": oracle(buggy), "corrected_violations": oracle(corrected),
        "identical_local_replays": 10,
        "limitation": "The fixed in-memory set is not durable or concurrency safe; a real implementation needs a database uniqueness rule and an idempotent fulfillment integration. No discovery, generalization or production claim."
    }
    target = Path(__file__).with_name("counterexample_kernel_results.json")
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
