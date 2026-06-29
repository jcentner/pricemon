from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FeedItem:
    item_id: str
    source: str
    title: str
    link: str
    summary: str = ""
    published_at: str = ""