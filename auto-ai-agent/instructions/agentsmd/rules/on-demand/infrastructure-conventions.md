---
name: infrastructure-conventions
description: How managed infrastructure is created, changed, named and addressed — rebuild over repair, no manual touches, guest names carry the guest ID, FQDN never a literal IP, named launchd executables. Read before changing any live guest or service.
type: LLM Prompt
title: "Infrastructure conventions"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/infrastructure-conventions"
tags:
  - shared-instructions
  - agent-instructions
timestamp: "2026-10-18T12:18:06-04:00"
status: active
consumers:
  - dryvist/nix-ai
  - dryvist/nix-claude-code
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: dryvist/ai-assistant-instructions
    path: "agentsmd/rules/on-demand/infrastructure-conventions.md"
    note: Migrated from the instruction repository.
---

# Infrastructure conventions

## Rebuild over repair

Resilience comes from being cleanly rebuildable, not from guarding things
against deletion.

Use OpenTofu with the `tofu` command for infrastructure-as-code operations.

- **No destroy-protection and no "don't touch" guards.** No `protection = true`,
  no destroy-blocking preconditions. A guard that stops a rebuild is a guard
  that hides the fact that the rebuild no longer works.
- Irreplaceable data lives on a persistent dataset. Configuration management
  reconstructs everything else.
- Prefer rebuild-from-source over snapshot restore. A snapshot restores the
  drift along with the service.

## Every component runs in 10 minutes or less

- Break every change into individual components. Each component must be able to run on its own in development in
  10 minutes or less. Promotions from develop to main are the only exception.
- If any other session ever needs to do one part of your work, that part must also be able to run on its own in
  10 minutes or less.
- A full run that chains components may take longer, though ideally it does not.
- Always build DRY, reusable modules, across repos and within each repo. Any repo may be split into several.

## Never manually touch a live guest

No SSH in and run, no one-off container exec, no hand-edited inventory pointing
at a temporary lease address.

The order is fixed: infrastructure-as-code creates the shell with a
deterministic hardware address, then a fixed address reservation, then the DNS
record, then configuration management converges it by FQDN.

Needing a manual touch is a gap in the automation. Fix the gap; do not perform
the touch and move on. If you do intervene by hand, record the automation gap
before you continue — not later.

## Unrecoverable resources

- **Check before spending.** Before a path spends a resource that only a reboot
  can restore, check every known edge case. Never “try and see” when trying
  spends it.
- **Keep recovery reboot-independent.** Log each decision made by a guard that can block or halt recovery.
- **Keep cluster lifecycle automation AI-free.** If an agent finds a manual step is needed, file the automation
  gap in the task tracker before continuing.

## Always FQDN, never a hardcoded IP

In code, in documentation, and in interactive commands. Addresses are derived
from the network segment plus a host identifier, so a literal breaks silently
the moment a host moves segments. The only legitimate address literal is the
DNS record itself.

## Guest names carry the guest ID

Every guest is named `<app>-<guest-id>`: the hypervisor name, the hostname,
the configuration-management inventory name and the DNS label. The name is
generated from the infrastructure-as-code entry, never hand-picked. Never add an
ordinal name (`-1`, `-2`, `-01`) to a new guest.

An existing guest with an ordinal name moves to the generated name in its own
rename wave. Re-address it in state (a `moved` block, never a destroy and
recreate), and re-pin its SSH host key in the same change.

## Credentials at the least-shared tier

Generate a new credential at the narrowest tier that needs it — random, and
generate-if-absent. Promote it to a shared secret store only once a second
consumer actually exists. A credential seeded "just in case" is a credential
nobody rotates.

Fetch a credential once per session and reuse the variable. Never write it to a
temporary file or a `.env`; hold it in memory.

## Container placement

System containers by default. Reach for a full container runtime only when the
vendor ships that way and nothing else works, for ephemeral CI runners, or for
development and test. Document the exception at the top of the owning
repository's agent instructions.

High-volume network traffic must never traverse a virtualized container
network.

## macOS: named executables, never a generic interpreter

A launchd job's program is a named, single-purpose executable — never `sh`,
`bash`, `zsh`, `env`, `python` or `node`, and never the `command`/`script`
shorthand that renders `/bin/sh -c`. A process that needs a privacy permission
(screen, microphone, AppleEvents, full disk access, calendar) runs as its own
binary, spawned with responsibility disclaimed so the grant is filed under that
binary. Never request, suggest or accept a privacy grant for a shell, terminal
or temp-path client.

## Diagnosing a fast connection failure

A connection that fails in a couple of milliseconds is not an outage. On some
operating systems, local-network access is gated per-application, so a
non-system binary is refused instantly while a system binary reaches the same
host and port. Check the gate before you blame the network, and never route
around it by disabling a validity or freshness check.
