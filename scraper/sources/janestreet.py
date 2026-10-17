"""Jane Street Monthly Quantitative Puzzle scraper."""

from __future__ import annotations

import calendar
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from scraper.http import create_session, load_source_cache, safe_get, save_source_cache
from scraper.models import CompetitionRecord
from scraper.normalize import build_record

logger = logging.getLogger(__name__)

SOURCE_NAME = "janestreet"
PUZZLE_URL = "https://www.janestreet.com/puzzles/current-puzzle/"


def scrape() -> List[CompetitionRecord]:
    session = create_session()
    resp = safe_get(session, PUZZLE_URL)
    now = datetime.now(timezone.utc)
    last_day = calendar.monthrange(now.year, now.month)[1]
    start_iso = f"{now.year:04d}-{now.month:02d}-01"
    end_iso = f"{now.year:04d}-{now.month:02d}-{last_day:02d}"

    puzzle_title = "Current Monthly Puzzle"
    puzzle_desc = (
        "Jane Street's monthly quantitative probability, combinatorics, and algorithmic "
        "thinking challenge. Solve before month-end to make the public solver leaderboard."
    )

    if resp is not None and resp.text:
        try:
            soup = BeautifulSoup(resp.text, "lxml")
            header = soup.select_one(".puzzle-header h3, .puzzle-title, h1, h3")
            if header:
                raw_t = header.get_text(" ", strip=True)
                if raw_t and len(raw_t) < 120:
                    puzzle_title = raw_t
            content = soup.select_one(".puzzle-content, .content, article p")
            if content:
                raw_d = content.get_text(" ", strip=True)
                if raw_d and len(raw_d) > 30:
                    puzzle_desc = raw_d[:450]
            save_source_cache(
                SOURCE_NAME,
                {"title": puzzle_title, "description": puzzle_desc, "month": f"{now.year:04d}-{now.month:02d}"},
            )
        except Exception as exc:
            logger.debug("Jane Street puzzle parse fallback: %s", exc)
    else:
        cached: Dict[str, Any] | None = load_source_cache(SOURCE_NAME)
        if isinstance(cached, dict):
            puzzle_title = str(cached.get("title") or puzzle_title)
            puzzle_desc = str(cached.get("description") or puzzle_desc)

    rec = build_record(
        title=f"Jane Street Monthly Quant Puzzle: {puzzle_title}",
        platform="Jane Street",
        source=SOURCE_NAME,
        url=PUZZLE_URL,
        prize="Leaderboard & Swag",
        start_date=start_iso,
        end_date=end_iso,
        raw_status="active",
        category="Valuation, Portfolio & Case Arenas",
        tags=["jane-street", "quant-puzzle", "probability", "combinatorics", "prop-trading"],
        description=puzzle_desc,
        organizer="Jane Street",
        evaluation_metric="Exact Mathematical Solution",
        difficulty="Advanced",
        competition_type="tournament",
    )

    records = [rec] if rec else []
    logger.info("Jane Street yielded %d active monthly puzzle", len(records))
    return records

