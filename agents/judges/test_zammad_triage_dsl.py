"""Contract tests for the zammad-triage Dify DSL code nodes, with the HTTP helper mocked."""

import inspect
import json
from pathlib import Path
import re

import yaml


_DSL = yaml.safe_load(
    (
        Path(__file__).resolve().parents[2]
        / "agents"
        / "dify"
        / "zammad-triage.dsl.yml"
    ).read_text()
)
_NODES = {node["id"]: node["data"] for node in _DSL["workflow"]["graph"]["nodes"]}
_FAKE_TOKEN = "fake-zammad-token-0f3a"
_POLICY = {
    "ok": True,
    "allowed": ["1", "3"],
    "readonly": ["2"],
    "denied": ["3"],
    "read": ["1", "2"],
    "write": ["1"],
    "tags": ["stale"],
}
_REFS = [
    {"ticket_index": 0, "id": "10", "group_id": "1"},
    {"ticket_index": 1, "id": "11", "group_id": "2"},
    {"ticket_index": 2, "id": "12", "group_id": "3"},
]
_ENV = (
    "https://zammad.example.test",
    "https://bao.example.test",
    "<ROLE>",
    "<SECRET>",
    "<PATH>",
)
_STAMP = "2026-11-02T00:00:00Z"


def _node(node_id, fail_writes=False, live=None):
    """Exec a code node with `req` replaced by a recorder that serves fake OpenBao and Zammad answers."""
    calls = []

    def req(url, m="GET", h=None, b=None):  # same parameter names as the nodes' helper
        calls.append((m, url, json.dumps(h or {}), b))
        if url.endswith("/auth/approle/login"):
            return {"auth": {"client_token": "fake-bao-token"}}
        if url.startswith(_ENV[1]):
            return {"data": {"token": _FAKE_TOKEN}}
        if "/tickets/search" in url:
            group = url.split("group_id%3A")[1].split("&")[0]
            return [
                {
                    "id": 10 + int(group),
                    "group_id": int(group),
                    "title": "Ticket " + group,
                    "priority_id": 2,
                    "state": "open",
                    "created_at": "2026-10-01T00:00:00Z",
                    "updated_at": "2026-10-20T00:00:00Z",
                }
            ]
        if fail_writes:
            raise OSError("write failed")
        return {}

    namespace = {}
    exec(compile(_NODES[node_id]["code"], node_id, "exec"), namespace)
    namespace["req"] = req
    if live is not None:
        namespace["LIVE"] = live
    return namespace["main"], calls


def _guard(actions, mode="shadow", text=None, **node):
    main, calls = _node("guard", **node)
    out = main(
        text or json.dumps({"actions": actions}),
        json.dumps(_REFS),
        json.dumps(_POLICY),
        True,
        mode,
        *_ENV,
    )
    return json.loads(out["actions"]), out, calls


def _outputs(node_id):
    """Outputs a selector may name: declared code outputs, an LLM node's text, and the sys values used here."""
    if node_id == "sys":
        return {"timestamp"}
    data = _NODES[node_id]
    return set(data.get("outputs") or {}) | (
        {"text"} if data["type"] == "llm" else set()
    )


def _selectors():
    for data in _NODES.values():
        for item in data.get("variables", []) + (
            data.get("outputs") if data["type"] == "end" else []
        ):
            yield item["value_selector"]
        for message in data.get("prompt_template", []):
            yield from (
                ref.split(".")
                for ref in re.findall(r"\{\{#([^#]+)#\}\}", message["text"])
            )


def test_every_selector_names_a_declared_output_or_env_variable():
    env = {variable["name"] for variable in _DSL["workflow"]["environment_variables"]}
    assert all(
        e["source"] in _NODES and e["target"] in _NODES
        for e in _DSL["workflow"]["graph"]["edges"]
    )
    selectors = list(_selectors())
    assert ["fetch", "model"] in selectors and ["triage", "text"] in selectors
    for source, name in selectors:
        assert name in (env if source == "env" else _outputs(source)), (source, name)


