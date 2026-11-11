"""No text reaches the channel that contains a clickable or previewable link to a host outside the allow-list, and no run that failed validation writes anything."""

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


def test_github_owner_repo_path_is_unchanged():
    assert REDACT.redact("https://github.com/owner/repo/pull/12") == "https://github.com/owner/repo/pull/12"


def test_secrets_inside_a_github_link_are_still_removed():
    link = "https://github.com/acme/app/pull/12?token=" + "gh" + "p_abcdefghijklmnopqrstu"
    assert REDACT.redact(link) == "https://github.com/acme/app/pull/12?token=[REDACTED]"


# A non-GitHub URL is replaced whole. The old rule redacted only its host, so these changed expectations are intended.
def test_other_hosts_are_replaced_whole():
    assert REDACT.redact("https://example.org/x") == "[REDACTED]"


@pytest.mark.parametrize(
    "url",
    [
        "https://internal%2Ecorp%2Eexample/x",
        "https://internal．corp．example/x",  # fullwidth full stop
        "https://internal。corp。example/x",  # ideographic full stop
        "https://intranet/x",
        "https://2130706433/x",
        "https://0x0a000001/x",
        "https://evil.md/x",
    ],
)
def test_non_github_urls_are_replaced_whole(url):
    assert REDACT.redact(url) == "[REDACTED]"


def test_a_url_inside_a_sentence_is_replaced_and_the_sentence_is_kept():
    assert REDACT.redact("see https://evil.example/x for details") == "see [REDACTED] for details"


def test_a_sentence_without_a_url_is_unchanged():
    text = "Review the open pull request before the release freeze."
    assert REDACT.redact(text) == text


@pytest.mark.parametrize(
    "url",
    [
        "https://user@github.com/a/b",
        "https://github.com:8443/a/b",
        "http://github.com/a/b",
        "https://github.com.evil.example/x",
        "https://[github.com/a/b",
    ],
)
def test_urls_that_fail_the_public_host_check_are_replaced_whole(url):
    assert REDACT.redact(url) == "[REDACTED]"


def test_the_public_host_is_compared_case_insensitively():
    assert REDACT.redact("https://GitHub.com/a/b") == "https://GitHub.com/a/b"


def test_github_exemption_ends_at_the_query_so_a_nested_internal_host_is_redacted():
    out = REDACT.redact("https://github.com/a/b?u=https://internal.corp.example/x")
    assert out == "https://github.com/a/b?u=[REDACTED]"


def test_github_exemption_ends_at_the_query_so_a_nested_address_is_redacted():
    out = REDACT.redact("https://github.com/a/b?next=https://10.1.2.3/admin")
    assert out == "https://github.com/a/b?next=[REDACTED]"


def test_github_exemption_ends_at_the_fragment_too():
    out = REDACT.redact("https://github.com/a/b#https://internal.corp.example/x")
    assert out == "https://github.com/a/b#[REDACTED]"


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
        ("https://github.com/a/b,https://internal.corp.example/x", "https://github.com/a/b,[REDACTED]"),
        ("https://github.com/a/b;https://internal.corp.example/x", "https://github.com/a/b;[REDACTED]"),
        ("https://github.com/a/b|https://10.1.2.3/x", "https://github.com/a/b|[REDACTED]"),
        ("https://github.com/a/b)https://internal.corp.example/x", "https://github.com/a/b)[REDACTED]"),
        ("https://github.com/a/b@10.1.2.3", "https://github.com/a/b@[REDACTED]"),
        ("https://github.com/@internal.corp.example/x", "https://github.com/@[REDACTED]/x"),
    ],
)
def test_github_exemption_stops_at_any_non_path_character(text, expected):
    assert REDACT.redact(text) == expected
