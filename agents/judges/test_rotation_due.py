"""Exercise stateless windows and the rendered native Dify dispatch graph offline."""

import importlib.util
import json
import math
from pathlib import Path

import pytest
import yaml

from test_dify_render import render_checkout, sample_checkout


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "rotation_due", ROOT / "agents/dify-src/helpers/rotation_due.py",
)
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)
AGENTS = [{"name": "sample", "every_minutes": 60, "offset_minutes": 10}]


@pytest.mark.parametrize("now,expected", [(10, ["sample"]), (11, ["sample"]), (12, []), (70, ["sample"])])
def test_two_minute_window(now, expected):
    assert HELPER.rotation_due(now, AGENTS)["due"] == expected


@pytest.mark.parametrize("speed,now", [(0.5, 40), (2.0, 130)])
def test_speed_and_offset(speed, now):
    assert HELPER.rotation_due(now, AGENTS, speed)["due"] == ["sample"]
    assert HELPER.rotation_due(now - 3, AGENTS, speed, 3)["due"] == ["sample"]
    assert HELPER.rotation_due(now - 3, AGENTS, speed)["due"] == []


@pytest.mark.parametrize("paused", [True, "true", "TRUE"])
def test_pause_and_log(paused):
    result = HELPER.rotation_due(10, AGENTS, ROTATION_PAUSED=paused)
    assert result["due"] == []
    assert result["skipped"] == ["sample"]
    assert json.loads(result["log"]) == {
        "due": [], "skipped": ["sample"],
        "ROTATION_SPEED": 1.0, "ROTATION_OFFSET": 0.0, "ROTATION_PAUSED": True,
    }
    assert "\n" not in result["log"]
    assert HELPER.rotation_due(10, AGENTS, ROTATION_PAUSED="false")["due"] == ["sample"]


@pytest.mark.parametrize("kwargs", [
    {"ROTATION_SPEED": 0}, {"ROTATION_SPEED": -1}, {"ROTATION_SPEED": "nan"},
    {"ROTATION_SPEED": 0.01}, {"ROTATION_OFFSET": "inf"}, {"ROTATION_PAUSED": "yes"},
])
def test_invalid_knobs_fail_closed(kwargs):
    with pytest.raises(ValueError):
        HELPER.rotation_due(10, AGENTS, **kwargs)


def driver(tmp_path, definitions):
    _, base = sample_checkout(tmp_path)
    for name, every, runtime in definitions:
        definition = {**base, "name": name, "tier": 2, "triggers": [{"kind": "rotation", "every": every}]}
        if runtime is not None:
            definition["expected_runtime_minutes"] = runtime
        (tmp_path / "agents" / f"{name}.yaml").write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr
    dsl = yaml.safe_load((tmp_path / "agents/dify/tier2-rotation.dsl.yml").read_text())
    nodes = {node["id"]: node["data"] for node in dsl["workflow"]["graph"]["nodes"]}
    namespace = {}
    exec(nodes["due"]["code"], namespace)
    return dsl, nodes, namespace


def assert_max_two(agents, speed=1.0):
    if not agents:
        return
    cycle = math.lcm(2, *(round(agent["every_minutes"] * speed) for agent in agents))
    longest = math.ceil(max(agent["expected_runtime_minutes"] for agent in agents))
    active = []
    by_name = {agent["name"]: agent for agent in agents}
    for minute in range(-longest - 2, cycle + longest):
        active = [end for end in active if end > minute]
        if minute % 2:
            for name in HELPER.rotation_due(minute, agents, speed)["due"]:
                active.append(minute + by_name[name]["expected_runtime_minutes"])
        assert len(active) <= 2, f"{len(active)} runs overlap at minute {minute}"


