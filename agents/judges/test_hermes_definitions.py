"""Offline contracts for canonical Hermes tasks and native Promptfoo suites."""

from pathlib import Path
import json

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / "agents"
SCOUTS = {
    "model-watch",
    "benchmark-tracker",
    "trending-quants",
    "ai-news-digest",
    "model-benchmarker",
}
DEFINITIONS = [
    (path, yaml.safe_load(path.read_text()))
    for path in sorted(AGENTS.glob("*.yaml"))
    if yaml.safe_load(path.read_text()).get("home_platform") == "hermes"
]


@pytest.mark.parametrize("path,agent", DEFINITIONS, ids=[p.stem for p, _ in DEFINITIONS])
def test_hermes_authority_and_local_routing(path, agent):
    assert agent["name"] == path.stem
    assert agent["schema_version"] == 2
    assert agent["mode"] == "shadow"
    assert agent["tier"] == (0 if path.stem == "donna" else 2)
    assert agent["privacy_class"] == "private"
    assert agent["code_work"] == "none"
    assert agent["mcp_servers"] == []
    assert agent["litellm_role"] == "review-local"
    assert agent["routing"] == {
        "local_only": True,
        "cloud_fallback": False,
        "max_wait_seconds": 43200,
    }
    assert agent["a2a"] == {
        "gateway": "agentgateway",
        "identity_check": "required",
        "allowlist_from": ["connectors", "peers"],
    }
    assert set(agent["tools"]) <= {
        "litellm.chat_completions", "a2a.call", "web_search", "web_extract"
    }
    assert set(agent["observability"]["attributes"]) == {
        "agent", "tier", "privacy_class", "model", "accelerator"
    }
    assert {"langfuse-trace", "phoenix-trace"} <= set(agent["channels"])
    assert agent["triggers"][0] == agent["trigger"]
    prompt = (ROOT / agent["prompt"]).read_text()
    assert "Mode is shadow" in prompt
    assert "never dispatch writes" in prompt
    assert "Preserve source bookmarks on" in prompt
    assert "confirmed receipt" in prompt


@pytest.mark.parametrize("path,agent", DEFINITIONS, ids=[p.stem for p, _ in DEFINITIONS])
def test_native_promptfoo_suite_references_canonical_sources(path, agent):
    suite_path = ROOT / agent["eval_set"]
    suite = yaml.safe_load(suite_path.read_text())
    variables = suite["defaultTest"]["vars"]
    for field, target in (("agent_prompt", agent["prompt"]), ("shared_prefix", agent["shared_prefix"])):
        assert variables[field].startswith("file://")
        assert (suite_path.parent / variables[field][7:]).resolve() == ROOT / target
    assert suite["defaultTest"]["assert"][0] == {
        "type": "is-json", "value": agent["output_schema"]
    }
    assert suite["sharing"] is False
    assert suite["writeLatestResults"] is False
    provider = suite["providers"][0]
    assert provider["id"] == "openai:chat:{{ env.EVAL_LOCAL_MODEL }}"
    assert provider["config"]["passthrough"]["metadata"]["privacy_class"] == "private"
    tests = suite["tests"]
    assert len(tests) >= 3
    assert len({test["description"] for test in tests}) == len(tests)
    for case in tests:
        assert isinstance(json.loads(case["vars"]["task"]), dict)
        assert case["assert"], "every case needs a scored outcome"


def test_scouts_share_the_dossier_gate_and_connector_boundary():
    for name in SCOUTS:
        agent = yaml.safe_load((AGENTS / f"{name}.yaml").read_text())
        prompt = (ROOT / agent["prompt"]).read_text()
        assert agent["tier"] == 2
        assert agent["connectors"] == ["github-clerk"]
        assert "Never edit the model list yourself" in prompt
        assert "older than\n12 months" in prompt
        assert "UNVERIFIED" in prompt
        if name != "model-benchmarker":
            assert agent["peers"] == ["model-benchmarker"]
    minutes = [
        yaml.safe_load((AGENTS / f"{name}.yaml").read_text())["trigger"]["cron"].split()[0]
        for name in SCOUTS
    ]
    assert len(set(minutes)) == len(minutes)


def test_model_watch_organizations_are_an_overridable_input():
    agent = yaml.safe_load((AGENTS / "model-watch.yaml").read_text())
    assert agent["parameters"]["llm_model_watch_orgs"] == {
        "type": "array",
        "items": {"type": "string"},
        "default": ["Qwen", "mlx-community", "unsloth", "nvidia", "bartowski"],
    }
    assert agent["parameters"]["llm_model_watch_limit_per_org"]["minimum"] == 1
    assert agent["parameters"]["llm_model_watch_accelerators"]["default"] == []


def test_dossier_covers_all_model_kinds_and_artifact_admission():
    text = (AGENTS / "prompts/model-benchmarker.md").read_text()
    for evidence in (
        "immutable revision", "license", "calibration provenance", "conversion date",
        "observed download date", "chat template", "reasoning parser", "tool parser",
        "co-resident", "concurrency", "predeclared acceptance criteria",
        "Arena", "LiveBench", "Artificial Analysis", "class balance", "abstention",
        "RULER", "AA-LCR", "LongBench", "SWE-bench", "Terminal-Bench", "LiveCodeBench",
        "Aider", "BFCL", "tau-bench", "MTEB", "ViDoRe", "re-embedding", "BEIR",
        "MIRACL", "OCRBench", "OmniDocBench", "olmOCR", "AILuminate", "HarmBench",
    ):
        assert evidence in text
