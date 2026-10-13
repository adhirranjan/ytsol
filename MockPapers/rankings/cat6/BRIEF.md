# CAT-6 ranking — brief for one chapter (or half-chapter)

You choose WHICH book questions go into the student's CAT-6 mock papers (exam 26-10-2026). Every
candidate has already been checked against the printed book (answer re-derived, stem corrected, figure
located), so you are judging *selection*, not correctness. **Do this work yourself — do NOT spawn
sub-agents.** Root: `E:\Adhir\AdWinUser\Desktop\icad-dps\ICAD\BooksScanned\MockPapers`.

## The papers
5 sets × 75 questions (25 Physics, 25 Chemistry, 25 Maths). Each subject = Part A 20 single-correct
MCQ + Part B 5 numerical (integer box), +4/−1. Sets form a ladder: Set 1 = the core must-do archetype
of every concept, later sets add variants and harder questions. The student sits them in the last 7
days before the exam, then two remediation sets built from what they miss.

## Inputs
- `rankings\cat6\<SUBJ>_candidates.json` → `candidates.<CHAPTER>.list`: the deterministic shortlist
  (~1.5× your quota) with code, lec, sec (level: 2…6 / Sugg / Board), stem, answer, has_opts, integer,
  type, figure.
- Full verified rows: `pool\<LEC>.json` (the whole checked pool for that lecture — you may pick a
  question that is NOT on the shortlist if it is better, as long as it is in the pool with
  `verified: "ok"`, not a `VRecap` code, and meets the Part A / Part B rule below).
- The checker's notes for any code: `pool_check\rows\<LEC>\<CODE>.json` (`reason`, `work`).

## Rules
1. **Exactly your quota** of picks, with exactly the Part-B count given in your prompt.
2. **Part B picks must have `integer: true`.** Part A picks must have `has_opts: true` (choices printed).
3. **One archetype per solving method.** Cluster near-duplicates (same method, different numbers) and
   keep the best one; the others only if the chapter would otherwise run short. Spread across EVERY
   lecture of your chapter, roughly in proportion to how much each lecture teaches.
4. **Difficulty:** aim for the range in your prompt for Level 5/6 (a range with a ceiling — do not
   overshoot it); most of the rest Level 3/4; a few Level 2 / Suggested only as Set-1 warm-up
   archetypes. Board questions only if they are genuinely MCQ/integer.
5. **Style mix:** include the multi-correct, assertion–reason, match-the-column and graph questions the
   chapter has (the real paper uses them), but keep them a minority.
6. **Skip** any question whose checker `reason` says the reading is ambiguous, convention-dependent,
   contested, or "intended" rather than forced; and any stem that says "as shown in the figure" when
   `figure` is false.
7. **tier**: 1 = core must-do (breadth — every key method once), 2 = variant / depth, 3 = harder.
   About 40% / 35% / 25%. Tier drives which set a question lands in.

## Output — `rankings\cat6\final_<NAME>.json` (NAME given in your prompt)
```json
{"chapter": "P10", "need": 45, "picks": [
  {"code": "P10L3V4Q2", "tier": 1, "partB": false, "style": "standard", "note": "banking angle tanθ = v²/rg"}
]}
```
`style` ∈ standard | multi-correct | assertion | match | graph | numerical. `note` = the method, in a few
words — it is how a reviewer sees that no two picks share a method.
**Write the file early and rewrite it every ~10 picks** (agents stall mid-stream; a half-written file
is recoverable, a lost one is not). The last write must contain exactly the quota.

## Report back
Count by tier, by level (L2/3/4/5/6/Sugg), Part-B count, lectures covered, and any lecture you could
not cover well (with why). Short.
