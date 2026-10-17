from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CompetitionRecord:
    """Canonical representation of an active quant / financial ML competition."""

    id: str
    title: str
    platform: str
    source: str
    url: str
    prize: str = "Knowledge"
    prize_usd: float = 0.0
    prize_currency: str = "USD"
    prize_raw: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    days_remaining: Optional[int] = None
    status: str = "active"
    category: str = "Alpha & Equity Prediction"
    tags: List[str] = field(default_factory=list)
    description: str = ""
    organizer: str = ""
    evaluation_metric: str = ""
    teams_count: Optional[int] = None
    competitors_count: Optional[int] = None
    entries_count: Optional[int] = None
    difficulty: str = "Intermediate"
    competition_type: str = "competition"
    conference: Optional[str] = None
    conference_year: Optional[int] = None
    paper_url: Optional[str] = None
    first_seen_at: Optional[str] = None
    is_new: bool = False
    prize_delta_usd: float = 0.0
    days_Shift: int = 0
    scraped_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SourceStatus:
    """Status telemetry for a single scraper source."""

    name: str
    status: str  # "ok", "cached", "degraded", "error"
    count: int = 0
    duration_ms: int = 0
    error: Optional[str] = None
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

