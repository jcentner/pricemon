from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FeedItem:
    item_id: str
    source: str
    source_name: str
    title: str
    link: str
    summary: str = ""
    published_at: str = ""


@dataclass(frozen=True, slots=True)
class MatchedItem:
    item: FeedItem
    rule_name: str