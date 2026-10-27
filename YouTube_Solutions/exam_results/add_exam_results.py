"""Mark each question of an ExamPapers YouTube-Solutions page as correct / wrong / unsolved / cancelled
from the ICAD result PDF (ExamPapers/<Exam>-Result.pdf).

  python add_exam_results.py                      # every ExamPapers/*-Result.pdf -> its page
  python add_exam_results.py <Result.pdf> <page.html>
  python add_exam_results.py <rows.json> <page.html>   # scanned result with no text layer:
        {"score": "88/300", "rows": {"1": {"st": "c|w|u|x", "key": "B", "your": "B"}, ...}}

Idempotent: everything injected sits inside <!--r-->..<!--/r--> or /*r*/../*/r*/ and is stripped first."""
import glob, json, os, re, sys
import fitz

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAGES = os.path.join(ROOT, "YouTube_Solutions", "ExamPapers_YouTube_Solutions")

ST = {"Correct": "c", "Wrong": "w", "Unsolved": "u", "Canceled": "x"}
ANS = re.compile(r"^([A-D]{1,4}|null|[-\d.,]+)$")  # a "Your" cell: letter(s), null, number or answer array


def parse(pdf, nq):
    """nq = highest question number on the page; the result PDF sometimes prints the paper twice (Q76.. = Q1..)."""
    lines = [l.strip() for p in fitz.open(pdf) for l in p.get_text().splitlines() if l.strip()]
    start = lambda i: i + 1 < len(lines) and lines[i].isdigit() and lines[i + 1] in ST
    rows, arrays = {}, {}
    for i in range(len(lines)):
        if not start(i) or int(lines[i]) > nq:
            continue
        q = int(lines[i])
        key = lines[i + 2].split("-")[0]  # numerical keys print as "16-16"
        your = lines[i + 3] if i + 3 < len(lines) and not start(i + 3) and ANS.match(lines[i + 3]) else ""
        if "," in your:  # numerical section: whole answer array shown on its first row
            arrays[q] = your.split(",")
            your = ""
        rows[q] = {"st": ST[lines[i + 1]], "key": key, "your": "" if your == "null" else your}
    for q0, arr in arrays.items():
        for k, v in enumerate(arr):
            if v and q0 + k in rows:
                rows[q0 + k]["your"] = v
    text = "\n".join(lines)
    m = re.search(r"(\d+)\s*/\s*(\d+)\s*\nScore", text)
    score = f"{m.group(1)}/{m.group(2)}" if m else ""
    m = re.search(r"\nTotal\n(\d+)\n(\d+)\n(\d+)\n\d+\n(\d+)\n", text)  # Questions, Unsolved, Correct, -, Wrong
    if m:  # cross-check against the PDF's own summary (cancelled questions are not counted there)
        got = [sum(r["st"] != "x" for r in rows.values())] + [sum(r["st"] == k for r in rows.values()) for k in "ucw"]
        assert got == [int(g) for g in m.groups()], f"parsed q/u/c/w {got}, PDF summary says {list(m.groups())}"
    return rows, score


CSS = """/*r*/
  :root{--wrong-bg:#fde8e8;--wrong-ink:#b42318;--uns-bg:rgba(125,125,125,.14)}
  @media (prefers-color-scheme: dark){:root{--wrong-bg:#3b1616;--wrong-ink:#ff8a80}}
  .st{display:inline-block;margin-top:4px;min-width:22px;padding:1px 5px;border-radius:6px;font-size:.72rem;font-weight:800;text-align:center}
  .st.c{background:var(--exact-bg);color:var(--exact-ink)} .st.w{background:var(--wrong-bg);color:var(--wrong-ink)} .st.u,.st.x{background:var(--uns-bg);color:var(--muted)}
  tr[data-st=c]>td.num{box-shadow:inset 3px 0 var(--exact-ink)} tr[data-st=w]>td.num{box-shadow:inset 3px 0 var(--wrong-ink)} tr[data-st=u]>td.num,tr[data-st=x]>td.num{box-shadow:inset 3px 0 var(--line)}
  .mine{display:block;margin-top:5px;font-size:.76rem;font-weight:700;color:var(--wrong-ink)}
  .result{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:14px 0 4px;font-size:.88rem}
  .result b{margin-right:4px}
  .result button{appearance:none;cursor:pointer;border:1px solid var(--line);background:var(--card);color:var(--ink);font:600 12.5px/1 inherit;padding:7px 12px;border-radius:999px}
  .result button.on{background:var(--head);color:var(--headtxt);border-color:var(--head)}
/*/r*/
"""

JS = """<!--r--><script>
(function(){
  var bar=document.getElementById('myResult');
  bar.addEventListener('click',function(e){
    var b=e.target.closest('button'); if(!b) return;
    bar.querySelectorAll('button').forEach(function(x){x.classList.toggle('on',x===b)});
    var f=b.dataset.f;
    document.querySelectorAll('tr[data-st]').forEach(function(tr){
      var d=(f==='all'||tr.dataset.st===f)?'':'none';
      tr.style.display=d;
      var s=tr.nextElementSibling; if(s&&s.classList.contains('solnrow')) s.style.display=d;
    });
    document.querySelectorAll('.tablecard').forEach(function(t){
      var any=[].some.call(t.querySelectorAll('tr[data-st]'),function(r){return r.style.display!=='none'});
      t.style.display=any?'':'none';
      var h=t.previousElementSibling; if(h&&h.tagName==='H2') h.style.display=any?'':'none';
    });
  });
})();
</script><!--/r-->
"""

