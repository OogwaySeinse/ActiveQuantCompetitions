from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"


def create_session(retries: int = 3, backoff_factor: float = 0.6) -> requests.Session:
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "POST"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def save_source_cache(source_name: str, payload: Any) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path = CACHE_DIR / f"{source_name}.json"
        cache_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:
        logger.debug("Failed to write cache for %s: %s", source_name, exc)


def load_source_cache(source_name: str) -> Optional[Any]:
    cache_path = CACHE_DIR / f"{source_name}.json"
    if not cache_path.exists():
        return None
    try:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.debug("Failed to read cache for %s: %s", source_name, exc)
        return None


def safe_get(
    session: requests.Session,
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, Any]] = None,
    timeout: int = 25,
    delay: float = 0.2,
) -> Optional[requests.Response]:
    if delay > 0:
        time.sleep(delay)
    try:
        resp = session.get(url, params=params, headers=headers, timeout=timeout)
        if resp.status_code >= 400:
            logger.warning("GET %s returned HTTP %s", url, resp.status_code)
            return None
        return resp
    except requests.RequestException as exc:
        logger.warning("GET %s failed: %s", url, exc)
        return None


def safe_post(
    session: requests.Session,
    url: str,
    *,
    json_body: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
    headers: Optional[Dict[str, Any]] = None,
    timeout: int = 25,
    delay: float = 0.2,
) -> Optional[requests.Response]:
    if delay > 0:
        time.sleep(delay)
    try:
        resp = session.post(url, json=json_body, data=data, headers=headers, timeout=timeout)
        if resp.status_code >= 400:
            logger.warning("POST %s returned HTTP %s", url, resp.status_code)
            return None
        return resp
    except requests.RequestException as exc:
        logger.warning("POST %s failed: %s", url, exc)
        return None

