# Rachel – data/scrapers progress

## Use this now
- **Schema:** [scrapers/schema.py](scrapers/schema.py) has `Listing`. Scholarships and opportunities use one model, told apart by `kind`. Null or `[]` means unknown, and unknown should never disqualify.
- **Mock data (20):** [data/sample_listings.json](data/sample_listings.json). It has 12 **fake** scholarships/opps (`source: "sample"`, "(FAKE)" in provider, example.org URLs) covering every type, plus 8 real hackathons. One sweepstakes example is included.
- **Real data (319):** [data/listings.json](data/listings.json). These are all opportunities so far, no scholarships yet: 70 MLH hackathons, 163 Devpost hackathons, and 86 Pathways STEM programs.
- **Distance (Person 3):** [scrapers/geo.py](scrapers/geo.py) has `zip_to_latlng(zip)` and `distance_miles(a, b)`. In-person listings have `location.lat/lng` when we could find them. It runs offline from Census data in `data/geo/`.

## Status
| Source | State |
|---|---|
| MLH | ✅ 70 |
| Devpost | ✅ 163 (invite-only dropped) |
| Pathways to Science | ✅ 86 parsed without the LLM: 64 HS, 43 free/paid. Dates and eligibility details wait for the LLM pass |
| CareerOneStop | 🟡 adapter written; **need token** (env `COS_USER_ID`, `COS_TOKEN`) |
| Hand-picked local pages | 🟡 pipeline ready, list empty. Waiting on **demo city** |
| LLM extraction | 🟡 written + tested with a mocked response; no key yet |
| Dedupe, drop expired, coordinates | ✅ |

**Coordinate coverage:** Pathways 78/86, MLH 36/70 (most misses are outside the US), Devpost 7/88 in-person (its locations are venue names like "Palace of Fine Arts").

## Run
```
pip install -r requirements.txt
py -m scrapers.run --sources mlh devpost pathways   # no key needed
py -m scrapers.run --limit 20                       # everything, cap LLM calls per source
```
LLM env vars: `LLM_API_KEY`, `LLM_MODEL`, and `LLM_BASE_URL` (OpenAI-compatible, so Gemini/OpenAI/etc. all work). With a key set, Pathways switches to full LLM extraction automatically. LLM calls and fetched pages are cached in `data/cache/` (gitignored).

To add a local page, append `{"url": ..., "kind": "scholarship"|"opportunity"}` to [data/sources.json](data/sources.json). Manual entries go in `data/manual_listings.json` (same schema).

## Blocked on / need from team
1. **Which LLM provider + key?**
2. **Demo city** (for hand-picked local scholarships + events)
3. CareerOneStop token (requested? who?)

## Notes for consumers
- Hackathon `school_levels`: MLH is `["college"]` unless the name says high school, and Devpost is `[]` (unknown).
- Pathways `cost: 0` is a keyword guess ("free", "stipend", "paid internship"...). Null means we don't know the cost, not that it isn't free.
- `published_applicants` is set when known (Devpost = registrations). Odds model can use it.
- `id` is a stable 12-char hash of url+title.
