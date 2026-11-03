"""Runs the Code nodes of the code-simplifier workflow against fixtures.

Each node runs from its copy in agents/dify/code-simplifier.dsl.yml. The two token parse nodes are covered by
test_token_nodes.py. No node here receives a token value, so the token-placement rule applies only there.
Refused cases must return the node's refusal. validate_review falls back to a generic body, with status refused when
the model refused or the body held a secret, and handback when the reply could not be read. guard_review_write decides
whether the review is written.
"""

import json
from pathlib import Path

import pytest
import yaml


_DSL = Path(__file__).resolve().parents[2] / "agents" / "dify" / "code-simplifier.dsl.yml"
_NODES = {node["id"]: node["data"] for node in yaml.safe_load(_DSL.read_text())["workflow"]["graph"]["nodes"]}

_REPO = "dryvist/ai-llm-prompts"
_REF = "feature/simplify"
_SHA = "a" * 40
_OTHER_SHA = "e" * 40
_PR_NUMBER = 7
_GENERIC = "No concrete behavior-preserving simplification was established."
_HANDBACK = "OpenBao, token, or pull request eligibility checks did not authorize this mandate."
# Built from parts so no credential-shaped literal is written to the file. The node's secret scan must match it.
_SECRET = "AKIA" + "ABCDEFGH" + "IJKLMNOP"
# The hunk starts at line 1. The context line is line 1 and the added line is line 2.
_PATCH = "@@ -1 +1,2 @@\n old\n+new line\n"
_FILES = [{"filename": "docs/a.md", "status": "modified", "changes": 2, "patch": _PATCH}]
_CHANGED = [{"path": "docs/a.md", "lines": [2]}]
_SUGGESTION = {"path": "docs/a.md", "line": 2, "body": "Tighten this.\n```suggestion\nnew line\n```"}
_REVIEW_JSON = json.dumps({"event": "COMMENT", "commit_id": _SHA, "body": _GENERIC, "comments": []})


def _main(node_id):
    namespace = {}
    exec(compile(_NODES[node_id]["code"], f"code-simplifier:{node_id}", "exec"), namespace)  # defines functions only
    return namespace["main"]


def _pr(**overrides):
    pr = {
        "number": _PR_NUMBER,
        "state": "open",
        "draft": True,
        "body": "",
        "head": {"ref": _REF, "sha": _SHA, "repo": {"full_name": _REPO}},
        "base": {"ref": "main", "repo": {"full_name": _REPO}},
    }
    pr.update(overrides)
    return json.dumps(pr)


def _pull_request(pr_body=None, rules_body="[]", ref=_REF, head_sha=_SHA, pr_number=_PR_NUMBER):
    return _main("guard_pull_request")(ref, head_sha, _REPO, pr_number, pr_body or _pr(), rules_body)


def _review_context(**overrides):
    args = {"files_body": json.dumps(_FILES), "rules_body": "[]", "pr_body": _pr(), "requested_action": "simplify"}
    args.update(overrides)
    return _main("prepare_review")(args["files_body"], "pull_request", "explicit", _REPO, _PR_NUMBER, _REF, _SHA,
                                   "ci-bot", args["pr_body"], args["rules_body"], args["requested_action"])


def _model(comments=(), body="Looks good.", decision="comment"):
    return json.dumps({"decision": decision, "review_body": body, "comments": list(comments)})


def _review(model_text, changed=_CHANGED, mode="shadow"):
    return _main("validate_review")(model_text, json.dumps(changed), _REPO, _PR_NUMBER, _REF, _SHA, "ci-bot",
                                    "pull_request", "explicit", mode)


def _mandate(repo=_REPO, ref=_REF, head_sha=_SHA, actor="ci-bot", mode="shadow", pr_number=_PR_NUMBER,
             event="pull_request"):
    return _main("validate_mandate")(repo, ref, head_sha, actor, event, "explicit", mode, pr_number)


def _token(repo=_REPO, mode="shadow", read_set="contents-read", write_set="contents-write"):
    return _main("token_request")(repo, mode, read_set, write_set)


def _review_write(pr_body=None, rules_body="[]", review_json=_REVIEW_JSON, head_sha=_SHA, pr_number=_PR_NUMBER,
                  ref=_REF):
    return _main("guard_review_write")(_REPO, pr_number, ref, head_sha, pr_body or _pr(), rules_body, review_json)


