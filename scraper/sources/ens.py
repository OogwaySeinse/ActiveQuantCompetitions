"""ENS Challenge Data (Collège de France / ENS Paris) quantitative finance & insurance scraper."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from scraper.http import create_session, load_source_cache, safe_get, save_source_cache
from scraper.models import CompetitionRecord
from scraper.normalize import build_record, is_quant_competition

logger = logging.getLogger(__name__)

SOURCE_NAME = "ens"
SEARCH_URL = "https://challengedata.ens.fr/challenges/challenges_search"
BASE_URL = "https://challengedata.ens.fr"


def _parse_html(html: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    items: List[Dict[str, Any]] = []

    for container in soup.select("div.search_result_container"):
        h4 = container.select_one("h4")
        if not h4:
            continue
        em = h4.select_one("em")
        org_text = (em.get_text(" ", strip=True) if em else "").replace("\xa0", " ")
        if em:
            em.extract()
        title = h4.get_text(" ", strip=True).replace("\xa0", " ")

        organizer = "ENS Challenge Data"
        year = None
        m = re.search(r"(?:by|par)\s+(.+?)\s*\((\d{4})\)", org_text, re.IGNORECASE)
        if m:
            organizer = m.group(1).strip()
            year = int(m.group(2))
        elif org_text:
            organizer = re.sub(r"^(?:by|par)\s+", "", org_text, flags=re.IGNORECASE).strip()

        link_el = container.select_one("a[href*='/challenges/']")
        if not link_el:
            parent_a = container.find_parent("a", href=True)
            href = parent_a["href"] if parent_a else ""
        else:
            href = link_el.get("href") or ""

        if not href:
            continue
        url = href if href.startswith("http") else f"{BASE_URL}{href}"

        tags: List[str] = []
        for tag_div in container.select("div[title]"):
            t = (tag_div.get("title") or tag_div.get_text(" ", strip=True) or "").strip()
            if t and t.lower() not in {"competitive challenge"}:
                tags.append(t)

        desc_el = container.select_one("p")
        desc = desc_el.get_text(" ", strip=True) if desc_el else ""

        items.append(
            {
                "title": title,
                "organizer": organizer,
                "year": year,
                "url": url,
                "tags": tags,
                "description": desc,
            }
        )

    return items


def _items_to_records(items: List[Dict[str, Any]]) -> List[CompetitionRecord]:
    current_year = datetime.now(timezone.utc).year
    records: List[CompetitionRecord] = []

    for item in items:
        title = str(item.get("title") or "").strip()
        organizer = str(item.get("organizer") or "ENS Challenge Data").strip()
        year = item.get("year")
        url = str(item.get("url") or "").strip()
        tags = list(item.get("tags") or [])
        desc = str(item.get("description") or "").strip()

        if not is_quant_competition(
            title,
            description=desc,
            tags=tags,
            source_name=SOURCE_NAME,
            organizer=organizer,
        ):
            continue

        is_current_season = isinstance(year, int) and year >= current_year
        comp_type = "competition" if is_current_season else "benchmark"
        end_date = f"{year}-12-31" if is_current_season else None
        start_date = f"{year}-01-15" if isinstance(year, int) else None
        prize = "Academic & Sponsor Awards" if is_current_season else "Knowledge"

        full_title = f"{title} ({organizer} {year})" if year and organizer not in title else title
        full_desc = (
            desc
            or f"Quantitative data science challenge hosted by {organizer} on ENS Challenge Data ({year or 'Ongoing'})."
        )

        rec = build_record(
            title=full_title,
            platform="ENS Challenge Data",
            source=SOURCE_NAME,
            url=url,
            prize=prize,
            start_date=start_date,
            end_date=end_date,
            raw_status="active",
            tags=tags + ["ens-paris", organizer.lower().replace(" ", "-")],
            description=full_desc,
            organizer=organizer,
            competition_type=comp_type,
        )
        if rec:
            records.append(rec)

    return records


def scrape() -> List[CompetitionRecord]:
    session = create_session()
    resp = safe_get(session, SEARCH_URL)
    items: List[Dict[str, Any]] = []

    if resp is not None and resp.text:
        try:
            items = _parse_html(resp.text)
            if items:
                save_source_cache(SOURCE_NAME, items)
        except Exception as exc:
            logger.warning("ENS Challenge Data HTML parse failed: %s", exc)

    if not items:
        cached = load_source_cache(SOURCE_NAME)
        if isinstance(cached, list):
            items = cached

    records = _items_to_records(items)
    logger.info("ENS Challenge Data yielded %d quant challenges", len(records))
    return records
