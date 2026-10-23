"""Pathways to Science (IBP) STEM programs. Search page -> programhub detail pages -> RawRecords for LLM extraction."""
from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .. import fetch
from ..schema import RawRecord

BASE = "https://www.pathwaystoscience.org/"
LEVELS = {
    "HS": "HighSchool_High School Students",
    "college": "Undergrads*Fresh_Undergraduate Students - First Year",
}


def search(level_value: str) -> list[str]:
    html = fetch.get(urljoin(BASE, "programs.aspx"), params={"u": level_value, "submit": "y", "adv": "adv"})
    soup = BeautifulSoup(html, "html.parser")
    return sorted({urljoin(BASE, a["href"]) for a in soup.find_all("a", href=True) if "programhub.aspx" in a["href"].lower()})


def detail(url: str, level: str) -> RawRecord | None:
    soup = BeautifulSoup(fetch.get(url), "html.parser")
    for t in soup(["script", "style"]):
        t.decompose()
    title = (soup.title.string or "").strip() if soup.title else ""
    apply = next((a["href"] for a in soup.find_all("a", href=True) if "apply" in a.get_text().lower()
                  and not a["href"].lower().startswith(("programhub", "/programhub", "#"))), None)
    text = soup.get_text("\n", strip=True)
    start = text.find("Program Info")
    end = text.find("Membership Information")
    text = text[start if start >= 0 else 0: end if end > 0 else None]
    if not title or len(text) < 100:
        return None
    return RawRecord(source="pathways", url=apply or url, title=title, raw_text=text[:8000],
                     hint={"kind": "opportunity", "type": "program", "school_levels": [level], "listing_page": url})


def fetch_raw(limit: int | None = None) -> list[RawRecord]:
    out, seen = [], set()
    for level, value in LEVELS.items():
        for url in search(value):
            if url in seen:
                continue
            seen.add(url)
            if (r := detail(url, level)):
                out.append(r)
            if limit and len(out) >= limit:
                return out
    return out