def test_rendered_offsets_runtime_overlap_and_timestamp(tmp_path):
    dsl, nodes, namespace = driver(tmp_path, [
        ("gamma", "7d", None), ("alpha", "1d", 12), ("beta", "12h", None),
    ])
    agents = namespace["ROTATION_AGENTS"]
    assert agents == [
        {"name": "alpha", "every_minutes": 1440, "offset_minutes": 0, "expected_runtime_minutes": 12},
        {"name": "beta", "every_minutes": 720, "offset_minutes": 240, "expected_runtime_minutes": 10},
        {"name": "gamma", "every_minutes": 10080, "offset_minutes": 6720, "expected_runtime_minutes": 10},
    ]
    for speed in (0.5, 1.0, 2.0):
        assert_max_two(agents, speed)
    assert namespace["main"](60, 1, 0, "false")["due"] == ["alpha"]
    assert nodes["schedule"]["cron_expression"] == "1-59/2 * * * *"
    assert nodes["schedule"]["timezone"] == "UTC"
    before = (tmp_path / "agents/dify/tier2-rotation.dsl.yml").read_bytes()
    assert render_checkout(tmp_path).returncode == 0
    assert (tmp_path / "agents/dify/tier2-rotation.dsl.yml").read_bytes() == before


def test_overlap_check_rejects_crowded_runtime():
    crowded = [{**AGENTS[0], "name": name, "expected_runtime_minutes": 10} for name in ("a", "b", "c")]
    with pytest.raises(AssertionError, match="3 runs overlap"):
        assert_max_two(crowded)


def test_committed_roster_runtime_overlap():
    dsl = yaml.safe_load((ROOT / "agents/dify/tier2-rotation.dsl.yml").read_text())
    due = next(node["data"] for node in dsl["workflow"]["graph"]["nodes"] if node["id"] == "due")
    namespace = {}
    exec(due["code"], namespace)
    assert_max_two(namespace["ROTATION_AGENTS"])


@pytest.mark.parametrize("every", ["0m", "1m", "1.5h", "daily"])
def test_renderer_rejects_invalid_intervals(tmp_path, every):
    path, definition = sample_checkout(tmp_path)
    definition.update(tier=2, triggers=[{"kind": "rotation", "every": every}])
    path.write_text(yaml.safe_dump(definition))
    assert render_checkout(tmp_path).returncode != 0


@pytest.mark.parametrize("tier,home", [(0, "dify"), (1, "dify"), (2, "sim")])
def test_only_tier_two_dify_agents_enter_driver(tmp_path, tier, home):
    path, definition = sample_checkout(tmp_path)
    definition.update(tier=tier, home_platform=home, triggers=[{"kind": "rotation", "every": "1d"}])
    path.write_text(yaml.safe_dump(definition))
    assert render_checkout(tmp_path).returncode == 0
    output = yaml.safe_load((tmp_path / "agents/dify/tier2-rotation.dsl.yml").read_text())
    code = next(node["data"]["code"] for node in output["workflow"]["graph"]["nodes"] if node["id"] == "due")
    namespace = {}
    exec(code, namespace)
    assert namespace["ROTATION_AGENTS"] == []


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
    # Follow the emitted graph for due, skipped, and paused ticks, without sending HTTP.
    edges = dsl["workflow"]["graph"]["edges"]
    for timestamp, paused, expected in [
        (60, "false", ["dispatch-beta"]), (660, "false", ["dispatch-gamma"]),
        (1260, "false", ["dispatch-sample"]), (180, "false", []), (60, "true", []),
    ]:
        result = namespace["main"](timestamp, 1, 0, paused)
        current, visited = "due", []
        while current != "done":
            node = nodes[current]
            handle = "source"
            if node["type"] == "if-else":
                condition = node["cases"][0]["conditions"][0]
                handle = str(condition["value"] in result["due"]).lower()
            if node["type"] == "http-request":
                visited.append(current)
            current = next(edge["target"] for edge in edges if edge["source"] == current and edge["sourceHandle"] == handle)
        assert visited == expected
        assert nodes["done"]["outputs"] == [{"variable": "log", "value_selector": ["due", "log"]}]
