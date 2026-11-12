"""Exercise the Slack Clerk Dify intent prompt and read guard."""

import json
from pathlib import Path

import pytest
import yaml


_AGENTS = Path(__file__).resolve().parents[1]
_OPERATIONS = ("get_channel_history", "get_thread_replies")
_INTENT_SHAPE = 'Return only one JSON object with exactly this shape: {"operation":"<operation>"}.'


def _source():
    return yaml.safe_load((_AGENTS / "slack-clerk.yaml").read_text())


def _node(source, node_id):
    nodes = source["dify"]["workflow"]["graph"]["nodes"]
    return next(node["data"] for node in nodes if node["id"] == node_id)


def _guard():
    namespace = {}
    code = _node(_source(), "guard")["code"]
    exec(compile(code, "slack-clerk guard", "exec"), namespace)
    return namespace["main"]


def _call(intent_text, operation):
    thread_ts = "1712345678.1234" if operation == "get_thread_replies" else ""
    return _guard()(intent_text, operation, "C123ABC", thread_ts, 20, '["C123ABC"]')


def test_parse_request_prompt_documents_exact_intent_shape():
    parse_request = _node(_source(), "parse_request")
    user_prompt = next(message["text"] for message in parse_request["prompt_template"] if message["role"] == "user")

    assert _INTENT_SHAPE in user_prompt
    assert f"The operation value must be exactly one of: {', '.join(_OPERATIONS)}." in user_prompt
    assert "No other keys, prose, or Markdown." in user_prompt


@pytest.mark.parametrize("operation", _OPERATIONS)
def test_documented_intent_shape_passes_guard(operation):
    result = _call(json.dumps({"operation": operation}), operation)

    assert result["allowed"] is True
    assert result["operation"] == operation


@pytest.mark.parametrize("operation", _OPERATIONS)
def test_guard_rejects_unknown_intent_keys(operation):
    result = _call(json.dumps({"operation": operation, "extra": "rejected"}), operation)

    assert result["allowed"] is False
    assert result["error"] == "request classification did not match the typed operation"


def test_guard_rejects_intent_that_does_not_match_typed_operation():
    result = _call(json.dumps({"operation": "get_channel_history"}), "get_thread_replies")

    assert result["allowed"] is False
    assert result["error"] == "request classification did not match the typed operation"


def test_guard_rejects_unknown_operation():
    result = _call(json.dumps({"operation": "post_message"}), "post_message")

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
    assert "slack.post_message" not in source["dify_tools"]
