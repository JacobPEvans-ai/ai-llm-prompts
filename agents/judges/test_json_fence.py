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


def _yaml_mapping(root, *parts):
    path = root.joinpath(*parts)
    try:
        document = yaml.safe_load(path.read_text())
    except OSError as error:
        pytest.fail(f"{path.relative_to(root)} cannot be read: {error}")
    except yaml.YAMLError as error:
        pytest.fail(f"{path.relative_to(root)} does not parse as YAML: {error}")
    if not isinstance(document, dict):
        pytest.fail(f"{path.relative_to(root)} does not parse to a YAML mapping")
    return document


def _rendered_nodes(root=_ROOT):
    for path in sorted((root / "agents" / "dify").glob("*.dsl.yml")):
        dsl = _yaml_mapping(root, "agents", "dify", path.name)
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


_PROFILE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _base_prefix(root):
    """The one shared prefix this repo's profiles declare, in agents/profiles/defaults.yaml."""
    prefix = _yaml_mapping(root, "agents", "profiles", "defaults.yaml").get("shared_prefix")
    if not isinstance(prefix, str) or not prefix:
        pytest.fail("agents/profiles/defaults.yaml declares no shared_prefix")
    return prefix


def _resolved_prefix(root, stem, definition):
    """The shared prefix agents/dify-src/agent.tmpl merges for this definition: it wins over its extends profile,
    which wins over defaults; without extends the definition resolves on its own."""
    layers = [definition]
    extends = definition.get("extends")
    if extends is not None:
        if not isinstance(extends, str) or not _PROFILE_NAME.fullmatch(extends) or extends == "defaults":
            pytest.fail(f"agents/{stem}.yaml has an invalid extends profile name: {extends!r}")
        layers.append(_yaml_mapping(root, "agents", "profiles", f"{extends}.yaml"))
        layers.append(_yaml_mapping(root, "agents", "profiles", "defaults.yaml"))
    for layer in layers:
        prefix = layer.get("shared_prefix")
        if prefix is not None:
            if not isinstance(prefix, str) or not prefix:
                pytest.fail(f"agents/{stem}.yaml resolves a shared_prefix that is not a path string")
            return prefix
    pytest.fail(f"agents/{stem}.yaml resolves no shared_prefix through its extends chain")


def _roster(root):
    """Map each agent definition stem to the shared prefix its extends chain resolves to."""
    return {
        path.stem: _resolved_prefix(root, path.stem, _yaml_mapping(root, "agents", path.name))
        for path in sorted((root / "agents").glob("*.yaml"))
    }


def _public_stems(root, roster):
    base = _base_prefix(root)
    return {stem for stem, prefix in roster.items() if prefix == base}


def _orphan_files(pairs, roster):
    return sorted({file for file, _ in pairs if file.removesuffix(".dsl.yml") not in roster})


def _unlisted_roster_pairs(pairs, public_stems):
    """Roster parse nodes missing from the hard-coded list; overlay DSLs may add nodes outside the list."""
    return sorted(
        (file, title)
        for file, title in pairs - _PUBLIC_NODES
        if file.removesuffix(".dsl.yml") in public_stems
    )


def test_every_model_output_parse_node_routes_through_the_helper():
    names = {(file, title) for file, title, _ in _NODES}
    roster = _roster(_ROOT)
    assert _orphan_files(names, roster) == []
    assert _PUBLIC_NODES <= names
    assert _unlisted_roster_pairs(names, _public_stems(_ROOT, roster)) == []


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


