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
IPV4_RE = re.compile(r"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")
IPV6_RE = re.compile(r"(?<![A-Fa-f0-9:])[A-Fa-f0-9:]{2,}(?![A-Fa-f0-9:])")
REDACTED = "[REDACTED]"


def _is_address(candidate):
    try:
        ipaddress.ip_address(candidate)
        return True
    except ValueError:
        return False


def redact(text):
    text = SECRET_RE.sub(lambda match: (match.group("label") or "") + REDACTED, text)
    text = IPV4_RE.sub(lambda match: REDACTED if _is_address(match.group(0)) else match.group(0), text)
    text = IPV6_RE.sub(lambda match: REDACTED if ":" in match.group(0) and _is_address(match.group(0)) else match.group(0), text)
    return HOST_RE.sub(lambda match: match.group(0) if match.group(0).rsplit(".", 1)[-1].lower() in FILE_EXTENSIONS else REDACTED, text)


def needs_redaction(text):
    return REDACTED in text or redact(text) != text
