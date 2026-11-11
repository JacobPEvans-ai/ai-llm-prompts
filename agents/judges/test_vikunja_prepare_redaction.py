"""The rendered vikunja-triage prepare node redacts fetched task text before the LLM node.

Property. A credential inside a fetched task's text reaches the model input only as [REDACTED].
"""

import json

from dify_nodes import node_main


# Built from parts so no credential-shaped literal is written to the file.
TOKEN = "ghp_" + "K" * 30


def test_fetched_task_secrets_are_redacted_before_the_model():
    task = {
        "id": 7,
        "title": "Rotate the leaked deploy credential",
        "description": f"token {TOKEN} reported in CI logs",
    }
    result = node_main("vikunja-triage", "prepare")(
        results=[json.dumps({"project_id": "p1", "tasks": [task]})],
        policy_ok=True,
        timestamp="1794312000",
        web_host="github.example",
        api_base="https://api.github.example",
        bao_addr="",
        role_id="role",
        secret_id="secret",
        token_path="github-token/vikunja-triage",
    )
    model_tasks = result["model_tasks"]
    assert TOKEN not in model_tasks and "[REDACTED]" in model_tasks
    payload = json.loads(model_tasks)
    assert payload["tasks"][0]["title"] == "Rotate the leaked deploy credential"
    assert payload["tasks"][0]["description"] == "token [REDACTED] reported in CI logs"
