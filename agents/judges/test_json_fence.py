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


def _rendered_nodes(root=_ROOT):
    for path in sorted((root / "agents" / "dify").glob("*.dsl.yml")):
        dsl = yaml.safe_load(path.read_text())
        for node in dsl["workflow"]["graph"]["nodes"]:
            code = node.get("data", {}).get("code", "")
            if isinstance(code, str) and _CALL.search(code):
                yield path.name, node["data"]["title"], code


_NODES = list(_rendered_nodes())

# Every node of this repo's own roster that parses model output must route through the helper.
_PUBLIC_NODES = {
    ("alert-triage.dsl.yml", "Bound and redact trigger input"),
    ("dep-review.dsl.yml", "Bound and redact trigger input"),
    ("docs-drift.dsl.yml", "Bound and redact trigger input"),
    ("pr-keeper.dsl.yml", "Bound and redact trigger input"),
    ("release-promoter.dsl.yml", "Bound and redact trigger input"),
    ("repo-janitor.dsl.yml", "Bound and redact trigger input"),
    ("action-extractor.dsl.yml", "Validate reply"),
    ("commit-grouper.dsl.yml", "Validate reply"),
    ("code-simplifier.dsl.yml", "Validate and force comment review"),
    ("doc-contradiction-finder.dsl.yml", "Validate contradiction findings"),
    ("docs-updater.dsl.yml", "Validate safe page proposals"),
    ("plain-rewriter.dsl.yml", "Validate reply"),
    ("style-gate.dsl.yml", "Validate reply"),
    ("tag-suggester.dsl.yml", "Validate reply"),
    ("vikunja-clerk.dsl.yml", "Code guard"),
    ("vikunja-clerk.dsl.yml", "Update project guard"),
    ("vikunja-triage.dsl.yml", "Guard proposed actions"),
    ("zammad-triage.dsl.yml", "Guard and dispatch"),
}


def _roster_names(root=_ROOT):
    # A DSL belongs to this checkout's roster when its agent definition extends a profile that ships here;
    # overlay rosters extend profiles that this checkout does not carry.
    profiles = {path.stem for path in (root / "agents" / "profiles").glob("*.yaml")}
    names = set()
    for path in (root / "agents").glob("*.yaml"):
        extends = (yaml.safe_load(path.read_text()) or {}).get("extends")
        chain = extends if isinstance(extends, list) else [extends]
        if chain and chain[0] in profiles:
            names.add(path.stem)
    return names


def _unlisted_roster_pairs(pairs, roster_names):
    return sorted(
        (file, title)
        for file, title in pairs - _PUBLIC_NODES
        if file.removesuffix(".dsl.yml") in roster_names
    )


def test_every_model_output_parse_node_routes_through_the_helper():
    names = {(file, title) for file, title, _ in _NODES}
    assert _PUBLIC_NODES <= names
    assert _unlisted_roster_pairs(names, _roster_names()) == []


@pytest.mark.parametrize(
    ("file", "title", "code"), _NODES, ids=[f"{f}:{t}" for f, t, _ in _NODES]
)
def test_rendered_node_defines_helper_and_accepts_a_fenced_reply(file, title, code):
    namespace = {}
    exec(
        compile(code, f"{file}:{title}", "exec"), namespace
    )  # defines the node's functions only
    assert namespace["strip_json_fence"](f"```json\n{_OBJECT}\n```") == _OBJECT


def _write(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def _dsl_yaml(title, code):
    return yaml.safe_dump(
        {
            "app": {"mode": "workflow", "name": "overlay-helper"},
            "kind": "app",
            "version": "0.7.0",
            "workflow": {
                "graph": {
                    "nodes": [
                        {"data": {"code": code, "title": title}, "id": "validate", "type": "custom"}
                    ]
                }
            },
        }
    )


_COMPLIANT_CODE = '''\
import json


def strip_json_fence(text):
    value = str(text)
    stripped = value.strip(" \\t\\r\\n")
    if len(stripped) >= 6 and stripped.startswith("```") and stripped.endswith("```"):
        return stripped[3:-3].strip(" \\t\\r\\n")
    return value


def main(reply):
    return json.loads(strip_json_fence(reply))
'''


def _synthetic_pairs(tmp_path):
    return {(file, title) for file, title, _ in _rendered_nodes(tmp_path)}


def test_compliant_overlay_parse_node_outside_the_roster_passes(tmp_path):
    _write(tmp_path, "agents/dify/overlay-helper.dsl.yml", _dsl_yaml("Validate reply", _COMPLIANT_CODE))
    # The overlay's agent definition extends a profile this checkout does not carry.
    _write(
        tmp_path,
        "agents/overlay-helper.yaml",
        yaml.safe_dump({"name": "overlay-helper", "extends": "overlay-profile"}),
    )
    pairs = _synthetic_pairs(tmp_path)
    assert ("overlay-helper.dsl.yml", "Validate reply") in pairs
    assert _unlisted_roster_pairs(pairs, _roster_names(tmp_path)) == []


def test_unlisted_roster_parse_node_still_fails(tmp_path):
    _write(tmp_path, "agents/dify/overlay-helper.dsl.yml", _dsl_yaml("Validate reply", _COMPLIANT_CODE))
    _write(
        tmp_path,
        "agents/overlay-helper.yaml",
        yaml.safe_dump({"name": "overlay-helper", "extends": "interactive"}),
    )
    _write(
        tmp_path,
        "agents/profiles/interactive.yaml",
        (_ROOT / "agents" / "profiles" / "interactive.yaml").read_text(),
    )
    pairs = _synthetic_pairs(tmp_path)
    assert _unlisted_roster_pairs(pairs, _roster_names(tmp_path)) == [
        ("overlay-helper.dsl.yml", "Validate reply")
    ]


def test_public_dsl_that_drops_the_helper_call_still_fails(tmp_path):
    rendered = (_ROOT / "agents" / "dify" / "plain-rewriter.dsl.yml").read_text()
    assert _CALL.search(rendered)
    _write(
        tmp_path,
        "agents/dify/plain-rewriter.dsl.yml",
        rendered.replace("json.loads(strip_json_fence(raw))", "json.loads(raw)"),
    )
    pairs = _synthetic_pairs(tmp_path)
    assert not _PUBLIC_NODES <= pairs
    assert ("plain-rewriter.dsl.yml", "Validate reply") in _PUBLIC_NODES - pairs
