import ipaddress
import re

# The one redaction rule. The finder validator applies it to each quote and to the cited page text before the verbatim
# check, so a quote that the prompt redacted still matches its page. A credential keeps its label and loses its value.
SECRET_RE = re.compile(
    r"(?i)(?:(?P<label>(?:api[_-]?key|secret|token)\s*[:=]\s*['\"]?)[A-Za-z0-9_./+=-]{24,}"
    r"|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|github_pat_[A-Za-z0-9_]{30,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})"
)
HOST_RE = re.compile(r"(?i)\b(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,63}\b")
FILE_EXTENSIONS = {"md", "py", "ts", "tsx", "js", "jsx", "json", "yaml", "yml", "toml", "txt", "html", "css"}
# md and py are also country-code TLDs, so only a two-label name such as README.md stays a file reference.
# shortcut: a two-label host under .md or .py (corp.md) stays unredacted; upgrade to a page-path allowlist if one appears.
CCTLD_EXTENSIONS = {"md", "py"}
IPV4_RE = re.compile(r"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")
IPV6_RE = re.compile(r"(?<![A-Fa-f0-9:])[A-Fa-f0-9:]{2,}(?![A-Fa-f0-9:])")
REDACTED = "[REDACTED]"


def _is_address(candidate):
    try:
        ipaddress.ip_address(candidate)
        return True
    except ValueError:
        return False


def _redact_ipv6(match):
    candidate = match.group(0)
    if ":" not in candidate:
        return candidate
    # Prose can touch an address on either side ("Peer:2001:db8::1", "2001:db8::: is down", "ab2001:db8::1"); try every
    # span, longest first from the leftmost start, and keep what surrounds the address outside the redaction.
    for start in range(len(candidate)):
        for end in range(len(candidate), start + 1, -1):
            span = candidate[start:end]
            if ":" in span and _is_address(span):
                return candidate[:start] + REDACTED + _redact_ipv6_text(candidate[end:])
    return candidate


def _redact_ipv6_text(text):
    return IPV6_RE.sub(_redact_ipv6, text) if text else text


def _redact_host(match):
    name = match.group(0)
    labels = name.lower().split(".")
    if labels[-1] in FILE_EXTENSIONS and (labels[-1] not in CCTLD_EXTENSIONS or len(labels) == 2):
        return name
    return REDACTED


def redact(text):
    text = SECRET_RE.sub(lambda match: (match.group("label") or "") + REDACTED, text)
    text = IPV4_RE.sub(lambda match: REDACTED if _is_address(match.group(0)) else match.group(0), text)
    text = IPV6_RE.sub(_redact_ipv6, text)
    return HOST_RE.sub(_redact_host, text)


def needs_redaction(text):
    return REDACTED in text or redact(text) != text
