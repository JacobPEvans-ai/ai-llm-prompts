"""The docs-updater Dify gate admits both mandate shapes and rejects everything else."""

from pathlib import Path

import pytest
import yaml


_ROOT = Path(__file__).resolve().parents[2]
_DSL = _ROOT / "agents" / "dify" / "docs-updater.dsl.yml"
_GATE_TITLE = "Validate merged PR event"
_NODES = yaml.safe_load(_DSL.read_text())["workflow"]["graph"]["nodes"]
_START = next(node["data"] for node in _NODES if node.get("data", {}).get("type") == "start")
_GATE = next(node["data"] for node in _NODES if node.get("data", {}).get("title") == _GATE_TITLE)
_PR_EVENT = {
    "event": "pull_request",
    "action": "closed",
    "merged": "true",
    "org": "dryvist",
    "repo": "dryvist/example",
    "pr_number": 141,
}


def _run_gate(**inputs):
    declared = {variable["variable"] for variable in _START["variables"]}
    kwargs = {}
    for binding in _GATE["variables"]:
        selector = binding["value_selector"]
        assert selector[0] == "start" and selector[1] in declared, binding
        kwargs[binding["variable"]] = inputs.get(selector[1], "")
    namespace = {}
    exec(compile(_GATE["code"], _GATE_TITLE, "exec"), namespace)  # defines the gate's function only
    return namespace["main"](**kwargs)


def test_event_gate_routes_only_on_the_pull_request_eligibility_output():
    event_gate = next(node["data"] for node in _NODES if node["id"] == "event_gate")
    conditions = event_gate["cases"][0]["conditions"]
    assert [condition["variable_selector"] for condition in conditions] == [["validate_event", "eligible"]]


def test_shape_a_merged_pull_request_is_accepted_and_eligible():
    result = _run_gate(**_PR_EVENT)
    assert result["accepted"] == 1 and result["eligible"] == 1
    assert result["decision"] == "" and result["finding_ref"] == ""


@pytest.mark.parametrize("decision", ["A", "B", "neither"])
def test_shape_b_operator_decision_is_accepted_without_pull_request_reads(decision):
    result = _run_gate(repo="dryvist/example", finding_ref="finding-1", operator_decision=decision)
    assert result == {"accepted": 1, "eligible": 0, "decision": decision, "finding_ref": "finding-1"}


@pytest.mark.parametrize("decision", ["C", "a", "maybe"])
def test_shape_b_unknown_operator_decision_is_rejected(decision):
    result = _run_gate(repo="dryvist/example", finding_ref="finding-1", operator_decision=decision)
    assert result["accepted"] == 0 and result["eligible"] == 0


def test_shape_b_keeps_the_repository_allowlist():
    result = _run_gate(repo="other-org/example", finding_ref="finding-1", operator_decision="A")
    assert result["accepted"] == 0


def test_shape_b_rejects_a_malformed_finding_reference():
    result = _run_gate(repo="dryvist/example", finding_ref="finding 1; drop", operator_decision="A")
    assert result["accepted"] == 0


def test_shape_a_rejects_a_pull_request_outside_the_dryvist_org():
    result = _run_gate(**{**_PR_EVENT, "org": "other-org"})
    assert result["accepted"] == 0 and result["eligible"] == 0
