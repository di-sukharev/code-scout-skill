# Code Scout

Скилл передаёт первичный поиск по коду саб-агенту и экономит контекст основного
агента. Scout находит нужные файлы, связи и тесты. Он возвращает короткую карту
со ссылками на строки кода. Основной агент начинает работу с этой карты.

Scout не меняет код и не запускает проверки. По умолчанию: Codex — Luna,
Claude Code — Sonnet, effort `medium`. Модель и effort можно указать в запросе.
Scout пишет отчёт на английском: так отчёт занимает меньше токенов.

Установка — отправьте агенту:

```text
Install this skill and its Claude agent globally: https://github.com/di-sukharev/code-scout-skill
```

Или скопируйте папку `code-scout` в `~/.codex/skills/` либо `~/.claude/skills/`.
Для Claude Code скопируйте ещё `claude-agents/effort-medium.md` в `~/.claude/agents/`
и перезапустите Claude Code. Без этого агента scout наследует effort сессии и стоит дороже.

Запуск:

```text
Use $code-scout to find how authentication works before changing it.
```

[SKILL.md](code-scout/SKILL.md) · [MIT](LICENSE)
