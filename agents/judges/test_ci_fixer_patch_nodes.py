"""Runs the write-path Code nodes of the ci-fixer workflow against fixtures.

guard_context, validate_patch, prepare_context, guard_ref_update and the three write guards. The helpers come from
test_ci_fixer_nodes.py. The workflow is fail-closed: log redaction is unavailable, so live ref updates and pushes stay
refused. Tests that need the flag on set it explicitly on the exec'd node. The write guards allow a matching live target.
"""

import json

import pytest

from test_ci_fixer_nodes import (
    _CHECK_RUN, _COMMIT, _FILES, _OTHER_SHA, _PR_NUMBER, _REF, _REPO, _SECRET, _SECRET_CONTEXT, _SHA, _TREE,
    _check, _head_commit, _main, _pr,
)


# guard_context: the eligibility and bounded-context check before model input.

def _context(**overrides):
    args = {
        "payload_repo": _REPO,
        "payload_head_ref": _REF,
        "payload_head_sha": _SHA,
        "payload_check_run_id": _CHECK_RUN,
        "payload_pr_number": _PR_NUMBER,
        "check_run_body": _check(),
        "annotations_body": "[]",
        "current_pr_body": _pr(),
        "rules_body": "[]",
        "files_body": json.dumps(_FILES),
        "head_commit_body": _head_commit(),
        "mode": "shadow",
    }
    args.update(overrides)
    return args


def _guard_context(**overrides):
    return _main("guard_context")(**_context(**overrides))


def test_guard_context_allows_model_input_in_shadow():
    out = _guard_context()
    assert out["eligible"] == 1 and out["comment_allowed"] == 1 and out["model_allowed"] == 1
    assert out["tree_sha"] == _TREE and out["current_head_sha"] == _SHA
    assert out["changed_lines"] == 3 and out["reason"] == ""


def test_guard_context_keeps_model_input_closed_in_live():
    out = _guard_context(mode="live")
    assert out["eligible"] == 1 and out["model_allowed"] == 0
    assert out["reason"] == "bounded context or secret scan did not authorize model input"


@pytest.mark.parametrize(
    "overrides, eligible, reason",
    [
        ({"check_run_body": "not json"}, 0, "GitHub context could not be read"),
        ({"annotations_body": json.dumps({"message": "Forbidden"})}, 0,
         "bounded context or secret scan did not authorize model input"),
        # Only the protected-branch clause may fire: the payload, PR head and check run all name main.
        ({
            "payload_head_ref": "main",
            "current_pr_body": _pr(head={"ref": "main", "sha": _SHA, "repo": {"full_name": _REPO}}),
            "check_run_body": _check(head_branch="main"),
        }, 0, "bounded context or secret scan did not authorize model input"),
        ({"files_body": json.dumps([{"filename": "docs/a.md", "additions": 200, "deletions": 0}])}, 0,
         "bounded context or secret scan did not authorize model input"),
    ],
    ids=["malformed", "error payload", "protected head branch", "over the line limit"],
)
def test_guard_context_refuses_what_it_cannot_bound(overrides, eligible, reason):
    out = _guard_context(**overrides)
    assert out["eligible"] == eligible
    assert out["model_allowed"] == 0
    assert out["reason"] == reason


def test_guard_context_keeps_a_secret_out_of_model_input():
    out = _guard_context(annotations_body=json.dumps([{"message": _SECRET_CONTEXT}]))
    assert out["eligible"] == 1 and out["model_allowed"] == 0
    assert _SECRET_CONTEXT not in json.dumps(out)


# validate_patch: the model's patch and the write guards. Live pushes stay closed unless log redaction is on.

_GOOD_PATCH = {"decision": "commit", "patches": [{"path": "docs/a.md", "content": "hello\n",
                                                 "diff": "@@ -1 +1 @@\n-old\n+new\n"}]}


def _patch(model_text, files=None, mode="shadow", eligible=1, log_available=False, enable_push="true"):
    node = _main("validate_patch")
    node.__globals__["LOG_REDACTION_AVAILABLE"] = log_available
    return node(
        model_text,
        json.dumps(_FILES if files is None else files),
        enable_push,
        eligible,
        _REPO,
        _PR_NUMBER,
        _REF,
        _SHA,
        mode,
        "ci-bot",
        "check_run",
        "explicit",
        _pr(),
        "[]",
    )


def _patch_text(path="docs/a.md", content="hello\n", lines=1):
    diff = "@@ -1 +1 @@\n" + "+x\n" * lines
    return json.dumps({"decision": "commit", "patches": [{"path": path, "content": content, "diff": diff}]})


def test_validate_patch_proposes_in_shadow_and_never_pushes():
    out = _patch(json.dumps(_GOOD_PATCH))
    assert out["status"] == "proposed" and out["reason"] == ""
    assert out["path"] == "docs/a.md" and json.loads(out["content_json"]) == "hello\n"
    assert out["push_allowed"] == 0


def test_validate_patch_allows_a_live_push_when_every_gate_is_open():
    out = _patch(json.dumps(_GOOD_PATCH), mode="live", log_available=True)
    assert out["push_allowed"] == 1
    assert out["status"] == "ready" and out["reason"] == ""


