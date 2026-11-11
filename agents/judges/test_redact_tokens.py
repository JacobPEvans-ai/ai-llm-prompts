"""The shared redaction rule removes token shapes and redacts hosts and addresses; strip_urls removes every link."""

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

LINKS = [
    "https://github.com/acme/app/pull/12",
    "https://internal.corp.example/x",
    "https://internal．corp．example/x",  # fullwidth full stop
    "https://internal。corp。example/x",  # ideographic full stop
    "https://intranet/x",
    "https://2130706433/x",
    "https://0x0a000001/x",
    "https://evil.md/x",
    "https://user@github.com/a/b",
    "https://github.com:8443/a/b",
    "http://github.com/a/b",
    "ftp://files.example/a?b=1",
    "https://[github.com/a/b",
]


@pytest.mark.parametrize("token", TOKENS)
def test_token_shapes_are_removed(token):
    out = REDACT.redact(f"deploy used {token} today")
    assert token not in out
    assert "[REDACTED]" in out


def test_secret_inside_a_link_is_removed_with_the_link():
    link = "https://github.com/acme/app/pull/12?token=" + "gh" + "p_abcdefghijklmnopqrstu"
    assert REDACT.strip_urls(REDACT.redact(link)) == "[link removed]"


@pytest.mark.parametrize("url", LINKS)
def test_every_scheme_url_is_replaced_whole(url):
    assert REDACT.strip_urls(url) == "[link removed]"


def test_github_is_not_special():
    assert REDACT.strip_urls("https://github.com/owner/repo/pull/12") == "[link removed]"


def test_a_url_inside_a_sentence_is_replaced_and_the_sentence_is_kept():
    assert REDACT.strip_urls("see https://evil.example/x for details") == "see [link removed] for details"


def test_the_placeholder_has_no_characters_that_could_form_a_link_or_a_control_sequence():
    assert not set(REDACT.LINK_REMOVED) & set("<>&:/")


def test_a_sentence_without_a_url_is_unchanged():
    text = "Review the open pull request before the release freeze."
    assert REDACT.strip_urls(text) == text
    assert REDACT.redact(text) == text


def test_shared_redact_still_redacts_hosts_in_non_url_text():
    assert REDACT.redact("the host internal.corp.example is down") == "the host [REDACTED] is down"


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
