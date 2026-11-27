"""Link the question tags on mock result sheets to their solution rows.

Each <span class="tag">CODE</span> inside a result-sheet <td class="q"> is a source code. Forms seen:
  P12L3V5Q8        page P12L3, level 5, question 8          (lecture)
  P12L3VSuggQ5     page P12L3, Suggested Problems, Q5      (lecture)
  M10SBVPYQQ21     page M10SB, Strong Box PYQ, Q21         (Strong Box)
  M8BSBVPYQQ1      page M8BSB, Strong Box PYQ, Q1
  P10L6L7V3Q3      page P10L6L7 (two lectures in one file)
  C5XVRT4Q48       ICAD paper RT-4, question 48            (exam source; X marks it)

The code is resolved through YouTube_Solutions/tools/row_anchors.json and the tag is wrapped in
<a class="tag-link" target="_blank" href="<relative path>#<anchor>">. Unresolved codes stay plain
text and are reported. Idempotent: old tag links are removed before relinking.

Usage: python link_result_sheet.py <result-sheet.html> [...]
"""
import glob, json, os, re, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BOOKS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
YS = os.path.join(BOOKS, "YouTube_Solutions")
ANCHORS = os.path.join(YS, "tools", "row_anchors.json")

# stem = chapter (+ optional letter) + optional lecture(s) or Strong Box + optional X (exam marker)
CODE_RE = re.compile(r"^(?P<stem>[A-Z]+\d+[A-Z]?(?:(?:L\d+)+|SB)?X?)V(?P<lvl>Sugg|PYQ|Board|[A-Z]+\d+|\d+)Q(?P<num>\d+)$")
LINK_CSS = ("  a.tag-link{color:inherit;text-decoration:none;border-bottom:1px dotted var(--ink-soft)}" + chr(10)
            + "  a.tag-link:hover{color:var(--ink)}" + chr(10))
TAG_RE = re.compile(r'(<a [^>]*>)?<span class="tag">([^<]+)</span>(</a>)?')


def load_index():
    rows = json.load(open(ANCHORS, encoding="utf-8"))
    by_stem = defaultdict(list)
    for r in rows:
        by_stem[r["stem"]].append(r)
    paths = {}
    for f in glob.glob(os.path.join(YS, "**", "*_YouTube_Solutions.html"), recursive=True):
        paths[os.path.basename(f)] = f
    return by_stem, paths


def stems_for(stem, by_stem):
    """Exact stem, then any indexed stem of the same chapter that also covers these lectures
    (e.g. P3L6 is printed inside P3L6L7)."""
    if stem in by_stem:
        yield stem
    m = re.match(r"^([A-Z]+\d+[A-Z]?)((?:L\d+)+)$", stem)
    if not m:
        return
    want = set(re.findall(r"L\d+", m.group(2)))
    for other in by_stem:
        mo = re.match(r"^([A-Z]+\d+[A-Z]?)((?:L\d+)+)$", other)
        if mo and mo.group(1) == m.group(1) and other != stem and want <= set(re.findall(r"L\d+", mo.group(2))):
            yield other


def sec_matches(section, lvl, lecs):
    """Does an index section label match a code level (Sugg/PYQ/Board/digit)?
    Combined files label sections with their lecture, e.g. 'other-l6level1' (Lecture 6, Level 1)."""
    sec = section.lower()
    lec = re.search(r"(?:^|-)l(\d+)(?=[a-z])", sec)          # lecture tag inside the label
    if lec and lecs and ("L" + lec.group(1)) not in lecs:
        return False
    if lvl == "Sugg":
        return "sugg" in sec
    if lvl == "PYQ":
        return "pyq" in sec or "previous" in sec
    if lvl == "Board":
        return "board" in sec
    return (re.search(r"level" + re.escape(lvl) + r"(?!\d)", sec) is not None
            or sec == "l" + lvl or sec.endswith("-l" + lvl))


def resolve(code, by_stem):
    m = CODE_RE.match(code)
    if not m:
        return None, "unparsed"
    lvl, num = m["lvl"], m["num"]
    if re.match(r"^(RT|CAT)\d", lvl):          # ICAD paper: the exam page stem starts with the paper code
        cands = [r for k, rs in by_stem.items() if k.startswith(lvl + "-") for r in rs
                 if r["num"] == num]
    else:
        cands = []
        lecs = set(re.findall(r"L\d+", m["stem"]))  # lectures named by the code, e.g. {L6}
        for stem in stems_for(m["stem"], by_stem):   # exact stem first, then combined files
            cands = [r for r in by_stem.get(stem, []) if r["num"] == num
                     and sec_matches(r["section"], lvl, lecs)]
            if cands:
                break
    if not cands:
        return None, "no row"
    return cands[0], ("ambiguous" if len(cands) > 1 else "ok")


def link_file(path, by_stem, paths, here_dir):
    text = open(path, encoding="utf-8").read()
    stats = defaultdict(int)
    problems = []

    def repl(m):
        code = m.group(2)
        row, status = resolve(code, by_stem)
        if row is None:
            stats["unresolved"] += 1
            problems.append((code, status))
            return f'<span class="tag">{code}</span>'
        stats[status] += 1
        rel = os.path.relpath(paths[row["page"]], here_dir).replace(os.sep, "/")
        return (f'<a class="tag-link" target="_blank" rel="noopener" '
                f'href="{rel}#{row["anchor"]}"><span class="tag">{code}</span></a>')

    new = TAG_RE.sub(repl, text)
    if "a.tag-link" not in new:
        new = new.replace("  td.you{width:30%;", LINK_CSS + "  td.you{width:30%;", 1)
    open(path, "w", encoding="utf-8", newline="").write(new)
    return dict(stats), problems


def main():
    by_stem, paths = load_index()
    for path in sys.argv[1:]:
        path = os.path.abspath(path)
        stats, problems = link_file(path, by_stem, paths, os.path.dirname(path))
        print(os.path.basename(path), stats)
        for code, status in problems:
            print("   unresolved:", code, status)


if __name__ == "__main__":
    main()
