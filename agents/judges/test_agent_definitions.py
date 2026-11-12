"""Contract tests for the homelab agent roster and canonical prompt copies."""

from pathlib import Path
import re
import shutil

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


_DELIVERY_FIELDS = {"kind", "channel_env", "token_env", "failure_channel_env", "dashboard_url_env", "max_chars", "thread", "input_from"}
_DELIVERY_OPTIONAL = {"error_from"}
_ENV_NAME = re.compile(r"[A-Z][A-Z0-9_]*")


def validate_delivery(agent):
    """Optional Slack thread delivery. The renderer asserts the same rules when it renders the DSL."""
    if "delivery" not in agent:
        return
    delivery = agent["delivery"]
    assert isinstance(delivery, dict) and _DELIVERY_FIELDS <= set(delivery) <= _DELIVERY_FIELDS | _DELIVERY_OPTIONAL, (
        "delivery fields must match the contract"
    )
    assert delivery["kind"] == "slack_thread", "delivery kind must be slack_thread"
    assert delivery["thread"] == "daily_parent", "delivery thread must be daily_parent"
    envs = [delivery[field] for field in ("channel_env", "token_env", "failure_channel_env", "dashboard_url_env")]
    assert all(isinstance(env, str) and _ENV_NAME.fullmatch(env) for env in envs), "delivery env names must be uppercase"
    assert len(set(envs)) == len(envs), "delivery env names must be distinct"
    assert delivery["failure_channel_env"] != delivery["channel_env"], "failure channel env must differ from the delivery channel env"
    max_chars = delivery["max_chars"]
    assert type(max_chars) is int and 100 <= max_chars <= 10000, "delivery max_chars must be from 100 to 10000"
    for field in ("input_from", "error_from"):
        if field not in delivery:
            continue
        source = delivery[field]
        assert isinstance(source, list) and len(source) == 2 and all(isinstance(part, str) and part for part in source), (
            f"delivery {field} must name a node and an output"
        )


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
    validate_delivery(agent)

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


def test_triggered_agents_name_their_reader_and_acted_signal():
    """An agent started by an event, rotation or anchor names who reads its output and the signal that it was acted on."""
    offenders = [
        agent["name"]
        for _, agent in _definitions()
        if {trigger.get("kind") for trigger in agent.get("triggers", [])} & {"event", "rotation", "anchor"}
        and not all(isinstance(agent.get(field), str) and agent[field].strip() for field in ("reader", "acted_signal"))
    ]
    assert offenders == [], f"triggered agents must declare reader and acted_signal: {offenders}"


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
    for name in ("pr-keeper", "docs-updater"):
        agent = definition(name)
        assert agent["code_work"] == "sandbox"


def test_connector_integration_ownership_is_unique():
    owners = [agent["owns"] for _, agent in _definitions() if "owns" in agent]
    assert len(owners) == len(set(owners))


def _validate_prompt_handoffs(agent, body, roster):
    """Require gateway peers for every other roster name mentioned in a prompt."""
    names = "|".join(re.escape(name) for name in sorted(roster, key=len, reverse=True))
    handoffs = set(re.findall(
        rf"\b({names})\b",
        body.lower(),
    )) - {agent["name"]}
    declared = set(agent.get("connectors", [])) | set(agent.get("peers", []))
    assert handoffs <= declared, f"{agent['name']}: undeclared handoff peers: {sorted(handoffs - declared)}"
    if handoffs:
        assert "a2a.call" in agent["tools"], f"{agent['name']}: handoffs require a2a.call"


@pytest.mark.parametrize("path,agent", _definitions(), ids=lambda item: item.stem if isinstance(item, Path) else None)
def test_roster_prompt_handoffs_declare_gateway_peers(path, agent):
    roster = {peer["name"] for _, peer in _definitions()}
    _validate_prompt_handoffs(agent, _prompt_body(_ROOT / agent["prompt"]), roster)


@pytest.mark.parametrize("handoff", [
    "Ask task-clerk to record the remediation.",
    "Coordinate with task-clerk to record the remediation.",
    "Ordinary tasks go to\n task-clerk through A2A.",
    "Hand off to task-clerk.",
    "The task-clerk result is available.",
    "TASK-CLERK supplies a scoped request.",
])
def test_prompt_handoff_fixture_rejects_missing_peer(handoff):
    agent = {"name": "incident-clerk", "tools": ["a2a.call"], "connectors": []}
    with pytest.raises(AssertionError, match="undeclared handoff peers.*task-clerk"):
        _validate_prompt_handoffs(agent, handoff, {"incident-clerk", "task-clerk"})


