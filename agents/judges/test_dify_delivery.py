"""Slack thread delivery and failure notices: rendered into Dify Code nodes, then run offline against a fake Slack."""

import ast
import builtins
import datetime
import json
import re
import urllib.parse
import urllib.request
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
DIGEST, FAILURE = "C0DIGEST01", "C0FAILURE1"
NO_PREVIEW = {"unfurl_links": False, "unfurl_media": False, "parse": "none"}


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
    assert fake.posts(DIGEST)[0] == {"channel": DIGEST, "text": "sample digest 2026-11-10 (UTC)", **NO_PREVIEW}
    assert fake.posts(DIGEST)[1]["thread_ts"] == "200.0"


def test_first_run_of_the_day_creates_one_parent_then_replies(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack(history=[])
    namespace["call"] = fake
    run(namespace, {"text": "x"})
    parent, reply = fake.posts(DIGEST)
    assert parent == {"channel": DIGEST, "text": "sample digest 2026-11-10 (UTC)", **NO_PREVIEW}
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
        "sample failure: delivery failed at 2026-11-10 12:00 UTC. Dashboard: https://dashboard.example/agents"
    )
    assert not [post for post in fake.posts(DIGEST) if "failed" in post["text"]]


def prior_notice(ts):
    return {"bot_id": "B0BOT", "text": "sample failure: delivery failed at 2026-11-10 09:00 UTC.", "ts": str(ts)}


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


