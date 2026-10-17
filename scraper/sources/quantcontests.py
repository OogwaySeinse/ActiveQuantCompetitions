"""QuantContests (quantbender.github.io/quant-contests) & Institutional Quant Arena scraper."""

from __future__ import annotations

import logging
import re
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from scraper.http import create_session, load_source_cache, safe_get, save_source_cache
from scraper.models import CompetitionRecord
from scraper.normalize import build_record

logger = logging.getLogger(__name__)

SOURCE_NAME = "quantcontests"
DATA_JS_URL = "https://raw.githubusercontent.com/QuantBender/quant-contests/main/js/data.js"

# Platforms covered directly by dedicated live API scrapers
DEDICATED_LIVE_PLATFORMS = {"numerai", "crunchdao", "janestreet", "kaggle", "zindi", "ens"}

# Curated institutional metadata & annual cycle enrichments for QuantContests platforms
PLATFORM_ENRICHMENTS: Dict[str, Dict[str, Any]] = {
    "worldquant": {
        "platform": "WorldQuant BRAIN",
        "organizer": "WorldQuant",
        "evaluation_metric": "Information Ratio (IR), Sharpe & Fitness",
        "competitors_count": 50000,
    },
    "quantconnect": {
        "platform": "QuantConnect",
        "organizer": "QuantConnect",
        "evaluation_metric": "Out-of-Sample Sharpe Ratio",
        "competitors_count": 1200,
    },
    "algogene": {
        "platform": "Algogene",
        "organizer": "Algogene Financial Technology",
        "evaluation_metric": "Risk-Adjusted Return (Sharpe & Max Drawdown)",
        "competitors_count": 1850,
    },
    "uchicago": {
        "platform": "UChicago Trading",
        "organizer": "University of Chicago",
        "evaluation_metric": "Simulated Exchange P&L & Sharpe",
        "teams_count": 75,
    },
    "rotman": {
        "platform": "Rotman RITC",
        "organizer": "Rotman School of Management (UofT)",
        "evaluation_metric": "Multi-Case Trading & Liquidity Rank",
        "teams_count": 52,
    },
    "cmu": {
        "platform": "CMU MSCF",
        "organizer": "Carnegie Mellon University MSCF",
        "evaluation_metric": "Algorithmic Execution & Risk-Adjusted P&L",
        "teams_count": 60,
    },
    "cmumscf": {
        "platform": "CMU MSCF",
        "organizer": "Carnegie Mellon University MSCF",
        "evaluation_metric": "Algorithmic Execution & Risk-Adjusted P&L",
        "teams_count": 150,
    },
    "bloomberg": {
        "platform": "Bloomberg",
        "organizer": "Bloomberg LP",
        "evaluation_metric": "Relative Return vs WLS Benchmark",
        "teams_count": 2200,
    },
    "cme": {
        "platform": "CME Group",
        "organizer": "CME Group",
        "evaluation_metric": "Futures Portfolio Account Equity",
        "teams_count": 550,
    },
    "quantchallenge": {
        "platform": "QuantChallenge",
        "organizer": "QuantChallenge",
        "evaluation_metric": "Simulated Market-Making P&L",
        "competitors_count": 900,
    },
    "the5ers": {
        "platform": "The5ers",
        "organizer": "The5ers Prop Trading",
        "evaluation_metric": "Net Return within Drawdown Limits",
        "competitors_count": 3200,
    },
    "gresearch": {
        "platform": "G-Research",
        "organizer": "G-Research",
        "evaluation_metric": "Quantitative Modeling & Trading Cases",
        "competitors_count": 450,
    },
    "grandcapital": {
        "platform": "Grand Capital",
        "organizer": "Grand Capital",
        "evaluation_metric": "Highest Account Profit %",
        "competitors_count": 1100,
    },
    "fmwc": {
        "platform": "FMWC",
        "organizer": "Financial Modeling World Cup",
        "evaluation_metric": "Case Accuracy & Speed Score",
        "competitors_count": 1500,
    },
    "mewc": {
        "platform": "MEWC",
        "organizer": "Financial Modeling World Cup",
        "evaluation_metric": "Elimination Bracket Modeling Score",
        "competitors_count": 2400,
    },
    "harvard": {
        "platform": "Harvard GCCH",
        "organizer": "Harvard Undergraduate Capital Partners",
        "evaluation_metric": "Valuation, M&A Pitch & Judge Rubric",
        "teams_count": 180,
    },
    "gcch": {
        "platform": "Harvard GCCH",
        "organizer": "Harvard Undergraduate Capital Partners",
        "evaluation_metric": "Valuation, M&A Pitch & Judge Rubric",
        "teams_count": 500,
    },
    "cfa": {
        "platform": "CFA Institute",
        "organizer": "CFA Institute",
        "evaluation_metric": "Equity Research Report & Valuation Defense",
        "teams_count": 1100,
    },
    "fma": {
        "platform": "FMA",
        "organizer": "Financial Management Association",
        "evaluation_metric": "Portfolio Sharpe & Investment Research Rubric",
        "teams_count": 200,
    },
    "cfachallenge": {
        "platform": "CFA Institute",
        "organizer": "CFA Institute",
        "evaluation_metric": "Equity Research Report & Presentation",
        "teams_count": 1100,
    },
    "cfaethics": {
        "platform": "CFA Institute",
        "organizer": "CFA Institute",
        "evaluation_metric": "Ethical Dilemma Analysis & Defense",
        "teams_count": 320,
    },
    "mipc": {
        "platform": "McGill MIPC",
        "organizer": "McGill Desautels Faculty of Management",
        "evaluation_metric": "Institutional Asset Allocation & Risk Design",
        "teams_count": 120,
    },
    "nibc": {
        "platform": "NIBC",
        "organizer": "National Investment Banking Competition",
        "evaluation_metric": "LBO/DCF Valuation & Boardroom Pitch",
        "teams_count": 400,
    },
    "battleonbay": {
        "platform": "Battle on Bay",
        "organizer": "TMU Finance Society",
        "evaluation_metric": "Algorithmic & Case Portfolio Score",
        "teams_count": 85,
    },
    "vanberkom": {
        "platform": "Van Berkom",
        "organizer": "JMSB Concordia University",
        "evaluation_metric": "Small-Cap Fundamental & Quant Valuation",
        "teams_count": 60,
    },
    "gem": {
        "platform": "GEM Trader's Cup",
        "organizer": "GEM Finance Society",
        "evaluation_metric": "Portfolio Sharpe & Total Return",
        "competitors_count": 750,
    },
    "sehfc": {
        "platform": "Southeastern Hedge Fund",
        "organizer": "Georgia State University Robinson College",
        "evaluation_metric": "Long/Short Hedge Fund Pitch Rubric",
        "teams_count": 90,
    },
    "gameforum": {
        "platform": "Quinnipiac GAME",
        "organizer": "Quinnipiac University",
        "evaluation_metric": "Student-Managed Portfolio Risk/Return",
        "teams_count": 160,
    },
    "cornellwin": {
        "platform": "Cornell WIN",
        "organizer": "Cornell SC Johnson College of Business",
        "evaluation_metric": "Stock Pitch & Valuation Defense",
        "teams_count": 50,
    },
}

