"""Upgrade a quiz page (<Ch>_Quiz.html or RT5_Quiz/*_Quiz.html) to engine v2:
one question at a time + palette, soft per-question timer with per-type budgets
(t: 60 recall / 90 standard / 180 calculation), downloadable result page.

Usage:  python Quiz/upgrade_engine_v2.py <quiz.html> [--dry]

- Reads the engine from Quiz/engine_v2.js.
- Keeps the file's line endings (CRLF or LF) as found.
- Keeps the file's own "mastered"/"complete" title via DONE_TITLE.
- Re-runnable: a file already on v2 only gets its engine block refreshed.
- Questions that already carry t: are left alone; the rest are tagged by a heuristic.
  Eyeball the printed 60 / 180 lists afterwards.
"""
import re, sys, os, html as H
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
path = sys.argv[1]; dry = "--dry" in sys.argv
src = open(path, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in src else "\n"
src = src.replace("\r\n", "\n")
engine = open(os.path.join(HERE, "engine_v2.js"), encoding="utf-8", newline="").read().replace("\r\n", "\n")

CSS = """
  /* v2: palette · single-question view · soft timer */
  .pal{display:flex;flex-wrap:wrap;gap:10px 18px;margin:10px 0 4px}
  .pgrp{display:flex;flex-wrap:wrap;gap:5px;align-items:center}
  .plab{font-size:.68rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--accent);margin-right:3px}
  .pb{width:34px;height:30px;border-radius:8px;border:1px solid var(--line);background:var(--card2);color:var(--muted);font-weight:700;font-size:.8rem;cursor:pointer}
  .pb:hover{border-color:var(--brand)}
  .pb.ans{background:var(--good-bg);border-color:var(--good);color:var(--good)}
  .pb.cur{outline:2px solid var(--brand);outline-offset:1px;color:var(--ink)}
  .pb.over{box-shadow:inset 0 -3px 0 var(--bad)}
  .clock{margin-left:auto;font-variant-numeric:tabular-nums;font-weight:800;font-size:.82rem;border-radius:999px;padding:2px 11px;background:var(--chip);border:1px solid var(--line);color:var(--muted)}
  .clock.warn,.q.warn{border-color:var(--warn)} .clock.warn{color:var(--warn);background:var(--warn-bg)}
  .clock.over,.q.over{border-color:var(--bad)} .clock.over{color:var(--bad);background:var(--bad-bg)}
  .nav{display:flex;gap:10px;align-items:center;justify-content:space-between;margin:6px 0 14px;flex-wrap:wrap}
  .nav .mid{font-size:.78rem;color:var(--muted)}
  .slowrow{font-size:.88rem;padding:4px 0;border-bottom:1px dashed var(--line)}
  .tover{color:var(--bad);font-weight:700}
</style>"""

QUIZ_MARKUP = """  <!-- ================= QUIZ ================= -->
  <div id="scr-quiz" class="hide">
    <div class="bar">
      <span class="pill">Round <b id="pRound">1</b></span>
      <span class="pill">Q <b id="pCur">1</b>/<b id="pCount">0</b></span>
      <span class="pill">Answered <b id="pAns">0</b>/<b id="pTot">0</b></span>
      <div class="prog"><i id="pBar"></i></div>
      <span class="pill">Mastered <b id="pMast">0</b>/<b id="pSel">0</b></span>
      <span class="pill">&#9201; Round <b id="pTime">0:00</b></span>
    </div>
    <div class="pal" id="palette"></div>
    <div id="qcard"></div>
    <div class="nav">
      <button class="btn ghost" id="prevBtn" onclick="showQ(cur-1)">&larr; Previous</button>
      <span class="mid">&larr; &rarr; keys move between questions &middot; 1&ndash;4 picks an option &middot; the clock is a soft budget, it never cuts you off</span>
      <button class="btn" id="nextBtn" onclick="showQ(cur+1)">Next &rarr;</button>
    </div>
    <div class="banner mix" id="submitBox">
      <h2>Finished?</h2>
      <div style="font-size:.92rem" id="submitHint"></div>
      <div class="row"><button class="btn go" onclick="submitRound()">Submit answers</button></div>
    </div>
  </div>

"""

TIMER_LI = ('        <li>Every question carries a <b>soft time budget</b> (1:00 recall &middot; 1:30 standard &middot; 3:00 calculation). '
            'The clock turns amber at 75% and red when over, but <b>never cuts you off</b> &mdash; slow-but-correct answers are flagged in the review.</li>\n'
            '        <li>When the selection is mastered a <b>result page is downloaded</b> automatically (rounds, timings, every missed question with its working) &mdash; keep it in <code>Quiz/Results/</code>.</li>\n')

def must(n, what):
    if n != 1: raise SystemExit(f"{path}: patch '{what}' matched {n} times, expected 1")

# carry the file's own done title
m = (re.search(r'\? "([^"]+)" : "Selection mastered"', src)
     or re.search(r'const DONE_TITLE = "([^"]+)";', src))
eng = engine
if m:
    title = m.group(1)
    eng, n = re.subn(r'const DONE_TITLE = [^\n]*;\n', lambda _: 'const DONE_TITLE = "%s";\n' % title, eng, count=1)
    must(n, "done title")

if "   ENGINE  v2" in src:
    src, n = re.subn(r"/\* =+\n   ENGINE  v2.*?(?=/\* =+\n   EXAM LOCK)", lambda _: eng, src, count=1, flags=re.S)
    must(n, "engine refresh")
    print("already v2: engine refreshed")
else:
    src, n = re.subn(r"\n</style>", lambda _: CSS, src, count=1); must(n, "css")
    src, n = re.subn(r"(        <li>This repeats until <b>every selected question is correct</b>\.</li>\n)",
                     lambda m: m.group(1) + TIMER_LI, src, count=1); must(n, "intro li")
    src, n = re.subn(r"  <!-- ================= QUIZ ================= -->\n.*?(?=  <!-- ================= SUBMITTED)",
                     lambda _: QUIZ_MARKUP, src, count=1, flags=re.S); must(n, "quiz markup")
    src, n = re.subn(r'(<button class="btn go" id="rvBtn" onclick="nextRound\(\)">[^<]*</button>)',
                     lambda m: m.group(1) + ' <button class="btn ghost" onclick="downloadResult()">&#128229; Download result so far</button>',
                     src, count=1); must(n, "review btn")
    src, n = re.subn(r'(        <button class="btn" onclick="backToIntro\(\)">Choose different (?:lectures|chapters)</button>\n)',
                     lambda m: '        <button class="btn go" onclick="downloadResult()">&#128229; Download result page</button>\n' + m.group(1),
                     src, count=1); must(n, "done btn")
    # engine block, with or without its ENGINE banner comment
    src, n = re.subn(r"(?:/\* =+\n   ENGINE\n =+ \*/\n)?const BY_ID = .*?(?=/\* =+\n   EXAM LOCK)",
                     lambda _: eng, src, count=1, flags=re.S); must(n, "engine")

# per-type time budgets
def plain(s):
    return H.unescape(re.sub(r"<[^>]+>", "", s))

bank_start = src.index("const QUIZ = [")
bank_end = src.index("\n];", bank_start)
recs = re.split(r"(?m)^(?=\{id:)", src[bank_start:bank_end])
out, dist, lists = [recs[0]], {60: 0, 90: 0, 180: 0}, {60: [], 180: []}
for r in recs[1:]:
    head = re.match(r'\{id:(\d+), lec:"([^"]*)", blk:"([^"]*)", topic:"[^"]*",( t:\d+,)?', r)
    if not head: raise SystemExit(f"{path}: unparsed record: {r[:90]}")
    if head.group(4):
        out.append(r); continue
    qm = re.search(r'q:"(.*?)",\n', r, re.S); sm = re.search(r'sol:"(.*)"\}', r, re.S)
    qt = plain(qm.group(1)) if qm else ""; st = plain(sm.group(1)) if sm else ""
    eq = len(re.findall("=|⇒", st))            # working steps in the solution
    lec, blk = head.group(2), head.group(3)
    sb = lec == "SB" or blk.startswith("SB")
    if (eq >= 12 and len(qt) >= 80) or (sb and eq >= 6): t = 180
    elif eq <= 2 and not sb: t = 60
    else: t = 90
    dist[t] += 1
    if t in lists: lists[t].append(head.group(1))
    r2 = r[:head.end()] + " t:%d," % t + r[head.end():]
    out.append(r2)
src = src[:bank_start] + "".join(out) + src[bank_end:]
print("newly tagged:", dist, "| 60s:", ",".join(lists[60]), "| 180s:", ",".join(lists[180]))

if dry:
    print("dry run, nothing written"); sys.exit()
open(path, "w", encoding="utf-8", newline="").write(src.replace("\n", NL))
print("patched", path)
