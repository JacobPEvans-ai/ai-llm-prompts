DIFY_OUTPUT ?= agents/dify
AGENTS_ROOT ?= .

.PHONY: render-dify check-dify test
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

test: check-dify
	python3 -m pytest -q agents/judges
