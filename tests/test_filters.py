from __future__ import annotations

import unittest

from pricemon.config import RuleConfig
from pricemon.filters import category_matches, extract_category, extract_price, matches_filters, matches_rule


class FilterTests(unittest.TestCase):
    def test_extracts_price(self) -> None:
        self.assertEqual(extract_price("[GPU] RTX 5070 - $499.99"), "$499.99")

    def test_extracts_category(self) -> None:
        self.assertEqual(extract_category("[SSD] 2TB NVMe $99"), "ssd")

    def test_category_matches_compound_tags(self) -> None:
        self.assertTrue(category_matches("ssd m.2", ("ssd",)))
        self.assertFalse(category_matches("monitor", ("ssd",)))

    def test_matches_include_exclude_and_category(self) -> None:
        self.assertTrue(
            matches_filters(
                "[GPU] RTX 5070 $499",
                include=("rtx",),
                exclude=("prebuilt",),
                categories=("gpu",),
            )
        )

    def test_matches_rule_with_price_bounds(self) -> None:
        rule = RuleConfig(
            name="gpu",
            categories=("gpu",),
            include_any=("rtx",),
            exclude_any=("prebuilt",),
            max_price=650,
        )

        self.assertTrue(matches_rule("[GPU] RTX 5070 $499", rule))
        self.assertFalse(matches_rule("[GPU] RTX 5070 $799", rule))
        self.assertFalse(
            matches_filters(
                "[GPU] RTX 5070 prebuilt $999",
                include=("rtx",),
                exclude=("prebuilt",),
                categories=("gpu",),
            )
        )