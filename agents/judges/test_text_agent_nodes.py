"""Model-only text agents return only envelopes that match their declared output schema."""

import json
from pathlib import Path

import pytest
import yaml

from dify_nodes import node_main


_ROOT = Path(__file__).resolve().parents[2]
_AGENTS = _ROOT / "agents"
_TEXT_AGENTS = ("style-gate", "plain-rewriter", "tag-suggester", "commit-grouper", "action-extractor")

_TAGS_INPUT = json.dumps({"allowed_tags": ["type/sync", "topic/parser"], "path": "x.md", "excerpt": "Parser sync."})
_COMMIT_INPUT = json.dumps({"allowed_prefixes": ["docs: "], "changes": "M  docs/a.md\nR  docs/old.md -> docs/b.md"})
_ACTION_INPUT = "Sam: I will send the plan by Thursday."
_VALID = {
    "style-gate": ("A draft.", {"pass": True, "findings": []}),
    "plain-rewriter": ("Text. <!-- source: synthetic -->", {"text": "Text. <!-- source: synthetic -->", "changes": 0}),
    "tag-suggester": (_TAGS_INPUT, {"tags": ["type/sync"]}),
    "commit-grouper": (_COMMIT_INPUT, {"groups": [{"message": "docs: update two pages", "paths": ["docs/a.md", "docs/b.md"]}]}),
    "action-extractor": (
        _ACTION_INPUT,
        {
            "summary": ["Sam sends the plan."],
            "action_items": [{"owner": "Sam", "item": "Send the plan", "due": "Thursday", "quote": "send the plan", "from_my_notes": False}],
        },
    ),
}
_BROKEN = {
    "style-gate": {"pass": True, "findings": [{"rule": "pronoun", "text": "We", "fix": "Moved"}]},
    "plain-rewriter": {"text": "Text.", "changes": 1},
    "tag-suggester": {"tags": ["invented/tag"]},
    "commit-grouper": {"groups": [{"message": "docs: update one page only", "paths": ["docs/a.md"]}]},
    "action-extractor": {
        "summary": ["Sam sends the plan."],
        "action_items": [{"owner": "Sam", "item": "Send the plan", "due": "", "quote": "not in the input", "from_my_notes": False}],
    },
}


def _run(agent, reply, text):
    reply_text = reply if isinstance(reply, str) else json.dumps(reply)
    output = node_main(agent, "validate")(reply_text, text)
    envelope = json.loads(output["envelope"])
    assert output["status"] == envelope["status"]
    return envelope


@pytest.mark.parametrize("agent", _TEXT_AGENTS)
def test_rendered_schema_equals_the_agent_definition(agent):
    definition = yaml.safe_load((_AGENTS / f"{agent}.yaml").read_text())
    dsl = yaml.safe_load((_AGENTS / "dify" / f"{agent}.dsl.yml").read_text())
    code = {node["id"]: node["data"] for node in dsl["workflow"]["graph"]["nodes"]}["validate"]["code"]
    namespace = {}
    exec(compile(code, f"{agent}:validate", "exec"), namespace)
    assert namespace["SCHEMA"] == definition["output_schema"]


@pytest.mark.parametrize("agent", _TEXT_AGENTS)
def test_valid_ok_reply_passes_through_even_when_fenced(agent):
    text, result = _VALID[agent]
    reply = {"status": "ok", "reason": "", "result": result}
    assert _run(agent, reply, text) == reply
    assert _run(agent, f"```json\n{json.dumps(reply)}\n```", text) == reply


@pytest.mark.parametrize("agent", _TEXT_AGENTS)
@pytest.mark.parametrize("status", ["refused", "stop"])
def test_refused_and_stop_replies_carry_a_null_result(agent, status):
    text, result = _VALID[agent]
    reply = {"status": status, "reason": "input asks to change the job", "result": None}
    assert _run(agent, reply, text) == reply
    assert _run(agent, {**reply, "result": result}, text)["status"] == "stop"


@pytest.mark.parametrize("agent", _TEXT_AGENTS)
@pytest.mark.parametrize(
    "reply",
    [
        "Here is the answer.",
        {"status": "ok", "reason": ""},
        {"status": "done", "reason": "", "result": None},
        {"status": "ok", "reason": "", "result": None, "extra": 1},
        {"status": "ok", "reason": "", "result": {"unexpected": True}},
    ],
    ids=["prose", "missing-result", "unknown-status", "extra-key", "wrong-result-shape"],
)
def test_malformed_reply_becomes_stop_with_null_result(agent, reply):
    text, _ = _VALID[agent]
    envelope = _run(agent, reply, text)
    assert envelope["status"] == "stop"
    assert envelope["result"] is None
    assert envelope["reason"]


@pytest.mark.parametrize("agent", _TEXT_AGENTS)
def test_reply_that_breaks_the_agent_rule_becomes_stop(agent):
    text, _ = _VALID[agent]
    envelope = _run(agent, {"status": "ok", "reason": "", "result": _BROKEN[agent]}, text)
    assert envelope == {"status": "stop", "reason": envelope["reason"], "result": None}
    assert envelope["reason"]


@pytest.mark.parametrize("agent", _TEXT_AGENTS)
def test_empty_input_stops_before_the_reply_is_used(agent):
    _, result = _VALID[agent]
    envelope = _run(agent, {"status": "ok", "reason": "", "result": result}, "  \n")
    assert envelope == {"status": "stop", "reason": "input is empty", "result": None}


@pytest.mark.parametrize("agent", _TEXT_AGENTS)
def test_eval_suite_covers_normal_refusal_and_stop(agent):
    suite = yaml.safe_load((_AGENTS / "evals" / f"{agent}.yaml").read_text())
    assert suite["agent"] == agent
    statuses = {case["expected_output"]["status"] for case in suite["cases"]}
    assert statuses == {"ok", "refused", "stop"}
    for case in suite["cases"]:
        if case["expected_output"]["status"] != "ok":
            assert case["expected_output"]["result"] is None