@pytest.mark.parametrize("field", ["connectors", "peers"])
def test_prompt_handoff_requires_call_tool_even_with_declared_peer(field):
    agent = {"name": "incident-clerk", "tools": [], field: ["task-clerk"]}
    with pytest.raises(AssertionError, match="handoffs require a2a.call"):
        _validate_prompt_handoffs(agent, "Ask task-clerk to record it.", {"task-clerk"})
    agent["tools"] = ["a2a.call"]
    _validate_prompt_handoffs(agent, "Ask task-clerk to record it.", {"task-clerk"})


def test_self_reference_does_not_require_a_peer():
    agent = {"name": "task-clerk", "tools": [], "connectors": []}
    _validate_prompt_handoffs(agent, "You are task-clerk.", {"incident-clerk", "task-clerk"})


def _chain_shared_prefixes(root, agent):
    """shared_prefix values declared by profiles in this definition's extends chain, resolved through
    root's agents/profiles; defaults.yaml joins every chain as its base layer, like make resolve-agents."""
    prefixes = set()
    name = agent.get("extends")
    seen = set()
    while name and name not in seen:
        seen.add(name)
        profile = yaml.safe_load((root / "agents" / "profiles" / f"{name}.yaml").read_text()) or {}
        if profile.get("shared_prefix"):
            prefixes.add(profile["shared_prefix"])
        name = profile.get("extends")
    if seen:
        defaults = yaml.safe_load((root / "agents" / "profiles" / "defaults.yaml").read_text()) or {}
        if defaults.get("shared_prefix"):
            prefixes.add(defaults["shared_prefix"])
    return prefixes


def _roster_paths_and_prompt_metadata(definitions, root=None):
    root = _ROOT if root is None else root
    assert definitions

    roster_prefixes = set()
    for path, agent in definitions:
        assert isinstance(agent, dict), f"{path.name} must contain a YAML mapping"
        missing = _missing_roster_fields(agent)
        assert not missing, f"{path.name} is missing non-empty roster fields: {missing}"

        for field in ("prompt", "eval_set", "shared_prefix"):
            target = _ROOT / agent[field]
            assert target.is_file(), (
                f"{path.name} {field} does not name a file: {agent[field]}"
            )

        _prompt_body(_ROOT / agent["prompt"])
        chain_prefixes = _chain_shared_prefixes(root, agent)
        assert agent["shared_prefix"] in chain_prefixes, (
            f"{path.name} shared_prefix {agent['shared_prefix']} is not declared by a profile in its "
            f"extends chain: {sorted(chain_prefixes)}"
        )
        roster_prefixes.add(agent["shared_prefix"])

    for shared_prefix in sorted(roster_prefixes):
        _prompt_body(_ROOT / shared_prefix)


def test_agent_roster_paths_and_prompt_metadata_are_complete():
    _roster_paths_and_prompt_metadata(_definitions())


def _chain_fixture(name, extends, shared_prefix):
    agent = dict(definition("vikunja-triage"))
    agent.update(name=name, extends=extends, shared_prefix=shared_prefix)
    return Path(f"{name}.yaml"), agent


def test_a_same_chain_definition_with_a_different_prefix_fails():
    base = _chain_fixture("sample-clerk", "connector", "agents/prompts/shared/homelab.md")
    other = _chain_fixture("overlay-clerk", "connector", "agents/prompts/vikunja-clerk.md")
    with pytest.raises(AssertionError, match="not declared by a profile in its extends chain"):
        _roster_paths_and_prompt_metadata([base, other])


def test_an_overlay_profile_may_declare_its_own_shared_prefix(tmp_path):
    profiles = tmp_path / "agents" / "profiles"
    profiles.mkdir(parents=True)
    shutil.copy(_ROOT / "agents" / "profiles" / "defaults.yaml", profiles / "defaults.yaml")
    (profiles / "overlay.yaml").write_text("shared_prefix: agents/prompts/vikunja-clerk.md\n")
    overlay = _chain_fixture("overlay-clerk", "overlay", "agents/prompts/vikunja-clerk.md")

    _roster_paths_and_prompt_metadata([overlay], root=tmp_path)


def test_a_definition_whose_chain_declares_no_prefix_fails(tmp_path):
    profiles = tmp_path / "agents" / "profiles"
    profiles.mkdir(parents=True)
    (profiles / "defaults.yaml").write_text("tier: 0\n")
    (profiles / "overlay.yaml").write_text("tier: 1\n")
    overlay = _chain_fixture("overlay-clerk", "overlay", "agents/prompts/vikunja-clerk.md")
    with pytest.raises(AssertionError, match="not declared by a profile in its extends chain"):
        _roster_paths_and_prompt_metadata([overlay], root=tmp_path)


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


