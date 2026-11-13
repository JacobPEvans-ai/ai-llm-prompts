"""Shared loader and fixtures for the judge tests that run Dify Code nodes.

node_main(workflow, node_id) returns the main function of a Code node, executed from its copy in
agents/dify/<workflow>.dsl.yml. Each call runs in a fresh namespace, so a test that patches a module-level
flag on the returned function does not change any other call.
"""

import functools
from pathlib import Path

import yaml


_DIFY = Path(__file__).resolve().parents[2] / "agents" / "dify"

REPO = "jpe-ai-agents/ai-llm-prompts"
SHA = "a" * 40
OTHER_SHA = "e" * 40
PR_NUMBER = 7
# Built from parts so no credential-shaped literal is written to the file. The node's secret scan must match it.
SECRET = "AKIA" + "ABCDEFGH" + "IJKLMNOP"


@functools.lru_cache(maxsize=None)
def _nodes(workflow):
    dsl = yaml.safe_load((_DIFY / f"{workflow}.dsl.yml").read_text())
    return {node["id"]: node["data"] for node in dsl["workflow"]["graph"]["nodes"]}


def node_main(workflow, node_id):
    namespace = {}
    exec(
        compile(_nodes(workflow)[node_id]["code"], f"{workflow}:{node_id}", "exec"),
        namespace,
    )  # defines functions only
    return namespace["main"]
