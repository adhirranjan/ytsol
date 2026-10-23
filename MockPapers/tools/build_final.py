"""Build a remediation "Final Set" from the questions the student missed in the marked mocks.

    python tools/build_final.py RT4 A     -> MockPapers/RT4-Final-A.html
    python tools/build_final.py RT4 B     -> MockPapers/RT4-Final-B.html (never repeats Final-A)

Then print it like any set:  python tools/build_questions.py RT4 Final-A

Pool = every wrong/blank row of mock-papers-result/<EXAM>-*-Result-Sheet.html (a Final set's own
sheet included, once it exists), minus questions already used by an earlier Final set, minus
flagged keys. Same rules as RT3-Final-Set (2026-09-20):
  * blank scores above wrong - a blank is a total non-start; at equal weight blanks lose every tie
  * chapter quota = geometric mean of the chapter's miss share and its mock-set exam prior
  * every lecture with 4+ misses is seeded one guaranteed slot before the quota fills
  * at most 2 questions per lecture (relaxed only if a chapter would otherwise run short)
  * misses from sheets marked AFTER the previous Final was built (Set 10, a Final's own sheet) get
    a small boost - the freshest evidence. Final-A has no earlier Final, so nothing is boosted.
Part A / Part B is decided by build_questions.repartition(): choices printed -> A, none -> B.
"""
import collections, glob, io, json, math, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAM = (sys.argv[1] if len(sys.argv) > 1 else "RT4").upper()
WHICH = (sys.argv[2] if len(sys.argv) > 2 else "A").upper()
NICE = EXAM.replace("RT", "RT-").replace("CAT", "CAT-")
LETTERS = "ABCDEFGH"[:"ABCDEFGH".index(WHICH)]          # earlier Finals: their picks are excluded

ROW = re.compile(r'<td class="q">\d+<span class="tag">([^<]+)</span></td>'
                 r'<td class="you([^"]*)">[^<]*</td><td class="key">(.*?)</td>')   # key may hold <sub>
CELL = re.compile(r'<span class="code">([^<]+)</span><span class="ans">([^<]*)</span>')
CHAP = lambda c: re.match(r"[PCM]\d+", c).group(0)               # M5A/B/C -> M5, M8A/B/C -> M8
LEC = lambda c: re.match(r"[PCM]\d+[A-D]?(?:(?:L\d+)+|SB)", c).group(0)
LEVEL = lambda c: re.search(r"V(\w+?)Q\d+$", c).group(1)
nat = lambda c: [int(t) if t.isdigit() else t for t in re.findall(r"\d+|\D+", c)]

# ---- the master sheet: every set's codes (for the exam prior) and its verified key text
master = io.open(os.path.join(MP, "%s-Mock-Sets.html" % EXAM), encoding="utf-8").read()
ANS = dict(CELL.findall(master))

# the printed papers' key is build_questions.ans() (book key + KEY_FIX); use it, not the grid text.
# A KEY_FIX carrying a warning means the book key itself is wrong - the "miss" may have been right
# (C2L10V6Q8: Set 9 answered "a, b", which is the correct answer), so it is no remediation material.
bq = os.path.join(MP, "tools", "build_questions.py")
g = {"__file__": bq}
argv = sys.argv; sys.argv = ["b", EXAM, "1"]
exec(compile(io.open(bq, encoding="utf-8").read().split("\nfor subj, v in SETS.items():")[0], bq, "exec"), g)
sys.argv = argv
ANS = {c: g["ans"](c) for c in ANS}
PRIOR = collections.Counter(CHAP(c) for c in ANS)

# ---- misses, oldest sheet first so the last one read is the newest
def sheet_order(p):
    n = re.search(r"-(?:Set(\d+)|Final-(?:Set-)?([A-H]))-Result", p)   # Final-A or Final-Set-A
    return (1, n.group(2)) if n.group(2) else (0, "%03d" % int(n.group(1)))
sheets = sorted((p for p in glob.glob(os.path.join(MP, "mock-papers-result", "%s-*-Result-Sheet.html" % EXAM))
                 if re.search(r"-(?:Set\d+|Final-(?:Set-)?[A-H])-Result", p)),    # not the real exam's sheet
                key=sheet_order)
MISS = {}                                   # code -> (blank, sheet)
FLAG = set()
hits = collections.Counter()                # lecture -> miss EVENTS: a question missed again in a
for p in sheets:                            # Final counts twice, lifting its lecture's siblings
    src = os.path.basename(p).replace("-Result-Sheet.html", "")
    for code, cls, key in ROW.findall(io.open(p, encoding="utf-8").read()):
        if "flagged" in key or "⚠" in key: FLAG.add(code)
        MISS[code] = ("blank" in cls, src)  # a later re-miss overwrites with the newer sheet
        hits[LEC(code)] += 1

