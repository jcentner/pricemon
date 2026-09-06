from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pricemon.config import _load_rules, load_settings


class ConfigTests(unittest.TestCase):
    def test_defaults_to_buildapcsales_feed(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = load_settings("missing-config.toml")

        self.assertEqual(settings.poll_interval_seconds, 60)
        self.assertEqual(len(settings.sources), 1)
        self.assertEqual(settings.sources[0].name, "buildapcsales")
        self.assertEqual(settings.rules[0].name, "all-deals")
        self.assertEqual(settings.rules[0].exclude_any, ("expired", "sold out"))
        self.assertEqual(settings.rules[0].exclude_patterns, ())

    def test_loads_rules_from_toml(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            config_path.write_text(
                r"""
poll_interval_seconds = 30

[[sources]]
name = "gpu"
url = "https://www.reddit.com/r/buildapcsales/new/.rss"

[[rules]]
name = "rtx-gpu"
sources = ["gpu"]
include_any = ["RTX"]
exclude_any = ["prebuilt"]
exclude_patterns = ['\BRTX', '(?P<GPU>RTX)(?P=GPU)', ' OLED ']
categories = ["GPU"]
max_price = 650
""".strip(),
                encoding="utf-8",
            )

            with patch.dict(os.environ, {}, clear=True):
                settings = load_settings(config_path)

        self.assertEqual(settings.poll_interval_seconds, 30)
        self.assertEqual(settings.sources[0].name, "gpu")
        self.assertEqual(settings.rules[0].name, "rtx-gpu")
        self.assertEqual(settings.rules[0].sources, ("gpu",))
        self.assertEqual(settings.rules[0].include_any, ("rtx",))
        self.assertEqual(settings.rules[0].exclude_any, ("prebuilt",))
        self.assertEqual(
            settings.rules[0].exclude_patterns,
            (r"\BRTX", r"(?P<GPU>RTX)(?P=GPU)", " OLED "),
        )
        self.assertEqual(settings.rules[0].categories, ("gpu",))
        self.assertEqual(settings.rules[0].max_price, 650)

    def test_loads_source_specific_categories(self) -> None:
        rules = _load_rules([{
            "name": "gpu",
            "categories": {"BuildAPCSales": ["GPU"], "slickdeals": []},
        }])
        self.assertEqual(rules[0].categories, {"buildapcsales": ("gpu",), "slickdeals": ()})

    def test_rejects_invalid_exclude_patterns(self) -> None:
        for patterns in ("laptop", [123], ["["], ["(?P<GPU>RTX)(?P=missing)"]):
            with self.subTest(patterns=patterns):
                with self.assertRaisesRegex(ValueError, "rule 'gpu'.*exclude_patterns"):
                    _load_rules([{"name": "gpu", "exclude_patterns": patterns}])

    def test_rejects_invalid_source_categories(self) -> None:
        with self.assertRaisesRegex(ValueError, "filter values must be lists"):
            _load_rules([{"name": "gpu", "categories": {"buildapcsales": "gpu"}}])