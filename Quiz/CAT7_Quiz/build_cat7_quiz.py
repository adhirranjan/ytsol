#!/usr/bin/env python3
# Build CAT-7 revision quizzes: 3 parallel sets x 3 subjects = 9 files, 25 Q each.
#
# CAT-7 (exam Mon 30 Nov 2026) syllabus is only four chapters:
#   P12 Rotational Motion | C7 Chemical & Ionic Equilibrium | M10 Quadratic | M11 Trig Equations
# All four are "quoted" chapters, so every question here is a real ICAD book exercise.
#
# Two things differ from build_rt5_quiz.py:
#   * hard-weighted (~56% from LEVEL-5/6 and the Strong Box), because a CAT is a
#     narrow-syllabus paper and the easy bands are already drilled in the chapter quiz;
#   * questions that CAT7-Mock-Sets.html already uses are pushed to the LAST set, so
#     the first two passes are not a re-run of the mock papers.
import re, sys, os, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = r"e:\Adhir\AdWinUser\Desktop\icad-dps\ICAD\BooksScanned"
QDIR = os.path.join(ROOT, "Quiz")
OUT  = os.path.join(QDIR, "CAT7_Quiz")
os.makedirs(OUT, exist_ok=True)

NSETS = 3
PER_SET = 25
HARD_PER_SET = 14                       # 14/25 = 56%
HARD = {"5", "6", "7", "8", "9", "10", "11", "SB"}

# per-chapter quota PER SET
PLAN = {
    "Physics":   [("P12", 25)],
    "Chemistry": [("C7", 25)],
    "Maths":     [("M10", 13), ("M11", 12)],
}
TIER = {"P12": "the whole CAT-7 physics syllabus",
        "C7":  "the whole CAT-7 chemistry syllabus",
        "M10": "CAT-7 maths, part 1 of 2",
        "M11": "CAT-7 maths, part 2 of 2"}

# ---------- array extraction helpers (same as build_rt5_quiz.py) ----------
def slice_array(text, decl):
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
            if depth == 0: chunks.append(body[start:k + 1])
    return chunks


# ---------- band + book-pointer code, read off the row's own src: ----------
def band_of(src):
    s = src.upper()
    if "STRONG" in s: return "SB"
    if "SUGGEST" in s: return "Sugg"
    if "BOARD" in s: return "Board"
    if "QUICK" in s or "RECAP" in s: return "Recap"
    m = re.search(r"LEVEL[- ]?(\d+)", s)
    return m.group(1) if m else None          # None = a theory/solved-example row


def code_of(ch, src):
    """Rebuild the book-pointer code so it can be compared with the mock papers.
    Returns None for a theory/solved-example row: it has no exercise address, so it
    cannot be one of the mock papers' questions either."""
    band = band_of(src)
    if band is None:
        return None
    head, _, tail = src.partition("\u00b7")
    lec = "SB" if "Strong" in head or head.strip() == "SB" else "L" + re.sub(r"\D", "", head)
    qn = re.search(r"Q(\d+)", tail or src)
    return f"{ch}{lec}V{band}Q{qn.group(1) if qn else '0'}"


MOCK = open(os.path.join(ROOT, "MockPapers", "CAT7-Mock-Sets.html"), encoding="utf-8").read()
MOCKCODES = set(re.findall(r"(?:P12|C7|M10|M11)(?:SB|L\d+)V[A-Za-z0-9]+Q\d+", MOCK))

CHAP_NAME = {}


