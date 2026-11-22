# RT-5 exam solution rows — solver spec

S = C:/Users/adhirranjan/AppData/Local/Temp/claude/95d52bebfde8b3c8/ef3d8fff-5157-458b-a988-c2624afe1792/scratchpad/rt5
Project root (READ-ONLY for you): E:/Adhir/AdWinUser/Desktop/icad-dps/ICAD/BooksScanned
Paper: ExamPapers/RT5-20261116-AnswerKey-Question-Paper.pdf — the ACTUAL ICAD exam RT-5, 16/11/2026, EXCEL JEE-2028 Ph-1 (Regular), PCM, 75 Q.
Syllabus (full cumulative Phase-1): PHY P1–P11 · CHEM C1–C6 · MATH M1–M7, M8A–M8D, M9 (Complex Numbers-I, except rotation & geometry).
On Windows Python always start with `sys.stdout.reconfigure(encoding="utf-8")`.
Do this work YOURSELF — do NOT spawn sub-agents.

## Inputs
- Page images S/pages/pNN.png (200 dpi): key p01 · Q1–4 p02 · Q5–8 p03 · Q9–14 p04 · Q15–20 p05 · Q21–25 p06 · Q26–35 p07 · Q36–50 p08 · Q51–63 p09 · Q64–75 p10.
  READ THE IMAGE with the Read tool — figures, tables and maths matter. Need more detail? Crop/zoom with PyMuPDF from the paper PDF into S/tmp/ (e.g. 400 dpi clip of the question).
  S/text.txt is the text layer (garbles maths; use only to copy plain words).
  Section headings on the paper are misleading: Q36–45 and Q64–70 sit under a "NUMERICAL VALUE TYPE" banner but ARE single-correct MCQs.
  Part B (numerical) = Q21–25, Q46–50, Q71–75 only.
- Book index S/book_index.txt — one line per book question: `ref | question | ANS | VID url [match] title`. Grep it (Grep tool, -i, distinctive words/numbers). Its question text is a compressed paraphrase.
- Past ICAD exams S/past_exams.txt (RT1–RT4, CAT3–CAT6, already solved & verified): `EXAM · Qn | question || ANS || VID || BOOKREF`. RT papers REPEAT questions from these (RT-4 had 12 verbatim repeats, 10 of them from RT-3). GREP IT FIRST for every question — a hit gives a vetted video and book ref to start from (still re-verify both, and still write your own solution).
- Lecture PDFs (image-only scans) listed in S/lecture_pdfs.txt (paths relative to project root). Render a page:
  `python -c "import fitz;d=fitz.open(r'<pdf>');d[<i>].get_pixmap(dpi=100).save(r'<S>/tmp/<name>.png')"` then Read the PNG.
  The book index EXCLUDES each lecture's Solved Examples / theory illustrations — those live only in the PDFs.
- House-style example rows: S/example_row.txt — read it first.

## Printed key (p.1, "Final Answer Key (No Correction)")
1A 2C 3D 4C 5A 6B 7C 8B 9D 10D 11A 12D 13D 14A 15C 16A 17A 18B 19D 20D · 21:1 22:1 23:25 24:3 25:0
26B 27D 28A 29D 30A 31A 32B 33D 34A 35D 36C 37A 38D 39B 40A 41C 42D 43C 44C 45C · 46:6 47:7 48:5 49:0 50:2
51D 52B 53B 54C 55D 56D 57C 58B 59B 60B 61C 62A 63B 64B 65C 66C 67B 68C 69D 70A · 71:1 72:1 73:13 74:25 75:4

