"""Historical competition tracking, first-seen registry, and daily diff annotations."""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from scraper.models import CompetitionRecord
from scraper.normalize import canonicalize_url

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HISTORY_DIR = DATA_DIR / "history"
FIRST_SEEN_PATH = HISTORY_DIR / "first_seen.json"
NEW_BADGE_WINDOW_DAYS = 3


def load_first_seen() -> Dict[str, Dict[str, Any]]:
    if not FIRST_SEEN_PATH.exists():
        return {}
    try:
        payload = json.loads(FIRST_SEEN_PATH.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception as exc:
        logger.warning("Failed to load first_seen.json: %s", exc)
    return {}


def save_first_seen(registry: Dict[str, Dict[str, Any]]) -> None:
    try:
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        FIRST_SEEN_PATH.write_text(
            json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    except Exception as exc:
        logger.warning("Failed to save first_seen.json: %s", exc)


def annotate_with_history(
    records: List[CompetitionRecord],
    today: Optional[date] = None,
) -> Dict[str, Any]:
    """Enrich records with `first_seen_at`, `is_new`, `prize_delta_usd`, `days_Shift`."""
    ref_today = today or datetime.now(timezone.utc).date()
    today_iso = ref_today.isoformat()
    registry = load_first_seen()
    is_bootstrap = len(registry) == 0

    new_count = 0
    prize_changes = 0
    deadline_changes = 0

    for rec in records:
        key = canonicalize_url(rec.url) or rec.id
        entry = registry.get(key)

        if entry is None:
            first_seen_date = today_iso
            rec.first_seen_at = first_seen_date
            rec.is_new = False if is_bootstrap else True
            if rec.is_new:
                new_count += 1
            registry[key] = {
                "id": rec.id,
                "title": rec.title,
                "platform": rec.platform,
                "first_seen_at": first_seen_date,
                "initial_prize_usd": rec.prize_usd,
                "last_prize_usd": rec.prize_usd,
                "initial_end_date": rec.end_date,
                "last_end_date": rec.end_date,
                "last_seen_at": today_iso,
            }
        else:
            first_seen_date = str(entry.get("first_seen_at") or today_iso)
            rec.first_seen_at = first_seen_date

            try:
                seen_dt = date.fromisoformat(first_seen_date[:10])
                rec.is_new = (not is_bootstrap) and (0 <= (ref_today - seen_dt).days <= NEW_BADGE_WINDOW_DAYS)
                if rec.is_new:
                    new_count += 1
            except ValueError:
                rec.is_new = False

            prev_prize = float(entry.get("last_prize_usd") or 0.0)
            if prev_prize > 0 and rec.prize_usd > 0 and abs(rec.prize_usd - prev_prize) >= 1.0:
                rec.prize_delta_usd = round(rec.prize_usd - prev_prize, 2)
                prize_changes += 1

            prev_end = entry.get("last_end_date")
            if prev_end and rec.end_date and prev_end != rec.end_date:
                try:
                    d_old = date.fromisoformat(str(prev_end)[:10])
                    d_new = date.fromisoformat(str(rec.end_date)[:10])
                    rec.days_Shift = (d_new - d_old).days
                    if rec.days_Shift != 0:
                        deadline_changes += 1
                except ValueError:
                    pass

            entry["last_prize_usd"] = rec.prize_usd
            entry["last_end_date"] = rec.end_date
            entry["last_seen_at"] = today_iso
            registry[key] = entry

    save_first_seen(registry)

    try:
        snapshot_dir = HISTORY_DIR / "snapshots"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path = snapshot_dir / f"{today_iso}.json"
        snapshot_summary = {
            "date": today_iso,
            "total_active": len(records),
            "total_prize_usd": round(sum(r.prize_usd for r in records), 2),
            "new_count": new_count,
            "prize_changes": prize_changes,
            "deadline_changes": deadline_changes,
        }
        snapshot_path.write_text(json.dumps(snapshot_summary, indent=2), encoding="utf-8")
    except Exception as exc:
        logger.debug("Snapshot write skipped: %s", exc)

    return {
        "new_competitions": new_count,
        "prize_changes": prize_changes,
        "deadline_changes": deadline_changes,
        "tracked_total": len(registry),
    }

