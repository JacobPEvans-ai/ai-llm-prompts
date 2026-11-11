DIFY_OUTPUT ?= agents/dify
AGENTS_ROOT ?= .
ROTATION_DRIVER_NAME ?= tier2-rotation
export ROTATION_DRIVER_NAME
INDEX_OUTPUT ?= $(AGENTS_ROOT)/agents/index.md
PROMPT_INDEX_OUTPUT ?= $(AGENTS_ROOT)/agents/prompts/index.md
PYTEST ?= python3 -m pytest
AUTOMATION_ROOT ?= automation
POLICY_PROMPT_OUTPUT ?= $(AUTOMATION_ROOT)
POLICY_RUBRICS := policy-gate security-review semantic-review leak-review
GITHUB_AGENT_PROMPT_OUTPUT ?= $(AUTOMATION_ROOT)
GITHUB_AGENT_PROMPT_FILES := ai-workflows-docs-drift.prompt.yml ai-workflows-dep-review.md
.DEFAULT_GOAL := resolve-agents

.PHONY: render-policy-prompts check-policy-prompts $(addprefix render-policy-prompt-,$(POLICY_RUBRICS))
render-policy-prompts: $(addprefix render-policy-prompt-,$(POLICY_RUBRICS))

$(addprefix render-policy-prompt-,$(POLICY_RUBRICS)): render-policy-prompt-%:
	@mkdir -p "$(POLICY_PROMPT_OUTPUT)"
	@gomplate -c .="$(AUTOMATION_ROOT)/policy-gate-src/$*.yaml" \
		-t rubric="$(AUTOMATION_ROOT)/policy-gate-src/rubric.tmpl" \
		-i '{{ tmpl.Exec "rubric" (dict "name" "$*" "rubric" .) }}' \
		-o "$(POLICY_PROMPT_OUTPUT)/ai-workflows-$*.prompt.yml"

check-policy-prompts:
	@set -eu; output=$$(mktemp -d "$${TMPDIR:-/tmp}/policy-prompts.XXXXXX"); trap 'rm -rf "$$output"' EXIT; \
		mkdir "$$output/committed"; \
		cp $(foreach name,$(POLICY_RUBRICS),"$(AUTOMATION_ROOT)/ai-workflows-$(name).prompt.yml") "$$output/committed/"; \
		$(MAKE) --no-print-directory render-policy-prompts POLICY_PROMPT_OUTPUT="$$output/rendered"; \
		diff -ru "$$output/committed" "$$output/rendered"

.PHONY: render-github-agent-prompts check-github-agent-prompts render-github-agent-prompt-docs-drift render-github-agent-prompt-dep-review
render-github-agent-prompts: render-github-agent-prompt-docs-drift render-github-agent-prompt-dep-review

render-github-agent-prompt-docs-drift:
	@mkdir -p "$(GITHUB_AGENT_PROMPT_OUTPUT)"
	@gomplate -f "$(AUTOMATION_ROOT)/ai-workflows-docs-drift.prompt.yml.tmpl" \
		-o "$(GITHUB_AGENT_PROMPT_OUTPUT)/ai-workflows-docs-drift.prompt.yml"

render-github-agent-prompt-dep-review:
	@mkdir -p "$(GITHUB_AGENT_PROMPT_OUTPUT)"
	@gomplate -f "$(AUTOMATION_ROOT)/ai-workflows-dep-review.md.tmpl" \
		-o "$(GITHUB_AGENT_PROMPT_OUTPUT)/ai-workflows-dep-review.md"

check-github-agent-prompts:
	@set -eu; output=$$(mktemp -d "$${TMPDIR:-/tmp}/github-agent-prompts.XXXXXX"); trap 'rm -rf "$$output"' EXIT; \
		mkdir "$$output/committed"; \
		cp $(foreach file,$(GITHUB_AGENT_PROMPT_FILES),"$(AUTOMATION_ROOT)/$(file)") "$$output/committed/"; \
		$(MAKE) --no-print-directory render-github-agent-prompts GITHUB_AGENT_PROMPT_OUTPUT="$$output/rendered"; \
		diff -ru "$$output/committed" "$$output/rendered"

