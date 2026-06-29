# GitHub Copilot Instructions

This repo is a lightweight RSS-to-Telegram monitor for PC parts deals.

## Project Shape

- Python package code lives in `src/pricemon/`.
- Tests live in `tests/` and should use stdlib `unittest` unless a dependency is already justified.
- Runtime config comes from `.env` for secrets and `config.toml` for non-secret feed/filter settings.
- Do not require Reddit credentials. This project monitors public RSS feeds.

## Development

- Keep dependencies minimal. Prefer stdlib where it stays readable.
- Do not commit Telegram bot tokens, chat IDs, or local SQLite data.
- Validate with `python3 -m unittest discover -s tests` and `python3 -m compileall src tests`.
- Keep user-facing notification text compact and Telegram-safe.

## Scope

- Build for a single self-hosted user first.
- Avoid multi-user bot commands, web dashboards, or browser automation until requested.