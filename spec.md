# Spec: Personalized Scholarship & Opportunity Finder

> Working name: **TBD** (placeholder: "Scout"). Status: draft v0.1, 2026-10-23.

## 1. Problem

Scholarship sites like Bold.org, Fastweb, and Scholarships.com are bad at matching students to awards:

- **Shallow profiles.** They ask for GPA, state, and intended major, then return hundreds of generic results. A student who did varsity fencing, volunteered at a food bank, and placed at a state science fair gets the same list as everyone else in their state.
- **Noisy results.** Lists are padded with sweepstakes-style "no essay" scholarships, sponsored listings, and awards the student isn't eligible for.
- **Data harvesting.** Many sites exist mainly to collect student contact info for marketers.
- **Scholarships only.** They don't show the free or cheap opportunities that build a student's profile in the first place: hackathons, company office visits, career fairs, workshops, and summer programs.

## 2. Existing tools and our angle

| Product | What it does | Gap |
|---|---|---|
| Fastweb, Bold.org, Scholarships.com | Big national databases, simple filters | Generic matches; lots of manual filtering; lead-gen "no essay" awards |
| ScholarshipOwl | Matching + AI essay drafts | Paid; still matches on shallow profile fields |
| Scholly | Quick mobile matching | Reviewers call its filters basic |
| Going Merry | Matching + in-app applications | One source says it shut down in March 2026 (unconfirmed) |
| Niche, RaiseMe | College search; RaiseMe gives micro-scholarships for achievements | Tied to specific colleges; not a general finder |
| Extracurrify | Free AI "counselor" with ~250 curated activities + scholarships | Small curated list; not location-based or scraped |
| MLH, Devpost, blog roundups | Hackathon listings | Scattered; nothing aimed at "free things near me for a teen" |

**Our angle: niche scholarships.** The big sites compete on volume of national awards that thousands of students apply to. The money that's actually winnable is in **niche and local awards** with small applicant pools: a community foundation award for one county, a scholarship from a parent's union or employer, a state bowling association award, a heritage society award, a credit union's essay contest. These are hard to find because they live on small, scattered websites, which is exactly what a scraper plus LLM extraction can fix.

So the product's promise is: **"the scholarships nobody else applied for, because nobody else found them."** Every design decision should favor small applicant pools over big dollar amounts.

## 3. Goal

Let a student describe what they've actually done in plain keywords and get back:

1. **Scholarships** they are realistically eligible for, ranked by how well they fit, with the reason for each match.
2. **Discovery opportunities** near them (or online) that are free or low-cost and easy to apply to.

Success for the hackathon demo: a judge enters a realistic student profile and within seconds sees a short, clearly explained list that is visibly more relevant than what Fastweb returns for the same inputs.

## 4. Users

- **Primary:** high school juniors and seniors and college undergrads (roughly 16–22), especially first-generation and low-income students who don't have a counselor doing this for them.
- **Secondary:** counselors and mentors who want to find opportunities for a group of students.

## 5. Core features

### 5.1 Profile intake
- A fast, keyword-first form, not a 40-field survey. Chips and tags with autocomplete for:
  - Sports and athletics (e.g. "varsity soccer", "cross country captain")
  - Clubs and activities (e.g. "robotics", "debate", "school newspaper")
  - Volunteering, including organizations and causes (e.g. "food bank", "Habitat for Humanity", "tutoring")
  - Competitions and awards (e.g. "USACO Silver", "state science fair 2nd place")
  - Academics: GPA, test scores (optional), intended major(s), class year
  - Background (optional, clearly explained): location, school, first-gen status, financial need, heritage or identity groups, military family, disability, and so on. Many scholarships are restricted to these groups, so including them improves matches, but every one is opt-in.
  - **Connections** (optional; this is where niche awards hide): parent or guardian employers, unions, military branch, religious congregation, credit union or bank, Scouts / 4-H / FFA / Boys & Girls Club, fraternal orgs (Elks, Rotary, Lions, VFW), hobbies and odd skills (e.g. chess, bowling, duck calling, knitting), and county of residence.
