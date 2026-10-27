"""RT-5 (16-11-2026) mock sets - 10 sets dealt from four book-checked sources.

    python tools/build_rt5.py            -> MockPapers/RT5-Mock-Sets.html
    then per set: python tools/build_questions.py RT5 <N>

Per subject per set (25): 6 past-ICAD + 3 Strong Box + 3 tagged JEE PYQ + 13 lecture exercises.
  * past-ICAD = questions of the eight real ICAD papers (codes <CH>XV<EXAM>Q<n>). RT-4 took 10 of its 75 from
    RT-3, the previous RT, so RT-4 and CAT-6 rank first; questions the student got wrong or left blank in
    the real exam rank above ones they got right.
  * Strong Box: every real paper used it (33 of 525 questions), Level 7-11 as often as its PYQ section.
  * tagged JEE PYQs: ~10-12% of recent papers; ICAD re-sets the same JEE question across exams.
  * lecture: the rest of each chapter's quota, round-robin over lectures; easy Suggested / Board rows get
    their share (CAT-6 lifted several verbatim and our CAT-6 sets had under-picked them).
Only book-checked rows (verified "ok") are used; nothing the student has seen in an earlier mock.
Chapter quotas: select_rt5.W (from the real RT-3 / RT-4 chapter shares).
"""
import collections, glob, io, json, os, re, sys, zlib

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CK = os.path.join(MP, "pool_check")
nat = lambda s: [int(t) if t.isdigit() else t for t in re.findall(r"\d+|\D+", s)]
CH = lambda c: re.match(r"[PCM]\d+[A-D]?", c).group(0)
hsh = lambda c: zlib.crc32(c.encode())

# chapter weights and the 'already seen' set come from the shortlist step
src = io.open(os.path.join(MP, "tools", "select_rt5.py"), encoding="utf-8").read()
sel = {"__file__": os.path.join(MP, "tools", "select_rt5.py")}
exec(compile(src.split("\npatch = collections")[0], "select_rt5", "exec"), sel)
W, target, used, exact, TAG, BANDS = (sel[k] for k in ("W", "target", "used", "exact", "TAG", "BANDS"))
NSETS, PER = 10, {"past": 6, "sb": 3, "pyq": 3, "lec": 13}

# printed-paper helpers (stem, has_choices, ans, repartition) - same judgement the paper will make
bq = os.path.join(MP, "tools", "build_questions.py")
g = {"__file__": bq}
argv = sys.argv; sys.argv = ["b", "CAT6", "1"]
exec(compile(io.open(bq, encoding="utf-8").read().split("\nfor subj, v in SETS.items():")[0], bq, "exec"), g)
sys.argv = argv
META, has_choices, ans = g["META"], g["has_choices"], g["ans"]

PAST = json.load(io.open(os.path.join(CK, "past_meta.json"), encoding="utf-8"))
RECENT = {"RT4": 2, "CAT6": 1.5, "RT3": 1.2, "CAT5": 1, "CAT4": .6, "RT2": .6, "CAT3": .4, "RT1": .4}
OWN = {"u": 2.2, "w": 2, "": 1.2, "c": .6}           # '' = RT-3, no result on file

def kind(c):
    l = META[c]["lec"]
    return "past" if l.endswith("X") else "sb" if l.endswith("SB") else "pyq" if c in TAG else "lec"

def usable(c):
    r = META[c]; a = ans(c)
    return (r.get("verified") == "ok" and r["sec"] != "Recap" and c not in used and c not in exact
            and CH(c) in W[c[0]] and W[c[0]][CH(c)] > 0 and "⚠" not in a and a.strip() not in ("", "-", "—")
            and (has_choices(c) or r.get("integer")))

def score(c):
    k = kind(c)
    if k == "past":
        m = PAST.get(c) or PAST.get(META[c].get("orig", ""), {})
        return OWN.get(m.get("st", ""), 1) + RECENT.get(m.get("exam"), .4) + (.3 if m.get("pyq") else 0)
    if k in ("sb", "pyq"):
        p = TAG.get(c, ""); yr = re.search(r"(19|20)\d\d", p)
        return ((2 if re.search(r"JEE Main|AIEEE", p) else 1 if p else 0) + (.5 if yr and int(yr.group(0)) >= 2015 else 0)
                + {"7": 1.5, "8": 1.5, "9": 1, "10": .5, "11": .5}.get(META[c]["sec"], 0))
    return 0

stemkey = lambda c: re.sub(r"[^a-z0-9]", "", (META[c]["stem"] or "").lower())[:80]

