"""Runs the Code nodes of the ci-fixer workflow against fixtures.

Each node runs from its copy in agents/dify/ci-fixer.dsl.yml. Refused cases must return the node's refusal.
The workflow is fail-closed: log redaction is unavailable, so live ref updates and pushes stay refused. The write
guards allow a matching live target, and their tests check that case. The two token parse nodes are covered by
test_token_nodes.py.
A node with no refusal branch is checked on its output shape, and the test says so.
"""

import json
from pathlib import Path

import pytest
import yaml


_DSL = Path(__file__).resolve().parents[2] / "agents" / "dify" / "ci-fixer.dsl.yml"
_NODES = {node["id"]: node["data"] for node in yaml.safe_load(_DSL.read_text())["workflow"]["graph"]["nodes"]}

_REPO = "dryvist/ai-llm-prompts"
_REF = "feature/fix-ci"
_SHA = "a" * 40
_OTHER_SHA = "e" * 40
_TREE = "b" * 40
_COMMIT = "c" * 40
_BLOB = "d" * 40
_PR_NUMBER = 7
_CHECK_RUN = 99
_FILES = [{"filename": "docs/a.md", "additions": 2, "deletions": 1}]
# Built from parts so no credential-shaped literal is written to the file. The node's secret scan must match these.
_SECRET = "AKIA" + "ABCDEFGH" + "IJKLMNOP"
_SECRET_CONTEXT = "token" + ": " + "abcdefghijklmnopqrstuvwxyz0123"
_ZERO = {"sha": "", "ready": 0}


def _main(node_id):
    namespace = {}
    exec(compile(_NODES[node_id]["code"], f"ci-fixer:{node_id}", "exec"), namespace)  # defines the node's functions only
    return namespace["main"]


def _pr(**overrides):
    pr = {
        "number": _PR_NUMBER,
        "state": "open",
        "body": "",
        "head": {"ref": _REF, "sha": _SHA, "repo": {"full_name": _REPO}},
        "base": {"ref": "main", "repo": {"full_name": _REPO}},
    }
    pr.update(overrides)
    return json.dumps(pr)


def _check(**overrides):
    check = {
        "id": _CHECK_RUN,
        "status": "completed",
        "conclusion": "failure",
        "head_sha": _SHA,
        "head_branch": _REF,
        "pull_requests": [{"number": _PR_NUMBER}],
    }
    check.update(overrides)
    return json.dumps(check)


def _head_commit():
    return json.dumps({"sha": _COMMIT, "tree": {"sha": _TREE}})


# parse_blob: the blob sha or nothing.

@pytest.mark.parametrize(
    "body, expected",
    [
        (json.dumps({"sha": _BLOB}), {"sha": _BLOB, "ready": 1}),
        (json.dumps({"url": "https://example.test/blob"}), _ZERO),
        (json.dumps({"message": "Not Found"}), _ZERO),
        ("not json", _ZERO),
    ],
    ids=["success", "missing field", "error payload", "malformed"],
)
def test_parse_blob(body, expected):
    assert _main("parse_blob")(body) == expected


# build_tree_request: no refusal branch. It builds the tree from its inputs; guard_tree_write refuses downstream.

def test_build_tree_request_builds_one_blob_entry():
    out = _main("build_tree_request")(_TREE, "docs/a.md", _BLOB)
    assert json.loads(out["tree_json"]) == {
        "base_tree": _TREE,
        "tree": [{"path": "docs/a.md", "mode": "100644", "type": "blob", "sha": _BLOB}],
    }


# validate_mandate: the mandate fields and their formats.

_MANDATE = (_REPO, _REF, _SHA, "ci-bot", "check_run", "explicit", "shadow", _CHECK_RUN)


def _refused(reason):
    return {"valid": 0, "encoded_ref": "", "status": "handback", "reason": reason}


@pytest.mark.parametrize(
    "args, expected",
    [
        (_MANDATE, {"valid": 1, "encoded_ref": _REF, "status": "ready", "reason": ""}),
        ((_REPO, _REF, _SHA, "", "check_run", "explicit", "shadow", _CHECK_RUN),
         _refused("required mandate fields are missing")),
        (("other/ai-llm-prompts", _REF, _SHA, "ci-bot", "check_run", "explicit", "shadow", _CHECK_RUN),
         _refused("repository owner must be dryvist and repository name must be valid")),
        ((_REPO, "refs/heads/main", _SHA, "ci-bot", "check_run", "explicit", "shadow", _CHECK_RUN),
         _refused("mandated ref is invalid")),
        ((_REPO, _REF, "XYZ", "ci-bot", "check_run", "explicit", "shadow", _CHECK_RUN),
         _refused("mandated head_sha is invalid")),
        ((_REPO, _REF, _SHA, "ci-bot", "push", "explicit", "shadow", _CHECK_RUN),
         _refused("event must be check_run")),
        ((_REPO, _REF, _SHA, "ci-bot", "check_run", "explicit", "preview", _CHECK_RUN),
         _refused("mode must be shadow or live")),
        ((_REPO, _REF, _SHA, "ci-bot", "check_run", "explicit", "shadow", 0),
         _refused("check_run_id must be a positive integer")),
    ],
    ids=[
        "success", "missing field", "error owner", "bad ref", "bad sha", "wrong event",
        "token-set mode mismatch", "bad check run id",
    ],
)
def test_validate_mandate(args, expected):
    assert _main("validate_mandate")(*args) == expected


