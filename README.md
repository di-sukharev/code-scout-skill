# Code Scout

Саб-агент делает первичный поиск по репозиторию и приносит основному агенту короткий
отчёт: как работает текущая реализация, где находится нужный код, с чем он связан,
какие есть тесты и что осталось неизвестным. Основной агент принимает решения
и выполняет задачу, не повторяя весь поиск.

Один свежий скаут без истории разговора. По умолчанию: Codex — `gpt-5.6-luna`,
Claude Code — `sonnet`.
Другую модель можно указать в запросе. Скаут только читает код; файлы не меняет,
тесты и сборку не запускает. Если нужный код уже известен или отчёт ещё актуален,
повторное исследование не требуется.

Отчёт — обычный Markdown, обычно до 500 слов, со ссылками на файлы и строки.
Факты отделены от предположений и пробелов. Основной агент читает конкретные
участки по мере необходимости; существенные пробелы уточняет у того же скаута.

## Установка

Отправьте агенту:

```text
Install the code-scout skill globally from
https://github.com/di-sukharev/code-scout-skill/tree/master/skills/code-scout
```

Или скопируйте `skills/code-scout` в `~/.codex/skills/` либо `~/.claude/skills/`.
Нужны саб-агенты с доступом к выбранной модели.

## Использование

```text
Use $code-scout to find how authentication and session expiry work in this repo
before implementing refresh-token support.
```

Для автоматического применения можно добавить в проектный `AGENTS.md`:

```md
- Use $code-scout for initial repository research when the relevant implementation
  is not yet known. Reuse current findings instead of repeating broad searches.
```

[Полный протокол](skills/code-scout/SKILL.md). [MIT](LICENSE).
