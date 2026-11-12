"""Scheduled Hermes reports share one fetched-item and urgent-accounting contract."""

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
SURFACE = ROOT / "auto-ai-agent" / "hermes.md"
KANBAN = ROOT / "auto-ai-agent" / "hermes-daily-status-kanban-summary.md"
RENDER = {"engine": "literal", "variables": [], "frontmatter": "strip"}
REPORT_RULES = (
    (
        "Count fetched items exactly for every source-defined priority, including zero counts; "
        "report exact unknown and unset counts separately. Never infer, map, or normalize priority."
    ),
    "List completed actions with observed outcomes. Proposals, attempts, plans, and inferences are not completed actions.",
    (
        "Account for every fetched urgent item by ID. For each acted item, report its action and "
        "observed outcome. For each unacted item, give exactly one reason from: “not permitted for "
        "this profile”, “no valid assignee”, “not ready”, “blocked by guard”, “waiting on a person”. "
        "For “not permitted for this profile”, name the responsible profile."
    ),
    (
        "“Nothing new” cannot replace this accounting. Hourly reports with no new findings still "
        "deliver a concise outcome to their configured non-Slack reader or an existing thread; "
        "never use bare [SILENT] for that hourly reader."
    ),
    "Reporting grants no authority. Existing permissions, approvals, execution rules, and guards still apply.",
)
REASONS = (
    "not permitted for this profile",
    "no valid assignee",
    "not ready",
    "blocked by guard",
    "waiting on a person",
)


def rendered_body(path):
    opening, metadata, body = path.read_text().split("---\n", 2)
    assert opening == "", f"{path.name} must open with YAML frontmatter"
    frontmatter = yaml.safe_load(metadata)
    assert frontmatter["render"]["frontmatter"] == "strip"
    return frontmatter, body


def test_shared_surface_renders_the_five_report_contract_bullets():
    frontmatter, body = rendered_body(SURFACE)
    assert frontmatter["render"] == RENDER
    section = body.split("## Scheduled report contract\n\n", 1)[1].split("\n\n", 1)[0]
    bullets = [line[2:] for line in section.splitlines() if line.startswith("- ")]
    assert tuple(bullets) == REPORT_RULES
    for reason in REASONS:
        assert f"“{reason}”" in section


def test_daily_kanban_summary_renders_board_details_and_uses_shared_contract():
    frontmatter, body = rendered_body(KANBAN)
    assert frontmatter["render"]["engine"] == "jinja2"
    assert frontmatter["render"]["variables"] == ["hermes_agent_dashboard_port"]
    text = " ".join(body.split())
    assert "follow the scheduled-report contract in the shared Hermes surface" in text
    for status in ("ready", "in_progress", "blocked", "done"):
        assert status in text, status
    assert "any other status it reports" in text
    assert "board: 3 ready, 1 in_progress, 2 blocked, 14 done today" in text
    assert "name it by id with a link" in text
    assert "{{ hermes_agent_dashboard_port }}" in text
    assert not any(reason in text for reason in REASONS)
