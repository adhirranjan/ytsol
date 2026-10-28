"""CAT-7 (30-11-2026) mock sets - 8 sets dealt from the book-checked CAT-7 pool (build_rt5.py, minus past-ICAD).

    python tools/build_cat7.py           -> MockPapers/CAT7-Mock-Sets.html
    python tools/figtool.py paper CAT7-Mock-Sets.html
    then per set: python tools/build_questions.py CAT7 <N>

Per subject per set (25):
  Physics / Maths  3 Strong Box + 3 JEE PYQ + 19 lecture
  Chemistry        2 JEE PYQ + 23 lecture  (no C7 Strong Box was scanned)
  * Strong Box = its Level 7-11 sections; JEE PYQ = tagged lecture rows, then the Strong Box's own PYQ
    section. P12's Strong Box has only 14 usable Level 7-11 rows, so its shortfall goes to PYQ slots.
  * lecture: round-robin over lectures, level bands in BANDS order; Level 1 left out (warm-up recall).
  * the rest of the Strong Box / PYQ rows stay unused for Final-A/B (build_final.py).
Only book-checked rows (verified "ok"); no corrected keys; nothing in an earlier mock.
"""
import collections, glob, io, os, re, sys, zlib

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
nat = lambda s: [int(t) if t.isdigit() else t for t in re.findall(r"\d+|\D+", s)]
CH = lambda c: re.match(r"[PCM]\d+[A-D]?", c).group(0)
hsh = lambda c: zlib.crc32(c.encode())

# 'already seen' set and the PYQ tags come from the RT-5 shortlist step
src = io.open(os.path.join(MP, "tools", "select_rt5.py"), encoding="utf-8").read()
sel = {"__file__": os.path.join(MP, "tools", "select_rt5.py")}
exec(compile(src.split("\npatch = collections")[0], "select_rt5", "exec"), sel)
TAG = sel["TAG"]
used = set()                                   # every earlier mock / Final / chapter paper, not CAT-7's own
for f in glob.glob(os.path.join(MP, "*.html")) + glob.glob(os.path.join(MP, "ChapterPapers", "*.html")):
    if not os.path.basename(f).startswith("CAT7-"):
        used |= set(re.findall(r'<span class="code">([^<]+)</span>', io.open(f, encoding="utf-8").read()))

W = {"P": {"P12": 1}, "C": {"C7": 1}, "M": {"M10": 1.1, "M11": .9}}   # M10 7 lectures / 417 Q, M11 6 / 321
NSETS = 8
PER = {"P": {"sb": 3, "pyq": 3}, "C": {"sb": 0, "pyq": 2}, "M": {"sb": 3, "pyq": 3}}
BANDS = ["Sugg", "5", "3", "4", "6", "Board", "2"]
# P12SBV9Q7: match table's row A sits on the previous page, too faded to crop
SKIP = {"P12SBV9Q7"}

def target(subj, n):
    w = W[subj]; tot = sum(w.values())
    raw = {k: n * v / tot for k, v in w.items()}
    q = {k: int(raw[k]) for k in w}
    for k in sorted(w, key=lambda k: raw[k] - q[k], reverse=True)[:n - sum(q.values())]: q[k] += 1
    return q

# printed-paper helpers (stem, has_choices, ans, repartition) - same judgement the paper will make
bq = os.path.join(MP, "tools", "build_questions.py")
g = {"__file__": bq}
argv = sys.argv; sys.argv = ["b", "CAT6", "1"]
exec(compile(io.open(bq, encoding="utf-8").read().split("\nfor subj, v in SETS.items():")[0], bq, "exec"), g)
sys.argv = argv
META, has_choices, ans = g["META"], g["has_choices"], g["ans"]

def kind(c):
    r = META[c]
    if r["lec"].endswith("SB"): return "pyq" if r["sec"] == "PYQ" else "sb"
    return "pyq" if c in TAG else "lec"

def usable(c):
    r = META[c]; a = ans(c)
    return (CH(c) in W[c[0]] and c not in SKIP and r.get("verified") == "ok" and r["sec"] != "Recap" and c not in used
            and "⚠" not in a and a.strip() not in ("", "-", "—") and (has_choices(c) or r.get("integer")))

def score(c):
    k = kind(c)
    if k == "lec": return 0
    p = TAG.get(c, "") or (META[c]["stem"] if META[c]["sec"] == "PYQ" else ""); yr = re.search(r"(19|20)\d\d", p)
    return ((2 if re.search(r"JEE Main|AIEEE", p) else 1 if p else 0) + (.5 if yr and int(yr.group(0)) >= 2015 else 0)
            + {"7": 1.5, "8": 1.5, "9": 1, "10": .5, "11": .5}.get(META[c]["sec"], 0)
            + (.3 if c in TAG else 0))                    # tagged lecture PYQ before the Strong Box's own PYQ section

