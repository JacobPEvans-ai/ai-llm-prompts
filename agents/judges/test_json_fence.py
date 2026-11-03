"""Tests for the shared JSON fence stripper used by Dify parse nodes, the promptfoo grader and the Python judge."""

import importlib.util
import json
from pathlib import Path
import re

import pytest
import yaml


_ROOT = Path(__file__).resolve().parents[2]
_HELPER_PATH = _ROOT / "agents" / "dify-src" / "helpers" / "json_fence.py"
_JUDGE_PATH = _ROOT / "agents" / "judges" / "parse-json-schema.py"
_CALL = re.compile(r"json\.loads\(strip_json_fence\(")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_helper = _load(_HELPER_PATH, "json_fence_helper")
_judge = _load(_JUDGE_PATH, "parse_json_schema_judge")

_OBJECT = '{"decision": "none", "proposed_calls": [], "reply": "ok"}'
_CASES = [
    (_OBJECT, _OBJECT),
    (f"```json\n{_OBJECT}\n```", _OBJECT),
    (f"```\n{_OBJECT}\n```", _OBJECT),
    (f"  ```JSON\n{_OBJECT}\n```  ", _OBJECT),
    (f"```json{_OBJECT}```", _OBJECT),
    (
        f"Here you go:\n```json\n{_OBJECT}\n```",
        f"Here you go:\n```json\n{_OBJECT}\n```",
    ),
    ("```unterminated", "```unterminated"),
    ("null", "null"),
    ("  " + _OBJECT + "  ", "  " + _OBJECT + "  "),
    ("﻿```json\n" + _OBJECT + "\n```", "﻿```json\n" + _OBJECT + "\n```"),
    ("\x1c" + _OBJECT, "\x1c" + _OBJECT),
]


@pytest.mark.parametrize(("raw", "expected"), _CASES)
def test_helper_strips_only_one_surrounding_fence(raw, expected):
    assert _helper.strip_json_fence(raw) == expected


@pytest.mark.parametrize(("raw", "expected"), _CASES)
def test_python_judge_copy_matches_the_helper(raw, expected):
    assert _judge.strip_json_fence(raw) == _helper.strip_json_fence(raw) == expected


def test_fenced_object_parses_and_bare_prose_still_fails():
    assert json.loads(
        _helper.strip_json_fence(f"```json\n{_OBJECT}\n```")
    ) == json.loads(_OBJECT)
    with pytest.raises(json.JSONDecodeError):
        json.loads(_helper.strip_json_fence("Here you go: " + _OBJECT))


def test_judge_gives_a_fenced_reply_the_same_verdict_as_the_bare_reply():
    assert _judge.check_reply(f"```json\n{_OBJECT}\n```") == _judge.check_reply(_OBJECT)


def _rendered_nodes():
    for path in sorted((_ROOT / "agents" / "dify").glob("*.dsl.yml")):
        dsl = yaml.safe_load(path.read_text())
        for node in dsl["workflow"]["graph"]["nodes"]:
            code = node.get("data", {}).get("code", "")
            if isinstance(code, str) and _CALL.search(code):
                yield path.name, node["data"]["title"], code


_NODES = list(_rendered_nodes())


def test_every_model_output_parse_node_routes_through_the_helper():
    names = {(file, title) for file, title, _ in _NODES}
    assert names == {
        ("ci-fixer.dsl.yml", "Validate patch and write guards"),
        ("code-simplifier.dsl.yml", "Validate and force comment review"),
        ("doc-contradiction-finder.dsl.yml", "Validate contradiction findings"),
        ("docs-updater.dsl.yml", "Validate safe page proposals"),
        ("vikunja-clerk.dsl.yml", "Code guard"),
        ("vikunja-clerk.dsl.yml", "Update project guard"),
        ("vikunja-triage.dsl.yml", "Guard proposed actions"),
        ("zammad-triage.dsl.yml", "Guard and dispatch"),
    }


@pytest.mark.parametrize(
    ("file", "title", "code"), _NODES, ids=[f"{f}:{t}" for f, t, _ in _NODES]
)
def test_rendered_node_defines_helper_and_accepts_a_fenced_reply(file, title, code):
    namespace = {}
    exec(
        compile(code, f"{file}:{title}", "exec"), namespace
    )  # defines the node's functions only
    assert namespace["strip_json_fence"](f"```json\n{_OBJECT}\n```") == _OBJECT