SETS = {}
report = []
for subj, name in (("P", "Physics"), ("C", "Chemistry"), ("M", "Mathematics")):
    T = target(subj, 25 * NSETS)
    cand = collections.defaultdict(list)
    for c in META:
        if c[0] == subj and usable(c): cand[kind(c)].append(c)
    for k in ("past", "sb", "pyq"): cand[k].sort(key=lambda c: (-score(c), hsh(c)))
    chosen, have, seen = [], collections.Counter(), set()
    noch = lambda c: not has_choices(c)
    def take(c):
        k = stemkey(c)
        if k in seen: return False
        if noch(c) and sum(map(noch, chosen)) >= 5 * NSETS: return False     # Part B holds 5 per set
        seen.add(k); chosen.append(c); have[CH(c)] += 1; return True
    # past / SB / PYQ: best first, never past a chapter's quota (past at most 40% of it)
    for k in ("past", "sb", "pyq"):
        n = 0
        for c in cand[k]:
            if n >= PER[k] * NSETS: break
            cap = T[CH(c)] if k != "past" else max(1, int(.4 * T[CH(c)] + .5))
            if have[CH(c)] < cap and sum(CH(x) == CH(c) and kind(x) == k for x in chosen) < cap and take(c): n += 1
    # lecture rows fill each chapter's quota: round-robin over its lectures, level bands in BANDS order
    lec = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
    for c in sorted(cand["lec"], key=hsh): lec[CH(c)][META[c]["lec"]][META[c]["sec"]].append(c)
    def fill(ch, n):
        got, i = 0, 0
        while got < n and any(any(b.values()) for b in lec[ch].values()):
            for L in sorted(lec[ch], key=nat):
                for j in range(len(BANDS)):
                    b = lec[ch][L].get(BANDS[(i + j) % len(BANDS)])
                    if b:
                        if take(b.pop(0)): got += 1
                        break
                if got >= n: break
            i += 1
        return got
    short = 0
    for ch in sorted(T, key=nat):
        short += max(0, T[ch] - have[ch]) - fill(ch, max(0, T[ch] - have[ch]))
    # a chapter that ran dry hands its slots to the rest, one at a time, largest quota first
    while short > 0:
        got = 0
        for ch in sorted(T, key=lambda k: -T[k]):
            if short <= 0: break
            n = fill(ch, 1); short -= n; got += n
        if not got: break
    assert len(chosen) == 25 * NSETS, (subj, len(chosen), short)

    # ---- deal: best first, each set gets PER[source] of each source, chapters spread evenly
    sets = [[] for _ in range(NSETS)]
    order = sorted(chosen, key=lambda c: (["past", "sb", "pyq", "lec"].index(kind(c)), -score(c), hsh(c)))
    for c in order:
        k = kind(c)
        cap = lambda s: sum(kind(x) == k for x in s) < PER[k] or k == "lec"
        s = min((s for s in sets if len(s) < 25 and cap(s)),
                key=lambda s: (noch(c) and sum(map(noch, s)) >= 5, sum(CH(x) == CH(c) for x in s), len(s)),
                default=None)
        if s is None: s = min((s for s in sets if len(s) < 25), key=len)
        s.append(c)
    # ---- Part B needs 5 numericals; at most 5 questions may lack printed choices (they all go to B)
    bcap = lambda c: noch(c) or META[c].get("integer")
    for _ in range(200):
        bad = [s for s in sets if sum(map(noch, s)) > 5 or sum(1 for x in s if bcap(x)) < 5]
        if not bad: break
        s = bad[0]
        if sum(map(noch, s)) > 5:
            out = next(x for x in s if noch(x))
            pick = lambda t, y: not noch(y) and kind(y) == kind(out) and sum(map(noch, t)) < 5
        else:
            out = next(x for x in s if not bcap(x))
            pick = lambda t, y: bcap(y) and not noch(y) and kind(y) == kind(out) and sum(1 for z in t if bcap(z)) > 5
        sw = [(t, y) for t in sets if t is not s for y in t if pick(t, y)]
        if not sw:
            raise SystemExit("cannot balance Part B in %s: no-choice per set %s, B-capable %s, by source %s" % (
                name, [sum(map(noch, x)) for x in sets], [sum(1 for z in x if bcap(z)) for x in sets],
                dict(collections.Counter(kind(c) for c in chosen if noch(c)))))
        t, y = min(sw, key=lambda ty: (CH(ty[1]) != CH(out), hsh(ty[1])))
        s[s.index(out)], t[t.index(y)] = y, out
    for i, s in enumerate(sets):
        a, b = g["repartition"](sorted(s, key=nat))
        SETS.setdefault(i + 1, {})[name] = (sorted(a, key=nat), sorted(b, key=nat))
    mix = collections.Counter(kind(c) for c in chosen)
    report.append("%-11s %s · %s" % (name, dict(mix), " ".join("%s %d" % (k, have[k]) for k in sorted(have, key=nat))))

# ---- render, in the CAT-6 sheet's format (build_questions / build_final read it)
master = io.open(os.path.join(MP, "CAT6-Mock-Sets.html"), encoding="utf-8").read()
head = master[:master.index("<body>")].replace("CAT-6 Mock Sets", "RT-5 Mock Sets")
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
legend = ("Every set = per subject 6 questions from the real ICAD papers (codes <code>{Ch}XV{Exam}Q{n}</code>, "
          "e.g. <code>P6XVRT4Q12</code> = RT-4 Q12; the ones you got wrong or left blank, and RT-4 / CAT-6, first) "
          "+ 3 Strong Box (<code>SB</code>) + 3 JEE previous-year questions + 13 lecture exercises "
          "(<code>{Lecture}V{Level}Q{n}</code>). Every question was checked against the printed book or paper and "
          "its answer re-derived; none appeared in an earlier mock. Chapter shares follow the real RT-3 and RT-4 "
          "papers: the CAT-6 chapters about a third, no chapter left out. Sit each set as the real exam: "
          "3 hours, one sitting, no notes; note when you finish each subject.")
html = (head + '<body><div class="wrap"><header id="top"><h1>ICAD RT-5 Mock Sets</h1><p>Exam 16-11-2026 · '
        '%d sets × 75 Q (25 Phy · 25 Chem · 25 Maths) · Part A 20 MCQ + Part B 5 Numerical · 4R−1W</p></header>'
        '<div class="legend">%s</div>%s</div></body></html>' % (NSETS, legend, "".join(cards)))
io.open(os.path.join(MP, "RT5-Mock-Sets.html"), "w", encoding="utf-8").write(html)
print("\n".join(report))
allc = [c for i in SETS for a, b in SETS[i].values() for c in a + b]
assert len(allc) == len(set(allc)) == 75 * NSETS
print("WROTE RT5-Mock-Sets.html · %d questions, no repeats" % len(allc))