- **Free-text "tell us about yourself"** box. An LLM extracts tags from it so users can paste a resume or activities list instead of typing tags.
- Profile is editable at any time, and matches update live.

### 5.2 Scholarship matching
- **Hard eligibility filters** remove anything the student can't win: location, class year, GPA minimum, citizenship or residency, major, school, and deadline not passed.
- **Relevance ranking** on what's left: how closely the scholarship's focus (sport, cause, field, identity, activity) matches the student's tags.
- **"Why you matched" explanation** on every card (e.g. *"Matches: varsity soccer, Ohio resident, intended engineering major"*).
- Each card shows amount, deadline, effort level (essay or no essay, recommendation letters needed), and a link to the source.
- Sort and filter by deadline, amount, effort, and local vs. national. Local scholarships are less competitive and are the biggest gap in existing sites.
- **Excludes junk by default:** sweepstakes and "no-essay" lead-generation awards are flagged or hidden.

### 5.3 Discovery opportunities
- Free or low-cost events near the user's location or online: hackathons, company visits and open houses, career fairs, info sessions, workshops, pre-college programs, and fellowships.
- Filters: distance or online, cost (free / under $X / travel stipend offered), date, type, and age eligibility.
- Matched to interests too, so a robotics kid sees a FIRST event or a hardware hackathon first.

### 5.4 Quick apply
- **One-click "apply" deep link** to the real application page.
- **Saved profile autofill helper:** a copyable summary (activities list, short bio) formatted for common application fields.
- **Essay reuse hints (stretch):** group scholarships by similar essay prompts so one essay can be adapted for several.
- **Tracker:** save, mark as applied or won, and get deadline reminders.

## 6. Data pipeline

### 6.1 Sources
Start with sources that are public and allowed to be scraped or that offer an API. **Do not scrape Bold.org or Fastweb**: their ToS forbid it and the data is the thing we're competing with.

| Type | Candidate sources |
|---|---|
| Scholarships | Community foundation sites (many cities have one with a local scholarship list), university financial aid "outside scholarships" pages, state higher-ed agency lists, corporate and professional association scholarship pages, CareerOneStop scholarship finder (U.S. Dept. of Labor) |
| Niche scholarships | Union and large-employer foundation pages, Rotary/Elks/Lions/VFW chapter sites, credit unions, hobby and sports governing bodies (e.g. state bowling, chess, and 4-H/FFA associations), heritage and cultural societies, local business and newspaper award pages, high school counseling office "local scholarships" PDFs |
| Hackathons | MLH season list, Devpost hackathon listings |
| Events | Eventbrite / Luma / Meetup (via APIs where available), company university-recruiting and events pages, local library and makerspace calendars |
| Programs | University pre-college and summer program pages, nonprofit program lists |

For the hackathon, a **seed dataset of ~200–500 scholarships and ~100 opportunities** from a handful of sources is enough. Plus a few hand-curated local entries for the demo city.

### 6.2 Scraper
- Python: `httpx` + `BeautifulSoup` for static pages, Playwright for JS-heavy ones.
- One small adapter per source that outputs raw records (title, URL, raw text, source).
- Respect `robots.txt`, rate-limit, and cache pages so we don't re-hit sites during development.
- Scheduled re-scrape (cron / GitHub Action) to catch new listings and drop expired ones.

### 6.3 Extraction and normalization
Raw scholarship pages are messy prose. An LLM pass turns each one into a structured record:

```json
{
  "title": "...",
  "provider": "...",
  "amount_min": 1000,
  "amount_max": 1000,
  "deadline": "2027-02-01",
  "url": "...",
  "eligibility": {
    "states": ["OH"],
    "class_years": ["HS senior"],
    "min_gpa": 3.0,
    "citizenship": ["US citizen", "permanent resident"],
    "majors": ["engineering"],
    "identity_groups": [],
    "need_based": false
  },
  "focus_tags": ["soccer", "community service"],
  "requirements": { "essay": true, "recommendations": 1, "transcript": true },
  "is_sweepstakes": false,
  "raw_text": "..."
}
```

