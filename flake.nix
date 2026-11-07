{
  description = "Versioned Dryvist LLM prompt catalog";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    claude-code-plugins = {
      url = "github:dryvist/claude-code-plugins?ref=v6";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, claude-code-plugins }:
    let
      systems = [
        "aarch64-darwin"
        "aarch64-linux"
        "x86_64-linux"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
      catalogDirectories = [
        ./auto-ai-agent
        ./automation
        ./applications
        ./developer-tools
      ];
      promptFiles = nixpkgs.lib.concatMap
        (directory:
          builtins.filter
            (path:
              nixpkgs.lib.hasSuffix ".md" (toString path)
              && builtins.baseNameOf (toString path) != "index.md")
            (nixpkgs.lib.filesystem.listFilesRecursive directory))
        catalogDirectories;
      requiredFields = [
        "type"
        "title"
        "description"
        "resource"
        "tags"
        "timestamp"
        "status"
        "consumers"
        "render"
        "source_history"
      ];
      fieldValue = field: path:
        let
          prefix = "${field}:";
          lines = nixpkgs.lib.splitString "\n" (builtins.readFile path);
          matches = builtins.filter (line: nixpkgs.lib.hasPrefix prefix line) lines;
        in
        if matches == [ ] then null else nixpkgs.lib.removePrefix prefix (builtins.head matches);
      validPrompt = path:
        let promptType = nixpkgs.lib.trim (fieldValue "type" path);
        in
        nixpkgs.lib.all (field: fieldValue field path != null) requiredFields
        && builtins.elem promptType [ "LLM Prompt" "LLM Prompt Fragment" ];
      resources = map (path: nixpkgs.lib.trim (fieldValue "resource" path)) promptFiles;
      promptBody = path:
        nixpkgs.lib.concatStringsSep "\n---\n"
          (nixpkgs.lib.drop 1 (nixpkgs.lib.splitString "\n---\n" (builtins.readFile path)));
      bodyHashes = map (path: builtins.hashString "sha256" (promptBody path)) promptFiles;
    in
    {
      packages = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
          instructionsBuilder = pkgs.writeShellApplication {
            name = "render-ai-llm-prompts-instructions";
            runtimeInputs = [ pkgs.coreutils pkgs.findutils pkgs.gawk ];
            text = builtins.readFile ./scripts/render-instructions.sh;
          };
          instructions = pkgs.runCommand "ai-llm-prompts-instructions" {
            nativeBuildInputs = [ instructionsBuilder ];
          } ''
            render-ai-llm-prompts-instructions ${./auto-ai-agent/instructions} "$out"
          '';
          mkCatalog = name: path: pkgs.linkFarm "ai-llm-prompts-${name}" [
            {
              name = "share/ai-llm-prompts/${name}";
              inherit path;
            }
          ];
          auto-ai-agent = mkCatalog "auto-ai-agent" ./auto-ai-agent;
          automation = mkCatalog "automation" ./automation;
          applications = pkgs.runCommand "ai-llm-prompts-applications" { } ''
            mkdir -p $out/share/ai-llm-prompts/applications
            cp -R ${./applications}/. $out/share/ai-llm-prompts/applications/
            chmod -R u+w $out/share/ai-llm-prompts/applications

            rule_file=${instructions}/agentsmd/rules/operating-core.md
            skill_file=${claude-code-plugins}/homelab-ops/skills/monitoring-first/SKILL.md
            rule_count=$(grep -F -c 'Check system state with monitoring first; follow the `monitoring-first` skill before direct shell probes.' "$rule_file")
            test "$rule_count" -eq 1
            monitoring_rule=$(grep -F 'Check system state with monitoring first;' "$rule_file" | sed 's/^- \*\*//; s/\*\*$//')
            test "$(grep -F -c 'name: monitoring-first' "$skill_file")" -eq 1

            prompt=$out/share/ai-llm-prompts/applications/langgraph-homelab-assistant.md
            {
              sed '1,/^---$/d' ${./applications/langgraph-homelab-assistant.md}
              printf '\n\n## Monitoring-first operating rule\n\n%s\n' "$monitoring_rule"
              printf '\n## Monitoring-first procedure\n\n'
              sed '1,/^---$/d' "$skill_file"
            } > "$prompt"

            test "$(grep -F -c 'Check system state with monitoring first; follow the `monitoring-first` skill before direct shell probes.' "$prompt")" -eq 1
            grep -Fq 'Use the monitoring stack to understand current state' "$prompt"
            grep -Fq 'Observability stack' "$prompt"
          '';
          developer-tools = mkCatalog "developer-tools" ./developer-tools;
        in
        {
          inherit auto-ai-agent automation applications developer-tools instructions;
          default = pkgs.symlinkJoin {
            name = "ai-llm-prompts";
            paths = [ auto-ai-agent automation applications developer-tools ];
          };
        });

      checks = forAllSystems (system:
        let pkgs = nixpkgs.legacyPackages.${system};
        in
        self.packages.${system} // {
          agent-tests = pkgs.runCommand "ai-llm-prompts-agent-tests" {
            nativeBuildInputs = [
              pkgs.gnumake
              pkgs.git
              pkgs.gomplate
              pkgs.jq
              pkgs.nodejs
              pkgs.yq
              (pkgs.python3.withPackages (pythonPackages: with pythonPackages; [ pytest pyyaml ]))
            ];
          } ''
            cp -R ${self}/. source
            chmod -R u+w source
            cd source
            make check-dify
            python3 -m pytest -q agents/judges
            touch $out
          '';
          okf = assert nixpkgs.lib.all validPrompt promptFiles;
            assert builtins.length resources == builtins.length (nixpkgs.lib.unique resources);
            assert builtins.length bodyHashes == builtins.length (nixpkgs.lib.unique bodyHashes);
            pkgs.writeText "ai-llm-prompts-okf-validation" "Validated ${toString (builtins.length promptFiles)} unique OKF prompts.\n";
        });

      devShells = forAllSystems (system:
        let pkgs = import nixpkgs { inherit system; };
        in {
          default = pkgs.mkShellNoCC {
            packages = with pkgs; [
              gnumake
              git
              gomplate
              markdownlint-cli2
              nodejs
              pre-commit
              yq-go
              (python3.withPackages (ps: [ ps.pytest ps.pyyaml ]))
            ];
          };
        });

      formatter = forAllSystems (system: nixpkgs.legacyPackages.${system}.nixpkgs-fmt);
    };
}
