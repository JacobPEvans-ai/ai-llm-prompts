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


def test_the_scheme_list_is_the_owner_list():
    assert REDACT.SCHEMES == (
        "http", "https", "ftp", "ftps", "ws", "wss", "file", "ssh", "git", "slack", "mailto", "tel", "data", "javascript",
    )


@pytest.mark.parametrize(
    "link",
    ["https:/intranet/x", "https:\\\\intranet/x", "https:\\intranet/x", "https:intranet/x", "HTTPS:intranet/x",
     "mailto:ops@intranet.example", "javascript:alert(1)", "data:text/plain,hello"],
)
def test_slashless_and_backslash_forms_of_a_known_scheme_are_replaced(link):
    assert REDACT.strip_urls(link) == "[link removed]"


@pytest.mark.parametrize("text", ["note: x", "time: 10:30", "key: value", "C:\\Users\\me\\file.txt", "data: value"])
def test_ordinary_prose_and_windows_paths_are_not_schemes(text):
    assert REDACT.strip_urls(text) == text


def test_bearer_label_without_a_leading_word_boundary_is_redacted():
    assert REDACT.redact("xBearer abcdefgh12345678ijklmnop") == "xBearer [REDACTED]"


def test_a_link_that_carries_a_bearer_value_loses_the_value_too():
    text = "https://intranet/xBearer abcdefgh12345678ijklmnop"
    assert REDACT.strip_urls(REDACT.redact(text)) == "[link removed] [REDACTED]"


def test_api_key_label_without_a_leading_word_boundary_is_redacted():
    assert REDACT.redact("xapi_key=" + "A" * 40) == "xapi_key=[REDACTED]"


def test_zero_width_characters_cannot_split_a_token():
    token = "gh" + "p_" + "Ab3" * 8
    split = "\u200b".join(token)
    assert REDACT.strip_invisible(split) == token
    assert REDACT.redact(REDACT.strip_invisible(split)) == "[REDACTED]"


class KnownLimits:
    """Documented gaps in the redactor. The upstream control is that fetched input is redacted before it reaches the model."""

    def test_a_token_with_a_space_every_six_characters_passes_through_unchanged(self):
        token = "gh" + "p_" + "Ab3" * 8
        spaced = " ".join(token[i : i + 6] for i in range(0, len(token), 6))
        assert REDACT.redact(spaced) == spaced

    def test_an_api_key_value_split_by_spaces_passes_through_unchanged(self):
        text = "api_key=" + " ".join(["A" * 6] * 5)
        assert REDACT.redact(text) == text

    @pytest.mark.parametrize(
        "text",
        ["password=" + "Xk9Lm2Pq7Rs4Tv8Wy1Zb3Cd5", "password: " + "Xk9Lm2Pq7Rs4Tv8Wy1Zb3Cd5",
         "secret_key=" + "Xk9Lm2Pq7Rs4Tv8Wy1Zb3Cd5"],
    )
    def test_labels_the_redactor_does_not_know_pass_through_unchanged(self, text):
        assert REDACT.redact(text) == text
