from __future__ import annotations

from .config import load_settings


def main() -> None:
    settings = load_settings()
    print(
        "pricemon configured: "
        f"{len(settings.sources)} source(s), "
        f"poll every {settings.poll_interval_seconds}s"
    )


if __name__ == "__main__":
    main()