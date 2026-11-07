# Codex Agent Workflow

This is the second rules-related file requested. It covers collaboration and delivery process; `rules.md` covers product engineering constraints.

## Required loop

1. **Inspect:** read the repository, existing instructions, dependency manifests, and current behavior before changing files. Do not assume a blank repository.
2. **Orient:** summarize what exists, identify conflicts with this brief, and state the smallest next step.
3. **Confirm assumptions:** use the defaults in `prd.md` unless a repository fact or genuine blocker requires a choice. Ask one focused question only for a blocking decision; continue independent work while waiting.
4. **Plan one phase:** name its goal, files likely to change, acceptance checks, risks, and estimate. Do not implement all phases in one pass.
5. **Implement narrowly:** complete the current phase, preserve existing conventions, and keep changes reviewable.
6. **Verify:** run the checks relevant to changed behavior. Do not claim a check passed if it did not run. Record commands and outcomes briefly.
7. **Review:** inspect the final diff for accidental files, secret leakage, missed docs/config, and unmet acceptance criteria.
8. **Report:** summarize changes, decisions, verification, limitations, and the exact next phase. Stop at the phase boundary and let the user steer.

## Phase gates

- A phase is complete only when its acceptance criteria in `phases.md` are met or explicitly listed as blocked with evidence.
- Do not build future-phase features opportunistically. A small prerequisite is acceptable only when explained.
- Before adding a new dependency, explain why the standard library/current dependencies are insufficient and choose the smallest suitable option.
- Keep durable decisions in README or an ADR; do not bury them in chat-only context.
- Do not add query routing, semantic cache, feedback learning, multi-tenancy, or distributed infrastructure to the MVP without explicit scope review.

## User interaction

- Make reversible routine implementation choices using the documented defaults.
- Ask before destructive actions, external publication, or changes that could discard user data.
- Show useful progress at phase boundaries; avoid asking the user to decide details that can be benchmarked or documented as defaults.
- If requirements conflict, cite the conflicting files and propose a smallest resolution.

## Definition of done for a phase

- Acceptance criteria are met.
- Relevant checks ran and results are reported.
- Docs/config are updated.
- No known regression or unresolved error is hidden.
- The next phase is named without starting it automatically.