.PHONY: resolve-agents render-dify check-dify render-sim check-sim render-langflow check-langflow render-index check-index test
resolve-agents:
	@set -eu; cd "$(AGENTS_ROOT)"; for definition in agents/*.yaml; do \
		name=$$(basename "$$definition" .yaml); \
		test "$$(yq -r '.name' "$$definition")" = "$$name"; \
		gomplate -c .="$$definition" -t source="$(CURDIR)/agents/dify-src/agent.tmpl" \
			-i '{{ tmpl.Exec "resolve" . }}{{ "\n" }}'; \
	done

render-dify:
	@mkdir -p "$(DIFY_OUTPUT)"
	@set -eu; name="$$ROTATION_DRIVER_NAME"; \
		case "$$name" in \
			*[!a-z0-9-]*) printf 'ROTATION_DRIVER_NAME must use only lowercase letters, digits, and hyphens, got "%s"\n' "$$name" >&2; exit 1 ;; \
		esac; \
		if [ "$${#name}" -lt 3 ] || [ "$${#name}" -gt 63 ]; then \
			printf 'ROTATION_DRIVER_NAME must be 3 to 63 characters long, got "%s"\n' "$$name" >&2; exit 1; \
		fi
	@set -eu; output=$$(mktemp -d "$${TMPDIR:-/tmp}/agents.XXXXXX"); trap 'rm -rf "$$output"' EXIT; \
		$(MAKE) --no-print-directory resolve-agents > "$$output/definitions.jsonl"; \
		cd "$(AGENTS_ROOT)"; while IFS= read -r definition; do \
			printf '%s\n' "$$definition" | yq '.agent' > "$$output/agent.yaml"; \
			platform=$$(yq -er '.home_platform' "$$output/agent.yaml"); \
			[ "$$platform" = dify ] || continue; \
			name=$$(yq -r '.name' "$$output/agent.yaml"); \
			gomplate -c .="$$output/agent.yaml" -f "$(CURDIR)/agents/dify-src/agent.tmpl" -o "$(abspath $(DIFY_OUTPUT))/$$name.dsl.yml"; \
		done < "$$output/definitions.jsonl"; \
		jq -s 'map(.agent)' "$$output/definitions.jsonl" > "$$output/agents.json"; \
		gomplate -t driver="$(CURDIR)/agents/dify-src/rotation.tmpl" \
			-i '{{ tmpl.Exec "driver-metadata" . }}' > "$$output/driver.json"; \
		driver=$$(jq -r '.name' "$$output/driver.json"); \
		gomplate -c agents="$$output/agents.json" -f "$(CURDIR)/agents/dify-src/rotation.tmpl" \
			-o "$(abspath $(DIFY_OUTPUT))/$$driver.dsl.yml"; \
		jq -c '.[] | select(.home_platform == "dify") | {name, mode, tier, kind: "agent"}' \
			"$$output/agents.json" > "$$output/manifest.jsonl"; \
		jq -c . "$$output/driver.json" >> "$$output/manifest.jsonl"; \
		while IFS= read -r entry; do \
			name=$$(printf '%s\n' "$$entry" | jq -r '.name'); \
			hash=$$(sha256sum "$(abspath $(DIFY_OUTPUT))/$$name.dsl.yml"); \
			printf '%s\n' "$$entry" | jq --arg path "agents/dify/$$name.dsl.yml" \
				--arg sha256 "$${hash%% *}" '. + {path: $$path, sha256: $$sha256}'; \
		done < "$$output/manifest.jsonl" > "$$output/entries.jsonl"; \
		jq -s 'sort_by(.name)' "$$output/entries.jsonl" > "$(abspath $(DIFY_OUTPUT))/manifest.json"

check-dify: check-policy-prompts check-github-agent-prompts
	@set -eu; output=$$(mktemp -d "$${TMPDIR:-/tmp}/dify.XXXXXX"); trap 'rm -rf "$$output"' EXIT; \
		mkdir "$$output/committed"; \
		cp "$(AGENTS_ROOT)"/agents/dify/*.dsl.yml "$$output/committed/"; \
		cp "$(AGENTS_ROOT)/agents/dify/manifest.json" "$$output/committed/"; \
		$(MAKE) --no-print-directory render-dify DIFY_OUTPUT="$$output/rendered"; \
		diff -ru "$$output/committed" "$$output/rendered"

render-sim render-langflow: render-%:
	@mkdir -p "$(or $(SHADOW_OUTPUT),agents/$*)"
	@set -eu; output=$$(mktemp -d "$${TMPDIR:-/tmp}/agents.XXXXXX"); trap 'rm -rf "$$output"' EXIT; \
		$(MAKE) --no-print-directory resolve-agents > "$$output/definitions.jsonl"; \
		cd "$(AGENTS_ROOT)"; while IFS= read -r definition; do \
			printf '%s\n' "$$definition" | yq '.agent' > "$$output/agent.yaml"; \
			home=$$(yq -er '.home_platform' "$$output/agent.yaml"); \
			[ "$$home" = dify ] || continue; \
			shadows=$$(yq -r '(.shadows // []) | join(",")' "$$output/agent.yaml"); \
			case ",$$shadows," in *,$*,*) ;; *) continue ;; esac; \
			name=$$(yq -r '.name' "$$output/agent.yaml"); \
			reason=$$(gomplate -c .="$$output/agent.yaml" -t shadow="$(CURDIR)/agents/sim-src/shared.tmpl" \
				-i '{{ tmpl.Exec "shadow-eligibility" (dict "definition" . "runtime" "$*") }}'); \
			if [ -n "$$reason" ]; then printf 'SKIP | %s | %s | %s\n' '$*' "$$name" "$$reason"; continue; fi; \
			gomplate -c .="$$output/agent.yaml" -t dify="$(CURDIR)/agents/dify-src/agent.tmpl" \
				-t shadow="$(CURDIR)/agents/sim-src/shared.tmpl" \
				-f "$(CURDIR)/agents/$*-src/agent.tmpl" \
				-o "$(abspath $(or $(SHADOW_OUTPUT),agents/$*))/$$name.json"; \
		done < "$$output/definitions.jsonl"

check-sim check-langflow: check-%:
	@set -eu; output=$$(mktemp -d "$${TMPDIR:-/tmp}/$*.XXXXXX"); trap 'rm -rf "$$output"' EXIT; \
		$(MAKE) --no-print-directory render-$* SHADOW_OUTPUT="$$output/rendered"; \
		diff -ru "$(AGENTS_ROOT)/agents/$*" "$$output/rendered"

render-index:
	@set -eu; output=$$(mktemp -d "$${TMPDIR:-/tmp}/catalog.XXXXXX"); trap 'rm -rf "$$output"' EXIT; \
		$(MAKE) --no-print-directory resolve-agents > "$$output/definitions.jsonl"; \
		jq -s 'map(.agent) | sort_by(.name)' "$$output/definitions.jsonl" > "$$output/agents.json"; \
		gomplate -c agents="$$output/agents.json" -f "$(CURDIR)/agents/catalog-src/index.tmpl" -o "$(abspath $(INDEX_OUTPUT))"; \
		gomplate -c agents="$$output/agents.json" -f "$(CURDIR)/agents/catalog-src/prompts.tmpl" -o "$(abspath $(PROMPT_INDEX_OUTPUT))"

check-index:
	@set -eu; output=$$(mktemp -d "$${TMPDIR:-/tmp}/catalog.XXXXXX"); trap 'rm -rf "$$output"' EXIT; \
		$(MAKE) --no-print-directory render-index INDEX_OUTPUT="$$output/index.md" PROMPT_INDEX_OUTPUT="$$output/prompts.md"; \
		diff -u "$(AGENTS_ROOT)/agents/index.md" "$$output/index.md"; \
		diff -u "$(AGENTS_ROOT)/agents/prompts/index.md" "$$output/prompts.md"

test: check-dify check-sim check-langflow check-index
	$(PYTEST) -q agents/judges
