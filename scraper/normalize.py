from __future__ import annotations

import hashlib
import re
from datetime import date, datetime, timezone
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from dateutil import parser as date_parser

from scraper.fx import get_fx_rates
from scraper.models import CompetitionRecord
from scraper.research import enrich_research_fields

TRACKING_QUERY_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "ref",
    "source",
    "fbclid",
    "gclid",
}

PLATFORM_ALIASES: Dict[str, str] = {
    "numerai": "Numerai",
    "numer.ai": "Numerai",
    "crunchdao": "CrunchDAO",
    "crunch": "CrunchDAO",
    "worldquant": "WorldQuant BRAIN",
    "worldquant brain": "WorldQuant BRAIN",
    "quantconnect": "QuantConnect",
    "algogene": "Algogene",
    "ens": "ENS Challenge Data",
    "ens challenge data": "ENS Challenge Data",
    "challengedata": "ENS Challenge Data",
    "challengedata.ens.fr": "ENS Challenge Data",
    "janestreet": "Jane Street",
    "jane street": "Jane Street",
    "wundernn": "Wunder Fund",
    "wunder fund": "Wunder Fund",
    "independent": "Wunder Fund",
    "uchicago": "UChicago Trading",
    "utc": "UChicago Trading",
    "rotman": "Rotman RITC",
    "ritc": "Rotman RITC",
    "cmu": "CMU MSCF",
    "cmu mscf": "CMU MSCF",
    "bloomberg": "Bloomberg",
    "cme": "CME Group",
    "cme group": "CME Group",
    "quantchallenge": "QuantChallenge",
    "the5ers": "The5ers",
    "gresearch": "G-Research",
    "g-research": "G-Research",
    "grandcapital": "Grand Capital",
    "grand capital": "Grand Capital",
    "fmwc": "FMWC",
    "mewc": "MEWC",
    "harvard": "Harvard GCCH",
    "harvard gcch": "Harvard GCCH",
    "gcch": "Harvard GCCH",
    "fma": "FMA",
    "cmumscf": "CMU MSCF",
    "stocktrak": "StockTrak",
    "cfa": "CFA Institute",
    "cfa institute": "CFA Institute",
    "cfachallenge": "CFA Institute",
    "cfaethics": "CFA Institute",
    "mipc": "McGill MIPC",
    "mcgill": "McGill MIPC",
    "nibc": "NIBC",
    "battleonbay": "Battle on Bay",
    "battle on bay": "Battle on Bay",
    "vanberkom": "Van Berkom",
    "van berkom": "Van Berkom",
    "gem": "GEM Trader's Cup",
    "sehfc": "Southeastern Hedge Fund",
    "gameforum": "Quinnipiac GAME",
    "cornellwin": "Cornell WIN",
    "imc": "IMC Trading",
    "imc trading": "IMC Trading",
    "citadel": "Citadel / Correlation One",
    "correlation one": "Citadel / Correlation One",
    "optiver": "Optiver",
    "kaggle": "Kaggle",
    "zindi": "Zindi",
    "drivendata": "DrivenData",
    "aicrowd": "AIcrowd",
    "codalab": "CodaLab",
    "codabench": "Codabench",
    "devpost": "Devpost",
    "tianchi": "Alibaba Tianchi",
    "alibaba tianchi": "Alibaba Tianchi",
    "mlcontests": "MLContests",
    "quantcontests": "QuantContests",
}

CURRENCY_SYMBOLS: Dict[str, str] = {
    "$": "USD",
    "usd": "USD",
    "usdc": "USDC",
    "usdt": "USDT",
    "dai": "DAI",
    "nmr": "NMR",
    "us$": "USD",
    "€": "EUR",
    "eur": "EUR",
    "£": "GBP",
    "gbp": "GBP",
    "₹": "INR",
    "inr": "INR",
    "rs": "INR",
    "¥": "CNY",
    "￥": "CNY",
    "rmb": "CNY",
    "cny": "CNY",
    "jpy": "JPY",
    "cad": "CAD",
    "c$": "CAD",
    "aud": "AUD",
    "a$": "AUD",
    "chf": "CHF",
    "krw": "KRW",
    "₩": "KRW",
    "sgd": "SGD",
    "s$": "SGD",
    "hkd": "HKD",
    "hk$": "HKD",
}

