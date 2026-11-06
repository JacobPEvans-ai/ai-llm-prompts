"""Offline contracts for canonical Hermes tasks and native Promptfoo suites."""

from pathlib import Path
import json
import re

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
def test_task_connectors_are_declared_for_a2a(path, agent):
    prompt = (ROOT / agent["prompt"]).read_text()
    task = prompt.split("## Authority and completion", 1)[0]
    required = set(re.findall(r"\b[a-z]+-clerk\b", task))
    assert required <= set(agent["connectors"]), (
        f"{path.stem} lacks task connectors: {sorted(required - set(agent['connectors']))}"
    )
    assert "connectors" in agent["a2a"]["allowlist_from"]


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


def test_every_source_cron_prompt_has_a_definition_without_reviving_retirements():
    snapshot = yaml.safe_load((AGENTS / "evals/fixtures/hermes-cron-roster.yaml").read_text())
    for name, original in snapshot["crons"].items():
        path = AGENTS / f"{name}.yaml"
        if not original["prompt"]:
            assert not path.exists(), "promptless retirement records must stay retired"
            continue
        agent = yaml.safe_load(path.read_text())
        assert agent["home_platform"] == "hermes"
        assert agent["enabled"] == original["enabled"]
        assert {
            "path": original["source"],
            "prompt": original["prompt"],
            "revision": snapshot["revision"],
        }.items() <= agent["source_replacements"][0].items()
        expected_cron = original["schedule"]
        if name == "zammad-review":
            expected_cron = expected_cron.replace("41 ", "43 ", 1)
            assert agent["source_replacements"][0]["schedule_pull_request"] == 2042
        assert agent["trigger"]["cron"] == expected_cron


def _cron_values(expression, maximum):
    values = set()
    for part in expression.split(","):
        if part == "*":
            values.update(range(maximum + 1))
        elif part.startswith("*/"):
            values.update(range(0, maximum + 1, int(part[2:])))
        elif "-" in part:
            start, end = map(int, part.split("-"))
            values.update(range(start, end + 1))
        else:
            values.add(int(part))
    return values


def test_enabled_crons_and_new_scouts_have_distinct_weekly_start_minutes():
    occupied = {}
    for path, agent in DEFINITIONS:
        trigger = agent["trigger"]
        if not agent.get("enabled", True) or trigger["kind"] != "schedule":
            continue
        minute, hour, day, month, weekday = trigger["cron"].split()
        assert day == month == "*"
        for dow in _cron_values(weekday, 6):
            for hh in _cron_values(hour, 23):
                for mm in _cron_values(minute, 59):
                    slot = (dow, hh, mm)
                    assert slot not in occupied, (
                        f"{path.stem} collides with {occupied.get(slot)} at {slot}"
                    )
                    occupied[slot] = path.stem
