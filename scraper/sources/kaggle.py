"""Kaggle source scraper filtered for Quantitative Finance, Trading, and Financial ML."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from scraper.http import create_session, load_source_cache, safe_get, save_source_cache
from scraper.models import CompetitionRecord
from scraper.normalize import build_record, is_quant_competition

logger = logging.getLogger(__name__)

SOURCE_NAME = "kaggle"
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

QUANT_SEARCH_TERMS = [
    "",
    "quant",
    "trading",
    "finance",
    "stock",
    "crypto",
    "order book",
    "volatility",
    "credit risk",
    "fraud",
    "portfolio",
    "insurance",
    "price prediction",
]


def _bootstrap_local_kaggle_Auth() -> bool:
    """Load credentials from env vars, ~/.kaggle/kaggle.json, or repo-root kaggle.json."""
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        return True
    if os.environ.get("KAGGLE_API_TOKEN"):
        return True

    candidates = [
        ROOT_DIR / "kaggle.json",
        Path.home() / ".kaggle" / "kaggle.json",
    ]
    for path in candidates:
        if path.exists():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                username = raw.get("username")
                key = raw.get("key")
                if username and key:
                    os.environ["KAGGLE_USERNAME"] = str(username).strip()
                    os.environ["KAGGLE_KEY"] = str(key).strip()
                    return True
            except Exception as exc:
                logger.debug("Failed reading %s: %s", path, exc)
    return False


def _scrape_via_kaggle_sdk() -> List[Dict[str, Any]]:
    if not _bootstrap_local_kaggle_Auth():
        return []

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        items: List[Dict[str, Any]] = []
        seen_refs: set[str] = set()

        for term in QUANT_SEARCH_TERMS:
            max_pages = 3 if term == "" else 1
            for page in range(1, max_pages + 1):
                kwargs: Dict[str, Any] = {"page": page}
                if term:
                    kwargs["search"] = term
                resp = api.competitions_list(**kwargs)
                comps = list(getattr(resp, "competitions", resp) or []) if resp is not None else []
                if not comps:
                    break
                for c in comps:
                    ref = str(getattr(c, "ref", "") or getattr(c, "url", "") or "")
                    if not ref or ref in seen_refs:
                        continue
                    seen_refs.add(ref)
                    tags = [str(getattr(t, "name", t)) for t in (getattr(c, "tags", None) or [])]
                    url = ref if ref.startswith("http") else f"https://www.kaggle.com/competitions/{ref}"
                    items.append(
                        {
                            "title": getattr(c, "title", ""),
                            "url": url,
                            "prize": getattr(c, "reward", "Knowledge"),
                            "end_date": str(getattr(c, "deadline", "") or ""),
                            "start_date": str(getattr(c, "enabledDate", "") or getattr(c, "enabled_date", "") or ""),
                            "category": getattr(c, "category", ""),
                            "description": getattr(c, "description", ""),
                            "organization_name": getattr(c, "organizationName", None)
                            or getattr(c, "organization_name", None)
                            or "Kaggle",
                            "evaluation_metric": getattr(c, "evaluationMetric", None)
                            or getattr(c, "evaluation_metric", None)
                            or "",
                            "teams_count": getattr(c, "teamCount", None) or getattr(c, "team_count", None),
                            "tags": tags,
                        }
                    )
        return items
    except Exception as exc:
        logger.warning("Kaggle SDK fetch failed: %s", exc)
        return []


def _scrape_via_public_endpoint() -> List[Dict[str, Any]]:
    session = create_session()
    items: List[Dict[str, Any]] = []
    resp = safe_get(session, "https://www.kaggle.com/competitions")
    if not resp or not resp.text:
        return items

    soup = BeautifulSoup(resp.text, "lxml")
    for script in soup.find_all("script"):
        text = script.string or ""
        if "competitions" in text and "reward" in text:
            try:
                start = text.find("{")
                end = text.rfind("}")
                if start != -1 and end != -1:
                    data = json.loads(text[start : end + 1])
                    for comp in data.get("competitions", []):
                        slug = comp.get("competitionName") or comp.get("slug") or ""
                        items.append(
                            {
                                "title": comp.get("title", ""),
                                "url": f"https://www.kaggle.com/competitions/{slug}" if slug else "",
                                "prize": comp.get("rewardDisplay") or comp.get("reward") or "Knowledge",
                                "end_date": comp.get("deadline", ""),
                                "start_date": comp.get("enabledDate", ""),
                                "category": comp.get("hostSegmentTitle", ""),
                                "description": comp.get("briefDescription", ""),
                                "organization_name": comp.get("organizationName", "Kaggle"),
                                "evaluation_metric": comp.get("evaluationMetric", ""),
                                "teams_count": comp.get("totalTeams"),
                                "tags": [t.get("name", "") for t in (comp.get("tags") or []) if isinstance(t, dict)],
                            }
                        )
            except Exception:
                continue
    return items


def _items_to_records(items: List[Dict[str, Any]]) -> List[CompetitionRecord]:
    records: List[CompetitionRecord] = []
    for item in items:
        title = str(item.get("title") or "").strip()
        desc = str(item.get("description") or "").strip()
        raw_cat = str(item.get("category") or "").strip()
        tags = list(item.get("tags") or [])
        organizer = str(item.get("organization_name") or "Kaggle")

        if not is_quant_competition(
            title,
            description=desc,
            category=raw_cat,
            tags=tags,
            source_name=SOURCE_NAME,
            organizer=organizer,
        ):
            continue

        comp_type = "benchmark" if raw_cat.lower() in {"getting started", "playground"} else ""
        rec = build_record(
            title=title,
            platform="Kaggle",
            source=SOURCE_NAME,
            url=str(item.get("url") or ""),
            prize=item.get("prize"),
            start_date=item.get("start_date"),
            end_date=item.get("end_date"),
            category="",
            tags=tags + ([raw_cat] if raw_cat else []),
            description=desc,
            organizer=organizer,
            evaluation_metric=str(item.get("evaluation_metric") or ""),
            teams_count=item.get("teams_count"),
            competition_type=comp_type,
        )
        if rec:
            records.append(rec)
    return records


def scrape() -> List[CompetitionRecord]:
    items = _scrape_via_kaggle_sdk()
    if not items:
        items = _scrape_via_public_endpoint()

    if items:
        save_source_cache(SOURCE_NAME, items)
    else:
        cached = load_source_cache(SOURCE_NAME)
        if isinstance(cached, list):
            items = cached

    records = _items_to_records(items)
    logger.info("Kaggle yielded %d active quant competitions", len(records))
    return records
