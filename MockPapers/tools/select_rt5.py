"""RT-5 (16-11-2026) candidate shortlist - what must be book-checked before the 10 sets can be dealt.

    python tools/select_rt5.py        -> pool_check/manifest_patch/<LEC>.json  (older lectures: lecture + PYQ picks)
                                       -> pool_check/manifest/<CH>SB.json       (older Strong Boxes: a shortlist)

The CAT-6 chapters (P9-P11, C6, M8D, M9) and their Strong Boxes are already book-checked in pool/; the older
chapters' pools are not, so only the shortlist is checked (`pool_check.py patch` writes the verdicts back into
pool/<LEC>.json in place). Per subject a set is 6 past-ICAD + 3 Strong Box + 3 tagged PYQ + 13 lecture.

Chapter weights (per 25) come from the real papers: in RT-3 / RT-4 the newest CAT block took 25-55% and the
older chapters kept a share in proportion to how often they had been asked (P4, P6, C4, C2 heavy; tool
chapters P1/P2/M1 almost only embedded).
"""
import collections, glob, io, json, os, re, sys, zlib

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(MP)
CK = os.path.join(MP, "pool_check")
nat = lambda s: [int(t) if t.isdigit() else t for t in re.findall(r"\d+|\D+", s)]
CH = lambda c: re.match(r"[PCM]\d+[A-D]?", c).group(0)

W = {"P": {"P1": 0, "P2": .5, "P3": 1, "P4": 4, "P5": 1.5, "P6": 4, "P7": 2, "P8": 3,
           "P9": 2.5, "P10": 3.5, "P11": 3},
     "C": {"C1": 2, "C2": 3, "C3": 3, "C4": 4, "C5": 5, "C6": 8},
     "M": {"M1": .5, "M2": 1, "M3": 1, "M4": 2, "M5A": 1, "M5B": .5, "M5C": 1, "M6": 2, "M7": 3,
           "M8A": 2, "M8B": 2, "M8C": 1, "M8D": 3, "M9": 5}}
CHECKED = {"P9", "P10", "P11", "C6", "M8D", "M9"}            # CAT-6: whole pool already book-checked
NSETS, SRC = 10, {"past": 6, "sb": 3, "pyq": 3, "lec": 13}      # per subject per set
FINALS = 6                                                     # SB/PYQ slack per subject for Final-A/B

def target(subj, n):
    """largest-remainder split of n over the subject's chapters by W"""
    w = W[subj]; tot = sum(w.values())
    raw = {k: n * v / tot for k, v in w.items()}
    q = {k: int(raw[k]) for k in w}
    for k in sorted(w, key=lambda k: raw[k] - q[k], reverse=True)[:n - sum(q.values())]: q[k] += 1
    return q

# ---- what the student has already seen: every earlier mock set, Final and chapter paper
used = set()
for f in glob.glob(os.path.join(MP, "*.html")) + glob.glob(os.path.join(MP, "ChapterPapers", "*.html")):
    if os.path.basename(f).startswith("RT5-"): continue          # RT-5's own sets and Finals
    used |= set(re.findall(r'<span class="code">([^<]+)</span>', io.open(f, encoding="utf-8").read()))
# lecture questions a real ICAD paper asked word for word - they come in as past-ICAD questions instead
exact = set()
for v in json.load(io.open(os.path.join(CK, "past_meta.json"), encoding="utf-8")).values():
    m = re.match(r"exact\s*([PCM]\d+[A-D]?)\s*·\s*(L[\dL]+)\s*·\s*(?:Lvl|Level)\s*(\w+)\s*·\s*Q(\d+)", v["bookref"])
    if m: exact.add("%s%sV%sQ%s" % m.groups())

POOL = {}
for f in glob.glob(os.path.join(MP, "pool", "*.json")):
    for r in json.load(io.open(f, encoding="utf-8")): POOL[r["code"]] = r

def secnorm(s):
    s = s.upper(); m = re.search(r"LEVEL[\s:-]*(\d+)", s)
    return m.group(1) if m else "PYQ" if "PREVIOUS" in s else "Sugg" if "SUGG" in s else "Board" if "BOARD" in s else None
TAG = {}
for p in glob.glob(os.path.join(ROOT, "YouTube_Solutions", "pyq_tags", "*.json")):
    if not re.fullmatch(r"[PCM]\d+[A-D]?", os.path.basename(p)[:-5]): continue
    for x in json.load(io.open(p, encoding="utf-8")):
        TAG["%sV%sQ%s" % (x["page"], secnorm(x["section"]), x["num"])] = x["paper"]

def askable(r):        # older pools hold paraphrased one-line stems; a letter key means the book prints options,
                       # and the book check restores the full printed question
    a = (r.get("answer") or "").strip()
    return (r["sec"] != "Recap" and a and "⚠" not in a and (r.get("has_opts") or re.match(r"^-?[\d.]+|^[a-dA-D][\s).,]", a))
            and not re.search(r"\b(prove|show that|derive|explain)\b", r["stem"] or "", re.I))

