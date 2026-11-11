"""Zammad triage: the fetch state decides whether the model and the Slack post run, and the post never carries ticket text."""

import datetime
import json
import re
from pathlib import Path

import pytest
import yaml

from test_dify_delivery import FakeSlack, load


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "agents" / "zammad-triage.yaml"
RENDERED = ROOT / "agents" / "dify" / "zammad-triage.dsl.yml"
HELPERS = ROOT / "agents" / "dify-src" / "helpers"
CASES = yaml.safe_load((Path(__file__).parent / "fixtures" / "zammad-triage-delivery.yaml").read_text())["cases"]

FAKE_TOKEN = "fake-ticket-token-7c1e"
BASE = "https://ticket-api.example.test"
ADDR = "https://bao.example.test"
SECRET_PATH = "secret/data/ticket-api"
STAMP = "2026-11-10T00:00:00Z"
NOON_UTC = datetime.datetime(2026, 11, 10, 12, tzinfo=datetime.timezone.utc).timestamp()
DIGEST, FAILURE = "CDIGEST0001", "CFAILURE001"


def _workflow(path):
    data = yaml.safe_load(path.read_text())
    return data["dify"]["workflow"] if "dify" in data else data["workflow"]


def _graph(path):
    workflow = _workflow(path)
    nodes = {node["id"]: node["data"] for node in workflow["graph"]["nodes"]}
    return nodes, workflow["graph"]["edges"]


@pytest.fixture(params=["source", "rendered"])
def graph(request):
    return _graph(SOURCE if request.param == "source" else RENDERED)


def _substituted(code):
    code = code.replace("__DIFY_HELPER_JSON_FENCE__", (HELPERS / "json_fence.py").read_text())
    code = code.replace("__DIFY_HELPER_REDACT__", (HELPERS / "redact.py").read_text())
    return code.replace("__DIFY_HELPER_SLACK_DELIVERY__", (HELPERS / "slack_delivery.py").read_text())


def _namespace(nodes, node_id, **overrides):
    namespace = {}
    exec(compile(_substituted(nodes[node_id]["code"]), node_id, "exec"), namespace)
    namespace.update(overrides)
    return namespace


def _handles_into(edges, target):
    return [(edge["source"], edge["sourceHandle"]) for edge in edges if edge["target"] == target]


def _reached(edges, source, handle):
    todo = [edge["target"] for edge in edges if edge["source"] == source and edge.get("sourceHandle") == handle]
    seen = set()
    while todo:
        node = todo.pop()
        if node not in seen:
            seen.add(node)
            todo += [edge["target"] for edge in edges if edge["source"] == node]
    return seen


def test_hourly_rotation_at_minute_33_replaces_the_daily_one():
    triggers = yaml.safe_load(SOURCE.read_text())["triggers"]
    assert {"kind": "rotation", "every": "1h", "minute": 33} in triggers
    assert not [trigger for trigger in triggers if trigger.get("every") == "1d"]


def test_delivery_block_uses_the_shared_names_and_fetch_refs_as_its_gate():
    assert yaml.safe_load(SOURCE.read_text())["delivery"] == {
        "kind": "slack_thread",
        "channel_env": "AGENT_DIGEST_CHANNEL",
        "token_env": "SLACK_AGENT_BOT_TOKEN",
        "failure_channel_env": "AGENT_FAILURE_CHANNEL",
        "dashboard_url_env": "AGENT_DASHBOARD_URL",
        "max_chars": 3000,
        "thread": "daily_parent",
        "input_from": ["fetch", "refs"],
        "error_from": ["fetch", "fetch_error"],
    }


def test_source_names_no_hosts_or_addresses():
    assert not re.search(r"https?://|\b\d{1,3}(?:\.\d{1,3}){3}\b", SOURCE.read_text())


