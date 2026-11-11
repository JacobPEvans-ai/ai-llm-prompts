import ipaddress
import re

# The one redaction rule. The finder validator applies it to each quote and to the cited page text before the verbatim
# check, so a quote that the prompt redacted still matches its page. A credential keeps its label and loses its value.
SECRET_RE = re.compile(
    r"(?i)(?:(?P<label>(?:api[_-]?key|secret|token)\s*[:=]\s*['\"]?)[A-Za-z0-9_./+=-]{24,}"
    r"|(?P<bearer>\bBearer\s+)(?:(?=[A-Za-z0-9._~+/=-]*[0-9])[A-Za-z0-9._~+/=-]{16,}|[A-Za-z0-9._~+/=-]{24,})"
    r"|xox[abposr]-[A-Za-z0-9-]{10,}|\bhv[sbr]\.[A-Za-z0-9_-]{20,}"
    r"|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|github_pat_[A-Za-z0-9_]{30,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})"
)
# Every scheme:// URL runs to whitespace or one of <>"'. Agent and fetched text never keeps one: strip_urls replaces each
# with LINK_REMOVED. The template builds the only links, from validated ids, outside this rule.
URL_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^\s<>\"']*")
LINK_REMOVED = "[link removed]"
SECRET_KEY_SEGMENTS = {"token", "authorization", "password", "secret", "cookie", "apikey"}
HOST_RE = re.compile(r"(?i)\b(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,63}\b")
FILE_EXTENSIONS = {"md", "py", "ts", "tsx", "js", "jsx", "json", "yaml", "yml", "toml", "txt", "html", "css"}
# md and py are also country-code TLDs, so two-label matches may be file references rather than hosts.
# shortcut: keep that exception until a collision calls for a page-path allowlist.
CCTLD_EXTENSIONS = {"md", "py"}
IPV4_RE = re.compile(r"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")
IPV6_RE = re.compile(r"(?<![A-Fa-f0-9:])[A-Fa-f0-9:]{2,}(?![A-Fa-f0-9:])")
REDACTED = "[REDACTED]"
MAX_IPV6_LEN = 45  # longest textual IPv6 form (IPv4-mapped, no zone)


def _is_address(candidate):
    if IPV4_RE.fullmatch(candidate):
        # ipaddress rejects leading zeros, so read each octet as decimal first.
        candidate = ".".join(str(int(octet)) for octet in candidate.split("."))
    try:
        ipaddress.ip_address(candidate)
        return True
    except ValueError:
        return False


def _redact_ipv6(match):
    candidate = match.group(0)
    if ":" not in candidate:
        return candidate
    # Prose can touch an address on either side ("Peer:2001:db8::1", "2001:db8::: is down", "ab2001:db8::1"); scan the
    # run left to right, redact the longest address at the leftmost start, and keep the text around it.
    parts, pos = [], 0
    while pos < len(candidate):
        span = _first_address_span(candidate, pos)
        if span is None:
            break
        parts += [candidate[pos : span[0]], REDACTED]
        pos = span[1]
    return "".join(parts) + candidate[pos:]


def _first_address_span(candidate, pos):
    for start in range(pos, len(candidate)):
        for end in range(min(len(candidate), start + MAX_IPV6_LEN), start + 1, -1):
            span = candidate[start:end]
            if ":" in span and _is_address(span):
                return start, end
    return None


def _redact_host(match):
    name = match.group(0)
    labels = name.lower().split(".")
    if labels[-1] in FILE_EXTENSIONS and (labels[-1] not in CCTLD_EXTENSIONS or len(labels) == 2):
        return name
    return REDACTED


def _is_secret_key(key):
    compact = re.sub(r"[^a-z0-9]", "", key.lower())
    if any(word in compact for word in ("password", "secret", "authorization", "cookie", "apikey")) or compact.endswith("token"):
        return True
    # Keep case-insensitive words as well as camelCase segments (for example, ToKeN).
    words = re.split(r"[^a-z0-9]+", key.lower())
    key = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", key)
    key = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key)
    segments = re.split(r"[^a-z0-9]+", key.lower())
    return any(segment in SECRET_KEY_SEGMENTS for segment in words + segments) or any(
        left == "api" and right == "key" for left, right in zip(segments, segments[1:])
    )


def _redact_secrets(text):
    return SECRET_RE.sub(lambda match: (match.group("label") or match.group("bearer") or "") + REDACTED, text)


def _redact_plain(text):
    text = _redact_secrets(text)
    text = IPV4_RE.sub(lambda match: REDACTED if _is_address(match.group(0)) else match.group(0), text)
    text = IPV6_RE.sub(_redact_ipv6, text)
    return HOST_RE.sub(_redact_host, text)


def strip_urls(text):
    return URL_RE.sub(LINK_REMOVED, text)


def redact(text):
    if isinstance(text, dict):
        return {key: REDACTED if _is_secret_key(key) else redact(value) for key, value in text.items()}
    if isinstance(text, list):
        return [redact(value) for value in text]
    if not isinstance(text, str):
        return text
    return _redact_plain(text)


def needs_redaction(text):
    return REDACTED in text or redact(text) != text
