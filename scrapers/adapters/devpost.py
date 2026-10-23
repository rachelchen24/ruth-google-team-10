"""Devpost hackathons via the site's internal JSON endpoint (unofficial, may change)."""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone

from .. import fetch
from ..schema import Listing, Location

API = "https://devpost.com/api/hackathons"
MONTHS = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


def parse_period(s: str) -> tuple[date | None, date | None]:
    """'Oct 30 - Dec 04, 2026' | 'Nov 01 - 05, 2026' | 'Dec 20, 2026' | 'Aug 23, 2026 - Jan 02, 2027'."""
    parts = [p.strip() for p in s.split(" - ")]
    end_m = re.match(r"(?:(\w{3}) )?(\d{1,2}), (\d{4})", parts[-1])
    if not end_m:
        return None, None
    start_m = re.match(r"(\w{3}) (\d{1,2})(?:, (\d{4}))?", parts[0])
    end_mon = MONTHS.get(end_m.group(1) or start_m.group(1))
    end = date(int(end_m.group(3)), end_mon, int(end_m.group(2)))
    if len(parts) == 1:
        return end, end
    start_year = int(start_m.group(3)) if start_m.group(3) else end.year
    start = date(start_year, MONTHS[start_m.group(1)], int(start_m.group(2)))
    if start > end:  # 'Dec 28 - Jan 03, 2027' crosses a year
        start = start.replace(year=start.year - 1)
    return start, end


def fetch_listings(max_pages: int = 10) -> list[Listing]:
    now = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for status in ("upcoming", "open"):
        for page in range(1, max_pages + 1):
            data = json.loads(fetch.get(API, params={"status[]": status, "page": page, "per_page": 40}))
            hacks = data["hackathons"]
            for h in hacks:
                if h["id"] in seen or h.get("invite_only"):
                    continue
                seen.add(h["id"])
                start, end = parse_period(h.get("submission_period_dates") or "")
                loc = (h.get("displayed_location") or {}).get("location") or ""
                online = loc.strip().lower() == "online"
                prize = re.sub(r"<[^>]+>", "", h.get("prize_amount") or "")
                themes = [t["name"].lower() for t in h.get("themes", [])]
                out.append(Listing(
                    kind="opportunity", type="hackathon", source="devpost",
                    title=h["title"], provider=h.get("organization_name"), url=h["url"],
                    summary=f"Hackathon ({'online' if online else loc}). Prizes: {prize or 'n/a'}. "
                            f"{h.get('registrations_count', 0)} registered.",
                    scope="online" if online else "local",
                    start_date=start, end_date=end,
                    location=None if online else Location(city=loc),
                    is_online=online, cost=0, apply_effort=["short_form"],
                    focus_tags=["hackathon", "coding", *themes],
                    published_applicants=h.get("registrations_count"),
                    raw_text=json.dumps(h), scraped_at=now,
                ).finalize())
            if len(hacks) < 40:
                break
    return out