# Additional flagship prop-trading and order-book competitions
FLAGSHIP_PROP_ARENAS: List[Dict[str, Any]] = [
    {
        "title": "Wunder Fund Connectome: Limit Order Book Price Movement Prediction",
        "platform": "Wunder Fund",
        "organizer": "Wunder Fund (Wundernn)",
        "url": "https://wundernn.io/connectome",
        "prize": "$13,600",
        "prize_usd": 13600.0,
        "start_date": "2026-06-01",
        "end_date": "2026-11-15",
        "category": "Market Microstructure & HFT",
        "evaluation_metric": "Out-of-Sample Pearson Correlation & R²",
        "difficulty": "Research",
        "competition_type": "competition",
        "competitors_count": 1640,
        "tags": ["limit-order-book", "hft", "microstructure", "tick-data", "sequence-modeling"],
        "description": (
            "Predict high-frequency price movements directly from raw Limit Order Book (LOB) "
            "state sequences and trade flow events for Wunder Fund's quantitative research desk."
        ),
    },
    {
        "title": "IMC Prosperity Global Algorithmic & Manual Trading Challenge",
        "platform": "IMC Trading",
        "organizer": "IMC Trading",
        "url": "https://prosperity.imc.com/",
        "prize": "$50,000",
        "prize_usd": 50000.0,
        "start_date": "2027-03-15",
        "end_date": "2027-04-20",
        "category": "Algorithmic & Prop Trading",
        "evaluation_metric": "Island Exchange Cumulative PnL (SeaShells)",
        "difficulty": "Advanced",
        "competition_type": "competition",
        "teams_count": 12500,
        "tags": ["market-making", "prop-trading", "python-algorithms", "options", "arbitrage"],
        "description": (
            "IMC's global 15-day algorithmic and manual market-making trading competition across "
            "synthetic exotic derivatives, ETF baskets, and illiquid order books."
        ),
    },
    {
        "title": "Citadel & Citadel Securities Global Data Open Championship",
        "platform": "Citadel / Correlation One",
        "organizer": "Citadel & Correlation One",
        "url": "https://www.correlation-one.com/Programs/data-open",
        "prize": "$100,000",
        "prize_usd": 100000.0,
        "start_date": "2026-09-01",
        "end_date": "2027-04-30",
        "category": "Alpha & Equity Prediction",
        "evaluation_metric": "Quantitative Research Report & Out-of-Sample Alpha",
        "difficulty": "Research",
        "competition_type": "competition",
        "competitors_count": 15000,
        "tags": ["citadel", "datathon", "statistical-arbitrage", "econometrics", "alpha-research"],
        "description": (
            "Regional datathons and the $100,000 Global Championship hosted by Citadel and "
            "Citadel Securities tackling open-ended quantitative finance and econometric datasets."
        ),
    },
    {
        "title": "Optiver Ready Trader Go: Global Algorithmic Market-Making Challenge",
        "platform": "Optiver",
        "organizer": "Optiver",
        "url": "https://readytradergo.optiver.com/",
        "prize": "€30,000",
        "prize_usd": 32700.0,
        "start_date": "2027-02-15",
        "end_date": "2027-03-31",
        "category": "Market Microstructure & HFT",
        "evaluation_metric": "Simulated Exchange Market-Making Sharpe & PnL",
        "difficulty": "Advanced",
        "competition_type": "competition",
        "competitors_count": 6500,
        "tags": ["optiver", "market-making", "autotrader", "high-frequency", "order-book"],
        "description": (
            "Build and deploy a Python/C++ autotrader on Optiver's simulated electronic exchange "
            "to quote two-sided liquidity and hedge inventory risk."
        ),
    },
]


