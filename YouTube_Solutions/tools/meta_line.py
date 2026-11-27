"""Put the code tag (qtag) and the topic on one line under the question.

Before: <span class="qtag">CODE</span><div class="topic-sub">TOPIC</div>
After : <div class="meta-line"><span class="qtag">CODE</span><span class="topic-sub">TOPIC</div>
Idempotent. Lecture / Strong Box solution pages only (exam pages are skipped).
Usage: python meta_line.py            (dry run)
       python meta_line.py --write
"""
import glob, os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WRITE = "--write" in sys.argv
PAT = re.compile(r'<span class="qtag">([^<]*)</span><div class="topic-sub">(.*?)</div>', re.S)
CSS_OLD = ".topic-sub{color:var(--muted);font-size:.8rem;margin-top:4px;line-height:1.35}"
CSS_NEW = (".meta-line{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:4px}"
           ".topic-sub{color:var(--muted);font-size:.8rem;line-height:1.35}")

def convert(text):
    t, n = PAT.subn(lambda m: f'<div class="meta-line"><span class="qtag">{m.group(1)}</span>'
                              f'<span class="topic-sub">{m.group(2)}</span></div>', text)
    if n and CSS_OLD in t:
        t = t.replace(CSS_OLD, CSS_NEW, 1)
    elif n and CSS_NEW not in t:
        t = t.replace("</head>", "<style>" + CSS_NEW + "</style></head>", 1)
    return t, n

files = [f for f in glob.glob(os.path.join(ROOT, "**", "*_YouTube_Solutions.html"), recursive=True)
         if "ExamPapers_YouTube_Solutions" not in f and "exam_build" not in f and "PYQ_Audit" not in f]
pages = rows = 0
for f in sorted(files):
    text = open(f, encoding="utf-8").read()
    new, n = convert(text)
    if n:
        pages += 1; rows += n
        if WRITE:
            open(f, "w", encoding="utf-8", newline="").write(new)
print(f"pages {'changed' if WRITE else 'to change'}: {pages}   rows: {rows}")
