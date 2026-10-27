"""Build YouTube_Solutions/PYQ_Index.html: every PYQ-tagged row on one filterable page.

Reads the tagged pages themselves (run add_pyq_tags.py first), so it always matches them.
Usage:  python build_pyq_index.py
"""
import glob, html, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "PYQ_Index.html")

CHAPTERS = {
    "C1": "States of Matter", "C2": "Structure of Atom", "C3": "Mole Concept", "C4": "Periodic Properties",
    "C5": "Chemical Bonding", "C6": "Thermodynamics", "C7": "Chemical & Ionic Equilibrium",
    "P1": "Maths Tools-I", "P2": "Maths Tools-II", "P3": "Vectors", "P4": "Motion in 1D & 2D",
    "P5": "Force Systems", "P6": "Newton's Laws", "P7": "Friction", "P8": "Work, Energy & Power",
    "P9": "Collision", "P10": "Circular Motion", "P11": "Centre of Mass", "P12": "Rotational Motion",
    "P13": "Gravitation",
    "M1": "Measurement of Angles", "M2": "Sets", "M3": "Trig Ratios & Identities", "M4": "Functions-I",
    "M5A": "Compound Angles", "M5B": "Transformation Formulae", "M5C": "Multiple & Submultiple Angles",
    "M6": "Inequalities", "M7": "Exp & Log Equations", "M8A": "Arithmetic Progressions",
    "M8B": "Geometric Progressions", "M8C": "Harmonic Progressions", "M8D": "Special Series",
    "M9": "Complex Numbers", "M10": "Quadratic Equations", "M11": "Trig Equations", "M12": "Properties of Triangle",
}
SUBJ = {"C": "Chemistry", "P": "Physics", "M": "Maths"}
EXAMS = {"RT1": "13 Jul", "CAT3": "27 Jul", "RT2": "10 Aug", "CAT4": "31 Aug", "RT3": "21 Sep", "CAT5": "28 Sep", "RT4": "12 Oct", "CAT6": "26 Oct"}


def text(s):
    s = re.sub(r"<(br|/p|/div|/li)[^>]*>", " ", s)        # block breaks -> space, inline tags (sub/sup) -> nothing
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def nat(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


rows = []
for path in glob.glob(os.path.join(ROOT, "**", "*_YouTube_Solutions.html"), recursive=True):
    if "M-OLD" in path:
        continue
    page = os.path.basename(path).replace("_YouTube_Solutions.html", "")
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    exam = re.match(r"(RT\d|CAT\d)", page)
    if exam:
        ch, subj = exam[1], "ICAD exam papers"
        chname, where = f"{exam[1][:-1]}-{exam[1][-1]} · {EXAMS[exam[1]]} 2026", ""
    else:
        ch = re.match(r"([PCM]\d+[A-D]?)", page)[1]
        subj, chname = SUBJ[ch[0]], CHAPTERS[ch]
        where = page[len(ch):]                       # L4 / SB / L6L7 ...
    parts = re.split(r"(<h2[^>]*>.*?</h2>)", open(path, encoding="utf-8").read(), flags=re.S)
    for i in range(1, len(parts), 2):
        sec = re.sub(r"\s*\d+\s*Q$", "", text(parts[i]))
        # exam pages carry the result overlay: data-st="…" on the row, <!--r-->✓<!--/r--> in the # cell
        for aid, num, row in re.findall(r'<tr id="(pyq-[^"]+)"[^>]*><td class="num">([^<]+)(?:<!--r-->.*?<!--/r-->)?</td><td class="q">(.*?)</tr>', parts[i + 1], flags=re.S):
            q, paper, url = re.search(r'(.*?)<div class="pyq"><span class="paper">📝 PYQ: ([^<]+)</span><a href="([^"]+)"', row, flags=re.S).groups()
            q = text(q)
            yr = int(re.search(r"\d{4}", paper)[0])
            kind = "Main" if paper.startswith(("JEE Main", "AIEEE")) else "Advanced"
            rows.append(dict(s=subj, c=ch, cn=chname, w=(where + " · " if where else "") + sec, n=num.strip(),
                             q=q[:220] + ("…" if len(q) > 220 else ""), p=html.unescape(paper), y=yr, k=kind,
                             b=f"{rel}#{aid}", u=url, o=(nat(ch), nat(where), i, nat(num))))

ORDER = ["Physics", "Chemistry", "Maths", "ICAD exam papers"]
rows.sort(key=lambda r: (ORDER.index(r["s"]), r["o"]))
for r in rows:
    del r["o"]
chap = {}
for r in rows:
    chap.setdefault((r["s"], r["c"], r["cn"]), []).append(r["k"])

chips = ""
for s in ORDER:
    cs = [(c, cn, ks) for (ss, c, cn), ks in chap.items() if ss == s]
    chips += (f'<div class="chaprow"><div class="chapname">{s}</div><div class="chips">'
              + "".join(f'<button class="chip" data-c="{c}" title="{html.escape(cn)}">{c}<span class="qn">{len(ks)}</span></button>' for c, cn, ks in cs)
              + "</div></div>")

n_main = sum(r["k"] == "Main" for r in rows)
page = open(os.path.join(HERE, "pyq_index_template.html"), encoding="utf-8").read()
page = (page.replace("{{TOTAL}}", str(len(rows))).replace("{{MAIN}}", str(n_main)).replace("{{ADV}}", str(len(rows) - n_main))
        .replace("{{CHIPS}}", chips).replace("{{DATA}}", json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")))
open(OUT, "w", encoding="utf-8").write(page)
print(f"{len(rows)} rows ({n_main} Main, {len(rows) - n_main} Advanced) -> {OUT}")
want = sum(len(json.load(open(f, encoding="utf-8"))) for f in glob.glob(os.path.join(HERE, "*.json")))
assert len(rows) == want, f"pages hold {len(rows)} tags but the JSON files list {want} — re-run add_pyq_tags.py"
