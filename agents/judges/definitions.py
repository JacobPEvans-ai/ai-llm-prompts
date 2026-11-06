"""Read the same gomplate resolution output used by make render-dify."""

from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]


def resolve_records(root=ROOT):
    result = subprocess.run(
        ["make", "--no-print-directory", "resolve-agents", f"AGENTS_ROOT={root}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [json.loads(line) for line in result.stdout.splitlines()]


@lru_cache(maxsize=1)
def _roster():
    return resolve_records()


def definitions():
    return [(ROOT / "agents" / f"{record['agent']['name']}.yaml", deepcopy(record["agent"])) for record in _roster()]


def definition(name):
    return next(agent for path, agent in definitions() if path.stem == name)
