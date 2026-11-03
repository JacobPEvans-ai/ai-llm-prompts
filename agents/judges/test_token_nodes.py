"""Runs the token-handling Code nodes that the Dify workflows repeat, against fixtures.

Each workflow carries its own copy of these nodes, so each copy runs on every fixture.
A parse node returns its token only in its designated output field. Every other output, and every
refused or failing case, must hold no token value. The token request node carries no token.
"""

import json
from pathlib import Path

import pytest
import yaml


_DIFY = Path(__file__).resolve().parents[2] / "agents" / "dify"
_WORKFLOWS = ("doc-contradiction-finder", "docs-updater", "ci-fixer", "code-simplifier")
_READ_SET_WORKFLOWS = ("doc-contradiction-finder", "docs-updater")
_TOKEN_FIELD = {"parse_openbao": "client_token", "parse_github_token": "token"}

_OPENBAO = {
    "success": ('{"auth": {"client_token": "tok-example-1", "lease_duration": 3600}}',
                {"client_token": "tok-example-1", "ready": 1}, []),
    "missing field": ('{"auth": {"lease_duration": 3600}}', {"client_token": "", "ready": 0}, []),
    "error payload": ('{"errors": ["permission denied"], "debug": {"client_token": "tok-example-2"}}',
                      {"client_token": "", "ready": 0}, ["tok-example-2"]),
    "malformed": ("not json", {"client_token": "", "ready": 0}, []),
    "non-object body": ("[]", {"client_token": "", "ready": 0}, []),
}

_GITHUB = {
    "success": ('{"token": "ghs-example-1", "expires_at": "2026-01-01T00:00:00Z"}',
                {"token": "ghs-example-1", "ready": 1}, []),
    "installation field": ('{"installation_token": "ghs-example-2"}', {"token": "ghs-example-2", "ready": 1}, []),
    "missing field": ('{"expires_at": "2026-01-01T00:00:00Z"}', {"token": "", "ready": 0}, []),
    "error payload": ('{"message": "Bad credentials", "token_hint": "ghs-example-3"}',
                      {"token": "", "ready": 0}, ["ghs-example-3"]),
    "malformed": ("{", {"token": "", "ready": 0}, []),
    "non-object body": ("[]", {"token": "", "ready": 0}, []),
    "both fields": ('{"token": "ghs-example-4", "installation_token": "ghs-example-5"}',
                    {"token": "ghs-example-4", "ready": 1}, ["ghs-example-5"]),
}


def _main(workflow, node_id):
    dsl = yaml.safe_load((_DIFY / f"{workflow}.dsl.yml").read_text())
    node = next(item for item in dsl["workflow"]["graph"]["nodes"] if item["id"] == node_id)
    namespace = {}
    exec(compile(node["data"]["code"], f"{workflow}:{node_id}", "exec"), namespace)  # defines the node's functions only
    return namespace["main"]


def _holders(out, value):
    return sorted(key for key, item in out.items() if value in str(item))


def _assert_token_placement(out, token_field, must_not_appear, expected_token):
    for value in must_not_appear:
        assert _holders(out, value) == [], f"{value} leaked into the outputs"
    if expected_token:
        assert _holders(out, expected_token) == [token_field], "the token must sit only in its designated field"


@pytest.mark.parametrize("workflow", _WORKFLOWS)
@pytest.mark.parametrize("case", list(_OPENBAO))
def test_openbao_response_parse(workflow, case):
    body, expected, must_not_appear = _OPENBAO[case]
    out = _main(workflow, "parse_openbao")(body)
    assert out == expected
    _assert_token_placement(out, "client_token", must_not_appear, expected["client_token"])


@pytest.mark.parametrize("workflow", _WORKFLOWS)
@pytest.mark.parametrize("case", list(_GITHUB))
def test_github_token_parse(workflow, case):
    body, expected, must_not_appear = _GITHUB[case]
    out = _main(workflow, "parse_github_token")(body)
    assert out == expected
    _assert_token_placement(out, "token", must_not_appear, expected["token"])


_REQUESTS = {
    "success": (("dryvist/ai-llm-prompts", "contents-read"), 1,
                {"repositories": ["dryvist/ai-llm-prompts"], "token_set": "contents-read"}),
    "missing field": (("", "contents-read"), 0, None),
    "error payload": (("https://example.test/not-a-repo", "contents-read"), 0, None),
    "token-set empty": (("dryvist/ai-llm-prompts", ""), 0, None),
    "token-set blank": (("dryvist/ai-llm-prompts", "   "), 0, None),
    "token-set unset": (("dryvist/ai-llm-prompts", None), 0, None),
    "non-dryvist owner": (("other/repo", "contents-read"), 0, None),
}


@pytest.mark.parametrize("workflow", _READ_SET_WORKFLOWS)
@pytest.mark.parametrize("case", list(_REQUESTS))
def test_read_only_token_request(workflow, case):
    (repo, read_set), ready, request = _REQUESTS[case]
    out = _main(workflow, "token_request")(repo, read_set)
    assert set(out) == {"ready", "request_json"}
    assert out["ready"] == ready
    if request is None:
        assert out["request_json"] == "{}"
    else:
        assert json.loads(out["request_json"]) == request
