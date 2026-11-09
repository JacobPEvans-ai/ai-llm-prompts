"""Profile resolution runs through gomplate, including nested and empty overrides."""

import subprocess

import pytest
import yaml

from definitions import resolve_records
from test_dify_render import driver_dsl, sample_checkout, render_checkout


@pytest.fixture
def profiled_checkout(tmp_path):
    path, agent = sample_checkout(tmp_path)
    profiles = tmp_path / "agents" / "profiles"
    profiles.mkdir()
    defaults = {"home_platform": "dify", "routing": {"local": True, "tier": 2}, "tools": ["read"]}
    profile = {"routing": {"tier": 0}, "enabled": True, "limit": 9}
    (profiles / "defaults.yaml").write_text(yaml.safe_dump(defaults))
    (profiles / "interactive.yaml").write_text(yaml.safe_dump(profile))
    agent.pop("prompt")
    agent.update(extends="interactive", routing={"local": False}, tools=[], enabled=False, limit=0,
                 identity="explicit-identity", api_key_ref="explicit-key")
    path.write_text(yaml.safe_dump(agent))
    return path, agent


def test_deep_merge_and_explicit_empty_overrides(profiled_checkout, tmp_path):
    record, = resolve_records(tmp_path)
    agent = record["agent"]
    assert agent["routing"] == {"local": False, "tier": 0}
    assert agent["tools"] == []
    assert agent["enabled"] is False and agent["limit"] == 0
    assert agent["identity"] == "explicit-identity" and agent["api_key_ref"] == "explicit-key"
    assert agent["prompt"] == "agents/prompts/sample.md"
    assert agent["eval_set"] == "agents/evals/sample.yaml"
    assert record["profile"]["routing"] == {"local": True, "tier": 0}
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("name", ["../interactive", "defaults", "missing", "bad/name", ""])
def test_invalid_or_missing_profile_fails(profiled_checkout, tmp_path, name):
    path, agent = profiled_checkout
    agent["extends"] = name
    path.write_text(yaml.safe_dump(agent))
    with pytest.raises(subprocess.CalledProcessError):
        resolve_records(tmp_path)


@pytest.mark.parametrize("field", ["identity", "api_key_ref", "name", "extends", "prompt", "eval_set"])
def test_profile_cannot_rebind_explicit_or_conventional_fields(profiled_checkout, tmp_path, field):
    profile = tmp_path / "agents" / "profiles" / "interactive.yaml"
    profile.write_text(yaml.safe_dump({field: "another"}))
    with pytest.raises(subprocess.CalledProcessError):
        resolve_records(tmp_path)


@pytest.mark.parametrize("field", ["prompt", "eval_set"])
def test_conventional_paths_cannot_be_overridden(profiled_checkout, tmp_path, field):
    path, agent = profiled_checkout
    agent[field] = "agents/other.yaml"
    path.write_text(yaml.safe_dump(agent))
    with pytest.raises(subprocess.CalledProcessError):
        resolve_records(tmp_path)


def test_rotation_driver_uses_inherited_tier_and_triggers(profiled_checkout, tmp_path):
    profile = tmp_path / "agents" / "profiles" / "interactive.yaml"
    profile.write_text("tier: 2\ntriggers: [{kind: rotation, every: 1d}]\n")
    path, agent = profiled_checkout
    agent.pop("triggers")
    path.write_text(yaml.safe_dump(agent))
    result = render_checkout(tmp_path)
    assert result.returncode == 0, result.stderr
    output = yaml.safe_load(driver_dsl(tmp_path).read_text())
    code = next(node["data"]["code"] for node in output["workflow"]["graph"]["nodes"] if node["id"] == "due")
    namespace = {}
    exec(code, namespace)
    assert namespace["ROTATION_AGENTS"] == [
        {"name": "sample", "every_minutes": 1440, "offset_minutes": 0, "expected_runtime_minutes": 10},
    ]
