"""Slack thread delivery and failure notices: rendered into Dify Code nodes, then run offline against a fake Slack."""

import ast
import builtins
import datetime
from pathlib import Path

import pytest
import yaml

from test_dify_render import render_checkout, sample_checkout


DELIVERY = {
    "kind": "slack_thread",
    "channel_env": "SAMPLE_DIGEST_CHANNEL",
    "token_env": "SAMPLE_BOT_TOKEN",
    "failure_channel_env": "SAMPLE_FAILURE_CHANNEL",
    "dashboard_url_env": "SAMPLE_DASHBOARD_URL",
    "max_chars": 3000,
    "thread": "daily_parent",
    "input_from": ["start", "text"],
}
NOON_UTC = datetime.datetime(2026, 11, 10, 12, tzinfo=datetime.timezone.utc).timestamp()
DAY_START = int(datetime.datetime(2026, 11, 10, tzinfo=datetime.timezone.utc).timestamp())
DIGEST, FAILURE = "C-DIGEST", "C-FAILURE"


def render_sample(tmp_path, delivery=DELIVERY):
    path, definition = sample_checkout(tmp_path)
    if delivery is not None:
        definition["delivery"] = delivery
    path.write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr
    return tmp_path / "agents" / "dify" / "sample.dsl.yml"


def load(dsl_path):
    dsl = yaml.safe_load(Path(dsl_path).read_text())
    return dsl, {node["id"]: node["data"] for node in dsl["workflow"]["graph"]["nodes"]}


def namespace_for(dsl_path, node_id):
    _, nodes = load(dsl_path)
    namespace = {}
    exec(compile(nodes[node_id]["code"], node_id, "exec"), namespace)
    return namespace


class FakeSlack:
    """Stands in for the helper's call(): records each Slack method and answers from canned history."""

    def __init__(self, history=(), fail=lambda method, channel: False):
        self.history = list(history)
        self.fail = fail
        self.calls = []

    def __call__(self, api, token, method, payload=None, query=None):
        arguments = payload or query or {}
        self.calls.append((method, arguments))
        if self.fail(method, arguments.get("channel")):
            raise RuntimeError(method + " failed")
        if method == "conversations.history":
            return {"ok": True, "messages": self.history}
        return {"ok": True, "ts": "200.0"}

    def posts(self, channel=None):
        return [args for method, args in self.calls
                if method == "chat.postMessage" and (channel is None or args["channel"] == channel)]


def run(namespace, outputs, **overrides):
    arguments = {
        "run_timestamp": NOON_UTC, "bot_token": "token", "api_base": "https://slack.example/api",
        "digest_channel": DIGEST, "failure_channel": FAILURE,
        "dashboard_url": "https://dashboard.example/agents", "input_value": '[{"task_index": 0}]',
    }
    arguments.update(overrides)
    return namespace["main"](**arguments, **outputs)


def test_delivery_nodes_render_only_when_declared(tmp_path):
    dsl_path = render_sample(tmp_path, delivery=None)
    _, nodes = load(dsl_path)
    assert not [name for name in nodes if name.startswith(("deliver-", "notify-failure-", "failed-"))]
    names = {variable["name"] for variable in load(dsl_path)[0]["workflow"]["environment_variables"]}
    assert "SLACK_API_BASE" not in names


def test_declared_delivery_gates_each_end_and_the_model_failure(tmp_path):
    dsl_path = render_sample(tmp_path)
    dsl, nodes = load(dsl_path)
    edges = dsl["workflow"]["graph"]["edges"]
    assert nodes["deliver-done"]["type"] == "code"
    assert any(edge["source"] == "model" and edge["target"] == "deliver-done" for edge in edges)
    assert any(edge["source"] == "deliver-done" and edge["target"] == "done" for edge in edges)
    assert not any(edge["source"] == "model" and edge["target"] == "done" for edge in edges)
    assert {"variable": "text", "value_selector": ["model", "text"]} in nodes["deliver-done"]["variables"]
    assert {"variable": "input_value", "value_selector": ["start", "text"]} in nodes["deliver-done"]["variables"]
    assert nodes["model"]["error_strategy"] == "fail-branch"
    assert any(edge["source"] == "model" and edge["sourceHandle"] == "fail-branch"
               and edge["target"] == "notify-failure-model" for edge in edges)
    assert nodes["failed-model"]["type"] == "end"
    assert {"variable": "failure_channel", "value_selector": ["env", "SAMPLE_FAILURE_CHANNEL"]} in (
        nodes["notify-failure-model"]["variables"])