def pscore(c):
    p = TAG.get(c, ""); yr = re.search(r"(19|20)\d\d", p)
    return (2 if re.search(r"JEE Main|AIEEE", p) else 1) + (.5 if yr and int(yr.group(0)) >= 2015 else 0)

hsh = lambda c: zlib.crc32(c.encode())                         # deterministic, spread across a section
BANDS = ["Sugg", "5", "3", "4", "6", "Board", "2", "1"]        # CAT-6: easy Sugg/Board rows were under-picked

patch = collections.defaultdict(list)
report = []
for subj in "PCM":
    need = {s: target(subj, n * NSETS + (FINALS if s in ("sb", "pyq") else 0)) for s, n in SRC.items()}
    for ch in sorted(W[subj], key=nat):
        if ch in CHECKED or not W[subj][ch]: continue
        rows = [r for c, r in POOL.items() if CH(c) == ch and "SB" not in c and "X" not in r["lec"][len(ch):]
                and c not in used and c not in exact and askable(r)]
        # tagged PYQs first (they also cover the PYQ slots); 1.5x what the chapter's PYQ quota needs
        pyq = sorted((r for r in rows if r["code"] in TAG), key=lambda r: (-pscore(r["code"]), hsh(r["code"])))
        pyq = pyq[:int(need["pyq"][ch] * 1.5 + .999)]
        # lecture rows: round-robin over lectures, level bands in BANDS order, 1.3x the quota
        rest = [r for r in rows if r["code"] not in TAG]
        bylec = collections.defaultdict(lambda: collections.defaultdict(list))
        for r in rest: bylec[r["lec"]][r["sec"]].append(r)
        for l in bylec.values():
            for s in l: l[s].sort(key=lambda r: hsh(r["code"]))
        want, lec = int(need["lec"][ch] * 1.3 + .999), []
        i = 0
        while len(lec) < want and any(any(b.values()) for b in bylec.values()):
            for L in sorted(bylec, key=nat):
                for k in range(len(BANDS)):
                    b = bylec[L].get(BANDS[(i + k) % len(BANDS)])
                    if b: lec.append(b.pop(0)); break
                if len(lec) >= want: break
            i += 1
        for r in pyq + lec:
            patch[r["lec"]].append({"code": r["code"], "sec": r["sec"], "num": r["num"],
                                    "key": r["answer"], "stem": r["stem"]})
        report.append("%-4s target %3d · lecture %3d/%3d · PYQ %2d/%2d" % (ch, sum(need[s][ch] for s in need),
                      len(lec), need["lec"][ch], len(pyq), need["pyq"][ch]))

os.makedirs(os.path.join(CK, "manifest_patch"), exist_ok=True)
for lec, rows in patch.items():
    json.dump(sorted(rows, key=lambda r: nat(r["code"])), io.open(os.path.join(CK, "manifest_patch", lec + ".json"),
              "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- older Strong Boxes: shortlist 2x each chapter's SB quota; Level 7-9 and recent JEE Main / AIEEE first
exec(compile(io.open(os.path.join(MP, "tools", "pool_check.py"), encoding="utf-8").read().split('\nif __name__')[0],
             "pool_check", "exec"), pc := {"__file__": os.path.join(MP, "tools", "pool_check.py")})
old_sb = [ch for s in W for ch in W[s] if ch not in CHECKED and W[s][ch]
          and glob.glob(os.path.join(ROOT, "YouTube_Solutions", "**", ch + "SB_YouTube_Solutions.html"), recursive=True)]
pc["sbmanifest"](set(old_sb))                                  # full manifests, trimmed to the shortlist below
for ch in old_sb:
    p = os.path.join(CK, "manifest", ch + "SB.json")
    m = json.load(io.open(p, encoding="utf-8"))
    q = target(ch[0], SRC["sb"] * NSETS + FINALS)[ch]
    sc = lambda r: ({"7": 2, "8": 2, "9": 1.5, "10": .5, "11": .5}.get(r["sec"], 0)
                    + (pscore(r["code"]) if r["code"] in TAG else 0), -hsh(r["code"]))
    keep, per = [], collections.Counter()
    for r in sorted(m, key=sc, reverse=True):
        if len(keep) >= 2 * q + 2: break
        if per[r["sec"]] >= max(4, q): continue
        keep.append(r); per[r["sec"]] += 1
    json.dump(sorted(keep, key=lambda r: nat(r["code"])), io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    report.append("%-4s SB shortlist %2d of %3d (quota %d)" % (ch, len(keep), len(m), q))

print("\n".join(report))
print("patch manifests: %d lectures, %d questions" % (len(patch), sum(map(len, patch.values()))))
print("SB shortlists: %d chapters, %d questions" % (len(old_sb), sum(
      len(json.load(io.open(os.path.join(CK, "manifest", c + "SB.json"), encoding="utf-8"))) for c in old_sb)))
