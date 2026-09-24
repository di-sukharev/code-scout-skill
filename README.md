# Code Scout

Скилл передаёт первичный поиск по коду саб-агенту и экономит контекст основного
агента. Scout находит нужные файлы, связи и тесты. Он возвращает короткую карту
со ссылками на строки кода. Основной агент начинает работу с этой карты.

Scout не меняет код и не запускает проверки. По умолчанию: Codex — Luna,
Claude Code — Sonnet. Модель можно указать в запросе.

Установка — отправьте агенту:

```text
Install this skill globally: https://github.com/di-sukharev/code-scout-skill
```

Запуск:

```text
Use $code-scout to find how authentication works before changing it.
```

[SKILL.md](code-scout/SKILL.md) · [MIT](LICENSE)
