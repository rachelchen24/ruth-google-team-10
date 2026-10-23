"""Hand-picked pages (community foundations, university outreach, company events, counseling lists...).

Add URLs to data/sources.json: [{"url": ..., "kind": "scholarship"|"opportunity", "note": "..."}].
Each page becomes one RawRecord; the LLM splits multi-listing pages into several listings.
"""
from __future__ import annotations

import json
from pathlib import Path

from bs4 import BeautifulSoup

from .. import fetch
from ..schema import RawRecord

SOURCES = Path(__file__).resolve().parents[2] / "data" / "sources.json"


def fetch_raw() -> list[RawRecord]:
    if not SOURCES.exists():
        return []
    out = []
    for src in json.loads(SOURCES.read_text(encoding="utf-8")):
        try:
            soup = BeautifulSoup(fetch.get(src["url"]), "html.parser")
        except Exception as e:  # one bad page shouldn't kill the run
            print(f"pages: skip {src['url']}: {e}")
            continue
        for t in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            t.decompose()
        title = soup.title.string.strip() if soup.title and soup.title.string else src["url"]
        out.append(RawRecord(source="pages", url=src["url"], title=title,
                             raw_text=soup.get_text("\n", strip=True)[:20000],
                             hint={k: v for k, v in src.items() if k != "url"}))
    return out