# token_request (Select token permission set): the read set in shadow, the write set in live, nothing else.
# The node checks the owner as defense in depth; validate_mandate also enforces dryvist before it runs.

_TOKEN_ZERO = {"ready": 0, "request_json": "{}"}


@pytest.mark.parametrize(
    "args, ready, token_set",
    [
        ((_REPO, "shadow", "contents-read", "contents-write"), 1, "contents-read"),
        ((_REPO, "live", "contents-read", "contents-write"), 1, "contents-write"),
        (("", "shadow", "contents-read", "contents-write"), 0, None),
        ((_REPO, "preview", "contents-read", "contents-write"), 0, None),
        ((_REPO, "live", "contents-read", ""), 0, None),
        ((_REPO, "live", "contents-read", None), 0, None),
        (("other/ai-llm-prompts", "shadow", "contents-read", "contents-write"), 0, None),
        ((None, "shadow", "contents-read", "contents-write"), 0, None),
    ],
    ids=["shadow reads", "live writes", "missing repository", "mode mismatch", "empty write set", "unset write set",
         "non-dryvist owner", "non-string repository"],
)
def test_select_token_permission_set(args, ready, token_set):
    out = _main("token_request")(*args)
    assert set(out) == {"ready", "request_json"}
    assert out["ready"] == ready
    if token_set is None:
        assert out == _TOKEN_ZERO
    else:
        assert json.loads(out["request_json"]) == {"repositories": [_REPO], "token_set": token_set}


# extract_check_target: a failed check run with exactly one linked PR, on the mandated head.

_CHECK_HANDBACK = "check run does not match the mandate or has no single linked PR"


def _check_without_prs():
    check = json.loads(_check())
    del check["pull_requests"]
    return json.dumps(check)


@pytest.mark.parametrize(
    "body, eligible, pr_number, reason",
    [
        (_check(), 1, _PR_NUMBER, ""),
        (_check_without_prs(), 0, 0, _CHECK_HANDBACK),
        (json.dumps({"message": "Not Found"}), 0, 0, _CHECK_HANDBACK),
        ("not json", 0, 0, "check run response is invalid"),
        (_check(head_sha=_OTHER_SHA), 0, 0, _CHECK_HANDBACK),
        (_check(conclusion="success"), 0, 0, _CHECK_HANDBACK),
        (_check(pull_requests=[{"number": _PR_NUMBER}, {"number": 8}]), 0, 0, _CHECK_HANDBACK),
    ],
    ids=["success", "missing field", "error payload", "malformed", "head mismatch", "conclusion mismatch",
         "two linked PRs"],
)
def test_extract_check_target(body, eligible, pr_number, reason):
    out = _main("extract_check_target")(body, _REPO, _CHECK_RUN, _REF, _SHA)
    assert out["eligible"] == eligible
    assert out["pr_number"] == pr_number
    assert out["status"] == ("ready" if eligible else "handback")
    assert out["reason"] == reason


# prepare_handback: no inputs change the handback.

@pytest.mark.parametrize("args", [(_REPO, "shadow"), ("", "live")], ids=["shadow", "live with no repository"])
def test_prepare_handback_always_hands_back(args):
    assert _main("prepare_handback")(*args) == {
        "status": "handback",
        "reason": "The check run, PR, or repository guards did not authorize this mandate.",
    }


# prepare_comment: the comment-only reply. It writes nothing and hands back.

def test_prepare_comment_hands_back_with_a_comment_and_trace():
    out = _main("prepare_comment")(_REPO, _PR_NUMBER, _REF, _SHA, "ci-bot", "check_run", "explicit", "shadow")
    assert out["status"] == "handback"
    assert out["body"].startswith("No automated source changes were made.")
    assert json.loads(out["request_json"]) == {"body": out["body"]}
    trace = json.loads(out["trace_json"])
    assert trace["repo"] == _REPO and trace["pr_number"] == _PR_NUMBER and trace["mode"] == "shadow"


def test_prepare_comment_passes_missing_fields_through_to_the_trace():
    out = _main("prepare_comment")("", 0, "", "", "", "", "", "live")
    assert out["status"] == "handback"
    assert json.loads(out["trace_json"])["mode"] == "live"
