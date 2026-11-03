"""The docs-updater Dify gate admits both mandate shapes and rejects everything else."""

from pathlib import Path

import pytest
import yaml


_ROOT = Path(__file__).resolve().parents[2]
_DSL = _ROOT / "agents" / "dify" / "docs-updater.dsl.yml"
_GATE_TITLE = "Validate merged PR event"
_NODES = yaml.safe_load(_DSL.read_text())["workflow"]["graph"]["nodes"]
_START = next(
    node["data"] for node in _NODES if node.get("data", {}).get("type") == "start"
)
_GATE = next(
    node["data"] for node in _NODES if node.get("data", {}).get("title") == _GATE_TITLE
)
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
    exec(
        compile(_GATE["code"], _GATE_TITLE, "exec"), namespace
    )  # defines the gate's function only
    return namespace["main"](**kwargs)


def test_event_gate_routes_only_on_the_pull_request_eligibility_output():
    event_gate = next(node["data"] for node in _NODES if node["id"] == "event_gate")
    conditions = event_gate["cases"][0]["conditions"]
    assert [condition["variable_selector"] for condition in conditions] == [
        ["validate_event", "eligible"]
    ]


def test_shape_a_merged_pull_request_is_accepted_and_eligible():
    result = _run_gate(**_PR_EVENT)
    assert result["accepted"] == 1 and result["eligible"] == 1
    assert result["decision"] == "" and result["finding_ref"] == ""


@pytest.mark.parametrize("decision", ["A", "B", "neither"])
def test_shape_b_operator_decision_is_accepted_without_pull_request_reads(decision):
    result = _run_gate(
        repo="dryvist/example", finding_ref="finding-1", operator_decision=decision
    )
    assert result == {
        "accepted": 1,
        "eligible": 0,
        "decision": decision,
        "finding_ref": "finding-1",
    }


@pytest.mark.parametrize("decision", ["C", "a", "maybe"])
def test_shape_b_unknown_operator_decision_is_rejected(decision):
    result = _run_gate(
        repo="dryvist/example", finding_ref="finding-1", operator_decision=decision
    )
    assert result["accepted"] == 0 and result["eligible"] == 0


def test_shape_b_keeps_the_repository_allowlist():
    result = _run_gate(
        repo="other-org/example", finding_ref="finding-1", operator_decision="A"
    )
    assert result["accepted"] == 0


def test_shape_b_rejects_a_malformed_finding_reference():
    result = _run_gate(
        repo="dryvist/example", finding_ref="finding 1; drop", operator_decision="A"
    )
    assert result["accepted"] == 0


def test_shape_a_rejects_a_pull_request_outside_the_dryvist_org():
    result = _run_gate(**{**_PR_EVENT, "org": "other-org"})
    assert result["accepted"] == 0 and result["eligible"] == 0


_EDGES = yaml.safe_load(_DSL.read_text())["workflow"]["graph"]["edges"]
_PULL_REQUEST_PATH = [
    "start",
    "validate_event",
    "event_gate",
    "openbao_login",
    "parse_openbao",
    "login_gate",
    "token_request",
    "token_request_gate",
    "mint_github_token",
    "parse_github_token",
    "token_gate",
    "get_repo",
    "get_pull_request",
    "get_pull_files",
    "prepare_context",
    "context_gate",
    "docs_updater_llm",
    "validate_proposal",
    "end_proposal",
]
_PULL_REQUEST_READS = {
    "openbao_login",
    "mint_github_token",
    "get_repo",
    "get_pull_request",
    "get_pull_files",
}


def _walk(start, handles):
    """Follow one rendered edge per handle from start. Each hop must have exactly one matching edge."""
    node, visited = start, [start]
    for handle in handles:
        targets = [
            edge["target"]
            for edge in _EDGES
            if edge["source"] == node and edge.get("sourceHandle") == handle
        ]
        assert len(targets) == 1, (
            f"{node} has {len(targets)} edges on handle {handle!r}"
        )
        node = targets[0]
        visited.append(node)
    return visited


def test_every_rendered_edge_joins_two_declared_nodes():
    ids = {node["id"] for node in _NODES}
    assert all(edge["source"] in ids and edge["target"] in ids for edge in _EDGES)


def test_operator_decision_edges_reach_the_model_without_pull_request_reads():
    visited = _walk(
        "start", ["source", "source", "false", "accepted", "source", "eligible"]
    )
    assert visited == [
        "start",
        "validate_event",
        "event_gate",
        "decision_gate",
        "prepare_context",
        "context_gate",
        "docs_updater_llm",
    ]
    assert not _PULL_REQUEST_READS & set(visited)


def test_pull_request_edges_still_route_through_the_reads_to_the_model():
    handles = [
        "source",
        "source",
        "eligible",
        "source",
        "source",
        "ready",
        "source",
        "eligible",
        "source",
        "source",
        "ready",
        "source",
        "source",
        "source",
        "source",
        "eligible",
        "source",
        "source",
    ]
    visited = _walk("start", handles)
    assert visited == _PULL_REQUEST_PATH
    assert "decision_gate" not in visited


def test_every_start_selector_names_a_declared_start_variable():
    declared = {variable["variable"] for variable in _START["variables"]}
    selectors = [
        binding["value_selector"]
        for node in _NODES
        for binding in node.get("data", {}).get("variables", [])
        if binding.get("value_selector", [""])[0] == "start"
    ]
    assert selectors and all(selector[1] in declared for selector in selectors)