def test_delivery_env_vars_hold_names_and_no_values(tmp_path):
    dsl, _ = load(render_sample(tmp_path))
    env = {variable["name"]: variable for variable in dsl["workflow"]["environment_variables"]}
    assert env["SAMPLE_BOT_TOKEN"]["value_type"] == "secret"
    for name in ("SAMPLE_BOT_TOKEN", "SAMPLE_DIGEST_CHANNEL", "SAMPLE_FAILURE_CHANNEL", "SAMPLE_DASHBOARD_URL", "SLACK_API_BASE"):
        assert env[name]["value"] == ""
    assert len({variable["id"] for variable in dsl["workflow"]["environment_variables"]}) == len(
        dsl["workflow"]["environment_variables"])


def test_failure_channel_env_must_differ_from_the_delivery_channel(tmp_path):
    path, definition = sample_checkout(tmp_path)
    definition["delivery"] = {**DELIVERY, "failure_channel_env": DELIVERY["channel_env"]}
    path.write_text(yaml.safe_dump(definition))
    result = render_checkout(tmp_path)
    assert result.returncode != 0
    assert "failure channel env must differ from the delivery channel env" in result.stderr


@pytest.mark.parametrize("updates", [
    {"kind": "webhook"}, {"thread": "per_run"}, {"channel_env": "digest"}, {"max_chars": 99},
    {"max_chars": 10001}, {"input_from": ["missing", "text"]}, {"input_from": ["start"]},
])
def test_render_rejects_invalid_delivery(tmp_path, updates):
    path, definition = sample_checkout(tmp_path)
    definition["delivery"] = {**DELIVERY, **updates}
    path.write_text(yaml.safe_dump(definition))
    assert render_checkout(tmp_path).returncode != 0


