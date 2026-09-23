# The Unofficial Guide

Luming Fei — corpus: `campus_life`.

Picked `campus_life` for unit 1 to get the pipeline working end to end
without fighting messy chunk boundaries first. Planning to revisit with
`advice_threads` or `city_guides` later as a harder follow-up.

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

This is a retrieval-augmented question-answering system built on
`campus_life`, a corpus of 88 short posts about student life at a
university — dining halls, dorms, courses, and administrative rules. Ask it
something like "how long is the wait at Kestrel Commons during lunch?" or
"is CS 210 a heavy workload?" and it retrieves the relevant post(s), answers
using only that text, and names the source file. Ask it something the
corpus doesn't cover — like a World Cup result or a Rust syntax question —
and it says so instead of guessing.

## Chunking Strategy

**Chunk size:** no fixed size — paragraph-based, merged until each chunk
reaches at least 100 characters.
**Overlap:** none.

The starter's 800-character fixed window never splits campus_life at all
(88 documents in, 88 chunks out) because almost no post reaches 800
characters. That's not wrong, but it's not right either — some posts hold
several unrelated facts in one document. `housing_morrow_house.txt`, for
example, has a building-history paragraph, a "the good" paragraph, a "the
bad" paragraph, and a laundry/noise paragraph, all under one title. One
fixed chunk mixes all four; a question about laundry cost would retrieve a
chunk that's mostly about damp floors and cheap rent.

So `split_documents` (chunker.py) splits on blank-line paragraph breaks
instead, then merges consecutive paragraphs — starting from the title line
— until the running total passes 100 characters, so no chunk is a bare
title fragment. Result: 88 documents become 143 chunks, averaging 194
characters (shortest 100, longest 409). Morrow House now comes out as two
chunks instead of one — building info in the first, the good/bad/laundry
facts grouped in the second — which is closer to how a person would
actually look something up in it.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_cs_340.txt#0` — produced by: `chunker.py::split_documents`

```
CS 340 Databases

I'm a junior and I've done this twice now. Format is lecture twice a week plus a project that runs the whole term. Assessment: one midterm and a final, both open-book. Lightly curved, usually two or three points.
```

**Chunk 3** — source: `course_phys_130_exams.txt#0` — produced by: `chunker.py::split_documents`

```
PHYS 130 Mechanics — assessment

Three midterms, no final, plus a lab practical. Not curved, but the lowest midterm is dropped.

The lab practical is worth 20% and almost nobody prepares for it.
```

**Chunk 4** — source: `dining_verrill_street_grill_followup.txt#1` — produced by: `chunker.py::split_documents`

```
Also worth saying: one register, so the queue is a single line no matter how busy. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_morrow_house.txt#1` — produced by: `chunker.py::split_documents`

```
The good: cheapest housing tier by about $900 a year, and the singles are real singles.

The bad: known damp problem on the ground floor; two rooms were taken offline in 2024.
```

## Sample Answer

**Question:** How many hours a week does CS 210 take outside of class?

**Answer:**

```
CS 210 takes 8 to 10 hours a week outside of class (source: course_cs_210_workload.txt).

Sources retrieved: course_cs_210_workload.txt, course_econ_101.txt, course_stat_150.txt, course_stat_150_workload.txt, money_jobs.txt
```

**My relevance cutoff:** 0.6 (the starter default — kept as-is)

Ran all 6 test questions and all 5 `OUT_OF_SCOPE` questions through
`python app.py retrieve` and recorded the best distance for each. The two
groups don't just have a gap, they're nowhere near each other: every
in-corpus question lands under 0.38, every out-of-scope question lands over
0.80. The starter's default cutoff of 0.6 sits comfortably in that empty
middle, and moving it up or down within roughly 0.4-0.75 wouldn't change a
single verdict on these 11 questions — so I kept it rather than tuning a
number that isn't doing any close calls yet.

| Question | In corpus? | Best distance |
|---|---|---|
| How long is the wait at Kestrel Commons during the lunch rush? | Yes | 0.198 |
| How late is it noisy in Morrow House on weekends, and are there enforced quiet hours? | Yes | 0.146 |
| How many hours a week does CS 210 take outside of class? | Yes | 0.269 |
| How often does the campus shuttle run on weekends? | Yes | 0.180 |
| What should I know about Kestrel Commons before going for lunch? | Yes | 0.376 |
| What time does Halden Hall close, and is that easy to miss? | Yes | 0.347 |
| What is the capital of Mongolia? | No | 0.825 |
| How do I change the oil in a diesel engine? | No | 0.923 |
| Who won the 1994 World Cup? | No | 0.874 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.803 |
| How do I write a for loop in Rust? | No | 0.877 |

## How I Used AI

**1.** Environment setup crashed with two unrelated build errors:
`chroma-hnswlib` and `cryptography` both failed to compile from source under
Python 3.13 on my Intel Mac. I had Claude dig into why, and it found that
neither package ships a prebuilt wheel for cp313 on this platform (and the
latest `cryptography` had dropped Intel-Mac wheels entirely). It installed
Python 3.12 via `uv` and pinned `cryptography==45.0.7` to a version that
still has an x86_64 wheel. Then `python app.py index` crashed separately —
onnxruntime's CoreML execution provider errored out mid-batch. Claude traced
that to `store.py::_embedder` defaulting to whatever providers were
available, and forced `CPUExecutionProvider` explicitly. I didn't touch this
code myself; I read the diagnosis, understood why it happened, and verified
`index`/`ask` both ran cleanly afterward.

