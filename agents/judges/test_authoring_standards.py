"""Mechanical authoring gates for profiles, trigger descriptions, and eval contracts."""

import math
from pathlib import Path
import re

import pytest
import yaml

from definitions import resolved_records


ROOT = Path(__file__).resolve().parents[2]
CATEGORIES = {"normal", "malformed", "ambiguous", "oversized", "unavailable-source", "negative-trigger"}
THRESHOLDS = {
    "correctness_min", "privacy_violations_max", "latency_ms_max",
    "cloud_cost_usd_max", "consequential_failures_max",
}


def redundant_paths(source, inherited, prefix=""):
    for key, value in source.items():
        if key not in inherited:
            continue
        path = f"{prefix}.{key}" if prefix else key
        previous = inherited[key]
        if isinstance(value, dict) and isinstance(previous, dict):
            yield from redundant_paths(value, previous, path)
        elif isinstance(value, bool) == isinstance(previous, bool) and value == previous:
            yield path


def validate_source(source, profile):
    assert isinstance(source, dict), "definition must be a mapping"
    assert isinstance(source.get("extends"), str) and source["extends"], "profile required"
    assert not {"prompt", "eval_set"}.intersection(source), "paths follow from name"
    for field in ("identity", "api_key_ref"):
        assert isinstance(source.get(field), str) and source[field].strip(), f"explicit {field} required"
    duplicates = list(redundant_paths(source, profile))
    assert not duplicates, f"redundant profile values: {duplicates}"


def validate_description(agent):
    description = agent.get("description")
    assert isinstance(description, str), "description required"
    for label in ("Use when", "Do not use when"):
        assert re.search(rf"(?im)^[ \t]*{label}:[ \t]*\S[^\n]*$", description), f"description requires {label} line"


def validate_unique_jobs(agents, bodies):
    stems = set()
    prompts = set()
    for agent, body in zip(agents, bodies, strict=True):
        name = agent["name"]
        assert not re.search(r"-v\d+(?:-|$)", name, re.IGNORECASE), "versioned agent name forbidden"
        stem = re.sub(r"[-_]", "", name.casefold())
        assert stem not in stems, "duplicate name stem"
        stems.add(stem)
        prompt = re.sub(r"\s+", " ", body).strip()
        assert prompt and prompt not in prompts, "duplicate prompt text"
        prompts.add(prompt)


def validate_eval_suite(suite):
    assert isinstance(suite, dict), "eval suite must be a mapping"
    cases = suite.get("cases")
    assert isinstance(cases, list) and cases, "eval cases required"
    categories = set()
    for case in cases:
        assert isinstance(case, dict), "eval case must be a mapping"
        assert not case.get("skip"), "coverage cases must run"
        assert isinstance(case.get("category"), str) and case["category"], "case category required"
        assert any(key in case for key in ("input", "input_fixture", "input_event_summary", "structured_fields", "tasks", "tickets")), "eval input required"
        assert case.get("expected_output") or case.get("expected_behavior"), "eval expectation required"
        categories.add(case["category"])
    assert CATEGORIES <= categories, f"missing eval categories: {CATEGORIES - categories}"


def validate_eval_policy(agent):
    policy = agent.get("eval_policy")
    assert isinstance(policy, dict), "eval policy required"
    thresholds = policy.get("thresholds")
    assert isinstance(thresholds, dict) and THRESHOLDS <= thresholds.keys(), "eval thresholds required"
    for key in THRESHOLDS:
        value = thresholds[key]
        assert type(value) in (int, float) and math.isfinite(value) and value >= 0, "invalid eval threshold"
    assert thresholds["correctness_min"] <= 1, "correctness threshold must be a ratio"
    assert thresholds["latency_ms_max"] > 0, "latency threshold must be positive"
    baseline = policy.get("baseline")
    assert isinstance(baseline, dict), "eval baseline required"
    assert baseline.get("compare_to") == "previous_released_version", "baseline must use previous release"
    assert baseline.get("missing_results") == "block_promotion", "missing baseline must block promotion"
    assert baseline.get("regression") == "block_promotion", "baseline regression must block promotion"


