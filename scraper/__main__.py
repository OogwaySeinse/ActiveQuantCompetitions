from __future__ import annotations

import argparse
import logging
import sys

from scraper.pipeline import run_pipeline
from scraper.sources import ALL_SCRAPERS


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scrape and normalize active Quant & Financial ML competitions across all platforms."
    )
    parser.add_argument(
        "--sources",
        nargs="*",
        choices=sorted(ALL_SCRAPERS.keys()),
        help="Optional subset of scraper sources to run.",
    )
    parser.add_argument(
        "--min-records",
        type=int,
        default=1,
        help="Minimum number of active quant records required for exit code 0.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    payload = run_pipeline(selected_sources=args.sources)
    total = payload["metadata"]["total_active"]
    total_prize = payload["metadata"]["total_prize_usd"]
    logging.info("Pipeline complete: %d active quant competitions ($%s total prize pool)", total, f"{total_prize:,.0f}")

    if total < args.min_records:
        logging.error("Active quant competitions (%d) below minimum threshold (%d)", total, args.min_records)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

