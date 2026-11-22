"""Build an ExamPapers YouTube-Solutions page from solver rows.

  python build_exam_page.py <work dir> <out.html>

<work dir> holds rows/Q<NN>.json (see SOLVE_SPEC.md), page.json and optionally flag_note.json:
  page.json = {"title": "Revision Test 5 (16/11/2026)", "stem": "RT5-20261116", "scope": "<b>Scope:</b> ... "}
The scope text gets " {nbook} of 75 questions have a book reference; {nex} are exact." appended.
Head CSS + footer script are lifted from TPL with its result overlay and PYQ CSS stripped
(add_exam_results.py / add_pyq_tags.py re-add them; run both after every rebuild).
Run from the BooksScanned root."""
import json, glob, re, sys, html
sys.stdout.reconfigure(encoding='utf-8')
S = sys.argv[1]; OUT = sys.argv[2]
TPL = r"YouTube_Solutions/ExamPapers_YouTube_Solutions/CAT6-20261026_YouTube_Solutions.html"
cfg = json.load(open(S + '/page.json', encoding='utf-8'))
t = open(TPL, encoding='utf-8').read()
t = re.sub(r'<!--r-->.*?<!--/r-->\n?|/\*r\*/.*?/\*/r\*/\n?', '', t, flags=re.S)  # template's result overlay
t = re.sub(r"  /\* --- PYQ provenance tag.*?/\* --- end PYQ tag --- \*/\n", "", t, flags=re.S)  # template's PYQ CSS
head = t[:t.index('<body>') + len('<body>')]
head = re.sub(r'<title>.*?</title>', f'<title>EXCEL JEE-2028 · {cfg["title"]} · PCM · YouTube Solutions</title>', head, flags=re.S)
script = t[t.index('<script>', t.index('<footer')):]
assert 'myResult' not in head + script and 'pyq' not in head + script, 'template leak'


def normref(b):
    parts = b.split(' · ')
    if len(parts) >= 3:
        tail = parts[3:] if len(parts) > 3 and re.match(r'(Q|Ex)', parts[-1]) else []
        sec = ' · '.join(parts[2:len(parts) - len(tail)])
        m = re.search(r'(?i)level[\s:-]*(\d+)', sec)
        if m: sec = 'Lvl' + m.group(1)
        elif re.search(r'(?i)recap', sec): sec = 'Recap'
        elif re.search(r'(?i)board', sec): sec = 'Board'
        elif re.search(r'(?i)sugg', sec): sec = 'Sugg'
        elif re.search(r'(?i)previous year', sec): sec = 'PYQ'
        parts = parts[:2] + [sec] + tail
    return ' · '.join(parts)


rows = {}
for f in glob.glob(S + '/rows/Q*.json'):
    r = json.load(open(f, encoding='utf-8')); rows[int(r['num'])] = r
missing = [n for n in range(1, 76) if n not in rows]
if missing: print('MISSING', missing)
flags = [n for n in sorted(rows) if rows[n].get('flag')]
nbook = sum(1 for r in rows.values() if r.get('bookref_tag'))
nex = sum(1 for r in rows.values() if r.get('bookref_tag') == 'ex')


def row(r):
    n = r['num']
    vid = f'<a href="{r["video_url"]}" target="_blank">{r["video_title"]}</a>' if r.get('video_url') else '<span class="na">&mdash;</span>'
    badge = '<span class="badge exact">&#128994; Exact</span>' if r.get('match') == 'exact' else '<span class="badge sim">&#128993; Similar</span>'
    if not r.get('video_url'): badge = '<span class="na">&mdash;</span>'
    lt = f'<span class="lt">{r["ans_letter"]}</span>' if r.get('ans_letter') else ''
    if r.get('flag'):
        ans = f'<span class="ansval flagged">{lt}{r["ans_text"]} <span class="warn" title="{html.escape(r["flag"], quote=True)}">&#9888;</span></span>'
    else:
        ans = f'<span class="ansval">{lt}{r["ans_text"]}</span>'
    tag = r.get('bookref_tag')
    br = (f'<span class="rtag {tag}">{"exact" if tag == "ex" else "similar"}</span>{html.escape(normref(r["bookref"])).replace(" · ", " &middot; ")}'
          if tag else '<span class="na">&mdash;</span>')
    return (f'<tr><td class="num">{n}</td><td class="q">{r["q_html"]}</td><td class="topic">{r["topic"]}</td><td>{vid}</td><td>{badge}</td><td class="ans">{ans}</td><td class="bookref">{br}</td></tr>\n'
            f'<tr class="solnrow"><td colspan="7"><details class="soln"><summary></summary><div class="solnbody">{r["soln_html"]}</div></details></td></tr>\n')


secs = [('Physics', 'A', 'Single Correct', 1, 20), ('Physics', 'B', 'Numerical Value', 21, 25), ('Chemistry', 'A', 'Single Correct', 26, 45),
        ('Chemistry', 'B', 'Numerical Value', 46, 50), ('Mathematics', 'A', 'Single Correct', 51, 70), ('Mathematics', 'B', 'Numerical Value', 71, 75)]
body = []
for sub, p, kind, a, b in secs:
    body.append(f'<h2>{sub} &mdash; Part {p} &middot; {kind} (Q{a}&ndash;{b})</h2>\n<div class="tablecard"><div class="scroll"><table>\n<thead><tr><th>#</th><th>Question</th><th>Topic</th><th>YouTube</th><th>Match</th><th class="ans-h">Answer</th><th class="ref-h">Book&nbsp;Ref</th></tr></thead>\n<tbody>\n')
    body += [row(rows[n]) for n in range(a, b + 1) if n in rows]
    body.append('</tbody></table></div></div>\n\n')
flagtxt = json.load(open(S + '/flag_note.json', encoding='utf-8')) if glob.glob(S + '/flag_note.json') else ''
out = head + f'''
<div class="wrap">
<header>
  <h1>EXCEL JEE-2028 &middot; {cfg["title"]} &middot; PCM</h1>
  <p class="sub">Exam questions mapped to YouTube solution videos, with a full worked solution on every question</p>
  <div class="legend">
    <span class="badge exact">&#128994; Exact</span><span style="color:var(--muted);font-size:.82rem">video solves the same question (same numbers)</span>
    <span class="badge sim">&#128993; Similar</span><span style="color:var(--muted);font-size:.82rem">video teaches the same method / concept with different numbers</span>
  </div>
  <div class="note">{cfg["scope"]} {nbook} of 75 questions have a book reference; {nex} are exact.</div>
</header>

<div class="controls">
  <button id="ansBtn" class="ansbtn" type="button">&#128273; Show Answers</button>
  <span class="hint">Answers (from the paper's bundled <b>Answer Key</b>) are hidden by default &mdash; click to reveal all, or click any single blurred answer. &#9888; marks an answer that does not reconcile with independent working &mdash; hover for the correction.</span>
</div>

''' + ''.join(body) + f'''<div class="note" style="text-align:left;margin-top:26px">
  <b>Answer key.</b> {flagtxt}
</div>
<footer>ICAD &middot; EXCEL JEE-2028 &middot; {cfg["title"]} &middot; PCM &middot; Generated from {cfg["stem"]}</footer>
</div>
''' + script
open(OUT, 'w', encoding='utf-8').write(out)
print('rows', len(rows), 'flags', flags, 'book', nbook, 'exact', nex, 'bytes', len(out))
