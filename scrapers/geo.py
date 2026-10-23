"""Offline US geocoding from Census 2024 gazetteer centroids (data/geo/). No API, no rate limits.

  zip_to_latlng("43210")                    -> (39.99, -83.01)
  place_to_latlng("Columbus", "OH")         -> (39.98, -82.98)
  geocode_text("Palace of Fine Arts, San Francisco, California, USA") -> (37.77, -122.42)
  distance_miles(a, b)
"""
from __future__ import annotations

import csv
import math
import re
from functools import cache
from pathlib import Path

from .schema import Listing

GEO = Path(__file__).resolve().parent.parent / "data" / "geo"

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
    "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC", "puerto rico": "PR",
}
CODES = set(US_STATES.values())
# Census interior points that land somewhere silly (SF's includes the Farallon Islands).
OVERRIDES = {("CA", "san francisco"): (37.7749, -122.4194)}


def state_code(s: str | None) -> str | None:
    if not s:
        return None
    s = s.strip().rstrip(".")
    return s.upper() if s.upper() in CODES else US_STATES.get(s.lower())


@cache
def _zips() -> dict[str, tuple[float, float]]:
    with open(GEO / "zips.csv", encoding="utf-8") as f:
        return {r["zip"]: (float(r["lat"]), float(r["lng"])) for r in csv.DictReader(f)}


@cache
def _places() -> dict[tuple[str, str], tuple[float, float]]:
    with open(GEO / "places.csv", encoding="utf-8") as f:
        d = {(r["state"], r["name"]): (float(r["lat"]), float(r["lng"])) for r in csv.DictReader(f)}
    return d | OVERRIDES


def zip_to_latlng(z: str | None) -> tuple[float, float] | None:
    return _zips().get((z or "").strip()[:5]) if z else None


def place_to_latlng(city: str | None, state: str | None) -> tuple[float, float] | None:
    st = state_code(state)
    if not (city and st):
        return None
    name = re.sub(r"^(st\.?|saint) ", "st. ", city.strip().lower())
    return _places().get((st, name)) or _places().get((st, name.replace("st. ", "saint ")))


def geocode_text(text: str | None) -> tuple[float, float] | None:
    """Best effort on free text like 'Newell Hall, Gainesville, FL 32611' or 'Boston, Massachusetts, USA'."""
    if not text:
        return None
    if (m := re.search(r"\b(\d{5})(?:-\d{4})?\b", text)) and (ll := zip_to_latlng(m.group(1))):
        return ll
    parts = [p.strip() for p in text.split(",") if p.strip()]
    parts = [p for p in parts if p.lower() not in ("usa", "us", "united states", "united states of america")]
    for i in range(len(parts) - 1, 0, -1):
        st = state_code(re.sub(r"\s+\d{5}.*$", "", parts[i]))
        if st and (ll := place_to_latlng(parts[i - 1], st)):
            return ll
    return None


def distance_miles(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lng1, lat2, lng2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lng2 - lng1) / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(h))


def fill_coords(l: Listing) -> Listing:
    """Set location.lat/lng (and state when we learn it) if missing."""
    loc = l.location
    if not loc or loc.lat is not None:
        return l
    ll = zip_to_latlng(loc.zip) or place_to_latlng(loc.city, loc.state) or geocode_text(
        ", ".join(p for p in (loc.city, loc.state) if p))
    if ll:
        loc.lat, loc.lng = ll
    return l
