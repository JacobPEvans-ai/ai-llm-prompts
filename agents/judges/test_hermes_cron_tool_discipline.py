"""Hermes cron tool discipline is defined once, in the shared Hermes surface."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
SURFACE = ROOT / "auto-ai-agent" / "hermes.md"
RULE_HEADING = "Cron tool discipline:"
RULE_MARKERS = ("per-run file", "read it in full first")
# Cron runs have no user to approve the terminal tool's dangerous-command guard,
# so an inline interpreter call via -c/-e is refused; the surface names the flags
# to forbid and every cron prompt must stay off them.
INLINE_SCRIPT = re.compile(
    r"\b(?:python3?|bash|sh|zsh|ksh|dash|node|deno|bun|perl|ruby|pwsh|powershell)\s+-[ce]\b"
)


def hermes_prompt_files():
    catalog = ROOT / "auto-ai-agent"
    return sorted({*catalog.glob("hermes-*.md"), *catalog.glob("hermes-*/*.md")})


def surface_body():
    opening, metadata, body = SURFACE.read_text().split("---\n", 2)
    assert opening == "", "surface must open with YAML frontmatter"
    return body


def test_surface_carries_each_cron_tool_rule_clause_once():
    body = surface_body()
    assert body.count(RULE_HEADING) == 1, "the cron tool rule is stated once"
    for marker in RULE_MARKERS:
        assert marker in body, marker


def test_no_hermes_prompt_instructs_an_inline_script():
    for path in hermes_prompt_files():
        if path == SURFACE:
            continue
        found = [match.group(0) for match in INLINE_SCRIPT.finditer(path.read_text())]
        assert not found, f"{path.relative_to(ROOT)} instructs inline script execution: {found}"


def test_no_hermes_prompt_restates_the_cron_tool_rule():
    for path in hermes_prompt_files():
        if path == SURFACE:
            continue
        carried = [marker for marker in RULE_MARKERS if marker in path.read_text()]
        assert not carried, f"{path.relative_to(ROOT)} restates the shared cron tool rule: {carried}"


def test_inline_script_pattern_catches_the_guarded_forms():
    for text in (
        "run python -c 'print(1)'",
        "use python3 -c \"import sys\" to parse it",
        "call bash -c 'ls'",
        "via `sh -c` here",
        "node -e 'process.exit(1)'",
    ):
        assert INLINE_SCRIPT.search(text), text


def test_inline_script_pattern_ignores_non_script_flags():
    for text in ("sort -count | head 30", "earliest=-2h", "curl -sS -m 8 -o /dev/null", "state_id 6 pending_time"):
        assert not INLINE_SCRIPT.search(text), text


# The assistant's attention jobs run with no scripts at all, and a quiet run
# logs one line of reason before its [SILENT] marker.
NO_SCRIPT_PROMPTS = ("hermes-assistant-pulse.md", "hermes-assistant-nudge.md")


def test_assistant_attention_prompts_forbid_scripts_and_explain_silence():
    for name in NO_SCRIPT_PROMPTS:
        text = (ROOT / "auto-ai-agent" / name).read_text()
        flat = " ".join(text.split())
        for clause in (
            "Use only the tools this job grants you.",
            "Never write, save or run a script",
            "never create a scratch file",
            "your whole reply is one line",
            "any check you skipped",
            "name it inside the one line",
            "End that line with the bare marker [SILENT], with nothing after it",
        ):
            assert clause in flat, f"{name} lacks: {clause}"
        assert "exactly [SILENT] and nothing else" not in flat, name
        assert re.search(r"^Checked [^\n`]+\. \[SILENT\]$", text, re.M), f"{name} shows a reasoned [SILENT] line"
