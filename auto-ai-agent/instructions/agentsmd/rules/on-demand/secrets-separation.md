---
name: secrets-separation
description: The secrets method — path grammar, zone mounts, admin mirror, identity classes, grants as data, engines over static, and credential handling. Read before creating, moving, granting, or consuming any credential.
type: LLM Prompt
title: "Secrets separation"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/secrets-separation"
tags:
  - shared-instructions
  - agent-instructions
timestamp: "2026-11-13T20:30:00-05:00"
status: active
consumers:
  - dryvist/nix-ai
  - dryvist/nix-claude-code
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: dryvist/ai-assistant-instructions
    path: "agentsmd/rules/on-demand/secrets-separation.md"
    note: Migrated from the instruction repository.
---

# Secrets separation

This rule is the method. An estate's services, identities and grants are private data in its private documentation.

## One path grammar

Every static secret sits at one of these shapes, and nowhere else:

```text
<zone>/<service>/<instance>/<access>          access = ro | rw | self
admin/<zone>/<service>/<instance>/<scope>     scope  = admin | management | owner | root
config/<service>/<instance>                   non-secret settings
```

- **`ro`** reads the service. **`rw`** changes its data. **`self`** holds what
  only the service itself reads, such as its own database password.
- **One leaf, one access level.** A read key and a write key never share a
  leaf, so a grant on a leaf is a grant of exactly one capability.
- **`<instance>`** names the deployment, so two instances never share a credential.

## Zones: the boundary is the mount

A path prefix gives no policy boundary; a mount does. Each zone is its own mount, chosen by how far a leak reaches:

| Zone | Holds |
| --- | --- |
| `int` | services reachable only inside the network |
| `ext-ai` | usage keys for external model providers |
| `ext-saas` | keys for other internet-reachable vendors |
| `ext-critical` | internet-reachable and destructive: DNS, cloud accounts, backup accounts, signing |
| `admin` | a mirror of the zones for anything that can mint, delete or re-permission |
| `config` | non-secret topology and settings |
| `state` | lease and lock objects |

An operator may declare further zones in the estate's arrangement document.

**Placement test.** Ask in order, and stop at the first yes:

1. Can it mint, delete, or change the permissions of other credentials or
   users? It goes under `admin/<zone>/...`.
2. Is the service reachable from the public internet? It goes in the `ext-`
   zone that matches its kind; destructive reach means `ext-critical`.
3. Otherwise it goes in `int`.

Unsure which zone? Ask. Do not guess.

## Identity classes and grants

Every identity belongs to one class. The class alone sets token lifetime,
login shape, permitted source network and whether a human gate applies.

| Class | Is |
| --- | --- |
| everyday | an interactive agent or tool session doing routine work |
| service | a workload reading what it runs on |
| sandbox | a harness whose prompt, tools or output path the operator does not fully control |
| automation | the dedicated unattended identity that converges infrastructure |
| sudo | a short-lived, narrowly scoped elevation the operator approves at each opening |
| restricted | an identity that reaches an operator-declared zone, human-gated per session |
| operator session | the human-gated full-access session described below |

A **grant** is one line: identity, zone, service, instance, access. A segment
may be `+` to mean every value of that one segment.

- **No wildcard across zones.** Only the operator session reads more than one
  zone by wildcard.
- **Everyday, service and sandbox identities are denied every `admin` path**
  and every operator-declared zone.
- **A sandbox identity gets exact leaves**: the paths it consumes, never a
  subtree and never a list capability over its neighbours.
- **One reader, one credential.** Two consumers never share a login.

## The arrangement is data

The secrets engine role names no service, identity or grant. One private, version-controlled **arrangement document** lists zones, services,
identities and grants; the role renders every mount, identity and policy from it, and a public schema validates it.

To change who can read what, change that document. Never hand-write a policy.

## The operator session

One identity has full access: a session opened by the operator with a
hardware-key touch or a single-sign-on approval. It ends after 12 hours. It can
read and write every mount and engine. It cannot create a token that outlives
the session, change its own unlock factor, or disable audit.

