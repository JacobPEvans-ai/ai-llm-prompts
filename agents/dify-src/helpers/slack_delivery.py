"""Slack thread delivery for rendered Dify Code nodes.

The node defines AGENT before it includes this text. The functions read only AGENT and their arguments, and keep no
state between runs. Summary text is built by the delivery node, which owns the redaction and truncation limits.
"""

import datetime
import json
import urllib.parse
import urllib.request


def call(api, token, method, payload=None, query=None):
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
    """Return the ts of this agent's parent post for the day, or None. Reads at most three history pages."""
    cursor = None
    for _ in range(3):
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
            break
    return None


def notify_failure(api, token, failure_channel, digest_channel, dashboard_url, stamp, reason):
    """Post one failure line. Never posts to the digest channel. Returns failed-unreported when it cannot."""
    if not failure_channel or failure_channel == digest_channel:
        return "failed-unreported"
    text = AGENT + " " + reason + " at " + stamp.strftime("%Y-%m-%d %H:%M") + " UTC. Dashboard: " + dashboard_url
    try:
        call(api, token, "chat.postMessage", {"channel": failure_channel, "text": text})
    except Exception:
        return "failed-unreported"
    return "failed"


def post_digest(api, token, channel, failure_channel, dashboard_url, stamp, body):
    """Post body as a reply in today's parent thread. Returns posted, or a failure status after a notice."""
    day = stamp.strftime("%Y-%m-%d")
    parent = AGENT + " digest " + day + " (UTC)"
    try:
        ts = parent_ts(api, token, channel, parent, day_start(stamp) - 1)
        if ts is None:
            ts = call(api, token, "chat.postMessage", {"channel": channel, "text": parent})["ts"]
        call(api, token, "chat.postMessage", {"channel": channel, "thread_ts": ts, "text": body})
    except Exception:
        return notify_failure(api, token, failure_channel, channel, dashboard_url, stamp, "delivery failed")
    return "posted"
