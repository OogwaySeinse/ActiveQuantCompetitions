"""Codabench / CodaLab public competitions API scraper filtered for Quant & Financial ML."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from scraper.http import create_session, load_source_cache, safe_get, save_source_cache
from scraper.models import CompetitionRecord
from scraper.normalize import build_record, is_quant_competition

logger = logging.getLogger(__name__)

SOURCE_NAME = "codalab"
CODABENCH_API = "https://www.codabench.org/api/competitions/public/"


def _fetch_codabench() -> List[Dict[str, Any]]:
    session = create_session()
    results: List[Dict[str, Any]] = []
    for page in range(1, 3):
        resp = safe_get(
            session,
            CODABENCH_API,
            params={"page": page, "search": ""},
            headers={"Accept": "application/json"},
        )
        if not resp:
            break
        try:
            payload = resp.json()
            rows = payload.get("results") if isinstance(payload, dict) else payload
            if not isinstance(rows, list) or not rows:
                break
            results.extend(rows)
        except Exception as exc:
            logger.debug("Codabench parse error page %d: %s", page, exc)
            break
    return results


def _items_to_records(items: List[Dict[str, Any]]) -> List[CompetitionRecord]:
    records: List[CompetitionRecord] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        comp_id = item.get("id")
        title = str(item.get("title") or "").strip()
        if not title or not comp_id:
            continue

        desc = str(item.get("description") or "").strip()
        organizer = str(item.get("created_by") or "Codabench")
        if not is_quant_competition(
            title,
            description=desc,
            source_name=SOURCE_NAME,
            organizer=organizer,
        ):
            continue

        url = f"https://www.codabench.org/competitions/{comp_id}/"
        reward = item.get("reward") or "Knowledge"

        rec = build_record(
            title=title,
            platform="Codabench",
            source=SOURCE_NAME,
            url=url,
            prize=reward,
            start_date=item.get("created_when"),
            end_date=item.get("end_date") or item.get(" end_time"),
            description=desc,
            organizer=organizer,
            competitors_count=item.get("participants_count"),
        )
        if rec:
            records.append(rec)
    return records


def scrape() -> List[CompetitionRecord]:
    items = _fetch_codabench()
    if items:
        save_source_cache(SOURCE_NAME, items)
    else:
        cached = load_source_cache(SOURCE_NAME)
        if isinstance(cached, list):
            items = cached

    records = _items_to_records(items)
    logger.info("Codabench yielded %d active quant competitions", len(records))
    return records

