from __future__ import annotations

import unittest
from pathlib import Path

from pricemon.config import RuleConfig, load_settings
from pricemon.models import FeedItem
from pricemon.monitor import _match_item


# Public Slickdeals RSS titles observed 2026-09-06.
LIVE_ARC_TITLES = (
    "Intel Arc Pro B50 16GB GDDR6 PCIE 5.0 x8 AI SFF Graphics Card (70w) $349.99",
    "Intel Arc Pro B50 128Bit 16GB GDDR6 PCIe 5.0 x8 Workstation SFF Graphics Card @ $330 + F/S",
    "ASRock Intel Arc Pro B60 Creator Single-Fan AI & Workstation Graphics Card; 24GB GDDR6 Memory; PCIe 5.0 x8 Interface; 20 Ray $649.99",
    "Sparkle Intel Arc Pro ARC B60 PRO SBP60W-24G 24GB $799.99",
)
LIVE_RTX_TITLES = (
    "PNY NVIDIA GeForce RTX\u2122 5070 Ti OC Triple Fan, Graphics Card (16GB GDDR7 $890.99",
    "GIGABYTE Gaming GeForce RTX 5070 Ti 16GB GDDR7 PCI Express 5.0 ATX Graphics Card $909.99",
)
LIVE_REJECTED_TITLES = (
    'Lenovo Legion Pro 5i Gen 10 (Cert. Refurb): 16" QHD+ 165Hz OLED, Intel Ultra 9 275HX, RTX 5070 Ti, 32GB DDR5, 1TB SSD $1908.63',
    'Acer Nitro 16S: 16" QHD+ 180Hz IPS, Ryzen AI 7 350, RTX 5070 TI, 16GB DDR5, 512GB SSD $1499.99',
    "Cert. Refurb: MSI AEGIS Z2: R7 8700F, RTX 5070 Ti, 32GB DDR5, 2TB SSD $1999.99",
    "Skytech King 95 Gaming Desktop: R7 9850X3D, RTX 5070 Ti, 32GB DDR5, 2TB SSD, 850W $2349.99",
    "Certified Refurb: Acer Nitro 60 PC: Ryzen 9 7900, RTX 5070 Ti, 32GB RAM, 2TB SSD $1860 + Free S&H",
    "Seasonic Focus GX 750W ATX 3.1 Fully Modular 80 Plus Gold Power Supply (White) $89.99 + Free Shipping",
    "YMMV - Home Depot has Schlage B60 series Deadbolt clearance $19.53 or lower",
    "Arylic Amplifiers - 5th anniversary sale 20% off B50 $111.20, H50 $319.20",
)


class GpuRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = load_settings(Path(__file__).resolve().parents[1] / "config.example.toml")

    def match(self, title: str, source: str = "slickdeals-5070-ti") -> str | None:
        item = FeedItem(item_id="1", source="feed", source_name=source, title=title, link="https://example.com/1")
        matched = _match_item(item, self.settings.rules)
        return matched.rule_name if matched else None

    def test_example_has_exactly_two_unbounded_focused_rules(self) -> None:
        self.assertEqual([rule.name for rule in self.settings.rules], ["arc-b50-b60", "rtx-5070-ti"])
        for rule in self.settings.rules:
            self.assertIsNone(rule.min_price)
            self.assertIsNone(rule.max_price)
            self.assertEqual(rule.categories, {"buildapcsales": ("gpu",)})

    def test_live_card_titles(self) -> None:
        for title in LIVE_ARC_TITLES:
            with self.subTest(title=title):
                self.assertEqual(self.match(title, "slickdeals-arc-b50"), "arc-b50-b60")
                self.assertEqual(self.match(title, "slickdeals-arc-b60"), "arc-b50-b60")
        for title in LIVE_RTX_TITLES:
            with self.subTest(title=title):
                self.assertEqual(self.match(title), "rtx-5070-ti")

    def test_live_noise_rejected(self) -> None:
        for title in LIVE_REJECTED_TITLES:
            for source in self.settings.sources:
                with self.subTest(title=title, source=source.name):
                    self.assertIsNone(self.match(title, source.name))

    def test_arc_variants_and_token_boundaries(self) -> None:
        for model in ("Arc B50", "ARC B60", "Arc Pro B50", "Arc Pro B60", "Arc Pro B60 Dual 48GB"):
            with self.subTest(model=model):
                self.assertEqual(self.match(f"Intel {model} Graphics Card $1999", "slickdeals-arc-b60"), "arc-b50-b60")
        for model in ("B650", "B660", "B860", "XB60", "B60X", "B600", "B50X"):
            with self.subTest(model=model):
                self.assertIsNone(self.match(f"Intel Arc {model} motherboard", "slickdeals-arc-b60"))
        self.assertIsNone(self.match("Fooarc B60 graphics card", "slickdeals-arc-b60"))

    def test_compendium_formats_and_pickup(self) -> None:
        # Observed titles from the compendium remain non-targets.
        for title in (
            "[GPU] Microcenter In Store Only- ASRock AMD Radeon RX 9060 XT Challenger OC Dual Fan 16GB GDDR6 PCIe 5.0 Graphics Card - $389.99",
            'THUNDEROBOT Radiant 16: 16" 2560x1600 300Hz, i9-14900HX, RTX 5080, 64GB DDR5, 2TB PCIe SSD $2458.99',
            "ASRock Z890 Taichi LGA 1851 Intel Z890 ATX Motherboard $200 + Free Shipping",
        ):
            with self.subTest(title=title):
                self.assertIsNone(self.match(title))
        # Target substitutions in the compendium's tagged and pickup formats.
        self.assertEqual(self.match("[GPU] Microcenter In Store Only- Intel Arc Pro B60 Dual 48GB $1599", "buildapcsales"), "arc-b50-b60")
        self.assertEqual(self.match("[Micro Center] Gigabyte NVIDIA GeForce RTX 5070 Ti WINDFORCE SFF Overclocked Triple Fan 16GB GPU $1149.99 + Free Store Pickup"), "rtx-5070-ti")

    def test_each_laptop_and_prebuilt_clue_without_category_tags(self) -> None:
        for clue in ('14"', '15.6"', '16\u201d', '18"', "14inch", "16-inch", "17.3-inch",
                     "18 inch", "OLED", "165Hz", "300 Hz", "275HX", "14900hx", "13620H",
                     "laptop", "notebook", "Gaming Laptop", "Laptop GPU", "Mobile",
                     "prebuilt", "pre-built", "gaming desktop", "PC:", "MSI Aegis",
                     "32GB DDR5", "1TB SSD", "Ryzen 7 9700X", "Core Ultra 7 265K", "i7-14700F"):
            with self.subTest(clue=clue):
                self.assertIsNone(self.match(f"RTX 5070 Ti {clue} $999"))

    def test_rtx_spelling_and_desktop_card_terms(self) -> None:
        for model in ("RTX 5070 Ti", "RTX5070Ti", "rtx 5070ti", "RTX\u2122 5070 Ti"):
            with self.subTest(model=model):
                self.assertEqual(self.match(f"{model} desktop graphics card 16GB GDDR7 2610MHz $9999"), "rtx-5070-ti")
        for model in ("RTX 5070", "RTX 5070 Titan", "RTX 15070 Ti", "RTX 5070TiX", "RTX 5080"):
            with self.subTest(model=model):
                self.assertIsNone(self.match(f"{model} graphics card"))

    def test_reddit_categories_and_source_scope(self) -> None:
        for title, expected in (("Intel Arc B50", "arc-b50-b60"), ("RTX 5070 Ti", "rtx-5070-ti")):
            with self.subTest(title=title):
                self.assertIsNone(self.match(title, "buildapcsales"))
                self.assertIsNone(self.match(f"[Laptop] {title}", "buildapcsales"))
                self.assertEqual(self.match(f"[GPU] {title}", "buildapcsales"), expected)
                self.assertIsNone(self.match(f"[GPU] {title}", "unconfigured"))

    def test_first_matching_rule_wins(self) -> None:
        item = FeedItem(item_id="1", source="feed", source_name="buildapcsales",
                        title="[GPU] RTX 5070 Ti $999", link="https://example.com/1")
        focused = self.settings.rules[1]
        broad = RuleConfig(name="all-deals")
        for rules, expected in (((focused, broad), "rtx-5070-ti"), ((broad, focused), "all-deals")):
            with self.subTest(expected=expected):
                matched = _match_item(item, rules)
                self.assertIsNotNone(matched)
                self.assertEqual(matched.rule_name, expected)
