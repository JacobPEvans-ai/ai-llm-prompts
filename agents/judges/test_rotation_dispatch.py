"""Follow rendered dispatch paths offline, including native HTTP error defaults."""

import json

import pytest

from test_rotation_due import driver


def run_tick(dsl, nodes, result, responses):
    """Walk active edges; skipped code inputs are None, as in Dify's CodeNode."""
    values = {("due", key): value for key, value in result.items()}
    current, visited = "due", []
    edges = dsl["workflow"]["graph"]["edges"]
    while current != "done":
        node = nodes[current]
        handle = "source"
        if node["type"] == "if-else":
            condition = node["cases"][0]["conditions"][0]
            handle = str(condition["value"] in result["due"]).lower()
        elif node["type"] == "http-request":
            visited.append(current)
            status = responses[current]
            if isinstance(status, Exception) or not 200 <= status < 300:
                assert node["error_strategy"] == "default-value"
                status = next(item["value"] for item in node["default_value"] if item["key"] == "status_code")
            values[(current, "status_code")] = status
        elif current == "tick-log":
            namespace = {}
            exec(node["code"], namespace)
            inputs = {item["variable"]: values.get(tuple(item["value_selector"])) for item in node["variables"]}
            values.update({(current, key): value for key, value in namespace["main"](**inputs).items()})
        outgoing = [edge for edge in edges if edge["source"] == current and edge["sourceHandle"] == handle]
        assert len(outgoing) == 1
        current = outgoing[0]["target"]
    assert nodes["done"]["outputs"] == [{"variable": "log", "value_selector": ["tick-log", "log"]}]
    log = values[("tick-log", "log")]
    assert "\n" not in log
    return visited, json.loads(log)


def test_dispatch_uses_secret_environment_ids_and_native_branches(tmp_path):
    dsl, nodes, namespace = driver(tmp_path, [
        ("sample", "30m", None), ("beta", "30m", None), ("gamma", "30m", None),
    ])
    env = {item["name"]: item for item in dsl["workflow"]["environment_variables"]}
    assert env["SAMPLE_WEBHOOK_ID"]["value_type"] == "secret"
    assert env["SAMPLE_WEBHOOK_ID"]["value"] == ""
    assert env["SAMPLE_TRIGGER_URL"]["value"] == ""
    assert nodes["dispatch-sample"]["url"] == (
        "{{#env.SAMPLE_TRIGGER_URL#}}/triggers/webhook/{{#env.SAMPLE_WEBHOOK_ID#}}"
    )
    assert nodes["dispatch-sample"]["method"] == "post"
    assert nodes["dispatch-sample"]["body"]["type"] == "none"
    assert nodes["dispatch-sample"]["retry_config"]["retry_enabled"] is False
    assert nodes["due"]["variables"] == [
        {"variable": "timestamp", "value_selector": ["sys", "timestamp"]},
        {"variable": "speed", "value_selector": ["env", "ROTATION_SPEED"]},
        {"variable": "offset", "value_selector": ["env", "ROTATION_OFFSET"]},
        {"variable": "paused", "value_selector": ["env", "ROTATION_PAUSED"]},
    ]
    for name, node in nodes.items():
        if node["type"] == "http-request":
            assert node["error_strategy"] == "default-value", name
            assert node["default_value"] == [{"key": "status_code", "type": "number", "value": 0}]
    for timestamp, paused, expected in [
        (60, "false", ["dispatch-beta"]), (660, "false", ["dispatch-gamma"]),
        (1260, "false", ["dispatch-sample"]), (180, "false", []), (60, "true", []),
    ]:
        result = namespace["main"](timestamp, 1, 0, paused)
        visited, log = run_tick(dsl, nodes, result, {name: 202 for name in expected})
        assert visited == expected
        assert log == {**json.loads(result["log"]), "failures": []}


@pytest.mark.parametrize("statuses", [
    [TimeoutError("private request details"), 202, 202],
    [202, ConnectionError("private request details"), 202],
    [202, 202, TimeoutError("private request details")],
    [500, 403, 503],
])
def test_failed_dispatches_continue_and_always_emit_tick_log(tmp_path, statuses):
    dsl, nodes, namespace = driver(tmp_path, [
        ("alpha-agent", "2m", None), ("beta-agent", "2m", None), ("gamma-agent", "2m", None),
    ])
    result = namespace["main"](60, 1, 0, "false")
    responses = {f"dispatch-{name}": status for name, status in zip(result["due"], statuses, strict=True)}
    visited, log = run_tick(dsl, nodes, result, responses)
    assert visited == list(responses)
    assert log == {
        **json.loads(result["log"]),
        "failures": [name for name, status in zip(result["due"], statuses, strict=True)
                     if isinstance(status, Exception) or status >= 300],
    }
    assert "private request details" not in json.dumps(log)


def test_empty_roster_emits_tick_log(tmp_path):
    dsl, nodes, namespace = driver(tmp_path, [])
    result = namespace["main"](60, 1, 0, "false")
    visited, log = run_tick(dsl, nodes, result, {})
    assert visited == []
    assert log == {**json.loads(result["log"]), "failures": []}
