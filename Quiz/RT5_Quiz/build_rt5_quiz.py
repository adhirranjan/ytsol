#!/usr/bin/env python3
# Build RT-5 revision quizzes: 4 parallel sets x 3 subjects = 12 files, 25 Q each.
# Pulls questions verbatim from the per-chapter mastery quizzes, priority-weighted,
# lecture-spread, dealt into 4 non-overlapping parallel sets. Reuses the C6 engine.
import re, sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

QDIR = r"e:\Adhir\AdWinUser\Desktop\icad-dps\ICAD\BooksScanned\Quiz"
OUT  = os.path.join(QDIR, "RT5_Quiz")
os.makedirs(OUT, exist_ok=True)

# ---- allocation (total across the 4 sets), in priority order ----
PLAN = {
  "Physics": [("P8",16),("P10",12),("P9",10),("P11",10),("P4",12),("P6",12),
              ("P7",8),("P3",8),("P5",4),("P1",4),("P2",4)],
  "Chemistry": [("C6",24),("C5",20),("C2",16),("C3",16),("C1",12),("C4",12)],
  "Maths": [("M9",20),("M8D",12),("M7",12),("M5C",12),("M8A",8),("M8B",8),
            ("M6",8),("M5A",4),("M5B",4),("M1",3),("M2",3),("M3",3),("M4",3)],
}
TIER = {  # chapter -> tier label
  **{c:"Tier 1 · master first" for c in ["P8","P4","P6","P9","P10","P11","C6","C5","C3","M9","M8D","M5A","M5B","M5C"]},
  **{c:"Tier 2 · solid"        for c in ["P7","P3","P5","C2","C1","M6","M8A","M8B","M7"]},
  **{c:"Tier 3 · maintain"     for c in ["P1","P2","C4","M1","M2","M3","M4"]},
}

# ---------- array extraction helpers ----------
def slice_array(text, decl):
    """Return (start_idx_of_'[', end_idx_after_']') for `const NAME = [ ... ]`."""
    m = re.search(decl + r"\s*=\s*\[", text)
    i = text.index("[", m.start())
    depth, j, instr, esc = 0, i, False, False
    while j < len(text):
        ch = text[j]
        if instr:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': instr = False
        else:
            if ch == '"': instr = True
            elif ch == "[": depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0: return i, j + 1
        j += 1
    raise ValueError("unterminated array for " + decl)

def split_objects(body):
    """Split array body text into top-level {...} chunks."""
    chunks, depth, start, instr, esc = [], 0, None, False, False
    for k, ch in enumerate(body):
        if instr:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': instr = False
            continue
        if ch == '"': instr = True
        elif ch == "{":
            if depth == 0: start = k
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                chunks.append(body[start:k+1])
    return chunks

def load_chapter(code):
    p = os.path.join(QDIR, f"{code}_Quiz.html")
    txt = open(p, encoding="utf-8").read()
    i, j = slice_array(txt, r"const QUIZ")
    body = txt[i+1:j-1]
    qs = []
    for ch in split_objects(body):
        lec_m = re.search(r'lec:\s*"([^"]*)"', ch)
        qs.append({"raw": ch, "lec": lec_m.group(1) if lec_m else ""})
    h1 = re.search(r"<h1>(.*?)</h1>", txt, re.S).group(1).strip()
    return qs, h1

def spread(qs, n):
    """Pick n questions spread across lectures (round-robin over lec groups)."""
    groups = {}
    for q in qs:
        groups.setdefault(q["lec"], []).append(q)
    keys = list(groups)  # preserves first-seen (source) order
    out, idx = [], 0
    while len(out) < n and any(groups[k] for k in keys):
        g = groups[keys[idx % len(keys)]]
        if g: out.append(g.pop(0))
        idx += 1
    return out[:n]

# ---------- select + deal into 4 parallel sets ----------
CHAP_NAME = {}
def build_subject(subject, plan):
    sets = [[] for _ in range(4)]       # list of (chap, qdict)
    g = 0
    for code, total in plan:
        qs, h1 = load_chapter(code)
        CHAP_NAME[code] = h1
        if total > len(qs):
            raise SystemExit(f"{code}: asked {total} but pool has {len(qs)}")
        for q in spread(qs, total):
            sets[g % 4].append((code, q)); g += 1
    return sets

