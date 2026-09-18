---
name: code-scout
description: >-
  Save primary-agent context by assigning codebase research to a lower-cost scout.
  Use when the implementation or relevant code connections are unknown.
  Skip when a focused local read or a current report is sufficient.
---

## Dispatch

Use the scout model selected by the user. If the user did not select a model, use these defaults:

- Codex: `gpt-5.6-luna`.
- Claude Code: `sonnet`.

Start one new scout without the parent agent's conversation history.
In Codex, set `fork_turns: "none"`. In Claude Code, start a new `general-purpose` agent.

Pass the absolute repository path, task, research questions, constraints, and known
entry points. Separate known facts from assumptions. Do not tell the scout what
conclusions to reach. Do not research the implementation just to prepare the assignment.
Include the instructions in **Scout research** and **Scout report**.

Reuse reports while they still apply to the task and current code.
If delegation is forbidden or unavailable, explain the limitation and research locally.
Do the same if the selected model is unavailable. Follow the instructions in **Scout research**.
Do not silently use another model.

## Scout research

- Read the applicable repository instructions. Do not edit files or implement changes.
  Do not run tests or builds. Do not use a browser or delegate research to another agent.
- Use `rg`, `rg --files`, and focused reads. Start with known entry points or likely
  paths. Expand the search to answer unresolved questions.
  If the location is unknown, you can use broad searches.
- Select the output format before each tool call. Use paths to find files and matching
  lines to locate logic. Use excerpts with enough context to understand the logic.
  Avoid large outputs that do not help answer the research questions.
  If output is truncated, narrow the query or divide it into smaller queries.
  Do not treat partial output as complete.
- Trace the relevant callers, data flow, contracts, side effects, and tests.
  Explain how they connect. Skip unrelated code paths and exhaustive codebase reviews.
- Separate verified facts, inferences, and unknowns.
  If you do not find an item, state where you searched for it.
- Stop when you have answered the research questions and explained the relevant connections.
  Also stop if further useful research is blocked. Report significant gaps in the evidence.

## Scout report

Return findings directly, without search logs or routine status updates.
Aim for 500 words or fewer. Use more words when essential evidence or connections require them.

1. **Behavior:** answer the questions and explain the relevant flow.
2. **Code and evidence:** support significant findings with symbols and absolute file links
   that include current line numbers. Explain the roles and connections.
   Include exact conditions, signatures, data shapes, or short excerpts when a summary would omit details needed for the next step.
3. **Tests and constraints:** list relevant tests, check commands from configuration,
   and applicable rules or contracts. Distinguish tests you read from checks you ran.
   State what remains unverified.
4. **Open questions:** list significant gaps in the evidence, conflicts, or decisions needed.
   Omit this section if there are none.

Avoid speculative fixes, refactors, and hypothetical edge cases.
State what you do not know. Do not present assumptions as verified facts.

## Use the report

The primary agent makes decisions, implements changes, and validates the result.
Trust verified findings unless evidence contradicts them. Use the report's references
for focused reads needed to resolve specific details or implement and validate safely.
For local searches, follow the search instructions in **Scout research**.
Do not repeat completed research or read the scout's conversation history.

Send remaining research questions to the same scout. Request only additions and corrections.
If retries produce no new evidence, stop retrying. Resolve the unanswered questions locally.
If you need a decision from the user, ask the user. Continue the original task.
