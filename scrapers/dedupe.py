"""Dedupe by normalized URL, then fuzzy title within the same kind (§6.3). Keeps the richer record."""
from __future__ import annotations

import re
from datetime import date
from difflib import SequenceMatcher
from urllib.parse import urlparse

from .schema import Listing


def _norm_url(u: str) -> str:
    p = urlparse(u.lower())
    return (p.netloc.removeprefix("www.") + p.path.rstrip("/"))


def _norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()


def _richness(l: Listing) -> int:
    return sum(1 for v in l.model_dump(exclude={"raw_text"}).values() if v not in (None, [], {}, ""))


def dedupe(listings: list[Listing], threshold: float = 0.9) -> list[Listing]:
    kept: list[Listing] = []
    by_url: dict[str, int] = {}
    for l in sorted(listings, key=_richness, reverse=True):
        u = _norm_url(l.url)
        if u in by_url:
            continue
        t = _norm_title(l.title)
        if any(k.kind == l.kind and SequenceMatcher(None, t, _norm_title(k.title)).ratio() >= threshold
               and (k.provider or "").lower() == (l.provider or "").lower() for k in kept):
            continue
        by_url[u] = len(kept)
        kept.append(l)
    return kept


def drop_expired(listings: list[Listing], today: date | None = None) -> list[Listing]:
    today = today or date.today()
    def live(l: Listing) -> bool:
        last = l.deadline or l.application_deadline or l.end_date
        return last is None or last >= today
    return [l for l in listings if live(l)]
