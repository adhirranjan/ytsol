# Pool check — addendum for REAL ICAD exam papers (read after BRIEF.md)

You check the questions of ONE real ICAD exam paper (RT-n / CAT-n) so they can be re-used in RT-5 mock
papers (exam 16-11-2026). Everything in `BRIEF.md` applies, with these differences.

- **Your questions:** `MockPapers\pool_check\past_assign\<EXAM>.json` — 75 entries `{code, lec, q, bookref}`.
  `code` = `<CH>XV<EXAM>Q<q>` (CH = chapter from the solution page's book reference; `P0` / `C0` / `M0`
  when it had none). The manifest entry for a code is in `manifest\<lec>.json` (several exams share one
  chapter manifest — touch only YOUR codes). Row files go to `rows\<lec>\<code>.json`.
- **The print:** `ExamPapers\<EXAM>-<date>-AnswerKey-Question-Paper.pdf`, already rendered at 170 dpi to
  `C:\Users\ADHIRR~1\AppData\Local\Temp\icad_pages\<EXAM>_p01.png …` — do NOT re-render. `page` and the
  figure bbox refer to THIS PDF. The official answer key is printed in the same PDF (usually at the end).
  RT1 and CAT3 PDFs hold Set A (first half of the pages) and Set B; use **Set A** — the manifest follows A.
- **The manifest stem** comes from our solution page: it may carry a "[Figure: …]" text description and
  paraphrased options. `stem_book` must be the question AS PRINTED (no "[Figure: …]" text — give the
  figure bbox instead), with options `(a) … (d)` lower-case.
- **Key:** solve it yourself first, then compare with the manifest key AND the official printed key. ICAD
  keys are wrong sometimes (e.g. CAT6 Q52 has no unique answer → `unusable`). A question the paper marks
  cancelled/bonus is `unusable` unless it has exactly one correct answer as printed (then `ok`).
- **Two extra keys in every row:**
  - `"chapter"`: the book chapter the question belongs to — one of P1…P11, C1…C6, M1…M4, M5A, M5B,
    M5C, M6, M7, M8A, M8B, M8C, M8D, M9, M10, M11, P12, C7 (correct the bookref if it is wrong; this
    decides which chapter quota the question fills). Chapter titles: P1 BMT-1, P2 BMT-2 (calculus),
    P3 Vectors, P4 Motion 1D/2D, P5 Force System, P6 NLM, P7 Friction, P8 Work-Energy-Power, P9 Collision,
    P10 Circular Motion, P11 Centre of Mass · C1 States of Matter, C2 Structure of Atom, C3 Basic Concepts
    (mole), C4 Periodicity, C5 Chemical Bonding, C6 Thermodynamics · M1 Angles, M2 Sets, M3 Trig Ratios &
    Identities, M4 Functions-I, M5A Compound Angles, M5B Transformation, M5C Multiple/Sub-multiple &
    Conditional Identities, M6 Functions-II, M7 Exponential & Log, M8A AP, M8B GP, M8C HP & means,
    M8D AGP & special series, M9 Complex Numbers-I, M10 Quadratic Equations, M11 Trig Equations.
  - `"lecture"`: the book lecture if the bookref names one and you agree (e.g. "P6L3"), else null.
- **in_scope:** false when the chapter is outside the RT-5 syllabus (P12, C7, M10, M11, Complex Numbers-II)
  or it is M9 rotation / Argand-plane geometry (loci, regions, areas, distances over curves).
- Your scratchpad subfolder is named after your exam (e.g. `<scratchpad>\RT4\`).
- **When done:** every code in your assign file must have a row file. Report as BRIEF.md says, plus how
  many chapters you corrected.
