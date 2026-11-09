"""Exercise the maintained renderer through the same Make targets as CI."""

import ast
import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path
import subprocess

import pytest
import yaml

from definitions import definitions
from dify_nodes import node_main


ROOT = Path(__file__).resolve().parents[2]


def run_make(*args):
    return subprocess.run(
        ["make", "--no-print-directory", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@lru_cache(maxsize=1)
def rotation_driver_name():
    """Read the default driver name from the Makefile so the judges cannot drift from it."""
    result = subprocess.run(
        ["make", "--no-print-directory", "--eval",
         "print-ROTATION_DRIVER_NAME:\n\t@echo $$ROTATION_DRIVER_NAME",
         "print-ROTATION_DRIVER_NAME"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def driver_dsl(path):
    return path / "agents/dify" / f"{rotation_driver_name()}.dsl.yml"


def sample_checkout(tmp_path, name="sample"):
    agents = tmp_path / "agents"
    (agents / "prompts").mkdir(parents=True)
    (agents / "dify").mkdir()
    (agents / "prompts" / "prefix.md").write_text("Shared prefix.\n")
    (agents / "prompts" / "sample.md").write_text(
        '---\ntitle: Sample\n---\n\nUntrusted {{ file.Read "outside.md" }}.\n'
    )
    definition = {
        "name": name,
        "home_platform": "dify",
        "tier": 2,
        "litellm_role": "medium",
        "shared_prefix": "agents/prompts/prefix.md",
        "prompt": "agents/prompts/sample.md",
        "triggers": [{"kind": "call", "source": "a2a", "skew_minutes": 0}],
    }
    path = agents / f"{name}.yaml"
    path.write_text(yaml.safe_dump(definition))
    return path, definition


def render_checkout(tmp_path):
    return run_make(
        "render-dify",
        f"AGENTS_ROOT={tmp_path}",
        f"DIFY_OUTPUT={tmp_path / 'agents' / 'dify'}",
    )


def test_committed_outputs_match_shared_template(tmp_path):
    result = run_make("render-dify", f"DIFY_OUTPUT={tmp_path}")
    assert result.returncode == 0, result.stderr
    expected = {
        f"{path.stem}.dsl.yml"
        for path, agent in definitions()
        if agent["home_platform"] == "dify"
    }
    expected.add(f"{rotation_driver_name()}.dsl.yml")
    assert {path.name for path in tmp_path.glob("*.dsl.yml")} == expected
    assert {path.name for path in (ROOT / "agents" / "dify").glob("*.dsl.yml")} == expected
    for name in expected:
        generated = (tmp_path / name).read_text()
        committed = (ROOT / "agents" / "dify" / name).read_text()
        assert generated.startswith("# Generated from agents/")
        assert generated == committed, name
    assert not list((ROOT / "agents" / "dify-src").glob("*/*.dsl.yml.tmpl"))


def test_manifest_covers_rendered_files_with_matching_hashes():
    manifest = json.loads((ROOT / "agents/dify/manifest.json").read_text())
    agents = {agent["name"]: agent for _, agent in definitions() if agent["home_platform"] == "dify"}
    assert [entry["name"] for entry in manifest] == sorted([*agents, rotation_driver_name()])
    assert {entry["path"] for entry in manifest} == {
        path.relative_to(ROOT).as_posix() for path in (ROOT / "agents/dify").glob("*.dsl.yml")
    }
    for entry in manifest:
        assert set(entry) == {"name", "path", "sha256", "mode", "tier", "kind"}
        path = ROOT / entry["path"]
        assert path.is_file()
        assert path.name == f"{entry['name']}.dsl.yml"
        assert entry["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        if entry["name"] in agents:
            assert entry["kind"] == "agent"
            assert entry["mode"] == agents[entry["name"]]["mode"]
            assert entry["tier"] == agents[entry["name"]]["tier"]
        else:
            driver = subprocess.run(
                ["gomplate", "-t", f"driver={ROOT}/agents/dify-src/rotation.tmpl",
                 "-i", '{{ tmpl.Exec "driver-metadata" . }}'],
                capture_output=True, text=True, check=True,
                env={**os.environ, "ROTATION_DRIVER_NAME": rotation_driver_name()},
            )
            assert {key: entry[key] for key in ("name", "kind", "mode", "tier")} == json.loads(driver.stdout)


def test_render_takes_the_rotation_driver_name_as_input(tmp_path):
    result = run_make(
        "render-dify", "ROTATION_DRIVER_NAME=sample-rotation", f"DIFY_OUTPUT={tmp_path}",
    )
    assert result.returncode == 0, result.stderr
    expected = {
        f"{path.stem}.dsl.yml"
        for path, agent in definitions()
        if agent["home_platform"] == "dify"
    }
    expected.add("sample-rotation.dsl.yml")
    assert {path.name for path in tmp_path.glob("*.dsl.yml")} == expected
    assert not (tmp_path / "tier2-rotation.dsl.yml").exists()
    dsl = yaml.safe_load((tmp_path / "sample-rotation.dsl.yml").read_text())
    assert dsl["app"]["name"] == "sample-rotation"
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    entry = next(e for e in manifest if e["name"] == "sample-rotation")
    assert entry["path"] == "agents/dify/sample-rotation.dsl.yml"
    assert entry["kind"] == "driver" and entry["mode"] is None and entry["tier"] == 2


@pytest.mark.parametrize("name", ["ab", "No-Hyphens", "with_underscore", "with space", "x" * 64])
def test_invalid_rotation_driver_names_fail(tmp_path, name):
    result = run_make(
        "render-dify", f"ROTATION_DRIVER_NAME={name}", f"DIFY_OUTPUT={tmp_path}",
    )
    assert result.returncode != 0
    assert "ROTATION_DRIVER_NAME" in result.stderr


@pytest.mark.parametrize("name", ["github-clerk", "zammad-clerk"])
def test_new_dify_agent_needs_only_definition_and_prompt(tmp_path, name):
    sample_checkout(tmp_path, name)
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr
    output = tmp_path / "agents" / "dify" / f"{name}.dsl.yml"
    dsl = yaml.safe_load(output.read_text())
    assert dsl["app"]["name"] == name
    nodes = dsl["workflow"]["graph"]["nodes"]
    model = next(node["data"] for node in nodes if node["data"]["type"] == "llm")
    assert model["model"]["name"] == "medium"
    assert model["context"] == {"enabled": False, "variable_selector": []}
    assert model["prompt_template"][0]["text"] == (
        'Shared prefix.\n\nUntrusted {{ file.Read "outside.md" }}.'
    )
    assert model["prompt_template"][1]["text"] == "Untrusted input: {{#start.text#}}"


def test_non_dify_agent_is_skipped_without_fragments(tmp_path):
    sample_checkout(tmp_path)
    (tmp_path / "agents" / "elsewhere.yaml").write_text("name: elsewhere\nhome_platform: sim\n")
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr
    assert {p.name for p in (tmp_path / "agents" / "dify").iterdir()} == {
        "sample.dsl.yml", f"{rotation_driver_name()}.dsl.yml", "manifest.json",
    }


def test_missing_home_platform_fails(tmp_path):
    path, definition = sample_checkout(tmp_path)
    del definition["home_platform"]
    path.write_text(yaml.safe_dump(definition))
    assert render_checkout(tmp_path).returncode != 0


@pytest.mark.parametrize("prompt", ["../outside.md", "agents/../../outside.md"])
def test_prompt_paths_stay_inside_checkout(tmp_path, prompt):
    path, definition = sample_checkout(tmp_path)
    definition["prompt"] = prompt
    path.write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    assert result.returncode != 0
    assert "prompt paths must name repository files under agents/" in result.stderr


def test_name_must_match_definition_filename(tmp_path):
    path, definition = sample_checkout(tmp_path)
    definition["name"] = "another-agent"
    path.write_text(yaml.safe_dump(definition))
    assert render_checkout(tmp_path).returncode != 0


def test_anchor_renders_a_daily_utc_schedule(tmp_path):
    path, definition = sample_checkout(tmp_path)
    definition["triggers"] = [{"kind": "anchor", "at": "06:07"}]
    path.write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr
    output = yaml.safe_load((tmp_path / "agents" / "dify" / "sample.dsl.yml").read_text())
    start = output["workflow"]["graph"]["nodes"][0]["data"]
    assert start["type"] == "trigger-schedule"
    assert start["cron_expression"] == "07 06 * * *" and start["timezone"] == "UTC"



def test_weekly_anchor_renders_days(tmp_path):
    path, definition = sample_checkout(tmp_path)
    definition["triggers"] = [{"kind": "anchor", "at": "06:07", "days": ["Mon", "Fri"]}]
    path.write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr
    output = yaml.safe_load((tmp_path / "agents/dify/sample.dsl.yml").read_text())
    assert output["workflow"]["graph"]["nodes"][0]["data"]["cron_expression"] == "07 06 * * 1,5"


def test_tier1_rotation_uses_native_schedule(tmp_path):
    path, definition = sample_checkout(tmp_path)
    definition.update(tier=1, triggers=[{"kind": "rotation", "every": "15m"}])
    path.write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr
    output = yaml.safe_load((tmp_path / "agents/dify/sample.dsl.yml").read_text())
    start = output["workflow"]["graph"]["nodes"][0]["data"]
    assert start["type"] == "trigger-schedule"
    assert start["cron_expression"] == "7,22,37,52 * * * *"
    driver = yaml.safe_load(driver_dsl(tmp_path).read_text())
    assert '"name": "sample"' not in str(driver)


@pytest.mark.parametrize("tier", [0, 1])
@pytest.mark.parametrize("interval", range(1, 61))
def test_native_minute_rotations_exclude_quarter_hours(tmp_path, tier, interval):
    path, definition = sample_checkout(tmp_path)
    definition.update(tier=tier, triggers=[{"kind": "rotation", "every": f"{interval}m"}])
    path.write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    if interval < 2 or 60 % interval:
        assert result.returncode != 0
        assert "native rotation interval cannot be expressed safely as cron" in result.stderr
        assert not (tmp_path / "agents/dify/sample.dsl.yml").exists()
        return
    assert result.returncode == 0, result.stderr
    output = yaml.safe_load((tmp_path / "agents/dify/sample.dsl.yml").read_text())
    start = output["workflow"]["graph"]["nodes"][0]["data"]
    assert start["type"] == "trigger-schedule" and start["timezone"] == "UTC"
    minute_field, *remaining_fields = start["cron_expression"].split()
    assert remaining_fields == ["*", "*", "*", "*"]
    minutes = [int(minute) for minute in minute_field.split(",")]
    assert 7 in minutes
    assert all(0 <= minute < 60 for minute in minutes)
    assert not {0, 15, 30, 45}.intersection(minutes)
    starts = sorted(minutes)
    assert all(end - begin >= interval for begin, end in zip(starts, starts[1:] + [starts[0] + 60]))


@pytest.mark.parametrize("mode", ["live", None])
def test_generic_external_tools_require_shadow(tmp_path, mode):
    path, definition = sample_checkout(tmp_path)
    definition.update(tools=["github.create_pull_request"], mcp_servers=["github"])
    if mode is not None:
        definition["mode"] = mode
    path.write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    assert result.returncode != 0
    assert "generic workflows with tools must be shadow proposals" in result.stderr


def test_generic_shadow_connector_is_proposal_only(tmp_path):
    path, definition = sample_checkout(tmp_path)
    definition.update(mode="shadow", tools=["github.create_pull_request"], mcp_servers=["github"])
    path.write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr
    dsl = yaml.safe_load((tmp_path / "agents/dify/sample.dsl.yml").read_text())
    assert {node["data"]["type"] for node in dsl["workflow"]["graph"]["nodes"]} == {"start", "llm", "end"}


def test_generic_event_only_renders_webhook(tmp_path):
    path, definition = sample_checkout(tmp_path)
    definition["triggers"] = [{"kind": "event", "source": "github.check_run"}]
    path.write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr
    dsl = yaml.safe_load((tmp_path / "agents/dify/sample.dsl.yml").read_text())
    nodes = dsl["workflow"]["graph"]["nodes"]
    assert {node["data"]["type"] for node in nodes} == {
        "trigger-webhook", "llm", "end", "code", "if-else", "variable-aggregator",
    }
    assert nodes[0]["data"]["method"] == "post"

def test_event_and_rotation_share_a_native_webhook_entry(tmp_path):
    path, definition = sample_checkout(tmp_path)
    definition["triggers"] = [{"kind": "event", "source": "vikunja"}, {"kind": "rotation", "every": "1d"}]
    path.write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr
    output = yaml.safe_load((tmp_path / "agents" / "dify" / "sample.dsl.yml").read_text())
    graph = output["workflow"]["graph"]
    nodes = {node["id"]: node["data"] for node in graph["nodes"]}
    assert nodes["start"]["type"] == "trigger-webhook"
    assert nodes["start"]["method"] == "post"
    assert nodes["start"]["content_type"] == "application/json"
    edges = [edge for edge in graph["edges"] if edge["source"] == "start"]
    assert len(edges) == 1 and edges[0]["target"] == "start-input"
    assert not any(data["type"] in ("start", "trigger-schedule") for data in nodes.values())


@pytest.mark.parametrize("name", ["pr-keeper", "alert-triage", "release-promoter"])
def test_each_event_branch_stops_bad_input_before_the_model(name):
    dsl = yaml.safe_load((ROOT / "agents/dify" / f"{name}.dsl.yml").read_text())
    graph = dsl["workflow"]["graph"]
    nodes = {node["id"]: node["data"] for node in graph["nodes"]}
    aggregate = nodes["trigger-input"]
    model_input = next(message["text"] for message in nodes["model"]["prompt_template"] if message["role"] == "user")
    assert "{{#trigger-input.output#}}" in model_input
    assert aggregate["type"] == "variable-aggregator" and aggregate["output_type"] == "string"
    payload = {"payload": {"action": "opened", "number": 7}, "scope": {"repository": "example/repo"},
               "mandate": {"operation": "create_pull_request", "request_id": "req-1"}}
    saw_webhook = False
    for entry, data in nodes.items():
        if not data["type"].startswith("trigger-"):
            continue
        prepare = f"{entry}-input"
        gate = f"{prepare}-gate"
        refused = f"{prepare}-refused"
        assert [prepare, "text"] in aggregate["variables"]
        assert any(edge["source"] == entry and edge["target"] == prepare for edge in graph["edges"])
        assert nodes[prepare]["outputs"] == {"text": {"type": "string"}, "stop": {"type": "boolean"}}
        assert nodes[gate]["type"] == "if-else"
        stop_condition = nodes[gate]["cases"][0]["conditions"][0]
        assert stop_condition["variable_selector"] == [prepare, "stop"]
        assert stop_condition["varType"] == "boolean" and stop_condition["value"] is True
        assert nodes[refused]["type"] == "end"
        assert nodes[refused]["outputs"] == [{"variable": "text", "value_selector": [prepare, "text"]}]
        assert any(edge["source"] == prepare and edge["target"] == gate for edge in graph["edges"])
        assert any(edge["source"] == gate and edge["sourceHandle"] == "stop" and edge["target"] == refused
                   for edge in graph["edges"])
        assert any(edge["source"] == gate and edge["sourceHandle"] == "false" and edge["target"] == "trigger-input"
                   for edge in graph["edges"])
        assert not any(edge["source"] == gate and edge["target"] == "model" for edge in graph["edges"])
        assert not any(edge["source"] == refused for edge in graph["edges"])
        namespace = {}
        exec(compile(nodes[prepare]["code"], prepare, "exec"), namespace)
        assert "def refused_envelope" not in nodes[prepare]["code"]
        assert namespace["build_envelope"]("refused", "invalid triggering event", None) == {
            "status": "refused", "reason": "invalid triggering event", "result": None,
        }
        main = namespace["main"]
        if data["type"] == "trigger-schedule":
            output = main(timestamp=123)
            assert output["stop"] is False
            assert json.loads(output["text"])["result"] == {"timestamp": 123, "kind": "schedule"}
            continue
        saw_webhook = True
        assert {"variable": "event", "value_selector": [entry, "_webhook_raw"]} in nodes[prepare]["variables"]
        output = main(timestamp=123, event={"body": payload, "headers": {"Authorization": "excluded"}})
        assert output["stop"] is False
        text = output["text"]
        assert json.loads(text) == {"status": "ok", "reason": "", "result": {"timestamp": 123, "kind": "event", "event": payload}}
        assert "excluded" not in text
        secret = "AKIA" + "ABCDEFGH" + "IJKLMNOP"
        redacted = main(timestamp=123, event={"body": {"description": secret}})["text"]
        assert secret not in redacted and "[REDACTED]" in redacted
        for malformed in (None, [], {}, {"body": []}, {"body": "not an object"}):
            output = main(timestamp=123, event=malformed)
            assert output["stop"] is True
            assert json.loads(output["text"]) == {
                "status": "stop", "reason": "invalid triggering event", "result": None,
            }
        output = main(timestamp=123, event={"body": {"payload": "x" * 30001}})
        assert output["stop"] is True
        assert json.loads(output["text"]) == {
            "status": "stop", "reason": "trigger input exceeds 30000 characters", "result": None,
        }
    assert saw_webhook
    assert any(edge["source"] == "trigger-input" and edge["target"] == "model" for edge in graph["edges"])


@pytest.mark.parametrize("name", ["pr-keeper", "alert-triage", "release-promoter", "repo-janitor"])
def test_webhook_input_redacts_nested_secret_values_before_serialization(name):
    dsl = yaml.safe_load((ROOT / "agents/dify" / f"{name}.dsl.yml").read_text())
    payload = {
        "payload": {
            "action": "opened",
            "headers": {"aUtHoRiZaTiOn": "fixture-only", "COOKIE": ["fixture-only"]},
            "items": [{"api_key": "short", "nested": {
                "ToKeN": 123, "Password": False, "SECRET": {"value": "fixture-only"},
            }}],
        },
        "scope": {"repository": "example/repo"},
        "mandate": {"operation": "create_pull_request", "request_id": "req-1"},
        "count": 7, "enabled": True, "optional": None,
    }
    expected = {
        **payload,
        "payload": {
            "action": "opened",
            "headers": {"aUtHoRiZaTiOn": "[REDACTED]", "COOKIE": "[REDACTED]"},
            "items": [{"api_key": "[REDACTED]", "nested": {
                "ToKeN": "[REDACTED]", "Password": "[REDACTED]", "SECRET": "[REDACTED]",
            }}],
        },
    }
    for node in dsl["workflow"]["graph"]["nodes"]:
        if node["data"]["type"] != "trigger-webhook":
            continue
        main = node_main(name, f"{node['id']}-input")
        text = main(timestamp=123, event={"body": payload})["text"]
        assert json.loads(text)["result"]["event"] == expected
        assert "fixture-only" not in text and len(text) <= 30000
    assert payload["payload"]["items"][0]["api_key"] == "short"


@pytest.mark.parametrize("key,masked", [
    (key, True) for key in (
        "api_key", "apiKey", "x-api-key", "X-API-Key", "token", "access_token",
        "refresh_token", "authToken", "my_token", "password", "auth_password",
        "secret", "client_secret", "secret_id", "authorization", "Proxy-Authorization",
        "cookie", "Set-Cookie",
        "accesstoken", "clientsecret", "xapikey", "passwordhash", "sessioncookie", "authtoken",
    )
] + [
    (key, False) for key in (
        "max_tokens", "prompt_tokens", "completion_tokens", "total_tokens", "input_tokens",
        "output_tokens", "cache_read_input_tokens", "tokenizer", "tokens_used", "tokencount",
    )
])
@pytest.mark.parametrize("name", ["pr-keeper", "alert-triage", "release-promoter", "repo-janitor"])
def test_webhook_secret_key_segments_preserve_usage_counters(name, key, masked):
    dsl = yaml.safe_load((ROOT / "agents/dify" / f"{name}.dsl.yml").read_text())
    payload = {"items": [{"nested": {key: 42}}]}
    for node in dsl["workflow"]["graph"]["nodes"]:
        if node["data"]["type"] != "trigger-webhook":
            continue
        main = node_main(name, f"{node['id']}-input")
        result = json.loads(main(timestamp=123, event={"body": payload})["text"])
        actual = result["result"]["event"]["items"][0]["nested"][key]
        assert actual == ("[REDACTED]" if masked else 42)
    assert payload["items"][0]["nested"][key] == 42


@pytest.mark.parametrize("triggers", [
    [{"kind": "anchor", "at": "06:07"}, {"kind": "anchor", "at": "18:17"}],
    [{"kind": "anchor", "at": "06:15"}], [{"kind": "anchor", "at": "06:08"}],
    [{"kind": "rotation", "every": "0d"}], [{"kind": "schedule", "cadence": "7 * * * *"}],
])
def test_invalid_rendered_triggers_fail(tmp_path, triggers):
    path, definition = sample_checkout(tmp_path)
    definition["triggers"] = triggers
    path.write_text(yaml.safe_dump(definition))
    assert render_checkout(tmp_path).returncode != 0


@pytest.mark.parametrize("marker", ["__DIFY_SYSTEM_PROMPT__", "__DIFY_SYSTEM_PROMPT__\n"])
def test_custom_graph_preserves_prompt_newline_and_expands_helpers(tmp_path, marker):
    path, definition = sample_checkout(tmp_path)
    definition["dify"] = {
        "prompt": marker,
        "code": "__DIFY_HELPER_JSON_FENCE__",
        "comparison_operator": "=",
        "schema": "__DIFY_OUTPUT_SCHEMA__",
    }
    definition["output_schema"] = {
        "description": "Apostrophe's and \\ paths",
        "type": "object",
    }
    path.write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr
    output = yaml.safe_load((tmp_path / "agents" / "dify" / "sample.dsl.yml").read_text())
    assert output["prompt"] == (
        'Shared prefix.\n\nUntrusted {{ file.Read "outside.md" }}.'
        + ("\n" if marker.endswith("\n") else "")
    )
    helper = (ROOT / "agents" / "dify-src" / "helpers" / "json_fence.py").read_text()
    assert output["code"] == helper.rstrip("\n")
    assert output["comparison_operator"] == "="
    assert json.loads(ast.literal_eval(output["schema"])) == definition["output_schema"]


@pytest.mark.parametrize(
    "graph",
    [
        {"prompt": "absent"},
        {"prompt": "__DIFY_SYSTEM_PROMPT__", "another": "__DIFY_SYSTEM_PROMPT__\n"},
        {"prompt": "__DIFY_SYSTEM_PROMPT__", "value": "__DIFY_UNKNOWN__"},
    ],
)
def test_missing_duplicate_or_unknown_markers_fail(tmp_path, graph):
    path, definition = sample_checkout(tmp_path)
    definition["dify"] = graph
    path.write_text(yaml.safe_dump(definition))
    assert render_checkout(tmp_path).returncode != 0


@pytest.mark.parametrize("drift", ["prompt", "render", "missing", "extra", "header"])
def test_check_rejects_source_drift_and_hand_edits(tmp_path, drift):
    sample_checkout(tmp_path)
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr
    args = ("check-dify", f"AGENTS_ROOT={tmp_path}")
    assert run_make(*args).returncode == 0
    output = tmp_path / "agents" / "dify" / "sample.dsl.yml"
    if drift == "prompt":
        (tmp_path / "agents" / "prompts" / "sample.md").write_text("Changed prompt.\n")
    elif drift == "render":
        output.write_text(output.read_text().replace("medium", "changed"))
    elif drift == "header":
        output.write_text(output.read_text().replace("# Generated from", "# Hand edited"))
    elif drift == "missing":
        output.unlink()
    else:
        (output.parent / "orphan.dsl.yml").write_text(output.read_text())
    assert run_make(*args).returncode != 0


def test_rotation_can_also_have_a_fixed_anchor(tmp_path):
    path, definition = sample_checkout(tmp_path)
    definition["triggers"] = [{"kind": "rotation", "every": "1d"}, {"kind": "anchor", "at": "06:07"}]
    path.write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr
    dsl = yaml.safe_load((tmp_path / "agents" / "dify" / "sample.dsl.yml").read_text())
    graph = dsl["workflow"]["graph"]
    nodes = {node["id"]: node["data"] for node in graph["nodes"]}
    assert nodes["start"]["type"] == "trigger-schedule"
    assert nodes["webhook-0"]["type"] == "trigger-webhook"
    assert any(edge["source"] == "webhook-0" and edge["data"]["sourceType"] == "trigger-webhook" for edge in graph["edges"])
    assert "{{#start.text#}}" not in str(dsl)


def test_start_and_trigger_nodes_cannot_coexist(tmp_path):
    path, definition = sample_checkout(tmp_path)
    definition["dify"] = {
        "prompt": "__DIFY_SYSTEM_PROMPT__",
        "workflow": {"graph": {"nodes": [
            {"id": "start", "data": {"type": "start"}},
            {"id": "webhook", "data": {"type": "trigger-webhook"}},
        ]}},
    }
    path.write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    assert result.returncode != 0
    assert "Start node and trigger nodes cannot coexist" in result.stderr


def tool_node(server, name, parameters=None):
    return {"data": {
        "type": "tool",
        "provider_type": "mcp",
        "provider_name": server,
        "tool_name": name,
        "tool_parameters": parameters or {},
    }}


def individual_tool_checkout(tmp_path, tools, nodes):
    path, definition = sample_checkout(tmp_path)
    definition.update(mcp_servers=["filesystem", "git"], tools=tools)
    definition["dify"] = {
        "prompt": "__DIFY_SYSTEM_PROMPT__",
        "workflow": {"graph": {"nodes": nodes}},
    }
    path.write_text(yaml.safe_dump(definition))
    return path, definition


def test_individual_mcp_servers_render_one_node_per_tool(tmp_path):
    individual_tool_checkout(
        tmp_path,
        tools=["filesystem.read_text_file", "git.git_status", "a2a.call"],
        nodes=[tool_node("filesystem", "read_text_file"), tool_node("git", "git_status")],
    )
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr
    output = yaml.safe_load((tmp_path / "agents" / "dify" / "sample.dsl.yml").read_text())
    nodes = output["workflow"]["graph"]["nodes"]
    assert {(node["data"]["provider_name"], node["data"]["tool_name"]) for node in nodes} == {
        ("filesystem", "read_text_file"),
        ("git", "git_status"),
    }


def test_undeclared_individual_tool_node_fails(tmp_path):
    individual_tool_checkout(
        tmp_path,
        tools=["filesystem.read_text_file"],
        nodes=[tool_node("filesystem", "write_file")],
    )
    result = render_checkout(tmp_path)
    assert result.returncode != 0
    assert "must name an individually declared tool" in result.stderr


def test_subcommand_parameter_on_individual_tool_node_fails(tmp_path):
    individual_tool_checkout(
        tmp_path,
        tools=["filesystem.read_text_file"],
        nodes=[tool_node("filesystem", "read_text_file", {
            "subcommand": {"type": "constant", "value": "read_text_file"},
        })],
    )
    result = render_checkout(tmp_path)
    assert result.returncode != 0
    assert "cannot take a subcommand parameter" in result.stderr


def test_declared_individual_tool_without_a_node_fails(tmp_path):
    individual_tool_checkout(
        tmp_path,
        tools=["filesystem.read_text_file", "filesystem.write_file"],
        nodes=[tool_node("filesystem", "read_text_file")],
    )
    result = render_checkout(tmp_path)
    assert result.returncode != 0
    assert "must appear on a tool node" in result.stderr


def test_subcommand_tools_with_two_prefixes_fail(tmp_path):
    path, definition = sample_checkout(tmp_path)
    definition.update(mcp_servers=["vikunja"], tools=["vikunja_tasks.list", "zammad_rest.search"])
    definition["dify"] = {
        "prompt": "__DIFY_SYSTEM_PROMPT__",
        "workflow": {"graph": {"nodes": [tool_node("vikunja", "vikunja_tasks")]}},
    }
    path.write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    assert result.returncode != 0
    assert "must share one MCP tool prefix" in result.stderr
