"""Exercise the Splunk Clerk Dify intent prompt and read guard."""

import json
from pathlib import Path

import pytest
import yaml


_AGENTS = Path(__file__).resolve().parents[1]
_OPERATIONS = ("search",)
_INTENT_SHAPE = 'Return only one JSON object with exactly this shape: {"operation":"<operation>"}.'
_QUERY = "search index=fixture_alerts sourcetype=synthetic_event | stats count"


def _source():
    return yaml.safe_load((_AGENTS / "splunk-clerk.yaml").read_text())


def _node(source, node_id):
    nodes = source["dify"]["workflow"]["graph"]["nodes"]
    return next(node["data"] for node in nodes if node["id"] == node_id)


def _guard():
    namespace = {}
    code = _node(_source(), "guard")["code"]
    exec(compile(code, "splunk-clerk guard", "exec"), namespace)
    return namespace["main"]


def _call(intent_text, operation="search"):
    return _guard()(
        operation,
        _QUERY,
        "-15m",
        "now",
        50,
        intent_text,
        '["fixture_alerts"]',
        '["synthetic_event"]',
    )


def test_parse_request_prompt_documents_exact_intent_shape():
    parse_request = _node(_source(), "parse_request")
    user_prompt = next(message["text"] for message in parse_request["prompt_template"] if message["role"] == "user")

    assert _INTENT_SHAPE in user_prompt
    assert f"The operation value must be exactly one of: {', '.join(_OPERATIONS)}." in user_prompt
    assert "No other keys, prose, or Markdown." in user_prompt


def test_documented_intent_shape_passes_guard():
    result = _call(json.dumps({"operation": "search"}))

    assert result["allowed"] is True
    assert result["search_query"].endswith("| head 50")


def test_guard_rejects_unknown_intent_keys():
    result = _call(json.dumps({"operation": "search", "extra": "rejected"}))

    assert result["allowed"] is False
    assert result["error"] == "request classification did not match the typed operation"


def test_guard_rejects_noncanonical_operation_case():
    result = _call(json.dumps({"operation": "search"}), "SEARCH")

    assert result["allowed"] is False
    assert result["error"] == "operation is outside the read-only scope"


def test_guard_rejects_unknown_operation():
    result = _call(json.dumps({"operation": "delete_index"}), "delete_index")

    assert result["allowed"] is False
    assert result["error"] == "operation is outside the read-only scope"


def test_dify_tools_match_read_only_graph_tools():
    source = _source()
    graph_tools = {
        f"{node['data']['provider_name']}.{node['data']['tool_name']}"
        for node in source["dify"]["workflow"]["graph"]["nodes"]
        if node["data"].get("type") == "tool"
    }

    assert set(source["dify_tools"]) == graph_tools
