from __future__ import annotations

import feedparser
import httpx

from .models import FeedItem


async def fetch_feed(url: str, *, user_agent: str, timeout: float = 20.0) -> list[FeedItem]:
    headers = {"User-Agent": user_agent}
    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()

    parsed = feedparser.parse(response.content)
    source = parsed.feed.get("title") or url
    items: list[FeedItem] = []
    for entry in parsed.entries:
        item_id = entry.get("id") or entry.get("link")
        title = entry.get("title") or "Untitled"
        link = entry.get("link") or ""
        if not item_id or not link:
            continue
        items.append(
            FeedItem(
                item_id=str(item_id),
                source=str(source),
                title=str(title),
                link=str(link),
                summary=str(entry.get("summary") or ""),
                published_at=str(entry.get("published") or entry.get("updated") or ""),
            )
        )
    return items