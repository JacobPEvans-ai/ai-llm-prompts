"""Tests for the byte-preserving Dify fragment renderer."""

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

import pytest
import yaml


_ROOT = Path(__file__).resolve().parents[2]
_RENDER_PATH = _ROOT / "agents" / "dify-src" / "render.py"
_SPEC = importlib.util.spec_from_file_location("dify_renderer", _RENDER_PATH)
render = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(render)


def _without_prompt_content(value):
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            if key == "environment_variables" and isinstance(child, list):
                # Shared-prefix inlining removes this prompt-only Dify variable.
                child = [item for item in child if item.get("name") != "SHARED_PREFIX"]
            result[key] = _without_prompt_content(child)
        if value.get("role") == "system" and "text" in result:
            result["text"] = "<SYSTEM_PROMPT>"
        return result
    if isinstance(value, list):
        return [_without_prompt_content(item) for item in value]
    return value


def test_dify_render_check_verifies_real_and_copied_fragment_hashes(tmp_path, monkeypatch, capsys):
    assert render.main(["--check"]) == 0

    root = tmp_path
    agents = root / "agents"
    source_root = agents / "dify-src"
    fragment = source_root / "code-simplifier" / "003.dsl.yml.tmpl"
    fragment.parent.mkdir(parents=True)
    shutil.copyfile(_ROOT / "agents" / "dify-src" / "code-simplifier" / fragment.name, fragment)
    (agents / "shared.md").write_text("Shared prompt")
    (agents / "prompt.md").write_text("Agent prompt")
    definition = agents / "code-simplifier.yaml"
    definition.write_text(json.dumps({
        "name": "code-simplifier",
        "shared_prefix": "agents/shared.md",
        "prompt": "agents/prompt.md",
    }))
    (agents / "dify").mkdir()

    with monkeypatch.context() as patch:
        patch.setattr(render, "ROOT", root)
        patch.setattr(render, "AGENTS", agents)
        patch.setattr(render, "SOURCE_ROOT", source_root)
        patch.setattr(render, "OUTPUT_ROOT", agents / "dify")
        patch.setattr(render, "load_yaml", lambda path: json.loads(path.read_text()))

        assert render.main(["--update-manifest"]) == 0
        output, rendered = render.render_agent(definition)
        output.write_text(rendered)
        assert render.main(["--check"]) == 0

        fragment.write_bytes(fragment.read_bytes() + b" ")
        assert render.main(["--check"]) == 1
        assert fragment.relative_to(root).as_posix() in capsys.readouterr().err

        (source_root / "fragments.sha256").write_text("")
        assert render.main(["--check"]) == 1
        assert fragment.relative_to(root).as_posix() in capsys.readouterr().err


def test_rendered_dify_structure_matches_origin_main_outside_prompts():
    if shutil.which("git") is None:
        pytest.skip("git is unavailable; no local origin/main baseline to compare")
    baseline = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", "origin/main^{commit}"],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if baseline.returncode != 0:
        pytest.skip("origin/main is unavailable locally; no network lookup is performed")

    differences = []
    for path in sorted((_ROOT / "agents" / "dify").glob("*.dsl.yml")):
        relative = path.relative_to(_ROOT).as_posix()
        original = subprocess.run(
            ["git", "show", f"origin/main:{relative}"],
            cwd=_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert original.returncode == 0, f"could not read origin/main:{relative}"
        before = _without_prompt_content(yaml.safe_load(original.stdout))
        after = _without_prompt_content(yaml.safe_load(path.read_text()))
        if before != after:
            differences.append(relative)

    assert not differences, f"unexpected Dify DSL structure changes: {differences}"