Opportunities get a similar schema with `type`, `start_date`, `location`, `is_online`, `cost`, `travel_stipend`, `age_min`, and `focus_tags`.

Deduplicate by URL plus fuzzy title match, since the same scholarship appears on many lists.

## 7. Matching and ML

Three layers, simplest first, so we have something working early and can improve it:

1. **Rule-based eligibility filter** (must-have). Applies the structured `eligibility` fields against the profile. Unknown fields don't disqualify.
2. **Semantic relevance score.** Embed the student's tags and bio, and each scholarship's `focus_tags` plus description; rank by cosine similarity. This is what makes "fencing" match a "student-athlete in an Olympic sport" scholarship that a keyword search would miss.
   - Embeddings: an off-the-shelf embedding model (hosted API or `sentence-transformers`), stored in a vector index (pgvector, Chroma, or just numpy for the demo).
3. **Re-rank and explain (stretch / likely demo highlight).** Send the top ~30 candidates and the profile to an LLM to re-rank and write the one-line "why you matched" text. Cache results per profile.

Other ML ideas if time allows:
- **Sweepstakes / low-quality classifier** to flag lead-gen "scholarships."
- **Win-likelihood heuristic:** smaller applicant pool (local, niche, essay-required) scores higher.
- **Feedback loop:** saves, hides, and applies are used to tune ranking.

## 8. Architecture

```
[Scrapers (Python, scheduled)] --> [LLM extraction + dedupe] --> [Postgres + pgvector]
                                                                       |
[Web app (Next.js)] <--> [API (FastAPI or Next.js routes)] <-----------+
        |                         |
   profile intake           match: filter -> embed rank -> LLM rerank/explain
```

Proposed default stack (change freely):
- **Frontend:** Next.js + Tailwind
- **Backend:** FastAPI (Python, which keeps scraper, ML, and API in one language) or Next.js API routes if the team prefers JS end to end
- **DB:** Postgres with pgvector (Supabase gives this plus auth for free)
- **LLM / embeddings:** one hosted provider for extraction, embeddings, and rerank
- **Hosting:** Vercel (frontend) + Render / Fly / Railway (Python API and scraper jobs)

## 9. Privacy and safety

- Users may be minors. Collect the minimum, make all identity and background fields optional, and never sell or share data.
- Don't require an account to see matches; an account is only for saving and tracking.
- Label what each sensitive field is used for ("used only to find scholarships restricted to this group").
- Link out to official applications; we don't collect application materials or payment info.
- Flag listings that charge an application fee, which is a common scam signal.

## 10. Hackathon scope

**MVP (must ship for demo):**
- [ ] Profile intake with tag chips + free-text extraction
- [ ] Seed dataset: scraped and LLM-normalized scholarships + opportunities from 3–5 sources
- [ ] Eligibility filter + embedding ranking
- [ ] Results page with scholarship and opportunity tabs, "why you matched" text, deadline/amount/effort, apply link
- [ ] Location-based filter for opportunities

**Stretch:**
- [ ] LLM rerank
- [ ] Save/track + deadline reminders
- [ ] Essay-prompt clustering
- [ ] Sweepstakes classifier
- [ ] Map view of nearby opportunities
- [ ] Counselor view for multiple students

## 11. Demo script (draft)

1. Show Fastweb (or a screenshot) for a sample student: long generic list.
2. Enter the same student in our app with real activities: fencing, food bank volunteer, robotics, 3.7 GPA, first-gen, Columbus OH.
3. Show a short ranked list with local scholarships at the top and clear "why you matched" text.
4. Switch to Opportunities: a free hackathon and a company open house nearby this month, each one click to apply.
5. Quick look at the pipeline: raw scraped page → structured record.

## 12. Open questions

- Team split: who owns scraper, ML/matching, backend, frontend?
- U.S.-only to start? Which demo city for local data?
- Python backend or all-JS?
- Which LLM / embedding provider (and whose API credits)?
- Name and branding.
- Do we need accounts at all for the demo, or just local storage?
