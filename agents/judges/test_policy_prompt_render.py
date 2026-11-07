"""Check policy prompt rendering and CI drift rejection through Make."""

import json
import shutil

import pytest
import yaml

from test_dify_render import ROOT, run_make


AUTOMATION = ROOT / "automation"
SOURCES = AUTOMATION / "policy-gate-src"


def test_policy_prompts_match_shared_template(tmp_path):
    result = run_make("render-policy-prompts", f"POLICY_PROMPT_OUTPUT={tmp_path}")
    assert result.returncode == 0, result.stderr
    expected = {f"ai-workflows-{path.stem}.prompt.yml" for path in SOURCES.glob("*.yaml")}
    assert {path.name for path in tmp_path.iterdir()} == expected
    for name in expected:
        rendered = tmp_path / name
        assert rendered.read_bytes() == (AUTOMATION / name).read_bytes(), name
        prompt = yaml.safe_load(rendered.read_text())
        schema = json.loads(prompt["jsonSchema"])
        properties = schema["schema"]["properties"]["findings"]["items"]["properties"]
        rubric = name.removeprefix("ai-workflows-").removesuffix(".prompt.yml")
        inputs = yaml.safe_load((SOURCES / f"{rubric}.yaml").read_text())
        assert set(inputs) == {"header", "system", "checks"}
        assert prompt["messages"][0]["content"] == inputs["system"]
        assert properties["check"]["enum"] == inputs["checks"]
        assert properties["result"]["enum"] == (["fail"] if rubric == "leak-review" else ["pass", "fail"])


@pytest.mark.parametrize("changed", ["rendered", "template", "input"])
def test_ci_check_rejects_policy_prompt_drift(tmp_path, changed):
    automation = tmp_path / "automation"
    shutil.copytree(SOURCES, automation / "policy-gate-src")
    for source in SOURCES.glob("*.yaml"):
        name = f"ai-workflows-{source.stem}.prompt.yml"
        shutil.copyfile(AUTOMATION / name, automation / name)
    args = (f"AUTOMATION_ROOT={automation}",)
    baseline = run_make("check-policy-prompts", *args)
    assert baseline.returncode == 0, baseline.stderr

    if changed == "rendered":
        path = automation / "ai-workflows-security-review.prompt.yml"
        path.write_text(path.read_text() + "# Hand edit.\n")
    elif changed == "template":
        path = automation / "policy-gate-src/rubric.tmpl"
        path.write_text(path.read_text().replace('"strict": true', '"strict": false'))
    else:
        path = automation / "policy-gate-src/security-review.yaml"
        path.write_text(path.read_text().replace("You review", "You inspect", 1))

    result = run_make("check-dify", *args)
    assert result.returncode != 0
    assert "ai-workflows-security-review.prompt.yml" in result.stdout
    assert "check-policy-prompts" in result.stderr


def test_policy_input_template_expressions_stay_literal(tmp_path):
    sources = tmp_path / "policy-gate-src"
    shutil.copytree(SOURCES, sources)
    path = sources / "security-review.yaml"
    marker = '{{ file.Read "does-not-exist" }}'
    path.write_text(path.read_text().replace("You review", marker, 1))
    result = run_make("render-policy-prompts", f"AUTOMATION_ROOT={tmp_path}")
    assert result.returncode == 0, result.stderr
    prompt = yaml.safe_load((tmp_path / "ai-workflows-security-review.prompt.yml").read_text())
    assert marker in prompt["messages"][0]["content"]
    assert prompt["messages"][1]["content"] == "CHANGED FILES:\n{{changed}}\n\nDIFF:\n{{diff}}"
