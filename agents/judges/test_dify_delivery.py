"""Slack thread delivery and failure notices: rendered into Dify Code nodes, then run offline against a fake Slack."""

import ast
import builtins
import datetime
import json
import urllib.request
from pathlib import Path

import pytest
import yaml

from definitions import definition
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
DIGEST, FAILURE = "C0DIGEST01", "C0FAILURE1"


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
    """Stands in for the helper's call(). Records each method. History answers from pages, linked by a cursor.

    channels maps a channel to its own pages; other channels use pages.
    """

    def __init__(self, history=(), pages=None, fail=lambda method, channel: False, channels=None):
        self.pages = pages if pages is not None else [list(history)]
        self.channels = channels or {}
        self.fail = fail
        self.calls = []

    def __call__(self, api, token, method, payload=None, query=None):
        arguments = payload or query or {}
        self.calls.append((method, arguments))
        if self.fail(method, arguments.get("channel")):
            raise RuntimeError(method + " failed")
        if method == "conversations.history":
            pages = self.channels.get(arguments.get("channel"), self.pages)
            index = int(arguments.get("cursor") or 0)
            more = index + 1 < len(pages)
            return {"ok": True, "messages": pages[index],
                    "response_metadata": {"next_cursor": str(index + 1) if more else ""}}
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
    {"error_from": ["missing", "text"]}, {"error_from": ["start"]}, {"extra": "field"},
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


