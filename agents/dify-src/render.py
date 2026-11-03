"""Render the committed Dify workflow DSLs from templates and agent prompts."""

import argparse
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / "agents"
SOURCE_ROOT = AGENTS / "dify-src"
OUTPUT_ROOT = AGENTS / "dify"
SYSTEM_PROMPT_MARKER = "__DIFY_SYSTEM_PROMPT__"
AGENT_NAME_MARKER = "__DIFY_AGENT_NAME__"
LITELLM_ROLE_MARKER = "__DIFY_LITELLM_ROLE__"
TRIGGER_CRON_MARKER = "__DIFY_TRIGGER_CRON__"
MODE_MARKER = "__DIFY_MODE__"
MCP_SERVER_MARKER = "__DIFY_MCP_SERVER__"
TOOL_NAME_MARKER = "__DIFY_TOOL_NAME__"
TOOL_OPERATIONS_MARKER = "__DIFY_TOOL_OPERATIONS__"
GITHUB_TOKEN_REF_MARKER = "__DIFY_GITHUB_TOKEN_REF__"
# Shared code-node helpers: each marker line is replaced by the helper source at the marker's indent.
HELPER_MARKERS = {"__DIFY_HELPER_JSON_FENCE__": SOURCE_ROOT / "helpers" / "json_fence.py"}

sys.path.insert(0, str(AGENTS / "evals" / "promptfoo"))
sys.dont_write_bytecode = True
from generate import load_yaml, prompt_body  # noqa: E402


def _repo_file(value, field):
    if not isinstance(value, str) or not value:
        raise ValueError(f"agent definition has no path for {field}")
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f"{field} does not name a repository file: {value}")
    return path


def _system_prompt(agent):
    shared_prefix = _repo_file(agent.get("shared_prefix"), "shared_prefix")
    canonical_prompt = _repo_file(agent.get("prompt"), "prompt")
    prompt = "\n\n".join((prompt_body(shared_prefix).rstrip(), prompt_body(canonical_prompt).strip()))
    return prompt, f"{agent['shared_prefix']} + {agent['prompt']}"


def _template(name):
    # Zero-padded fragment names keep the source YAML in byte order after cap-driven splitting.
    fragments = sorted((SOURCE_ROOT / name).glob("*.dsl.yml.tmpl"))
    if not fragments:
        raise ValueError(f"no Dify template fragments found for {name}")
    return "".join(path.read_text() for path in fragments)


def _tool_contract(agent):
    servers = agent.get("mcp_servers", [])
    if not servers:
        return {}
    if not isinstance(servers, list) or len(servers) != 1 or not isinstance(servers[0], str):
        raise ValueError("Dify MCP tool templates require exactly one declared MCP server")

    tools = agent.get("tools")
    if not isinstance(tools, list) or not tools:
        raise ValueError("Dify MCP tool templates require a non-empty tools list")
    tool_parts = [tool.split(".", 1) for tool in tools if isinstance(tool, str) and "." in tool]
    if len(tool_parts) != len(tools) or any(not part for pair in tool_parts for part in pair):
        raise ValueError("Dify MCP tools must use tool.operation names")
    tool_names = {name for name, _ in tool_parts}
    if len(tool_names) != 1:
        raise ValueError("Dify MCP tool templates require one declared tool name")

    operations = [operation for _, operation in tool_parts]
    if len(operations) != len(set(operations)):
        raise ValueError("Dify MCP tool operations must be unique")
    replacements = {
        MCP_SERVER_MARKER: servers[0],
        TOOL_NAME_MARKER: next(iter(tool_names)),
        TOOL_OPERATIONS_MARKER: "{" + ", ".join(repr(operation) for operation in sorted(operations)) + "}",
    }
    replacements.update(
        {f"__DIFY_TOOL_OPERATION_{operation.upper()}__": operation for operation in operations}
    )
    return replacements


def _expand_helpers(template):
    """Replace each helper marker line with the helper source, indented to the marker's indent."""
    for marker, source in HELPER_MARKERS.items():
        body = source.read_text().rstrip("\n").splitlines()
        pattern = re.compile(r"(?m)^([ \t]*)" + re.escape(marker) + r"$")
        template = pattern.sub(
            lambda match: "\n".join(f"{match.group(1)}{line}" if line else "" for line in body),
            template,
        )
    return template


