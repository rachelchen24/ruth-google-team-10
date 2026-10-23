# Spec: Personalized Scholarship & Opportunity Finder

> Working name: **TBD** (placeholder: "Scout"). Status: draft v0.4, 2026-10-23.

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

**Second angle, and the key differentiator: free discovery opportunities.** No scholarship finder shows free or low-cost things a student can just apply to and attend. Examples: a university's free women-in-STEM day (e.g. a Caltech WiSTEM-style event), local hackathons, company office visits and open houses, company-run events, and company competitions. These are often free, need only a short application, and are exactly what builds the record that wins scholarships later. Today students find them only by word of mouth.

## 3. Goal

Let a student paste something they've already written (a personal statement, resume, or past application), answer a handful of questions, and get back:

1. **Scholarships** they are realistically eligible for, ranked by how well they fit, with the reason for each match.
2. **Discovery opportunities** near them (or online) that are free or low-cost and easy to apply to.

Success for the hackathon demo: a judge enters a realistic student profile and within seconds sees a short, clearly explained list that is visibly more relevant than what Fastweb returns for the same inputs.

## 4. Users

- **Primary:** both high school students and college undergrads (roughly 14–22). The profile asks for school level, and both scholarships and opportunities are filtered by it. Focus especially on first-generation and low-income students who don't have a counselor doing this for them.
- **Secondary:** counselors and mentors who want to find opportunities for a group of students.

## 5. Core features

### 5.1 Profile intake: "paste, don't fill out"
**Principle: ask as few questions as possible, and make almost everything optional.** Other sites make students fill out 50+ required fields before showing a single result. We read what they've already written and ask only for what's missing.
- **Required:** only what we can't match without (ZIP and school level/grade). Everything else is optional.
- **Lots of optional fields, never in the way:** GPA, test scores, citizenship, background checklist, connections, intended major, and so on. They live in an "improve your matches" panel the student can open any time, not in the onboarding flow.
- Results show right after the required questions. Each optional field shows what it unlocks (*"Add GPA: +12 matches"*), so filling more in is a choice, not a gate.

**Step 1 (optional): paste or upload one thing they already have** (any of). Nothing here is required, including a resume:
- Personal statement or college essay
- Resume or activities list (e.g. a Common App activities section)
- A past scholarship or program application
- LinkedIn profile PDF, or just a few sentences about themselves

