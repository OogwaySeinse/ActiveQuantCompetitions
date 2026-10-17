"""Live & cached Foreign Exchange (FX) and Crypto/Stablecoin rates (base USD)."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Dict

import requests

logger = logging.getLogger(__name__)

CACHE_PATH = Path(__file__).resolve().parent.parent / "data" / "cache" / "fx_rates.json"
CACHE_TTL_SECONDS = 86400  # 24 hours

# Fallback USD multiplier per 1 unit of foreign/crypto currency
FALLBACK_TO_USD: Dict[str, float] = {
    "USD": 1.0,
    "USDC": 1.0,
    "USDT": 1.0,
    "DAI": 1.0,
    "NMR": 18.0,
    "EUR": 1.09,
    "GBP": 1.28,
    "INR": 0.012,
    "CNY": 0.14,
    "RMB": 0.14,
    "JPY": 0.0066,
    "CAD": 0.73,
    "AUD": 0.66,
    "CHF": 1.13,
    "KRW": 0.00073,
    "RUB": 0.011,
    "SGD": 0.75,
    "BRL": 0.18,
    "ZAR": 0.055,
    "HKD": 0.128,
}

_MEMO_RATES: Dict[str, float] | None = None


def get_fx_rates(refresh: bool = False) -> Dict[str, float]:
    """Return mapping of Currency Code -> USD multiplier (1 unit = X USD)."""
    global _MEMO_RATES
    if _MEMO_RATES is not None and not refresh:
        return _MEMO_RATES

    if not refresh and CACHE_PATH.exists():
        try:
            stat = CACHE_PATH.stat()
            if (time.time() - stat.st_mtime) < CACHE_TTL_SECONDS:
                data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
                if isinstance(data, dict) and "USD" in data:
                    merged = dict(FALLBACK_TO_USD)
                    merged.update({k: float(v) for k, v in data.items()})
                    _MEMO_RATES = merged
                    return _MEMO_RATES
        except Exception as exc:
            logger.debug("FX cache read failed: %s", exc)

    rates = dict(FALLBACK_TO_USD)
    try:
        resp = requests.get("https://open.er-api.com/v6/latest/USD", timeout=8)
        if resp.status_code == 200:
            payload = resp.json()
            per_usd = payload.get("rates") or {}
            for code, units_per_usd in per_usd.items():
                try:
                    val = float(units_per_usd)
                    if val > 0:
                        rates[code.upper()] = round(1.0 / val, 6)
                except (TypeError, ValueError):
                    continue
            rates["RMB"] = rates.get("CNY", 0.14)
            rates["USDC"] = 1.0
            rates["USDT"] = 1.0
            rates["DAI"] = 1.0
            CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            CACHE_PATH.write_text(json.dumps(rates, indent=2), encoding="utf-8")
    except Exception as exc:
        logger.debug("Live FX fetch failed (using fallback): %s", exc)

    _MEMO_RATES = rates
    return rates

