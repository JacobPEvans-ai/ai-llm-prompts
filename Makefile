DIFY_OUTPUT ?= agents/dify
AGENTS_ROOT ?= .
PYTEST ?= python3 -m pytest

.PHONY: resolve-agents render-dify check-dify test
resolve-agents:
	@set -eu; cd "$(AGENTS_ROOT)"; for definition in agents/*.yaml; do \
		name=$$(basename "$$definition" .yaml); \
		test "$$(yq -r '.name' "$$definition")" = "$$name"; \
		gomplate -c .="$$definition" -t source="$(CURDIR)/agents/dify-src/agent.tmpl" \
			-i '{{ tmpl.Exec "resolve" . }}{{ "\n" }}'; \
	done

render-dify:
	@mkdir -p "$(DIFY_OUTPUT)"
	@set -eu; output=$$(mktemp -d "$${TMPDIR:-/tmp}/agents.XXXXXX"); trap 'rm -rf "$$output"' EXIT; \
		$(MAKE) --no-print-directory resolve-agents > "$$output/definitions.jsonl"; \
		cd "$(AGENTS_ROOT)"; while IFS= read -r definition; do \
			printf '%s\n' "$$definition" | yq '.agent' > "$$output/agent.json"; \
			home=$$(yq -er '.home_platform' "$$output/agent.json"); \
			[ "$$home" = dify ] || continue; \
			name=$$(yq -r '.name' "$$output/agent.json"); \
			gomplate -c .="$$output/agent.json" -f "$(CURDIR)/agents/dify-src/agent.tmpl" -o "$(abspath $(DIFY_OUTPUT))/$$name.dsl.yml"; \
		done < "$$output/definitions.jsonl"

check-dify:
	@set -eu; output=$$(mktemp -d "$${TMPDIR:-/tmp}/dify.XXXXXX"); trap 'rm -rf "$$output"' EXIT; \
		mkdir "$$output/committed"; \
		cp "$(AGENTS_ROOT)"/agents/dify/*.dsl.yml "$$output/committed/"; \
		$(MAKE) --no-print-directory render-dify DIFY_OUTPUT="$$output/rendered"; \
		diff -ru "$$output/committed" "$$output/rendered"

test: check-dify
	$(PYTEST) -q agents/judges
