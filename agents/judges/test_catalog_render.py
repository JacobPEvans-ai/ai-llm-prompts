"""Exercise the catalog render and drift targets against an isolated roster."""

from pathlib import Path
import hashlib
import re
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


def test_hermes_group_indexes_cover_every_prompt():
    catalog = ROOT / "auto-ai-agent"
    indexes = [catalog / "index.md", *catalog.glob("hermes-*/index.md")]
    linked = []
    for index in indexes:
        for target in re.findall(r"\]\(([^)]+)\)", index.read_text()):
            path = (index.parent / target).resolve()
            assert path.is_file(), (index, target)
            linked.append(path)
    for prompt in catalog.glob("*.md"):
        if prompt.name == "index.md":
            continue
        assert linked.count(prompt.resolve()) == 1, prompt.name
    for index in indexes[1:]:
        assert linked.count(index.resolve()) == 1, index


def test_hourly_stats_index_reassembles_original_bytes():
    index = ROOT / "auto-ai-agent/hermes-reporting/index.md"
    targets = re.findall(r"^\d+\. .*\]\(([^)]+)\)", index.read_text(), re.MULTILINE)
    assert len(targets) == 3
    bodies = []
    for position, target in enumerate(targets, start=1):
        path = index.parent / target
        assert path.name == f"hermes-llm-stats-hourly-part{position}.md"
        opening, metadata, body = path.read_bytes().split(b"---\n", 2)
        assert opening == b""
        contract = yaml.safe_load(metadata)
        assert contract["type"] == "LLM Prompt Fragment"
        assert contract["render"] == {"engine": "literal", "variables": [], "frontmatter": "strip"}
        bodies.append(body)
    # Freeze the original literal body, including separators and its final byte.
    assert hashlib.sha256(b"".join(bodies)).hexdigest() == (
        "a3f57ba93b3ee2818288d30c5819e13fd6934da2e50e37f376747928c4039aef"
    )
