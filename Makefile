DIFY_OUTPUT ?= agents/dify
AGENTS_ROOT ?= .

.PHONY: render-dify check-dify render-sim check-sim render-langflow check-langflow test
render-dify:
	@mkdir -p "$(DIFY_OUTPUT)"
	@set -eu; cd "$(AGENTS_ROOT)"; for definition in agents/*.yaml; do \
		home=$$(yq -er '.home_platform' "$$definition"); \
		[ "$$home" = dify ] || continue; \
		name=$$(basename "$$definition" .yaml); \
		test "$$(yq -r '.name' "$$definition")" = "$$name"; \
		gomplate -c .="$$definition" -f "$(CURDIR)/agents/dify-src/agent.tmpl" -o "$(abspath $(DIFY_OUTPUT))/$$name.dsl.yml"; \
	done; \
		gomplate -f "$(CURDIR)/agents/dify-src/rotation.tmpl" \
		-o "$(abspath $(DIFY_OUTPUT))/tier2-rotation.dsl.yml"

check-dify:
	@set -eu; output=$$(mktemp -d "$${TMPDIR:-/tmp}/dify.XXXXXX"); trap 'rm -rf "$$output"' EXIT; \
		mkdir "$$output/committed"; \
		cp "$(AGENTS_ROOT)"/agents/dify/*.dsl.yml "$$output/committed/"; \
		$(MAKE) --no-print-directory render-dify DIFY_OUTPUT="$$output/rendered"; \
		diff -ru "$$output/committed" "$$output/rendered"

render-sim render-langflow: render-%:
	@mkdir -p "$(or $(SHADOW_OUTPUT),agents/$*)"
	@set -eu; cd "$(AGENTS_ROOT)"; for definition in agents/*.yaml; do \
		home=$$(yq -er '.home_platform' "$$definition"); \
		[ "$$home" = dify ] || continue; \
		shadows=$$(yq -r '(.shadows // []) | join(",")' "$$definition"); \
		case ",$$shadows," in *,$*,*) ;; *) continue ;; esac; \
		name=$$(basename "$$definition" .yaml); \
		test "$$(yq -r '.name' "$$definition")" = "$$name"; \
		reason=$$(gomplate -c .="$$definition" -t shadow="$(CURDIR)/agents/sim-src/shared.tmpl" \
			-i '{{ tmpl.Exec "shadow-eligibility" (dict "definition" . "runtime" "$*") }}'); \
		if [ -n "$$reason" ]; then printf 'SKIP | %s | %s | %s\n' '$*' "$$name" "$$reason"; continue; fi; \
		gomplate -c .="$$definition" -t dify="$(CURDIR)/agents/dify-src/agent.tmpl" \
			-t shadow="$(CURDIR)/agents/sim-src/shared.tmpl" \
			-f "$(CURDIR)/agents/$*-src/agent.tmpl" \
			-o "$(abspath $(or $(SHADOW_OUTPUT),agents/$*))/$$name.json"; \
	done

check-sim check-langflow: check-%:
	@set -eu; output=$$(mktemp -d "$${TMPDIR:-/tmp}/$*.XXXXXX"); trap 'rm -rf "$$output"' EXIT; \
		$(MAKE) --no-print-directory render-$* SHADOW_OUTPUT="$$output/rendered"; \
		diff -ru "$(AGENTS_ROOT)/agents/$*" "$$output/rendered"

test: check-dify check-sim check-langflow
	python3 -m pytest -q agents/judges
