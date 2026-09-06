# pricemon — session bootstrap

RSS deal monitor for PC parts: public Reddit and Slickdeals feeds, named
rules, SQLite dedupe, Telegram delivery. README.md is the authority for
what it does and how it runs; `docs/source-compendium.md` for feed
research; `docs/deployment.md` for the Podman and systemd path.

Where it runs: talos, as the talos-infra stack `stacks/pricemon/` since
2026-09-06 (image built on talos from `~/pricemon`, rules in that stack's
`config.toml`, secrets in sops, state under `/srv/data/pricemon`). The
Podman-on-a-VPS path in `docs/deployment.md` is the generic option, no
longer the live one.

Portfolio pointer: this repo is coordinated from `~/olympus` (its MAP.md
card and BACKLOG carry the cross-repo picture). Routing authority for
who builds and who reviews: olympus ADR-003 as amended by ADR-004. A
session opened here with no kickoff is standalone and must work from
this file plus the README.

Conventions:

- `config.toml`, `.env` and `data/` are local runtime files, never
  committed; `config.example.toml` is the documented example.
- Tests: `pytest` (`pip install -e .[dev]` in a venv). Keep them passing.
- Sources are RSS or Atom only; no scraping of pages without feeds.
- Secrets (the Telegram token and chat id) never appear in logs, docs
  or commits.
- Commit as you go; push only from the integrating session.
