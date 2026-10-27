# Pool check — addendum for SHORTLISTS of older lectures (read after BRIEF.md)

The RT-5 mock papers (exam 16-11-2026) re-use questions from the older chapters, whose pool was never
book-checked. Only a shortlist is checked. Everything in `BRIEF.md` applies, with these differences.

- **Manifests:** `MockPapers\pool_check\manifest_patch\<LEC>.json` (NOT `manifest\`). Each holds only the
  1–7 shortlisted questions of that lecture. Check exactly those codes; rows go to
  `MockPapers\pool_check\rows\<LEC>\<CODE>.json` as usual.
- **Skip the "Questions the manifest is missing" section of BRIEF.md** — a shortlist is incomplete on
  purpose. Never add rows for other questions.
- **The stored stems are often one-line paraphrases** ("At NTP a gas occupies 5.6 L — calculate moles")
  without the options. Expect `stem_ok: false` for most: write the full printed question with its
  options `(a) … (d)` into `stem_book`.
- **Pages:** `python MockPapers\tools\figtool.py pages <LEC> 170` renders the lecture. The exercises are
  at the back of the lecture; find the question by its section (Suggested / Board / Level-n) and number.
- **Answer keys:** `PhyV1\P-V1-Answer Key.pdf` (P1–P5), `PhyV2\P-V2-Answer Key.pdf` (P6–P10),
  `ChemV1\C-V1-Answer Key.pdf` (C1–C3), `ChemV2\C-V2-Answer Key.pdf` (C4–C6), `MathV1\M-V1-Answer Key.pdf`
  (M1–M7), `MathV2\M-V2-Answer Key.pdf` (M8A–M11).
- `in_scope` is true for every question here.
- When done, list your manifests and confirm every code has a row file. Do NOT run `pool_check.py patch`
  or `merge` — they write the pool; the coordinator runs them after every agent has reported.