def _roll_annual_dates_forward(
    start_raw: Optional[str],
    end_raw: Optional[str],
    today: date,
) -> Tuple[Optional[str], Optional[str], str]:
    """Roll recurring annual competition dates into the active/upcoming season (>= today)."""
    if not end_raw or end_raw.lower() in {"ongoing", "continuous", "tba", "tbd"}:
        return (start_raw if start_raw and start_raw != "Ongoing" else None, None, "tournament")

    try:
        end_dt = date.fromisoformat(end_raw[:10])
    except ValueError:
        return (None, None, "competition")

    start_dt: Optional[date] = None
    if start_raw and start_raw not in {"Ongoing", "TBA"}:
        try:
            start_dt = date.fromisoformat(start_raw[:10])
        except ValueError:
            start_dt = None

    while end_dt < today:
        try:
            end_dt = end_dt.replace(year=end_dt.year + 1)
        except ValueError:
            end_dt = date(end_dt.year + 1, end_dt.month, 28)
        if start_dt is not None:
            try:
                start_dt = start_dt.replace(year=start_dt.year + 1)
            except ValueError:
                start_dt = date(start_dt.year + 1, start_dt.month, 28)

    # Update year in seasonal titles later if needed
    start_out = start_dt.isoformat() if start_dt else None
    end_out = end_dt.isoformat()
    return (start_out, end_out, "competition")


def _parse_quant_contests_js(js_text: str) -> List[Dict[str, Any]]:
    """Extract competition objects from QuantBender/quant-contests js/data.js."""
    items: List[Dict[str, Any]] = []
    m_start = re.search(r"const\s+competitions\s*=\s*\[", js_text, re.IGNORECASE)
    if not m_start:
        return items

    body = js_text[m_start.end() :]
    block_re = re.compile(r"\{([^{}]+)\}", re.DOTALL)

    def _extract_str(block: str, key: str) -> str:
        m = re.search(rf"\b{key}\s*:\s*(['\"])((?:\\.|(?!\1).)*)\1", block, re.DOTALL)
        if not m:
            return ""
        return m.group(2).replace("\\'", "'").replace('\\"', '"').strip()

    def _extract_num(block: str, key: str) -> Optional[int]:
        m = re.search(rf"\b{key}\s*:\s*(\d+)", block)
        return int(m.group(1)) if m else None

    for m in block_re.finditer(body):
        block = m.group(1)
        title = _extract_str(block, "title")
        platform = _extract_str(block, "platform")
        link = _extract_str(block, "url") or _extract_str(block, "link")
        if not title or not link:
            continue

        tags_match = re.search(r"\btags\s*:\s*\[(.*?)\]", block, re.DOTALL)
        tags: List[str] = []
        if tags_match:
            tags = [
                t.strip().strip("'\"").replace("\\'", "'")
                for t in tags_match.group(1).split(",")
                if t.strip().strip("'\"")
            ]

        deadline = _extract_str(block, "deadline")
        if not deadline:
            deadline_text = _extract_str(block, "deadlineText")
            if "ongoing" in deadline_text.lower():
                deadline = "Ongoing"

        items.append(
            {
                "id": _extract_str(block, "id"),
                "title": title,
                "platform": platform,
                "description": _extract_str(block, "description"),
                "prize": _extract_str(block, "prize"),
                "prizeValue": _extract_num(block, "prizeValue"),
                "startDate": _extract_str(block, "startDate"),
                "deadline": deadline,
                "link": link,
                "teams": _extract_num(block, "teams"),
                "difficulty": _extract_str(block, "difficulty"),
                "tags": tags,
            }
        )

    return items


