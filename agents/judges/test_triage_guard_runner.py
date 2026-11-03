"""Runs the rendered triage guard's Code node over the vikunja guard fixtures, and checks its done gate.

GitHub and OpenBao are stubbed at urllib, as in test_triage_state_lookup.py. The guard's own
state lookup runs on the rendered DSL. Only fixtures with a `proposed` list reach the guard as model
output, so only those are scored. The other fixtures are skipped by name, and the test asserts the
exact skipped set, so no case drops silently.
"""

import json
import urllib.request
from pathlib import Path

import pytest
import yaml


_ROOT = Path(__file__).resolve().parents[2]
_DSL = _ROOT / "agents" / "dify" / "vikunja-triage.dsl.yml"
_FIXTURES = _ROOT / "agents" / "evals" / "guard" / "vikunja-triage.yaml"
_WEB_HOST = "github.com"
_API_BASE = "https://api.github.com"
_BAO = "https://bao.example"
_BAO_PATH = "secret/data/gh"
_POLICY = {"allowed": ["10"], "readonly": [], "rank_only": [], "denied": []}
_SUBSTITUTIONS = {
    "<GITHUB_WEB_HOST>": _WEB_HOST,
    "<OWNER>": "dryvist",
    "<REPO>": "ai-llm-prompts",
    "<N>": "236",
    "<TASK_ID>": "7",
    "<TASK_TITLE>": "Triage task",
    "<ALLOWED_PROJECT_ID>": "10",
    "<READONLY_PROJECT_ID>": "11",
    "<RANK_ONLY_PROJECT_ID>": "12",
    "<DENIED_PROJECT_ID>": "13",
    "<RANK_LABEL>": "ranked",
    "<OLD_TIMESTAMP>": "2026-01-01T00:00:00Z",
}
_PAYLOADS = {
    "open": {"state": "open", "merged": False},
    "merged": {
        "state": "closed",
        "merged": True,
        "pull_request": {"merged_at": "2026-11-01T00:00:00Z"},
    },
    "closed-unmerged": {
        "state": "closed",
        "merged": False,
        "pull_request": {"merged_at": None},
    },
}
_EXPECTED_SKIPPED = ["denied-project-is-never-read"] + [
    f"redacted-golden-{n:02d}" for n in range(1, 11)
]


def _guard_main():
    dsl = yaml.safe_load(_DSL.read_text())
    node = next(
        n
        for n in dsl["workflow"]["graph"]["nodes"]
        if "def state_for" in (n["data"].get("code") or "")
    )
    namespace = {}
    exec(
        compile(node["data"]["code"], "guard", "exec"), namespace
    )  # defines the node's functions only
    return namespace["main"]


_MAIN = _guard_main()
_CASES = yaml.safe_load(_FIXTURES.read_text())["cases"]
_SELECTED = [case for case in _CASES if "proposed" in case]
_SKIPPED = [case["id"] for case in _CASES if "proposed" not in case]


class _Response:
    def __init__(self, payload):
        self._body = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


def _install_stub(monkeypatch, github):
    """Serve OpenBao and the mapped GitHub objects. Returns every GitHub request made, in order.

    The guard swallows errors from its lookup, so an unexpected request is recorded here for the test to assert on.
    """
    requests = []

    def fake_urlopen(request, timeout=None):
        url = request.full_url
        if url == f"{_BAO}/v1/auth/approle/login":
            return _Response({"auth": {"client_token": "client"}})
        if url == f"{_BAO}/v1/{_BAO_PATH}":
            return _Response({"data": {"token": "gh-token"}})
        requests.append(url)
        if url in github:
            return _Response(github[url])
        raise AssertionError(f"unexpected request: {url}")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    return requests


def _substitute(case):
    text = json.dumps(case)
    for key, value in _SUBSTITUTIONS.items():
        text = text.replace(key, value)
    assert "<" not in text, f"unmapped placeholder in case: {text}"
    return json.loads(text)


