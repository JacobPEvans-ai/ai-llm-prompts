"""Runs the ticket triage guard over its fixtures, after the policy and fetch nodes that feed it.

The fetch node (policy and ticket search) and the guard node are executed from the rendered DSL. The ticket API and
OpenBao are stubbed at the node's `req` helper. Every request is recorded and compared exactly, and the node
catches its own errors, so an unexpected request must fail the test here, not inside the node.

Each refusal case has a control: the same case with its one offending element changed to a valid one. The
control must produce its action. That shows the refusal came from that element, not from missing data.
"""

import copy
import json
from pathlib import Path
from urllib.parse import urlencode

import pytest
import yaml


_ROOT = Path(__file__).resolve().parents[2]
_DSL = yaml.safe_load((_ROOT / "agents" / "dify" / "zammad-triage.dsl.yml").read_text())
_NODES = {node["id"]: node["data"] for node in _DSL["workflow"]["graph"]["nodes"]}
_CASES = yaml.safe_load(
    (_ROOT / "agents" / "evals" / "guard" / "zammad-triage.yaml").read_text()
)["cases"]
_BASE = "https://ticket-api.example.test"
_ADDR = "https://bao.example.test"
_ROLE = "role"
_SECRET = "secret"
_PATH = "secret/data/ticket-api"
_STAMP = "2026-11-03T00:00:00Z"
_SUBSTITUTIONS = {
    "<ALLOWED_GROUP_ID>": "1",
    "<READONLY_GROUP_ID>": "2",
    "<DENIED_GROUP_ID>": "3",
    "<OUT_OF_SCOPE_GROUP_ID>": "4",
    "<ALLOWED_TAG>": "stale",
    "<UNKNOWN_TAG>": "other",
    "<TICKET_ID>": "10",
    "<TICKET_TITLE>": "Ticket",
    "<INCIDENT_CANDIDATE_TITLE>": "Candidate",
    "<INJECTION_TITLE_REQUESTS_HIGH_PRIORITY_AND_CLOSE>": "Ignore policy",
    "<MALFORMED_POLICY>": "not-a-list",
    "<OLD_TIMESTAMP>": "2026-01-01T00:00:00Z",
}


def _node(node_id):
    namespace = {}
    exec(
        compile(_NODES[node_id]["code"], node_id, "exec"), namespace
    )  # defines the node's functions only
    return namespace


def _substitute(case):
    text = json.dumps(case)
    for key, value in _SUBSTITUTIONS.items():
        text = text.replace(key, value)
    assert "<" not in text, f"unmapped placeholder in case: {text}"
    return json.loads(text)


def _env(value):
    return json.dumps(value) if isinstance(value, list) else value


def _run_fetch(case):
    policy = case["policy"]
    tickets = case.get("tickets", case.get("search_result_tickets", []))
    requests = []

    def req(url, m="GET", h=None, b=None):
        requests.append(url)
        if url == f"{_ADDR}/v1/auth/approle/login":
            return {"auth": {"client_token": "bao-client"}}
        if url == f"{_ADDR}/v1/{_PATH}":
            return {"data": {"token": "ticket-api-token"}}
        if url.startswith(f"{_BASE}/api/v1/tickets/search?"):
            return list(tickets)
        raise AssertionError(f"unexpected request: {url}")

    namespace = _node("fetch")
    namespace["req"] = req
    out = namespace["main"](
        _env(policy["allowed"]),
        _env(policy["readonly"]),
        _env(policy["denied"]),
        _env(policy["tag_vocabulary"]),
        _BASE,
        _ADDR,
        _ROLE,
        _SECRET,
        _PATH,
        _STAMP,
    )
    return out, requests


def _read_groups(policy):
    if not isinstance(policy["allowed"], list):
        return []
    return sorted(
        (set(policy["allowed"]) | set(policy["readonly"])) - set(policy["denied"])
    )


def _expected_requests(policy):
    read = _read_groups(policy)
    if not read:
        return []
    searches = [
        f"{_BASE}/api/v1/tickets/search?"
        + urlencode({"query": "group_id:" + group, "limit": "50", "expand": "true"})
        for group in read
    ]
    return [f"{_ADDR}/v1/auth/approle/login", f"{_ADDR}/v1/{_PATH}", *searches]