def render_agent(definition_path):
    name = definition_path.stem
    agent = load_yaml(definition_path)
    if not isinstance(agent, dict) or agent.get("name") != name:
        raise ValueError(f"{definition_path.relative_to(ROOT)} must define name: {name}")

    template = _expand_helpers(_template(name))
    prompt, prompt_sources = _system_prompt(agent)

    replacements = {
        AGENT_NAME_MARKER: agent["name"],
        LITELLM_ROLE_MARKER: agent.get("litellm_role"),
    }
    required_markers = {AGENT_NAME_MARKER, LITELLM_ROLE_MARKER}

    trigger = agent.get("trigger", {})
    if trigger.get("kind") == "schedule":
        replacements[TRIGGER_CRON_MARKER] = trigger.get("cron")
        required_markers.add(TRIGGER_CRON_MARKER)
    elif TRIGGER_CRON_MARKER in template:
        raise ValueError(f"{name} template declares a schedule but its agent does not")

    if MODE_MARKER in template or re.search(r"\bname:\s*[A-Z0-9_]*MODE\b", template):
        replacements[MODE_MARKER] = agent.get("mode")
        required_markers.add(MODE_MARKER)

    tool_replacements = _tool_contract(agent)
    if tool_replacements:
        replacements.update(tool_replacements)
        required_markers.update((MCP_SERVER_MARKER, TOOL_NAME_MARKER, TOOL_OPERATIONS_MARKER))
    elif any(marker in template for marker in (MCP_SERVER_MARKER, TOOL_NAME_MARKER, TOOL_OPERATIONS_MARKER)):
        raise ValueError(f"{name} template declares MCP tools but its agent has none")

    github_reader = agent.get("github_reader")
    if github_reader is not None:
        replacements[GITHUB_TOKEN_REF_MARKER] = github_reader.get("github_token_ref")
        required_markers.add(GITHUB_TOKEN_REF_MARKER)

    for marker, value in replacements.items():
        if marker not in template:
            if marker in required_markers:
                raise ValueError(f"{name} template is missing the {marker} placeholder")
            continue
        if not isinstance(value, str) or not value:
            raise ValueError(f"{name} has no value for {marker}")
        template = template.replace(marker, value)

    unresolved = [
        marker
        for marker in re.findall(r"__DIFY_[A-Z0-9_]+__", template)
        if marker != SYSTEM_PROMPT_MARKER
    ]
    if unresolved:
        raise ValueError(f"{name} template has unresolved placeholders: {sorted(set(unresolved))}")

    markers = list(re.finditer(r"(?m)^([ \t]*)" + re.escape(SYSTEM_PROMPT_MARKER) + r"$", template))
    if len(markers) != 1:
        raise ValueError(f"{name} template must contain exactly one system-prompt placeholder")

    marker = markers[0]
    indent = marker.group(1)
    replacement = "\n".join(f"{indent}{line}" if line else "" for line in prompt.splitlines())
    rendered_template = template[: marker.start()] + replacement + template[marker.end() :]
    header = (
        f"# Generated from agents/{name}.yaml, agents/dify-src/{name}/, and {prompt_sources}; "
        "edit sources, then rerun agents/dify-src/render.py.\n"
    )
    return OUTPUT_ROOT / f"{name}.dsl.yml", header + rendered_template


def render_all():
    outputs = []
    for definition_path in sorted(AGENTS.glob("*.yaml")):
        outputs.append(render_agent(definition_path))
    if not outputs:
        raise ValueError("no agent definitions found")
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if any committed DSL differs from rendered output")
    args = parser.parse_args()

    try:
        outputs = render_all()
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Dify renderer error: {error}", file=sys.stderr)
        return 2

    if args.check:
        mismatches = [
            path.relative_to(ROOT)
            for path, rendered in outputs
            if not path.is_file() or path.read_bytes() != rendered.encode("utf-8")
        ]
        if mismatches:
            print("Dify DSL render check failed:", file=sys.stderr)
            for path in mismatches:
                print(f"  {path}", file=sys.stderr)
            return 1
        print(f"Dify DSL render check passed ({len(outputs)} workflows).")
        return 0

    for path, rendered in outputs:
        path.write_bytes(rendered.encode("utf-8"))
    print(f"Rendered {len(outputs)} Dify workflows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
