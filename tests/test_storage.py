from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pricemon.models import FeedItem
from pricemon.storage import SeenStore


class SeenStoreTests(unittest.TestCase):
    def test_marks_seen_and_initialized(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = SeenStore(Path(temp_dir) / "seen.db")
            store.init()
            item = FeedItem(
                item_id="1",
                source="feed",
                source_name="buildapcsales",
                title="[GPU] RTX 5070 $499",
                link="https://example.com/1",
            )

            self.assertFalse(store.is_initialized())
            self.assertFalse(store.is_seen(item.item_id))

            store.mark_seen(item, rule_name="gpu", delivered=True)
            store.set_initialized()

            self.assertTrue(store.is_seen(item.item_id))
            self.assertTrue(store.is_initialized())

    def test_marks_source_initialized(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = SeenStore(Path(temp_dir) / "seen.db")
            store.init()

            self.assertFalse(store.is_source_initialized("slickdeals-5080"))

            store.set_source_initialized("slickdeals-5080")

            self.assertTrue(store.is_source_initialized("slickdeals-5080"))