from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_CONFIG_PATH = Path("config.toml")
DEFAULT_DATABASE_PATH = Path("data/pricemon.db")
DEFAULT_USER_AGENT = "pricemon/0.1 (+https://github.com/your-user/pricemon)"


@dataclass(frozen=True, slots=True)
class SourceConfig:
    name: str
    url: str
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Settings:
    telegram_bot_token: str
    telegram_chat_id: str
    poll_interval_seconds: int
    database_path: Path
    user_agent: str
    sources: tuple[SourceConfig, ...]


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

    return Settings(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
        poll_interval_seconds=int(data.get("poll_interval_seconds", 45)),
        database_path=Path(os.getenv("PRICEMON_DB") or data.get("database_path", DEFAULT_DATABASE_PATH)),
        user_agent=str(data.get("user_agent", DEFAULT_USER_AGENT)).strip(),
        sources=sources,
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
        name = str(raw_source.get("name", "")).strip()
        url = str(raw_source.get("url", "")).strip()
        if not name or not url:
            raise ValueError("each source needs name and url")
        sources.append(
            SourceConfig(
                name=name,
                url=url,
                include=_as_tuple(raw_source.get("include", [])),
                exclude=_as_tuple(raw_source.get("exclude", [])),
                categories=_as_tuple(raw_source.get("categories", [])),
            )
        )
    return sources


def _as_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError("filter values must be lists")
    return tuple(str(item).strip().lower() for item in value if str(item).strip())