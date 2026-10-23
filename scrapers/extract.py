"""LLM pass: RawRecord -> list[Listing] (§6.3).

Provider-agnostic via the OpenAI SDK's compatible endpoint. Env vars:
  LLM_API_KEY, LLM_MODEL, LLM_BASE_URL (omit for OpenAI; Gemini: https://generativelanguage.googleapis.com/v1beta/openai/)
Results are cached by record hash in data/cache/llm/ so re-runs are free.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from .schema import Listing, RawRecord

CACHE = Path(__file__).resolve().parent.parent / "data" / "cache" / "llm"

PROMPT = """You turn scraped scholarship / student-opportunity pages into JSON for a student matching app.
Today is {today}. Return {{"listings": [...]}}. A page may hold 0, 1, or many listings; skip anything that is
not a scholarship or a student opportunity, and skip awards whose deadline has passed with no sign they recur.

Each listing object uses these keys (use null / [] when the page doesn't say; never guess):
kind: "scholarship" | "opportunity"
title, provider, url (direct apply/info link if present, else null), summary (1-2 plain sentences)
school_levels: subset of ["HS","college"]
scope: "local" | "state" | "national" | "online"
eligibility: {{states: [2-letter], counties: [], class_years: ["HS 9".."HS 12","college 1".."college 4"],
  min_gpa, citizenship: [], majors: [], identity_groups: [], need_based, min_age, max_age, gender: []}}
focus_tags: short lowercase tags for what the award/event is about (e.g. "robotics", "food insecurity", "soccer")
Scholarship only: amount_min, amount_max, num_awards, deadline (YYYY-MM-DD),
  requirements: {{essay, recommendations, transcript, interview, application_fee}},
  is_sweepstakes (true for no-essay lead-gen/raffle style awards)
Opportunity only: type: "outreach_event"|"hackathon"|"company_visit"|"company_event"|"competition"|"program",
  start_date, end_date, application_deadline (YYYY-MM-DD), location: {{city, state, zip}}, is_online,
  cost (0 if free), covers: subset of ["travel","food","lodging","stipend"],
  apply_effort: subset of ["short_form","essay","rec","first_come","interview"], capacity
published_applicants: integer only if the page states how many people applied.

Known context from the scraper (trust it): {hint}
Page title: {title}
Page URL: {url}
Page text:
{text}"""


def _client():
    from openai import OpenAI
    return OpenAI(api_key=os.environ["LLM_API_KEY"], base_url=os.environ.get("LLM_BASE_URL") or None)


def _parse_json(s: str) -> dict:
    s = re.sub(r"^```(?:json)?|```$", "", s.strip(), flags=re.M).strip()
    return json.loads(s)


def extract(rec: RawRecord) -> list[Listing]:
    key = hashlib.sha1(f"{rec.url}|{rec.title}|{rec.raw_text}".encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        resp = _client().chat.completions.create(
            model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": PROMPT.format(
                today=datetime.now().date(), hint=json.dumps(rec.hint), title=rec.title, url=rec.url,
                text=rec.raw_text)}],
            response_format={"type": "json_object"},
            temperature=0,
        )
        data = _parse_json(resp.choices[0].message.content)
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    now = datetime.now(timezone.utc).isoformat()
    out = []
    for d in data.get("listings", []):
        for k, v in rec.hint.items():  # scraper-known facts win over the LLM
            if k in Listing.model_fields and v:
                d[k] = v
        d["url"] = d.get("url") or rec.url
        d["source"] = rec.source
        d["raw_text"] = rec.raw_text
        d["scraped_at"] = now
        d = {k: v for k, v in d.items() if v is not None}
        try:
            out.append(Listing(**d).finalize())
        except ValidationError as e:
            print(f"extract: invalid listing from {rec.url}: {e.errors()[:2]}")
    return out
