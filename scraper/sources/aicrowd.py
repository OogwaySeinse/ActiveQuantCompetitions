"""AIcrowd source scraper filtered for Quantitative Finance & Time-Series Forecasting."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from scraper.http import create_session, load_source_cache, safe_get, save_source_cache
from scraper.models import CompetitionRecord
from scraper.normalize import build_record, is_quant_competition

logger = logging.getLogger(__name__)

SOURCE_NAME = "aicrowd"
CHALLENGES_URL = "https://www.aicrowd.com/challenges"


def _parse_html(html: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    items: List[Dict[str, Any]] = []
    seen_urls: set[str] = set()

    for node in soup.select("[data-react-props]"):
        raw = node.get("data-react-props")
        if not raw:
            continue
        try:
            data = json.loads(raw)
            challenges = data.get("challenges") if isinstance(data, dict) else None
            if isinstance(challenges, list):
                for ch in challenges:
                    title = ch.get("title") or ch.get("name") or ""
                    slug = ch.get("slug") or ""
                    url = ch.get("url") or (f"https://www.aicrowd.com/challenges/{slug}" if slug else "")
                    if not title or not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    items.append(
                        {
                            "title": title,
                            "url": url,
                            "prize": ch.get("prize") or ch.get("reward") or "Knowledge",
                            "end_date": ch.get("end_at") or ch.get("ends_at") or ch.get("deadline"),
                            "start_date": ch.get("start_at") or ch.get("starts_at"),
                            "status": ch.get("status") or "active",
                            "description": ch.get("tagline") or ch.get("description") or "",
                        }
                    )
        except Exception:
            continue

    for a in soup.select("a[href*='/challenges/']"):
        href = a.get("href", "")
        if not href or href.endswith("/challenges") or "/leaderboards" in href or "/problems" in href:
            continue
        url = href if href.startswith("http") else f"https://www.aicrowd.com{href}"
        if url in seen_urls:
            continue
        card = a.find_parent(["div", "article", "li"]) or a
        title_el = card.select_one("h3, h4, h5, .challenge-title")
        title = title_el.get_text(" ", strip=True) if title_el else a.get_text(" ", strip=True)
        if not title or len(title) < 4:
            continue
        text_blob = card.get_text(" ", strip=True)
        if re.search(r"\b(completed|ended|closed)\b", text_blob, re.IGNORECASE):
            continue
        seen_urls.add(url)
        prize_match = re.search(r"((?:\$|USD\s*|EUR\s*|€)[\d,]+(?:\s*[kKmM])?)", text_blob)
        items.append(
            {
                "title": title,
                "url": url,
                "prize": prize_match.group(1) if prize_match else "Knowledge",
                "end_date": None,
                "status": "active",
                "description": text_blob[:260],
            }
        )

    return items


def scrape() -> List[CompetitionRecord]:
    session = create_session()
    resp = safe_get(session, CHALLENGES_URL)
    items: List[Dict[str, Any]] = []

    if resp and resp.text:
        items = _parse_html(resp.text)
        if items:
            save_source_cache(SOURCE_NAME, items)

    if not items:
        cached = load_source_cache(SOURCE_NAME)
        if isinstance(cached, list):
            items = cached

    records: List[CompetitionRecord] = []
    for item in items:
        title = str(item.get("title") or "")
        desc = str(item.get("description") or "")
        if not is_quant_competition(title, description=desc, source_name=SOURCE_NAME):
            continue
        rec = build_record(
            title=title,
            platform="AIcrowd",
            source=SOURCE_NAME,
            url=str(item.get("url") or ""),
            prize=item.get("prize"),
            start_date=item.get("start_date"),
            end_date=item.get("end_date"),
            raw_status=str(item.get("status") or "active"),
            description=desc,
            organizer="AIcrowd",
        )
        if rec:
            records.append(rec)

    logger.info("AIcrowd yielded %d active quant competitions", len(records))
    return records

