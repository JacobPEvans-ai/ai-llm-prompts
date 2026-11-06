"""Offline shadow export, policy, and drift checks through the public Make targets."""

import ast
import json

import pytest
import yaml

from test_dify_render import ROOT, run_make, sample_checkout


RUNTIMES = ("sim", "langflow")


def render(runtime, root):
    return run_make(
        f"render-{runtime}", f"AGENTS_ROOT={root}",
        f"SHADOW_OUTPUT={root / 'agents' / runtime}",
    )


def sample(root):
    path, definition = sample_checkout(root)
    definition.update(
        shadows=list(RUNTIMES), mode="live", tier=2, privacy_class="private",
        tools=["litellm.chat_completions", "github.pulls.get", "github.pulls.create_review",
               "vikunja.tasks.update", "agent-sandbox.run", "unknown.operation"],
        connectors=["github-clerk"],
        output_schema={"type": "object", "properties": {"text": {"type": "string"}}},
    )
    path.write_text(yaml.safe_dump(definition))
    return path, definition


def document(runtime, root, name="sample"):
    return json.loads((root / "agents" / runtime / f"{name}.json").read_text())


def metadata(runtime, export):
    return export["state" if runtime == "sim" else "data"]["metadata"]


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_committed_exports_match_definitions_and_fresh_render(tmp_path, runtime):
    result = run_make(f"render-{runtime}", f"SHADOW_OUTPUT={tmp_path}")
    assert result.returncode == 0, result.stderr
    expected = {
        f"{path.stem}.json" for path in (ROOT / "agents").glob("*.yaml")
        if runtime in yaml.safe_load(path.read_text()).get("shadows", [])
        and yaml.safe_load(path.read_text())["home_platform"] == "dify"
    }
    committed = ROOT / "agents" / runtime
    assert {p.name for p in tmp_path.iterdir()} == expected
    assert {p.name for p in committed.iterdir()} == expected
    for name in expected:
        assert (tmp_path / name).read_bytes() == (committed / name).read_bytes()
        export = json.loads((tmp_path / name).read_text())
        definition = yaml.safe_load((ROOT / "agents" / name.replace(".json", ".yaml")).read_text())
        meta = metadata(runtime, export)
        assert meta["agent"] == definition["name"]
        assert meta["mode"] == "shadow"
        assert meta["litellm_role"] == definition["litellm_role"]
        assert meta["triggers"] == definition["triggers"]
        assert meta["output_schema"] == definition.get("output_schema")


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_replay_has_router_only_and_omits_writes_connectors_and_unknown_tools(tmp_path, runtime):
    _, definition = sample(tmp_path)
    result = render(runtime, tmp_path)
    assert result.returncode == 0, result.stderr
    export = document(runtime, tmp_path)
    meta = metadata(runtime, export)
    assert meta["mode"] == "shadow"
    assert meta["tier"] == 2
    assert meta["privacy_class"] == "private"
    assert meta["tools"] == ["litellm.chat_completions"]
    assert meta["omitted_tools"] == definition["tools"][1:]
    assert meta["results"] == ["langfuse-trace", "phoenix-trace"]
    assert "connectors" not in meta
    prompt = 'Shared prefix.\n\nUntrusted {{ file.Read "outside.md" }}.'
    if runtime == "sim":
        state = export["state"]
        assert export["version"] == "1.0"
        assert {b["type"] for b in state["blocks"].values()} == {"start_trigger", "api"}
        assert state["blocks"]["start"]["subBlocks"]["inputFormat"]["value"] == []
        call = state["blocks"]["router"]["subBlocks"]
        assert call["url"]["value"] == "{{LITELLM_API_BASE}}/chat/completions"
        assert call["method"]["value"] == "POST"
        assert call["headers"]["value"][0]["cells"]["Value"] == "Bearer {{SAMPLE_LITELLM_API_KEY}}"
        body = json.loads(call["body"]["value"])
        assert body["model"] == definition["litellm_role"]
        assert body["messages"] == [{"role": "system", "content": prompt},
                                    {"role": "user", "content": "<start.input>"}]
        assert "tools" not in body
        assert body["response_format"]["json_schema"]["schema"] == definition["output_schema"]
        assert len(state["edges"]) == 1
        assert state["edges"][0]["source"] == "start"
        assert state["edges"][0]["target"] == "router"
    else:
        assert export["last_tested_version"] == "1.13.0"
        nodes = export["data"]["nodes"]
        assert len(nodes) == 2
        assert nodes[0]["data"]["type"] == "TextInput"
        model = nodes[1]["data"]["node"]
        assert nodes[1]["data"]["type"] == "ext:openai:OpenAIModelComponent@official"
        fields = model["template"]
        assert fields["system_message"]["value"] == prompt
        assert fields["model_name"]["value"] == definition["litellm_role"]
        assert fields["openai_api_base"]["value"] == "LITELLM_API_BASE"
        assert fields["openai_api_base"]["load_from_db"] is True
        assert fields["api_key"]["value"] == "SAMPLE_LITELLM_API_KEY"
        assert fields["api_key"]["load_from_db"] is True
        assert fields["api_key"]["password"] is True
        kwargs = fields["model_kwargs"]["value"]
        assert "tools" not in kwargs
        assert kwargs["response_format"]["json_schema"]["schema"] == definition["output_schema"]
        edge = export["data"]["edges"][0]
        assert edge["source"] == nodes[0]["id"]
        assert edge["target"] == nodes[1]["id"]
        for endpoint in ("sourceHandle", "targetHandle"):
            assert json.loads(edge[endpoint].replace("œ", '"')) == edge["data"][endpoint]
        # Only pinned built-in component source is embedded; no generated execution code.
        vendor = (ROOT / "agents" / "langflow-src" / "openai.py").read_text()
        assert fields["code"]["value"] == vendor
        for node in nodes:
            ast.parse(node["data"]["node"]["template"]["code"]["value"])


