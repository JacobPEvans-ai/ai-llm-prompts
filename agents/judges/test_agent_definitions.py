"""Contract tests for the homelab agent roster and canonical prompt copies."""

from pathlib import Path
import re

import pytest
import yaml


_ROOT = Path(__file__).resolve().parents[2]
_AGENTS = _ROOT / "agents"
_ROSTER_FIELDS = (
    "home_platform",
    "prompt",
    "tools",
    "privacy_class",
    "litellm_role",
    "trigger",
    "memory_scope",
    "eval_set",
)
_OKF_FIELDS = {
    "type",
    "title",
    "description",
    "resource",
    "tags",
    "timestamp",
    "status",
    "consumers",
    "render",
    "source_history",
}
_KNOWN_DSL_PREFIX_GAPS = {
    name: pytest.mark.xfail(
        strict=True,
        reason="The existing Dify system prompt does not contain the canonical shared-prefix body before the agent prompt.",
    )
    for name in (
        "ci-fixer",
        "code-simplifier",
        "vikunja-clerk",
        "vikunja-triage",
        "zammad-triage",
    )
}


def _definitions():
    return [
        (path, yaml.safe_load(path.read_text()))
        for path in sorted(_AGENTS.glob("*.yaml"))
    ]


def _prompt_body(path):
    text = path.read_text()
    assert text.startswith("---\n"), f"{path.relative_to(_ROOT)} has no OKF frontmatter"
    separator = text.find("\n---\n", 4)
    assert separator >= 0, f"{path.relative_to(_ROOT)} has an unterminated OKF frontmatter block"
    frontmatter = yaml.safe_load(text[4:separator])
    assert isinstance(frontmatter, dict), f"{path.relative_to(_ROOT)} has invalid OKF frontmatter"
    assert _OKF_FIELDS <= frontmatter.keys(), (
        f"{path.relative_to(_ROOT)} is missing OKF fields: {_OKF_FIELDS - frontmatter.keys()}"
    )
    assert frontmatter["type"] in {"LLM Prompt", "LLM Prompt Fragment"}
    return text[separator + 5 :].lstrip()


def _normalize_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()


def test_agent_roster_paths_and_prompt_metadata_are_complete():
    definitions = _definitions()
    assert definitions

    shared_prefixes = set()
    for path, agent in definitions:
        assert isinstance(agent, dict), f"{path.name} must contain a YAML mapping"
        for field in _ROSTER_FIELDS:
            assert field in agent and agent[field] not in (None, "", [], {}), (
                f"{path.name} is missing non-empty roster field {field}"
            )

        for field in ("prompt", "eval_set", "shared_prefix"):
            target = _ROOT / agent[field]
            assert target.is_file(), f"{path.name} {field} does not name a file: {agent[field]}"

        shared_prefixes.add(agent["shared_prefix"])
        _prompt_body(_ROOT / agent["prompt"])

    assert len(shared_prefixes) == 1, f"agents use different shared prefixes: {sorted(shared_prefixes)}"
    _prompt_body(_ROOT / next(iter(shared_prefixes)))


_DSL_AGENTS = []
for _path, _agent in _definitions():
    _name = _path.stem
    if (_AGENTS / "dify" / f"{_name}.dsl.yml").is_file():
        _case = pytest.param(_name, marks=_KNOWN_DSL_PREFIX_GAPS[_name]) if _name in _KNOWN_DSL_PREFIX_GAPS else _name
        _DSL_AGENTS.append(_case)


@pytest.mark.parametrize("agent_name", _DSL_AGENTS)
def test_dify_system_prompt_contains_prefix_before_canonical_prompt(agent_name):
    agent = yaml.safe_load((_AGENTS / f"{agent_name}.yaml").read_text())
    expected = _prompt_body(_ROOT / agent["prompt"])
    shared_prefix = _prompt_body(_ROOT / agent["shared_prefix"])
    dsl = yaml.safe_load((_AGENTS / "dify" / f"{agent_name}.dsl.yml").read_text())
    system_prompts = [
        message["text"]
        for node in dsl["workflow"]["graph"]["nodes"]
        for data in [node.get("data", {})]
        if data.get("type") == "llm"
        for message in data.get("prompt_template", [])
        if message.get("role") == "system"
    ]
    assert len(system_prompts) == 1, f"{agent_name} must have exactly one system prompt in its Dify LLM nodes"

    actual = _normalize_whitespace(system_prompts[0])
    normalized_prefix = _normalize_whitespace(shared_prefix)
    normalized_prompt = _normalize_whitespace(expected)
    assert actual.startswith(normalized_prefix) and actual[len(normalized_prefix) :].lstrip().startswith(
        normalized_prompt
    ), (
        f"{agent_name} Dify system prompt must contain the canonical shared prefix before the agent prompt"
    )
