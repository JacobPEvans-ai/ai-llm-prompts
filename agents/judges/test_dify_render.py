"""Exercise the maintained renderer through the same Make targets as CI."""

import ast
import json
from pathlib import Path
import subprocess

import pytest
import yaml

from definitions import definitions


ROOT = Path(__file__).resolve().parents[2]


def run_make(*args):
    return subprocess.run(
        ["make", "--no-print-directory", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


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
    expected.add("tier2-rotation.dsl.yml")
    assert {path.name for path in tmp_path.glob("*.dsl.yml")} == expected
    assert {path.name for path in (ROOT / "agents" / "dify").glob("*.dsl.yml")} == expected
    for name in expected:
        generated = (tmp_path / name).read_text()
        committed = (ROOT / "agents" / "dify" / name).read_text()
        assert generated.startswith("# Generated from agents/")
        assert generated == committed, name
    assert not list((ROOT / "agents" / "dify-src").glob("*/*.dsl.yml.tmpl"))


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
        "sample.dsl.yml", "tier2-rotation.dsl.yml",
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
    assert len(edges) == 1 and edges[0]["target"] == "model"
    assert not any(data["type"] in ("start", "trigger-schedule") for data in nodes.values())


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
    assert graph["edges"][-1]["data"]["sourceType"] == "trigger-webhook"
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