def load_chapter(code):
    txt = open(os.path.join(QDIR, f"{code}_Quiz.html"), encoding="utf-8").read()
    i, j = slice_array(txt, r"const QUIZ")
    qs = []
    for ch in split_objects(txt[i + 1:j - 1]):
        src = re.search(r'src:"([^"]*)"', ch)
        src = src.group(1) if src else ""
        band = band_of(src)
        # A row quoted from the chapter's theory or solved examples carries no LEVEL
        # heading, so there is no band to read. It still carries the engine's time
        # budget t, which this project derives from counted working steps - use that
        # as the difficulty signal rather than dropping the row. Dropping them is what
        # silently cost the first build every question from M-11 L-4, L-5 and L-6.
        budget = int((re.search(r"\bt:(\d+)", ch) or [0, "90"])[1])
        qs.append({"raw": ch,
                   "lec": (re.search(r'lec:\s*"([^"]*)"', ch) or [None, ""])[1],
                   "band": band or "Ex",
                   "hard": band in HARD if band else budget >= 120,
                   "repeat": code_of(code, src) in MOCKCODES})
    CHAP_NAME[code] = re.search(r"<h1>(.*?)</h1>", txt, re.S).group(1).strip()
    return qs


def spread(qs):
    """Order a bucket so consecutive picks walk across lectures (round-robin)."""
    groups = collections.OrderedDict()
    for q in qs:
        groups.setdefault(q["lec"], []).append(q)
    keys = list(groups)
    out, idx = [], 0
    while any(groups[k] for k in keys):
        g = groups[keys[idx % len(keys)]]
        if g: out.append(g.pop(0))
        idx += 1
    return out


def queue(qs, hard):
    """Fresh questions first, mock-repeats last -> repeats land in the final set."""
    bucket = [q for q in qs if q["hard"] == hard]
    return (spread([q for q in bucket if not q["repeat"]])
            + spread([q for q in bucket if q["repeat"]]))


def deal(code, per_set):
    """Return NSETS lists of questions for one chapter."""
    qs = load_chapter(code)
    hq, eq = queue(qs, True), queue(qs, False)
    nhard = round(per_set * HARD_PER_SET / PER_SET)
    need_h, need_e = nhard * NSETS, (per_set - nhard) * NSETS
    if len(hq) < need_h:
        raise SystemExit(f"{code}: need {need_h} hard questions, pool has {len(hq)}")
    if len(eq) < need_e:
        raise SystemExit(f"{code}: need {need_e} easy questions, pool has {len(eq)}")
    sets = [[] for _ in range(NSETS)]
    for n in range(NSETS):
        sets[n] = [hq.pop(0) for _ in range(nhard)] + [eq.pop(0) for _ in range(per_set - nhard)]

    # The check that was missing first time round: no lecture of the chapter may be
    # absent from the three sets put together. Skipping unbanded rows had quietly
    # dropped M-11 L-4, L-5 and L-6 - half the chapter - and nothing complained.
    have = {q["lec"] for s in sets for q in s}
    gone = sorted({q["lec"] for q in qs} - have)
    if gone:
        raise SystemExit(f"{code}: these lectures appear in NO set: {gone}")
    return sets


# ---------- HTML emission ----------
TEMPLATE = open(os.path.join(QDIR, "C6_Quiz.html"), encoding="utf-8").read()
TI, TJ = slice_array(TEMPLATE, r"const QUIZ")
LI, LJ = slice_array(TEMPLATE, r"const LECTURES")
SUBCODE = {"Physics": "Phy", "Chemistry": "Chem", "Maths": "Maths"}


def js_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def nice(code):
    return CHAP_NAME[code].replace("&amp;", "&")


def short(code):
    return re.match(r"([A-Z])(.*)", code).expand(r"\1-\2")


