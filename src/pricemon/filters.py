from __future__ import annotations

import re


PRICE_PATTERN = re.compile(r"\$\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)")
CATEGORY_PATTERN = re.compile(r"^\s*\[([^\]]+)\]")


def extract_price(title: str) -> str | None:
    match = PRICE_PATTERN.search(title)
    if match is None:
        return None
    return "$" + match.group(1).replace(",", "")


def extract_category(title: str) -> str | None:
    match = CATEGORY_PATTERN.search(title)
    if match is None:
        return None
    return match.group(1).strip().lower()


def matches_filters(
    title: str,
    *,
    include: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
    categories: tuple[str, ...] = (),
) -> bool:
    normalized_title = title.lower()
    category = extract_category(title)

    if categories and (category is None or category not in categories):
        return False
    if include and not any(term in normalized_title for term in include):
        return False
    if exclude and any(term in normalized_title for term in exclude):
        return False
    return True