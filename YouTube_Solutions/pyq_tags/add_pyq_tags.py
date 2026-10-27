"""Tag YouTube Solutions rows that are real JEE PYQs with the paper + ExamGoal solution link.

Usage:  python add_pyq_tags.py P9 [P10 ... RT4-20261012]   (reads pyq_tags/<name>.json;
        a chapter, or one ExamPapers page named by its file stem)

<Ch>.json rows: {page, section, num, paper, url} -- section is the page's <h2> text
(question-count suffix like "9 Q" dropped), num is the row's # cell text.
Only number-verified matches belong in the JSON. Re-running is safe: old tags are
stripped before new ones are added.
"""
import glob, html, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CSS = """  /* --- PYQ provenance tag (pyq_tags/add_pyq_tags.py) --- */
  .pyq{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-top:7px;font-size:.76rem;font-weight:600}
  .pyq .paper{display:inline-block;padding:2px 10px;border-radius:999px;background:rgba(99,102,241,.13);color:#4f46e5;white-space:nowrap}
  .pyq a{white-space:nowrap}
  tr:target td{background:rgba(99,102,241,.10)}
  @media (prefers-color-scheme: dark){ .pyq .paper{background:rgba(129,140,248,.18);color:#a5b4fc} }
  /* --- end PYQ tag --- */
"""
# Legend goes on every checked page (even with 0 tags) so "checked, none found" is visible.
# Wrapped in display:contents + an end comment so strip() can find any older version.
LEGEND = ('<span class="pyqleg" style="display:contents"><span class="pyq" style="margin:0"><span class="paper">📝 JEE Main / Advanced paper</span></span>'
          '<span class="pyqlegend" style="color:var(--muted);font-size:.82rem">real JEE question, with ExamGoal&rsquo;s worked solution &middot; <b>{n}</b> on this page</span></span><!--/pyqleg-->')
LEGEND_MATH = ('<span class="pyqleg" style="display:contents"><span class="pyqlegend">📝 JEE paper — real JEE question, with ExamGoal&rsquo;s worked solution'
               ' &middot; <b>{n}</b> on this page</span></span><!--/pyqleg-->')
LEGEND_BADGE = ('<span class="pyqleg" style="display:contents"><span class="badge" style="background:#eef2ff;color:#4338ca">📝 JEE paper — real JEE question,'
                ' ExamGoal solution &middot; <b>{n}</b> on this page</span></span><!--/pyqleg-->')
OLD_LEGENDS = ['<span class="pyq" style="margin:0"><span class="paper">📝 JEE Main / Advanced paper</span></span>'
               '<span class="pyqlegend" style="color:var(--muted);font-size:.82rem">real JEE question, with ExamGoal&rsquo;s worked solution</span>',
               '<span class="pyqlegend">📝 JEE paper — real JEE question, with ExamGoal&rsquo;s worked solution</span>']
LEGEND_AFTER = [(r'<span class="badge sim">[^<]*Similar</span><span[^>]*>[^<]*</span>', LEGEND),  # Phy/Chem pages
                (r'<span><span class="dot similar"></span>[^<]*</span>', LEGEND_MATH),           # Math pages (on blue header)
                (r'<span class="badge sim">[^<]*Similar[^<]*</span>', LEGEND_BADGE)]              # badge-only legends (C1, C2, early Maths)


def section_key(h2):
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h2))).strip()
    return re.sub(r"\s*\d+\s*Q$", "", t)


def anchor(sec, num):
    """Row anchor used by PYQ_Index.html's Book links."""
    return "pyq-" + re.sub(r"[^a-z0-9]+", "-", f"{sec} {num}".lower()).strip("-")


def strip(h):
    h = re.sub(r"  /\* --- PYQ provenance tag.*?/\* --- end PYQ tag --- \*/\n", "", h, flags=re.S)
    h = re.sub(r'<span class="pyqleg".*?<!--/pyqleg-->', "", h, flags=re.S)
    for old in OLD_LEGENDS:
        h = h.replace(old, "")
    h = re.sub(r'<tr id="pyq-[^"]*"', "<tr", h)
    return re.sub(r'<div class="pyq"[^>]*>.*?</div>', "", h)


def tag(path, rows):
    h = strip(open(path, encoding="utf-8").read())
    want = {(r["section"], str(r["num"])): r for r in rows}
    h = h.replace("</style>", CSS + "</style>", 1)
    for pat, legend in LEGEND_AFTER:
        h, n = re.subn(f"({pat})", lambda m: m[1] + legend.format(n=len(rows)), h, count=1)
        if n:
            break
    parts = re.split(r"(<h2[^>]*>.*?</h2>)", h, flags=re.S)
    done = 0
    for i in range(1, len(parts), 2):
        sec = section_key(parts[i])

        def add(m):
            nonlocal done
            r = want.get((sec, m[2]))
            if not r:
                return m[0]
            done += 1
            return (f'<tr id="{anchor(sec, m[2])}"{m[1]}>' + m[0][len(m[1]) + 4:-5] + f'<div class="pyq"><span class="paper">📝 PYQ: {r["paper"]}</span>'
                    f'<a href="{r["url"]}" target="_blank" rel="noopener">Solution ↗</a></div></td>')

        # exam pages may already carry the result overlay (exam_results/add_exam_results.py)
        parts[i + 1] = re.sub(r'<tr((?: data-st="[cwux]")?)><td class="num">([^<]+)(?:<!--r-->.*?<!--/r-->)?</td><td class="q">.*?</td>',
                              add, parts[i + 1], flags=re.S)
    open(path, "w", encoding="utf-8").write("".join(parts))
    return done


if __name__ == "__main__":
    for ch in sys.argv[1:]:
        rows = json.load(open(os.path.join(HERE, ch + ".json"), encoding="utf-8"))
        # every page of the chapter (or the one exam page), tagged or not
        paths = (glob.glob(os.path.join(ROOT, "*", f"{ch}_YouTube_Solutions", "*_YouTube_Solutions.html"))
                 or glob.glob(os.path.join(ROOT, "**", f"{ch}_YouTube_Solutions.html"), recursive=True))
        for path in sorted(paths):
            page = os.path.basename(path).replace("_YouTube_Solutions.html", "")
            n = sum(r["page"] == page for r in rows)
            got = tag(path, [r for r in rows if r["page"] == page])
            print(f"{page}: tagged {got}/{n}")
            assert got == n, f"{page}: {n - got} rows not found"
