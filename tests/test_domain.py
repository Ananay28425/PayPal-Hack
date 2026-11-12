from app.domain import BROKEN_EXAMPLE, REPAIRED_EXAMPLE, Configuration, Requirements, Selection, evaluate
from app.counterexamples import run_configuration_cases


def test_detects_hidden_input_and_headphone_conflicts():
    result = evaluate(BROKEN_EXAMPLE)
    states = {item["code"]: item["status"] for item in result["checks"]}
    assert not result["ready"]
    assert states["input_capacity"] == "fail"
    assert states["listening_capacity"] == "fail"


def test_repaired_kit_is_compatible_and_within_budget():
    result = evaluate(REPAIRED_EXAMPLE)
    assert result["ready"]
    assert result["total_cents"] == 81_000
    assert all(item["status"] == "pass" for item in result["checks"])


def test_unknown_critical_fact_blocks_readiness():
    config = REPAIRED_EXAMPLE.model_copy(deep=True)
    config.selections = [Selection(product_id="interface-unknown", quantity=1)
                         if x.product_id == "interface-8" else x for x in config.selections]
    result = evaluate(config)
    assert not result["ready"]
    assert next(x for x in result["checks"] if x["code"] == "input_capacity")["status"] == "unknown"


def test_budget_and_connector_are_independent_rules():
    config = Configuration(requirements=Requirements(people=4, budget_cents=50_000),
        selections=[Selection(product_id="mic-usb", quantity=4), Selection(product_id="interface-8", quantity=1),
                    Selection(product_id="headphones", quantity=4), Selection(product_id="amp-4", quantity=1)])
    statuses = {x["code"]: x["status"] for x in evaluate(config)["checks"]}
    assert statuses["connector"] == "fail"
    assert statuses["budget"] == "fail"


def test_order_does_not_change_digest():
    config = REPAIRED_EXAMPLE.model_copy(deep=True)
    config.selections.reverse()
    assert evaluate(config)["digest"] == evaluate(REPAIRED_EXAMPLE)["digest"]


def test_independent_counterexample_expectations():
    cases = run_configuration_cases()
    assert len(cases) == 4
    assert all(case["passed"] for case in cases)


def test_custom_kit_unknown_capacity_and_quantity_repair():
    from app.domain import Configuration, evaluate, repair

    config = Configuration.model_validate({
        "requirements": {"people": 1, "budget_cents": 20000},
        "selections": [],
        "custom": {"requirement": "Workshop seats", "required_units": 12,
                   "items": [{"product_id": "custom-bench", "name": "Bench",
                              "quantity": 1, "unit_cents": 4000, "capacity": None}]},
    })
    assert evaluate(config)["checks"][0]["status"] == "unknown"
    assert repair(config)["reason"] == "missing_capacity"
    config.custom.items[0].capacity = 4
    original = evaluate(config)
    assert not original["ready"]
    result = repair(config)
    assert result["check"]["ready"]
    assert result["check"]["total_cents"] == 12000
    assert result["check"]["digest"] != original["digest"]
    assert result["check"]["snapshot"]["lines"][0]["quantity"] == 3
    config.requirements.budget_cents = 10000
    assert repair(config)["proposal"] is None