@pytest.mark.parametrize("runtime", RUNTIMES)
@pytest.mark.parametrize("drift", ["prompt", "prefix", "definition", "render", "missing", "extra"])
def test_check_rejects_source_drift_and_hand_edits(tmp_path, runtime, drift):
    path, definition = sample(tmp_path)
    assert render(runtime, tmp_path).returncode == 0
    args = (f"check-{runtime}", f"AGENTS_ROOT={tmp_path}")
    assert run_make(*args).returncode == 0
    output = tmp_path / "agents" / runtime / "sample.json"
    if drift in {"prompt", "prefix"}:
        key = "shared_prefix" if drift == "prefix" else "prompt"
        (tmp_path / definition[key]).write_text("Changed prompt.\n")
    elif drift == "definition":
        definition["litellm_role"] = "small"
        path.write_text(yaml.safe_dump(definition))
    elif drift == "render":
        output.write_text(output.read_text().replace("medium", "changed"))
    elif drift == "missing":
        output.unlink()
    else:
        (output.parent / "orphan.json").write_text(output.read_text())
    assert run_make(*args).returncode != 0


@pytest.mark.parametrize("runtime", RUNTIMES)
@pytest.mark.parametrize("field,value", [
    ("prompt", "agents/../../outside.md"), ("shared_prefix", "../outside.md"),
    ("name", "different"), ("home_platform", None),
])
def test_invalid_definition_fails_closed(tmp_path, runtime, field, value):
    path, definition = sample(tmp_path)
    definition[field] = value
    path.write_text(yaml.safe_dump(definition))
    assert render(runtime, tmp_path).returncode != 0


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_unselected_agents_are_skipped(tmp_path, runtime):
    path, definition = sample(tmp_path)
    definition["shadows"] = []
    path.write_text(yaml.safe_dump(definition))
    assert render(runtime, tmp_path).returncode == 0
    assert list((tmp_path / "agents" / runtime).iterdir()) == []