def _dsl_yaml(name, title, code):
    return yaml.safe_dump(
        {
            "app": {"mode": "workflow", "name": name},
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


def _checkout_defaults(tmp_path):
    _write(
        tmp_path,
        "agents/profiles/defaults.yaml",
        (_ROOT / "agents" / "profiles" / "defaults.yaml").read_text(),
    )


def test_overlay_agent_declaring_its_own_prefix_passes(tmp_path):
    # The overlay extends this repo's base interactive profile but its own profile overrides the shared prefix,
    # so its DSL is an overlay DSL and its compliant parse node may sit outside the hard-coded list.
    profile = yaml.safe_load((_ROOT / "agents" / "profiles" / "interactive.yaml").read_text())
    profile["shared_prefix"] = "agents/prompts/shared/overlay.md"
    _checkout_defaults(tmp_path)
    _write(tmp_path, "agents/profiles/interactive.yaml", yaml.safe_dump(profile))
    _write(
        tmp_path, "agents/overlay.yaml", yaml.safe_dump({"name": "overlay", "extends": "interactive"})
    )
    _write(tmp_path, "agents/dify/overlay.dsl.yml", _dsl_yaml("overlay", "Validate reply", _COMPLIANT_CODE))
    pairs = _synthetic_pairs(tmp_path)
    roster = _roster(tmp_path)
    assert ("overlay.dsl.yml", "Validate reply") in pairs
    assert "overlay" not in _public_stems(tmp_path, roster)
    assert _unlisted_roster_pairs(pairs, _public_stems(tmp_path, roster)) == []


def test_new_public_dsl_with_an_unlisted_parse_node_fails(tmp_path):
    _checkout_defaults(tmp_path)
    _write(
        tmp_path,
        "agents/profiles/interactive.yaml",
        (_ROOT / "agents" / "profiles" / "interactive.yaml").read_text(),
    )
    _write(
        tmp_path,
        "agents/sample-clerk.yaml",
        yaml.safe_dump({"name": "sample-clerk", "extends": "interactive"}),
    )
    _write(
        tmp_path,
        "agents/dify/sample-clerk.dsl.yml",
        _dsl_yaml("sample-clerk", "Validate reply", _COMPLIANT_CODE),
    )
    pairs = _synthetic_pairs(tmp_path)
    assert _unlisted_roster_pairs(pairs, _public_stems(tmp_path, _roster(tmp_path))) == [
        ("sample-clerk.dsl.yml", "Validate reply")
    ]


def test_orphan_dsl_without_a_definition_fails(tmp_path):
    _checkout_defaults(tmp_path)
    _write(
        tmp_path,
        "agents/dify/sample-clerk.dsl.yml",
        _dsl_yaml("sample-clerk", "Validate reply", _COMPLIANT_CODE),
    )
    assert _orphan_files(_synthetic_pairs(tmp_path), _roster(tmp_path)) == ["sample-clerk.dsl.yml"]


def test_definition_whose_chain_declares_no_prefix_fails(tmp_path):
    defaults = yaml.safe_load((_ROOT / "agents" / "profiles" / "defaults.yaml").read_text())
    del defaults["shared_prefix"]
    _write(tmp_path, "agents/profiles/defaults.yaml", yaml.safe_dump(defaults))
    _write(
        tmp_path,
        "agents/profiles/interactive.yaml",
        (_ROOT / "agents" / "profiles" / "interactive.yaml").read_text(),
    )
    _write(
        tmp_path,
        "agents/sample-clerk.yaml",
        yaml.safe_dump({"name": "sample-clerk", "extends": "interactive"}),
    )
    with pytest.raises(pytest.fail.Exception, match="resolves no shared_prefix"):
        _roster(tmp_path)


def test_definition_yaml_that_is_not_a_mapping_fails_with_a_clear_message(tmp_path):
    _checkout_defaults(tmp_path)
    _write(tmp_path, "agents/sample-clerk.yaml", "- just\n- a\n- list\n")
    with pytest.raises(pytest.fail.Exception, match="does not parse to a YAML mapping"):
        _roster(tmp_path)


def _public_checkout(tmp_path):
    for file in sorted({file for file, _ in _PUBLIC_NODES}):
        _write(tmp_path, f"agents/dify/{file}", (_ROOT / "agents" / "dify" / file).read_text())


def test_public_dsl_that_drops_the_helper_call_breaks_the_public_guarantee(tmp_path):
    _public_checkout(tmp_path)
    rendered = (_ROOT / "agents" / "dify" / "plain-rewriter.dsl.yml").read_text()
    assert _CALL.search(rendered)
    _write(
        tmp_path,
        "agents/dify/plain-rewriter.dsl.yml",
        rendered.replace("json.loads(strip_json_fence(raw))", "json.loads(raw)"),
    )
    assert _PUBLIC_NODES - _synthetic_pairs(tmp_path) == {
        ("plain-rewriter.dsl.yml", "Validate reply")
    }
