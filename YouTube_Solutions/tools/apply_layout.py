"""Apply the compact question-table layout to lecture and Strong Box solution pages.

Per question row:
  - Topic moves under the question text (grey, small).
  - The mock-style code tag (qtag) moves from under the number to under the question, above the topic.
  - The Match badge moves into the YouTube cell, before the title; the Match column is dropped.
  - YouTube link text is cut to 20 characters + "…" with the full title on hover.
  - The three search pills sit on their own line under the title, starting at the same left edge.
  - Column widths: # 40px, Question auto, YouTube 25%, Answer 12%.
Solution rows span 4 columns instead of 6.

Exam pages (ExamPapers_YouTube_Solutions) are skipped. Pages already converted are skipped.
Pages whose rows don't have the expected cells are reported and left alone.

Usage: python apply_layout.py            (dry run)
       python apply_layout.py --write
"""
import glob, html, os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../YouTube_Solutions
WRITE = "--write" in sys.argv

HEAD_CSS = (
    "<style>"
    ".qtag{display:block;margin:6px 0 0;padding:1px 4px;border-radius:3px;background:#eef2f7;"
    "color:#3d4a63;font:10.5px/1.3 Consolas,ui-monospace,monospace;white-space:nowrap;width:max-content}"
    "td.qcell{min-width:200px}"
    ".topic-sub{color:var(--muted);font-size:.8rem;margin-top:4px;line-height:1.35}"
    "td.ytcell{width:25%;min-width:0}"
    ".yt-top{display:flex;align-items:center;gap:4px;flex-wrap:wrap}"
    ".yt-top .badge{flex:none}"
    ".yt-pills{margin-top:6px;margin-left:0}"
    ".yt-pills .qs-wrap{margin-left:0;flex-wrap:nowrap;white-space:nowrap}"
    ".ytt{display:inline}"
    "table{table-layout:fixed}"
    "thead th:first-child{width:40px;padding-left:6px;padding-right:4px}"
    "td.num{width:40px;padding-left:6px;padding-right:4px}"
    "td.qcell{width:auto}"
    "thead th:nth-child(3){width:25%}"
    "thead th:nth-child(4){width:12%;min-width:120px}"
    "td.ans{width:12%;min-width:120px}"
    "th.ans-h{min-width:120px}"
    "</style></head>"
)
NEW_HEADER = ('<thead><tr><th>#</th><th>Question</th><th>YouTube</th>'
              '<th class="ans-h">Answer</th></tr></thead>')
OLD_HEADER_RE = re.compile(r'<thead><tr><th>#</th><th>Question</th><th>Topic</th><th>YouTube</th><th>Match</th>.*?</tr></thead>', re.S)
ROW_RE = re.compile(r'<tr((?:\s[^>]*)?)>((?:(?!</tr>).)*?<td[^>]*class="num".*?)</tr>', re.S)
CELL_RE = re.compile(r'<td([^>]*)>(.*?)</td>', re.S)
QTAG_RE = re.compile(r'<span class="qtag">([^<]*)</span>')
PILLS_RE = re.compile(r'<span class="qs-wrap">.*?</span>', re.S)


def short_title(inner):
    txt = html.unescape(re.sub(r'<[^>]+>', '', inner)).strip()
    if len(txt) <= 20:
        return txt, txt
    return txt[:20].rstrip() + "…", txt


def yt_cell(cell_html, badge):
    pills = PILLS_RE.search(cell_html)
    pills_html = pills.group(0) if pills else ""
    body = cell_html.replace(pills_html, "") if pills_html else cell_html
    m = re.search(r'<a([^>]*)>(.*?)</a>', body, re.S)
    if m:
        attrs, inner = m.group(1), m.group(2)
        short, full = short_title(inner)
        attrs = re.sub(r'\s*title="[^"]*"', "", attrs)
        link = f'<a{attrs} title="{html.escape(full, quote=True)}">{html.escape(short, quote=False)}</a>'
    else:
        link = body.strip()
    top = f'<div class="yt-top">{badge}{link}</div>'
    bottom = f'<div class="yt-pills">{pills_html}</div>' if pills_html else ""
    return top + bottom


def convert_row(attrs, inner):
    cells = CELL_RE.findall(inner)
    if len(cells) != 6:
        return None
    (num_a, num), (q_a, q), (t_a, topic), (y_a, yt), (m_a, match), (a_a, ans) = cells
    tags = QTAG_RE.findall(num)
    if len(tags) != 1:
        return None
    code = tags[0]
    num_clean = QTAG_RE.sub("", num)
    badge = re.search(r'<span class="badge[^"]*">.*?</span>', match, re.S)
    badge = badge.group(0) if badge else ""
    qcell = (f'<td class="qcell"><div class="q">{q}</div>'
             f'<span class="qtag">{code}</span>'
             f'<div class="topic-sub">{topic}</div></td>')
    ycell = f'<td class="ytcell">{yt_cell(yt, badge)}</td>'
    return f'<tr{attrs}><td{num_a}>{num_clean}</td>{qcell}{ycell}<td{a_a}>{ans}</td></tr>'


def convert(text):
    """Return (new_text, stats) or (None, reason)."""
    if 'class="qcell"' in text:
        return None, "already converted"
    if 'class="num"' not in text:
        return None, "no question table"
    stats = Counter()
    failed = []

    def row(m):
        new = convert_row(m.group(1), m.group(2))
        if new is None:
            failed.append(m.group(0)[:80])
            return m.group(0)
        stats["rows"] += 1
        return new

    t = ROW_RE.sub(row, text)
    if failed:
        return None, f"{len(failed)} rows did not match the expected cells"
    if stats["rows"] == 0:
        return None, "no rows converted"
    t, n_hdr = OLD_HEADER_RE.subn(NEW_HEADER, t)   # every question table, not just the first
    if n_hdr == 0:
        return None, "header not found"
    stats["solnrow"] = t.count('<td colspan="6">')
    t = t.replace('<td colspan="6">', '<td colspan="4">')
    t = t.replace("</head>", HEAD_CSS, 1)
    return t, stats


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "**", "*_YouTube_Solutions.html"), recursive=True))
    files = [f for f in files if "ExamPapers_YouTube_Solutions" not in f
             and "exam_build" not in f and "PYQ_Audit" not in f]
    done, skipped, total = 0, [], Counter()
    for f in files:
        text = open(f, encoding="utf-8").read()
        new, info = convert(text)
        if new is None:
            skipped.append((os.path.relpath(f, ROOT), info))
            continue
        done += 1
        total.update(info)
        if WRITE:
            open(f, "w", encoding="utf-8", newline="").write(new)
    print(f"pages {'converted' if WRITE else 'to convert'}: {done}")
    print(f"rows: {total['rows']}   solution rows re-spanned: {total['solnrow']}")
    print(f"skipped: {len(skipped)}")
    for p, why in skipped:
        if why != "no question table":
            print("   ", p, "-", why)


if __name__ == "__main__":
    main()
