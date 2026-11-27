"""Make #q-... links land on the question row, not below it.

Problem: the browser scrolls to the anchor on load, then fonts / late layout push the row further
down, so a link from a mock result sheet can land on the wrong part of the page. Also the sticky
nav covers the top of the row.

Fix (per solution page):
  - CSS: [id^="q-"]{scroll-margin-top:64px} so the sticky nav does not hide the row.
  - JS: after load, after fonts are ready, and at 300 ms / 1.2 s, scroll the hash target into view.
Idempotent (marker comment). Exam pages are skipped.

Usage: python hash_scroll.py            (dry run)
       python hash_scroll.py --write
"""
import glob, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WRITE = "--write" in sys.argv
MARK = "<!-- hash-scroll -->"
BLOCK = (
    MARK
    + "<style>[id^=\"q-\"]{scroll-margin-top:64px}</style>"
    + "<script>(function(){"
    + "function go(){var h=location.hash;if(h&&h.indexOf('#q-')===0){"
    + "var el=document.getElementById(h.slice(1));if(el){el.scrollIntoView({block:'start'});}}}"
    + "if(document.readyState==='complete'){go();}else{window.addEventListener('load',go);}"
    + "if(document.fonts&&document.fonts.ready){document.fonts.ready.then(go);}"
    + "setTimeout(go,300);setTimeout(go,1200);"
    + "})();</script>"
)

files = [f for f in glob.glob(os.path.join(ROOT, "**", "*_YouTube_Solutions.html"), recursive=True)
         if "ExamPapers_YouTube_Solutions" not in f and "exam_build" not in f and "PYQ_Audit" not in f]
todo = 0
for f in sorted(files):
    text = open(f, encoding="utf-8").read()
    if MARK in text or 'id="q-' not in text:
        continue
    todo += 1
    if WRITE:
        new = text.replace("</body>", BLOCK + "</body>", 1)
        open(f, "w", encoding="utf-8", newline="").write(new)
print(f"pages {'updated' if WRITE else 'to update'}: {todo}")