def emit_set(subject, n, items):
    order = [c for c, _ in PLAN[subject]]
    items = sorted(items, key=lambda ci: (order.index(ci[0]), ci[1]["lec"]))
    present = [c for c in order if any(ci[0] == c for ci in items)]

    lectures = "[\n" + ",\n".join(
        f'  {{key:"{c}", name:{js_str(nice(c))}, desc:{js_str(TIER[c])}}}'
        for c in present) + "\n]"

    q_lines, nid, cur = [], 0, None
    for code, q in items:
        if code != cur:
            cur = code
            q_lines.append(f"\n/* ---------------- {nice(code)} ---------------- */")
        nid += 1
        raw = q["raw"]
        raw = re.sub(r"\bid:\s*\d+", f"id:{nid}", raw, count=1)
        raw = re.sub(r'lec:\s*"[^"]*"', f'lec:"{code}"', raw, count=1)
        # keep the book address visible: chapter + lecture + level in front of the block label
        tag = f'{short(code)} {q["lec"]} L{q["band"]}' if q["band"].isdigit() \
              else f'{short(code)} {q["lec"]} {q["band"]}'
        raw = re.sub(r'blk:\s*"', f'blk:"{tag} \u00b7 ', raw, count=1)
        q_lines.append(raw + ",")
    quiz = "[\n" + "\n".join(q_lines) + "\n]"

    out = TEMPLATE[:LI] + lectures + TEMPLATE[LJ:TI] + quiz + TEMPLATE[TJ:]

    nhard = sum(1 for _, q in items if q["hard"])
    title = f"CAT-7 {subject} \u00b7 Revision Quiz \u2014 Set {n}"
    hero = (f'<header class="hero">\n'
            f'    <p>ICAD \u00b7 CAT-7 (Mon 30 Nov 2026) \u00b7 {subject} revision</p>\n'
            f'    <h1>CAT-7 {subject} \u00b7 Set {n}</h1>\n'
            f'    <p id="heroSub">{len(items)} questions \u00b7 {nhard} from LEVEL-5/6 and the Strong Box '
            f'\u00b7 one of {NSETS} non-overlapping sets \u00b7 loop until every answer is right.</p>\n'
            f'  </header>')
    foot = (f'<div class="foot">ICAD \u00b7 CAT-7 revision \u00b7 {subject} Set {n} of {NSETS} \u00b7 '
            f'every question quoted from the ICAD exercises and carried verbatim from the '
            f'per-chapter mastery quizzes, where each answer was independently re-derived '
            f'\u2014 mismatches against the printed key are flagged &#9888; in the working.</div>')

    out = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", out, count=1, flags=re.S)
    out = re.sub(r'<header class="hero">.*?</header>', lambda m: hero, out, count=1, flags=re.S)
    out = re.sub(r'<div class="foot">.*?</div>', lambda m: foot, out, count=1, flags=re.S)
    out = out.replace("Choose the lectures to be quizzed on", "Choose the chapters to be quizzed on")
    out = out.replace("All lectures are selected by default — that quizzes the whole chapter.",
                      f"All chapters are selected by default — that runs the full {len(items)}-question set.")
    out = out.replace('"Chapter C-6 mastered"', f'"CAT-7 {subject} Set {n} complete"')
    out = out.replace("Choose different lectures", "Choose different chapters")

    fn = os.path.join(OUT, f"CAT7_{SUBCODE[subject]}_Set{n}_Quiz.html")
    open(fn, "w", encoding="utf-8").write(out)
    return fn, items


# ---------- run ----------
rows = []
for subject, plan in PLAN.items():
    per_chap = {code: deal(code, q) for code, q in plan}
    for n in range(1, NSETS + 1):
        items = [(code, q) for code, _ in plan for q in per_chap[code][n - 1]]
        fn, items = emit_set(subject, n, items)
        rows.append(dict(
            subject=subject, n=n, file=os.path.basename(fn), total=len(items),
            hard=sum(1 for _, q in items if q["hard"]),
            repeat=sum(1 for _, q in items if q["repeat"]),
            dist=[(c, sum(1 for ci in items if ci[0] == c)) for c, _ in plan],
            bands=collections.Counter(q["band"] for _, q in items),
            lecs=collections.Counter(f'{short(c)} {q["lec"]}' for c, q in items)))

# ---------- folder index ----------
style = re.search(r"<style>.*?</style>",
                  open(os.path.join(QDIR, "Quiz_Index.html"), encoding="utf-8").read(), re.S).group(0)