Reads within an identity's grants are pre-authorized; anything else waits for this session. Never propose a locally stored key, a pasted token, or a switch of
identity to get past a refusal: name the gate that is missing.

## Engines before static secrets

- **Prefer a secrets engine wherever one exists.** Short-lived minted credentials remove the rotation problem.
- An engine keeps its own mount. Its management credential lives in the
  engine's own configuration, not in a key-value leaf.
- If the engine for a resource is not configured, that need is blocked. It is
  not a licence to store a static copy.
- **Migrating a secret is not done when it is copied.** It is done when a live
  consumer is proven against the new path and the original is deleted.

## Secret zero

**The run wrapper supplies secret zero and nothing else.** Whatever bootstraps
a process gives it exactly two things: the address of the central store, and
the login pair of the identity it runs as. Every other value resolves from the
central store at run time. A second value in the wrapper is a second store, and
it drifts.

Privileged unattended convergence runs as the **automation identity**, distinct from the interactive human account, which stays interactively gated
and never carries a standing password-less grant.

A hosted cloud thread has forge write through the hosting provider's app only
and no secret-store access (`claude-projects.md`).

## Object storage: one bucket per workload, two keys per bucket

- **Every large or distinct data store gets its own bucket**, never a shared key prefix. Backups never share with anything.
- **Exactly two scoped keys per bucket**, named after it: a read-only key and a
  read-write key. Consumers take the narrowest one that works.
- Account-wide admin keys are break-glass only. Never used by a service, never
  stored where a service can read them.

## Forge credentials: minted per call, never ambient

A code-hosting CLI is **not** authenticated on any agent harness, by design. **A probe that finds no session is the expected state**, never a reason to stop.

- **Mint at call time, in the shell that uses it.** Never mint at
  environment-load time: a direnv-style loader caches its dump to disk, which
  persists the credential.
- **Take the narrowest scope.** Read for anything that only reads; a
  repo-scoped write credential only to write.
- **Interactive wrappers are shell functions or aliases** and do not exist in an agent shell. Use the underlying command the operator's local notes name.
- **Tag the mint with an identity that names the agent**, so leases and audit
  entries distinguish one harness and one session from another.
- **A minted installation credential has no user identity.** A call that asks
  "who am I" is refused; use resource-scoped calls instead.

Helper names, variables and endpoints live in the operator's local files, never in a committed artifact.

## Handling a credential

- **Never print a value.** Capture it into a variable and use the variable. No
  echo, no verbose HTTP client, no dump of the environment.
- **Never put a credential in a command's arguments**, a file, or a brief sent
  to another agent. Pass it in memory or through a file descriptor.
- **Record the accessor at mint time** and hold it in memory with the token.
- **Revoke in an EXIT trap in the same shell**, set before the token is used,
  so every exit path revokes it. Expiry is not revocation.
- **Never leave a minted token alive after its shell exits.**
- **Never hand-type a credential into a shared store.** Generate it at the
  source, idempotently, at the least-shared place it is first used.

## Access: certificate first, break-glass never casually

Try the rungs in order and never invert them:

1. **The certificate authority.** Sign an ephemeral keypair, use it, discard it.
2. **A legacy shared key**, only while its retirement is unfinished.
3. **Break-glass admin credential**: only after 1 and 2 were tried and failed. Say so in the write-up.

**An SSH certificate principal is not the login user.** Test as the configured login user before concluding the authority is missing.

**Never weaken host verification**: no disabling strict checking, no accept-on-first-use, no discarding known-hosts. Remove the one stale entry,
re-verify that host, and record why.

## The failure signature to expect

- An HTTP 429 from a secret-store standby node means the standby is healthy.
- A helper that exits successfully having exported nothing is the bug. A credential helper fails loudly.
- If a tool cannot authenticate, the fix is the credential path. Never a local
  copy, and never a credential pasted into a file.
- **A source-address or network-class refusal is not a broken credential.**
  Check which network class the caller is on before rotating or recreating
  anything.
- An empty list from a read identity is a permission result, not evidence that
  nothing is there.
