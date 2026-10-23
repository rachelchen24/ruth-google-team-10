"""Pathways to Science (IBP) STEM programs. Search page -> programhub detail pages -> RawRecords for LLM extraction.

No LLM key? `to_listing()` parses the labelled sections (level, description, institution, disciplines, keywords)
directly. Dates, eligibility details, and cost are left for the LLM pass.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .. import fetch
from ..geo import state_code
from ..schema import Listing, Location, RawRecord

BASE = "https://www.pathwaystoscience.org/"
LEVELS = {
    "HS": "HighSchool_High School Students",
    "college": "Undergrads*Fresh_Undergraduate Students - First Year",
}
FREE_HINT = re.compile(r"\b(free|no cost|at no charge|tuition[- ]free|stipend|paid (summer )?(internship|research)|"
                       r"fully funded|full scholarship|housing (is )?provided)\b", re.I)


def search(level_value: str) -> dict[str, dict]:
    """programhub URL -> {provider, location} from the result list's org header ('Org (City, ST)')."""
    html = fetch.get(urljoin(BASE, "programs.aspx"), params={"u": level_value, "submit": "y", "adv": "adv"})
    soup = BeautifulSoup(html, "html.parser")
    out: dict[str, dict] = {}
    for h2 in soup.find_all("h2"):
        header = h2.find_parent("div")
        body = header.find_next_sibling("div") if header else None
        a = body.find("a", href=re.compile("programhub", re.I)) if body else None
        if not a:
            continue
        url = urljoin(BASE, a["href"])
        meta = {"provider": h2.get_text(strip=True)}
        span = header.find("span")
        if span and (m := re.match(r"\s*\((.+),\s*([^,]+)\)\s*$", span.get_text())):
            meta["location"] = {"city": m.group(1).strip().title(), "state": state_code(m.group(2))}
        out.setdefault(url, meta)
    return out


def detail(url: str, level: str, meta: dict) -> RawRecord | None:
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
                     hint={"kind": "opportunity", "type": "program", "school_levels": [level],
                           "listing_page": url, **meta})


def fetch_raw(limit: int | None = None) -> list[RawRecord]:
    out, seen = [], set()
    for level, value in LEVELS.items():
        for url, meta in search(value).items():
            if url in seen:
                continue
            seen.add(url)
            if (r := detail(url, level, meta)):
                out.append(r)
            if limit and len(out) >= limit:
                return out
    return out


def _section(text: str, label: str, stops: tuple[str, ...]) -> list[str]:
    i = text.find(label)
    if i < 0:
        return []
    lines = []
    for line in text[i + len(label):].split("\n"):
        if line in stops:
            break
        if line.strip():
            lines.append(line.strip())
    return lines


def to_listing(rec: RawRecord) -> Listing:
    t = rec.raw_text
    labels = ("Academic Level:", "Description:", "Participating Institution(s):", "Program Materials:",
              "This Program can be Described by:", "Academic Disciplines:", "Keywords:", "Learn More and Apply!",
              "This program is funded by:", "Page last updated", "Application Deadline:", "Program Dates:")
    levels = _section(t, "Academic Level:", labels)
    desc = " ".join(_section(t, "Description:", labels))
    tags = _section(t, "Academic Disciplines:", labels) + _section(t, "Keywords:", labels)
    school_levels = sorted({"HS" for l in levels if l.startswith("High School")} |
                           {"college" for l in levels if l.startswith("Undergraduate")}) or rec.hint["school_levels"]
    summary = " ".join(re.split(r"(?<=[.!?])\s+", desc)[:2])[:400] or None
    loc = rec.hint.get("location")
    return Listing(
        kind="opportunity", type="program", source="pathways", title=rec.title,
        provider=rec.hint.get("provider"), url=rec.url, summary=summary,
        school_levels=school_levels, location=Location(**loc) if loc else None,
        is_online=bool(re.search(r"\b(virtual|online|remote)\b", desc, re.I)) or None,
        cost=0 if FREE_HINT.search(desc) else None,
        covers=["stipend"] if re.search(r"\b(stipend|paid)\b", desc, re.I) else [],
        focus_tags=["stem", *[x.replace(" Fields", "") for x in tags]],
        raw_text=rec.raw_text, scraped_at=datetime.now(timezone.utc).isoformat(),
    ).finalize()