def _refused(reason):
    return {"valid": 0, "status": "handback", "reason": reason}


# guard_pull_request: the PR must be open, unruled, on the mandated head, and not a protected branch.

@pytest.mark.parametrize(
    "kwargs, eligible",
    [
        ({}, 1),
        ({"rules_body": json.dumps({"rules": []})}, 1),
        ({"pr_body": "not json"}, 0),
        ({"pr_body": json.dumps({"message": "Not Found"})}, 0),
        ({"rules_body": json.dumps([{"id": 1}])}, 0),
        ({"pr_body": _pr(state="closed")}, 0),
        ({"pr_number": 8}, 0),
        ({"head_sha": _OTHER_SHA}, 0),
        # Only the protected-branch clause may fire: the mandate and the PR head both name main.
        ({"ref": "main", "pr_body": _pr(head={"ref": "main", "sha": _SHA, "repo": {"full_name": _REPO}})}, 0),
        ({"pr_body": _pr(base={"ref": "main", "repo": {"full_name": "other/ai-llm-prompts"}})}, 0),
        ({"pr_body": _pr(head={"ref": _REF, "sha": _SHA, "repo": {"full_name": "other/fork"}})}, 0),
        ({"ref": "other-branch"}, 0),
        ({"ref": "develop", "pr_body": _pr(head={"ref": "develop", "sha": _SHA, "repo": {"full_name": _REPO}})}, 0),
    ],
    ids=["success", "rules object", "malformed", "error payload", "rules present", "closed PR",
         "PR number mismatch", "head sha mismatch", "protected head branch", "base repo mismatch", "fork head",
         "mandate ref mismatch", "protected develop branch"],
)
def test_guard_pull_request(kwargs, eligible):
    assert _pull_request(**kwargs) == {"eligible": eligible}


# prepare_review: the bounded review context. Every refusal returns no context.

def test_prepare_review_builds_context_from_the_changed_lines():
    out = _review_context()
    assert out["safe"] == 1 and out["status"] == "proposed"
    assert json.loads(out["changed_files_json"]) == _CHANGED
    context = json.loads(out["review_context"])
    assert context["repository"] == _REPO and context["pull_number"] == _PR_NUMBER
    assert context["files"] == [{"path": "docs/a.md", "status": "modified", "patch": _PATCH}]


@pytest.mark.parametrize(
    "overrides",
    [
        {"files_body": "not json"},
        {"files_body": json.dumps({"filename": "docs/a.md"})},
        {"files_body": json.dumps(["docs/a.md"])},
        {"files_body": json.dumps([dict(_FILES[0], filename=None)])},
        {"files_body": json.dumps([dict(_FILES[0], changes=6001)])},
        {"files_body": json.dumps([_FILES[0]] * 41)},
        {"files_body": json.dumps([dict(_FILES[0], patch=f"+key {_SECRET}\n")])},
        {"rules_body": json.dumps([{"id": 1}])},
        {"requested_action": f"key {_SECRET}"},
    ],
    ids=["malformed", "not a list", "non-object file", "no file path", "over the change limit", "too many files",
         "secret in patch", "rules present", "secret in request"],
)
def test_prepare_review_refuses(overrides):
    out = _review_context(**overrides)
    assert out["safe"] == 0 and out["status"] == "handback" and out["review_context"] == ""
    assert _SECRET not in json.dumps(out)


# validate_review: the model's review. A comment is kept only on lines it changed; otherwise the body stands alone.

def test_validate_review_keeps_a_suggestion_on_a_changed_line():
    out = _review(_model([_SUGGESTION]))
    assert out["status"] == "proposed" and out["event"] == "COMMENT"
    assert json.loads(out["request_json"]) == {
        "commit_id": _SHA,
        "event": "COMMENT",
        "body": "Looks good.",
        "comments": [{"path": "docs/a.md", "start_line": 2, "line": 2, "side": "RIGHT", "body": _SUGGESTION["body"]}],
    }


