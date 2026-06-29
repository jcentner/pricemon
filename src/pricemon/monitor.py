from __future__ import annotations

import asyncio
from dataclasses import dataclass

from .config import RuleConfig, Settings, SourceConfig
from .filters import matches_rule
from .models import FeedItem, MatchedItem
from .rss import fetch_feed
from .storage import SeenStore
from .telegram import render_message, send_message


@dataclass(frozen=True, slots=True)
class RunResult:
    fetched: int = 0
    marked_seen: int = 0
    matched: int = 0
    sent: int = 0


async def run_once(settings: Settings, *, dry_run: bool = False) -> RunResult:
    store = SeenStore(settings.database_path)
    if not dry_run:
        store.init()

    items = await _fetch_all(settings)
    fetched = len(items)

    if dry_run:
        matches = _match_items(items, settings.rules)
        for match in matches:
            print(render_message(match))
            print()
        return RunResult(fetched=fetched, matched=len(matches))

    if settings.first_run_mark_seen and not store.is_initialized():
        store.mark_many_seen(items)
        store.set_initialized()
        return RunResult(fetched=fetched, marked_seen=fetched)

    sent = 0
    matched = 0
    for item in reversed(items):
        if store.is_seen(item.item_id):
            continue
        match = _match_item(item, settings.rules)
        if match is None:
            store.mark_seen(item)
            continue
        matched += 1
        await send_message(
            bot_token=settings.telegram_bot_token,
            chat_id=settings.telegram_chat_id,
            text=render_message(match),
            disable_web_page_preview=settings.disable_web_page_preview,
        )
        store.mark_seen(item, rule_name=match.rule_name, delivered=True)
        sent += 1
    store.set_initialized()
    return RunResult(fetched=fetched, matched=matched, sent=sent)


async def run_forever(settings: Settings) -> None:
    while True:
        try:
            result = await run_once(settings)
            print(_format_result(result))
        except Exception as exc:
            print(f"poll failed: {exc}")
        await asyncio.sleep(settings.poll_interval_seconds)


def validate_delivery_settings(settings: Settings) -> None:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
    if not settings.telegram_chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID is required")


def _format_result(result: RunResult) -> str:
    return (
        f"fetched={result.fetched} "
        f"marked_seen={result.marked_seen} "
        f"matched={result.matched} "
        f"sent={result.sent}"
    )


async def _fetch_all(settings: Settings) -> list[FeedItem]:
    items: list[FeedItem] = []
    for source in settings.sources:
        try:
            items.extend(await _fetch_source(source, settings))
        except Exception as exc:
            print(f"fetch failed for {source.name}: {exc}")
    return items


async def _fetch_source(source: SourceConfig, settings: Settings) -> list[FeedItem]:
    return await fetch_feed(source.name, source.url, user_agent=settings.user_agent)


def _match_items(items: list[FeedItem], rules: tuple[RuleConfig, ...]) -> list[MatchedItem]:
    matches: list[MatchedItem] = []
    for item in items:
        match = _match_item(item, rules)
        if match is not None:
            matches.append(match)
    return matches


def _match_item(item: FeedItem, rules: tuple[RuleConfig, ...]) -> MatchedItem | None:
    for rule in rules:
        if rule.sources and item.source_name not in rule.sources:
            continue
        if matches_rule(item.title, rule):
            return MatchedItem(item=item, rule_name=rule.name)
    return None