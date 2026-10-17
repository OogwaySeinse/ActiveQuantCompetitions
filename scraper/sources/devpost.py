"""Devpost JSON API scraper for Quantitative Finance, Algorithmic Trading, and FinTech hackathons."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from scraper.http import create_session, load_source_cache, safe_get, save_source_cache
from scraper.models import CompetitionRecord
from scraper.normalize import build_record, is_quant_competition

logger = logging.getLogger(__name__)

SOURCE_NAME = "devpost"
API_URL = "https://devpost.com/api/hackathons"
SEARCH_QUERIES = ["quantitative finance", "algorithmic trading", "quant trading", "fintech", "defi trading"]


def _clean_html_text(raw: str) -> str:
    if not raw:
        return ""
    if "<" in raw and ">" in raw:
        return BeautifulSoup(raw, "lxml").get_text(" ", strip=True)
    return raw.strip()


def _parse_date_range(date_str: str) -> tuple[str | None, str | None]:
    text = (date_str or "").strip()
    if not text:
        return (None, None)
    if " - " in text:
        left, right = text.split(" - ", 1)
        year_match = re.search(r"(\d{4})", right)
        if year_match and not re.search(r"\d{4}", left):
            left = f"{left}, {year_match.group(1)}"
        month_match = re.match(r"^([A-Za-z]{3,9})\s+\d{1,2}", left)
        if month_match and re.match(r"^\d{1,2},?\s*\d{4}$", right.strip()):
            right = f"{month_match.group(1)} {right.strip()}"
        return (left.strip(), right.strip())
    return (None, text)


def _fetch_api() -> List[Dict[str, Any]]:
    session = create_session()
    collected: Dict[str, Dict[str, Any]] = {}

    for query in SEARCH_QUERIES:
        resp = safe_get(
            session,
            API_URL,
            params={
                "status[]": ["open", "upcoming"],
                "search": query,
                "page": 1,
            },
            headers={"Accept": "application/json"},
        )
        if not resp:
            continue
        try:
            payload = resp.json()
            hackathons = payload.get("hackathons") if isinstance(payload, dict) else []
            if not isinstance(hackathons, list):
                continue
            for h in hackathons:
                url = str(h.get("url") or "")
                if url and url not in collected:
                    collected[url] = h
        except Exception as exc:
            logger.debug("Devpost JSON parse failed for '%s': %s", query, exc)

    return list(collected.values())


def _items_to_records(items: List[Dict[str, Any]]) -> List[CompetitionRecord]:
    records: List[CompetitionRecord] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        title = _clean_html_text(str(item.get("title") or ""))
        url = str(item.get("url") or "")
        if not title or not url:
            continue

        prize_raw = _clean_html_text(str(item.get("prize_amount") or "Knowledge"))
        themes = [
            str(t.get("name", "")).strip()
            for t in (item.get("themes") or [])
            if isinstance(t, dict) and t.get("name")
        ]
        org = str(item.get("organization_name") or "Devpost")

        if not is_quant_competition(
            title,
            description=" ".join(themes),
            tags=themes,
            source_name=SOURCE_NAME,
            organizer=org,
        ):
            continue

        start_raw, end_raw = _parse_date_range(str(item.get("submission_period_dates") or ""))
        open_state = str(item.get("open_state") or "open").lower()

        rec = build_record(
            title=title,
            platform="Devpost",
            source=SOURCE_NAME,
            url=url,
            prize=prize_raw,
            start_date=start_raw,
            end_date=end_raw,
            raw_status="upcoming" if open_state == "upcoming" else "active",
            tags=themes,
            description=f"Quantitative & FinTech hackathon hosted by {org}. Themes: {', '.join(themes) or 'Quant Finance'}.",
            organizer=org,
            competitors_count=item.get("registrations_count"),
            competition_type="hackathon",
        )
        if rec:
            records.append(rec)
    return records


def scrape() -> List[CompetitionRecord]:
    items = _fetch_api()
    if items:
        save_source_cache(SOURCE_NAME, items)
    else:
        cached = load_source_cache(SOURCE_NAME)
        if isinstance(cached, list):
            items = cached

    records = _items_to_records(items)
    logger.info("Devpost yielded %d active quant hackathons", len(records))
    return records

