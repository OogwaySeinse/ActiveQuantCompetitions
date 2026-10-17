"""CrunchDAO Hub REST API scraper for quantitative finance and decentralized ML competitions."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from scraper.http import create_session, load_source_cache, safe_get, save_source_cache
from scraper.models import CompetitionRecord
from scraper.normalize import build_record, is_quant_competition

logger = logging.getLogger(__name__)

SOURCE_NAME = "crunchdao"
API_URL = "https://api.hub.crunchdao.com/v1/competitions"


def _parse_items(items: List[Dict[str, Any]]) -> List[CompetitionRecord]:
    records: List[CompetitionRecord] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        status_raw = str(item.get("status") or "").upper()
        if status_raw not in {"OPEN", "PENDING"}:
            continue

        slug = str(item.get("name") or item.get("id") or "").strip()
        title = str(item.get("fullName") or item.get("displayName") or slug).strip()
        desc = str(item.get("shortDescription") or "").strip()
        organizer = str(item.get("hostedByName") or "CrunchDAO").strip()

        tags = ["crunchdao", "decentralized-ml"]
        mode = str(item.get("mode") or "").lower()
        if mode:
            tags.append(mode)
        if item.get("continuous"):
            tags.append("continuous")

        if not is_quant_competition(
            title,
            description=desc,
            tags=tags,
            source_name=SOURCE_NAME,
            organizer=organizer,
        ):
            continue

        raw_url = str(item.get("url") or "").strip().rstrip("/")
        if slug and (not raw_url or raw_url in {"https://hub.crunchdao.com", "http://hub.crunchdao.com"}):
            url = f"https://hub.crunchdao.com/competitions/{slug}"
        else:
            url = raw_url or f"https://hub.crunchdao.com/competitions/{slug}"

        prize_text = item.get("prizePoolText") or item.get("prizePoolUsd") or "USDC Rewards"
        prize_usd_raw = item.get("prizePoolUsd")
        prize_usd_override = None
        if prize_usd_raw is not None:
            try:
                prize_usd_override = float(prize_usd_raw)
            except (TypeError, ValueError):
                prize_usd_override = None

        stats = item.get("statistics") if isinstance(item.get("statistics"), dict) else {}
        participants = stats.get("participants") or stats.get("entrants")
        teams = stats.get("teams")
        submissions = stats.get("submissions")

        continuous = bool(item.get("continuous"))
        end_raw = None if continuous else item.get("end")
        start_raw = item.get("start")
        comp_type = "tournament" if continuous else "competition"
        raw_state = "upcoming" if status_raw == "PENDING" else "active"

        rec = build_record(
            title=title,
            platform="CrunchDAO",
            source=SOURCE_NAME,
            url=url,
            prize=prize_text,
            prize_usd_override=prize_usd_override,
            start_date=str(start_raw) if start_raw else None,
            end_date=str(end_raw) if end_raw else None,
            raw_status=raw_state,
            tags=tags,
            description=desc,
            organizer=organizer,
            teams_count=int(teams) if isinstance(teams, int) and teams > 0 else None,
            competitors_count=int(participants) if isinstance(participants, int) and participants > 0 else None,
            entries_count=int(submissions) if isinstance(submissions, int) and submissions > 0 else None,
            competition_type=comp_type,
        )
        if rec:
            records.append(rec)

    return records


def scrape() -> List[CompetitionRecord]:
    session = create_session()
    resp = safe_get(session, API_URL)
    items: List[Dict[str, Any]] = []

    if resp is not None:
        try:
            payload = resp.json()
            if isinstance(payload, list):
                items = payload
                save_source_cache(SOURCE_NAME, items)
        except Exception as exc:
            logger.warning("CrunchDAO JSON parse failed: %s", exc)

    if not items:
        cached = load_source_cache(SOURCE_NAME)
        if isinstance(cached, list):
            items = cached

    records = _parse_items(items)
    logger.info("CrunchDAO yielded %d active quant competitions", len(records))
    return records
