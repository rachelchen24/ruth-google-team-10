"""MLH season page. Event data is embedded as Inertia JSON in <script data-page="app">."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from .. import fetch
from ..schema import Listing, Location

SEASON_URL = "https://www.mlh.com/seasons/{season}/events"

US_STATES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA", "colorado": "CO",
    "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS", "kentucky": "KY", "louisiana": "LA",
    "maine": "ME", "maryland": "MD", "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
    "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN", "texas": "TX",
    "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
}


def state_code(s: str | None) -> str | None:
    if not s:
        return None
    s = s.strip()
    return s.upper() if len(s) == 2 else US_STATES.get(s.lower())


def fetch_listings(season: int = 2027) -> list[Listing]:
    url = SEASON_URL.format(season=season)
    soup = BeautifulSoup(fetch.get(url), "html.parser")
    props = json.loads(soup.find("script", attrs={"data-page": "app"}).string)["props"]
    now = datetime.now(timezone.utc).isoformat()
    out = []
    for e in props["upcomingEvents"]:
        venue = e.get("venueAddress") or {}
        online = e.get("formatType") == "digital"
        name = e["name"].strip()
        hs = "high school" in name.lower() or name.lower().startswith("hs ")
        focus = [f.lower() for f in (e.get("customFields") or {}).get("hackathon_focus", [])]
        underserved = (e.get("customFields") or {}).get("underserved_types", [])
        out.append(Listing(
            kind="opportunity", type="hackathon", source="mlh",
            title=name, provider="MLH member event",
            url=e.get("websiteUrl") or f"https://www.mlh.com{e['url']}",
            summary=f"MLH hackathon in {e.get('location')}." if not online else "Online MLH hackathon.",
            school_levels=["HS"] if hs else ["college"],
            scope="online" if online else "local",
            start_date=e["startsAt"][:10], end_date=e["endsAt"][:10],
            location=None if online else Location(city=venue.get("city"), state=state_code(venue.get("state"))),
            is_online=online, cost=0, covers=["food"],  # MLH events are free and feed attendees
            apply_effort=["short_form"],
            eligibility={"identity_groups": underserved},
            focus_tags=["hackathon", "coding", *focus],
            raw_text=json.dumps(e), scraped_at=now,
        ).finalize())
    return out