**Step 2: LLM extraction.** One LLM call pulls a structured profile out of the text:
- Activities, sports, clubs, leadership roles
- Volunteering (organizations and causes)
- Competitions, awards, and honors
- Academic interests and intended major
- Background details the student chose to share (first-gen, heritage, family circumstances, challenges overcome)
- Connections where niche awards hide (parent's job or union, church, Scouts / 4-H / FFA, hobbies)
- Writing themes, useful later for matching essay prompts

**Step 3: confirm, don't type.** Show the extracted profile as editable chips: *"Here's what we picked up: robotics captain, food bank volunteer, first-gen, interested in mechanical engineering. Anything wrong or missing?"* The student removes or adds chips with one click.

**Step 4: ask only the gaps (target 3–5 questions max)**, skipping any the document already answered:
1. ZIP code (required; for local scholarships and nearby events)
2. School level and grade (required; HS 9–12 / college year)
3. GPA (optional; a range is fine)
4. Optional and skippable: citizenship/residency, and an "any of these apply?" checklist (first-gen, military family, financial need, etc.), since these hard-filter lots of awards

**No document?** That's fine and fully supported. Fall back to a quick chip picker with autocomplete (sports, clubs, volunteering, awards), plus the same gap questions.

**Privacy:** the raw document is processed and discarded by default; we store only the extracted chips unless the student opts in to saving it (e.g. for essay reuse). Every sensitive field stays optional and is labeled with why we ask.

The profile is editable at any time and matches update live. Students can paste more documents later to enrich it.

### 5.2 Scholarship matching
- **Hard eligibility filters** remove anything the student can't win: location, class year, GPA minimum, citizenship or residency, major, school, and deadline not passed.
- **Relevance ranking** on what's left: how closely the scholarship's focus (sport, cause, field, identity, activity) matches the student's tags.
- **Match % on every card** (e.g. *"88% match"*). This is a **profile-fit score**, not a chance of winning: it combines how many eligibility criteria are confirmed met and how closely the student's tags match the scholarship's focus (see §7). It needs no training data, so it's in MVP scope.
- **Estimated odds (prototype):** e.g. *"Est. odds: ~1 in 12 (high)."* A rough heuristic, clearly labeled as an estimate, shown next to match %. A real trained model comes later once we have outcome data; see §7.2.
- **"Why you matched" explanation** on every card (e.g. *"Matches: varsity soccer, Ohio resident, intended engineering major"*).
- Each card shows amount, deadline, effort level (essay or no essay, recommendation letters needed), and a link to the source.
- Sort and filter by deadline, amount, effort, and local vs. national. Local scholarships are less competitive and are the biggest gap in existing sites.
- **Excludes junk by default:** sweepstakes and "no-essay" lead-generation awards are flagged or hidden.

### 5.3 Discovery opportunities (key differentiator)
This is a first-class tab, equal to scholarships, not an add-on.

- **What counts:** free or low-cost things a student can apply to and attend, in person nearby or online:
  - University outreach events (e.g. women-in-STEM days like Caltech WiSTEM, engineering open houses, diversity preview weekends)
  - Hackathons (local, school-run, and MLH-style)
  - Company office visits, open houses, and "day in the life" tours
  - Company events: info sessions, workshops, student summits, conferences with free student passes
  - Company and org competitions: coding, case, design, pitch, essay, science, and math contests
  - Pre-college and summer programs that are free or have full aid, plus fellowships and short paid programs
- **Cost and access are front and center.** Each card shows: cost (free / $ amount), whether travel, food, or lodging is covered, how to apply (short form, essay, teacher rec, first-come), application deadline, and event date.
- Filters: distance or online, cost, date, type, school level (HS / college), and eligibility (age, gender, grade, location).
- **Same match % and "why you matched"** as scholarships, so a robotics student sees a hardware hackathon or a company's robotics competition first.
- **Apply fast:** link straight to the application, with the profile summary ready to paste.
- **Connects to scholarships:** attending some of these (competitions, programs) makes a student eligible for or more competitive for scholarships. See "almost eligible" matches in §12.

### 5.4 Quick apply
- **One-click "apply" deep link** to the real application page.
- **Saved profile autofill helper:** a copyable summary (activities list, short bio) formatted for common application fields.
- **Essay reuse hints (stretch):** group scholarships by similar essay prompts so one essay can be adapted for several.
- **Tracker:** save, mark as applied or won, and get deadline reminders.

### 5.5 Goals and progress
Students set a goal and see a progress bar, so applying feels like a plan rather than an endless list.

**Goal setup (one screen, all optional):**
- **Money goal:** "$____ by ____" (a date, or "in N weeks / months"). E.g. *$5,000 by May 1*.
- **Weekly application goal:** "Apply to __ scholarships and __ opportunities per week."

**Progress display:**
- **Money bar:** amount won so far vs. goal, with a lighter segment for **pending** (applied, waiting to hear). Optionally a third segment for **expected value of pending** (sum of amount × estimated odds), which shows whether the student is applying to enough to realistically hit the goal.
- **Weekly bar:** applications submitted this week vs. weekly goal, with a streak counter for weeks the goal was met.
- **Pace check:** *"To reach $5,000 by May 1 at your current odds, apply to ~4 scholarships a week. You're at 2."* Uses the estimated odds from §7.2.
- **This week's picks:** the top N matches, with deadlines soonest first, where N is the weekly goal. One click to apply, then one click to mark as applied.

**Tracking statuses:** saved → applied → won / not selected, plus attended for opportunities. Marking won asks for the amount (defaults to the listed amount). These outcomes are also the training data for the real odds model (§7.2), so collecting them from day one matters.

Reminders (email or browser notification) for upcoming deadlines and when a student is behind their weekly goal.

## 6. Data pipeline

### 6.1 Sources
Start with sources that are public and allowed to be scraped or that offer an API. **Do not scrape Bold.org or Fastweb**: their ToS forbid it and the data is the thing we're competing with.

| Type | Candidate sources |
|---|---|
| Scholarships | Community foundation sites (many cities have one with a local scholarship list), university financial aid "outside scholarships" pages, state higher-ed agency lists, corporate and professional association scholarship pages, CareerOneStop scholarship finder (U.S. Dept. of Labor) |
| Niche scholarships | Union and large-employer foundation pages, Rotary/Elks/Lions/VFW chapter sites, credit unions, hobby and sports governing bodies (e.g. state bowling, chess, and 4-H/FFA associations), heritage and cultural societies, local business and newspaper award pages, high school counseling office "local scholarships" PDFs |
| Hackathons | MLH season list, Devpost hackathon listings |
| University outreach | University outreach, women-in-STEM, diversity, and admissions event pages (engineering schools, research institutes), department "K-12 outreach" pages |
| Company visits, events, competitions | Company university-recruiting, student-programs, and events pages; company-run student competitions; Eventbrite / Luma / Meetup (via APIs where available) filtered to free student events |
| Local events | Library, makerspace, museum, and community college calendars |
| Programs | University pre-college and summer program pages (free or full-aid only), nonprofit program lists |

**What's actually available (researched 2026-10-23):**

| Source | Access | What we get | Notes |
|---|---|---|---|
| CareerOneStop Scholarship Finder (U.S. Dept. of Labor) | Free web API, needs a registered token | ~9,500 scholarships, fellowships, grants, prizes: name, provider, summary, level of study, amount, deadline month | Best structured base for national data. Request a token on day 1, since approval may not be instant. Mostly national, light on local awards. |
| Pathways to Science (Institute for Broadening Participation) | Website (scrape politely or ask for data) | ~1,200–1,500 STEM programs, HS through grad, filterable by level, location, funding | Not all free; filter on funding. Good for programs and outreach events. |
| NSF REU sites directory | Public NSF site | Paid summer research for undergrads | College only; U.S. citizens / permanent residents. |
| Devpost | No official API; site uses an internal JSON endpoint | Hackathons: title, dates, location/online, prizes, themes | Unofficial and may change; find the endpoint in browser devtools. |
| MLH | No API; scrape the season page | Student hackathons | Small, easy to scrape. |
| Eventbrite | Public search API removed in 2020 | Only events by a known org, venue, or ID | Can't search "free student events near X." Use org/venue lookups for known hosts (universities, companies) instead. |
| University outreach, company events, community foundations, counseling office lists | Scrape individual pages | The niche and local data that is our differentiator | No aggregate exists; this is the hand-picked + scraper + LLM-extraction work. |
| Bold.org, College Board BigFuture, Fastweb | Third-party scrapers exist (e.g. on Apify) | Thousands of listings | **Don't use**: likely against their ToS, and it's the competitor's data. |

**Outcome data (who applied, who won):** no public dataset exists. The closest are survey reports (e.g. Sallie's survey of ~500 applicants) and occasional program evaluations. This confirms the chance-of-winning model (§7.2) needs data we would have to collect ourselves.

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

Opportunities get a similar schema with `type` (outreach event, hackathon, company visit, company event, competition, program), `host_org`, `start_date`, `application_deadline`, `location`, `is_online`, `cost`, `covers` (travel / food / lodging), `apply_effort` (short form, essay, rec, first-come), `school_levels` (HS / college), eligibility (age, grade, gender, location), and `focus_tags`.

Deduplicate by URL plus fuzzy title match, since the same scholarship appears on many lists.

## 7. Matching and ML

Three layers, simplest first, so we have something working early and can improve it:

1. **Rule-based eligibility filter** (must-have). Applies the structured `eligibility` fields against the profile. Unknown fields don't disqualify.
2. **Semantic relevance score.** Embed the student's tags and bio, and each scholarship's `focus_tags` plus description; rank by cosine similarity. This is what makes "fencing" match a "student-athlete in an Olympic sport" scholarship that a keyword search would miss.
   - Embeddings: an off-the-shelf embedding model (hosted API or `sentence-transformers`), stored in a vector index (pgvector, Chroma, or just numpy for the demo).
3. **Re-rank and explain (stretch / likely demo highlight).** Send the top ~30 candidates and the profile to an LLM to re-rank and write the one-line "why you matched" text. Cache results per profile.

### 7.1 Match % (MVP)
The percentage on each card, for both scholarships and opportunities. No training needed:

```
match % = 100 × (w1 × eligibility_confidence + w2 × relevance)
```

- `eligibility_confidence`: share of the listing's eligibility criteria the profile is confirmed to meet. Unknowns count as partial, not zero.
- `relevance`: embedding similarity between profile and listing, rescaled to 0–1 across the candidate set.
- Start with `w1 = 0.4, w2 = 0.6` and tune by eye on test profiles. Label it **"match"**, never "chance of winning."

### 7.2 Odds of getting it

We don't yet know how much outcome data we can get (no public applicant/winner dataset exists, see §6.1), so this is built in two stages behind the same interface, `estimate_odds(profile, listing) -> {p, low, high, label, reasons}`. The UI doesn't care which stage is behind it.

**Stage 1: model trained on synthetic data (hackathon prototype).** We have real listings but no real outcomes, so we simulate application rounds, then train a real model on the simulated outcomes. This proves the full ML pipeline (features → training → calibrated odds → UI) works, so swapping in real data later is a data change, not a rebuild.

*Step 1: simulation assumptions.* These encode what we believe drives odds, and they are the generator, not the model:
- `est_applicants` per listing, from how narrow eligibility is. Start from a pool size by geographic scope (e.g. national ~5,000, state ~800, county or one school ~40), then shrink it for each extra restriction (specific activity, major, identity group, GPA floor). Use the provider's published applicant count when the listing has one.
- `num_awards` per listing, extracted from the listing (default 1).
- Effort: essay, recs, or interview required → fewer applicants finish; "no essay" → huge pools.
- For opportunities: capacity (seats) if listed; first-come / no-selection events let nearly everyone who applies in time get in.

*Step 2: generate synthetic applicants.*
- Create a few thousand synthetic student profiles by sampling realistic distributions: grade, GPA, state/county, number and type of activities, leadership roles, awards, first-gen, and so on. For variety, also have an LLM write ~100–200 short persona descriptions, then run them through the same extraction as real intake (§5.1), which also tests that pipeline.
- For each real listing, draw an applicant pool of size `est_applicants` from the synthetic students who are eligible.

*Step 3: simulate who wins.*
- Give each applicant a hidden "strength" score for that listing: match % (§7.1) + GPA + leadership/awards + essay quality (random, since we can't see it) + noise.
- The top `num_awards` applicants by strength win. Everyone else in the pool is "not selected."
- Output: a table of (student features, listing features, won 0/1), probably 100k+ rows.

*Step 4: train and calibrate.*
- Features: match %, eligibility confidence, est. pool size, num_awards, effort level, scope (local / state / national), GPA, activity and award counts, leadership flag.
- Model: logistic regression first (explainable), then try gradient-boosted trees (e.g. LightGBM / XGBoost) if time allows.
- Hold out a test split; report AUC and a calibration plot. Calibrate with isotonic or Platt scaling.
- Use feature importances or SHAP to generate the "why" text: *"Your odds are good mainly because this is county-only and you match its robotics focus."*

*Honesty note:* a model trained on synthetic data can only learn the assumptions we put into the simulator. It shows that the pipeline works, not that the numbers are true. The UI and pitch both say so ("prototype estimate, trained on simulated data").

*Fallback:* the Step 1 assumptions also work on their own as a direct formula (`p ≈ num_awards / est_applicants × fit adjustment`) if training isn't ready in time.

**Display:** never a precise-looking "87%". Show a band plus a plain-language range: *"Est. odds: High (~1 in 8)"* with a tooltip *"Rough estimate based on how many people are likely eligible and how well you fit. Not a guarantee."* Labels: Long shot / Fair / Good / High.

**Validation for the demo:** hand-check 10–20 listings where the provider publishes applicant counts or past winner counts, and sanity-check that the simulated pool sizes and odds are in the right ballpark.

**Stage 2: same model, real data (after launch).** Once users report outcomes (§5.5 tracker: applied → won / not selected):
- Training data: (profile features, listing features, outcome) per application. Supplement with partner providers or counselors who share applicant counts and results.
- Same features and training code as Stage 1. Options: retrain on real data only, or pretrain on synthetic data and fine-tune / reweight toward real outcomes as they come in.
- Compare real outcomes against the simulator to find which assumptions were wrong, and fix the simulator too.
- Calibrate (e.g. isotonic or Platt scaling) so "1 in 8" really means about 1 in 8 across similar applications.
- Switch from Stage 1 to Stage 2 per listing type only once there's enough data for that type; otherwise keep the synthetic-trained model.

**How much data is enough?** Unknown yet; that's the open question. Rough guide: a few hundred labeled outcomes for a coarse model, thousands for anything per-category. Until then, the synthetic-trained Stage 1 model stays on, and the pitch presents Stage 2 as the roadmap.

### 7.3 Other ML ideas if time allows
- **Sweepstakes / low-quality classifier** to flag lead-gen "scholarships."
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
- [ ] Paste/upload intake: LLM extracts profile → confirm chips → 3–5 gap questions
- [ ] Odds model, Stage 1: simulate applicants and outcomes, train and calibrate on synthetic data (§7.2), shown as a labeled band
- [ ] Goal setup + money and weekly progress bars, with the applied/won tracker
- [ ] Seed dataset: scraped and LLM-normalized scholarships + opportunities from 3–5 sources each, with a strong set of free outreach events, hackathons, company visits, and competitions for the demo area
- [ ] Eligibility filter + embedding ranking + match %
- [ ] Results page with scholarship and opportunity tabs, match %, "why you matched" text, deadline/amount/effort (or cost/what's covered), apply link
- [ ] Location and cost filters for opportunities
- [ ] HS / college toggle

**Stretch:**
- [ ] LLM rerank
- [ ] Deadline and behind-on-goal reminders
- [ ] Essay-prompt clustering
- [ ] Sweepstakes classifier
- [ ] Map view of nearby opportunities
- [ ] Counselor view for multiple students

**Future (pitch as roadmap):**
- [ ] Stage 2: retrain the odds model on real reported outcomes (§7.2)

## 11. Demo script (draft)

1. Show Fastweb (or a screenshot) for a sample student: long generic list.
2. Paste the same student's personal statement into our app. In seconds it shows extracted chips (fencing, food bank volunteer, robotics captain, first-gen) and asks only ZIP, grade, and GPA.
3. Show a short ranked list with match %, estimated odds, and local scholarships at the top, with clear "why you matched" text.
4. **Switch to Opportunities (the big moment):** a free university women-in-STEM day, a local hackathon, and a company office visit nearby this month, each marked free, with what's covered, and one click to apply. Point out that no scholarship site shows these.
5. Quick look at the pipeline: raw scraped page → structured record, and the odds model's calibration plot and top features (trained on simulated data).
6. Set a goal ("$5,000 by May 1, 3 applications a week"), mark two as applied, and watch the progress bars and pace check update.
7. Close with the roadmap: the same model retrains on real outcomes as students report them.

## 12. Ideas backlog / future improvements
Not committed; pull into scope as time allows.
- **Voice intake:** the student talks about themselves instead of typing ("I do robotics, I volunteer at the food bank on weekends…"). Speech-to-text, then the same LLM extraction as a pasted document (§5.1). Also usable for adding to the profile later. Optional, like every other input.
- **Resume upload (optional, never required):** if it's not in the first version, add PDF/DOCX resume upload that feeds the same extraction. Students without a resume skip it with no penalty.
- **Rank by expected value:** amount × estimated odds ÷ effort, using applicant-pool size.
- **"Almost eligible" matches:** "join FFA or attend this competition and you'd qualify for 3 more scholarships." Links the opportunities tab to scholarships.
- **Interview-style intake:** a short chat that asks follow-ups to surface niche connections (parent's employer or union, specific volunteer org).
- **Counselor PDF upload:** parse a school's local scholarship list into structured records.
- **Student-submitted listings:** students add scholarships and events they found or won.
- **Predict reopening of yearly awards and events:** "opened in January last year; we'll remind you."
- **Essay prompt clustering** and **calendar (.ics) export.**
- **Scam flags:** application fees, SSN requests, lead-gen "no essay" awards.

## 13. Open questions

- Team split: who owns scraper, ML/matching, backend, frontend?
- U.S.-only to start? Which demo city for local data?
- Python backend or all-JS?
- Which LLM / embedding provider (and whose API credits)?
- Name and branding.
- Do we need accounts at all for the demo, or just local storage?
- How do we tell HS vs. college eligibility apart when a listing doesn't say?
- How much outcome data can we get for the odds model, and from where (user reports, partner providers, counselors)?
- Which document types do we support at launch (paste text only, or PDF/DOCX upload too)?
