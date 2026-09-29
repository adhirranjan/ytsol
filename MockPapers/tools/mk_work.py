"""Build the per-chapter-group work files an authoring agent reads for one or more sets.

    python tools/mk_work.py RT4 10           -> work10_PHYA.json ... work10_MATHB.json

Each row carries the FULL stored stem (never truncated - capped stems produced seven false
"truncated stem" reports in an earlier round) plus needs_options, which is true when the stored
answer looks like an MCQ letter but the stem carries no printed choices.
"""
import glob, io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAM = (sys.argv[1] if len(sys.argv) > 1 else "RT4").upper()
SETNS = [int(x) for x in sys.argv[2:]] or [10]

META = {}
for f in os.listdir(os.path.join(MP, "pool")):
    for r in json.load(io.open(os.path.join(MP, "pool", f), encoding="utf-8")):
        META[r["code"]] = r
OPTS = set()
for f in glob.glob(os.path.join(MP, "options_*.json")):
    for k, v in json.load(io.open(f, encoding="utf-8")).items():
        if isinstance(v, dict) and v.get("options"): OPTS.add(k)

GROUP = {"PHYA": "P1 P2 P3 P4", "PHYB": "P5 P6 P7 P8", "CHEMA": "C1 C2",
         "CHEMB": "C3 C4 C5", "MATHA": "M1 M2 M3 M4 M5", "MATHB": "M6 M7 M8"}
GROUP = {g: tuple(v.split()) for g, v in GROUP.items()}

h = io.open(os.path.join(MP, "%s-Mock-Sets.html" % EXAM), encoding="utf-8").read()
cards = dict(zip(*[iter(re.split(r'<div class="setcard" id="s(\d+)">', h)[1:])] * 2))

rows = {g: [] for g in GROUP}
for sn in SETNS:
    for code in re.findall(r'<span class="code">([^<]+)</span>',
                           cards[str(sn)].split("<details")[0]):
        m = META[code]
        lec, sec, num = re.match(r"([A-Z]+\d+[A-C]?L\d+(?:L\d+)?)V(.+?)Q(\d+)$", code).groups()
        ch = re.match(r"([A-Z]+\d+)", code).group(1)
        grp = next(g for g, chs in GROUP.items() if ch in chs)
        ans = m["answer"].strip()
        mcq = bool(re.match(r"^[a-dA-D][\s).:,]", ans) or re.match(r"^[a-d](,\s*[a-d])+$", ans))
        rows[grp].append({"code": code, "set": sn, "lecture": lec, "section": sec, "number": int(num),
                          "needs_options": mcq and "(a)" not in m["stem"] and code not in OPTS,
                          "stem": m["stem"], "answer": ans})

print("Set(s) %s = %d questions" % (",".join(map(str, SETNS)), sum(len(v) for v in rows.values())))
for g, v in rows.items():
    p = os.path.join(MP, "work%s_%s.json" % ("".join(map(str, SETNS)), g))
    json.dump(v, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("  %-22s %2d questions  %2d lectures  %2d need options"
          % (os.path.basename(p), len(v), len({r["lecture"] for r in v}),
             sum(r["needs_options"] for r in v)))
