"""Exercise the inline release publisher without contacting Langfuse."""

import json
import os
from pathlib import Path
import subprocess

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = yaml.safe_load(
    (ROOT / ".github/workflows/langfuse-prompt-sync.yml").read_text()
)
STEP = WORKFLOW["jobs"]["sync"]["steps"][-1]


def run_sync(tmp_path, dry_run, content="---\ntitle: Example\n---\nHello {{name}}\n"):
    prompts = tmp_path / "agents/prompts"
    prompts.mkdir(parents=True)
    (prompts / "example.md").write_text(content)
    calls = tmp_path / "calls"
    env = {
        **os.environ,
        "DRY_RUN": str(dry_run).lower(),
        "RELEASE_TAG": "v0.2.0",
        "LANGFUSE_HOST": "",
        "LANGFUSE_PUBLIC_KEY": "",
        "LANGFUSE_SECRET_KEY": "",
        "CALLS": str(calls),
    }
    if not dry_run:
        env.update(
            LANGFUSE_HOST="https://example.invalid",
            LANGFUSE_PUBLIC_KEY="test-public",
            LANGFUSE_SECRET_KEY="test-secret",
        )
    result = subprocess.run(
        ["bash", "-c", 'npx() { printf "%s\\0" "$@" >> "$CALLS"; };\n' + STEP["run"]],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
    )
    return result, calls


def test_pull_request_dry_run_needs_no_credentials_or_cli(tmp_path):
    result, calls = run_sync(tmp_path, True)
    assert result.returncode == 0, result.stderr
    assert "Validated prompt: example" in result.stdout
    assert not calls.exists()


def test_release_sends_body_and_labels_to_official_cli(tmp_path):
    result, calls = run_sync(tmp_path, False)
    assert result.returncode == 0, result.stderr
    args = calls.read_bytes().decode().split("\0")[:-1]
    assert args[:-1] == [
        "--yes", "@langfuse/cli@1.3.1", "api", "prompts", "create", "--body-json"
    ]
    assert json.loads(args[-1]) == {
        "name": "example",
        "type": "text",
        "labels": ["v0.2.0", "production"],
        "prompt": "Hello {{name}}\n",
    }
    assert "Hello" not in result.stdout


@pytest.mark.parametrize("content", ["", "---\ntitle: Example\n---\n\n"])
def test_empty_prompt_fails_without_publishing(tmp_path, content):
    result, calls = run_sync(tmp_path, False, content)
    assert result.returncode != 0
    assert not calls.exists()


def test_empty_catalog_fails(tmp_path):
    result = subprocess.run(
        ["bash", "-c", STEP["run"]],
        cwd=tmp_path,
        env={**os.environ, "DRY_RUN": "true", "RELEASE_TAG": "v0.2.0"},
        capture_output=True,
    )
    assert result.returncode != 0


def test_release_requires_credentials_before_publishing(tmp_path):
    result = subprocess.run(
        ["bash", "-c", STEP["run"]],
        cwd=tmp_path,
        env={**os.environ, "DRY_RUN": "false", "LANGFUSE_HOST": ""},
        text=True,
        capture_output=True,
    )
    assert result.returncode != 0
    assert "Missing LANGFUSE_HOST" in result.stderr


def test_catalog_dry_run():
    result = subprocess.run(
        ["bash", "-c", STEP["run"]],
        cwd=ROOT,
        env={**os.environ, "DRY_RUN": "true", "RELEASE_TAG": "v0.2.0"},
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    assert set(result.stdout.splitlines()) == {
        f"Validated prompt: {path.stem}"
        for path in (ROOT / "agents/prompts").glob("*.md")
    }