@pytest.mark.parametrize(
    "model_text, files, mode, eligible, status",
    [
        (json.dumps(_GOOD_PATCH), None, "live", 1, "refused"),
        # The model reply cannot be read, so the target guard cannot pass: handback, not refused.
        ("not json", None, "shadow", 1, "handback"),
        (json.dumps({"error": "rate limited"}), None, "shadow", 1, "refused"),
        (_patch_text(path="src/b.md"), None, "shadow", 1, "refused"),
        (_patch_text(path=".github/ci.yml"), [{"filename": ".github/ci.yml", "additions": 1, "deletions": 0}],
         "shadow", 1, "refused"),
        (_patch_text(content=f"key {_SECRET}"), None, "shadow", 1, "refused"),
        (_patch_text(lines=121), None, "shadow", 1, "refused"),
        # A shadow proposal forms only when eligible is 1. An ineligible mandate is handed back, never proposed.
        (json.dumps(_GOOD_PATCH), None, "shadow", 0, "handback"),
    ],
    ids=["live writes stay closed", "malformed", "error payload", "path not changed",
         "denied path", "secret in content", "over the line limit", "guard not eligible"],
)
def test_validate_patch_refuses(model_text, files, mode, eligible, status):
    out = _patch(model_text, files=files, mode=mode, eligible=eligible)
    assert out["status"] == status
    assert out["push_allowed"] == 0


def test_validate_patch_never_returns_a_secret():
    out = _patch(_patch_text(content=f"key {_SECRET}"))
    assert _SECRET not in json.dumps(out)


# prepare_context: builds the review context. It has no refusal branch; the guards run before it.

def test_prepare_context_builds_the_review_context():
    out = _main("prepare_context")(_REPO, _PR_NUMBER, _REF, _SHA, "ci-bot", "check_run", "explicit",
                                   _check(), "[]", json.dumps(_FILES))
    context = json.loads(out["review_context"])
    assert context["repository"] == _REPO and context["pull_request_number"] == _PR_NUMBER
    assert "unavailable" in context["logs"]


def test_prepare_context_passes_an_empty_check_run_through():
    out = _main("prepare_context")(_REPO, _PR_NUMBER, _REF, _SHA, "ci-bot", "check_run", "explicit", "", "[]", "[]")
    assert json.loads(out["review_context"])["check_run"] == ""


# guard_ref_update: the ref update. Log redaction is unavailable, so it is never eligible.

def _ref_update(pr_body=None, head=_SHA, mode="live", enable_push="true", mandate_ref=_REF, log_available=False):
    node = _main("guard_ref_update")
    node.__globals__["LOG_REDACTION_AVAILABLE"] = log_available
    return node(
        pr_body or _pr(), head, mandate_ref, enable_push, json.dumps({"sha": _COMMIT}), _REPO, _PR_NUMBER, "[]", mode,
    )


def test_guard_ref_update_stays_closed_while_log_redaction_is_unavailable():
    assert _ref_update() == {"eligible": 0, "ref_encoded": ""}


def test_guard_ref_update_allows_the_ref_when_every_gate_is_open():
    assert _ref_update(log_available=True) == {"eligible": 1, "ref_encoded": _REF}


@pytest.mark.parametrize(
    "kwargs",
    [
        {"pr_body": "not json"},
        {"head": _OTHER_SHA},
        {"mandate_ref": "other-branch"},
        {"mode": "shadow"},
        {"enable_push": "false"},
    ],
    ids=["malformed", "head mismatch", "ref mismatch", "shadow mode", "push disabled"],
)
def test_guard_ref_update_refuses_each_clause_with_the_flag_on(kwargs):
    assert _ref_update(log_available=True, **kwargs) == {"eligible": 0, "ref_encoded": ""}


# The three write guards share one body. Each runs the same cases on its own copy.

_WRITE_GUARDS = ("guard_tree_write", "guard_commit_write", "guard_comment_write")
_WRITE_REFUSAL = "write target no longer matches the mandate"


def _write_guard(node_id, **overrides):
    args = {
        "repo": _REPO,
        "pr_number": _PR_NUMBER,
        "ref": _REF,
        "head_sha": _SHA,
        "pr_body": _pr(),
        "rules_body": "[]",
        "enable_push": "true",
        "mode": "live",
        "target_body": json.dumps({"sha": _TREE}),
    }
    args.update(overrides)
    return _main(node_id)(**args)


@pytest.mark.parametrize("node_id", _WRITE_GUARDS)
def test_write_guard_allows_a_matching_live_target(node_id):
    assert _write_guard(node_id) == {"allowed": 1, "reason": ""}


@pytest.mark.parametrize("node_id", _WRITE_GUARDS)
@pytest.mark.parametrize(
    "overrides",
    [
        {"mode": "shadow"},
        {"enable_push": "false"},
        {"target_body": ""},
        {"rules_body": json.dumps([{"id": 1}])},
        {"pr_body": _pr(head={"ref": _REF, "sha": _OTHER_SHA, "repo": {"full_name": _REPO}})},
        {"pr_body": _pr(state="closed")},
    ],
    ids=["shadow mode", "push disabled", "missing target", "rules present", "head mismatch", "closed PR"],
)
def test_write_guard_refuses_a_mismatch(node_id, overrides):
    assert _write_guard(node_id, **overrides) == {"allowed": 0, "reason": _WRITE_REFUSAL}


@pytest.mark.parametrize("node_id", _WRITE_GUARDS)
@pytest.mark.parametrize("pr_body", ["not json", json.dumps({"message": "Not Found"})],
                         ids=["malformed", "error payload"])
def test_write_guard_refuses_an_unreadable_pr(node_id, pr_body):
    out = _write_guard(node_id, pr_body=pr_body)
    assert out["allowed"] == 0
