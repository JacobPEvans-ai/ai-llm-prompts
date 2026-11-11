"""Scheduled Hermes reports share one fetched-item and urgent-accounting contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SURFACE = ROOT / "auto-ai-agent" / "hermes.md"
CONTRACT = ROOT / "auto-ai-agent" / "hermes-report-contract.md"
KANBAN = ROOT / "auto-ai-agent" / "hermes-daily-status-kanban-summary.md"
REASONS = (
    "not permitted for this profile",
    "no valid assignee",
    "not ready",
    "blocked by guard",
    "waiting on a person",
)
CLOSED_REASON_LIST = (
    "“not permitted for this profile”, “no valid assignee”, “not ready”, "
    "“blocked by guard”, “waiting on a person”"
)


def test_surface_points_to_the_shared_report_contract_once():
    text = " ".join(SURFACE.read_text().split())
    pointer = "[report](hermes-report-contract.md)"
    assert text.count(pointer) == 1
    assert CLOSED_REASON_LIST not in text


def test_shared_report_contract_defines_counts_actions_accounting_and_authority():
    text = " ".join(CONTRACT.read_text().split())
    for clause in (
        "Count fetched items exactly for every source-defined priority",
        "including zero counts",
        "report exact unknown and unset counts separately",
        "Never infer, map, or normalize priority",
        "List completed actions with observed outcomes",
        "Proposals, attempts, plans, and inferences are not completed actions",
        "Account for every fetched urgent item by ID",
        "For each acted item, report its action and observed outcome",
        "For each unacted item, give exactly one reason from",
        "For “not permitted for this profile”, name the responsible profile",
        "Nothing new” cannot replace this accounting",
        "Reporting grants no authority",
        "Existing permissions, approvals, execution rules, and guards still apply",
    ):
        assert clause in text, clause
    for reason in REASONS:
        assert f"“{reason}”" in text, reason


def test_daily_kanban_summary_uses_shared_contract_and_keeps_board_details():
    text = " ".join(KANBAN.read_text().split())
    assert "shared report contract (`hermes-report-contract.md`)" in text
    assert "priority counts, completed-action outcomes, and accounting for every fetched urgent item" in text
    assert "urgent item" in text
    for status in ("ready", "in_progress", "blocked", "done"):
        assert status in text, status
    assert "name it by id with a link" in text
    assert "{{ hermes_agent_dashboard_port }}" in text
    assert not any(reason in text for reason in REASONS)
