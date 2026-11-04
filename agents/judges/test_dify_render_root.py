"""The Dify renderer can render another checkout's agents with this repository's helpers."""

import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest


_ROOT = Path(__file__).resolve().parents[2]
_RENDER = _ROOT / "agents" / "dify-src" / "render.py"
_SPEC = importlib.util.spec_from_file_location("dify_render_root_under_test", _RENDER)
render = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(render)

_TEMPLATE = """app:
  name: __DIFY_AGENT_NAME__
model: __DIFY_LITELLM_ROLE__
code: |
  __DIFY_HELPER_JSON_FENCE__
prompt: |
  __DIFY_SYSTEM_PROMPT__
"""


def _checkout(root, prompt="agents/prompts/sample.md"):
    agents = root / "agents"
    (agents / "prompts" / "shared").mkdir(parents=True)
    (agents / "dify-src" / "sample").mkdir(parents=True)
    (agents / "dify").mkdir()
    (agents / "prompts" / "shared" / "prefix.md").write_text("Shared prefix.\n")
    (agents / "prompts" / "sample.md").write_text("Sample prompt.\n")
    (agents / "dify-src" / "sample" / "000.dsl.yml.tmpl").write_text(_TEMPLATE)
    (agents / "sample.yaml").write_text(
        "name: sample\n"
        "home_platform: dify\n"
        "litellm_role: medium\n"
        "shared_prefix: agents/prompts/shared/prefix.md\n"
        f"prompt: {prompt}\n"
    )
    return agents / "dify" / "sample.dsl.yml"


def _run(*args):
    return subprocess.run(
        [sys.executable, str(_RENDER), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def test_root_renders_another_checkout_with_this_repositorys_helpers(tmp_path):
    output = _checkout(tmp_path)
    result = _run("--root", str(tmp_path))
    assert result.returncode == 0, result.stderr
    rendered = output.read_text()
    assert "name: sample" in rendered
    assert "model: medium" in rendered
    assert "Shared prefix." in rendered and "Sample prompt." in rendered
    helper = (_ROOT / "agents" / "dify-src" / "helpers" / "json_fence.py").read_text()
    assert helper.splitlines()[0] in rendered
    assert _run("--root", str(tmp_path), "--check").returncode == 0


def test_root_keeps_prompt_paths_inside_the_chosen_checkout(tmp_path):
    checkout = tmp_path / "checkout"
    _checkout(checkout, prompt="../outside.md")
    (tmp_path / "outside.md").write_text("Outside prompt.\n")
    result = _run("--root", str(checkout))
    assert result.returncode == 2
    assert "prompt does not name a repository file: ../outside.md" in result.stderr


def test_default_root_is_this_repository():
    assert render.ROOT == _ROOT
    assert render.OUTPUT_ROOT == _ROOT / "agents" / "dify"


def test_missing_root_directory_fails(tmp_path):
    result = _run("--root", str(tmp_path / "absent"))
    assert result.returncode == 2
    assert "--root is not a directory" in result.stderr


@pytest.mark.parametrize("marker", sorted(render.HELPER_MARKERS))
def test_helpers_resolve_from_this_repository(marker):
    assert render.HELPER_MARKERS[marker].is_relative_to(_ROOT / "agents" / "dify-src" / "helpers")