@pytest.fixture
def source_agent():
    return {
        "name": "example-agent", "extends": "interactive", "identity": "explicit-identity",
        "api_key_ref": "explicit-key", "routing": {"tier": 0},
        "description": "Use when: a draft needs checking.\nDo not use when: an edit is requested.",
    }


@pytest.fixture
def eval_suite():
    return {"cases": [{"id": category, "category": category, "input": "synthetic case", "expected_behavior": "Return a bounded result."} for category in sorted(CATEGORIES)]}


@pytest.fixture
def eval_agent():
    return yaml.safe_load((ROOT / "agents" / "profiles" / "defaults.yaml").read_text())


def test_profile_difference_passes(source_agent):
    validate_source(source_agent, {"routing": {"tier": 2, "local": True}})


@pytest.mark.parametrize("inherited", [{"routing": {"tier": 0}}, {"identity": "explicit-identity"}])
def test_restatement_fails_including_nested_values(source_agent, inherited):
    with pytest.raises(AssertionError, match="redundant profile values"):
        validate_source(source_agent, inherited)


def test_lists_replace_atomically_and_booleans_differ_from_numbers():
    assert list(redundant_paths({"tools": ["read"], "enabled": False}, {"tools": ["read", "write"], "enabled": 0})) == []
    assert list(redundant_paths({"tools": ["read"]}, {"tools": ["read"]})) == ["tools"]


@pytest.mark.parametrize("name,profile,fields", [
    (name, "task-advisor", ("connectors", "tools")) for name in (
        "donna-evening-wrap", "donna-research", "donna-weekly-review",
        "daily-innovation", "credential-steward", "agent-audit",
    )
] + [
    (name, "weekly-splunk-reader", ("privacy_class", "connectors", "tools", "triggers"))
    for name in ("voice-learn", "splunk-deepdive")
])
def test_shared_profiles_supply_values_and_reject_restatements(name, profile, fields):
    source = yaml.safe_load((ROOT / "agents" / f"{name}.yaml").read_text())
    assert source["extends"] == profile
    record = next(record for record in resolved_records() if record["agent"]["name"] == name)
    validate_source(source, record["profile"])
    for field in fields:
        assert field not in source
        assert record["agent"][field] == record["profile"][field]
        restated = {**source, field: record["agent"][field]}
        with pytest.raises(AssertionError, match=f"redundant profile values:.*{field}"):
            validate_source(restated, record["profile"])


@pytest.mark.parametrize("field", ["extends", "identity", "api_key_ref"])
def test_source_requires_explicit_references(source_agent, field):
    del source_agent[field]
    with pytest.raises(AssertionError):
        validate_source(source_agent, {})


@pytest.mark.parametrize("field", ["prompt", "eval_set"])
def test_source_cannot_restate_conventional_paths(source_agent, field):
    source_agent[field] = "agents/example"
    with pytest.raises(AssertionError, match="paths follow from name"):
        validate_source(source_agent, {})


def test_positive_and_negative_trigger_lines_pass(source_agent):
    validate_description(source_agent)


@pytest.mark.parametrize("name", [
    "agent-audit",
    "ai-news",
    "alert-triage",
    "credential-steward",
    "daily-innovation",
    "donna-evening-wrap",
    "donna-morning-brief",
    "donna-research",
    "donna-weekly-review",
    "github-clerk",
    "merge-steward",
    "model-benchmarker",
    "model-scout",
    "plan-reconciler",
    "pr-keeper",
    "promotion-review",
    "release-digest",
    "release-promoter",
    "repo-janitor",
    "session-closer",
    "ship-runner",
    "splunk-deepdive",
    "voice-learn",
    "zammad-clerk",
])
def test_consolidated_agents_describe_triggers_and_worked_invocations(name):
    source = yaml.safe_load((ROOT / "agents" / f"{name}.yaml").read_text())
    assert source["extends"]
    description = source["description"]
    assert "Typical triggers include " in description
    assert '"When to invoke"' in description
    body = (ROOT / "agents/prompts" / f"{name}.md").read_text().split("\n---\n", 1)[1]
    section = re.search(r"(?ms)^## When to invoke\n(.*?)(?=^## |\Z)", body)
    assert section, "worked invocation section required"
    scenarios = re.findall(r"(?m)^- \*\*[^\n]+?\*\* \S[^\n]*$", section[1])
    assert 2 <= len(scenarios) <= 4, "two to four worked invocation scenarios required"