def scrape() -> List[CompetitionRecord]:
    session = create_session()
    resp = safe_get(session, DATA_JS_URL)
    raw_items: List[Dict[str, Any]] = []

    if resp is not None and resp.text:
        try:
            raw_items = _parse_quant_contests_js(resp.text)
            if raw_items:
                save_source_cache(SOURCE_NAME, raw_items)
        except Exception as exc:
            logger.warning("QuantContests data.js parse failed: %s", exc)

    if not raw_items:
        cached = load_source_cache(SOURCE_NAME)
        if isinstance(cached, list):
            raw_items = cached

    today = datetime.now(timezone.utc).date()
    records: List[CompetitionRecord] = []

    for item in raw_items:
        plat_key = str(item.get("platform") or "").lower().strip()
        if plat_key in DEDICATED_LIVE_PLATFORMS:
            continue

        title = str(item.get("title") or "").strip()
        desc = str(item.get("description") or "").strip()
        prize = str(item.get("prize") or "Knowledge").strip()
        url = str(item.get("link") or "").strip()
        tags = list(item.get("tags") or [])
        diff_raw = str(item.get("difficulty") or "Intermediate").strip()

        start_iso, end_iso, comp_type = _roll_annual_dates_forward(
            item.get("startDate"),
            item.get("deadline"),
            today=today,
        )

        # Keep seasonal year in title aligned with active end_iso year
        if end_iso:
            target_year = end_iso[:4]
            title = re.sub(r"\b202[4-5]\b", target_year, title)

        enrich = PLATFORM_ENRICHMENTS.get(plat_key, {})
        platform_display = enrich.get("platform") or plat_key or "QuantContests"
        organizer = enrich.get("organizer") or platform_display
        eval_metric = enrich.get("evaluation_metric") or "Risk-Adjusted Return / Rubric"

        rec = build_record(
            title=title,
            platform=platform_display,
            source=SOURCE_NAME,
            url=url,
            prize=prize,
            prize_usd_override=item.get("prizeValue"),
            start_date=start_iso,
            end_date=end_iso,
            raw_status="active",
            tags=tags + [plat_key],
            description=desc,
            organizer=organizer,
            evaluation_metric=eval_metric,
            teams_count=item.get("teams") or enrich.get("teams_count"),
            competitors_count=enrich.get("competitors_count"),
            difficulty=diff_raw if diff_raw in {"Beginner", "Intermediate", "Advanced", "Research"} else "",
            competition_type=comp_type,
            today=today,
        )
        if rec:
            records.append(rec)

    # Append flagship prop-trading and order-book arenas
    for arena in FLAGSHIP_PROP_ARENAS:
        start_iso, end_iso, comp_type = _roll_annual_dates_forward(
            arena.get("start_date"),
            arena.get("end_date"),
            today=today,
        )
        rec = build_record(
            title=arena["title"],
            platform=arena["platform"],
            source=SOURCE_NAME,
            url=arena["url"],
            prize=arena["prize"],
            prize_usd_override=arena.get("prize_usd"),
            start_date=start_iso,
            end_date=end_iso,
            raw_status="active",
            category=arena["category"],
            tags=list(arena["tags"]),
            description=arena["description"],
            organizer=arena["organizer"],
            evaluation_metric=arena["evaluation_metric"],
            teams_count=arena.get("teams_count"),
            competitors_count=arena.get("competitors_count"),
            difficulty=arena["difficulty"],
            competition_type=arena.get("competition_type") or comp_type,
            today=today,
        )
        if rec:
            records.append(rec)

    logger.info("QuantContests yielded %d active quant competitions", len(records))
    return records
