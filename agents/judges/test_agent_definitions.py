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
        _DSL_AGENTS.append(_name)


def _system_prompts(dsl):
    return [
        (data.get("title"), message["text"])
        for node in dsl["workflow"]["graph"]["nodes"]
        for data in [node.get("data", {})]
        if data.get("type") == "llm"
        for message in data.get("prompt_template", [])
        if message.get("role") == "system"
    ]


@pytest.mark.parametrize("agent_name", _DSL_AGENTS)
def test_dify_system_prompt_matches_its_declared_source(agent_name):
    agent = yaml.safe_load((_AGENTS / f"{agent_name}.yaml").read_text())
    dsl = yaml.safe_load((_AGENTS / "dify" / f"{agent_name}.dsl.yml").read_text())
    system_prompts = _system_prompts(dsl)
    assert len(system_prompts) == 1, f"{agent_name} must have exactly one system prompt in its Dify LLM nodes"
    node_title, actual_prompt = system_prompts[0]
    exception = agent.get("dify_system_prompt_exception")
    if exception is not None:
        assert exception.get("node") == node_title, f"{agent_name} exception must name its Dify system-prompt node"
        assert exception.get("reason"), f"{agent_name} exception must document why it differs"
        exception_source = _ROOT / exception["source"]
        assert exception_source.is_file(), f"{agent_name} exception source does not exist: {exception['source']}"
        assert _normalize_whitespace(actual_prompt) == _normalize_whitespace(exception_source.read_text()), (
            f"{agent_name} Dify system prompt must match its declared exception source"
        )
        return

    expected = "\n\n".join(
        (
            _prompt_body(_ROOT / agent["shared_prefix"]),
            _prompt_body(_ROOT / agent["prompt"]),
        )
    )
    assert _normalize_whitespace(actual_prompt) == _normalize_whitespace(expected), (
        f"{agent_name} Dify system prompt must equal the canonical shared prefix and prompt body"
    )


def test_only_vikunja_clerk_uses_a_declared_dify_system_prompt_exception():
    exceptions = {path.stem for path, agent in _definitions() if "dify_system_prompt_exception" in agent}
    assert exceptions == {"vikunja-clerk"}