@pytest.mark.parametrize(
    "model_text, status",
    [
        (_model([_SUGGESTION], decision="refuse"), "refused"),
        ("not json", "handback"),
        (json.dumps({"error": "rate limited"}), "handback"),
        (_model([], body=f"key {_SECRET}"), "refused"),
    ],
    ids=["refused decision", "malformed", "error payload", "secret in body"],
)
def test_validate_review_falls_back_to_the_generic_review(model_text, status):
    out = _review(model_text)
    request = json.loads(out["request_json"])
    assert request["body"] == _GENERIC and request["comments"] == []
    assert out["status"] == status
    assert _SECRET not in out["request_json"]


@pytest.mark.parametrize(
    "comment",
    [
        dict(_SUGGESTION, line=3),
        dict(_SUGGESTION, start_line=1),
        dict(_SUGGESTION, body="Two.\n```suggestion\na\n```\n```suggestion\nb\n```"),
        dict(_SUGGESTION, body="Plain text, no suggestion."),
        dict(_SUGGESTION, body=f"Key {_SECRET}\n```suggestion\nx\n```"),
    ],
    ids=["unchanged line", "unchanged start line", "two suggestion blocks", "no suggestion block", "secret in comment"],
)
def test_validate_review_drops_a_comment_it_cannot_place(comment):
    request = json.loads(_review(_model([comment]))["request_json"])
    assert request["comments"] == [] and request["body"] == "Looks good."


def test_validate_review_drops_every_comment_above_the_limit():
    request = json.loads(_review(_model([_SUGGESTION] * 6))["request_json"])
    assert request["comments"] == [] and request["body"] == "Looks good."


def test_validate_review_drops_a_range_with_an_unchanged_line_inside():
    changed = [{"path": "docs/a.md", "lines": [2, 4]}]
    request = json.loads(_review(_model([dict(_SUGGESTION, start_line=2, line=4)]), changed=changed)["request_json"])
    assert request["comments"] == [] and request["body"] == "Looks good."


def test_validate_review_keeps_the_same_range_when_every_line_changed():
    changed = [{"path": "docs/a.md", "lines": [2, 3, 4]}]
    request = json.loads(_review(_model([dict(_SUGGESTION, start_line=2, line=4)]), changed=changed)["request_json"])
    assert [(comment["start_line"], comment["line"]) for comment in request["comments"]] == [(2, 4)]


def test_validate_review_reads_a_fenced_reply():
    out = _review("```json\n" + _model([_SUGGESTION]) + "\n```")
    assert len(json.loads(out["request_json"])["comments"]) == 1


# validate_mandate: the mandate fields and their formats. Only the pull_request event is accepted.

@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, {"valid": 1, "status": "ready", "reason": ""}),
        ({"actor": ""}, _refused("required mandate fields are missing")),
        ({"repo": "other/ai-llm-prompts"},
         _refused("repository owner must be dryvist and repository name must be valid")),
        ({"ref": "feature branch"}, _refused("mandated ref is invalid")),
        ({"ref": "feature/../x"}, _refused("mandated ref is invalid")),
        ({"ref": "refs/heads/feature/simplify"}, _refused("mandated ref is invalid")),
        ({"head_sha": "XYZ"}, _refused("mandated head_sha is invalid")),
        ({"mode": "preview"}, _refused("mode must be shadow or live")),
        ({"pr_number": 0}, _refused("pr_number must be a positive integer")),
        ({"pr_number": True}, _refused("pr_number must be a positive integer")),
        ({"event": "check_run"}, _refused("event must be pull_request")),
    ],
    ids=["success", "missing field", "error owner", "bad ref", "ref with dot-dot", "refs prefix", "bad sha",
         "mode mismatch", "bad pr number", "bool pr number", "check_run event"],
)
def test_validate_mandate(kwargs, expected):
    assert _mandate(**kwargs) == expected


# token_request (Select token permission set): the read set in shadow, the write set in live, nothing else.

@pytest.mark.parametrize(
    "kwargs, ready, token_set",
    [
        ({"mode": "shadow"}, 1, "contents-read"),
        ({"mode": "live"}, 1, "contents-write"),
        ({"repo": ""}, 0, None),
        ({"mode": "preview"}, 0, None),
        ({"mode": "shadow", "read_set": ""}, 0, None),
        ({"mode": "live", "write_set": None}, 0, None),
    ],
    ids=["shadow reads", "live writes", "missing repository", "mode mismatch", "empty read set", "unset write set"],
)
def test_select_token_permission_set(kwargs, ready, token_set):
    out = _token(**kwargs)
    assert set(out) == {"ready", "request_json"} and out["ready"] == ready
    if token_set is None:
        assert out == {"ready": 0, "request_json": "{}"}
    else:
        assert json.loads(out["request_json"]) == {"repositories": [_REPO], "token_set": token_set}


