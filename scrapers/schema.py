"""Listing schema (spec §6.3). One model for both scholarships and opportunities; `kind` tells them apart.

Persons 3/4/5 consume this. Unknown = null / empty list, and unknown never disqualifies (§7).
"""
from __future__ import annotations

import hashlib
from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field

Kind = Literal["scholarship", "opportunity"]
OppType = Literal["outreach_event", "hackathon", "company_visit", "company_event", "competition", "program"]
SchoolLevel = Literal["HS", "college"]
Scope = Literal["local", "state", "national", "online"]


class Eligibility(BaseModel):
    states: list[str] = []            # 2-letter codes; empty = anywhere
    counties: list[str] = []          # e.g. "Santa Clara County, CA"
    class_years: list[str] = []       # "HS 9".."HS 12", "college 1".."college 4"
    min_gpa: Optional[float] = None
    citizenship: list[str] = []       # "US citizen", "permanent resident", "DACA", ...
    majors: list[str] = []
    identity_groups: list[str] = []   # "first-gen", "women", "Hispanic/Latino", "military family", ...
    need_based: Optional[bool] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    gender: list[str] = []


class Requirements(BaseModel):
    essay: Optional[bool] = None
    recommendations: Optional[int] = None
    transcript: Optional[bool] = None
    interview: Optional[bool] = None
    application_fee: Optional[float] = None   # scam signal (§9)


class Location(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class Listing(BaseModel):
    id: str = ""                      # stable hash of url+title, filled by finalize()
    kind: Kind
    title: str
    provider: Optional[str] = None    # scholarship sponsor or opportunity host_org
    url: str
    source: str                       # adapter name: "mlh", "devpost", "pathways", "careeronestop", "manual", ...
    summary: Optional[str] = None     # 1-3 sentences, for cards + embeddings
    school_levels: list[SchoolLevel] = []
    scope: Optional[Scope] = None
    eligibility: Eligibility = Field(default_factory=Eligibility)
    focus_tags: list[str] = []        # lowercase, e.g. ["robotics", "community service"]

    # scholarship fields
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    num_awards: Optional[int] = None
    deadline: Optional[date] = None
    requirements: Requirements = Field(default_factory=Requirements)
    is_sweepstakes: bool = False

    # opportunity fields
    type: Optional[OppType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    application_deadline: Optional[date] = None
    location: Optional[Location] = None
    is_online: Optional[bool] = None
    cost: Optional[float] = None      # 0 = free
    covers: list[Literal["travel", "food", "lodging", "stipend"]] = []
    apply_effort: list[Literal["short_form", "essay", "rec", "first_come", "interview"]] = []
    capacity: Optional[int] = None

    # odds-model hints (§7.2)
    published_applicants: Optional[int] = None

    raw_text: Optional[str] = None
    scraped_at: Optional[str] = None

    def finalize(self) -> "Listing":
        if not self.id:
            self.id = hashlib.sha1(f"{self.url}|{self.title}".encode()).hexdigest()[:12]
        self.focus_tags = sorted({t.strip().lower() for t in self.focus_tags if t.strip()})
        return self


class RawRecord(BaseModel):
    """What an adapter emits before LLM extraction (§6.2)."""
    source: str
    url: str
    title: str
    raw_text: str
    hint: dict = {}   # anything structured the adapter already knows (kind, type, dates...)
