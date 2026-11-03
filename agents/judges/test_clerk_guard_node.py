"""Runs the clerk's Code guard nodes over the guard fixtures: intent in, tool calls out.

The first node, "Code guard", takes the intent and builds the first call. The second node,
"Update project guard", takes the fetched task and builds the update.

A case gives its intent as a mapping. A case with intent_raw gives the exact text the guard receives.
A case takes its mandates and context from the case itself. A case that sets neither takes them
from the matching model-suite case. A refused case must return allowed false and the reason
fragment the case names. Every other case must return allowed true. Each refusal has a control
case that changes only the inputs the refusal names (offends) and must pass.

The Code guard builds a create call as a preview. It builds list and get calls from its output
fields. An update returns the get that checks the task first. Only that first call is compared.
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
_ABSENT = object()


def _code_guard(title):
    dsl = yaml.safe_load(_DSL.read_text())
    node = next(item for item in dsl["workflow"]["graph"]["nodes"] if item["data"].get("title") == title)
    namespace = {}
    exec(compile(node["data"]["code"], title, "exec"), namespace)  # defines the node's functions only
    return namespace["main"]


def _load_cases(*names):
    return [case for name in names for case in yaml.safe_load((_EVALS / "guard" / name).read_text())["cases"]]


_MAIN = _code_guard("Code guard")
_UPDATE_MAIN = _code_guard("Update project guard")
_FIXTURES = _load_cases("vikunja-clerk-args.yaml", "vikunja-clerk-args-scope.yaml")
_UPDATE_FIXTURES = _load_cases("vikunja-clerk-update.yaml", "vikunja-clerk-update-gaps.yaml")
_BY_ID = {case["id"]: case for case in _FIXTURES}
_UPDATE_BY_ID = {case["id"]: case for case in _UPDATE_FIXTURES}
_MODEL = {case["id"]: case for case in yaml.safe_load((_EVALS / "vikunja-clerk.yaml").read_text())["cases"]}


def _call(operation, args):
    return {"tool": "vikunja_tasks", "operation": operation, "args": args}


def _inputs(case):
    model = _MODEL.get(case["id"], {})
    fields = model.get("structured_fields", {})
    mandates = case.get("mandates", {"project_id": fields.get("project_id"), "task_id": fields.get("task_id")})
    context = {**_DEFAULT_CONTEXT, **model.get("guard_context", {}), **case.get("context", {})}
    return {
        "intent": case["intent"],
        "intent_raw": case.get("intent_raw"),
        "task_result": case.get("task_result"),
        "mandates": {key: str(value or "") for key, value in mandates.items()},
        "context": context,
    }


def _run(case):
    inputs = _inputs(case)
    context = inputs["context"]
    intent_text = inputs["intent_raw"] if inputs["intent_raw"] is not None else json.dumps(inputs["intent"])
    result = _MAIN(
        intent_text,
        inputs["mandates"]["project_id"],
        inputs["mandates"]["task_id"],
        context.get("allowed_projects_raw", json.dumps(context["allowed_projects"])),
        json.dumps(context["denied_projects"]),
        context["inbox"],
        context["mode"],
    )
    if result["needs_update_check"]:
        return [_call("get", {"id": result["task_id"]})], True, result
    if result["preview"]:
        assert result["dispatch"] == (context["mode"] == "live"), "dispatch must equal (mode == live)"
        call = json.loads(result["preview"])
        operation = call["args"].pop("subcommand")
        return [{"tool": call["tool"], "operation": operation, "args": call["args"]}], False, result
    if result["dispatch"] and result["operation"] == "get":
        return [_call("get", {"id": result["task_id"]})], False, result
    if result["dispatch"] and result["operation"] == "list":
        args = {key: result[key] for key in ("done", "filter", "search") if result[key] not in (None, "")}
        return [_call("list", args)], False, result
    return [], False, result


def _run_update(case):
    inputs = _inputs(case)
    context = inputs["context"]
    result = _UPDATE_MAIN(
        json.dumps(inputs["intent"]),
        json.dumps(inputs["task_result"]),
        inputs["mandates"]["project_id"],
        inputs["mandates"]["task_id"],
        context.get("allowed_projects_raw", json.dumps(context["allowed_projects"])),
        context.get("denied_projects_raw", json.dumps(context["denied_projects"])),
        context["mode"],
    )
    if result["preview"]:
        assert result["dispatch"] == (context["mode"] == "live"), "dispatch must equal (mode == live)"
        call = json.loads(result["preview"])
        operation = call["args"].pop("subcommand")
        return [{"tool": call["tool"], "operation": operation, "args": call["args"]}], result
    return [], result


def _flatten(value, prefix=""):
    if isinstance(value, dict):
        flat = {}
        for key, item in value.items():
            flat.update(_flatten(item, f"{prefix}.{key}" if prefix else key))
        return flat
    return {prefix: value}


def _changed_paths(first, second):
    a, b = _flatten(first), _flatten(second)
    return {path for path in set(a) | set(b) if a.get(path, _ABSENT) != b.get(path, _ABSENT)}


@pytest.mark.parametrize("case", _FIXTURES, ids=[case["id"] for case in _FIXTURES])
def test_code_guard_builds_the_fixture_calls(case):
    calls, partial, result = _run(case)
    if case.get("refusal"):
        assert result["allowed"] is False, result["reason"]
        assert case["refusal"] in result["reason"]
    else:
        assert result["allowed"] is True, result["reason"]
    expected = case["expected_tool_calls"]
    if partial:
        assert calls == expected[:1]
    else:
        assert calls == expected


_REFUSALS = [case for case in _FIXTURES if case.get("refusal")]


@pytest.mark.parametrize("case", _REFUSALS, ids=[case["id"] for case in _REFUSALS])
def test_each_refusal_has_a_control_that_changes_only_what_it_offends(case):
    control = _BY_ID[case["id"] + "-control"]
    assert "refusal" not in control
    assert _changed_paths(_inputs(case), _inputs(control)) == set(case["offends"])


@pytest.mark.parametrize("case", _UPDATE_FIXTURES, ids=[case["id"] for case in _UPDATE_FIXTURES])
def test_update_guard_builds_the_fixture_calls(case):
    calls, result = _run_update(case)
    if case.get("refusal"):
        assert result["allowed"] is False, result["reason"]
        assert case["refusal"] in result["reason"]
    else:
        assert result["allowed"] is True, result["reason"]
    assert calls == case["expected_tool_calls"]


_UPDATE_REFUSALS = [case for case in _UPDATE_FIXTURES if case.get("refusal")]


@pytest.mark.parametrize("case", _UPDATE_REFUSALS, ids=[case["id"] for case in _UPDATE_REFUSALS])
def test_each_update_refusal_has_a_control_that_changes_only_what_it_offends(case):
    control = _UPDATE_BY_ID[case["id"] + "-control"]
    assert "refusal" not in control
    assert _changed_paths(_inputs(case), _inputs(control)) == set(case["offends"])