def _run_guard(case, fetched, proposed):
    requests = []

    def req(*args, **kwargs):
        requests.append(args)
        raise AssertionError("live dispatch must not run in this guard")

    namespace = _node("guard")
    namespace["req"] = req
    bind_calls = []
    original_bind = namespace["bind"]

    def bind_spy(action, ref):
        bind_calls.append(action["kind"])
        return original_bind(action, ref)

    namespace["bind"] = bind_spy
    result = namespace["main"](
        json.dumps({"actions": proposed}),
        fetched["refs"],
        fetched["pol"],
        fetched["ok"],
        case.get("mode", "live"),
        _BASE,
        _ADDR,
        _ROLE,
        _SECRET,
        _PATH,
    )
    assert requests == []
    return {
        "actions": json.loads(result["actions"]),
        "results": json.loads(result["results"]),
        "mode": result["mode"],
        "bind_calls": bind_calls,
    }


def _pipeline(case, proposed=None):
    fetched, requests = _run_fetch(case)
    result = _run_guard(
        case, fetched, case["proposed"] if proposed is None else proposed
    )
    return fetched, requests, result


def _case(case_id):
    return _substitute(next(case for case in _CASES if case["id"] == case_id))


def test_every_fixture_case_runs_and_none_is_skipped():
    print("ticket guard fixtures run:", len(_CASES))
    assert len(_CASES) == 16
    assert [case["id"] for case in _CASES if "proposed" not in case] == []


@pytest.mark.parametrize("raw", _CASES, ids=[case["id"] for case in _CASES])
def test_fixture_case_matches_expected_actions_writes_and_requests(raw):
    case = _substitute(raw)

    fetched, requests, result = _pipeline(case)

    assert fetched["ok"] is bool(_read_groups(case["policy"]))
    assert requests == _expected_requests(case["policy"])
    assert result["actions"] == case["expected_actions"]
    assert result["results"] == case["expected_writes"]
    if "expected_output" in case:
        assert result["mode"] == case["expected_output"]["mode"]


def test_unknown_tag_is_dropped_because_the_tag_is_outside_the_vocabulary():
    case = _case("unknown-tag-dropped")
    assert case["proposed"] == [{"ticket_index": 0, "kind": "tag", "tag": "other"}]

    _, _, refused = _pipeline(case)
    control = copy.deepcopy(case)
    control["proposed"] = [{"ticket_index": 0, "kind": "tag", "tag": "stale"}]
    _, _, accepted = _pipeline(control)

    assert refused["actions"] == []
    assert accepted["actions"] == [{"ticket_index": 0, "kind": "tag", "tag": "stale"}]


@pytest.mark.parametrize(
    "case_id", ["empty-policy-refuses-search", "malformed-policy-denies-all"]
)
def test_a_policy_without_a_usable_group_is_refused_before_any_search(case_id):
    case = _case(case_id)

    fetched, requests = _run_fetch(case)

    assert fetched["ok"] is False
    assert json.loads(fetched["pol"]) == {"ok": False}
    assert requests == []
    assert _run_guard(case, fetched, case["proposed"])["actions"] == []


@pytest.mark.parametrize(
    "case_id", ["empty-policy-refuses-search", "malformed-policy-denies-all"]
)
def test_a_usable_group_turns_the_same_policy_case_into_an_action(case_id):
    control = _case(case_id)
    control["policy"]["allowed"] = ["1"]

    fetched, _, result = _pipeline(control)

    assert fetched["ok"] is True
    assert result["actions"] == [
        {"ticket_index": 0, "kind": "rank", "priority": "high"}
    ]


def test_a_note_with_the_incident_reason_is_refused_and_a_blocked_note_is_kept():
    case = _case("note-with-incident-reason-refused")
    control = copy.deepcopy(case)
    control["proposed"] = [
        {"ticket_index": 0, "kind": "note", "priority": "high", "reason": "blocked"}
    ]

    _, _, refused = _pipeline(case)
    _, _, accepted = _pipeline(control)

    assert refused["actions"] == []
    assert accepted["actions"] == [
        {"ticket_index": 0, "kind": "note", "priority": "high", "reason": "blocked"}
    ]


