# RT-5 row verifier — adversarial spec

Your job is to REFUTE the solver's rows, not to rubber-stamp them. S, inputs, formats and tag rules are as in S/SOLVE_SPEC.md — read it first.
On Windows Python always start with `sys.stdout.reconfigure(encoding="utf-8")`. Do this work YOURSELF — do NOT spawn sub-agents.
Rows under test: S/rows/Q<NN>.json. Do NOT edit S/rows yourself.

Per question:
1. Read the question from the PAGE IMAGE yourself (S/pages/pNN.png; zoom if needed). Check q_html against it: wrong numbers, missing/altered options, figure data missing or mis-transcribed → defect.
2. Solve independently BEFORE reading soln_html. Compare with the row's ans_letter/ans_text and the printed key. Then read soln_html line by line: every substitution and arithmetic step must be right; the final line must match ans_text; a flagged row's tooltip must be correct; an unflagged row whose answer is actually wrong is the worst defect. Check any "distractor comes from …" story in the JEE Trick by actually doing that arithmetic. Any error → defect (give corrected working).
3. Book Ref: verify the claim. "ex": open the cited line in S/book_index.txt or render the cited PDF page and confirm same numbers/answer. "si"/null: grep S/book_index.txt and S/past_exams.txt with different keywords AND render Solved-Examples/Recap pages of the 1–3 most relevant lecture PDFs looking for an exact source the solver missed. A verbatim repeat of a past ICAD paper (S/past_exams.txt) that the solver missed is a defect. Report a better ref if found.
4. Video: run the oembed curl on the row's video ID; 200/401 = alive. Check the title actually matches the question's method; "exact" must really be the same question with the same numbers (fetch the watch page/description if the title is not conclusive). Dead, off-topic, wrong exact/similar label, or null when a verifiable video exists → defect (supply a verified replacement).
5. House style: no vulgar-fraction entities/glyphs; Concept/Formula/Solution/Trick/final present; 1,400–2,600 chars; <pre> lines ≤ 62 chars (q_html too); JSON valid. Run `python E:/Adhir/AdWinUser/Desktop/icad-dps/ICAD/BooksScanned/YouTube_Solutions/exam_build/check_rows.py S` for the mechanical gates.

Write S/recheck/Q<NN>.json (UTF-8, ensure_ascii=False) IMMEDIATELY after each question:
{"num": 7, "ok": true | false, "answer_independent": "B", "agrees_with_row": true | false, "agrees_with_key": true | false,
 "defects": ["..."],
 "fixes": {only fields that must change, full replacement values, same formats as the row},
 "notes": "one line"}
Use "fixes": {} when nothing changes. If the solution text needs fixing, supply the complete corrected soln_html.

Final report (short): one line per question: num · ok/NOT-OK · fixed fields · answer vs key.