NON_MONETARY_PRIZES = {
    "knowledge": "Knowledge",
    "kudos": "Kudos",
    "swag": "Swag",
    "medals": "Medals",
    "nonmonetary": "Knowledge",
    "non-monetary": "Knowledge",
    "none": "Knowledge",
    "n/a": "Knowledge",
    "tba": "TBA",
    "tbd": "TBA",
    "unknown": "Knowledge",
    "": "Knowledge",
}

# Ordered Quant Domain taxonomy rules (9 specialized categories)
QUANT_CATEGORY_RULES: List[Tuple[str, List[str]]] = [
    (
        "Market Microstructure & HFT",
        [
            "limit order book",
            "order book",
            "order-book",
            "lob ",
            "high-frequency",
            "high frequency",
            "hft",
            "market making",
            "market-making",
            "bid-ask",
            "microstructure",
            "tick data",
            "execution algorithm",
            "optimal execution",
            "slippage",
            "order flow",
            "liquidity provision",
            "wundernn",
            "connectome",
        ],
    ),
    (
        "Crypto, DeFi & Digital Assets",
        [
            "crypto",
            "cryptocurrency",
            "bitcoin",
            "btc",
            "ethereum",
            "eth ",
            "solana",
            "memecoin",
            "pump.fun",
            "defi",
            "web3",
            "binance",
            "deribit",
            "dvol",
            "on-chain",
            "digital asset",
            "perpetual futures",
            "numerai crypto",
        ],
    ),
    (
        "Macro, Commodities & Derivatives",
        [
            "option pricing",
            "implied volatility",
            "volatility surface",
            "vol surface",
            "derivatives",
            "futures trading",
            "cme group",
            "commodity",
            "commodities",
            "interest rate",
            "yield curve",
            "fixed income",
            "foreign exchange",
            "forex",
            "macroeconomic",
            "crude oil",
            "electricity market",
            "power market",
            "energy trading",
        ],
    ),
    (
        "Financial NLP & Sentiment",
        [
            "sentiment",
            "xentiment",
            "financial nlp",
            "earnings call",
            "sec filing",
            "10-k",
            "10-q",
            "finbert",
            "news analytics",
            "social sentiment",
            "central bank",
            "esg report",
        ],
    ),
    (
        "Credit, Risk & Insurance",
        [
            "credit risk",
            "credit scoring",
            "default prediction",
            "loan default",
            "fraud detection",
            "transaction fraud",
            "anti-money laundering",
            "actuarial",
            "insurance",
            "insurprime",
            "claim prediction",
            "underwriting",
            "value at risk",
            "stress test",
            "bank churn",
            "customer churn",
            "bank customer",
        ],
    ),
    (
        "Valuation, Portfolio & Case Arenas",
        [
            "portfolio challenge",
            "portfolio optimization",
            "asset allocation",
            "investment banking",
            "valuation",
            "private equity",
            "venture capital",
            "m&a",
            "corporate finance",
            "small-cap",
            "small cap",
            "hedge fund competition",
            "equity research",
            "cfa institute",
            "research challenge",
            "ethics challenge",
            "financial modeling",
            "fmwc",
            "excel world championship",
            "mewc",
            "battle on bay",
            "nibc",
            "mipc",
            "game forum",
            "cornell win",
            "harvard gcch",
            "van berkom",
            "jane street",
            "monthly puzzle",
        ],
    ),
    (
        "Algorithmic & Prop Trading",
        [
            "algorithmic trading",
            "algo trading",
            "league of algo",
            "trading competition",
            "trading challenge",
            "trader's cup",
            "trading bot",
            "quant league",
            "prop trading",
            "funded account",
            "the5ers",
            "grand capital",
            "rotman",
            "ritc",
            "uchicago trading",
            "cmu mscf",
            "imc prosperity",
            "ready trader",
            "bloomberg global trading",
            "algogene",
            "quantconnect",
            "quantchallenge",
            "quant rush",
        ],
    ),
    (
        "Alpha & Equity Prediction",
        [
            "alpha",
            "cross-sectional",
            "equity",
            "equities",
            "stock",
            "s&p 500",
            "nasdaq",
            "sharpe",
            "sortino",
            "information coefficient",
            "long-short",
            "long/short",
            "market neutral",
            "worldquant",
            "numerai",
            "datacrunch",
            "return prediction",
            "factor model",
            "statistical arbitrage",
            "stat arb",
            "g-research",
            "qrt",
            "cfm",
        ],
    ),
    (
        "Time Series & Econometrics",
        [
            "structural break",
            "regime switching",
            "change point",
            "non-stationary",
            "cointegration",
            "econometric",
            "garch",
            "hawkes",
            "synthetic price",
            "synth",
            "time series",
            "forecasting",
            "house price",
            "housing price",
            "property price",
            "apartment price",
            "real estate",
            "sales forecasting",
            "price prediction",
        ],
    ),
]