**2.** For Milestone 3 I asked Claude to design and implement a chunker for
`campus_life` in `chunker.py`. Instead of guessing a chunk size, it measured
paragraph lengths across the corpus first (title lines are consistently
10-47 characters, and everything else is longer), and used that to justify
merging paragraphs forward until each chunk passes 100 characters — so the
title never ends up as a lone fragment. I checked the five sample chunks it
printed against the "could someone answer a question from just this"
standard from the milestone myself before accepting it, and re-ran all five
test questions to confirm retrieval still found the right documents after
the change.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

`scorer.py::judge` scores each answer with `rapidfuzz.fuzz.partial_ratio`
against its `expects` phrase (threshold 85, both strings whitespace-stripped
first). Diagnosis behind that design: an early version without whitespace
stripping scored "closes at 7:00pm" (correct) at 83.3 against `expects =
"7:00pm"` — a `fail` — for the same reason it would score "closes at
8:00pm" (a wrong digit) at the same 83.3. Both are edit-distance 1 over a
6-character string, so raw partial_ratio can't tell a formatting difference
from a factual one. Stripping whitespace from both sides before comparing
fixed the false negative (spaced "7:00 pm" now scores 100) without moving
the wrong-digit case, which stays at 83.3 and correctly stays below
threshold.

Criteria 3, 4, and 5 are single deterministic measurements (retrieval and
the gate don't change between runs on unchanged code), so the same number
is repeated across all three run columns rather than re-measured three
times — same reasoning the starter gives for criterion 3.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 5 of 6 | 6/6 | 6/6 | 6/6 | MET |
| 2. Every answer names a source | 6 of 6 | 6/6 | 6/6 | 6/6 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks read as complete thoughts | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Main+followup retrieved together | 2 of 2 | 2/2 | 2/2 | 2/2 | MET |

Full per-run output: `results/run_2026-09-23_1936_before.md`.

**Criterion 1 — real output** (`generate.py::answer_from_chunks`, question
"How many hours a week does CS 210 take outside of class?", run 1):

```
CS 210 takes 8 to 10 hours a week outside of class (course_cs_210_workload.txt).
```

**Criterion 2 — real output** (same function, "How often does the campus
shuttle run on weekends?", run 1):

```
The campus shuttle runs every 40 minutes on weekends. 

Source: transit_shuttle.txt
```

**Criterion 3 — real output** (`run_eval.py::check_out_of_scope`, cutoff 0.6):

```
What is the capital of Mongolia? -> refused (best distance 0.825)
How do I write a for loop in Rust? -> refused (best distance 0.877)
```

**Criterion 5 — real output** (`store.py::search`, both questions retrieve
both halves of their dining-hall pair):

```
Q5 sources: dining_halden_hall.txt, dining_kestrel_commons.txt,
dining_kestrel_commons_followup.txt, dining_north_kitchen.txt,
dining_north_kitchen_followup.txt

Q6 sources: dining_halden_hall.txt, dining_halden_hall_followup.txt,
dining_pellew_dining_hall.txt, dining_pellew_dining_hall_followup.txt
```

## Verdicts

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer (target: 5 of 6) | MET | All 6 questions passed the scorer on all 3 runs (18/18). The target held with room to spare, not just on one lucky pass. |
| 2 | Every answer names a source (target: 6 of 6) | MET | Every answer across all 3 runs had a source line — read them all directly in `results/run_2026-09-23_1936_before.md` rather than trusting the scorer for this one, since naming a source is a formatting check, not a fuzzy-match one. |
| 3 | Gate stops out-of-corpus questions (target: 4 of 5) | MET | 5/5 refused, and the best distance for every out-of-scope question (0.80-0.92) sat far above the 0.6 cutoff — not a close call, so I'm confident this holds beyond just this one measurement. |
| 4 | Chunks read as complete thoughts (target: 4 of 5) | MET | Read all 5 chunks from `app.py chunks -n 5` by hand; none started or ended mid-sentence. `chunks -n 5` returns the same 5 chunks every time (not a random sample), so this MET is really "5 of the same 5 chunks," not "5 of a fresh draw" — worth knowing if I ever add more chunks and re-check. |
| 5 | Main+followup retrieved together (target: 2 of 2) | MET | Both questions pulled chunks from both halves on all 3 runs. But the denominator is 2 — I'm calling this MET honestly, not confidently. Two questions passing twice each is weak evidence for a claim about "the system" in general; it tells me retrieval isn't obviously broken for this pattern, not that it's reliably solved. (This originally had a denominator of 1 in unit 1 — I added a 6th question, Halden Hall, specifically to get it to 2. See criteria.md.) 

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

No misses — all five criteria came out MET on the before-run. Nothing to
trace back to a pipeline stage.

Being honest about whether the targets were too safe: yes, for one of them.
**Criterion 3** (the relevance gate) is the loosest test in the set. My five
`OUT_OF_SCOPE` questions — capital of Mongolia, changing diesel oil, the 1994
World Cup, ibuprofen dosage, a Rust for-loop — aren't just outside the
corpus, they're from a completely different domain than anything
campus_life touches. The best distance for every one of them landed at 0.80
or higher, nowhere near the 0.6 cutoff, so the gate was never actually
tested near its boundary. A genuinely hard out-of-scope question would be
one that *sounds* like it belongs — something about a different school's
policies, or a campus-life topic this corpus doesn't happen to cover (dorm
policy at a school this corpus never mentions, say) — close enough in
subject that it might land nearer the cutoff instead of far past it.

Criteria 1 and 4 have the same shape of looseness in miniature: 6/6 against
a 5/6 target, and 5/5 against a 4/5 target, both with a full point of slack
that six real test questions and five fixed chunks never came close to
using.

If I were tightening one thing, it'd be criterion 3: swap one or two of the
`OUT_OF_SCOPE` questions for near-miss ones in the same general subject area
as campus_life, and see whether the cutoff still holds a clean gap or
starts to blur.

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
