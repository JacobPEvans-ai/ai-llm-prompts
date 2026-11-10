"""The secrets audit takes its skip list at render time and stops when it is empty."""

from pathlib import Path

PROMPT = Path(__file__).resolve().parents[2] / "auto-ai-agent" / "hermes-secrets-policy-audit.md"
VARIABLE = "hermes_agent_secrets_audit_skip_repos"
FAIL_CLOSED = (
    "If the skip list above is empty, scan nothing. Say in one sentence that the skip list "
    "is missing, then stop. This check comes after the token check: a missing token still means [SILENT]."
)


def _parts():
    _, head, body = PROMPT.read_text().split("---\n", 2)
    return head, body


def test_prompt_declares_its_skip_list_variable():
    head, _ = _parts()
    assert "engine: jinja2" in head
    assert f"- {VARIABLE}" in head


def test_skip_list_is_rendered_before_the_stop_rule():
    _, body = _parts()
    placeholder = "{{ " + VARIABLE + " | default('', true) | trim }}"
    assert body.count(placeholder) == 1
    assert body.index(placeholder) < body.index(FAIL_CLOSED)


def test_repo_skip_line_points_only_at_the_rendered_list():
    _, body = _parts()
    assert "- Entire repos: every repository or name pattern in the skip list below." in body
    assert "operator skip-list" not in body
