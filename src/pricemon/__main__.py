from __future__ import annotations

import argparse
import asyncio
import sys

from .config import load_settings
from .models import FeedItem, MatchedItem
from .monitor import _format_result, run_forever, run_once, validate_delivery_settings
from .telegram import render_message, send_message


def main() -> None:
    parser = argparse.ArgumentParser(description="RSS-to-Telegram PC deals monitor")
    parser.add_argument("--config", help="Path to config.toml")
    parser.add_argument("--once", action="store_true", help="Poll once and exit")
    parser.add_argument("--dry-run", action="store_true", help="Print matches without sending or writing state")
    parser.add_argument("--send-test", action="store_true", help="Send a test Telegram notification and exit")
    args = parser.parse_args()

    settings = load_settings(args.config)
    try:
        if args.send_test:
            validate_delivery_settings(settings)
            asyncio.run(_send_test(settings.telegram_bot_token, settings.telegram_chat_id))
            return

        if args.dry_run:
            result = asyncio.run(run_once(settings, dry_run=True))
            print(_format_result(result))
            return

        validate_delivery_settings(settings)
        if args.once:
            result = asyncio.run(run_once(settings))
            print(_format_result(result))
            return
        asyncio.run(run_forever(settings))
    except KeyboardInterrupt:
        return
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


async def _send_test(bot_token: str, chat_id: str) -> None:
    item = FeedItem(
        item_id="test",
        source="pricemon",
        source_name="test",
        title="[GPU] Test alert - $499.99",
        link="https://github.com/jcentner/pricemon",
    )
    await send_message(
        bot_token=bot_token,
        chat_id=chat_id,
        text=render_message(MatchedItem(item=item, rule_name="test")),
    )


if __name__ == "__main__":
    main()