"""The issue-linker prompt lists open issues instead of calling the search API."""

from pathlib import Path


_ROOT = Path(__file__).resolve().parents[2]
_PROMPT = (_ROOT / "automation" / "ai-workflows-issue-linker.md").read_text()
_LIST_COMMAND = "`gh issue list --state open --limit 200 --json number,title,body,labels`"


def test_issue_linker_prompt_lists_open_issues_without_search_commands():
    assert _LIST_COMMAND in _PROMPT
    search_lines = [
        line for line in _PROMPT.splitlines()
        if "gh search" in line or "--search" in line
    ]
    assert len(search_lines) == 1, search_lines
    assert "denied" in search_lines[0], search_lines
