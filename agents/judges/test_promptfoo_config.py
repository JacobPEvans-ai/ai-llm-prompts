"""Contract test for the Promptfoo local provider's request priority."""

from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[2]
_CONFIG = _ROOT / "agents" / "evals" / "promptfoo" / "promptfooconfig.yaml"


def _local_provider_config():
    config = yaml.safe_load(_CONFIG.read_text())
    provider = next(
        provider for provider in config["providers"] if provider.get("label") == "local"
    )
    return provider["config"]


def test_local_provider_sends_low_scheduling_priority():
    passthrough = _local_provider_config()["passthrough"]

    assert passthrough["priority"] == 100
    assert passthrough["chat_template_kwargs"] == {"enable_thinking": False}