# guard_review_write: the review is written only to the mandated open PR, on its head, as a comment.

_REVIEW_REFUSAL = "review write target no longer matches the mandate"
_REVIEW_UNREADABLE = "write target could not be revalidated against the mandate"


def test_guard_review_write_allows_a_matching_target():
    assert _review_write() == {"allowed": 1, "status": "ready", "reason": ""}


@pytest.mark.parametrize(
    "kwargs, reason",
    [
        ({"pr_body": "not json"}, _REVIEW_UNREADABLE),
        ({"review_json": "not json"}, _REVIEW_UNREADABLE),
        ({"pr_body": json.dumps({"message": "Not Found"})}, _REVIEW_REFUSAL),
        ({"rules_body": json.dumps([{"id": 1}])}, _REVIEW_REFUSAL),
        ({"pr_number": 8}, _REVIEW_REFUSAL),
        # Only the PR head clause may fire: the review commit follows the mandate, so the PR head is the mismatch.
        ({"head_sha": _OTHER_SHA, "review_json": json.dumps({"event": "COMMENT", "commit_id": _OTHER_SHA})},
         _REVIEW_REFUSAL),
        ({"pr_body": _pr(state="closed")}, _REVIEW_REFUSAL),
        ({"pr_body": _pr(head={"ref": _REF, "sha": _SHA, "repo": {"full_name": "other/fork"}})}, _REVIEW_REFUSAL),
        ({"review_json": json.dumps({"event": "APPROVE", "commit_id": _SHA})}, _REVIEW_REFUSAL),
        ({"review_json": json.dumps({"event": "COMMENT", "commit_id": _OTHER_SHA})}, _REVIEW_REFUSAL),
        ({"ref": "other-branch"}, _REVIEW_REFUSAL),
        ({"pr_body": _pr(base={"ref": "main", "repo": {"full_name": "other/ai-llm-prompts"}})}, _REVIEW_REFUSAL),
    ],
    ids=["malformed PR", "malformed review", "error payload", "rules present", "PR number mismatch",
         "head sha mismatch", "closed PR", "fork head", "approve event", "review commit mismatch", "ref mismatch",
         "base repo mismatch"],
)
def test_guard_review_write_refuses(kwargs, reason):
    assert _review_write(**kwargs) == {"allowed": 0, "status": "handback", "reason": reason}


# prepare_handback: no inputs change the handback.

@pytest.mark.parametrize("args", [(_REPO, "shadow"), ("", "live")], ids=["shadow", "live with no repository"])
def test_prepare_handback_always_hands_back(args):
    assert _main("prepare_handback")(*args) == {"status": "handback", "reason": _HANDBACK}


# Routing: only a proposed review reaches the target guard and the post. Refused and handback reviews end unposted.

def _edges():
    dsl = yaml.safe_load(_DSL.read_text())
    return {(edge["source"], edge["sourceHandle"], edge["target"]) for edge in dsl["workflow"]["graph"]["edges"]}


def test_only_a_proposed_review_reaches_the_guard_and_the_post():
    edges = _edges()
    assert {edge for edge in edges if edge[2] == "guard_review_write"} == {
        ("review_status_gate", "eligible", "guard_review_write"),
    }
    assert {edge for edge in edges if edge[2] == "review_status_gate"} == {
        ("validate_review", "source", "review_status_gate"),
    }
    assert {edge for edge in edges if edge[0] == "review_status_gate"} == {
        ("review_status_gate", "eligible", "guard_review_write"),
        ("review_status_gate", "false", "review_refusal_gate"),
    }
    assert {edge for edge in edges if edge[0] == "review_refusal_gate"} == {
        ("review_refusal_gate", "eligible", "end_review_refused"),
        ("review_refusal_gate", "false", "prepare_handback"),
    }
    assert {edge for edge in edges if edge[2] == "post_review"} == {("review_mode_gate", "eligible", "post_review")}
