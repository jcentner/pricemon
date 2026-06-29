from __future__ import annotations

import html

import httpx

from .filters import extract_category, extract_price
from .models import MatchedItem


def render_message(match: MatchedItem) -> str:
    item = match.item
    title = html.escape(item.title)
    category = extract_category(item.title)
    price = extract_price(item.title)

    lines = [f"<b>{title}</b>"]
    details = [item.source_name]
    details.append(f"rule: {match.rule_name}")
    if category:
        details.append(category.upper())
    if price:
        details.append(price)
    if details:
        lines.append(" | ".join(details))
    lines.append(html.escape(item.link))
    return "\n".join(lines)


async def send_message(
    *,
    bot_token: str,
    chat_id: str,
    text: str,
    disable_web_page_preview: bool = False,
) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": disable_web_page_preview,
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()