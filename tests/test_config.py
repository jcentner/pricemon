from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pricemon.config import load_settings


class ConfigTests(unittest.TestCase):
    def test_defaults_to_buildapcsales_feed(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = load_settings("missing-config.toml")

        self.assertEqual(settings.poll_interval_seconds, 45)
        self.assertEqual(len(settings.sources), 1)
        self.assertEqual(settings.sources[0].name, "buildapcsales")

    def test_loads_source_filters_from_toml(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            config_path.write_text(
                """
poll_interval_seconds = 30

[[sources]]
name = "gpu"
url = "https://www.reddit.com/r/buildapcsales/new/.rss"
include = ["RTX"]
exclude = ["prebuilt"]
categories = ["GPU"]
""".strip(),
                encoding="utf-8",
            )

            with patch.dict(os.environ, {}, clear=True):
                settings = load_settings(config_path)

        self.assertEqual(settings.poll_interval_seconds, 30)
        self.assertEqual(settings.sources[0].include, ("rtx",))
        self.assertEqual(settings.sources[0].exclude, ("prebuilt",))
        self.assertEqual(settings.sources[0].categories, ("gpu",))