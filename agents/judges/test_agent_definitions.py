"""Contract tests for the homelab agent roster and canonical prompt copies."""

from pathlib import Path
import re

import pytest
import yaml

from definitions import definition, definitions, resolved_records
from test_promptfoo_cases import cases
from test_triggers import validate_triggers
from test_authoring_standards import (
    validate_description, validate_eval_policy, validate_eval_suite,
    validate_source, validate_unique_jobs,
)


_ROOT = Path(__file__).resolve().parents[2]
_AGENTS = _ROOT / "agents"
_HOME_PLATFORMS = {"dify", "hermes", "sim", "langflow", "litellm"}
_ROSTER_FIELDS = (
    "name",
    "owner",
    "home_platform",
    "shadows",
    "tier",
    "prompt",
    "shared_prefix",
    "tools",
    "mcp_servers",
    "litellm_role",
    "triggers",
    "connectors",
    "code_work",
    "mode",
    "memory_scope",
    "eval_set",
    "identity",
    "api_key_ref",
    "description",
    "eval_policy",
)
_EMPTY_LIST_FIELDS = {"shadows", "tools", "mcp_servers", "connectors"}
_AGENT_NAME = re.compile(r"(?!.*fill)[a-z0-9]+(?:-[a-z0-9]+)*", re.IGNORECASE)
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


_definitions = definitions

def test_retired_eval_agent_has_no_definition_prompt_evals_or_fragments():
    for path in (
        _AGENTS / "hatchet-eval.yaml",
        _AGENTS / "prompts" / "hatchet-eval.md",
        _AGENTS / "evals" / "hatchet-eval.yaml",
        _AGENTS / "dify-src" / "hatchet-eval",
    ):
        assert not path.exists(), path.relative_to(_ROOT)


def test_agent_home_platforms_use_supported_values():
    for path, agent in _definitions():
        assert agent["home_platform"] in _HOME_PLATFORMS, path.name


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
        if field not in agent
        or agent[field] in (None, "", {})
        or (agent[field] == [] and field not in _EMPTY_LIST_FIELDS)
    ]


def _validate_v2(agent):
    """Executable v2 schema; preserve agent-specific extension fields."""
    assert isinstance(agent, dict), "definition must be a mapping"
    assert not _missing_roster_fields(agent), "missing required v2 fields"
    assert "trigger" not in agent, "use triggers instead of trigger"
    assert isinstance(agent["name"], str) and _AGENT_NAME.fullmatch(agent["name"]), "invalid name"
    assert type(agent["tier"]) is int and agent["tier"] in (0, 1, 2), "invalid tier"
    assert agent["home_platform"] in tuple(_HOME_PLATFORMS), "invalid home_platform"
    assert agent.get("privacy_class", "private") in ("public", "internal", "private"), "invalid privacy_class"
    assert agent["mode"] in ("shadow", "live"), "invalid mode"
    assert agent["code_work"] in ("none", "sandbox"), "invalid code_work"
    assert agent.get("kind", "agent") in ("agent", "connector"), "invalid kind"
    if "owns" in agent:
        assert agent.get("kind") == "connector", "only a connector may declare owns"
        assert isinstance(agent["owns"], str) and agent["owns"].strip(), "owns must name an integration"
    assert isinstance(agent["eval_set"], str) and agent["eval_set"].strip(), "eval_set must name a file"
    for field in _EMPTY_LIST_FIELDS:
        values = agent[field]
        assert isinstance(values, list), f"{field} must be a list"
        assert all(isinstance(value, str) and value.strip() for value in values), f"invalid {field} item"
        assert len(values) == len(set(values)), f"duplicate {field}"
    assert all(platform in _HOME_PLATFORMS for platform in agent["shadows"]), "invalid shadow platform"
    assert agent["home_platform"] not in agent["shadows"], "home cannot be a shadow"
    assert all(_AGENT_NAME.fullmatch(name) for name in agent["connectors"]), "invalid connector name"
    assert agent["name"] not in agent["connectors"], "agent cannot call itself as a connector"
    code_tools = {"github.git.create_blob", "github.git.create_tree", "github.git.create_commit", "github.git.update_ref"}
    if code_tools.intersection(agent["tools"]):
        assert agent["code_work"] == "sandbox", "code editing requires sandbox"
    validate_triggers(agent)

@pytest.fixture
def agent_v2():
    return _definitions()[0][1]


@pytest.mark.parametrize("tier", [0, 1, 2])
@pytest.mark.parametrize("platform", sorted(_HOME_PLATFORMS))
@pytest.mark.parametrize("privacy", ["public", "internal", "private"])
def test_valid_v2_routing_fixtures(agent_v2, tier, platform, privacy):
    agent_v2.update(tier=tier, home_platform=platform, shadows=[], privacy_class=privacy)
    _validate_v2(agent_v2)


