from __future__ import annotations

import csv
import json
import logging
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from scraper.dedupe import deduplicate_records
from scraper.history import annotate_with_history
from scraper.models import CompetitionRecord, SourceStatus
from scraper.normalize import is_active_competition
from scraper.sources import ALL_SCRAPERS

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
DASHBOARD_PUBLIC_DATA = ROOT_DIR / "apps" / "dashboard" / "public" / "data"

CSV_COLUMNS = [
    "id",
    "title",
    "platform",
    "source",
    "url",
    "prize",
    "prize_usd",
    "prize_currency",
    "start_date",
    "end_date",
    "days_remaining",
    "status",
    "category",
    "competition_type",
    "difficulty",
    "organizer",
    "evaluation_metric",
    "teams_count",
    "competitors_count",
    "entries_count",
    "conference",
    "conference_year",
    "paper_url",
    "first_seen_at",
    "is_new",
    "prize_delta_usd",
    "days_Shift",
    "tags",
    "description",
    "scraped_at",
]


def _save_records_cache(source_name: str, records: List[CompetitionRecord]) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path = CACHE_DIR / f"{source_name}.records.json"
        path.write_text(
            json.dumps([r.to_dict() for r in records], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:
        logger.debug("Failed to write records cache for %s: %s", source_name, exc)


def _load_records_cache(source_name: str) -> List[CompetitionRecord]:
    path = CACHE_DIR / f"{source_name}.records.json"
    if not path.exists():
        return []
    try:
        raw_list = json.loads(path.read_text(encoding="utf-8"))
        restored: List[CompetitionRecord] = []
        for item in raw_list:
            if not isinstance(item, dict):
                continue
            active, status, days_rem = is_active_competition(
                item.get("end_date"),
                raw_status=item.get("status", "active"),
            )
            if not active:
                continue
            item["status"] = status
            item["days_remaining"] = days_rem
            restored.append(CompetitionRecord(**item))
        return restored
    except Exception as exc:
        logger.debug("Failed to load records cache for %s: %s", source_name, exc)
        return []


def run_pipeline(selected_sources: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    """Run all (or selected) scrapers, deduplicate, and write JSON + CSV outputs."""
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sources_to_run = list(selected_sources) if selected_sources else list(ALL_SCRAPERS.keys())

    all_records: List[CompetitionRecord] = []
    statuses: List[SourceStatus] = []

    for name in sources_to_run:
        scraper_fn = ALL_SCRAPERS.get(name)
        if not scraper_fn:
            logger.warning("Unknown source '%s' skipped", name)
            continue

        t0 = time.perf_counter()
        try:
            records = scraper_fn()
            dt_ms = int((time.perf_counter() - t0) * 1000)

            if records:
                _save_records_cache(name, records)
                all_records.extend(records)
                statuses.append(
                    SourceStatus(
                        name=name,
                        status="ok",
                        count=len(records),
                        duration_ms=dt_ms,
                        updated_at=now_iso,
                    )
                )
            else:
                cached = _load_records_cache(name)
                if cached:
                    all_records.extend(cached)
                    statuses.append(
                        SourceStatus(
                            name=name,
                            status="cached",
                            count=len(cached),
                            duration_ms=dt_ms,
                            error="Live scrape returned 0 quant records; used cached snapshot",
                            updated_at=now_iso,
                        )
                    )
                else:
                    statuses.append(
                        SourceStatus(
                            name=name,
                            status="degraded",
                            count=0,
                            duration_ms=dt_ms,
                            error="0 quant records returned",
                            updated_at=now_iso,
                        )
                    )
        except Exception as exc:
            dt_ms = int((time.perf_counter() - t0) * 1000)
            logger.exception("Scraper '%s' raised an error", name)
            cached = _load_records_cache(name)
            if cached:
                all_records.extend(cached)
                statuses.append(
                    SourceStatus(
                        name=name,
                        status="cached",
                        count=len(cached),
                        duration_ms=dt_ms,
                        error=str(exc),
                        updated_at=now_iso,
                    )
                )
            else:
                statuses.append(
                    SourceStatus(
                        name=name,
                        status="error",
                        count=0,
                        duration_ms=dt_ms,
                        error=str(exc),
                        updated_at=now_iso,
                    )
                )

    deduped = deduplicate_records(all_records)
    history_meta = annotate_with_history(deduped)

    # Sort: live competitions & tournaments first, then by deadline urgency, then by prize_usd desc
    deduped.sort(
        key=lambda r: (
            0 if r.competition_type in ("competition", "tournament", "hackathon") else 1,
            0 if r.days_remaining is not None else 1,
            r.days_remaining if r.days_remaining is not None else 999999,
            -r.prize_usd,
            r.title.lower(),
        )
    )

    total_prize_usd = round(sum(r.prize_usd for r in deduped), 2)
    ending_soon_count = sum(1 for r in deduped if r.status == "ending_soon")
    platforms_summary: Dict[str, int] = {}
    categories_summary: Dict[str, int] = {}
    for r in deduped:
        platforms_summary[r.platform] = platforms_summary.get(r.platform, 0) + 1
        categories_summary[r.category] = categories_summary.get(r.category, 0) + 1

    payload: Dict[str, Any] = {
        "metadata": {
            "generated_at": now_iso,
            "total_active": len(deduped),
            "total_prize_usd": total_prize_usd,
            "ending_soon_count": ending_soon_count,
            "platforms_count": len(platforms_summary),
            "platforms": platforms_summary,
            "categories": categories_summary,
            "history": history_meta,
            "sources": [s.to_dict() for s in statuses],
        },
        "competitions": [r.to_dict() for r in deduped],
    }

    write_outputs(payload, deduped)
    return payload


def write_outputs(payload: Dict[str, Any], records: List[CompetitionRecord]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    json_path = DATA_DIR / "competitions.json"
    csv_path = DATA_DIR / "competitions.csv"

    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for rec in records:
            row = rec.to_dict()
            row["tags"] = "; ".join(rec.tags or [])
            writer.writerow({col: row.get(col, "") for col in CSV_COLUMNS})

    if DASHBOARD_PUBLIC_DATA.parent.exists():
        DASHBOARD_PUBLIC_DATA.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(json_path, DASHBOARD_PUBLIC_DATA / "competitions.json")
        shutil.copyfile(csv_path, DASHBOARD_PUBLIC_DATA / "competitions.csv")

    logger.info(
        "Wrote %d active quant competitions to %s and %s",
        len(records),
        json_path,
        csv_path,
    )