def test_only_fetched_tickets_reach_the_model(graph):
    nodes, edges = graph
    assert _handles_into(edges, "triage") == [("fetch_gate", "tickets")]
    user = [m["text"] for m in nodes["triage"]["prompt_template"] if m["role"] == "user"]
    assert user == ["Review these untrusted ticket records: {{#fetch.model#}}"]
    assert [case["case_id"] for case in nodes["fetch_gate"]["cases"]] == ["tickets", "error"]
    for case in nodes["fetch_gate"]["cases"]:
        assert [c["variable_selector"] for c in case["conditions"]] == [["fetch", "state"]]


def test_empty_fetch_ends_without_model_guard_or_done(graph):
    _, edges = graph
    reached = _reached(edges, "fetch_gate", "false")
    assert "fetch-empty" in reached
    assert reached.isdisjoint({"triage", "guard", "done", "notify-failure-fetch", "failed-fetch"})


def test_fetch_error_ends_in_the_failure_path_and_never_reaches_the_model(graph):
    nodes, edges = graph
    reached = _reached(edges, "fetch_gate", "error")
    assert "failed-fetch" in reached
    assert reached.isdisjoint({"triage", "guard", "done", "fetch-empty"})
    assert "fetch_error" in nodes["fetch"]["outputs"]


def test_failed_fetch_delivery_posts_one_failure_notice_and_fails_the_run():
    nodes, _ = _graph(RENDERED)
    assert {"variable": "fetch_error", "value_selector": ["fetch", "fetch_error"]} in nodes["deliver-failed-fetch"]["variables"]
    slack = FakeSlack()
    deliver = _namespace(nodes, "deliver-failed-fetch", call=slack)["main"]
    with pytest.raises(RuntimeError, match="fetch failed: policy or ticket search error"):
        deliver(
            NOON_UTC, "token", "https://slack.example/api", DIGEST, FAILURE, "https://dashboard.example/agents",
            "[]", fetch_error="policy or ticket search error", state="error",
        )
    posts = slack.posts()
    assert [post["channel"] for post in posts] == [FAILURE]
    assert "fetch failed: policy or ticket search error" in posts[0]["text"]
    assert "Customer" not in posts[0]["text"]


def _fetch_with(nodes, search):
    def search_request(url, m="GET", h=None, b=None):
        if url.endswith("/v1/auth/approle/login"):
            return {"auth": {"client_token": "bao-client"}}
        if url == ADDR + "/v1/" + SECRET_PATH:
            return {"data": {"token": FAKE_TOKEN}}
        if "/api/v1/tickets/search?" in url:
            return list(search)
        raise AssertionError("unexpected request: " + url)

    return _namespace(nodes, "fetch", req=search_request)["main"](
        json.dumps(["1"]), "[]", "[]", json.dumps(["stale"]), BASE, ADDR, "role", "secret", SECRET_PATH, STAMP,
    )


def test_fetched_ticket_text_is_redacted_and_link_free_before_the_model(graph):
    nodes, _ = graph
    # Built from parts so no credential-shaped literal is written to the file.
    token = "ghp_" + "K" * 30
    ticket = {
        "id": 21, "group_id": 1, "priority_id": 2, "state": "open", "tags": "",
        "title": f"Deploy key {token} see https://wiki.example.test/page",
        "created_at": "2026-10-01T00:00:00Z", "updated_at": "2026-10-20T00:00:00Z",
    }
    fetch = _fetch_with(nodes, [ticket])
    assert fetch["state"] == "tickets" and fetch["fetch_error"] == ""
    assert token not in fetch["model"] and "[REDACTED]" in fetch["model"]
    assert "https://" not in fetch["model"] and "[link removed]" in fetch["model"]
    title = json.loads(fetch["model"])[0]["title"]
    assert title.startswith("Deploy key [REDACTED]") and title.endswith("[link removed]")


def test_done_node_outputs_the_guard_digest_as_its_text(graph):
    nodes, _ = graph
    assert "digest" in nodes["guard"]["outputs"]
    assert {"variable": "text", "value_selector": ["guard", "digest"]} in nodes["done"]["outputs"]