def test_failed_post_sends_one_notice_to_the_failure_channel_and_fails_the_run(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack(fail=lambda method, channel: method == "chat.postMessage" and channel == DIGEST)
    namespace["call"] = fake
    with pytest.raises(RuntimeError, match="delivery failed; failure notice failed"):
        run(namespace, {"text": "x"})
    notices = fake.posts(FAILURE)
    assert len(notices) == 1
    assert notices[0]["text"] == (
        "sample delivery failed at 2026-11-10 12:00 UTC. Dashboard: https://dashboard.example/agents"
    )
    assert not [post for post in fake.posts(DIGEST) if "failed" in post["text"]]


def prior_notice(ts):
    return {"bot_id": "B0BOT", "text": "sample delivery failed at 2026-11-10 09:00 UTC.", "ts": str(ts)}


def test_second_failure_within_24_hours_posts_no_notice(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack(channels={FAILURE: [[prior_notice(NOON_UTC - 3 * 3600)]]},
                     fail=lambda method, channel: method == "chat.postMessage" and channel == DIGEST)
    namespace["call"] = fake
    with pytest.raises(RuntimeError, match=r"delivery failed; failure notice suppressed \(already notified\)"):
        run(namespace, {"text": "x"})
    assert fake.posts(FAILURE) == []
    lookups = [args for method, args in fake.calls
               if method == "conversations.history" and args["channel"] == FAILURE]
    assert lookups == [{"channel": FAILURE, "oldest": str(int(NOON_UTC) - 86400), "limit": 200}]


def test_failure_after_24_hours_posts_a_new_notice(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack(channels={FAILURE: [[prior_notice(NOON_UTC - 86400 - 60)]]},
                     fail=lambda method, channel: method == "chat.postMessage" and channel == DIGEST)
    namespace["call"] = fake
    with pytest.raises(RuntimeError, match="; failure notice failed$"):
        run(namespace, {"text": "x"})
    assert len(fake.posts(FAILURE)) == 1


def test_unreadable_failure_history_still_posts_the_notice(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack(fail=lambda method, channel: (method == "conversations.history" and channel == FAILURE)
                     or (method == "chat.postMessage" and channel == DIGEST))
    namespace["call"] = fake
    with pytest.raises(RuntimeError, match="; failure notice failed$"):
        run(namespace, {"text": "x"})
    assert len(fake.posts(FAILURE)) == 1


@pytest.mark.parametrize("failure_channel", [DIGEST, ""])
def test_failure_notice_is_never_posted_to_the_digest_channel(tmp_path, failure_channel):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack(fail=lambda method, channel: method == "chat.postMessage" and channel == DIGEST)
    namespace["call"] = fake
    with pytest.raises(RuntimeError, match="failure notice failed-unreported"):
        run(namespace, {"text": "x"}, failure_channel=failure_channel)
    assert not [post for post in fake.posts() if "failed" in post["text"]]


def test_failed_model_run_posts_one_notice_and_fails_the_run(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "notify-failure-model")
    fake = FakeSlack()
    namespace["call"] = fake
    with pytest.raises(RuntimeError, match="run failed; failure notice failed"):
        namespace["main"](
            run_timestamp=NOON_UTC, bot_token="token", api_base="https://slack.example/api",
            digest_channel=DIGEST, failure_channel=FAILURE, dashboard_url="https://dashboard.example/agents",
        )
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


ROOT = Path(__file__).resolve().parents[2]
DELIVERY_PREFIXES = ("deliver-", "notify-failure-", "failed-")


def committed(name):
    return load(ROOT / "agents" / "dify" / f"{name}.dsl.yml")


def test_only_vikunja_triage_declares_delivery_nodes():
    declaring = set()
    for path in (ROOT / "agents" / "dify").glob("*.dsl.yml"):
        _, nodes = load(path)
        if any(node_id.startswith(DELIVERY_PREFIXES) for node_id in nodes):
            declaring.add(path.name[: -len(".dsl.yml")])
    assert declaring == {"vikunja-triage"}


def test_vikunja_triage_renders_delivery_and_failure_nodes():
    dsl, nodes = committed("vikunja-triage")
    edges = dsl["workflow"]["graph"]["edges"]
    for end in ("shadow_end", "live_end"):
        assert nodes[f"deliver-{end}"]["type"] == "code"
        assert any(edge["source"] == f"deliver-{end}" and edge["target"] == end for edge in edges)
    assert {"variable": "input_value", "value_selector": ["prepare", "task_refs"]} in nodes["deliver-shadow_end"]["variables"]
    assert nodes["triage"]["error_strategy"] == "fail-branch"
    assert any(edge["source"] == "triage" and edge["sourceHandle"] == "fail-branch"
               and edge["target"] == "notify-failure-triage" for edge in edges)
    assert nodes["notify-failure-triage"]["type"] == "code"
    assert nodes["failed-triage"]["type"] == "end"
    env = {variable["name"]: variable for variable in dsl["workflow"]["environment_variables"]}
    assert env["SLACK_AGENT_BOT_TOKEN"]["value_type"] == "secret"
    for name in ("SLACK_AGENT_BOT_TOKEN", "AGENT_DIGEST_CHANNEL", "AGENT_FAILURE_CHANNEL", "AGENT_DASHBOARD_URL",
                 "SLACK_API_BASE"):
        assert env[name]["value"] == ""
    for node_id in ("deliver-shadow_end", "deliver-live_end", "notify-failure-triage"):
        assert unbound_names(nodes[node_id]["code"]) == []


def test_vikunja_delivery_only_flows_to_its_end_nodes():
    dsl, nodes = committed("vikunja-triage")
    edges = dsl["workflow"]["graph"]["edges"]
    delivery = {node_id for node_id in nodes if node_id.startswith(DELIVERY_PREFIXES)}
    outgoing = {edge["target"] for edge in edges if edge["source"] in delivery}
    assert outgoing <= {"shadow_end", "live_end", "failed-triage"}


def test_vikunja_triage_runs_hourly_at_minute_43_and_stays_shadow():
    agent = definition("vikunja-triage")
    assert {"kind": "rotation", "every": "1h", "minute": 43} in agent["triggers"]
    assert agent["mode"] == "shadow"
    _, driver = committed("tier2-rotation")
    namespace = {}
    exec(driver["due"]["code"], namespace)
    entry = next(item for item in namespace["ROTATION_AGENTS"] if item["name"] == "vikunja-triage")
    assert entry == {"name": "vikunja-triage", "every_minutes": 60, "offset_minutes": 43, "expected_runtime_minutes": 10}
    dsl, _ = committed("vikunja-triage")
    env = {variable["name"]: variable["value"] for variable in dsl["workflow"]["environment_variables"]}
    assert env["VIKUNJA_TRIAGE_MODE"] == "shadow"


VIKUNJA = ROOT / "agents" / "dify" / "vikunja-triage.dsl.yml"
# Token-shaped fixtures are assembled from parts, so no credential-shaped literal is written to the file.
SLACK_TOKEN = "xox" + "b-1234567890-abcdefghijk"
VAULT_TOKEN = "hv" + "s.CAESIJabcdefghijklmnopqrstuvwxyz0123"
BEARER_VALUE = "abcdefghijklmnopqrstuvwx"
GITHUB_TOKEN = "gh" + "p_abcdefghijklmnopqrstu"


def test_summary_neutralises_slack_markup_before_posting(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack()
    namespace["call"] = fake
    run(namespace, {"text": "<!channel> <!here> <@UEXAMPLE> <https://evil.example|click> a & b"})
    # The host is redacted by the shared rule. Escaping keeps the angle brackets from forming a link.
    assert fake.posts(DIGEST)[-1]["text"] == (
        "&lt;!channel&gt; &lt;!here&gt; &lt;@UEXAMPLE&gt; &lt;https://[REDACTED]|click&gt; a &amp; b"
    )


def test_truncation_never_splits_an_escaped_entity(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack()
    namespace["call"] = fake
    run(namespace, {"text": "<" * 5000})
    reply = fake.posts(DIGEST)[-1]["text"]
    assert len(reply) == 3000 and reply.endswith("\n[truncated]")
    assert reply[: -len("\n[truncated]")].replace("&lt;", "") == ""


def test_slack_vault_and_bearer_tokens_are_redacted_before_posting(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack()
    namespace["call"] = fake
    run(namespace, {"text": f"keys {SLACK_TOKEN}, {VAULT_TOKEN}, Authorization: Bearer {BEARER_VALUE}"})
    reply = fake.posts(DIGEST)[-1]["text"]
    for secret in (SLACK_TOKEN, VAULT_TOKEN, BEARER_VALUE):
        assert secret not in reply
    assert reply.count("[REDACTED]") == 3


def test_public_github_links_survive_and_secrets_inside_them_do_not(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack()
    namespace["call"] = fake
    run(namespace, {"text": "PR https://github.com/acme/app/pull/12 and "
                            f"https://github.com/acme/app/issues/3?token={GITHUB_TOKEN}"})
    reply = fake.posts(DIGEST)[-1]["text"]
    assert "https://github.com/acme/app/pull/12" in reply
    assert GITHUB_TOKEN not in reply
    assert "https://github.com/acme/app/issues/3?token=[REDACTED]" in reply


def test_history_failure_notifies_and_fails_the_run(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack(fail=lambda method, channel: method == "conversations.history")
    namespace["call"] = fake
    with pytest.raises(RuntimeError, match="delivery failed; failure notice failed"):
        run(namespace, {"text": "x"})
    assert [post["text"] for post in fake.posts(FAILURE)] == [
        "sample delivery failed at 2026-11-10 12:00 UTC. Dashboard: https://dashboard.example/agents",
    ]
    assert fake.posts(DIGEST) == []


def test_parent_create_failure_notifies_and_fails_before_any_reply(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack(history=[], fail=lambda method, channel: method == "chat.postMessage" and channel == DIGEST)
    namespace["call"] = fake
    with pytest.raises(RuntimeError, match="delivery failed; failure notice failed"):
        run(namespace, {"text": "x"})
    assert len(fake.posts(FAILURE)) == 1
    assert not [post for post in fake.posts(DIGEST) if "thread_ts" in post]


def test_parent_is_found_on_a_later_history_page(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    other = {"ts": "50.0", "text": "unrelated", "bot_id": "B2"}
    parent = {"ts": "111.1", "text": "sample digest 2026-11-10 (UTC)", "bot_id": "B1"}
    fake = FakeSlack(pages=[[other], [parent]])
    namespace["call"] = fake
    assert run(namespace, {"text": "x"}) == {"status": "posted"}
    histories = [arguments for method, arguments in fake.calls if method == "conversations.history"]
    assert [history.get("cursor") for history in histories] == [None, "1"]
    assert all(history["oldest"] == str(DAY_START - 1) for history in histories)
    assert fake.posts(DIGEST) == [{"channel": DIGEST, "thread_ts": "111.1", "text": "x"}]


def test_parent_absent_from_every_page_is_created_once(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    other = {"ts": "50.0", "text": "unrelated", "bot_id": "B2"}
    fake = FakeSlack(pages=[[other], [other]])
    namespace["call"] = fake
    run(namespace, {"text": "x"})
    assert [method for method, _ in fake.calls].count("conversations.history") == 2
    assert fake.posts(DIGEST) == [
        {"channel": DIGEST, "text": "sample digest 2026-11-10 (UTC)"},
        {"channel": DIGEST, "thread_ts": "200.0", "text": "x"},
    ]


def test_fetch_error_sends_a_notice_and_fails_even_with_no_input(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack()
    namespace["call"] = fake
    with pytest.raises(RuntimeError, match="fetch failed: a Vikunja list call failed; failure notice failed"):
        run(namespace, {"text": "x"}, input_value="[]", fetch_error="a Vikunja list call failed")
    notices = fake.posts(FAILURE)
    assert len(notices) == 1 and "fetch failed: a Vikunja list call failed" in notices[0]["text"]
    assert fake.posts(DIGEST) == []


@pytest.mark.parametrize("digest", ["#general", "general", "c0lowercase"])
def test_digest_channel_must_be_a_channel_id(tmp_path, digest):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack()
    namespace["call"] = fake
    with pytest.raises(RuntimeError, match="delivery failed; failure notice failed"):
        run(namespace, {"text": "x"}, digest_channel=digest)
    assert not [post for post in fake.posts() if post["channel"] == digest]
    assert len(fake.posts(FAILURE)) == 1


def test_failure_channel_must_be_a_channel_id(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack(fail=lambda method, channel: method == "chat.postMessage" and channel == DIGEST)
    namespace["call"] = fake
    with pytest.raises(RuntimeError, match="failure notice failed-unreported"):
        run(namespace, {"text": "x"}, failure_channel="#alerts")
    assert not [post for post in fake.posts() if post["channel"] == "#alerts"]


@pytest.mark.parametrize("api", ["https://evil.example/api", "http://slack.com/api", "slack.com/api"])
def test_token_is_never_sent_to_an_untrusted_or_plain_base(tmp_path, api):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    with pytest.raises(RuntimeError, match="failure notice failed-unreported"):
        run(namespace, {"text": "x"}, api_base=api)


def test_approved_base_posts_through_the_real_call(tmp_path, monkeypatch):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    sent = []

    class Response:
        def __init__(self, body):
            self.body = body

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return json.dumps(self.body).encode()

    def fake_urlopen(request, timeout):
        sent.append((request.full_url, request.get_header("Authorization")))
        if "conversations.history" in request.full_url:
            return Response({"ok": True, "messages": []})
        return Response({"ok": True, "ts": "200.0"})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert run(namespace, {"text": "x"}, api_base="https://slack.com/api", bot_token="token") == {"status": "posted"}
    assert all(url.startswith("https://slack.com/api/") for url, _ in sent)
    assert {auth for _, auth in sent} == {"Bearer token"}


def test_delivery_status_is_reported_on_each_end_node(tmp_path):
    _, nodes = load(render_sample(tmp_path))
    assert {"variable": "delivery_status", "value_selector": ["deliver-done", "status"]} in nodes["done"]["outputs"]
    _, vikunja = committed("vikunja-triage")
    for end in ("shadow_end", "live_end"):
        assert {"variable": "delivery_status", "value_selector": [f"deliver-{end}", "status"]} in vikunja[end]["outputs"]


def test_fetch_error_input_is_declared_only_when_error_from_is_set(tmp_path):
    _, plain = load(render_sample(tmp_path / "plain", delivery=DELIVERY))
    assert not [variable for variable in plain["deliver-done"]["variables"] if variable["variable"] == "fetch_error"]
    _, declared = load(render_sample(tmp_path / "declared", delivery={**DELIVERY, "error_from": ["start", "text"]}))
    assert {"variable": "fetch_error", "value_selector": ["start", "text"]} in declared["deliver-done"]["variables"]


def test_vikunja_delivery_reads_the_guard_fetch_error_and_list_failures_route_to_it():
    _, nodes = committed("vikunja-triage")
    for node in ("deliver-shadow_end", "deliver-live_end"):
        assert {"variable": "fetch_error", "value_selector": ["guard", "fetch_error"]} in nodes[node]["variables"]
    assert nodes["list_tasks"]["error_strategy"] == "default-value"
    assert nodes["list_tasks"]["default_value"] == [{"key": "text", "type": "string", "value": ""}]


def test_list_failure_is_marked_not_read_as_an_empty_project():
    namespace = namespace_for(VIKUNJA, "scope_list_result")
    assert json.loads(namespace["main"](project_id="p1", body="")["result_json"]) == {
        "project_id": "p1", "error": "list failed",
    }
    assert json.loads(namespace["main"](project_id="p1", body="{}")["result_json"])["error"] == "list failed"
    assert json.loads(namespace["main"](project_id="p1", body="[]")["result_json"]) == {"project_id": "p1", "tasks": []}


def prepare_main(namespace, results, policy_ok=True):
    return namespace["main"](
        results=results, policy_ok=policy_ok, timestamp="1794312000", web_host="github.example",
        api_base="https://api.github.example", bao_addr="", role_id="role", secret_id="secret",
        token_path="github-token/vikunja-triage",
    )


def test_invalid_policy_is_a_fetch_error_not_an_empty_task_list():
    out = prepare_main(namespace_for(VIKUNJA, "prepare"), [], policy_ok=False)
    assert out["task_refs"] == "[]" and out["fetch_error"] == "project policy is invalid"


def test_failed_list_entry_is_reported_and_not_dropped():
    results = [json.dumps({"project_id": "p1", "error": "list failed"})]
    out = prepare_main(namespace_for(VIKUNJA, "prepare"), results)
    assert out["task_refs"] == "[]" and out["fetch_error"] == "a Vikunja list call failed"


def test_link_check_failure_is_reported_and_not_treated_as_unlinked():
    task = {"id": 7, "title": "fix https://github.example/acme/app/pull/12", "description": ""}
    out = prepare_main(namespace_for(VIKUNJA, "prepare"), [json.dumps({"project_id": "p1", "tasks": [task]})])
    assert json.loads(out["task_refs"])[0]["id"] == "7"
    assert out["fetch_error"] == "a GitHub link check failed"


def guard_main(namespace, **overrides):
    arguments = dict(
        model_text='{"actions": []}', refs_text="[]", allowed_raw='["p1"]', readonly_raw="[]", rank_raw="[]",
        denied_raw="[]", mode_raw="shadow", web_host="github.example", api_base="https://api.github.example",
        bao_addr="", role_id="role", secret_id="secret", token_path="github-token/vikunja-triage", prepare_error="",
    )
    arguments.update(overrides)
    return namespace["main"](**arguments)


def test_guard_carries_the_prepare_fetch_error_forward():
    out = guard_main(namespace_for(VIKUNJA, "guard"), prepare_error="a Vikunja list call failed")
    assert out["actions"] == [] and out["fetch_error"] == "a Vikunja list call failed"


def test_a_model_reply_that_is_not_json_is_a_fetch_error_not_an_empty_digest():
    out = guard_main(namespace_for(VIKUNJA, "guard"), model_text="Here are my actions: none")
    assert out["actions"] == [] and out["fetch_error"] == "model reply was not JSON"


@pytest.mark.parametrize("reply", ["null", '{"actions": "none"}', '{"Actions": []}', "{}", "[]"])
def test_a_model_reply_of_the_wrong_shape_is_a_fetch_error(reply):
    out = guard_main(namespace_for(VIKUNJA, "guard"), model_text=reply)
    assert out["actions"] == [] and out["fetch_error"] == "model reply had the wrong shape"


def test_the_valid_empty_reply_has_no_actions_and_no_fetch_error():
    out = guard_main(namespace_for(VIKUNJA, "guard"), model_text='{"actions": []}')
    assert out["actions"] == [] and out["fetch_error"] == ""


def test_github_state_failure_is_reported_and_no_action_is_proposed():
    ref = {"task_index": 0, "id": "7", "project_id": "p1", "title": "fix https://github.example/acme/app/pull/12",
           "description": "", "priority": None, "labels": [], "done": False}
    out = guard_main(
        namespace_for(VIKUNJA, "guard"),
        model_text=json.dumps({"actions": [{"task_index": 0, "kind": "comment"}]}),
        refs_text=json.dumps([ref]),
    )
    assert out["actions"] == [] and out["fetch_error"] == "a GitHub state check failed"


def test_dispatch_write_is_unreachable_in_shadow_mode():
    dsl, nodes = committed("vikunja-triage")
    graph = dsl["workflow"]["graph"]
    edges = graph["edges"]
    starts = [node_id for node_id, data in nodes.items() if data["type"].startswith("trigger-") or data["type"] == "start"]
    children = {}
    for node in graph["nodes"]:  # iteration bodies are linked by parentId, not by edges
        if node.get("parentId"):
            children.setdefault(node["parentId"], []).append(node["id"])

    def reachable(skip):
        seen, frontier = set(), list(starts)
        while frontier:
            node_id = frontier.pop()
            if node_id in seen:
                continue
            seen.add(node_id)
            frontier += children.get(node_id, [])
            frontier += [edge["target"] for edge in edges
                         if edge["source"] == node_id and (node_id, edge.get("sourceHandle")) != skip]
        return seen

    assert "dispatch_write" in reachable(skip=None)
    assert "dispatch_write" not in reachable(skip=("mode_gate", "live"))
    assert {edge["sourceHandle"] for edge in edges if edge["target"] == "dispatch_loop"} == {"live"}