def test_every_code_node_main_takes_exactly_its_declared_variables_by_keyword():
    keyword_kinds = {
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY,
    }
    for node_id, data in _NODES.items():
        if data.get("type") == "code":
            params = inspect.signature(_node(node_id)[0]).parameters
            assert list(params) == [
                variable["variable"] for variable in data["variables"]
            ]
            assert all(p.kind in keyword_kinds for p in params.values())


def test_empty_or_malformed_policy_refuses_before_any_request():
    for allowed in ("[]", "not json", '[""]', "[1]"):
        main, calls = _node("fetch")
        assert main(allowed, "[]", "[]", "[]", *_ENV, _STAMP)["ok"] is False
        assert calls == []


def test_fetch_keeps_the_token_out_of_every_output_and_the_model_prompt():
    main, calls = _node("fetch")
    out = main('["1"]', '["2"]', '["3"]', '["stale"]', *_ENV, _STAMP)
    assert out["ok"] is True
    assert [c[1].split("?")[0] for c in calls if "/tickets/search" in c[1]] == [
        _ENV[0] + "/api/v1/tickets/search"
    ] * 2
    assert _FAKE_TOKEN not in json.dumps(out)
    assert all(
        set(t)
        == {
            "ticket_index",
            "title",
            "priority",
            "state",
            "age_days",
            "tags",
            "last_updated_age_days",
        }
        for t in json.loads(out["model"])
    )
    actions, guarded, _ = _guard(
        [{"ticket_index": 0, "kind": "rank", "priority": "high"}],
        mode="live",
        live=True,
    )
    assert _FAKE_TOKEN not in json.dumps(guarded)


def test_shadow_and_hard_disabled_live_make_no_request():
    for mode in ("shadow", "live", "LIVE"):
        actions, out, calls = _guard(
            [{"ticket_index": 0, "kind": "rank", "priority": "high"}], mode=mode
        )
        assert actions == [{"ticket_index": 0, "kind": "rank", "priority": "high"}]
        assert out["mode"] == "shadow" and out["results"] == "[]" and calls == []


def test_guard_drops_readonly_denied_unscoped_and_unlisted_actions():
    for refused in (
        [{"ticket_index": 1, "kind": "rank", "priority": "high"}],
        [{"ticket_index": 2, "kind": "rank", "priority": "high"}],
        [{"ticket_index": 0, "kind": "tag", "tag": "unlisted"}],
    ):
        assert _guard(refused)[0] == []


def test_guard_denies_the_whole_run_on_unknown_shapes_reasons_and_over_cap():
    for refused in (
        [{"ticket_index": 0, "kind": "close"}],
        [{"ticket_index": 0, "kind": "rank", "priority": "high", "state": "closed"}],
        [{"ticket_index": 9, "kind": "rank", "priority": "high"}],
        [
            {
                "ticket_index": 0,
                "kind": "note",
                "priority": "high",
                "reason": "incident_candidate",
            },
            {"ticket_index": 0, "kind": "rank", "priority": "high"},
        ],
        [{"ticket_index": 0, "kind": "rank", "priority": "low"}] * 21,
    ):
        assert _guard(refused)[0] == []
    assert _guard([], text="not json")[0] == []


def test_incident_proposals_are_never_dispatched_and_block_writes_on_that_ticket():
    actions, out, calls = _guard(
        [
            {
                "ticket_index": 0,
                "kind": "propose_incident",
                "reason": "incident_candidate",
            },
            {"ticket_index": 0, "kind": "rank", "priority": "high"},
        ],
        mode="live",
        live=True,
    )
    assert [a["kind"] for a in actions] == ["propose_incident"] and calls == []


def test_live_dispatch_stops_at_the_first_failed_write_and_denies_the_rest():
    plan = [
        {"ticket_index": 0, "kind": "rank", "priority": "high"},
        {"ticket_index": 0, "kind": "tag", "tag": "stale"},
    ]
    _, out, calls = _guard(plan, mode="live", live=True, fail_writes=True)
    writes = [c for c in calls if c[1].startswith(_ENV[0])]
    assert [w[0] for w in writes] == ["PUT"]
    assert [r.get("denied", False) for r in json.loads(out["results"])] == [False, True]
    assert all(not r["ok"] for r in json.loads(out["results"]))