# Non-quant exclusions for biomedical / gaming / social-equity false positives
NON_QUANT_EXCLUSIONS = [
    "trading card",
    "ptcg",
    "pokemon",
    "pokémon",
    "health equity",
    "social equity",
    "gender equity",
    "racial equity",
    "mapping equity",
    "bias bounty",
    "healthcare cost",
    "broad-obesity",
    "broad-liver",
    "obesity",
    "liver",
    "metabolic disease",
    "gene perturbation",
    "leukemia",
    "myeloid",
    "patients diagnosed",
    "single-cell",
    "spatial transcriptomics",
    "histology",
    "pathology",
    "tumor",
    "cancer",
    "radiology",
    "mri ",
    "ct scan",
    "protein",
    "genomic",
    "crispr",
    "autoimmune",
    "inflammatory bowel",
    "birdclef",
    "ariel data challenge",
    "arc prize",
    "drawing with llms",
    "malaria",
    "crop yield",
    "seismic",
    "football",
    "job recommendation",
    "colour extraction",
    "product data classification",
    "_closed",
    "[closed]",
]

# Strong financial/quant phrases required for general ML platforms
GENERAL_PLATFORM_QUANT_PATTERNS = [
    r"\bquant\b",
    r"\bquantitative\s+finance\b",
    r"\balgorithmic\s+trading\b",
    r"\balgo\s+trading\b",
    r"\btrading\s+(?:signal|strategy|strategies|bot|challenge|competition|system|arena)\b",
    r"\blimit\s+order\s+book\b",
    r"\border[\s\-]book\b",
    r"\bmarket\s+(?:making|microstructure|neutral)\b",
    r"\bhigh[\s\-]frequency\s+trading\b",
    r"\bcross[\s\-]sectional\s+(?:equity|return|alpha)\b",
    r"\b(?:stock|equity|share|asset|crypto|bitcoin|memecoin|solana|ethereum|option|futures|commodity|electricity|housing|house|property|apartment)\s+(?:price|return|returns|volatility|market|forecasting|prediction|predictor|trading)\b",
    r"\b(?:memecoin|memecoins|pump\.fun|cryptocurrency|crypto\s+time\s+series|crypto\s+trading|defi\s+trading|deribit)\b",
    r"\b(?:price|return|volatility)\s+(?:movement|movements|prediction|forecasting|predictor)\b",
    r"\b(?:credit\s+risk|credit\s+scoring|loan\s+default|transaction\s+fraud|fraud\s+detection|bank\s+churn|bank\s+customer\s+churn)\b",
    r"\b(?:actuarial|insurance\s+(?:dataset|premium|claim|pricing)|insurprime)\b",
    r"\b(?:portfolio\s+optimization|asset\s+allocation|statistical\s+arbitrage|sharpe\s+ratio|implied\s+volatility)\b",
    r"\b(?:financial\s+series|financial\s+time\s+series|financial\s+market|financial\s+modeling)\b",
    r"\b(?:sales\s+forecasting)\b",
]


