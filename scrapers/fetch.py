"""Polite HTTP: robots.txt check, per-host rate limit, on-disk cache (§6.2)."""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

UA = "ScoutStudentFinder/0.1 (hackathon project; student scholarship search)"
CACHE = Path(__file__).resolve().parent.parent / "data" / "cache"
MIN_DELAY = 1.5  # seconds between hits to the same host

_client = httpx.Client(headers={"User-Agent": UA}, follow_redirects=True, timeout=30)
_robots: dict[str, RobotFileParser] = {}
_last_hit: dict[str, float] = {}


def allowed(url: str) -> bool:
    p = urlparse(url)
    host = f"{p.scheme}://{p.netloc}"
    if host not in _robots:
        rp = RobotFileParser()
        try:
            r = _client.get(f"{host}/robots.txt")
            rp.parse(r.text.splitlines() if r.status_code == 200 else [])
        except httpx.HTTPError:
            rp.parse([])
        _robots[host] = rp
    return _robots[host].can_fetch(UA, url)


def get(url: str, *, params: dict | None = None, headers: dict | None = None, use_cache: bool = True) -> str:
    """GET text, cached by URL+params. Raises PermissionError if robots.txt disallows."""
    key = hashlib.sha1(f"{url}|{sorted((params or {}).items())}".encode()).hexdigest()
    path = CACHE / f"{key}.txt"
    if use_cache and path.exists():
        return path.read_text(encoding="utf-8")
    if not allowed(url):
        raise PermissionError(f"robots.txt disallows {url}")
    host = urlparse(url).netloc
    wait = MIN_DELAY - (time.time() - _last_hit.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    r = _client.get(url, params=params, headers=headers)
    _last_hit[host] = time.time()
    r.raise_for_status()
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(r.text, encoding="utf-8")
    return r.text
