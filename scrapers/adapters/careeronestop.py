"""CareerOneStop Scholarship Finder API (U.S. DOL). Needs COS_USER_ID + COS_TOKEN env vars.

Register: https://www.careeronestop.org/Developers/WebAPI/registration.aspx
TODO once the token arrives: check the path + response field names against the API explorer;
records go through LLM extraction as JSON text, so field-name drift doesn't break anything.
"""
from __future__ import annotations

import json
import os

from .. import fetch
from ..schema import RawRecord

PATH = "https://api.careeronestop.org/v1/scholarshipfinder/{uid}/{kw}/0/0/0/{start}/{limit}"
KEYWORDS = ["high school", "undergraduate", "first generation", "community service", "engineering", "athlete"]


def fetch_raw(per_keyword: int = 100) -> list[RawRecord]:
    uid, token = os.environ.get("COS_USER_ID"), os.environ.get("COS_TOKEN")
    if not (uid and token):
        print("careeronestop: COS_USER_ID / COS_TOKEN not set, skipping")
        return []
    out, seen = [], set()
    for kw in KEYWORDS:
        url = PATH.format(uid=uid, kw=kw, start=0, limit=per_keyword)
        data = json.loads(fetch.get(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}))
        items = data.get("ScholarshipList") or data.get("Scholarships") or data.get("scholarships") or []
        for s in items:
            key = s.get("Id") or s.get("ID") or s.get("Name")
            if key in seen:
                continue
            seen.add(key)
            out.append(RawRecord(source="careeronestop", url=s.get("Url") or s.get("URL") or "",
                                 title=s.get("Name") or s.get("Title") or "", raw_text=json.dumps(s),
                                 hint={"kind": "scholarship", "scope": "national"}))
    return out
