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
    assert separator >= 0, (
        f"{path.relative_to(_ROOT)} has an unterminated OKF frontmatter block"
    )
    frontmatter = yaml.safe_load(text[4:separator])
    assert isinstance(frontmatter, dict), (
        f"{path.relative_to(_ROOT)} has invalid OKF frontmatter"
    )
    assert _OKF_FIELDS <= frontmatter.keys(), (
        f"{path.relative_to(_ROOT)} is missing OKF fields: {_OKF_FIELDS - frontmatter.keys()}"
    )
    assert frontmatter["type"] in {"LLM Prompt", "LLM Prompt Fragment"}
    return text[separator + 5 :].lstrip()


def _normalize_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()


def _missing_roster_fields(agent):
    return [
        field
        for field in _ROSTER_FIELDS
        if field not in agent or agent[field] in (None, "", [], {})
    ]


def test_roster_names_the_eight_criterion_six_fields():
    assert _ROSTER_FIELDS == (
        "home_platform",
        "prompt",
        "tools",
        "privacy_class",
        "litellm_role",
        "trigger",
        "memory_scope",
        "eval_set",
    )


@pytest.mark.parametrize("field", _ROSTER_FIELDS)
def test_a_definition_missing_one_roster_field_fails_the_check(field):
    _, agent = _definitions()[0]
    broken = {key: value for key, value in agent.items() if key != field}
    assert _missing_roster_fields(broken) == [field]


@pytest.mark.parametrize("empty", [None, "", [], {}])
@pytest.mark.parametrize("field", _ROSTER_FIELDS)
def test_a_definition_with_an_empty_roster_field_fails_the_check(field, empty):
    _, agent = _definitions()[0]
    broken = {**agent, field: empty}
    assert _missing_roster_fields(broken) == [field]


def test_agent_roster_paths_and_prompt_metadata_are_complete():
    definitions = _definitions()
    assert definitions

    shared_prefixes = set()
    for path, agent in definitions:
        assert isinstance(agent, dict), f"{path.name} must contain a YAML mapping"
        missing = _missing_roster_fields(agent)
        assert not missing, f"{path.name} is missing non-empty roster fields: {missing}"

        for field in ("prompt", "eval_set", "shared_prefix"):
            target = _ROOT / agent[field]
            assert target.is_file(), (
                f"{path.name} {field} does not name a file: {agent[field]}"
            )

        shared_prefixes.add(agent["shared_prefix"])
        _prompt_body(_ROOT / agent["prompt"])

    assert len(shared_prefixes) == 1, (
        f"agents use different shared prefixes: {sorted(shared_prefixes)}"
    )
    _prompt_body(_ROOT / next(iter(shared_prefixes)))


def _key_references(value):
    if isinstance(value, dict):
        for field, child in value.items():
            if field in {
                "api_key_ref",
                "secret_ref",
                "github_token_ref",
                "router_key_ref",
            }:
                if isinstance(child, str):
                    yield child
            yield from _key_references(child)
    elif isinstance(value, list):
        for child in value:
            yield from _key_references(child)


def test_agent_memory_scopes_identities_and_key_references_are_unique():
    definitions = _definitions()
    memory_scopes = [
        agent["memory_scope"]
        for _, agent in definitions
        if agent.get("memory_scope") not in (None, "", "none")
    ]
    identities = [agent["identity"] for _, agent in definitions]
    key_owners = {}
    for path, agent in definitions:
        for reference in set(_key_references(agent)):
            key_owners.setdefault(reference, set()).add(path.stem)

    assert len(memory_scopes) == len(set(memory_scopes)), (
        "agent memory scopes must be unique"
    )
    assert len(identities) == len(set(identities)), "agent identities must be unique"
    assert all(len(owners) == 1 for owners in key_owners.values()), (
        f"agent key references must be unique: {key_owners}"
    )


_MEMORY_TOKENS = ("hindsight", "memory")


