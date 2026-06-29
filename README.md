# pricemon

Fast, lightweight RSS monitor for PC parts deals. It watches public Reddit RSS feeds and sends matching posts to Telegram. No Reddit account or Reddit API credentials are required.

## Status

Scaffold only. Next implementation step is the polling loop, SQLite dedupe, and Telegram delivery.

## Configure

```bash
cp .env.example .env
cp config.example.toml config.toml
```

Set Telegram secrets in `.env`:

```text
TELEGRAM_BOT_TOKEN=123456:abc...
TELEGRAM_CHAT_ID=123456789
```

Edit `config.toml` for feeds and filters.

## Develop

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
python3 -m unittest discover -s tests
python3 -m compileall src tests
```

## Docker

```bash
docker compose up --build
```

## Suggested Agent Skills

No repo skill is needed yet. Add one later only if a repeated procedure emerges, such as deployment operations or source evaluation.