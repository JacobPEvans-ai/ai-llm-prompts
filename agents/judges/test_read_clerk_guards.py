"""Exercise the source Dify intent guards and their prompt contracts."""

import json
from pathlib import Path

import pytest
import yaml


_ROOT = Path(__file__).resolve().parents[2]
_AGENTS = _ROOT / "agents"
_INTENT_SHAPE = 'Return only one JSON object with exactly this shape: {"operation":"<operation>"}.'
_OPERATIONS = {
    "github-clerk": ("get_pull_request", "list_pull_requests"),
    "zammad-clerk": ("search_tickets", "get_ticket"),
}


def _source(name):
    return yaml.safe_load((_AGENTS / f"{name}.yaml").read_text())


def _node(source, node_id):
    nodes = source["dify"]["workflow"]["graph"]["nodes"]
    return next(node["data"] for node in nodes if node["id"] == node_id)


def _main(source, node_id):
    namespace = {}
    exec(compile(_node(source, node_id)["code"], node_id, "exec"), namespace)
    return namespace["main"]


def _guard_call(name, intent_text, operation):
    source = _source(name)
    main = _main(source, "guard")
    if name == "github-clerk":
        pr_number = 17 if operation == "get_pull_request" else None
        state = "" if operation == "get_pull_request" else "open"
        return main(intent_text, operation, "example/repo", pr_number, state, '["example/repo"]')
    query = "synthetic ticket" if operation == "search_tickets" else ""
    ticket_id = 17 if operation == "get_ticket" else None
    return main(intent_text, operation, query, ticket_id, "https://example.test", "configured")


@pytest.mark.parametrize(("name", "operations"), _OPERATIONS.items())
def test_parse_request_prompt_documents_guard_shape(name, operations):
    parse_request = _node(_source(name), "parse_request")
    user_prompt = next(
        message["text"]
        for message in parse_request["prompt_template"]
        if message["role"] == "user"
    )

    assert _INTENT_SHAPE in user_prompt
    assert f"The operation value must be exactly one of: {', '.join(operations)}." in user_prompt
    assert "No other keys, prose, or Markdown." in user_prompt


@pytest.mark.parametrize(
    ("name", "operation"),
    [(name, operation) for name, operations in _OPERATIONS.items() for operation in operations],
)
def test_documented_intent_shape_passes_guard(name, operation):
    intent_text = json.dumps({"operation": operation})

    result = _guard_call(name, intent_text, operation)

    assert result["allowed"] is True
    assert result["operation"] == operation


@pytest.mark.parametrize(("name", "operation"), [(name, ops[0]) for name, ops in _OPERATIONS.items()])
def test_guard_rejects_unknown_intent_keys(name, operation):
    intent_text = json.dumps({"operation": operation, "extra": "rejected"})

    result = _guard_call(name, intent_text, operation)

    assert result["allowed"] is False
    assert result["error"] == "request classification did not match the typed operation"


@pytest.mark.parametrize("name", _OPERATIONS)
def test_guard_rejects_unknown_operations(name):
    operation = "delete_resource"
    intent_text = json.dumps({"operation": operation})

    result = _guard_call(name, intent_text, operation)

    assert result["allowed"] is False
    assert result["error"] == "operation is outside the read-only scope"


def test_github_pull_request_normalizer_is_shared_by_detail_and_list():
    source = _source("github-clerk")
    nodes = source["dify"]["workflow"]["graph"]["nodes"]
    normalize_nodes = [
        node for node in nodes
        if node["data"].get("title") == "Normalize pull request result"
    ]

    assert len(normalize_nodes) == 1
    normalize = normalize_nodes[0]
    code = normalize["data"]["code"]
    assert code.count("def pull_summary(") == 1
    assert "if operation == \"get_pull_request\":" in code
    assert "elif operation == \"list_pull_requests\":" in code
    selectors = {
        tuple(variable["value_selector"])
        for variable in normalize["data"]["variables"]
    }
    assert ("pull_detail", "text") in selectors
    assert ("list_pulls", "text") in selectors
    assert ("guard", "operation") in selectors

    edges = source["dify"]["workflow"]["graph"]["edges"]
    assert {
        edge["source"]
        for edge in edges
        if edge["target"] == normalize["id"]
    } == {"pull_detail", "list_pulls"}


def test_github_shared_normalizer_handles_detail_and_list_payloads():
    main = _main(_source("github-clerk"), "normalize_pull_request")
    repository_json = json.dumps({"full_name": "example/repo"})
    pull = {"number": 17, "title": "Synthetic change"}

    detail = main("get_pull_request", json.dumps(pull), "", repository_json)
    listed = main("list_pull_requests", "", json.dumps([pull]), repository_json)

    assert detail["status"] == listed["status"] == "found"
    assert detail["items"] == listed["items"]
    assert detail["items"][0]["repository"] == "example/repo"
