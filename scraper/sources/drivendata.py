"""DrivenData scraper filtered for Quantitative Finance & Econometrics."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from scraper.http import create_session, load_source_cache, safe_get, save_source_cache
from scraper.models import CompetitionRecord
from scraper.normalize import build_record, is_quant_competition

logger = logging.getLogger(__name__)

SOURCE_NAME = "drivendata"
COMPETITIONS_URL = "https://www.drivendata.org/competitions/"


def _parse_html(html: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    items: List[Dict[str, Any]] = []

    active_Root = soup.find(id="active-comps") or soup
    cards = active_Root.select(".comp-card, .competition-tile, a[href*='/competitions/']")
    seen_urls: set[str] = set()

    for card in cards:
        link_el = card if card.name == "a" else card.select_one("a[href*='/competitions/']")
        if not link_el:
            continue
        href = link_el.get("href", "")
        if not href or not re.search(r"/competitions/\d+", href):
            continue
        url = href if href.startswith("http") else f"https://www.drivendata.org{href}"
        if url in seen_urls:
            continue

        parent_section = card.find_parent(id="completed-comps")
        if parent_section is not None:
            continue

        seen_urls.add(url)
        title_el = card.select_one("h3, h4, .title, .comp-title")
        title = title_el.get_text(" ", strip=True) if title_el else link_el.get_text(" ", strip=True)
        if not title:
            continue

        text_blob = card.get_text(" | ", strip=True)
        prize_match = re.search(r"(\$[\d,]+|\bKnowledge\b)", text_blob, re.IGNORECASE)
        prize = prize_match.group(1) if prize_match else "Knowledge"

        date_match = re.search(
            r"(\d+\s+(?:days?|months?|hours?)\s+(?:left|remaining)|[A-Z][a-z]{2,8}\.?\s+\d{1,2},\s+\d{4})",
            text_blob,
            re.IGNORECASE,
        )
        end_date = date_match.group(1) if date_match else None

        items.append(
            {
                "title": title,
                "url": url,
                "prize": prize,
                "end_date": end_date,
                "description": text_blob[:300],
            }
        )
    return items


def scrape() -> List[CompetitionRecord]:
    session = create_session()
    resp = safe_get(session, COMPETITIONS_URL)
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
            platform="DrivenData",
            source=SOURCE_NAME,
            url=str(item.get("url") or ""),
            prize=item.get("prize"),
            end_date=item.get("end_date"),
            description=desc,
            organizer="DrivenData",
        )
        if rec:
            records.append(rec)

    logger.info("DrivenData yielded %d active quant competitions", len(records))
    return records

