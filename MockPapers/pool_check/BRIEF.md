# Pool check — brief for one lecture

You verify every question of ONE lecture of the ICAD JEE book against the printed scan, before the
questions are admitted to the mock-paper pool. A student will sit papers built from your verdicts, so
correctness matters more than speed. **Do this work yourself — do NOT spawn sub-agents.**

Root: `E:\Adhir\AdWinUser\Desktop\icad-dps\ICAD\BooksScanned` (all paths below are relative to it).
Other agents run in parallel and share the session scratchpad: keep ALL your helper scripts and
rendered images inside a subfolder of it named after your lecture (e.g. `<scratchpad>\P10L3\`).
If the print has a wording misprint (wrong unit, dropped symbol, garbled subscript) that you can
resolve with certainty, write the CORRECTED full question into `stem_book` and say so in `reason`.
If a question only works under an unstated assumption (same direction, elastic, g = 10 …), put the
assumption INTO `stem_book` so the printed question has one answer.
On Windows start every Python script with `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`.

## Inputs
- Manifest: `MockPapers\pool_check\manifest\<LEC>.json` — a list of
  `{code, sec, num, key, stem}`. `code` = `<LEC>V<sec>Q<num>`; `sec` is `Sugg` (Suggested Problems),
  `Board` (Level: Board) or a level number `1`…`6`. `stem` and `key` were transcribed by an earlier
  agent and are NOT trusted: stems are sometimes paraphrased, truncated or missing options/data, and keys
  are sometimes mis-copied.
- The book pages: `python MockPapers\tools\figtool.py pages <LEC> 170` renders every page of the
  lecture PDF to PNG and prints the paths. READ the PNGs (they are images; the PDFs have no text layer).
  A lecture runs: theory → solved examples → quick recap → exercises (Suggested Problems, Level Board,
  Level-1 … Level-6). Only the exercises are in the manifest.
- The book's printed answer key (consult it only when your answer disagrees with the manifest key):
  Physics P6–P10 `PhyV2\P-V2-Answer Key.pdf`, P11+ `PhyV3\P-V3-Answer Key.pdf`; Chemistry C4–C6
  `ChemV2\C-V2-Answer Key.pdf`; Maths M8A–M11 `MathV2\M-V2-Answer Key.pdf`. Render a page with
  `fitz.open(path)[i].get_pixmap(dpi=170).save(png)` into your scratchpad.

## For EACH manifest entry, in order
First list `MockPapers\pool_check\rows\<LEC>\` — **skip every code that already has a file** (a
previous run did it). Then for each remaining code:
1. Find the question on the book page (section heading + question number).
2. Compare the manifest stem with the print: every number, unit, condition and option.
3. Solve it yourself, independently, before looking at the key. Then compare with `key`.
   - Agree → `verdict: "ok"`.
   - Disagree → re-derive a second way, check its structural twins in the same lecture, then read the
     printed answer key. If the printed key matches you, the manifest key was mis-copied: `ok`, with
     `correct_answer` = the right answer and `reason` saying so. If the printed key itself is wrong:
     `key_wrong`, `correct_answer` = your answer (option letter + value), `reason` = key-vs-working in
     one line. Be sure — about 1 in 14 ICAD keys really is wrong, but most disagreements are your slip.
4. **Write the row file immediately** — `MockPapers\pool_check\rows\<LEC>\<CODE>.json`, one Write
   call per question — then move to the next. Never derive several and write them together: agents
   stall mid-stream and everything not yet written is lost.

## Questions the manifest is missing
The manifest was built from earlier transcriptions that sometimes skipped a question. While you are on
each exercise section, compare its printed question numbers with the manifest. For every printed
question with NO manifest entry, check it the same way and write a row for it too, with the code
`<LEC>V<sec>Q<num>` from the book's own section and number, plus two extra keys: `"added": true` and
`"sec"` / `"num"` (as strings). Its `stem_book` must be the full printed question and `key` the
printed answer-key entry.

## Row file (UTF-8 JSON, exactly these keys)
```json
{"code": "P10L3V4Q7", "page": 14, "stem_ok": true, "stem_book": null,
 "figure": null, "type": "single", "options_printed": true,
 "key": "b 4 m/s", "derived": "b 4 m/s", "verdict": "ok", "correct_answer": "b 4 m/s",
 "integer": true, "in_scope": true, "reason": "", "work": "v = √(gR tanθ) = √(10·1.6·1) = 4 m/s"}
```
- `page`: 1-based page of the rendered PDF where the question is printed.
- `stem_ok`: true only if the manifest stem carries every number, condition and option of the print.
  Otherwise `stem_book` = the FULL question as printed, options included as `(a) … (b) … (c) … (d) …`.
  Use plain Unicode (², ₂, √, π, θ, →); write powers as x^(n) when superscripts won't do.
- `figure`: if the book prints a figure / diagram / graph / table for this question, give
  `{"page": n, "bbox": [x0, y0, x1, y1]}` as FRACTIONS (0–1) of page width/height from the top-left,
  enclosing just that figure (include the option graphs if the options are drawings). Otherwise null.
  A question needs its figure whenever the book prints one — even if the stem reads complete.
- `type`: `single` (one correct option), `multi` (one or more correct), `numerical` (a value, no
  options), `match` (match the columns), `assertion` (assertion–reason / statement I–II), `subjective`
  (prove / define / explain / derive / multi-part long answer with no single checkable answer).
- `integer`: true when the correct answer is a single integer (it could go in an integer answer box).
- `verdict: "unusable"` when it cannot be asked in a paper: `subjective`; data lives in a passage or
  figure that is not printed; illegible; no printed option is correct; two options identical; a
  multi-part question whose parts have separate answers. Give the reason in one line.
- `in_scope`: true, except where the brief for your lecture says otherwise.
- `work`: one line — the key step of your derivation (formula = substitution = result).

## Style rules
- Never write vulgar-fraction HTML entities (`&#85xx;`) or ⅖-style glyphs — write plain `(2/5)`.
- JSON must parse; escape quotes and backslashes.

## When done
Run `python MockPapers\tools\pool_check.py missing <LEC>`; it must print nothing. Then reply with ONE
short report: counts by verdict, every `key_wrong` code with its one-line reason, how many need a figure,
how many stems you replaced, and anything you could not read.
