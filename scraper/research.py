"""Academic conference, institutional quant lab, and paper linkage detection."""

from __future__ import annotations

import re
from typing import Iterable, List, Optional, Tuple

# Ordered list of (Canonical Sponsor/Conference Label, Regex Pattern)
CONFERENCE_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    ("ICAIF", re.compile(r"\bICAIF\b", re.IGNORECASE)),
    ("ADIA Lab", re.compile(r"\bADIA\s+Lab\b", re.IGNORECASE)),
    ("QRT Research", re.compile(r"\b(?:QRT|Qube\s+Research)\b", re.IGNORECASE)),
    ("CFM Research", re.compile(r"\b(?:CFM|Capital\s+Fund\s+Management)\b", re.IGNORECASE)),
    ("G-Research", re.compile(r"\bG[\-\s]?Research\b", re.IGNORECASE)),
    ("Jane Street", re.compile(r"\bJane\s+Street\b", re.IGNORECASE)),
    ("WorldQuant", re.compile(r"\bWorldQuant\b", re.IGNORECASE)),
    ("Wunder Fund", re.compile(r"\b(?:Wunder\s+Fund|Wundernn|Connectome)\b", re.IGNORECASE)),
    ("IMC Trading", re.compile(r"\bIMC\s+(?:Prosperity|Trading)\b", re.IGNORECASE)),
    ("Citadel Data Open", re.compile(r"\b(?:Citadel|Data\s+Open|Correlation\s+One)\b", re.IGNORECASE)),
    ("Optiver", re.compile(r"\bOptiver\b", re.IGNORECASE)),
    ("CFA Institute", re.compile(r"\bCFA\s+Institute\b", re.IGNORECASE)),
    ("AMF Regulator", re.compile(r"\bAutorit[eé]\s+des\s+March[eé]s\s+Financiers\b", re.IGNORECASE)),
    ("Institut Louis Bachelier", re.compile(r"\bLouis\s+Bachelier\b", re.IGNORECASE)),
    ("NeurIPS", re.compile(r"\b(?:NeurIPS|NIPS)\b", re.IGNORECASE)),
    ("ICML", re.compile(r"\bICML\b", re.IGNORECASE)),
    ("ICLR", re.compile(r"\bICLR\b", re.IGNORECASE)),
    ("KDD", re.compile(r"\b(?:SIGKDD|KDD(?:\s*Cup|\s*20\d{2})?)\b", re.IGNORECASE)),
    ("AAAI", re.compile(r"\bAAAI\b", re.IGNORECASE)),
    ("IJCAI", re.compile(r"\bIJCAI\b", re.IGNORECASE)),
    ("WSDM", re.compile(r"\bWSDM\b", re.IGNORECASE)),
    ("WWW", re.compile(r"\b(?:TheWebConf|WWW\s*20\d{2})\b", re.IGNORECASE)),
    ("ECML-PKDD", re.compile(r"\b(?:ECML[\-\s]?PKDD|ECML)\b", re.IGNORECASE)),
    ("IEEE BigData", re.compile(r"\bIEEE\s*Big\s*Data\b", re.IGNORECASE)),
]

ARXIV_URL_RE = re.compile(
    r"(https?://arxiv\.org/(?:abs|pdf)/\d{4}\.\d{4,5}(?:v\d+)?)",
    re.IGNORECASE,
)
ARXIV_ID_RE = re.compile(r"\barxiv\s*:\s*(\d{4}\.\d{4,5}(?:v\d+)?)\b", re.IGNORECASE)
DOI_URL_RE = re.compile(
    r"(https?://(?:dx\.)?doi\.org/10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)",
    re.IGNORECASE,
)
OPENREVIEW_URL_RE = re.compile(
    r"(https?://openreview\.net/forum\?id=[A-Za-z0-9_\-]+)",
    re.IGNORECASE,
)
SSRN_URL_RE = re.compile(
    r"(https?://(?:papers\.)?ssrn\.com/sol3/papers\.cfm\?abstract_id=\d+)",
    re.IGNORECASE,
)
YEAR_RE = re.compile(r"\b(202[0-9])\b")


def detect_conference(
    title: str,
    description: str,
    tags: Iterable[str],
    organizer: str = "",
    platform: str = "",
) -> Tuple[Optional[str], Optional[int]]:
    """Return (conference_or_sponsor_name, year) if text matches a known academic or quant research track."""
    combined = " ".join([title or "", description or "", organizer or "", platform or "", " ".join(tags or [])])
    if not combined.strip():
        return (None, None)

    for conf_name, pattern in CONFERENCE_PATTERNS:
        match = pattern.search(combined)
        if match:
            window_start = max(0, match.start() - 25)
            window_end = min(len(combined), match.end() + 35)
            snippet = combined[window_start:window_end]
            yr_match = YEAR_RE.search(snippet) or YEAR_RE.search(title or "")
            year = int(yr_match.group(1)) if yr_match else None
            return (conf_name, year)

    return (None, None)


def extract_paper_url(description: str) -> Optional[str]:
    """Extract arXiv, SSRN, OpenReview, or DOI URL from competition text if present."""
    if not description:
        return None

    for regex in (ARXIV_URL_RE, SSRN_URL_RE, OPENREVIEW_URL_RE, DOI_URL_RE):
        m = regex.search(description)
        if m:
            return m.group(1)

    m_id = ARXIV_ID_RE.search(description)
    if m_id:
        return f"https://arxiv.org/abs/{m_id.group(1)}"

    return None


def enrich_research_fields(
    title: str,
    description: str,
    tags: Iterable[str],
    organizer: str = "",
    platform: str = "",
) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """Return (conference, conference_year, paper_url)."""
    conf, year = detect_conference(title, description, tags, organizer=organizer, platform=platform)
    paper_url = extract_paper_url(description)
    return (conf, year, paper_url)

