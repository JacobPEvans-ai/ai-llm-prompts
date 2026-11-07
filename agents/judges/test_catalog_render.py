"""Exercise the catalog render and drift targets against an isolated roster."""

from pathlib import Path
import subprocess

import yaml


ROOT = Path(__file__).resolve().parents[2]


def make_catalog(tmp_path, target, *overrides):
    return subprocess.run(
        ["make", "--no-print-directory", target, f"AGENTS_ROOT={tmp_path}", *overrides],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def roster(tmp_path):
    agents = tmp_path / "agents"
    (agents / "prompts").mkdir(parents=True)
    for name, tier, triggers, reader, signal in (
        ("zulu", 2, [{"kind": "anchor", "at": "06:07", "days": ["Mon", "Fri"]}], "operator", "item moved"),
        ("alpha", 1, [{"kind": "event", "source": "github.push"}, {"kind": "rotation", "every": "15m"}],
         "reviewer", "checks green"),
    ):
        (agents / f"{name}.yaml").write_text(yaml.safe_dump({
            "name": name, "tier": tier, "triggers": triggers, "reader": reader, "acted_signal": signal,
        }))
    return agents


def test_catalog_uses_sorted_resolved_roster_and_output_overrides(tmp_path):
    roster(tmp_path)
    index = tmp_path / "roster.md"
    prompts = tmp_path / "prompts.md"
    result = make_catalog(tmp_path, "render-index", f"INDEX_OUTPUT={index}", f"PROMPT_INDEX_OUTPUT={prompts}")
    assert result.returncode == 0, result.stderr
    text = index.read_text()
    assert text.index("[alpha](alpha.yaml)") < text.index("[zulu](zulu.yaml)")
    assert "Trigger: event: github.push" in text
    assert "Trigger: rotation: 15m" in text
    assert "anchor: 06:07 UTC (Mon, Fri)" in text
    assert "Reader: reviewer" in text and "Acted signal: checks green" in text
    assert "agent-standards.md" in text and "evals/promptfoo/README.md" in text
    prompt_text = prompts.read_text()
    assert prompt_text.index("[alpha](alpha.md)") < prompt_text.index("[zulu](zulu.md)")
    assert "shared/homelab.md" in prompt_text


def test_catalog_drift_check_rejects_changed_output(tmp_path):
    agents = roster(tmp_path)
    result = make_catalog(tmp_path, "render-index")
    assert result.returncode == 0, result.stderr
    assert make_catalog(tmp_path, "check-index").returncode == 0
    (agents / "prompts" / "index.md").write_text("stale catalog\n")
    result = make_catalog(tmp_path, "check-index")
    assert result.returncode != 0
    assert "stale catalog" in result.stdout
