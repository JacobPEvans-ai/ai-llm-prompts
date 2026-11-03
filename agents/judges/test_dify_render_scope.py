"""Dify rendering covers only agents homed on Dify."""

import importlib.util
from pathlib import Path

import pytest


_ROOT = Path(__file__).resolve().parents[2]
_AGENTS = _ROOT / "agents"
_SPEC = importlib.util.spec_from_file_location(
    "dify_render_scope_under_test", _AGENTS / "dify-src" / "render.py"
)
render = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(render)


def _dify_definition_names():
    names = set()
    for path in sorted(_AGENTS.glob("*.yaml")):
        if render.load_yaml(path).get("home_platform") == "dify":
            names.add(path.stem)
    return names


def test_render_all_returns_only_dify_homed_workflows():
    rendered = {path.name.split(".")[0] for path, _ in render.render_all()}
    assert rendered == _dify_definition_names()
    assert "hatchet-eval" not in rendered


def test_every_dify_definition_has_a_fragment_directory():
    for name in _dify_definition_names():
        assert (_AGENTS / "dify-src" / name).is_dir(), name


def test_non_dify_definition_is_skipped_without_rendering(tmp_path, monkeypatch):
    (tmp_path / "agents").mkdir()
    (tmp_path / "agents" / "elsewhere.yaml").write_text("home_platform: hatchet\n")
    (tmp_path / "agents" / "homed.yaml").write_text("home_platform: dify\n")
    rendered = []
    monkeypatch.setattr(render, "ROOT", tmp_path)
    monkeypatch.setattr(render, "AGENTS", tmp_path / "agents")
    monkeypatch.setattr(
        render, "render_agent", lambda path: rendered.append(path.stem) or (path, "")
    )
    render.render_all()
    assert rendered == ["homed"]


def test_definition_without_home_platform_fails_the_render(tmp_path, monkeypatch):
    (tmp_path / "agents").mkdir()
    (tmp_path / "agents" / "orphan.yaml").write_text("name: orphan\n")
    monkeypatch.setattr(render, "ROOT", tmp_path)
    monkeypatch.setattr(render, "AGENTS", tmp_path / "agents")
    with pytest.raises(
        ValueError, match="agents/orphan.yaml must declare home_platform"
    ):
        render.render_all()