@pytest.mark.parametrize("mode", ["shadow", "live"])
@pytest.mark.parametrize("code_work", ["none", "sandbox"])
def test_valid_v2_execution_fixtures(agent_v2, mode, code_work):
    agent_v2.update(mode=mode, code_work=code_work)
    _validate_v2(agent_v2)


def test_v2_privacy_defaults_to_private(agent_v2):
    del agent_v2["privacy_class"]
    _validate_v2(agent_v2)
    assert agent_v2.get("privacy_class", "private") == "private"


def test_valid_connector_fixture(agent_v2):
    agent_v2.update(kind="connector", owns="example", connectors=["example-clerk"])
    _validate_v2(agent_v2)


@pytest.mark.parametrize("field", _ROSTER_FIELDS)
def test_v2_rejects_missing_required_fields(agent_v2, field):
    del agent_v2[field]
    with pytest.raises(AssertionError, match="missing required"):
        _validate_v2(agent_v2)


@pytest.mark.parametrize("updates", [
    {"name": "gpu-fill"}, {"name": "FILL-worker"}, {"name": "backfill"}, {"name": 1},
    {"tier": -1}, {"tier": 3}, {"tier": "1"}, {"tier": True}, {"tier": 1.0},
    {"home_platform": "hatchet"}, {"home_platform": []},
    {"shadows": "sim"}, {"shadows": ["hatchet"]}, {"shadows": ["dify"]},
    {"shadows": ["sim", "sim"]}, {"shadows": [None]},
    {"privacy_class": "public-code"}, {"privacy_class": None},
    {"connectors": "example-clerk"}, {"connectors": [None]},
    {"connectors": ["example-clerk", "example-clerk"]},
    {"connectors": ["action-extractor"]}, {"connectors": ["bad name"]},
    {"owns": "example"}, {"kind": "agent", "owns": "example"},
    {"kind": "connector", "owns": ""}, {"kind": "connector", "owns": []}, {"kind": "worker"},
    {"code_work": "direct"}, {"code_work": None},
    {"tools": ["github.git.create_blob"], "code_work": "none"},
    {"mode": "draft"}, {"mode": None},
    {"eval_set": ""}, {"eval_set": None}, {"eval_set": []}, {"eval_set": " "},
    {"triggers": []}, {"triggers": {}}, {"triggers": [None]},
    {"trigger": {"kind": "call"}},
])
def test_invalid_v2_definition_fixtures(agent_v2, updates):
    agent_v2.update(updates)
    with pytest.raises(AssertionError):
        _validate_v2(agent_v2)


def test_code_editing_fixture_requires_sandbox(agent_v2):
    agent_v2.update(tools=["github.git.create_blob"], code_work="sandbox")
    _validate_v2(agent_v2)


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
    expected = [] if empty == [] and field in _EMPTY_LIST_FIELDS else [field]
    assert _missing_roster_fields(broken) == expected


@pytest.mark.parametrize("path,agent", _definitions(), ids=lambda item: item.stem if isinstance(item, Path) else None)
def test_every_definition_conforms_to_v2(path, agent):
    _validate_v2(agent)
    assert path.stem == agent["name"]


def test_roster_passes_profile_and_authoring_standards():
    records = resolved_records()
    for record in records:
        agent = record["agent"]
        source = yaml.safe_load((_AGENTS / f"{agent['name']}.yaml").read_text())
        validate_source(source, record["profile"])
        validate_description(agent)
        validate_eval_policy(agent)
        suite = cases.load_suite(_ROOT / agent["eval_set"])
        assert suite["agent"] == agent["name"]
        validate_eval_suite(suite)
    validate_unique_jobs(
        [record["agent"] for record in records],
        [_prompt_body(_ROOT / record["agent"]["prompt"]) for record in records],
    )


def test_code_editing_agents_use_sandbox_jobs():
    for name in ("ci-fixer", "docs-updater"):
        agent = definition(name)
        assert agent["code_work"] == "sandbox"


def test_connector_integration_ownership_is_unique():
    owners = [agent["owns"] for _, agent in _definitions() if "owns" in agent]
    assert len(owners) == len(set(owners))


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
    agent = definition(agent_name)
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
    triggers = [trigger for trigger in agent["triggers"] if trigger["kind"] == "anchor"]
    if triggers:
        assert len(schedules) == 1
        assert schedules[0]["cron_expression"] == "{} {} * * *".format(*reversed(triggers[0]["at"].split(":")))
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
    agent = definition(agent_name)
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