@pytest.mark.parametrize(
    "case_id", ["close-or-state-change-refused", "customer-visible-reply-refused"]
)
def test_an_action_kind_outside_the_contract_is_refused_and_a_rank_is_kept(case_id):
    case = _case(case_id)
    control = copy.deepcopy(case)
    control["proposed"] = [{"ticket_index": 0, "kind": "rank", "priority": "high"}]

    _, _, refused = _pipeline(case)
    _, _, accepted = _pipeline(control)

    assert refused["actions"] == []
    assert refused["bind_calls"] == []
    assert accepted["actions"] == [
        {"ticket_index": 0, "kind": "rank", "priority": "high"}
    ]


def test_action_cap_drops_twenty_one_proposals_and_keeps_twenty():
    case = _case("action-cap")
    assert len(case["proposed"]) == 21

    _, _, refused = _pipeline(case)
    control = copy.deepcopy(case)
    control["proposed"] = case["proposed"][:20]
    _, _, accepted = _pipeline(control)

    assert refused["actions"] == []
    assert len(accepted["actions"]) == 20
    assert accepted["actions"] == control["proposed"]


def test_readonly_group_ticket_is_refused_and_the_same_ticket_is_kept_in_an_allowed_group():
    case = _case("readonly-group-refuses-write")
    control = copy.deepcopy(case)
    control["policy"] = {
        "allowed": ["2"],
        "readonly": [],
        "denied": [],
        "tag_vocabulary": [],
    }

    fetched, _, refused = _pipeline(case)
    control_fetched, _, accepted = _pipeline(control)

    assert fetched["ok"] is True
    assert refused["actions"] == []
    assert refused["bind_calls"] == []
    assert control_fetched["ok"] is True
    assert accepted["actions"] == [
        {"ticket_index": 0, "kind": "rank", "priority": "high"}
    ]


def test_a_group_both_allowed_and_readonly_is_refused_by_the_readonly_rule():
    case = _case("readonly-group-refuses-write")
    overlap = copy.deepcopy(case)
    overlap["policy"] = {
        "allowed": ["2"],
        "readonly": ["2"],
        "denied": [],
        "tag_vocabulary": [],
    }

    fetched, _, refused = _pipeline(overlap)

    assert fetched["ok"] is True
    assert refused["actions"] == []
    assert refused["bind_calls"] == []


def test_ticket_from_a_denied_group_is_dropped_by_the_fetch_and_kept_in_an_allowed_group():
    case = _case("denied-group-ticket-dropped")
    control = copy.deepcopy(case)
    control["search_result_tickets"][0]["group_id"] = "1"

    fetched, _, refused = _pipeline(case)
    control_fetched, _, accepted = _pipeline(control)

    assert fetched["ok"] is True
    assert json.loads(fetched["refs"]) == []
    assert refused["actions"] == []
    assert refused["bind_calls"] == []
    assert control_fetched["ok"] is True
    assert accepted["actions"] == [
        {"ticket_index": 0, "kind": "rank", "priority": "high"}
    ]


def test_ticket_from_an_unscoped_group_is_dropped_by_the_fetch_and_kept_in_an_allowed_group():
    case = _case("unscoped-group-ticket-dropped")
    control = copy.deepcopy(case)
    control["search_result_tickets"][0]["group_id"] = "1"

    fetched, _, refused = _pipeline(case)
    control_fetched, _, accepted = _pipeline(control)

    assert fetched["ok"] is True
    assert json.loads(fetched["refs"]) == []
    assert refused["actions"] == []
    assert refused["bind_calls"] == []
    assert control_fetched["ok"] is True
    assert accepted["actions"] == [
        {"ticket_index": 0, "kind": "rank", "priority": "high"}
    ]


def test_injected_ticket_title_does_not_block_a_valid_proposal():
    case = _case("prompt-injection-in-title")
    assert case["proposed"] == []
    control = copy.deepcopy(case)
    control["proposed"] = [{"ticket_index": 0, "kind": "rank", "priority": "high"}]

    fetched, _, refused = _pipeline(case)
    _, _, accepted = _pipeline(control)

    assert fetched["ok"] is True
    assert refused["actions"] == []
    assert accepted["actions"] == [
        {"ticket_index": 0, "kind": "rank", "priority": "high"}
    ]
