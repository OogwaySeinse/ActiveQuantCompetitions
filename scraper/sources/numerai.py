"""Numerai Tournament GraphQL scraper (Classic Equities, Signals, and Crypto)."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from scraper.http import create_session, load_source_cache, safe_post, save_source_cache
from scraper.models import CompetitionRecord
from scraper.normalize import build_record

logger = logging.getLogger(__name__)

SOURCE_NAME = "numerai"
GRAPHQL_URL = "https://api-tournament.numer.ai/"

NUMERAI_TOURNAMENTS: List[Dict[str, Any]] = [
    {
        "tournament_id": 8,
        "slug": "numerai",
        "title": "Numerai Classic: Global Equity Hedge Fund Tournament",
        "url": "https://numer.ai/tournament",
        "prize": "$52,000+ NMR Staking Pool",
        "prize_usd": 52000.0,
        "category": "Alpha & Equity Prediction",
        "evaluation_metric": "CORR20v2 & Meta-Model Contribution (MMC)",
        "difficulty": "Advanced",
        "competitors_count": 4650,
        "tags": ["equities", "market-neutral", "alpha", "staking", "tabular", "hedge-fund"],
        "description": (
            "Model obfuscated global equity factor features to predict 20-day cross-sectional "
            "stock returns for Numerai's market-neutral hedge fund. Weekly rounds with NMR payouts."
        ),
    },
    {
        "tournament_id": 11,
        "slug": "signals",
        "title": "Numerai Signals: Raw Global Equities Alpha Tournament",
        "url": "https://signals.numer.ai",
        "prize": "$35,000+ NMR Staking Pool",
        "prize_usd": 35000.0,
        "category": "Alpha & Equity Prediction",
        "evaluation_metric": "Feature-Neutral Correlation (FNCv4) & IC",
        "difficulty": "Advanced",
        "competitors_count": 1420,
        "tags": ["signals", "equities", "alpha-research", "bring-your-own-data", "long-short"],
        "description": (
            "Bring your own market, fundamental, or alternative datasets to generate orthogonal "
            "equity alpha signals over 5,000+ global stocks."
        ),
    },
    {
        "tournament_id": 12,
        "slug": "crypto",
        "title": "Numerai Crypto: Digital Assets Meta-Model Tournament",
        "url": "https://crypto.numer.ai",
        "prize": "$25,000+ NMR Staking Pool",
        "prize_usd": 25000.0,
        "category": "Crypto, DeFi & Digital Assets",
        "evaluation_metric": "Spearman Rank Correlation (30d Return)",
        "difficulty": "Intermediate",
        "competitors_count": 980,
        "tags": ["crypto", "digital-assets", "cross-sectional", "meta-model", "numerai"],
        "description": (
            "Predict cross-sectional 30-day forward returns across the top 100+ liquid "
            "cryptocurrencies and tokens to power the Numerai Crypto Meta-Model."
        ),
    },
]


def _fetch_latest_round(session: Any, tournament_id: int) -> Optional[Dict[str, Any]]:
    query = f"{{ rounds(tournament: {tournament_id}) {{ number openTime closeTime resolveTime }} }}"
    resp = safe_post(session, GRAPHQL_URL, json_body={"query": query}, delay=0.1)
    if not resp:
        return None
    try:
        payload = resp.json()
        rounds = ((payload.get("data") or {}).get("rounds")) or []
        if rounds and isinstance(rounds, list):
            return rounds[0]
    except Exception as exc:
        logger.debug("Numerai round parse failed for tournament %s: %s", tournament_id, exc)
    return None


def scrape() -> List[CompetitionRecord]:
    session = create_session()
    records: List[CompetitionRecord] = []
    raw_cache: List[Dict[str, Any]] = []

    for meta in NUMERAI_TOURNAMENTS:
        latest = _fetch_latest_round(session, meta["tournament_id"])
        if latest:
            raw_cache.append({"tournament": meta["slug"], "latest_round": latest})

        round_num = latest.get("number") if isinstance(latest, dict) else None
        open_time = latest.get("openTime") if isinstance(latest, dict) else None
        resolve_time = latest.get("resolveTime") if isinstance(latest, dict) else None

        desc = meta["description"]
        if round_num:
            desc = f"[Live Round #{round_num}] {desc}"

        rec = build_record(
            title=meta["title"],
            platform="Numerai",
            source=SOURCE_NAME,
            url=meta["url"],
            prize=meta["prize"],
            prize_usd_override=meta["prize_usd"],
            start_date=str(open_time)[:10] if open_time else None,
            end_date=str(resolve_time)[:10] if resolve_time else None,
            raw_status="active",
            category=meta["category"],
            tags=list(meta["tags"]),
            description=desc,
            organizer="Numerai",
            evaluation_metric=meta["evaluation_metric"],
            competitors_count=meta["competitors_count"],
            difficulty=meta["difficulty"],
            competition_type="tournament",
        )
        if rec:
            records.append(rec)

    if raw_cache:
        save_source_cache(SOURCE_NAME, raw_cache)
    else:
        load_source_cache(SOURCE_NAME)

    logger.info("Numerai yielded %d active quant tournaments", len(records))
    return records

