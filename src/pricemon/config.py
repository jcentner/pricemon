from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_CONFIG_PATH = Path("config.toml")
DEFAULT_DATABASE_PATH = Path("data/pricemon.db")
DEFAULT_USER_AGENT = "pricemon/0.1 (+https://github.com/jcentner/pricemon)"


@dataclass(frozen=True, slots=True)
class SourceConfig:
    name: str
    url: str


@dataclass(frozen=True, slots=True)
class RuleConfig:
    name: str
    sources: tuple[str, ...] = ()
    include_any: tuple[str, ...] = ()
    include_all: tuple[str, ...] = ()
    exclude_any: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    min_price: float | None = None
    max_price: float | None = None


@dataclass(frozen=True, slots=True)
class Settings:
    telegram_bot_token: str
    telegram_chat_id: str
    poll_interval_seconds: int
    first_run_mark_seen: bool
    disable_web_page_preview: bool
    database_path: Path
    user_agent: str
    sources: tuple[SourceConfig, ...]
    rules: tuple[RuleConfig, ...]


def load_settings(config_path: str | Path | None = None) -> Settings:
    load_dotenv()

    selected_config = Path(
        config_path or os.getenv("PRICEMON_CONFIG") or DEFAULT_CONFIG_PATH
    )
    data = _load_toml(selected_config)

    sources = tuple(_load_sources(data.get("sources", [])))
    if not sources:
        sources = (
            SourceConfig(
                name="buildapcsales",
                url="https://www.reddit.com/r/buildapcsales/new/.rss",
            ),
        )
    rules = tuple(_load_rules(data.get("rules", [])))
    if not rules:
        rules = (
            RuleConfig(
                name="all-deals",
                sources=tuple(source.name for source in sources),
                exclude_any=("expired", "sold out"),
            ),
        )

    return Settings(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
        poll_interval_seconds=int(data.get("poll_interval_seconds", 60)),
        first_run_mark_seen=_as_bool(data.get("first_run_mark_seen", True)),
        disable_web_page_preview=_as_bool(data.get("disable_web_page_preview", False)),
        database_path=Path(os.getenv("PRICEMON_DB") or data.get("database_path", DEFAULT_DATABASE_PATH)),
        user_agent=str(data.get("user_agent", DEFAULT_USER_AGENT)).strip(),
        sources=sources,
        rules=rules,
    )


def _load_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("rb") as config_file:
        return tomllib.load(config_file)


def _load_sources(raw_sources: object) -> list[SourceConfig]:
    if not isinstance(raw_sources, list):
        raise ValueError("sources must be a list")

    sources: list[SourceConfig] = []
    for raw_source in raw_sources:
        if not isinstance(raw_source, dict):
            raise ValueError("each source must be a table")
        name = str(raw_source.get("name", "")).strip().lower()
        url = str(raw_source.get("url", "")).strip()
        if not name or not url:
            raise ValueError("each source needs name and url")
        sources.append(
            SourceConfig(
                name=name,
                url=url,
            )
        )
    return sources


def _load_rules(raw_rules: object) -> list[RuleConfig]:
    if not isinstance(raw_rules, list):
        raise ValueError("rules must be a list")

    rules: list[RuleConfig] = []
    for raw_rule in raw_rules:
        if not isinstance(raw_rule, dict):
            raise ValueError("each rule must be a table")
        name = str(raw_rule.get("name", "")).strip()
        if not name:
            raise ValueError("each rule needs a name")
        rules.append(
            RuleConfig(
                name=name,
                sources=_as_tuple(raw_rule.get("sources", [])),
                include_any=_as_tuple(raw_rule.get("include_any", [])),
                include_all=_as_tuple(raw_rule.get("include_all", [])),
                exclude_any=_as_tuple(raw_rule.get("exclude_any", [])),
                categories=_as_tuple(raw_rule.get("categories", [])),
                min_price=_as_optional_float(raw_rule.get("min_price")),
                max_price=_as_optional_float(raw_rule.get("max_price")),
            )
        )
    return rules


def _as_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError("filter values must be lists")
    return tuple(str(item).strip().lower() for item in value if str(item).strip())


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _as_optional_float(value: object) -> float | None:
    if value is None:
        return None
    return float(value)