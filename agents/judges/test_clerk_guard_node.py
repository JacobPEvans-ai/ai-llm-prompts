"""Runs the clerk's Code guard node over the guard fixtures: intent in, tool calls out.

The mandates and the environment come from the matching model-suite case. The Code guard
builds a create call as a preview. It builds list and get calls from its output fields. An
update returns the get that checks the task first. Only that first call is compared.
"""

import json
from pathlib import Path

import pytest
import yaml


_EVALS = Path(__file__).resolve().parents[2] / "agents" / "evals"
_DSL = Path(__file__).resolve().parents[2] / "agents" / "dify" / "vikunja-clerk.dsl.yml"
_DEFAULT_CONTEXT = {
    "mode": "live",
    "allowed_projects": ["project-allowed"],
    "denied_projects": ["project-denied"],
    "inbox": "project-inbox",
}


def _code_guard():
    dsl = yaml.safe_load(_DSL.read_text())
    node = next(item for item in dsl["workflow"]["graph"]["nodes"] if item["data"].get("title") == "Code guard")
    namespace = {}
    exec(compile(node["data"]["code"], "Code guard", "exec"), namespace)  # defines the node's functions only
    return namespace["main"]


_MAIN = _code_guard()
_FIXTURES = yaml.safe_load((_EVALS / "guard" / "vikunja-clerk-args.yaml").read_text())["cases"]
_MODEL = {case["id"]: case for case in yaml.safe_load((_EVALS / "vikunja-clerk.yaml").read_text())["cases"]}


def _call(operation, args):
    return {"tool": "vikunja_tasks", "operation": operation, "args": args}


def _run(case):
    model = _MODEL[case["id"]]
    fields = model.get("structured_fields", {})
    context = {**_DEFAULT_CONTEXT, **model.get("guard_context", {})}
    result = _MAIN(
        json.dumps(case["intent"]),
        str(fields.get("project_id") or ""),
        str(fields.get("task_id") or ""),
        json.dumps(context["allowed_projects"]),
        json.dumps(context["denied_projects"]),
        context["inbox"],
        context["mode"],
    )
    if result["needs_update_check"]:
        return [_call("get", {"id": result["task_id"]})], True
    if result["preview"]:
        assert result["dispatch"] == (context["mode"] == "live"), "dispatch must equal (mode == live)"
        call = json.loads(result["preview"])
        operation = call["args"].pop("subcommand")
        return [{"tool": call["tool"], "operation": operation, "args": call["args"]}], False
    if result["dispatch"] and result["operation"] == "get":
        return [_call("get", {"id": result["task_id"]})], False
    if result["dispatch"] and result["operation"] == "list":
        args = {key: result[key] for key in ("done", "filter", "search") if result[key] not in (None, "")}
        return [_call("list", args)], False
    return [], False


@pytest.mark.parametrize("case", _FIXTURES, ids=[case["id"] for case in _FIXTURES])
def test_code_guard_builds_the_fixture_calls(case):
    calls, partial = _run(case)
    expected = case["expected_tool_calls"]
    if partial:
        assert calls == expected[:1]
    else:
        assert calls == expected
