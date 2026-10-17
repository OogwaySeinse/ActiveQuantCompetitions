"""MLContests aggregator JSON feed filtered for Quantitative Finance & Limit Order Book challenges."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from scraper.http import create_session, load_source_cache, safe_get, save_source_cache
from scraper.models import CompetitionRecord
from scraper.normalize import build_record, is_quant_competition

logger = logging.getLogger(__name__)

SOURCE_NAME = "mlcontests"
JSON_URLS = [
    "https://raw.githubusercontent.com/mlcontests/mlcontests.github.io/master/competitions.json",
    "https://mlcontests.com/competitions.json",
]


def _extract_list(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("competitions", "data", "items", "active"):
            if isinstance(payload.get(key), list):
                return [x for x in payload[key] if isinstance(x, dict)]
    return []


def _parse_items(items: List[Dict[str, Any]]) -> List[CompetitionRecord]:
    records: List[CompetitionRecord] = []
    for item in items:
        title = item.get("title") or item.get("name") or ""
        url = item.get("url") or item.get("link") or ""
        platform = item.get("platform") or item.get("host") or item.get("organizer") or "Independent"
        prize = item.get("prize") or item.get("reward") or item.get("prize_pool") or "Knowledge"
        start_date = item.get("start") or item.get("start_date") or item.get("launched")
        end_date = item.get("deadline") or item.get("end") or item.get("end_date")
        tags = item.get("tags") if isinstance(item.get("tags"), list) else []
        category = item.get("category") or item.get("type") or ""
        desc = item.get("description") or item.get("summary") or ""
        organizer = item.get("organizer") or item.get("sponsor") or str(platform)

        if not is_quant_competition(
            str(title),
            description=str(desc),
            category=str(category),
            tags=[str(t) for t in tags],
            source_name=SOURCE_NAME,
            organizer=str(organizer),
        ):
            continue

        rec = build_record(
            title=str(title),
            platform=str(platform),
            source=SOURCE_NAME,
            url=str(url),
            prize=prize,
            start_date=str(start_date) if start_date else None,
            end_date=str(end_date) if end_date else None,
            category="",
            tags=[str(t) for t in tags],
            description=str(desc),
            organizer=str(organizer),
        )
        if rec:
            records.append(rec)
    return records


def scrape() -> List[CompetitionRecord]:
    session = create_session()
    items: List[Dict[str, Any]] = []

    for url in JSON_URLS:
        resp = safe_get(session, url)
        if not resp:
            continue
        try:
            payload = resp.json()
            items = _extract_list(payload)
            if items:
                save_source_cache(SOURCE_NAME, items)
                break
        except Exception as exc:
            logger.debug("MLContests JSON parse failed for %s: %s", url, exc)

    if not items:
        cached = load_source_cache(SOURCE_NAME)
        if cached:
            items = _extract_list(cached)

    records = _parse_items(items)
    logger.info("MLContests yielded %d active quant competitions", len(records))
    return records

