"""The shared redaction rule removes token shapes, keeps public GitHub links, and still redacts other hosts."""

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("redact", ROOT / "agents/dify-src/helpers/redact.py")
REDACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REDACT)

# Token-shaped fixtures are assembled from parts, so no credential-shaped literal is written to the file.
TOKENS = [
    "xox" + "b-1234567890-abcdefghijk",
    "xox" + "p-1234567890-abcdefghijk",
    "hv" + "s.CAESIJabcdefghijklmnopqrstuvwxyz0123",
    "hv" + "b.CAESIJabcdefghijklmnopqrstuvwxyz0123",
    "Bearer " + "abcdefghijklmnopqrstuvwx",
]


@pytest.mark.parametrize("token", TOKENS)
def test_token_shapes_are_removed(token):
    out = REDACT.redact(f"deploy used {token} today")
    assert token not in out
    assert "[REDACTED]" in out


def test_public_github_links_keep_host_and_path():
    text = "see https://github.com/acme/app/pull/12 for context"
    assert REDACT.redact(text) == text


def test_secrets_inside_a_github_link_are_still_removed():
    link = "https://github.com/acme/app/pull/12?token=" + "gh" + "p_abcdefghijklmnopqrstu"
    assert REDACT.redact(link) == "https://github.com/acme/app/pull/12?token=[REDACTED]"


def test_other_hosts_are_still_redacted():
    assert REDACT.redact("https://example.org/x") == "https://[REDACTED]/x"
