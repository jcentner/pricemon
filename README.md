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
TELEGRAM_BOT_TOKEN=<bot-token>
TELEGRAM_CHAT_ID=<chat-id>
```

Edit `config.toml` for feeds and rules.

See [docs/source-compendium.md](docs/source-compendium.md) for researched source options and observed title formats.

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
- `categories`: title tags like `[GPU]`, `[SSD]`, `[Monitor]`. A list applies
  to every source; a table such as `{ buildapcsales = ["gpu"] }` applies
  only to the named sources. Unlisted sources have no category requirement.
- `include_all`: every term must appear in the title.
- `include_any`: at least one term must appear in the title.
- `exclude_any`: if any term appears, skip the item.
- `exclude_patterns`: a list of case-insensitive
  [Python regular expressions](https://docs.python.org/3/library/re.html);
  if any pattern matches anywhere in the title, skip the item. Use TOML
  literal strings (single quotes) to preserve backslashes, for example
  `exclude_patterns = ['\b\d{3}\s?Hz\b', '\b\d{3,5}HX\b']`.
  Invalid regexes fail config loading with the rule name. Patterns retain
  their original case and whitespace; `exclude_any` remains plain substring matching.
- `min_price` / `max_price`: best-effort price bounds parsed from the title.

Filtering order: source, seen-item check, category, excludes, include-all, include-any, price. The first matching rule wins, so put focused rules before broad catch-all rules.

`config.example.toml` contains exactly two focused watches: Intel Arc B50/B60
(including Pro and dual-GPU cards) and desktop RTX 5070 Ti. Both require
`[GPU]` on buildapcsales and accept untagged Slickdeals search results, with
no price bounds and no restriction on store pickup. Arc includes require
`arc` plus `b50` or `b60`; a regex rejects titles lacking standalone Arc and
B50/B60 tokens. RTX accepts `5070 ti` and `5070ti`, including `RTX` followed
by a trademark symbol, but rejects embedded model tokens and non-Ti cards.

The example regexes reject laptop words, 14-18-inch screen sizes (straight
or curly quotes, or `inch`), OLED, three-digit refresh rates, and numeric
H/HX mobile CPU models. Since a GPU model is also required, these clues
identify untagged laptop titles without requiring a literal `laptop` tag.
System RAM, SSD and CPU terms also reject prebuilts; plain `desktop` and
`workstation` are not excluded because they can describe standalone cards.
These are title heuristics, not a guarantee of stock, current price or
complete retailer coverage. Search feeds can include older deals.

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

## Deployment

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