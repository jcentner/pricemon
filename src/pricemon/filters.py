from __future__ import annotations

import re

from .config import RuleConfig


PRICE_PATTERN = re.compile(r"\$\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)")
CATEGORY_PATTERN = re.compile(r"^\s*\[([^\]]+)\]")


def extract_price(title: str) -> str | None:
    match = PRICE_PATTERN.search(title)
    if match is None:
        return None
    return "$" + match.group(1).replace(",", "")


def extract_price_value(title: str) -> float | None:
    price = extract_price(title)
    if price is None:
        return None
    return float(price.removeprefix("$"))


def extract_category(title: str) -> str | None:
    match = CATEGORY_PATTERN.search(title)
    if match is None:
        return None
    return match.group(1).strip().lower()


def category_matches(category: str | None, expected: tuple[str, ...]) -> bool:
    if not expected:
        return True
    if category is None:
        return False
    category_terms = set(re.split(r"[^a-z0-9]+", category))
    return any(item == category or item in category_terms for item in expected)


def matches_filters(
    title: str,
    *,
    include: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
    categories: tuple[str, ...] = (),
) -> bool:
    normalized_title = title.lower()
    category = extract_category(title)

    if not category_matches(category, categories):
        return False
    if include and not any(term in normalized_title for term in include):
        return False
    if exclude and any(term in normalized_title for term in exclude):
        return False
    return True


def matches_rule(title: str, rule: RuleConfig) -> bool:
    normalized_title = title.lower()
    category = extract_category(title)
    price = extract_price_value(title)

    if not category_matches(category, rule.categories):
        return False
    if rule.exclude_any and any(term in normalized_title for term in rule.exclude_any):
        return False
    if rule.include_all and not all(term in normalized_title for term in rule.include_all):
        return False
    if rule.include_any and not any(term in normalized_title for term in rule.include_any):
        return False
    if rule.min_price is not None and (price is None or price < rule.min_price):
        return False
    if rule.max_price is not None and (price is None or price > rule.max_price):
        return False
    return True