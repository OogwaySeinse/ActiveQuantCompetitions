"""Alibaba Tianchi competitions API scraper filtered for Quant & Financial ML."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from scraper.http import create_session, load_source_cache, safe_get, save_source_cache
from scraper.models import CompetitionRecord
from scraper.normalize import build_record, is_quant_competition

logger = logging.getLogger(__name__)

SOURCE_NAME = "tianchi"
API_URL = "https://tianchi.aliyun.com/competition/proxy/api/competition/api/race/listBrief"


def _fetch_api() -> List[Dict[str, Any]]:
    session = create_session()
    resp = safe_get(
        session,
        API_URL,
        params={
            "pageNum": 1,
            "pageSize": 50,
            "state": 1,
        },
        headers={
            "Accept": "application/json",
            "Referer": "https://tianchi.aliyun.com/competition/gameList/activeList",
        },
    )
    if not resp:
        return []
    try:
        payload = resp.json()
        data = payload.get("data") if isinstance(payload, dict) else None
        rows = data.get("list") if isinstance(data, dict) else None
        if isinstance(rows, list):
            return rows
    except Exception as exc:
        logger.debug("Tianchi JSON parse failed: %s", exc)
    return []


def _items_to_records(items: List[Dict[str, Any]]) -> List[CompetitionRecord]:
    records: List[CompetitionRecord] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        race_id = item.get("raceId") or item.get("id")
        title = str(item.get("raceNameEn") or item.get("raceName") or "").strip()
        if not title or not race_id:
            continue

        desc = str(item.get("briefEn") or item.get("brief") or "").strip()
        if not is_quant_competition(
            title,
            description=desc,
            source_name=SOURCE_NAME,
            organizer="Alibaba Tianchi",
        ):
            continue

        url = f"https://tianchi.aliyun.com/competition/entrance/{race_id}/introduction"
        bonus = item.get("bonus") or item.get("bonusTxt") or "Knowledge"
        currency = str(item.get("currencySymbol") or "¥")
        prize_str = f"{currency}{bonus}" if isinstance(bonus, (int, float)) and bonus > 0 else str(bonus)
        end_raw = item.get("currentSeasonEnd") or item.get("raceEndTime") or item.get("endTime")
        start_raw = item.get("currentSeasonStart") or item.get("raceStartTime") or item.get("startTime")

        rec = build_record(
            title=title,
            platform="Alibaba Tianchi",
            source=SOURCE_NAME,
            url=url,
            prize=prize_str,
            start_date=str(start_raw) if start_raw else None,
            end_date=str(end_raw) if end_raw else None,
            description=desc,
            organizer="Alibaba Cloud Tianchi",
            teams_count=item.get("teamNum"),
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
    logger.info("Tianchi yielded %d active quant competitions", len(records))
    return records