# ---------- HTML emission ----------
TEMPLATE = open(os.path.join(QDIR, "C6_Quiz.html"), encoding="utf-8").read()
TI, TJ = slice_array(TEMPLATE, r"const QUIZ")
LI, LJ = slice_array(TEMPLATE, r"const LECTURES")

def esc_js(s): return s  # names already safe

def chapter_order(subject):
    return [c for c, _ in PLAN[subject]]

def emit_set(subject, n, items):
    # keep chapters in subject priority order within the set
    order = chapter_order(subject)
    items = sorted(items, key=lambda ci: order.index(ci[0]))
    present = [c for c in order if any(ci[0] == c for ci in items)]

    # LECTURES array (one entry per chapter present)
    lec_lines = []
    for c in present:
        nm = CHAP_NAME[c].replace("&amp;", "&")
        lec_lines.append(f'  {{key:"{c}", name:{js_str(nm)}, desc:{js_str(TIER[c])}}}')
    lectures = "const LECTURES = [\n" + ",\n".join(lec_lines) + "\n]"

    # QUIZ array
    q_lines, nid = [], 0
    cur = None
    for code, q in items:
        if code != cur:
            cur = code
            q_lines.append(f"\n/* ---------------- {CHAP_NAME[code].replace('&amp;','&')} ---------------- */")
        nid += 1
        raw = q["raw"]
        origlec = q["lec"]
        raw = re.sub(r'\bid:\s*\d+', f'id:{nid}', raw, count=1)
        raw = re.sub(r'lec:\s*"[^"]*"', f'lec:"{code}"', raw, count=1)
        # fold original lecture into the blk label for context
        if origlec:
            raw = re.sub(r'blk:\s*"', f'blk:"{origlec} · ', raw, count=1)
        q_lines.append(raw + ",")
    quiz = "const QUIZ = [\n" + "\n".join(q_lines) + "\n]"

    # splice arrays into template (LECTURES first is earlier in file; order by index)
    out = TEMPLATE[:LI] + "[]" + TEMPLATE[LJ:]   # placeholder to keep indices simple
    # simpler: rebuild from original template with both replacements using indices on TEMPLATE
    out = TEMPLATE[:LI] + lectures[len("const LECTURES = "):] + TEMPLATE[LJ:TI] + quiz[len("const QUIZ = "):] + TEMPLATE[TJ:]

    # text swaps
    title = f"RT-5 {subject} · Revision Quiz — Set {n}"
    hero = (f'<header class="hero">\n'
            f'    <p>ICAD · RT-5 (16 Nov 2026) · {subject} revision</p>\n'
            f'    <h1>RT-5 {subject} · Set {n}</h1>\n'
            f'    <p id="heroSub">25 questions across {len(present)} chapters · priority-weighted · one of 4 parallel sets · loop until every answer is right.</p>\n'
            f'  </header>')
    foot = (f'<div class="foot">ICAD · RT-5 revision · {subject} Set {n} of 4 · '
            f'priority-weighted from your chapter &amp; study-priority analysis · '
            f'answers carried verbatim from the per-chapter mastery quizzes.</div>')

    out = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", out, count=1, flags=re.S)
    out = re.sub(r'<header class="hero">.*?</header>', lambda m: hero, out, count=1, flags=re.S)
    out = re.sub(r'<div class="foot">.*?</div>', lambda m: foot, out, count=1, flags=re.S)
    out = out.replace("Choose the lectures to be quizzed on", "Choose the chapters to be quizzed on")
    out = out.replace("All lectures are selected by default — that quizzes the whole chapter.",
                      "All chapters are selected by default — that runs the full 25-question set.")
    out = out.replace('"Chapter C-6 mastered"', f'"RT-5 {subject} Set {n} complete"')
    out = out.replace("Choose different lectures", "Choose different chapters")

    sub_code = {"Physics":"Phy","Chemistry":"Chem","Maths":"Maths"}[subject]
    fn = os.path.join(OUT, f"RT5_{sub_code}_Set{n}_Quiz.html")
    open(fn, "w", encoding="utf-8").write(out)
    return fn, len(items), present