stemkey = lambda c: re.sub(r"[^a-z0-9]", "", (META[c]["stem"] or "").lower())[:80]

SETS, report = {}, []
for subj, name in (("P", "Physics"), ("C", "Chemistry"), ("M", "Mathematics")):
    T = target(subj, 25 * NSETS)
    cand = collections.defaultdict(list)
    for c in META:
        if c[0] == subj and usable(c): cand[kind(c)].append(c)
    for k in ("sb", "pyq"): cand[k].sort(key=lambda c: (-score(c), hsh(c)))
    chosen, have, seen = [], collections.Counter(), set()
    noch = lambda c: not has_choices(c)
    def take(c):
        k = stemkey(c)
        if k in seen: return False
        if noch(c) and sum(map(noch, chosen)) >= 5 * NSETS: return False     # Part B holds 5 per set
        seen.add(k); chosen.append(c); have[CH(c)] += 1; return True
    # Strong Box first, then PYQ for its own slots plus whatever Strong Box could not fill
    need = {"sb": PER[subj]["sb"] * NSETS}
    for k in ("sb", "pyq"):
        n = 0
        if k == "pyq": need["pyq"] = (PER[subj]["sb"] + PER[subj]["pyq"]) * NSETS - got_sb
        for c in cand[k]:
            if n >= need[k]: break
            if have[CH(c)] < T[CH(c)] and take(c): n += 1
        if k == "sb": got_sb = n
    nsrc = {"sb": got_sb, "pyq": n}
    lec = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
    for c in sorted(cand["lec"], key=hsh): lec[CH(c)][META[c]["lec"]][META[c]["sec"]].append(c)
    def fill(ch, n, ok=lambda c: True):
        got, i = 0, 0
        while got < n and any(ok(c) for b in lec[ch].values() for s in BANDS for c in b.get(s, [])):
            for L in sorted(lec[ch], key=nat):
                for j in range(len(BANDS)):
                    b = [c for c in lec[ch][L].get(BANDS[(i + j) % len(BANDS)], []) if ok(c)]
                    if b:
                        lec[ch][L][BANDS[(i + j) % len(BANDS)]].remove(b[0])
                        if take(b[0]): got += 1
                        break
                if got >= n: break
            i += 1
        return got
    # Part B needs 5 integer answers per set: C7 has ~60 in all, so take them before the general fill
    bneed = 5 * NSETS - sum(1 for c in chosen if not has_choices(c) or META[c].get("integer"))
    for ch in sorted(T, key=nat):
        fill(ch, max(0, -(-bneed * T[ch] // sum(T.values()))), lambda c: META[c].get("integer"))
    short = 0
    for ch in sorted(T, key=nat):
        short += max(0, T[ch] - have[ch]) - fill(ch, max(0, T[ch] - have[ch]))
    assert not short and len(chosen) == 25 * NSETS, (subj, len(chosen), short)

    # ---- deal: best first, each set gets an even share of each source, chapters spread evenly
    cap_k = {k: -(-nsrc[k] // NSETS) for k in nsrc}
    sets = [[] for _ in range(NSETS)]
    order = sorted(chosen, key=lambda c: (["sb", "pyq", "lec"].index(kind(c)), -score(c), hsh(c)))
    for c in order:
        k = kind(c)
        cap = lambda s: k == "lec" or sum(kind(x) == k for x in s) < cap_k[k]
        s = min((s for s in sets if len(s) < 25 and cap(s)),
                key=lambda s: (noch(c) and sum(map(noch, s)) >= 5, sum(kind(x) == k for x in s),
                               sum(CH(x) == CH(c) for x in s), len(s)), default=None)
        if s is None: s = min((s for s in sets if len(s) < 25), key=len)
        s.append(c)
    # ---- Part B needs 5 numericals; at most 5 questions may lack printed choices (they all go to B)
    bcap = lambda c: noch(c) or META[c].get("integer")
    for _ in range(200):
        bad = [s for s in sets if sum(map(noch, s)) > 5 or sum(1 for x in s if bcap(x)) < 5]
        if not bad: break
        s = bad[0]; sw = []
        # try every swappable question in s, not just the first: Chemistry's PYQs have no integer partner
        for out in [x for x in s if noch(x)] if sum(map(noch, s)) > 5 else [x for x in s if not bcap(x)]:
            if sum(map(noch, s)) > 5:
                pick = lambda t, y: not noch(y) and kind(y) == kind(out) and sum(map(noch, t)) < 5
            else:
                pick = lambda t, y: bcap(y) and not noch(y) and kind(y) == kind(out) and sum(1 for z in t if bcap(z)) > 5
            sw = [(t, y) for t in sets if t is not s for y in t if pick(t, y)]
            if sw: break
        if not sw: raise SystemExit("cannot balance Part B in %s: no-choice %s, B-capable %s" % (
            name, [sum(map(noch, x)) for x in sets], [sum(1 for z in x if bcap(z)) for x in sets]))
        t, y = min(sw, key=lambda ty: (CH(ty[1]) != CH(out), hsh(ty[1])))
        s[s.index(out)], t[t.index(y)] = y, out
    for i, s in enumerate(sets):
        a, b = g["repartition"](sorted(s, key=nat))
        SETS.setdefault(i + 1, {})[name] = (sorted(a, key=nat), sorted(b, key=nat))
    mix = collections.Counter(kind(c) for c in chosen)
    left = {k: len(cand[k]) - mix[k] for k in ("sb", "pyq")}
    report.append("%-11s %s · %s · left for Finals %s" % (name, dict(mix), " ".join("%s %d" % (k, have[k]) for k in sorted(have, key=nat)), left))

# ---- render, in the CAT-6 sheet's format (build_questions / build_final read it)
master = io.open(os.path.join(MP, "CAT6-Mock-Sets.html"), encoding="utf-8").read()
head = master[:master.index("<body>")].replace("CAT-6 Mock Sets", "CAT-7 Mock Sets")
def grid(codes, start, key=False):
    return '<div class="grid">%s</div>' % "".join(
        '<div class="cell"><span class="n">%d</span><span class="code">%s</span>%s</div>'
        % (n, c, '<span class="ans">%s</span>' % ans(c) if key else "") for n, c in enumerate(codes, start))
cards = []
for i in range(1, NSETS + 1):
    card = ['<div class="setcard" id="s%d"><div class="sethead"><h2>Set %d</h2><a class="top" href="#top">top ↑</a></div>' % (i, i)]
    for s, (a, b) in SETS[i].items():
        card.append('<div class="subj"><h3>%s</h3><div class="subj"><h4>Part A · 20 MCQ (4R−1W)</h4>%s</div>'
                    '<div class="subj"><h4>Part B · 5 Numerical (4R−1W)</h4>%s</div></div>' % (s, grid(a, 1), grid(b, 21)))
    card.append('<details class="ansbox"><summary>Answer key — Set %d</summary>' % i)
    for s, (a, b) in SETS[i].items():
        for part, codes, st in (("A", a, 1), ("B", b, 21)):
            card.append('<div class="akey subj"><h4>%s · Part %s</h4>%s</div>' % (s, part, grid(codes, st, True)))
    card.append("</details></div>")
    cards.append("".join(card))
legend = ("Syllabus: P12 Rotational Motion · C7 Chemical &amp; Ionic Equilibrium · M10 Quadratic Equations, "
          "M11 Trigonometric Equations. Every set = per subject 3 Strong Box (<code>{Ch}SBV{Level}Q{n}</code>) "
          "+ 3 JEE previous-year questions (tagged lecture rows or the Strong Box PYQ section) + 19 lecture exercises "
          "(<code>{Lecture}V{Level}Q{n}</code>); Chemistry = 2 JEE PYQs + 23 lecture (no C7 Strong Box). "
          "Every question was checked against the printed book and its answer re-derived. Final-A/B come from "
          "your wrong and blank answers in Sets 1-8 plus unused Strong Box / PYQs. Sit each set as the real exam: "
          "3 hours, one sitting, no notes; note when you finish each subject.")
html = (head + '<body><div class="wrap"><header id="top"><h1>ICAD CAT-7 Mock Sets</h1><p>Exam 30-11-2026 · '
        '%d sets × 75 Q (25 Phy · 25 Chem · 25 Maths) · Part A 20 MCQ + Part B 5 Numerical · 4R−1W</p></header>'
        '<div class="legend">%s</div>%s</div></body></html>' % (NSETS, legend, "".join(cards)))
io.open(os.path.join(MP, "CAT7-Mock-Sets.html"), "w", encoding="utf-8").write(html)
print("\n".join(report))
allc = [c for i in SETS for a, b in SETS[i].values() for c in a + b]
assert len(allc) == len(set(allc)) == 75 * NSETS
print("WROTE CAT7-Mock-Sets.html · %d questions, no repeats" % len(allc))