def is_quant_competition(
    title: str,
    description: str = "",
    category: str = "",
    tags: Optional[Iterable[str]] = None,
    source_name: str = "",
    organizer: str = "",
) -> bool:
    """Return True if a competition belongs in the Active Quant Competitions index."""
    tag_list = [str(t).strip() for t in (tags or []) if str(t).strip()]
    title_low = (title or "").lower()
    desc_low = (description or "").lower()
    cat_low = (category or "").lower()
    org_low = (organizer or "").lower()
    src_low = (source_name or "").lower()
    combined_short = f"{title_low} {cat_low} {' '.join(t.lower() for t in tag_list)} {org_low}"
    combined_full = f"{combined_short} {desc_low}"

    for excl in NON_QUANT_EXCLUSIONS:
        if excl in combined_full:
            return False

    # Dedicated quant sources
    if src_low in {"numerai", "janestreet", "quantcontests"}:
        return True

    if src_low == "crunchdao":
        # CrunchDAO hosts both quant/finance and Broad Institute biomedical challenges
        return True

    if src_low == "ens":
        ens_quant_markers = [
            "finance",
            "economic sciences",
            "insurance",
            "real estate",
            "stock",
            "equity",
            "portfolio",
            "asset",
            "volatility",
            "credit",
            "claim",
            "liquidity",
            "order book",
            "trading",
            "market",
            "electricity",
            "energy",
            "qrt",
            "cfm",
            "autorite des marches financiers",
            "autorité des marchés financiers",
            "natixis",
            "bnp paribas",
            "crédit agricole",
            "credit agricole",
            "napoleon",
            "bachelier",
            "generali",
            "elmy",
        ]
        return any(m in combined_full for m in ens_quant_markers)

    # Filter out generic university homework codes on Kaggle unless clearly open trading/quant
    if re.match(r"^(?:unir|iasa|sch\d|cs\d{3}|stat\d{3}|econ\d{3})\b", title_low):
        return False

    for pattern in GENERAL_PLATFORM_QUANT_PATTERNS:
        if re.search(pattern, combined_short, flags=re.IGNORECASE):
            return True

    # Also allow unambiguous multi-word quant phrases in description
    unambiguous_desc_phrases = [
        "limit order book",
        "algorithmic trading",
        "cross-sectional equity",
        "portfolio optimization",
        "implied volatility",
        "option pricing",
        "sharpe ratio",
        "market microstructure",
        "high-frequency trading",
    ]
    if any(p in desc_low for p in unambiguous_desc_phrases):
        return True

    return False


def canonicalize_url(url: str) -> str:
    if not url:
        return ""
    url = url.strip()
    parsed = urlparse(url)
    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = re.sub(r"/+$", "", parsed.path or "")
    query_pairs = [
        (k, v)
        for k, v in parse_qsl(parsed.query, keep_blank_values=False)
        if k.lower() not in TRACKING_QUERY_KEYS
    ]
    query = urlencode(sorted(query_pairs))
    return urlunparse((scheme, netloc, path, "", query, ""))


def normalize_platform(raw_platform: str, fallback_source: str = "") -> str:
    candidate = (raw_platform or fallback_source or "Independent").strip()
    key = candidate.lower()
    return PLATFORM_ALIASES.get(key, candidate)


def normalize_title(title: str) -> str:
    cleaned = re.sub(r"\s+", " ", (title or "").strip())
    return cleaned


def slugify_title(title: str) -> str:
    text = (title or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def make_record_id(platform: str, title: str, url: str) -> str:
    canon = canonicalize_url(url)
    base = f"{platform.lower()}::{canon or slugify_title(title)}"
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]
    slug = re.sub(r"[^a-z0-9]+", "-", slugify_title(title)).strip("-")[:48]
    return f"{slug}-{digest}" if slug else digest


def parse_prize(raw: Optional[str | float | int]) -> Tuple[str, float, str]:
    """Return (formatted_prize, prize_usd, currency_code)."""
    fx_rates = get_fx_rates()
    if raw is None:
        return ("Knowledge", 0.0, "USD")

    if isinstance(raw, (int, float)):
        val = float(raw)
        if val <= 0:
            return ("Knowledge", 0.0, "USD")
        return (f"${val:,.0f}", val, "USD")

    text = str(raw).strip()
    if not text:
        return ("Knowledge", 0.0, "USD")

    low = text.lower().strip()
    if low in NON_MONETARY_PRIZES:
        return (NON_MONETARY_PRIZES[low], 0.0, "USD")

    # Detect currency
    currency = "USD"
    for token, code in CURRENCY_SYMBOLS.items():
        if token in low:
            currency = code
            break

    # Match numbers with optional k/m suffix, e.g. "$100,000", "30k $USDC", "1,000 $USDC/week"
    match = re.search(
        r"(\d{1,3}(?:[,\s]\d{3})+|\d+(?:\.\d+)?)\s*([kKmM]|thousand|million)?",
        text,
    )
    if not match:
        return (text, 0.0, "USD")

    num_str = re.sub(r"[,\s]", "", match.group(1))
    try:
        amount = float(num_str)
    except ValueError:
        return (text, 0.0, "USD")

    suffix = (match.group(2) or "").lower()
    if suffix in ("k", "thousand"):
        amount *= 1_000
    elif suffix in ("m", "million"):
        amount *= 1_000_000

    if amount <= 0:
        return ("Knowledge", 0.0, "USD")

    rate = fx_rates.get(currency, 1.0)
    usd_val = round(amount * rate, 2)

    if currency == "USD":
        # Preserve descriptive suffixes like "/round" or "/week" if present
        if any(s in low for s in ("/week", "/round", "/month", "ongoing", "usdc", "nmr")):
            display = text
        else:
            display = f"${amount:,.0f}"
    elif currency in ("USDC", "USDT", "DAI", "NMR"):
        display = text
    else:
        display = f"{text} (~${usd_val:,.0f})"

    return (display, usd_val, currency)