def test_summary_truncates_to_max_chars_with_visible_marker(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack()
    namespace["call"] = fake
    assert run(namespace, {"text": "x" * 5000}) == {"status": "posted"}
    reply = fake.posts(DIGEST)[-1]["text"]
    assert len(reply) == 3000 and reply.endswith("\n[truncated]")


def test_short_summary_is_posted_unchanged(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack()
    namespace["call"] = fake
    run(namespace, {"text": "short report"})
    assert fake.posts(DIGEST)[-1]["text"] == "short report"


def test_summary_redacts_addresses_before_posting(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack()
    namespace["call"] = fake
    run(namespace, {"text": "peer 192.0.2.10 is down"})
    reply = fake.posts(DIGEST)[-1]["text"]
    assert "192.0.2.10" not in reply and "[REDACTED]" in reply


@pytest.mark.parametrize("value", ["", "   ", "[]", "{}", "null", None])
def test_empty_input_posts_nothing(tmp_path, value):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack()
    namespace["call"] = fake
    assert run(namespace, {"text": "heartbeat"}, input_value=value) == {"status": "skipped"}
    assert fake.calls == []


def test_non_text_outputs_are_listed_as_key_value_lines(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack()
    namespace["call"] = fake
    run(namespace, {"actions": '[{"kind": "rank"}]', "mode": "shadow", "dispatch": False})
    reply = fake.posts(DIGEST)[-1]["text"]
    assert reply == 'actions: [{"kind": "rank"}]\ndispatch: false\nmode: shadow'


def test_reply_joins_the_existing_bot_parent_for_the_day(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    parent = {"ts": "111.1", "text": "sample digest 2026-11-10 (UTC)", "bot_id": "B1"}
    fake = FakeSlack(history=[parent])
    namespace["call"] = fake
    assert run(namespace, {"text": "x"}) == {"status": "posted"}
    assert fake.calls[0] == ("conversations.history", {"channel": DIGEST, "oldest": str(DAY_START - 1), "limit": 200})
    assert [method for method, _ in fake.calls].count("chat.postMessage") == 1
    assert fake.posts(DIGEST)[0]["thread_ts"] == "111.1"


def test_a_human_post_with_the_same_text_is_not_reused_as_parent(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    impostor = {"ts": "111.1", "text": "sample digest 2026-11-10 (UTC)"}
    fake = FakeSlack(history=[impostor])
    namespace["call"] = fake
    run(namespace, {"text": "x"})
    assert fake.posts(DIGEST)[0] == {"channel": DIGEST, "text": "sample digest 2026-11-10 (UTC)"}
    assert fake.posts(DIGEST)[1]["thread_ts"] == "200.0"


def test_first_run_of_the_day_creates_one_parent_then_replies(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack(history=[])
    namespace["call"] = fake
    run(namespace, {"text": "x"})
    parent, reply = fake.posts(DIGEST)
    assert parent == {"channel": DIGEST, "text": "sample digest 2026-11-10 (UTC)"}
    assert reply["thread_ts"] == "200.0" and reply["channel"] == DIGEST


def test_failed_post_sends_one_notice_to_the_failure_channel(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack(fail=lambda method, channel: method == "chat.postMessage" and channel == DIGEST)
    namespace["call"] = fake
    assert run(namespace, {"text": "x"}) == {"status": "failed"}
    notices = fake.posts(FAILURE)
    assert len(notices) == 1
    assert notices[0]["text"] == (
        "sample delivery failed at 2026-11-10 12:00 UTC. Dashboard: https://dashboard.example/agents"
    )
    assert not [post for post in fake.posts(DIGEST) if "failed" in post["text"]]


@pytest.mark.parametrize("failure_channel", [DIGEST, ""])
def test_failure_notice_is_never_posted_to_the_digest_channel(tmp_path, failure_channel):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack(fail=lambda method, channel: method == "chat.postMessage" and channel == DIGEST)
    namespace["call"] = fake
    assert run(namespace, {"text": "x"}, failure_channel=failure_channel) == {"status": "failed-unreported"}
    assert not [post for post in fake.posts() if "failed" in post["text"]]


def test_failed_model_run_posts_one_notice_and_ends(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "notify-failure-model")
    fake = FakeSlack()
    namespace["call"] = fake
    output = namespace["main"](
        run_timestamp=NOON_UTC, bot_token="token", api_base="https://slack.example/api",
        digest_channel=DIGEST, failure_channel=FAILURE, dashboard_url="https://dashboard.example/agents",
    )
    assert output == {"text": "Run failed; failure notice: failed"}
    assert fake.posts(FAILURE)[0]["text"].startswith("sample run failed at 2026-11-10 12:00 UTC")
    assert fake.posts(DIGEST) == []


def unbound_names(source):
    """Names a Code node loads but never binds. Scope-blind on purpose: it catches a name no part of the node defines."""
    tree = ast.parse(source)
    bound = set(dir(builtins))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            bound.add(node.name)
            arguments = node.args.args + node.args.kwonlyargs + node.args.posonlyargs
            bound.update(argument.arg for argument in arguments)
            bound.update(argument.arg for argument in (node.args.vararg, node.args.kwarg) if argument)
        elif isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load):
            bound.add(node.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            bound.update((alias.asname or alias.name).split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound.add(node.name)
    loaded = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)}
    return sorted(loaded - bound)


def test_unbound_name_check_flags_a_name_nobody_defines():
    assert unbound_names("def send():\n    return MAX_CHARS + len(TRUNCATED)\n") == ["MAX_CHARS", "TRUNCATED"]


@pytest.mark.parametrize("node_id", ["deliver-done", "notify-failure-model"])
def test_rendered_code_nodes_bind_every_name_they_use(tmp_path, node_id):
    _, nodes = load(render_sample(tmp_path))
    assert unbound_names(nodes[node_id]["code"]) == []
