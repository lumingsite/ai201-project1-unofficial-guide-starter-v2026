# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 5 of my 6 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:** Four of my six questions each map to one specific
document with a clear factual answer (wait times, workload hours, shuttle
frequency). The other two ("what should I know about Kestrel Commons" and
"what time does Halden Hall close") pull from a main post plus its
follow-up rather than a single document, which is the pattern I'd expect to
be shakier if retrieval only grabs one half.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:** This one is 6 of 6, not 5 of 6, because it isn't a
retrieval-quality question — it's a check that generate.py always prints the
source line it's told to print. The only way this fails is a code bug in the
answer-formatting step, not a hard question, so there's no reason to leave
room for a miss.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:** Not a clean gap — a wide-open one. All 5 in-corpus
questions came back under 0.38 (best distance); all 5 OUT_OF_SCOPE questions
came back over 0.80. Nothing landed in the 0.4-0.75 range in between, so the
default cutoff of 0.6 isn't a close call here, and I'd expect the gate to hit
5 of 5 rather than 4 of 5 on these particular ten questions. I kept the
target at 4 of 5 anyway rather than claiming 5 of 5, since a wider or messier
set of out-of-scope questions than these five could still land closer to the
boundary.

---

## 4. Chunks read as complete thoughts

At least 4 of 5 sampled chunks (`python app.py chunks -n 5`) read as a
complete thought: the chunk does not start with a lowercase continuation
word (e.g. "and", "but", "which") and does not end on a trailing comma,
semicolon, or conjunction.

**Why this target:** My documents are short (about 178–549 characters each)
and campus_life uses `fallback_split`, so most documents become a single
chunk already. I expect this to hold almost every time — the risk is the
rare longer post with two unrelated facts crammed together.

---

## 5. Both the original post and its follow-up get retrieved together

For questions about a dining hall that has both a main post and a
`_followup` document, both questions retrieve chunks from both documents.
Questions 5 and 6 in `questions.py` ("What should I know about Kestrel
Commons before going for lunch?" and "What time does Halden Hall close,
and is that easy to miss?") are what this criterion is measured against.

**Why this target:** Several dining-hall topics (Kestrel Commons, Halden
Hall, and others) are split across a main post and a follow-up reply. A
system that only finds one half is missing context a real student would
want, so I want to check retrieval isn't systematically dropping one side.
Only two of my six questions actually exercise this pattern, so the target
is "2 of 2" rather than a fraction with room for a miss — with a
denominator this small, "at least 4 of 5" from the brief's phrasing
doesn't fit, and inflating the count would just be padding.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
