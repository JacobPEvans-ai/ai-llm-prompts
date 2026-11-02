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
    exception = agent.get("dify_system_prompt_exception")
    if exception is not None:
        if not isinstance(exception, dict) or not exception.get("node") or not exception.get("reason"):
            raise ValueError("dify_system_prompt_exception must declare a node and reason")
        source = _repo_file(exception.get("source"), "dify_system_prompt_exception.source")
        try:
            source.relative_to(SOURCE_ROOT)
        except ValueError as error:
            raise ValueError("Dify system-prompt exceptions must use a source under agents/dify-src/") from error
        prompt = source.read_text().strip()
        if not prompt:
            raise ValueError(f"Dify system-prompt exception source is empty: {source.relative_to(ROOT)}")
        return prompt, exception["source"]

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


def render_agent(definition_path):
    name = definition_path.stem
    agent = load_yaml(definition_path)
    if not isinstance(agent, dict) or agent.get("name") != name:
        raise ValueError(f"{definition_path.relative_to(ROOT)} must define name: {name}")

    template = _template(name)
    markers = list(re.finditer(r"(?m)^([ \t]*)" + re.escape(SYSTEM_PROMPT_MARKER) + r"$", template))
    if len(markers) != 1:
        raise ValueError(f"{name} template must contain exactly one system-prompt placeholder")

    prompt, prompt_sources = _system_prompt(agent)
    marker = markers[0]
    indent = marker.group(1)
    replacement = "\n".join(f"{indent}{line}" if line else "" for line in prompt.splitlines())
    rendered_template = template[: marker.start()] + replacement + template[marker.end() :]
    header = (
        f"# Generated from agents/dify-src/{name}/ and {prompt_sources}; "
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
            if not path.is_file() or path.read_text() != rendered
        ]
        if mismatches:
            print("Dify DSL render check failed:", file=sys.stderr)
            for path in mismatches:
                print(f"  {path}", file=sys.stderr)
            return 1
        print(f"Dify DSL render check passed ({len(outputs)} workflows).")
        return 0

    for path, rendered in outputs:
        path.write_text(rendered)
    print(f"Rendered {len(outputs)} Dify workflows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