used, seen = set(), set()
for L in LETTERS:
    f = os.path.join(MP, "%s-Final-%s.html" % (EXAM, L))
    if not os.path.exists(f): raise SystemExit("build Final-%s first (%s missing)" % (L, f))
    t = io.open(f, encoding="utf-8").read()
    used |= set(re.findall(r'<span class="code">([^<]+)</span>', t))
    seen |= set(re.search(r'data-sources="([^"]*)"', t).group(1).split(","))
fresh = {MISS[c][1] for c in MISS} - seen if LETTERS else set()

def usable(c):
    a = ANS.get(c, "")
    return (c not in used and c not in FLAG and "⚠" not in a
            and a.strip() not in ("", "-", "—", "?") and "not in key" not in a)

pool = [c for c in MISS if usable(c)]

def score(c):
    blank, src = MISS[c]
    lv = LEVEL(c)
    return (10.5 if blank else 10.0) + 0.5 * (hits[LEC(c)] - 1) \
        + {"5": .6, "6": .6, "4": .3}.get(lv, 0) + (1.0 if src in fresh else 0)

def quotas(codes, subj, n=25):
    """largest-remainder split of n by sqrt(miss share x prior share)"""
    ch = sorted({CHAP(c) for c in codes if c[0] == subj})
    m = collections.Counter(CHAP(c) for c in codes if c[0] == subj)
    P = sum(PRIOR[k] for k in ch); M = sum(m.values())
    w = {k: math.sqrt(PRIOR[k] / P * m[k] / M) for k in ch}; W = sum(w.values())
    raw = {k: n * w[k] / W for k in ch}
    q = {k: min(int(raw[k]), m[k]) for k in ch}
    for k in sorted(ch, key=lambda k: raw[k] - q[k], reverse=True):
        if sum(q.values()) == n: break
        if q[k] < m[k]: q[k] += 1
    return q

# ---- Strong Box / PYQ. CATs lift verbatim from the Strong Box of their own chapters (33 of 525
# questions in seven past ICAD exams, Level 7-11 as often as the PYQ section) and from PYQs, so a CAT
# Final carries SBMIX[subject] of them besides the misses: book-checked, never in a mock set.
SBMIX = {"CAT6": {"P": 7, "C": 6, "M": 7}}.get(EXAM, {})
META = g["META"]
# what kind each of those is: L = SB Level 7-11, S = SB PYQ section, T = JEE-PYQ-tagged lecture row.
# The 33 SB questions in past ICAD papers were 26 L / 7 S, and 17 of their 39 JEE PYQs sat in lecture
# exercises (2026-10-23) - so from Final-B on, the mix is fixed per subject instead of left to sbscore
KINDMIX = {("CAT6", "B"): {"P": {"L": 3, "S": 2, "T": 2}, "C": {"L": 4, "S": 1, "T": 1},
                           "M": {"L": 5, "S": 1, "T": 1}}}.get((EXAM, WHICH), {})
KIND = lambda c: "T" if not LEC(c).endswith("SB") else "S" if META[c]["sec"] == "PYQ" else "L"
BOOKCH = {re.match(r"[PCM]\d+[A-D]?", c).group(0) for c in ANS}          # M8D, not M8
def secnorm(s):
    s = s.upper(); m = re.search(r"LEVEL[\s-]*(\d+)", s)
    return m.group(1) if m else "PYQ" if "PREVIOUS" in s else "Sugg" if "SUGG" in s else "Board" if "BOARD" in s else None
TAG = {}                                                                  # code -> "JEE Main 2020 ..."
for ch in BOOKCH:
    p = os.path.join(MP, "..", "YouTube_Solutions", "pyq_tags", ch + ".json")
    for x in json.load(io.open(p, encoding="utf-8")) if os.path.exists(p) else ():
        TAG["%sV%sQ%s" % (x["page"], secnorm(x["section"]), x["num"])] = x["paper"]

def sbscore(c):
    p, yr = TAG.get(c, ""), re.search(r"(19|20)\d\d", TAG.get(c, ""))
    return (2 if re.search(r"JEE Main|AIEEE", p) else 1 if p else 0) + (.5 if yr and int(yr.group(0)) >= 2018 else 0)         + {"7": 1.5, "8": 1.5, "9": 1, "10": .5, "11": .5}.get(META[c]["sec"], 0) + LEC(c).endswith("SB")