def test_another_integrations_message_with_the_agent_name_does_not_suppress(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    foreign = {"bot_id": "B0OTHER", "text": "sample deploy finished at 2026-11-10 09:00 UTC.", "ts": str(NOON_UTC - 3600)}
    fake = FakeSlack(channels={FAILURE: [[foreign]]},
                     fail=lambda method, channel: method == "chat.postMessage" and channel == DIGEST)
    namespace["call"] = fake
    with pytest.raises(RuntimeError, match="; failure notice failed$"):
        run(namespace, {"text": "x"})
    assert len(fake.posts(FAILURE)) == 1


def test_model_text_link_to_the_dashboard_is_replaced_in_the_digest(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack()
    namespace["call"] = fake
    run(namespace, {"text": "see https://dashboard.example/agents"})
    assert fake.posts(DIGEST)[-1]["text"] == "see [REDACTED]"


def test_template_built_dashboard_link_is_kept_in_the_failure_notice(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack(fail=lambda method, channel: method == "chat.postMessage" and channel == DIGEST)
    namespace["call"] = fake
    with pytest.raises(RuntimeError, match="; failure notice failed$"):
        run(namespace, {"text": "see https://dashboard.example/agents"})
    assert "Dashboard: https://dashboard.example/agents" in fake.posts(FAILURE)[0]["text"]


def test_failure_reason_is_redacted_while_the_dashboard_link_is_kept(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack()
    namespace["call"] = fake
    stamp = datetime.datetime.fromtimestamp(NOON_UTC, datetime.timezone.utc)
    namespace["notify_failure"](
        "https://slack.example/api", "token", FAILURE, DIGEST, "https://dashboard.example/agents", stamp,
        "fetch failed: see https://internal.corp.example/x",
    )
    assert fake.posts(FAILURE)[0]["text"] == (
        "sample failure: fetch failed: see [REDACTED] at 2026-11-10 12:00 UTC. Dashboard: https://dashboard.example/agents"
    )


def test_model_label_link_is_escaped_so_it_cannot_hide_its_target(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack()
    namespace["call"] = fake
    run(namespace, {"text": "<https://internal.corp.example|click>"})
    assert fake.posts(DIGEST)[-1]["text"] == "&lt;[REDACTED]&gt;"


def test_posted_digest_links_stay_on_github_however_the_clip_falls(tmp_path):
    """Property: for bodies with allowed and disallowed links at every offset near the limit, no posted link leaves github.com."""
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    limit = namespace["MAX_CHARS"]
    urls = [
        "https://github.com/acme/app/pull/12 (state: open).",
        "https://internal.corp.example/x",
        "https://github.com.evil.example/x",
        "https://user@github.com/x",
    ]
    for url in urls:
        for offset in range(limit - 80, limit + 6):  # a cut inside the link happens at most of these offsets
            fake = FakeSlack()
            namespace["call"] = fake
            run(namespace, {"text": " " * offset + "Linked GitHub work: " + url})
            posted = fake.posts(DIGEST)[-1]["text"]
            assert len(posted) <= limit, (offset, url)
            for found in re.finditer(r"[A-Za-z][A-Za-z0-9+.-]*://\S*", posted):
                parts = urllib.parse.urlsplit(found.group(0))
                assert parts.netloc == "github.com" and parts.hostname == "github.com", (offset, url, posted)


def test_every_post_turns_off_link_previews(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    posted = FakeSlack()
    namespace["call"] = posted
    run(namespace, {"text": "x"})  # parent and reply
    failing = FakeSlack(fail=lambda method, channel: method == "chat.postMessage" and channel == DIGEST)
    namespace["call"] = failing
    with pytest.raises(RuntimeError):
        run(namespace, {"text": "x"})  # the failed parent post, then the failure notice
    sent = posted.posts() + failing.posts()
    assert len(sent) == 4
    assert all(args["unfurl_links"] is False and args["unfurl_media"] is False and args["parse"] == "none" for args in sent)


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
    assert fake.posts(FAILURE)[0]["text"].startswith("sample failure: run failed at 2026-11-10 12:00 UTC")
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
        "&lt;!channel&gt; &lt;!here&gt; &lt;@UEXAMPLE&gt; &lt;[REDACTED]&gt; a &amp; b"
    )


def test_truncation_never_splits_an_escaped_entity(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    fake = FakeSlack()
    namespace["call"] = fake
    run(namespace, {"text": "<" * 5000})
    reply = fake.posts(DIGEST)[-1]["text"]
    assert 2900 < len(reply) <= 3000 and reply.endswith("\n[truncated]")  # escaping follows the cut, so not exactly 3000
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
        "sample failure: delivery failed at 2026-11-10 12:00 UTC. Dashboard: https://dashboard.example/agents",
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
    assert fake.posts(DIGEST) == [{"channel": DIGEST, "thread_ts": "111.1", "text": "x", **NO_PREVIEW}]


def test_parent_absent_from_every_page_is_created_once(tmp_path):
    namespace = namespace_for(render_sample(tmp_path), "deliver-done")
    other = {"ts": "50.0", "text": "unrelated", "bot_id": "B2"}
    fake = FakeSlack(pages=[[other], [other]])
    namespace["call"] = fake
    run(namespace, {"text": "x"})
    assert [method for method, _ in fake.calls].count("conversations.history") == 2
    assert fake.posts(DIGEST) == [
        {"channel": DIGEST, "text": "sample digest 2026-11-10 (UTC)", **NO_PREVIEW},
        {"channel": DIGEST, "thread_ts": "200.0", "text": "x", **NO_PREVIEW},
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

    bodies = []

    def fake_urlopen(request, timeout):
        sent.append((request.full_url, request.get_header("Authorization")))
        if request.data:
            bodies.append(json.loads(request.data))
        if "conversations.history" in request.full_url:
            return Response({"ok": True, "messages": []})
        return Response({"ok": True, "ts": "200.0"})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert run(namespace, {"text": "x"}, api_base="https://slack.com/api", bot_token="token") == {"status": "posted"}
    assert all(url.startswith("https://slack.com/api/") for url, _ in sent)
    assert {auth for _, auth in sent} == {"Bearer token"}
    posts = [body for body in bodies if "text" in body]
    assert len(posts) == 2 and all(
        body["unfurl_links"] is False and body["unfurl_media"] is False and body["parse"] == "none" for body in posts
    )


def test_delivery_status_is_reported_on_each_end_node(tmp_path):
    _, nodes = load(render_sample(tmp_path))
    assert {"variable": "delivery_status", "value_selector": ["deliver-done", "status"]} in nodes["done"]["outputs"]


def test_fetch_error_input_is_declared_only_when_error_from_is_set(tmp_path):
    _, plain = load(render_sample(tmp_path / "plain", delivery=DELIVERY))
    assert not [variable for variable in plain["deliver-done"]["variables"] if variable["variable"] == "fetch_error"]
    _, declared = load(render_sample(tmp_path / "declared", delivery={**DELIVERY, "error_from": ["start", "text"]}))
    assert {"variable": "fetch_error", "value_selector": ["start", "text"]} in declared["deliver-done"]["variables"]