def _github_for(linked):
    if not linked:
        return {}
    owner, repo, kind, number = linked["url"].split("/")[3:7]
    endpoint = "pulls" if kind == "pull" else "issues"
    return {
        f"{_API_BASE}/repos/{owner}/{repo}/{endpoint}/{number}": _PAYLOADS[
            linked["state"]
        ]
    }


def _guard(tasks, proposed, policy, mode="live"):
    refs = [
        {
            "task_index": index,
            "id": str(task["id"]),
            "project_id": task["project_id"],
            "title": task.get("title", ""),
            "description": task.get("description", ""),
            "created": task.get("created", ""),
            "due_date": "",
            "priority": task.get("priority"),
            "done": task.get("done", False),
            "labels": task.get("labels", []),
        }
        for index, task in enumerate(tasks)
    ]
    return _MAIN(
        json.dumps({"actions": proposed}),
        json.dumps(refs),
        json.dumps(policy["allowed"]),
        json.dumps(policy["readonly"]),
        json.dumps(policy["rank_only"]),
        json.dumps(policy["denied"]),
        mode,
        _WEB_HOST,
        _API_BASE,
        _BAO,
        "role",
        "secret",
        _BAO_PATH,
    )


def test_selected_and_skipped_fixtures_are_exactly_the_expected_set():
    print("skipped guard fixtures (no proposed list):", ", ".join(_SKIPPED))
    assert len(_SELECTED) == 11
    assert sorted(_SKIPPED) == sorted(_EXPECTED_SKIPPED)


@pytest.mark.parametrize("case", _SELECTED, ids=[case["id"] for case in _SELECTED])
def test_guard_returns_the_fixture_actions(case, monkeypatch):
    case = _substitute(case)
    github = _github_for(case.get("linked_work"))
    requests = _install_stub(monkeypatch, github)

    result = _guard(
        case["tasks"], case["proposed"], case["policy"], case.get("mode", "live")
    )

    assert requests == list(github)
    assert result["actions"] == case["expected_actions"]
    if "expected_output" in case:
        assert result["dispatch"] == case["expected_output"]["dispatch"]
        assert result["mode"] == case["expected_output"]["mode"]


def test_injected_task_text_cannot_mark_done_or_change_priority(monkeypatch):
    case = _substitute(
        next(c for c in _SELECTED if c["id"] == "task-text-injection-is-untrusted")
    )
    requests = _install_stub(monkeypatch, {})

    result = _guard(case["tasks"], case["proposed"], case["policy"])

    assert requests == []
    assert not [
        action
        for action in result["actions"]
        if action.get("done") or "priority" in action or "labels" in action
    ]


@pytest.mark.parametrize(
    "path, payload, done",
    [
        ("pull/236", _PAYLOADS["closed-unmerged"], False),
        ("pull/236", _PAYLOADS["merged"], True),
        ("issues/12", {"state": "closed"}, True),
        ("pull/236", _PAYLOADS["open"], False),
    ],
    ids=[
        "closed-unmerged-pr-is-not-done",
        "merged-pr-is-done",
        "closed-issue-is-done",
        "open-pr-is-not-done",
    ],
)
def test_done_gate_decides_from_the_linked_github_state(
    path, payload, done, monkeypatch
):
    kind, number = path.split("/")
    endpoint = "pulls" if kind == "pull" else "issues"
    url = f"https://{_WEB_HOST}/dryvist/ai-llm-prompts/{path}"
    api_url = f"{_API_BASE}/repos/dryvist/ai-llm-prompts/{endpoint}/{number}"
    requests = _install_stub(monkeypatch, {api_url: payload})
    tasks = [
        {
            "id": "7",
            "project_id": "10",
            "title": "Triage task",
            "description": f"Linked work: {url}",
        }
    ]

    result = _guard(tasks, [{"task_index": 0, "kind": "done"}], _POLICY)

    assert requests == [api_url]
    expected = (
        [{"operation": "update", "id": "7", "projectId": "10", "done": True}]
        if done
        else []
    )
    assert result["actions"] == expected