SBPOOL = [c for c, r in META.items() if SBMIX and re.match(r"[PCM]\d+[A-D]?", c).group(0) in BOOKCH
          and (LEC(c).endswith("SB") or c in TAG) and r.get("verified") == "ok" and r["sec"] != "Recap"
          and c not in ANS and c not in used and (g["has_choices"](c) or r.get("integer"))
          and "⚠" not in g["ans"](c)]

def sbpick(subj, n, chosen):
    """n Strong Box / PYQ questions, split over the subject's chapters by miss count, at most 2 per
       book section; option-less ones only while Part B (5) still has room after the misses"""
    sp = sorted((c for c in SBPOOL if c[0] == subj), key=lambda c: (-sbscore(c), nat(c)))
    avail = collections.Counter(CHAP(c) for c in sp)
    w = {k: sum(CHAP(c) == k for c in MISS) or 1 for k in avail}; W = sum(w.values())
    q = {k: min(avail[k], int(n * w[k] / W)) for k in w}
    while sum(q.values()) < n and any(q[k] < avail[k] for k in w):
        k = max((k for k in w if q[k] < avail[k]), key=lambda k: n * w[k] / W - q[k]); q[k] += 1
    room = 5 - sum(not g["has_choices"](c) for c in chosen)
    kq = KINDMIX.get(subj)
    if kq and room > 0:     # fill Part B with real numericals, not MCQs printed with their options
        sp.sort(key=lambda c: g["has_choices"](c))
    out = []
    # relax in order: the chapter split, then the per-section cap; the kind mix goes last
    for cap, chap, kind in ((2, 1, 1), (2, 0, 1), (99, 0, 1), (99, 0, 0)) if kq else ((2, 1, 0), (99, 1, 0)):
        for c in sp:
            grp = lambda x: (LEC(x), META[x]["sec"])
            if (c in out or len(out) >= n
                    or chap and sum(CHAP(x) == CHAP(c) for x in out) >= q[CHAP(c)]
                    or kind and kq and sum(KIND(x) == KIND(c) for x in out) >= kq[KIND(c)]
                    or sum(grp(x) == grp(c) for x in out) >= cap): continue
            if not g["has_choices"](c):
                if room <= 0: continue
                room -= 1
            out.append(c)
    return out

pick, SBP = {}, []
for subj, name in (("P", "Physics"), ("C", "Chemistry"), ("M", "Mathematics")):
    N = 25 - SBMIX.get(subj, 0)
    sp = sorted((c for c in pool if c[0] == subj), key=lambda c: (-score(c), nat(c)))
    q = quotas(sp, subj, N)
    chosen = []
    # seeds: the best question of every lecture that has beaten the student 4+ times
    for lec in sorted({LEC(c) for c in sp if hits[LEC(c)] >= 4}, key=nat):
        chosen.append(next(c for c in sp if LEC(c) == lec))
    for k in q: q[k] = max(q[k], sum(CHAP(c) == k for c in chosen))
    while sum(q.values()) > N:                     # seeds pushed a chapter over: trim the largest
        k = max((k for k in q if q[k] > sum(CHAP(c) == k for c in chosen)), key=q.get); q[k] -= 1
    for cap in (2, 3, 99):
        for k in sorted(q, key=nat):
            for c in sp:
                if sum(CHAP(x) == k for x in chosen) >= q[k]: break
                if CHAP(c) == k and c not in chosen and sum(LEC(x) == LEC(c) for x in chosen) < cap:
                    chosen.append(c)
    for c in sp:                                     # chapters ran dry: top up from the best left
        if len(chosen) >= N: break
        if c not in chosen: chosen.append(c)
    sb = sbpick(subj, 25 - N, chosen) if N < 25 else []
    SBP += sb
    chosen += sb
    chosen += [c for c in sp if c not in chosen][:25 - len(chosen)]   # Strong Box ran short: more misses
    assert len(chosen) == 25, (subj, len(chosen))
    pick[name] = sorted(chosen, key=nat)
    print("%-11s %s" % (name, " · ".join("%s %d" % (k, n) for k, n in
          sorted(collections.Counter(CHAP(c) for c in chosen).items(), key=lambda x: nat(x[0])))))

ANS.update({c: g["ans"](c) for c in SBP})

# ---- Part A / B exactly as the printed paper will split them
parts = {s: g["repartition"](pick[s]) for s in pick}

