# pricemon

Fast, lightweight RSS monitor for PC parts deals. It watches public Reddit RSS feeds and sends matching posts to Telegram. No Reddit account or Reddit API credentials are required.

## Features

- Public RSS feeds only; no Reddit account required.
- Named hardware rules with category, keyword, and price filters.
- SQLite dedupe with first-run mark-seen behavior.
- Telegram `sendMessage` delivery.
- `--once`, `--dry-run`, and `--send-test` modes.

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

Edit `config.toml` for feeds and rules.

Example rule:

```toml
[[rules]]
name = "gpu-upgrade"
sources = ["buildapcsales"]
categories = ["gpu"]
include_any = ["rtx 5070", "rtx 5080", "radeon"]
exclude_any = ["prebuilt", "laptop", "refurbished"]
max_price = 650
```

Rule fields:

- `sources`: source names from `[[sources]]`; empty means any source.
- `categories`: title tags like `[GPU]`, `[SSD]`, `[Monitor]`.
- `include_all`: every term must appear in the title.
- `include_any`: at least one term must appear in the title.
- `exclude_any`: if any term appears, skip the item.
- `min_price` / `max_price`: best-effort price bounds parsed from the title.

Filtering order: source, seen-item check, category, excludes, include-all, include-any, price. The first matching rule wins, so put focused rules before broad catch-all rules.

## Run

```bash
python3 -m pricemon --dry-run
python3 -m pricemon --send-test
python3 -m pricemon --once
python3 -m pricemon
```

`--dry-run` prints current matches without sending Telegram messages or writing SQLite state.

## Develop

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
python3 -m unittest discover -s tests
python3 -m compileall src tests
```

## Podman

Containers are optional; the plain Python commands above are enough for local use. For a VPS, Podman gives a simple always-on deployment path. See [docs/deployment.md](docs/deployment.md) for the systemd service runbook.

```bash
podman build -t pricemon:latest .
podman run --rm \
	--env-file .env \
	-v "$PWD/config.toml:/app/config.toml:ro" \
	-v "$PWD/data:/app/data" \
	localhost/pricemon:latest pricemon --dry-run
```

For 24/7 use, run the same image from a user-level `systemd` service with `Restart=always`.

## Suggested Agent Skills

No repo skill is needed yet. Add one later only if a repeated procedure emerges, such as deployment operations or source evaluation.