## Per question, in order
1. Transcribe question + options to HTML (q_html). MCQ: options inside `<span class="na">(A) … (B) … (C) … (D) …</span>`. Numerical: no options span. Use entities/<sup>/<sub>; NO vulgar-fraction entities or glyphs (&frac12;, &#8530;, ½ …) — write 1/2, (2/5). Tables → a <pre> block inside q_html (lines ≤ 62 chars). Keep the paper's wording; if a figure carries essential data, state it in [brackets] so the question is answerable without the figure.
2. SOLVE INDEPENDENTLY, fully, before looking at the key. Then compare with the printed key.
   - agree → flag = null.
   - disagree after careful re-check → keep the KEY's letter/value in ans_letter/ans_text, set flag = plain-text tooltip "Printed key gives (X) …; independent working gives (Y) because …" (no HTML tags in flag — use ² ³ characters), and say so in the solution's final line.
   - defective/ambiguous question (misprint, garbled stem) → explain in flag.
3. Book Ref. Grep S/past_exams.txt and S/book_index.txt; read every plausible candidate line in full. Then ALSO open the most likely lecture PDF(s) for the topic and scan ALL their Solved Examples / Quick Recap pages (low dpi) — not just Ex-1/Ex-2; on RT-4 the verifiers found 6 closer refs the solvers had missed — at most ~4 PDFs per question. Decide:
   "ex" = same question, same numbers & answer (minor rewording, different distractors, or asking the inverse quantity of the same setup still count) — verified by reading the book text or page image;
   "si" = nearest same-method question; null = nothing relevant.
   bookref format: "<Ch> · L<n> · <Sec> · <Qn>", Sec ∈ Lvl1..Lvl6, Sugg, Board, Recap, PYQ, SolvedEx; Strong Box → "SB" as the L part. E.g. "P7 · L2 · Lvl4 · Q6", "C5 · L3 · SolvedEx · Ex-3", "M8A · SB · PYQ · Q12".
   If the question repeats a past ICAD paper, say so in bookref_evidence ("= RT-3 Q14 verbatim").
4. Video. A live video is not a relevant video: check the real (oembed) title matches THIS question's method; "exact" only if it is this question with the same numbers (a converse question is "similar"). If the matched book/past-exam line has a VID url, reuse it (with the same exact/similar test). Otherwise WebSearch YouTube (English/Hindi) for a video solving this question / teaching this method. EVERY ID must be verified:
   `curl -s -o /dev/null -w "%{http_code}" "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=<ID>&format=json"`
   200 or 401 = alive (401 = embed-disabled, still fine, keep it). 403/400/404 = reject. Code 000 = network blip, re-probe. Never guess an ID. Nothing verifiable → video_url = null.
   video_title: descriptive (use oembed title; if the source title is a bare URL, re-probe oembed for the real title). Normalise youtu.be / shorts to `https://www.youtube.com/watch?v=ID`.
5. soln_html = inner HTML of <div class="solnbody">, exactly this structure (no new classes/sections):
   <div class="seg"><span class="lbl">Concept</span> …</div>
   <div class="seg"><span class="lbl">Formula</span> <span class="eq">…</span>. <span class="why">…</span></div>
   <div class="seg"><span class="lbl">Solution</span><div class="step">1. …<span class="why">…</span></div> … (optional <pre>, lines ≤ 62 chars)</div>
   <div class="trick"><span class="lbl">&#9889; JEE Trick</span> …</div>  (if you say where a distractor comes from, CHECK that arithmetic — wrong distractor stories were the commonest verifier fix)
   <div class="final">Answer: (C) 1, 2, 1.</div>
   Target 1,700–2,400 chars (house median ~1,950), 4–7 steps; chain formula → substitution → result on ONE line.
6. Write S/rows/Q<NN>.json (two-digit) IMMEDIATELY after finishing that question — one file per question, never batch at the end. UTF-8, json.dump(ensure_ascii=False):
{"num": 7, "q_html": "...", "topic": "2–5 words", "video_url": "https://www.youtube.com/watch?v=ID" | null, "video_title": "...", "match": "exact" | "similar",
 "key": "B", "ans_letter": "B" | null (null for numerical), "ans_text": "option content in HTML / numerical value", "flag": null | "tooltip text",
 "bookref_tag": "ex" | "si" | null, "bookref": "P7 · L2 · Lvl4 · Q6" | null, "bookref_evidence": "one line: where seen, numbers compared",
 "soln_html": "..."}
Validate it parses (python json.load) and run `python E:/Adhir/AdWinUser/Desktop/icad-dps/ICAD/BooksScanned/YouTube_Solutions/exam_build/check_rows.py S` (mechanical gates: structure, 1,400–2,800 chars, <pre> ≤ 62, no fraction glyphs) before moving on.

## Final report (short)
One line per question: num · your answer vs key · bookref tag+ref · video match · any flag.
