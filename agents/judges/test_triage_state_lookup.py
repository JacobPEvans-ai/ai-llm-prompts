"""Runs the rendered triage GitHub-state lookups with the HTTP layer stubbed.

The lookup decides whether a linked GitHub item is merged, closed-unmerged, closed or open. A closed
pull request that was never merged must not read as done, even when the URL uses the issues path.
"""

import json
import urllib.request
from pathlib import Path

import yaml


_DSL = Path(__file__).resolve().parents[2] / "agents" / "dify" / "vikunja-triage.dsl.yml"
_WEB_HOST = "github.com"
_API_BASE = "https://api.github.com"
_ADDR = "https://bao.example"
_PATH = "secret/data/gh"
_REPO = "/repos/dryvist/ai-llm-prompts"


def _code_with(marker):
    dsl = yaml.safe_load(_DSL.read_text())
    for node in dsl["workflow"]["graph"]["nodes"]:
        code = node["data"].get("code")
        if code and marker in code:
            namespace = {}
            exec(compile(code, marker, "exec"), namespace)  # defines the node's functions only
            return namespace
    raise AssertionError(f"no rendered node defines {marker}")


class _Response:
    def __init__(self, payload):
        self._body = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


def _stub_github(monkeypatch, objects):
    def fake_urlopen(request, timeout=None):
        url = request.full_url
        if url.endswith("/v1/auth/approle/login"):
            return _Response({"auth": {"client_token": "client"}})
        if "/v1/" in url:
            return _Response({"data": {"token": "gh-token"}})
        for suffix, payload in objects.items():
            if url.endswith(suffix):
                return _Response(payload)
        raise AssertionError(f"unexpected request: {url}")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)


def _state_for(monkeypatch, url, objects):
    _stub_github(monkeypatch, objects)
    return _code_with("def state_for")["state_for"](url, _WEB_HOST, _API_BASE, _ADDR, "role", "secret", _PATH, {})


def _link_state(monkeypatch, url, objects):
    _stub_github(monkeypatch, objects)
    return _code_with("def link_state")["link_state"](url, _WEB_HOST, _API_BASE, _ADDR, "role", "secret", _PATH, [])


def test_issues_url_for_a_closed_unmerged_pr_is_not_done(monkeypatch):
    url = f"https://{_WEB_HOST}/dryvist/ai-llm-prompts/issues/236"
    objects = {f"{_REPO}/issues/236": {"state": "closed", "pull_request": {"merged_at": None}}}

    assert _state_for(monkeypatch, url, objects) == "closed-unmerged"
    assert _link_state(monkeypatch, url, objects) == "closed-unmerged"


def test_issues_url_for_a_merged_pr_is_merged(monkeypatch):
    url = f"https://{_WEB_HOST}/dryvist/ai-llm-prompts/issues/236"
    objects = {f"{_REPO}/issues/236": {"state": "closed", "pull_request": {"merged_at": "2026-11-01T00:00:00Z"}}}

    assert _state_for(monkeypatch, url, objects) == "merged"
    assert _link_state(monkeypatch, url, objects) == "merged"


def test_pull_url_for_a_closed_unmerged_pr_is_not_done(monkeypatch):
    url = f"https://{_WEB_HOST}/dryvist/ai-llm-prompts/pull/236"
    objects = {f"{_REPO}/pulls/236": {"state": "closed", "merged": False}}

    assert _state_for(monkeypatch, url, objects) == "closed-unmerged"
    assert _link_state(monkeypatch, url, objects) == "closed-unmerged"


def test_pull_url_for_a_merged_pr_is_merged(monkeypatch):
    url = f"https://{_WEB_HOST}/dryvist/ai-llm-prompts/pull/236"
    objects = {f"{_REPO}/pulls/236": {"state": "closed", "merged": True}}

    assert _state_for(monkeypatch, url, objects) == "merged"


def test_issues_url_with_a_malformed_pull_request_field_is_not_done(monkeypatch):
    url = f"https://{_WEB_HOST}/dryvist/ai-llm-prompts/issues/236"
    objects = {f"{_REPO}/issues/236": {"state": "closed", "pull_request": "not-an-object"}}

    assert _state_for(monkeypatch, url, objects) == "closed-unmerged"
    assert _link_state(monkeypatch, url, objects) == "closed-unmerged"


def test_issues_url_for_a_closed_issue_stays_closed_and_done(monkeypatch):
    url = f"https://{_WEB_HOST}/dryvist/ai-llm-prompts/issues/12"
    objects = {f"{_REPO}/issues/12": {"state": "closed"}}

    assert _state_for(monkeypatch, url, objects) == "closed"