def test_agents_without_memory_scope_declare_no_memory_tool():
    for path, agent in _definitions():
        if agent["memory_scope"] != "none":
            continue
        declared = [*agent.get("tools", []), *agent.get("mcp_servers", [])]
        memory_names = [
            name
            for name in declared
            if any(token in str(name).lower() for token in _MEMORY_TOKENS)
        ]
        assert not memory_names, (
            f"{path.name} has memory_scope none but declares memory tools: {memory_names}"
        )


def test_memory_bank_names_appear_only_in_their_own_definition():
    for path, agent in _definitions():
        scope = agent["memory_scope"]
        if scope == "none":
            continue
        mentions = [
            file.relative_to(_ROOT).as_posix()
            for file in sorted(_AGENTS.rglob("*"))
            if file.is_file()
            and file.suffix in {".yaml", ".yml", ".md", ".py", ".tmpl", ".json"}
            and file.resolve() != Path(__file__).resolve()
            and scope in file.read_text(errors="ignore")
        ]
        assert mentions == [path.relative_to(_ROOT).as_posix()], (
            f"memory bank {scope} must appear only in its own definition: {mentions}"
        )


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
def test_dify_model_schedule_and_mcp_tools_follow_agent_definition(agent_name):
    agent = yaml.safe_load((_AGENTS / f"{agent_name}.yaml").read_text())
    dsl = yaml.safe_load((_AGENTS / "dify" / f"{agent_name}.dsl.yml").read_text())
    nodes = dsl["workflow"]["graph"]["nodes"]
    assert dsl["app"]["name"] == agent["name"]
    model_names = [
        data["model"]["name"]
        for node in nodes
        for data in [node.get("data", {})]
        if isinstance(data.get("model"), dict) and "name" in data["model"]
    ]
    assert model_names and set(model_names) == {agent["litellm_role"]}

    mode_defaults = [
        variable["value"]
        for variable in dsl["workflow"].get("environment_variables", [])
        if str(variable.get("name", "")).endswith("_MODE")
    ]
    assert all(value == agent["mode"] for value in mode_defaults)

    schedules = [
        data
        for node in nodes
        for data in [node.get("data", {})]
        if data.get("type") == "trigger-schedule"
    ]
    trigger = agent["trigger"]
    if trigger["kind"] == "schedule":
        assert len(schedules) == 1
        assert schedules[0]["cron_expression"] == trigger["cron"]
    else:
        assert not schedules

    if agent.get("mcp_servers"):
        expected_tools = {tool.split(".", 1)[0] for tool in agent["tools"]}
        actual_tools = {
            node.get("data", {}).get("tool_name")
            for node in nodes
            if node.get("data", {}).get("type") == "tool"
        }
        assert actual_tools == expected_tools

    github_reader = agent.get("github_reader")
    if github_reader:
        token_path = [
            variable
            for variable in dsl["workflow"].get("environment_variables", [])
            if variable.get("name") == "GITHUB_READ_TOKEN_PATH"
        ]
        assert len(token_path) == 1
        assert github_reader["github_token_ref"] in token_path[0].get("description", "")


@pytest.mark.parametrize("agent_name", _DSL_AGENTS)
def test_dify_system_prompt_matches_its_declared_source(agent_name):
    agent = yaml.safe_load((_AGENTS / f"{agent_name}.yaml").read_text())
    dsl = yaml.safe_load((_AGENTS / "dify" / f"{agent_name}.dsl.yml").read_text())
    system_prompts = _system_prompts(dsl)
    assert len(system_prompts) == 1, (
        f"{agent_name} must have exactly one system prompt in its Dify LLM nodes"
    )
    _, actual_prompt = system_prompts[0]
    expected = "\n\n".join(
        (
            _prompt_body(_ROOT / agent["shared_prefix"]),
            _prompt_body(_ROOT / agent["prompt"]),
        )
    )
    assert _normalize_whitespace(actual_prompt) == _normalize_whitespace(expected), (
        f"{agent_name} Dify system prompt must equal the canonical shared prefix and prompt body"
    )
