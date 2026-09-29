"""Generate MockPapers/MockPapers_Index.html by scanning the folder.

    python build_index.py

Reads what is actually on disk rather than a hardcoded list, so re-running it picks up newly
completed sets. A set counts as ready-to-sit when its question paper carries at least one figure
and every MCQ prints its options; otherwise it is listed as still needing the figure/options pass.
"""
import glob, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POOL = {}
for f in os.listdir(os.path.join(MP, "pool")):
    for r in json.load(open(os.path.join(MP, "pool", f), encoding="utf-8")):
        POOL[r["code"]] = r
OPTS = set()
for f in glob.glob(os.path.join(MP, "options_*.json")):
    for k, v in json.load(open(f, encoding="utf-8")).items():
        if isinstance(v, dict) and v.get("options"): OPTS.add(k)

def set_state(exam, n):
    """(questions_file, key_file, figures, mcqs_without_options) or None if not built"""
    q = os.path.join(MP, "%s-Set%d-Questions.html" % (exam, n))
    if not os.path.exists(q): return None
    k = "%s-Set%d-Key.html" % (exam, n)
    h = open(q, encoding="utf-8").read()
    figs = h.count('class="fig"')
    noopt = 0
    for blk in re.findall(r'<div class="q">.*?</div></div>', h, re.S):
        m = re.search(r'<span class="tag">([^<]+)</span>', blk)
        s = re.sub(r"<[^>]+>", "", re.search(r'<div class="b">(.*?)</div>', blk, re.S).group(1))
        c = m.group(1) if m else ""
        r = POOL.get(c)
        if not r: continue
        if re.match(r"^[a-dA-D][\s\).:]", r["answer"].strip()) and not (
                re.search(r"\(a\)", s) or s.count(" / ") >= 2 or c in OPTS or c == "M4L1V3Q4"):
            noopt += 1
    return (os.path.basename(q), k if os.path.exists(os.path.join(MP, k)) else None, figs, noopt)

EXAMS = [
    ("RT-4",  "RT4",  "12-10-2026", "current", "RT4-Mock-Sets.html",  []),
    ("CAT-5", "CAT5", "28-09-2026", "past",    "CAT5-Mock-Sets.html", []),
    ("RT-3",  "RT3",  "21-09-2026", "past",    "RT3-Mock-Sets.html",
     [("RT3-Final-Set.html", "Final Set - one last paper built from the wrong/blank questions of "
                             "Sets 1-8 plus Sets 9-10")]),
    ("CAT-4", "CAT4", "31-08-2026", "past",    "CAT4-Mock-Sets.html", []),
]

CSS = open(os.path.join(MP, "CAT4-Mock-Sets.html"), encoding="utf-8", errors="replace").read()
CSS = CSS[CSS.find("<style>"):CSS.find("</style>")] + """
 .exam{border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:16px 0;background:var(--card)}
 .exam h2{margin:0;font-size:1.2rem;display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
 .when{font-size:.82rem;color:var(--mut);font-weight:400}
 .badge{font-size:.68rem;font-weight:700;border-radius:20px;padding:2px 9px;letter-spacing:.03em}
 .badge.now{background:var(--accent);color:#fff}
 .badge.past{background:var(--line);color:var(--mut)}
 .master{margin:8px 0 2px;font-size:.9rem}
 table{width:100%;border-collapse:collapse;margin-top:8px;font-size:.87rem}
 th{text-align:left;font-size:.72rem;text-transform:uppercase;letter-spacing:.04em;color:var(--mut);
    border-bottom:1px solid var(--line);padding:4px 6px}
 td{padding:4px 6px;border-bottom:1px solid var(--line)}
 td.n{width:3.2em;color:var(--mut);font-variant-numeric:tabular-nums}
 .ready{color:var(--code);font-weight:600}
 .pending{color:var(--warn)}
 .meta{font-size:.76rem;color:var(--mut)}
 a{color:var(--accent)}
</style>"""

body = []
for name, pre, date, when, master, extras in EXAMS:
    if not os.path.exists(os.path.join(MP, master)): continue
    rows = []
    for n in range(1, 11):
        st = set_state(pre, n)
        if not st: continue
        q, k, figs, noopt = st
        ready = figs > 0 and noopt == 0
        rows.append('<tr><td class="n">%d</td><td><a href="%s">Question paper</a></td>'
                    '<td>%s</td><td class="%s">%s</td><td class="meta">%s</td></tr>'
                    % (n, q, '<a href="%s">Key</a>' % k if k else "&#8212;",
                       "ready" if ready else "pending",
                       "ready to sit" if ready else "needs figures / options",
                       "%d figures" % figs if figs else ""))
    body.append('<div class="exam"><h2>%s <span class="when">exam %s</span>'
                '<span class="badge %s">%s</span></h2>'
                '<p class="master">Master sheet: <a href="%s">%s</a> '
                '<span class="meta">&#8212; all sets as book-code grids with a collapsible key</span></p>%s%s</div>'
                % (name, date, "now" if when == "current" else "past",
                   "current" if when == "current" else "past", master, master,
                   "".join('<p class="master"><a href="%s">%s</a> <span class="meta">&#8212; %s</span></p>'
                           % (f, f, d) for f, d in extras),
                   ('<table><tr><th>Set</th><th>Paper</th><th>Key</th><th>State</th><th></th></tr>%s</table>'
                    % "".join(rows)) if rows else ""))

ch = os.path.join(MP, "ChapterPapers", "Chapter_Index.html")
if os.path.exists(ch):
    nch = len(set(os.path.basename(p).split("-")[0]
                  for p in glob.glob(os.path.join(MP, "ChapterPapers", "*-Coverage.html"))))
    body.append('<div class="exam"><h2>Chapter drills</h2>'
                '<p class="master"><a href="ChapterPapers/Chapter_Index.html">Chapter_Index.html</a> '
                '<span class="meta">&#8212; %d chapters, each as Coverage (every lecture at every '
                'level) and Mock (that chapter\'s mock-paper picks)</span></p></div>' % nch)

html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>ICAD Mock Papers</title>' + CSS +
        '</head><body><div class="wrap"><header id="top"><h1>ICAD Mock Papers</h1>'
        '<p>75 Q per set &#183; 25 Physics &#183; 25 Chemistry &#183; 25 Mathematics &#183; '
        'Part A 20 MCQ + Part B 5 numerical &#183; 300 marks &#183; 3 hours &#183; +4 / &#8722;1</p>'
        '</header><div class="legend">A question paper is <b class="ready">ready to sit</b> once it '
        'carries the book\'s figures and every MCQ prints its options. The others are readable but '
        'not yet complete. Answer keys are separate files so they need not be printed.</div>'
        + "".join(body) + '</div></body></html>')

out = os.path.join(MP, "MockPapers_Index.html")
open(out, "w", encoding="utf-8").write(html)
print("WROTE %s (%.0f KB)" % (os.path.basename(out), os.path.getsize(out) / 1024))
for name, pre, date, when, master, _ in EXAMS:
    sts = [set_state(pre, n) for n in range(1, 11)]
    have = [s for s in sts if s]
    if have:
        print("  %-6s %d sets, %d ready to sit" % (name, len(have),
              sum(1 for s in have if s[2] > 0 and s[3] == 0)))
