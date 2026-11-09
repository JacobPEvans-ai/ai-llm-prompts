"""Hermes report status levels are defined once, in the shared clause file."""

from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parents[2]
LEVELS = ROOT / "auto-ai-agent" / "hermes-reporting" / "status-levels.md"
EXPECTED = {
    "green": ("🟢", ":large_green_circle:", "healthy, no action"),
    "yellow": ("🟡", ":large_yellow_circle:", "degraded, unverified, flapping or above baseline; look when convenient"),
    "red": ("🔴", ":red_circle:", "failing or down; act now"),
}
RULE = "a report starts with exactly one marker, the worst level that applies"
FORBIDDEN = (":warning:", ":rotating_light:", ":white_check_mark:")
MARKERS = tuple(marker for triple in EXPECTED.values() for marker in triple[:2]) + FORBIDDEN
HEADLINE_LEVEL_PREFIX = "HEADLINE LEVEL:"
FOOTERS = (
    ROOT / "auto-ai-agent" / "hermes-direct-cron-footer.md",
    ROOT / "auto-ai-agent" / "hermes-direct-cron-footer-quiet.md",
)
# Prompts assembled without either direct-cron footer may state the markers
# inline themselves; none do today.
NON_FOOTER_EXCEPTIONS: tuple[Path, ...] = ()


def level_contract():
    opening, metadata, body = LEVELS.read_text().split("---\n", 2)
    assert opening == "", "file must open with YAML frontmatter"
    block = re.search(r"```yaml\n(.*?)```", body, re.DOTALL)
    assert block, "machine-readable status level block required"
    return yaml.safe_load(metadata), yaml.safe_load(block.group(1))


def hermes_prompt_files():
    catalog = ROOT / "auto-ai-agent"
    return sorted({*catalog.glob("hermes-*.md"), *catalog.glob("hermes-*/*.md")})


def test_status_levels_is_a_shared_fragment():
    frontmatter, _ = level_contract()
    assert frontmatter["type"] == "LLM Prompt Fragment"
    assert frontmatter["resource"] == "prompt://dryvist/auto-ai-agent/hermes-reporting/status-levels"
    assert frontmatter["render"]["frontmatter"] == "strip"


def test_status_levels_define_exactly_three_levels_machine_readably():
    _, contract = level_contract()
    levels = contract["status_levels"]
    assert set(levels) == set(EXPECTED) | {"rule", "forbidden_state_markers"}
    for name, (emoji, shortcode, meaning) in EXPECTED.items():
        assert levels[name]["emoji"] == emoji, name
        assert levels[name]["slack_shortcode"] == shortcode, name
        assert levels[name]["meaning"] == meaning, name
    assert levels["rule"] == RULE
    assert tuple(levels["forbidden_state_markers"]) == FORBIDDEN


def test_no_hermes_prompt_carries_a_status_marker_outside_status_levels():
    for path in hermes_prompt_files():
        if path == LEVELS or path in FOOTERS:
            continue
        found = [marker for marker in MARKERS if marker in path.read_text()]
        assert not found, f"{path.relative_to(ROOT)} carries {found}"


def test_headline_level_requirement_is_stated_once_in_the_cron_footers():
    allowed = {LEVELS, *FOOTERS, *NON_FOOTER_EXCEPTIONS}
    for path in hermes_prompt_files():
        if path in allowed:
            continue
        carried = [line for line in path.read_text().splitlines() if line.startswith(HEADLINE_LEVEL_PREFIX)]
        assert not carried, f"{path.relative_to(ROOT)} carries {carried}"


def footer_headline_level_line(contract):
    levels = contract["status_levels"]
    markers = "; ".join(
        f"{levels[name]['emoji']} {levels[name]['meaning'].replace('; ', ', ')}"
        for name in ("green", "yellow", "red")
    )
    return (
        "HEADLINE LEVEL: start the report's headline with exactly one status marker, "
        f"the worst level that applies: {markers}. Use no other status emoji."
    )


def test_footer_headline_level_lines_match_status_levels_exactly():
    _, contract = level_contract()
    expected = footer_headline_level_line(contract)
    for path in FOOTERS:
        lines = [line for line in path.read_text().splitlines() if line.startswith(HEADLINE_LEVEL_PREFIX)]
        assert len(lines) == 1, path
        assert lines[0] == expected, f"{path.name} drifted from {LEVELS.name}"
