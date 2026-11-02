"""Contract tests for the zammad-triage Dify DSL code nodes."""

import inspect
import json
from pathlib import Path

import yaml


_DSL = yaml.safe_load((Path(__file__).resolve().parents[2] / "agents" / "dify" / "zammad-triage.dsl.yml").read_text())
_NODES = {node["id"]: node["data"] for node in _DSL["workflow"]["graph"]["nodes"]}
_POLICY = {"ok": True, "allowed": ["1", "3"], "readonly": ["2"], "denied": ["3"], "read": ["1", "2"],
           "write": ["1"], "tags": ["stale"]}
_REFS = [{"ticket_index": 0, "id": "10", "group_id": "1"}, {"ticket_index": 1, "id": "11", "group_id": "2"},
         {"ticket_index": 2, "id": "12", "group_id": "3"}]
_ENV = ("https://zammad.example.test", "https://bao.example.test", "<ROLE>", "<SECRET>", "<PATH>")


def _main(node_id):
    namespace = {}
    exec(compile(_NODES[node_id]["code"], node_id, "exec"), namespace)
    return namespace["main"]


def _guard(actions, mode="shadow", text=None):
    out = _main("guard")(text or json.dumps({"actions": actions}), json.dumps(_REFS), json.dumps(_POLICY), True,
                         mode, *_ENV)
    return json.loads(out["actions"]), out


def test_every_code_node_main_takes_exactly_its_declared_variables():
    edges_ok = all(e["source"] in _NODES and e["target"] in _NODES for e in _DSL["workflow"]["graph"]["edges"])
    env = {variable["name"] for variable in _DSL["workflow"]["environment_variables"]}
    assert edges_ok
    for node_id, data in _NODES.items():
        if data.get("type") == "code":
            declared = [variable["variable"] for variable in data["variables"]]
            assert list(inspect.signature(_main(node_id)).parameters) == declared
            assert all(v["value_selector"][1] in env for v in data["variables"] if v["value_selector"][0] == "env")


def test_no_node_outputs_or_reads_the_zammad_token():
    for data in _NODES.values():
        assert "token" not in json.dumps(data.get("outputs", {})).lower()
        assert all("token" not in str(v["value_selector"]).lower() or v["value_selector"][1] == "ZAMMAD_TOKEN_PATH"
                   for v in data.get("variables", []))


def test_fetch_refuses_an_empty_or_malformed_policy_before_any_request():
    fetch = _main("fetch")
    assert fetch("[]", "[]", "[]", "[]", *_ENV, "2026-11-02T00:00:00Z")["ok"] is False
    assert fetch("not json", "[]", "[]", "[]", *_ENV, "2026-11-02T00:00:00Z")["ok"] is False


def test_guard_keeps_only_writable_in_vocabulary_actions_in_shadow():
    actions, out = _guard([{"ticket_index": 0, "kind": "rank", "priority": "high"}])
    assert actions == [{"ticket_index": 0, "kind": "rank", "priority": "high"}]
    assert out["results"] == "[]" and out["mode"] == "shadow"
    for refused in ([{"ticket_index": 1, "kind": "rank", "priority": "high"}],
                    [{"ticket_index": 2, "kind": "rank", "priority": "high"}],
                    [{"ticket_index": 0, "kind": "tag", "tag": "unlisted"}]):
        assert _guard(refused)[0] == []


def test_guard_denies_the_whole_run_on_unknown_shapes_and_over_cap():
    for refused in ([{"ticket_index": 0, "kind": "close"}],
                    [{"ticket_index": 0, "kind": "rank", "priority": "high", "state": "closed"}],
                    [{"ticket_index": 9, "kind": "rank", "priority": "high"}],
                    [{"ticket_index": 0, "kind": "rank", "priority": "low"}] * 21):
        assert _guard(refused)[0] == []
    assert _guard([], text="not json")[0] == []


def test_incident_proposals_are_never_dispatched_and_block_writes_on_that_ticket():
    actions, out = _guard([{"ticket_index": 0, "kind": "propose_incident", "reason": "incident_candidate"},
                           {"ticket_index": 0, "kind": "rank", "priority": "high"}], mode="live")
    assert [a["kind"] for a in actions] == ["propose_incident"] and out["results"] == "[]"


def test_only_exact_live_leaves_shadow():
    assert _guard([], mode="LIVE")[1]["mode"] == "shadow"