def js_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

# ---------- run ----------
summary = []
set_dist = {}   # filename -> list of (chap, count) in priority order
for subject in ["Physics", "Chemistry", "Maths"]:
    sets = build_subject(subject, PLAN[subject])
    for n in range(1, 5):
        items = sorted(sets[n-1], key=lambda ci: chapter_order(subject).index(ci[0]))
        order = chapter_order(subject)
        dist = [(c, sum(1 for ci in items if ci[0]==c)) for c in order if any(ci[0]==c for ci in items)]
        fn, cnt, present = emit_set(subject, n, sets[n-1])
        bn = os.path.basename(fn)
        set_dist[(subject, n)] = (bn, dist)
        summary.append((bn, cnt, len(present)))

# ---------- folder index ----------
idx_tpl = open(os.path.join(QDIR, "Quiz_Index.html"), encoding="utf-8").read()
style = re.search(r"<style>.*?</style>", idx_tpl, re.S).group(0)
SUBMAP = {"Physics":"Phy", "Chemistry":"Chem", "Maths":"Maths"}
cards = []
for subject in ["Physics", "Chemistry", "Maths"]:
    cards.append(f'  <h2 class="sub">{subject} — 4 parallel revision sets · 25 Q each</h2>')
    for n in range(1, 5):
        bn, dist = set_dist[(subject, n)]
        chips = " · ".join(f"{c[0]}-{c[1:]} {v}" for c, v in dist)
        cards.append(
          f'  <a class="card" href="{bn}">\n'
          f'    <span class="tag">S{n}</span>\n'
          f'    <span><span class="nm">RT-5 {subject} · Set {n}</span>'
          f'<span class="ds">{chips}</span></span>\n'
          f'    <span class="ct">25 Q</span>\n'
          f'  </a>')
index = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RT-5 Revision Quizzes — Set Index</title>
{style}
</head>
<body>
<div class="wrap">
  <header class="hero">
    <p>ICAD · RT-5 · exam Mon 16 Nov 2026 · cumulative P1–P11, C1–C6, M1–M9</p>
    <h1>📘 RT-5 Revision Quizzes</h1>
    <p>12 priority-weighted sets (4 per subject, 25 Q each). Every set is a full-subject revision pass — do one set every few days before the exam. Questions are pulled from the per-chapter mastery quizzes; the 4 sets never repeat a question.</p>
  </header>

  <div class="stats">
    <div class="stat"><b>12</b><span>Sets</span></div>
    <div class="stat"><b>300</b><span>Questions</span></div>
    <div class="stat"><b>25</b><span>Per set</span></div>
    <div class="stat"><b>0</b><span>Repeats across sets</span></div>
  </div>

  <div class="howto">
    <h2>How to use these</h2>
    <ol>
      <li>Each set covers the <b>whole subject</b>, weighted to where you lose marks (C6/C5/C2, P8/P10/P9-11, M9/M8D heaviest).</li>
      <li>Do <b>Set 1</b> now, Set 2 in ~3 days, and so on — four fresh passes over everything before 16 Nov.</li>
      <li>Same loop as the chapter quizzes: Submit → compulsory review → re-quiz only what you missed, until all correct 🏆.</li>
      <li>Weak chapters appear in <b>every</b> set, so you drill them hardest and most often.</li>
    </ol>
  </div>

{chr(10).join(cards)}

  <div class="foot"><a href="../Quiz_Index.html" style="color:var(--brand2)">← All chapter mastery quizzes</a> · priority-weighted from your RT-5 chapter &amp; study-priority analysis</div>
</div>
</body>
</html>
"""
open(os.path.join(OUT, "RT5_Quiz_Index.html"), "w", encoding="utf-8").write(index)

print("Built:")
for name, cnt, chaps in summary:
    print(f"  {name}: {cnt} Q, {chaps} chapters")
print(f"\nTotal files: {len(summary)} + index  |  Total questions: {sum(c for _,c,_ in summary)}")