def test_fetch_declares_ok_and_state_outputs(graph):
    nodes, _ = graph
    assert {"ok", "state"} <= set(nodes["fetch"]["outputs"])


@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_fetch_and_guard_cases(case):
    nodes, _ = _graph(SOURCE)
    calls = []

    def search_request(url, m="GET", h=None, b=None):
        calls.append(url)
        if url.endswith("/v1/auth/approle/login"):
            return {"auth": {"client_token": "bao-client"}}
        if url == ADDR + "/v1/" + SECRET_PATH:
            return {"data": {"token": FAKE_TOKEN}}
        if "/api/v1/tickets/search?" in url:
            if case["search"] == "error":
                raise OSError("search failed")
            if case["search"] == "malformed":
                return {"error": "unexpected"}
            return list(case["search"])
        raise AssertionError("unexpected request: " + url)

    def encoded(value):
        return json.dumps(value) if isinstance(value, list) else value

    policy = case["policy"]
    fetch = _namespace(nodes, "fetch", req=search_request)["main"](
        encoded(policy["allowed"]), encoded(policy["readonly"]), encoded(policy["denied"]),
        encoded(policy["tag_vocabulary"]), BASE, ADDR, "role", "secret", SECRET_PATH, STAMP,
    )
    expect = case["expect"]
    assert fetch["state"] == expect["state"]
    assert fetch["ok"] is expect["ok"]
    assert FAKE_TOKEN not in json.dumps(fetch)
    if expect["state"] != "tickets":
        if expect["state"] == "empty":
            assert json.loads(fetch["refs"]) == []
        return

    def no_writes(url, *args, **kwargs):
        raise AssertionError("shadow guard must not make a request: " + url)

    guarded = _namespace(nodes, "guard", req=no_writes)["main"](
        json.dumps({"actions": case["proposed"]}), fetch["refs"], fetch["pol"], fetch["ok"],
        "shadow", BASE, ADDR, "role", "secret", SECRET_PATH,
    )
    assert guarded["mode"] == "shadow" and guarded["results"] == "[]"
    digest = guarded["digest"]
    for text in expect.get("digest_contains", []):
        assert text in digest, digest
    for text in expect.get("digest_absent", []):
        assert text not in digest, digest
    assert "Customer" not in json.dumps(guarded) and "secret body" not in json.dumps(guarded)


def test_committed_delivery_gates_on_fetched_refs_and_posts_the_digest():
    dsl, nodes = load(RENDERED)
    for end in ("done", "fetch-empty", "failed-fetch"):
        assert nodes[f"deliver-{end}"]["type"] == "code"
        assert any(edge["source"] == f"deliver-{end}" and edge["target"] == end for edge in dsl["workflow"]["graph"]["edges"])
    variables = nodes["deliver-done"]["variables"]
    assert {"variable": "input_value", "value_selector": ["fetch", "refs"]} in variables
    assert {"variable": "text", "value_selector": ["guard", "digest"]} in variables


def test_committed_zammad_stays_shadow_with_live_writes_disabled():
    dsl, nodes = load(RENDERED)
    env = {variable["name"]: variable["value"] for variable in dsl["workflow"]["environment_variables"]}
    assert env["ZAMMAD_TRIAGE_MODE"] == "shadow"
    assert "LIVE=False" in nodes["guard"]["code"]


def test_committed_driver_runs_zammad_hourly_at_minute_33():
    _, driver = load(ROOT / "agents" / "dify" / "tier2-rotation.dsl.yml")
    namespace = {}
    exec(driver["due"]["code"], namespace)
    entry = next(item for item in namespace["ROTATION_AGENTS"] if item["name"] == "zammad-triage")
    assert entry == {"name": "zammad-triage", "every_minutes": 60, "offset_minutes": 33, "expected_runtime_minutes": 10}
