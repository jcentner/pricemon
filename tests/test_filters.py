from __future__ import annotations

import unittest

from pricemon.filters import extract_category, extract_price, matches_filters


class FilterTests(unittest.TestCase):
    def test_extracts_price(self) -> None:
        self.assertEqual(extract_price("[GPU] RTX 5070 - $499.99"), "$499.99")

    def test_extracts_category(self) -> None:
        self.assertEqual(extract_category("[SSD] 2TB NVMe $99"), "ssd")

    def test_matches_include_exclude_and_category(self) -> None:
        self.assertTrue(
            matches_filters(
                "[GPU] RTX 5070 $499",
                include=("rtx",),
                exclude=("prebuilt",),
                categories=("gpu",),
            )
        )
        self.assertFalse(
            matches_filters(
                "[GPU] RTX 5070 prebuilt $999",
                include=("rtx",),
                exclude=("prebuilt",),
                categories=("gpu",),
            )
        )