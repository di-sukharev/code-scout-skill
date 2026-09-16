---
name: code-scout
description: >-
  Delegate initial codebase research to a fresh subagent and receive a concise
  report on the current implementation, relevant dependencies, and tests.
  Use when a task needs repository discovery and the relevant code is not yet known.
  Skip when a focused local read or an existing report is sufficient.
---

## Purpose

Let a cheaper scout do the initial searching and reading so the primary agent
can reason from a compact report. The primary agent owns decisions,
implementation, and validation.

## Dispatch

Use the user's chosen model. Defaults: `gpt-5.6-luna` in Codex, `sonnet` in Claude Code.
Start one fresh scout with that model and no parent history
(Codex: `fork_turns: "none"`; Claude Code: a new `general-purpose` agent).
Do not research the implementation
before delegating. Pass the absolute repository path, the user's task, concrete
research questions, relevant constraints, and any already-known entry points.
Distinguish known facts from hypotheses; do not prescribe the answer.

Give the scout the research and report instructions below in its brief.
If delegation is forbidden or unavailable, or the selected model is unavailable,
report that briefly and do focused local research; do not silently substitute models.
Reuse an existing report while its scope and relevant code remain current.

## Scout research

- Stay read-only. Do not edit files, implement fixes, run tests or builds, open
  a browser, or delegate. Read applicable repository instructions.
- Use `rg`, `rg --files`, and focused reads to locate the current implementation.
  Follow relevant callers, data flow, contracts, and tests far enough to answer
  the research questions. Avoid unrelated code and exhaustive repository surveys.
- Explain what the code does today and which parts are connected. Identify
  relevant test cases and available check commands from project configuration;
  distinguish tests you read from checks actually run.
- Separate verified facts, inferences, and unknowns. If something is not found,
  state where you looked; do not claim repository-wide absence from a narrow search.
- Stop when the questions are answered or a concrete gap blocks further progress.
  Return findings directly, without a search transcript or routine status updates.

## Scout report

Use concise Markdown, normally within 500 words; expand only for essential evidence:

1. **Current behavior:** answer the research questions and summarize the relevant flow.
2. **Code map:** key files and symbols, with absolute file links and current line
   numbers; explain each one's role and relevant connections.
3. **Tests and constraints:** closest tests, available check commands, and repository
   rules or contracts that affect this task. State what was not verified.
4. **Open questions:** material gaps, conflicting evidence, or decisions the primary
   agent must make. Omit this section if there are none.

Include only evidence useful for the task. Do not propose speculative fixes,
refactors, or hypothetical edge cases. A partial report with clear gaps is better
than invented certainty.

## Use the report

Reason from the report without repeating broad discovery or checking every citation
as a ritual. Read the specific code needed to make a decision, edit safely, or
resolve a questionable claim. Refresh affected findings if the relevant code changed.
Do not read the scout's history.

If a material question remains, send the same scout a focused follow-up. Stop
retries that bring no new evidence; resolve the remaining gap locally or ask the
user when it requires their decision. Continue the original task from the findings.