ICON = {"c": "&#10003;", "w": "&#10007;", "u": "&ndash;", "x": "&#8856;"}
NAME = {"c": "Correct", "w": "Wrong", "u": "Unsolved", "x": "Cancelled"}


def inject(html, rows, score):
    html = re.sub(r"<!--r-->.*?<!--/r-->\n?|/\*r\*/.*?/\*/r\*/\n?", "", html, flags=re.S)
    html = re.sub(r' data-st="[cwux]"', "", html)
    seen = set()

    def row(m):
        q = int(m.group(2))
        r = rows.get(q)
        if not r:
            return m.group(0)
        seen.add(q)
        return (f'<tr{m.group(1)} data-st="{r["st"]}"><td class="num">{q}'
                f'<!--r--><br><span class="st {r["st"]}" title="{NAME[r["st"]]}">{ICON[r["st"]]}</span><!--/r--></td>')

    html = re.sub(r'<tr((?: id="[^"]*")?)><td class="num">(\d+)</td>', row, html)
    missing = set(rows) - seen
    assert not missing, f"rows not found in HTML: {sorted(missing)}"

    # "You marked: X" under the answer for wrong ones (not blurred; doesn't give the key away)
    def ans(m):
        r = rows[int(m.group(1))]
        if r["st"] != "w":
            return m.group(0)
        return m.group(0)[:-5] + f'<!--r--><span class="mine">You marked: {r["your"] or "?"}</span><!--/r--></td>'

    html = re.sub(r'<td class="num">(\d+)<!--r-->.*?<td class="ans">.*?</td>', ans, html, flags=re.S)

    n = {k: sum(r["st"] == k for r in rows.values()) for k in "cwux"}
    btns = "".join(f'<button data-f="{k}">{ICON[k]} {NAME[k]} {n[k]}</button>' for k in "cwux" if n[k] or k != "x")
    bar = (f'<!--r--><div class="result" id="myResult"><b>&#128202; My result{" &middot; " + score if score else ""}</b>'
           f'<button class="on" data-f="all">All {len(rows)}</button>{btns}</div><!--/r-->\n')
    html = html.replace("</style>", CSS + "</style>", 1)
    html = re.sub(r'(<div class="controls">.*?</div>\n)', lambda m: m.group(1) + bar, html, count=1, flags=re.S)
    html = html.replace("</body>", JS + "</body>", 1)
    return html, n


def run(src, page):
    html = open(page, encoding="utf-8").read()
    if src.endswith(".json"):
        d = json.load(open(src, encoding="utf-8"))
        rows, score = {int(q): r for q, r in d["rows"].items()}, d.get("score", "")
    else:
        rows, score = parse(src, max(int(q) for q in re.findall(r'<td class="num">(\d+)', html)))
    assert rows, "no questions parsed (scanned PDF? transcribe it to <Exam>-Result.json beside this script)"
    # wrong-set guard: the page is one set (e.g. RT-1A); a result from another set has the questions shuffled
    page_keys = {int(q): k for q, k in re.findall(r'<td class="num">(\d+)</td>.*?<td class="ans"><span class="ansval[^"]*"><span class="lt">([A-D])<', html, re.S)}
    off = [q for q, k in page_keys.items() if q in rows and rows[q]["key"] != k]
    assert len(off) <= 10, f"page key differs from result key on {len(off)} MCQs - result is for a different set"
    out, n = inject(html, rows, score)
    open(page, "w", encoding="utf-8", newline="").write(out)
    print(f"{os.path.basename(page)}: {score}  correct {n['c']}  wrong {n['w']}  unsolved {n['u']}"
          + (f"  cancelled {n['x']}" if n["x"] else ""))
    print("  Wrong:", ", ".join(f"Q{q} (you {r['your'] or '?'}, key {r['key']})" for q, r in sorted(rows.items()) if r["st"] == "w"))


if __name__ == "__main__":
    if len(sys.argv) == 3:
        run(*sys.argv[1:3])
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        found = glob.glob(os.path.join(ROOT, "ExamPapers", "*-Result.pdf")) + glob.glob(os.path.join(here, "*-Result.json"))
        for exam in sorted({re.sub(r"-Result\.(pdf|json)$", "", os.path.basename(f)) for f in found}):  # e.g. RT4-20261012
            pdf = os.path.join(ROOT, "ExamPapers", exam + "-Result.pdf")
            js = os.path.join(here, exam + "-Result.json")  # a hand-transcribed result (e.g. from a photo) has no PDF
            pages = glob.glob(os.path.join(PAGES, exam + "*_YouTube_Solutions.html"))
            if len(pages) != 1:
                print(f"{exam}: skipped, {len(pages)} matching pages")
                continue
            try:
                run(js if os.path.exists(js) else pdf, pages[0])
            except AssertionError as e:
                print(f"{exam}: NOT updated - {e}")
