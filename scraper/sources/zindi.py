"""Zindi Africa API scraper filtered for Quantitative Finance, Insurance, and Risk."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from scraper.http import create_session, load_source_cache, safe_get, save_source_cache
from scraper.models import CompetitionRecord
from scraper.normalize import build_record, is_quant_competition

logger = logging.getLogger(__name__)

SOURCE_NAME = "zindi"
API_URL = "https://api.zindi.africa/v1/competitions"


def _fetch_api() -> List[Dict[str, Any]]:
    session = create_session()
    results: List[Dict[str, Any]] = []
    for page in range(0, 3):
        resp = safe_get(session, API_URL, params={"page": page, "per_page": 50})
        if not resp:
            break
        try:
            payload = resp.json()
            data = payload.get("data") if isinstance(payload, dict) else payload
            if not isinstance(data, list) or not data:
                break
            results.extend(data)
        except Exception as exc:
            logger.debug("Zindi JSON parse error on page %d: %s", page, exc)
            break
    return results


def _items_to_records(items: List[Dict[str, Any]]) -> List[CompetitionRecord]:
    records: List[CompetitionRecord] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        slug = item.get("id") or item.get("slug") or ""
        title = str(item.get("title") or item.get("name") or "").strip()
        if not title:
            continue

        kind = str(item.get("kind") or "competition").lower()
        reward = str(item.get("reward") or "Knowledge").strip()
        subtitle = str(item.get("subtitle") or item.get("description") or "").strip()
        tags = [t for t in (item.get("topics") or item.get("tags") or []) if isinstance(t, str)]

        if not is_quant_competition(
            title,
            description=subtitle,
            tags=tags,
            source_name=SOURCE_NAME,
            organizer="Zindi",
        ):
            continue

        url = f"https://zindi.africa/competitions/{slug}" if slug else str(item.get("url") or "")
        comp_type = "hackathon" if "hackathon" in kind else ("benchmark" if reward.lower() == "knowledge" else "competition")

        rec = build_record(
            title=title,
            platform="Zindi",
            source=SOURCE_NAME,
            url=url,
            prize=reward,
            start_date=item.get("start_time") or item.get("Opens_at"),
            end_date=item.get("end_time") or item.get("closes_at"),
            raw_status=str(item.get("status") or "active"),
            tags=tags,
            description=subtitle,
            organizer="Zindi",
            competitors_count=item.get("all_users_count") or item.get("participants_count"),
            competition_type=comp_type,
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
    logger.info("Zindi yielded %d active quant competitions", len(records))
    return records

