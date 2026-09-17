---
name: code-scout
description: >-
  Save primary-agent context by delegating codebase discovery to a cheaper scout.
  Use when the implementation or relevant connections are unknown.
  Skip when a focused local read or current report suffices.
---

## Dispatch

Use the user's chosen scout model. Defaults: `gpt-5.6-luna` in Codex, `sonnet` in Claude Code.
Start one fresh scout without parent history
(Codex: `fork_turns: "none"`; Claude Code: a new `general-purpose` agent).

Pass the absolute repository path, task, research questions, constraints, and known
entry points. Separate facts from hypotheses; do not prescribe findings or research
the implementation just to prepare the brief. Include the research and report
instructions below.

Reuse reports while their scope and code remain current. If delegation is forbidden
or unavailable, or the selected model is unavailable, say so and research locally
with the same discipline; do not silently substitute models.

## Scout research

- Read applicable repository instructions. Stay read-only: no edits, implementation,
  tests/builds, browser, or further delegation.
- Use `rg`, `rg --files`, and focused reads. Start with known entry points or likely
  paths; widen to resolve gaps. Broad searches are appropriate when location is unknown.
- Choose output before calling tools: paths to find files, matching lines to locate
  logic, excerpts with enough context to understand it. Avoid content dumps.
  If truncated, narrow or partition the query; do not treat partial output as complete.
- Trace task-relevant callers, data flow, contracts, side effects, and tests to explain
  how the pieces connect. Skip unrelated branches and exhaustive surveys.
- Separate verified facts, inferences, and unknowns. Scope negative findings to
  where you searched.
- Stop when the research questions are answered and relevant connections explained,
  or further useful research is blocked. Report material gaps.

## Scout report

Return findings directly, without search logs or routine status updates.
Aim for 500 words or fewer; expand for essential evidence or connections.

1. **Behavior:** answer the questions and explain the relevant flow.
2. **Code and evidence:** tie material findings to symbols and absolute file links
   with current line numbers. Explain roles and connections; include exact conditions,
   signatures, data shapes, or short excerpts where paraphrasing would lose details
   needed next.
3. **Tests and constraints:** relevant tests, check commands from configuration,
   and applicable rules or contracts. Distinguish tests read from checks run;
   state what remains unverified.
4. **Open questions:** material gaps, conflicts, or decisions; omit if empty.

Avoid speculative fixes, refactors, and hypothetical edge cases.
Report gaps rather than invent certainty.

## Use the report

The primary agent owns decisions, implementation, and validation. Trust verified
findings unless evidence contradicts them. Use the supplied references for focused
reads needed to resolve a specific detail or implement and validate safely.
Apply the same search discipline locally; do not repeat discovery or read scout history.

Send remaining discovery questions to the same scout, requesting only additions
and corrections. Stop retries that yield no new evidence; resolve gaps locally
or ask the user when their decision is needed. Continue the original task.