def parse_date(raw: Optional[str], reference_now: Optional[datetime] = None) -> Optional[str]:
    """Parse flexible date strings into ISO YYYY-MM-DD."""
    if not raw:
        return None
    text = str(raw).strip()
    if not text or text.lower() in {"tba", "tbd", "none", "null", "ongoing", "continuous", "n/a", "-"}:
        return None

    now = reference_now or datetime.now(timezone.utc)

    rel_match = re.search(r"(\d+)\s+(day|days|month|months|hour|hours)", text, re.IGNORECASE)
    if rel_match and ("left" in text.lower() or "remaining" in text.lower() or "in " in text.lower()):
        qty = int(rel_match.group(1))
        unit = rel_match.group(2).lower()
        days_delta = qty * 30 if "month" in unit else (max(1, qty // 24) if "hour" in unit else qty)
        from datetime import timedelta

        target = (now + timedelta(days=days_delta)).date()
        return target.isoformat()

    cleaned = re.sub(r"^(?:ends|deadline|closes|due|until|by)[:\s]+", "", text, flags=re.IGNORECASE).strip()

    try:
        dt = date_parser.parse(cleaned, default=datetime(now.year, 1, 1))
        return dt.date().isoformat()
    except (ValueError, OverflowError, TypeError):
        return None


def compute_days_remaining(end_date_iso: Optional[str], today: Optional[date] = None) -> Optional[int]:
    if not end_date_iso:
        return None
    ref = today or datetime.now(timezone.utc).date()
    try:
        target = date.fromisoformat(end_date_iso)
    except ValueError:
        return None
    return (target - ref).days


def is_active_competition(
    end_date_iso: Optional[str],
    raw_status: str = "active",
    today: Optional[date] = None,
) -> Tuple[bool, str, Optional[int]]:
    """Determine if a competition is currently active or upcoming."""
    ref = today or datetime.now(timezone.utc).date()
    status_low = (raw_status or "active").lower().strip()

    if status_low in {"completed", "closed", "ended", "finished", "archived", "past"}:
        return (False, "ended", None)

    days_rem = compute_days_remaining(end_date_iso, today=ref)
    if days_rem is not None:
        if days_rem < 0:
            return (False, "ended", days_rem)
        if days_rem <= 7:
            return (True, "ending_soon", days_rem)

    if status_low in {"upcoming", "soon", "pending", "registration"}:
        return (True, "upcoming", days_rem)

    return (True, "active", days_rem)


def infer_category(title: str, description: str, tags: Iterable[str], raw_category: str = "") -> str:
    combined = " ".join([title or "", description or "", raw_category or "", " ".join(tags or [])]).lower()
    for category, keywords in QUANT_CATEGORY_RULES:
        for kw in keywords:
            if kw in combined:
                return category
    if raw_category and raw_category.strip():
        return raw_category.strip()
    return "Alpha & Equity Prediction"


def infer_competition_type(
    title: str,
    description: str,
    tags: Iterable[str],
    prize_raw: str,
    end_date_iso: Optional[str],
    raw_type: str = "",
) -> str:
    """Classify into 'competition' | 'tournament' | 'benchmark' | 'hackathon'."""
    if raw_type and raw_type.lower() in {"competition", "tournament", "benchmark", "hackathon", "practice"}:
        rt = raw_type.lower()
        return "benchmark" if rt == "practice" else rt

    combined = " ".join([title or "", description or "", " ".join(tags or [])]).lower()
    prize_low = (prize_raw or "").lower()

    if any(k in combined for k in ["hackathon", "bounty", "devpost"]):
        return "hackathon"

    if any(
        k in combined
        for k in [
            "tournament",
            "continuous",
            "ongoing",
            "weekly payout",
            "numerai",
            "datacrunch",
            "worldquant brain",
            "quant league",
        ]
    ):
        return "tournament"

    if any(k in combined for k in ["playground", "getting started", "tutorial", "practice", "benchmark"]):
        return "benchmark"

    if end_date_iso and end_date_iso >= "2029-01-01" and prize_low in {"knowledge", "kudos", "medals", ""}:
        return "benchmark"

    return "competition"


def infer_difficulty(
    prize_usd: float,
    category: str,
    tags: Iterable[str],
    description: str,
    raw_difficulty: str = "",
) -> str:
    if raw_difficulty and raw_difficulty.strip() in {"Beginner", "Intermediate", "Advanced", "Research"}:
        return raw_difficulty.strip()

    combined = " ".join([category or "", description or "", " ".join(tags or [])]).lower()
    if any(k in combined for k in ["beginner", "getting started", "playground", "starter", "student", "introductory"]):
        return "Beginner"
    if prize_usd >= 50_000 or any(
        k in combined
        for k in [
            "research",
            "adia lab",
            "limit order book",
            "high-frequency",
            "structural break",
            "market microstructure",
            "icaif",
            "neurips",
        ]
    ):
        return "Research"
    if prize_usd >= 10_000 or any(
        k in combined for k in ["advanced", "hedge fund", "prop trading", "sharpe", "market neutral", "options"]
    ):
        return "Advanced"
    return "Intermediate"


def build_record(
    *,
    title: str,
    platform: str,
    source: str,
    url: str,
    prize: Optional[str | float | int] = None,
    prize_usd_override: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    raw_status: str = "active",
    category: str = "",
    tags: Optional[List[str]] = None,
    description: str = "",
    organizer: str = "",
    evaluation_metric: str = "",
    teams_count: Optional[int] = None,
    competitors_count: Optional[int] = None,
    entries_count: Optional[int] = None,
    difficulty: str = "",
    competition_type: str = "",
    scraped_at: Optional[str] = None,
    today: Optional[date] = None,
) -> Optional[CompetitionRecord]:
    clean_title = normalize_title(title)
    canon_url = canonicalize_url(url)
    if not clean_title or not canon_url:
        return None

    norm_platform = normalize_platform(platform, fallback_source=source)
    start_iso = parse_date(start_date)
    end_iso = parse_date(end_date)

    active, norm_status, days_rem = is_active_competition(end_iso, raw_status=raw_status, today=today)
    if not active:
        return None

    prize_display, prize_usd, prize_currency = parse_prize(prize)
    if prize_usd_override is not None and prize_usd_override > 0:
        prize_usd = round(float(prize_usd_override), 2)
        if prize_display in ("Knowledge", "") and prize is None:
            prize_display = f"${prize_usd:,.0f}"

    clean_tags = sorted({t.strip() for t in (tags or []) if t and t.strip()})[:10]
    norm_category = infer_category(clean_title, description, clean_tags, raw_category=category)
    norm_diff = infer_difficulty(prize_usd, norm_category, clean_tags, description, raw_difficulty=difficulty)
    norm_type = infer_competition_type(
        clean_title,
        description,
        clean_tags,
        str(prize or ""),
        end_iso,
        raw_type=competition_type,
    )
    conference, conference_year, paper_url = enrich_research_fields(
        clean_title,
        description,
        clean_tags,
        organizer=organizer,
        platform=norm_platform,
    )

    now_iso = scraped_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return CompetitionRecord(
        id=make_record_id(norm_platform, clean_title, canon_url),
        title=clean_title,
        platform=norm_platform,
        source=source,
        url=canon_url,
        prize=prize_display,
        prize_usd=prize_usd,
        prize_currency=prize_currency,
        prize_raw=str(prize or ""),
        start_date=start_iso,
        end_date=end_iso,
        days_remaining=days_rem,
        status=norm_status,
        category=norm_category,
        tags=clean_tags,
        description=(description or "").strip()[:500],
        organizer=(organizer or norm_platform).strip(),
        evaluation_metric=(evaluation_metric or "").strip(),
        teams_count=teams_count,
        competitors_count=competitors_count,
        entries_count=entries_count,
        difficulty=norm_diff,
        competition_type=norm_type,
        conference=conference,
        conference_year=conference_year,
        paper_url=paper_url,
        scraped_at=now_iso,
    )
