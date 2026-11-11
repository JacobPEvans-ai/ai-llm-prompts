"""Slack thread delivery for rendered Dify Code nodes.

The node defines AGENT and TRUSTED_SLACK_HOSTS before it includes this text. The functions read only those names and
their arguments, and keep no state between runs. Every failure sends at most one notice per 24 hours, then raises,
so the Dify run ends failed. Summary text is built by the delivery node, which owns redaction and truncation.
"""

import datetime
import json
import re
import urllib.parse
import urllib.request

CHANNEL_ID = re.compile(r"[CGD][A-Z0-9]+")


def call(api, token, method, payload=None, query=None):
    parts = urllib.parse.urlsplit(api)
    if parts.scheme != "https" or parts.hostname not in TRUSTED_SLACK_HOSTS:
        raise RuntimeError("slack api base is not an approved https host")
    url = api.rstrip("/") + "/" + method
    if query:
        url += "?" + urllib.parse.urlencode(query)
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"Authorization": "Bearer " + token}
    if payload is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(request, timeout=5) as response:
        body = json.loads(response.read())
    if not body.get("ok"):
        raise RuntimeError(method + " failed: " + str(body.get("error", "unknown")))
    return body


def valid_channel(value):
    """Channel IDs only. A name such as #general would not reliably identify the channel at run time."""
    return isinstance(value, str) and CHANNEL_ID.fullmatch(value) is not None


def escape_mrkdwn(text):
    """Escape the three characters Slack reads as markup, so model or task text cannot mention, link, or broadcast."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fetched(value):
    """True when the run fetched any input. An empty list, object, or string is a heartbeat."""
    if isinstance(value, str):
        if not value.strip():
            return False
        try:
            value = json.loads(value)
        except ValueError:
            return True
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return value is not None


def day_start(stamp):
    return int(datetime.datetime(stamp.year, stamp.month, stamp.day, tzinfo=datetime.timezone.utc).timestamp())


def parent_ts(api, token, channel, text, since):
    """Return the ts of this agent's parent post for the day, or None. Follows the history cursor until found or done."""
    cursor = None
    while True:
        query = {"channel": channel, "oldest": str(since), "limit": 200}
        if cursor:
            query["cursor"] = cursor
        body = call(api, token, "conversations.history", query=query)
        for message in body.get("messages", []):
            is_parent = message.get("thread_ts", message.get("ts")) == message.get("ts")
            if message.get("bot_id") and message.get("text") == text and is_parent:
                return message["ts"]
        cursor = (body.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            return None


def recently_notified(api, token, failure_channel, stamp):
    """True when this agent's notice is in the failure channel from the last 24 hours. One bounded read, no paging."""
    since = int(stamp.timestamp()) - 86400
    query = {"channel": failure_channel, "oldest": str(since), "limit": 200}
    body = call(api, token, "conversations.history", query=query)
    prefix = escape_mrkdwn(AGENT) + " "
    return any(
        message.get("bot_id") and message.get("text", "").startswith(prefix) and float(message.get("ts", 0)) >= since
        for message in body.get("messages", [])
    )


def notify_failure(api, token, failure_channel, digest_channel, dashboard_url, stamp, reason):
    """Post at most one failure line per 24 hours. Returns failed, suppressed, or failed-unreported."""
    if not valid_channel(failure_channel) or failure_channel == digest_channel:
        return "failed-unreported"
    try:
        if recently_notified(api, token, failure_channel, stamp):
            return "suppressed (already notified)"
    except Exception:
        pass  # an unreadable history must not hide the notice, so post anyway
    text = escape_mrkdwn(
        AGENT + " " + reason + " at " + stamp.strftime("%Y-%m-%d %H:%M") + " UTC. Dashboard: " + dashboard_url
    )
    try:
        call(api, token, "chat.postMessage", {"channel": failure_channel, "text": text})
    except Exception:
        return "failed-unreported"
    return "failed"


def fail(api, token, failure_channel, digest_channel, dashboard_url, stamp, reason):
    """Send the failure notice, then raise so the Dify run ends failed. The message names no secret or response body."""
    status = notify_failure(api, token, failure_channel, digest_channel, dashboard_url, stamp, reason)
    raise RuntimeError(reason + "; failure notice " + status) from None


def post_digest(api, token, channel, failure_channel, dashboard_url, stamp, body):
    """Post body as a reply in today's parent thread. Raises, after a failure notice, when any step fails."""
    day = stamp.strftime("%Y-%m-%d")
    parent = AGENT + " digest " + day + " (UTC)"
    try:
        if not valid_channel(channel):
            raise ValueError("digest channel is not a channel ID")
        ts = parent_ts(api, token, channel, parent, day_start(stamp) - 1)
        if ts is None:
            ts = call(api, token, "chat.postMessage", {"channel": channel, "text": parent})["ts"]
        call(api, token, "chat.postMessage", {"channel": channel, "thread_ts": ts, "text": body})
    except Exception:
        fail(api, token, failure_channel, channel, dashboard_url, stamp, "delivery failed")
    return "posted"