def _declared_mcp_tools(agent, tools):
    servers = agent.get("mcp_servers", [])
    dotted = [tool.split(".", 1) for tool in tools if "." in tool]
    return {
        (prefix, name) for prefix, name in dotted if prefix in servers
    } | {
        (servers[0], prefix)
        for prefix, _ in dotted
        if servers and prefix not in servers and prefix != "a2a"
    } | {
        (servers[0], tool) for tool in tools if servers and "." not in tool
    }


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
    anchors = [trigger for trigger in agent["triggers"] if trigger["kind"] == "anchor"]
    rotations = [trigger for trigger in agent["triggers"] if trigger["kind"] == "rotation"]
    if anchors:
        assert len(schedules) == 1
        days = anchors[0].get("days")
        day_numbers = {day: n for n, day in enumerate(("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"))}
        day_field = ",".join(str(n) for n in sorted(day_numbers[day] for day in days)) if days else "*"
        assert schedules[0]["cron_expression"] == "{} {} * * {}".format(
            *reversed(anchors[0]["at"].split(":")), day_field
        )
    elif rotations and agent["tier"] < 2:
        assert len(schedules) == 1 and schedules[0]["timezone"] == "UTC"
    else:
        assert not schedules

    if "dify" not in agent:
        if agent.get("tools"):
            assert agent["mode"] == "shadow"
        assert {node["data"]["type"] for node in nodes} <= {
            "start", "llm", "end", "trigger-schedule", "trigger-webhook", "code", "if-else", "variable-aggregator"
        }
    elif agent.get("mcp_servers") or "dify_tools" in agent:
        expected_tools = _declared_mcp_tools(agent, agent["tools"])
        actual_tools = {
            (data.get("provider_name"), data.get("tool_name"))
            for node in nodes
            for data in [node.get("data", {})]
            if data.get("type") == "tool"
        }
        if "dify_tools" in agent:
            assert set(agent["dify_tools"]) <= set(agent.get("tools", []))
            expected_dify_tools = _declared_mcp_tools(agent, agent["dify_tools"])
            assert actual_tools == expected_dify_tools
            assert actual_tools <= expected_tools
            if not agent["dify_tools"]:
                tool_nodes = [node for node in nodes if node.get("data", {}).get("type") == "tool"]
                http_nodes = [node["data"] for node in nodes if node.get("data", {}).get("type") == "http-request"]
                assert not tool_nodes
                assert http_nodes and all(data.get("method", "").lower() == "get" for data in http_nodes)
        else:
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


_DELIVERY = {
    "kind": "slack_thread", "channel_env": "AGENT_DIGEST_CHANNEL", "token_env": "SLACK_AGENT_BOT_TOKEN",
    "failure_channel_env": "AGENT_FAILURE_CHANNEL", "dashboard_url_env": "AGENT_DASHBOARD_URL",
    "max_chars": 3000, "thread": "daily_parent", "input_from": ["prepare", "task_refs"],
}


def test_valid_delivery_fixture_and_absent_delivery():
    validate_delivery({"delivery": dict(_DELIVERY)})
    validate_delivery({"delivery": {**_DELIVERY, "error_from": ["guard", "fetch_error"]}})
    validate_delivery({})


@pytest.mark.parametrize("updates", [
    {"kind": "webhook"}, {"thread": "per_run"}, {"channel_env": "agent_digest"},
    {"failure_channel_env": "AGENT_DIGEST_CHANNEL"}, {"token_env": "AGENT_FAILURE_CHANNEL"},
    {"dashboard_url_env": "SLACK_AGENT_BOT_TOKEN"}, {"max_chars": 99}, {"max_chars": 10001},
    {"max_chars": True}, {"input_from": ["prepare"]}, {"input_from": ["prepare", "task_refs", "x"]},
    {"error_from": ["guard"]}, {"error_from": "guard"}, {"extra": "field"},
])
def test_invalid_delivery_fixtures(updates):
    with pytest.raises(AssertionError):
        validate_delivery({"delivery": {**_DELIVERY, **updates}})


def test_pr_keeper_replaces_ci_fixer():
    agent = definition("pr-keeper")
    assert agent["code_work"] == "sandbox"
    assert {"kind": "rotation", "every": "15m"} in agent["triggers"]
    assert {"kind": "event", "source": "github.check_run"} in agent["triggers"]
    for path in (
        "agents/ci-fixer.yaml", "agents/prompts/ci-fixer.md",
        "agents/evals/ci-fixer.yaml", "agents/dify/ci-fixer.dsl.yml",
    ):
        assert not (_ROOT / path).exists()