@pytest.mark.parametrize("description", [None, "Use when: checking a draft.", "Do not use when: editing.", "Use when:\nDo not use when:", "Use when:\nDo not use when: editing.", "Use when: checking. Do not use when: editing."])
def test_missing_trigger_lines_fail(description):
    with pytest.raises(AssertionError):
        validate_description({"description": description})


def test_distinct_jobs_pass():
    validate_unique_jobs([{"name": "draft-checker"}, {"name": "task-clerk"}], ["Check a draft.", "Handle a task."])


@pytest.mark.parametrize("names,bodies,reason", [
    (["draft-checker", "task-clerk"], ["Same prompt.", "  Same\n prompt. "], "duplicate prompt"),
    (["draft-checker", "draft_checker"], ["Check a draft.", "Handle a task."], "duplicate name stem"),
    (["draft-checker", "draft-checker-v2"], ["Check a draft.", "Handle a task."], "versioned agent"),
    (["draft-v12-checker"], ["Check a draft."], "versioned agent"),
])
def test_duplicate_jobs_and_version_names_fail(names, bodies, reason):
    with pytest.raises(AssertionError, match=reason):
        validate_unique_jobs([{"name": name} for name in names], bodies)


def test_complete_eval_coverage_passes(eval_suite):
    validate_eval_suite(eval_suite)


@pytest.mark.parametrize("category", sorted(CATEGORIES))
def test_each_missing_eval_category_fails(eval_suite, category):
    eval_suite["cases"] = [case for case in eval_suite["cases"] if case["category"] != category]
    with pytest.raises(AssertionError, match="missing eval categories"):
        validate_eval_suite(eval_suite)


@pytest.mark.parametrize("field", ["category", "input", "expected_behavior"])
def test_eval_labels_need_input_and_expectations(eval_suite, field):
    del eval_suite["cases"][0][field]
    with pytest.raises(AssertionError):
        validate_eval_suite(eval_suite)


def test_skipped_cases_cannot_supply_coverage(eval_suite):
    eval_suite["cases"][0]["skip"] = "later"
    with pytest.raises(AssertionError, match="must run"):
        validate_eval_suite(eval_suite)


def test_inherited_eval_thresholds_and_baseline_pass(eval_agent):
    validate_eval_policy(eval_agent)


@pytest.mark.parametrize("field", ["thresholds", "baseline"])
def test_missing_thresholds_or_baseline_fail(eval_agent, field):
    del eval_agent["eval_policy"][field]
    with pytest.raises(AssertionError):
        validate_eval_policy(eval_agent)


@pytest.mark.parametrize("field", sorted(THRESHOLDS))
def test_each_required_threshold_fails_when_missing(eval_agent, field):
    del eval_agent["eval_policy"]["thresholds"][field]
    with pytest.raises(AssertionError, match="thresholds required"):
        validate_eval_policy(eval_agent)


@pytest.mark.parametrize("value", [True, None, "1", -1, float("nan"), float("inf")])
def test_invalid_thresholds_fail(eval_agent, value):
    eval_agent["eval_policy"]["thresholds"]["correctness_min"] = value
    with pytest.raises(AssertionError, match="invalid eval threshold"):
        validate_eval_policy(eval_agent)


@pytest.mark.parametrize("field,value", [("compare_to", "current"), ("missing_results", "allow"), ("regression", "allow")])
def test_baseline_rules_fail_closed(eval_agent, field, value):
    eval_agent["eval_policy"]["baseline"][field] = value
    with pytest.raises(AssertionError):
        validate_eval_policy(eval_agent)
