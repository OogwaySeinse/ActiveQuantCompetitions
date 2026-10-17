from __future__ import annotations

from typing import Dict, List

from rapidfuzz import fuzz

from scraper.models import CompetitionRecord
from scraper.normalize import canonicalize_url, slugify_title

SOURCE_PRIORITY: Dict[str, int] = {
    "numerai": 100,
    "crunchdao": 98,
    "ens": 96,
    "janestreet": 95,
    "kaggle": 94,
    "drivendata": 90,
    "zindi": 88,
    "aicrowd": 86,
    "codalab": 84,
    "tianchi": 82,
    "devpost": 78,
    "quantcontests": 76,
    "mlcontests": 72,
}


def _completeness_score(rec: CompetitionRecord) -> float:
    score = float(SOURCE_PRIORITY.get(rec.source, 50))
    if rec.prize_usd > 0:
        score += 15.0
    if rec.end_date:
        score += 10.0
    if rec.description:
        score += min(len(rec.description) / 50.0, 8.0)
    if rec.tags:
        score += min(len(rec.tags) * 1.5, 6.0)
    if rec.teams_count or rec.competitors_count:
        score += 5.0
    if rec.evaluation_metric:
        score += 3.0
    return score


def merge_two(primary: CompetitionRecord, secondary: CompetitionRecord) -> CompetitionRecord:
    """Merge metadata from secondary into primary without overwriting richer fields."""
    if _completeness_score(secondary) > _completeness_score(primary):
        primary, secondary = secondary, primary

    if primary.prize_usd <= 0 and secondary.prize_usd > 0:
        primary.prize = secondary.prize
        primary.prize_usd = secondary.prize_usd
        primary.prize_currency = secondary.prize_currency
        primary.prize_raw = secondary.prize_raw

    if not primary.start_date and secondary.start_date:
        primary.start_date = secondary.start_date
    if not primary.end_date and secondary.end_date:
        primary.end_date = secondary.end_date
        primary.days_remaining = secondary.days_remaining
        primary.status = secondary.status

    if len(secondary.description or "") > len(primary.description or ""):
        primary.description = secondary.description

    if not primary.evaluation_metric and secondary.evaluation_metric:
        primary.evaluation_metric = secondary.evaluation_metric

    if not primary.teams_count and secondary.teams_count:
        primary.teams_count = secondary.teams_count
    if not primary.competitors_count and secondary.competitors_count:
        primary.competitors_count = secondary.competitors_count
    if not primary.entries_count and secondary.entries_count:
        primary.entries_count = secondary.entries_count

    if not primary.conference and secondary.conference:
        primary.conference = secondary.conference
        primary.conference_year = secondary.conference_year
    if not primary.paper_url and secondary.paper_url:
        primary.paper_url = secondary.paper_url

    merged_tags = sorted(set(primary.tags or []) | set(secondary.tags or []))
    primary.tags = merged_tags[:10]
    return primary


def deduplicate_records(records: List[CompetitionRecord], fuzzy_threshold: float = 91.0) -> List[CompetitionRecord]:
    """Deduplicate by canonical URL first, then by (platform, fuzzy title similarity)."""
    by_url: Dict[str, CompetitionRecord] = {}
    no_url: List[CompetitionRecord] = []

    for rec in records:
        canon = canonicalize_url(rec.url)
        if not canon:
            no_url.append(rec)
            continue
        if canon in by_url:
            by_url[canon] = merge_two(by_url[canon], rec)
        else:
            by_url[canon] = rec

    stage_one = list(by_url.values()) + no_url
    deduped: List[CompetitionRecord] = []

    for candidate in stage_one:
        cand_slug = slugify_title(candidate.title)
        matched_idx = None

        for idx, existing in enumerate(deduped):
            same_platform = existing.platform.lower() == candidate.platform.lower()
            exist_slug = slugify_title(existing.title)
            if not cand_slug or not exist_slug:
                continue

            if same_platform and cand_slug == exist_slug:
                matched_idx = idx
                break

            ratio = fuzz.token_set_ratio(cand_slug, exist_slug)
            if same_platform and ratio >= fuzzy_threshold:
                matched_idx = idx
                break
            if not same_platform and ratio >= 96.5 and existing.end_date and existing.end_date == candidate.end_date:
                matched_idx = idx
                break

        if matched_idx is not None:
            deduped[matched_idx] = merge_two(deduped[matched_idx], candidate)
        else:
            deduped.append(candidate)

    return deduped

