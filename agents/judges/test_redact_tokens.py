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


def test_github_exemption_ends_at_the_query_so_a_nested_internal_host_is_redacted():
    out = REDACT.redact("https://github.com/a/b?u=https://internal.corp.example/x")
    assert out == "https://github.com/a/b?u=https://[REDACTED]/x"


def test_github_exemption_ends_at_the_query_so_a_nested_address_is_redacted():
    out = REDACT.redact("https://github.com/a/b?next=https://10.1.2.3/admin")
    assert out == "https://github.com/a/b?next=https://[REDACTED]/admin"


def test_github_exemption_ends_at_the_fragment_too():
    out = REDACT.redact("https://github.com/a/b#https://internal.corp.example/x")
    assert out == "https://github.com/a/b#https://[REDACTED]/x"


def test_bearer_prose_is_not_redacted():
    text = "the bearer responsibilities are listed below"
    assert REDACT.redact(text) == text


def test_bearer_prose_with_a_sentence_final_dot_is_not_redacted():
    text = "the bearer responsibilities."
    assert REDACT.redact(text) == text


def test_short_bearer_value_with_a_digit_is_still_redacted():
    token = "Bearer " + "abcdefgh" + "12345678"
    out = REDACT.redact(f"auth {token} ok")
    assert token not in out
    assert out == "auth Bearer [REDACTED] ok"


@pytest.mark.parametrize(
    "text, expected",
    [
        ("https://github.com/a/b,https://internal.corp.example/x", "https://github.com/a/b,https://[REDACTED]/x"),
        ("https://github.com/a/b;https://internal.corp.example/x", "https://github.com/a/b;https://[REDACTED]/x"),
        ("https://github.com/a/b|https://10.1.2.3/x", "https://github.com/a/b|https://[REDACTED]/x"),
        ("https://github.com/a/b)https://internal.corp.example/x", "https://github.com/a/b)https://[REDACTED]/x"),
        ("https://github.com/a/b@10.1.2.3", "https://github.com/a/b@[REDACTED]"),
        ("https://github.com/@internal.corp.example/x", "https://github.com/@[REDACTED]/x"),
    ],
)
def test_github_exemption_stops_at_any_non_path_character(text, expected):
    assert REDACT.redact(text) == expected