# ---- render: same head/CSS as the master sheet, one setcard with id s1 (build_questions reads it)
head = master[:master.index('<body>')].replace("%s Mock Sets" % NICE, "%s Final Set %s" % (NICE, WHICH))
date = re.search(r"Exam ([\d-]+)", master).group(1)
nblank = sum(MISS[c][0] for s in pick.values() for c in s if c in MISS)
nmiss = sum(c in MISS for s in pick.values() for c in s)
srcs = collections.Counter(MISS[c][1] for s in pick.values() for c in s if c in MISS)
lecs = {LEC(c) for s in pick.values() for c in s if c in MISS}
seeded = sorted({l for l in lecs if hits[l] >= 4}, key=nat)
legend = ("Codes are book pointers <code>{Lecture}V{Level}Q{Number}</code> (<code>VBoard</code>/"
          "<code>VSugg</code> = Board/Suggested). Built only from what is not yet proven: %d questions "
          "you answered wrong and %d you left blank, taken from %s%s.%s %d lectures covered; every "
          "lecture that beat you four or more times is guaranteed a slot (%d of them); %d flagged "
          "keys are excluded. Chapter weighting = your error density blended with the %s exam prior. "
          "Answers are the book key (re-verify — ICAD keys are ~1-in-14 defective)."
          % (nmiss - nblank, nblank, ", ".join("%s: %d" % (re.sub(r"^\w+?-|Set-", "", k).replace("-", " ")
                                                       .replace("Set", "Set "), v)
                                           for k, v in sorted(srcs.items(), key=lambda x: nat(x[0]))),
             "" if WHICH == "A" else "; none of Final-%s's questions repeat" % "/".join(LETTERS),
             " Plus %d Strong Box / previous-year questions (<code>SB</code> codes, or tagged PYQs) — "
             "book-checked and never in a mock set: past CATs lifted questions verbatim from the "
             "Strong Box of the chapters they tested." % len(SBP) if SBP else "",
             len(lecs), len(seeded), len(FLAG), NICE))

def grid(codes, start, key=False):
    return '<div class="grid">%s</div>' % "".join(
        '<div class="cell"><span class="n">%d</span><span class="code">%s</span>%s</div>'
        % (n, c, '<span class="ans">%s</span>' % ANS[c] if key else "")
        for n, c in enumerate(codes, start))

card = ['<div class="setcard" id="s1" data-sources="%s"><div class="sethead"><h2>Final Set %s <span class="tier">%s</span>'
        '</h2><a class="top" href="#top">top ↑</a></div>'
        % (",".join(sorted({MISS[c][1] for c in MISS}, key=nat)), WHICH, "Your top-priority misses" if WHICH == "A" else "The next tier of misses")]
for s, (a, b) in parts.items():
    card.append('<div class="subj"><h3>%s</h3><div class="subj"><h4>Part A · 20 MCQ (4R−1W)</h4>%s</div>'
                '<div class="subj"><h4>Part B · 5 Numerical (4R−1W)</h4>%s</div></div>'
                % (s, grid(a, 1), grid(b, 21)))
card.append('<details class="ansbox"><summary>Answer key — Final Set %s</summary>' % WHICH)
for s, (a, b) in parts.items():
    for part, codes, st in (("A", a, 1), ("B", b, 21)):
        card.append('<div class="akey subj"><h4>%s · Part %s</h4>%s</div>' % (s, part, grid(codes, st, True)))
card.append('</details></div>')

html = (head + '<body><div class="wrap"><header id="top"><h1>ICAD %s Final Set %s</h1><p>Exam %s · 75 Q '
        '(25 Phy · 25 Chem · 25 Maths) · Part A 20 MCQ + Part B 5 Numerical · 4R−1W</p></header>'
        '<div class="legend">%s</div>%s</div></body></html>'
        % (NICE, WHICH, date, legend, "".join(card)))
out = os.path.join(MP, "%s-Final-%s.html" % (EXAM, WHICH))
io.open(out, "w", encoding="utf-8").write(html)
print("pool %d usable of %d missed (%d flagged, %d used by earlier Finals) · boosted %s"
      % (len(pool), len(MISS), len(FLAG), len(used & set(MISS)), sorted(fresh) or "none"))
print("seeded lectures:", " ".join("%s(%d)" % (l, hits[l]) for l in seeded))
print("blank %d · wrong %d · lectures %d · sources %s" % (nblank, nmiss - nblank, len(lecs), dict(srcs)))
for c in SBP: print("  SB %-14s %-6s %4.1f  %s" % (c, "A" if g["has_choices"](c) else "B", sbscore(c), TAG.get(c, "")))
print("SB/PYQ pool %d · picked %d" % (len(SBPOOL), len(SBP)))
print("WROTE", os.path.basename(out))