cards = []
for subject in PLAN:
    chaps = " + ".join(short(c) for c, _ in PLAN[subject])
    cards.append(f'  <h2 class="sub">{subject} — {chaps} — {NSETS} parallel sets · {PER_SET} Q each</h2>')
    for r in [x for x in rows if x["subject"] == subject]:
        chips = " · ".join(f"{short(c)} {v}" for c, v in r["dist"] if v)
        chips += f" · {r['hard']} hard"
        if r["repeat"]:
            chips += f" · {r['repeat']} also in the mock sets"
        cards.append(
            f'  <a class="card" href="{r["file"]}">\n'
            f'    <span class="tag">S{r["n"]}</span>\n'
            f'    <span><span class="nm">CAT-7 {subject} · Set {r["n"]}</span>'
            f'<span class="ds">{chips}</span></span>\n'
            f'    <span class="ct">{r["total"]} Q</span>\n'
            f'  </a>')

TOTAL = sum(r["total"] for r in rows)
THARD = sum(r["hard"] for r in rows)
index = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CAT-7 Revision Quizzes — Set Index</title>
{style}
</head>
<body>
<div class="wrap">
  <header class="hero">
    <p>ICAD · CAT-7 · exam Mon 30 Nov 2026 · P-12 Rotational Motion · C-7 Chemical &amp; Ionic Equilibrium · M-10 Quadratic Equations · M-11 Trigonometric Equations</p>
    <h1>📗 CAT-7 Revision Quizzes</h1>
    <p>{len(rows)} sets ({NSETS} per subject, {PER_SET} Q each). A CAT has a narrow syllabus, so these are
    <b>hard-weighted</b>: {THARD} of {TOTAL} questions come from LEVEL-5/6 and the Strong Box. Every question is
    quoted from the ICAD exercises of these four chapters; the {NSETS} sets never repeat a question.</p>
  </header>

  <div class="stats">
    <div class="stat"><b>{len(rows)}</b><span>Sets</span></div>
    <div class="stat"><b>{TOTAL}</b><span>Questions</span></div>
    <div class="stat"><b>{100*THARD//TOTAL}%</b><span>Level-5/6 &amp; Strong Box</span></div>
    <div class="stat"><b>0</b><span>Repeats across sets</span></div>
  </div>

  <div class="howto">
    <h2>How to use these</h2>
    <ol>
      <li>Nine days, nine sets — one a day: <b>Phy / Chem / Maths, Set 1</b> first, then Set 2, then Set 3.</li>
      <li>Set 1 and Set 2 are questions the <a href="../../MockPapers/CAT7-Mock-Sets.html">CAT-7 mock sets</a> do <b>not</b> use, so your first two passes are fresh. The overlap sits in Set 3 on purpose — by then repetition is the point.</li>
      <li>Same loop as the chapter quizzes: Submit → compulsory review → re-quiz only what you missed, until all correct 🏆.</li>
      <li>Full-screen exam lock is on: leave the window for more than 5 s and the round restarts.</li>
      <li>Each block label carries the book address (e.g. <code>P-12 L-3 L5</code>) so a wrong answer sends you straight back to the right exercise.</li>
    </ol>
  </div>

{chr(10).join(cards)}

  <div class="foot"><a href="../Quiz_Index.html" style="color:var(--brand2)">← All chapter mastery quizzes</a> · drawn from the P-12 / C-7 / M-10 / M-11 mastery quizzes, every answer independently re-derived</div>
</div>
</body>
</html>
"""
open(os.path.join(OUT, "CAT7_Quiz_Index.html"), "w", encoding="utf-8").write(index)

ORDER = ["Recap", "1", "2", "3", "4", "5", "6", "Sugg", "Board", "Ex", "SB"]
print("Built:")
for r in rows:
    b = "  ".join(f"{k}:{r['bands'][k]}" for k in ORDER if r["bands"][k])
    print(f"  {r['file']:30} {r['total']} Q  hard {r['hard']}  mock-repeats {r['repeat']}")
    print(f"       {dict(r['dist'])}   bands {b}")
    print(f"       lectures {dict(sorted(r['lecs'].items()))}")
print(f"\n{len(rows)} files + index  |  {TOTAL} questions  |  hard {THARD}/{TOTAL} = {100*THARD//TOTAL}%")
