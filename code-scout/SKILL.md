---
name: code-scout
description: >-
  A cheaper sub-agent maps the code a task needs, saving the lead model's context
  and search tokens. Use before broad research in unfamiliar code; skip when a
  focused read or a current report is enough.
---

Use one cheaper sub-agent without chat history. Choose its effort level based on the task.
Give it the repository path, task, questions, and relevant context. Keep the search read-only.

Request a concise report in English, with code references and clearly marked inferences:

- Code map: absolute paths, current line numbers, symbols, and their purpose.
- Connections: relevant callers, data flow, data model, contracts, and project rules.
- Tests and reuse: relevant tests, check commands, and existing code worth reusing.
- Gaps: unanswered questions, missing evidence, and where you looked.

Read the relevant code from the report and continue the original task.
