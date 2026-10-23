# Rachel – data/scrapers progress

## Use this now
- **Schema:** [scrapers/schema.py](scrapers/schema.py) has `Listing`. Scholarships and opportunities use one model, told apart by `kind`. Null or `[]` means unknown, and unknown should never disqualify.
- **Mock data (20):** [data/sample_listings.json](data/sample_listings.json). It has 12 **fake** scholarships/opps (`source: "sample"`, "(FAKE)" in provider, example.org URLs) covering every type, plus 8 real hackathons. One sweepstakes example is included.
- **Real data (233):** [data/listings.json](data/listings.json). These are all hackathons for now: 70 from MLH and 163 from Devpost.

## Status
| Source | State |
|---|---|
| MLH | ✅ done, 70 |
| Devpost | ✅ done, 163 (invite-only dropped) |
| Pathways to Science | 🟡 105 program pages scraped; waiting on LLM key to extract |
| CareerOneStop | 🟡 adapter written; **need token** (env `COS_USER_ID`, `COS_TOKEN`) |
| Hand-picked local pages | 🟡 pipeline ready, list empty. Waiting on **demo city** |
| LLM extraction | 🟡 written + tested with a mocked response; no key yet |
| Dedupe + drop expired | ✅ |

## Run
```
pip install -r requirements.txt
py -m scrapers.run --sources mlh devpost      # no key needed
py -m scrapers.run --limit 20                 # everything, cap LLM calls per source
```
LLM env vars: `LLM_API_KEY`, `LLM_MODEL`, and `LLM_BASE_URL` (OpenAI-compatible, so Gemini/OpenAI/etc. all work). LLM calls and fetched pages are cached in `data/cache/` (gitignored).

To add a local page, append `{"url": ..., "kind": "scholarship"|"opportunity"}` to [data/sources.json](data/sources.json). Manual entries go in `data/manual_listings.json` (same schema).

## Blocked on / need from team
1. **Which LLM provider + key?**
2. **Demo city** (for hand-picked local scholarships + events)
3. CareerOneStop token (requested? who?)

## Notes for consumers
- Hackathon `school_levels`: MLH is `["college"]` unless the name says high school, and Devpost is `[]` (unknown).
- `published_applicants` is set when known (Devpost = registrations). Odds model can use it.
- `id` is a stable 12-char hash of url+title.
