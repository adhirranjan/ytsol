"""Show each question's mock-style source code under its number on lecture / Strong Box pages.

Tag = <page stem>V<level>Q<num>, the same code the mock sets use, e.g. P12L3V5Q8, P12L3VSuggQ5,
P12L3VBoardQ1, M10SBVPYQQ21. Combined pages (P3L6L7) put the lecture in the code (P3L6V1Q1).
The tag sits in the number cell, after the number, so it shows below it.

Exam pages (ExamPapers_YouTube_Solutions) are skipped: their codes come from the mock side.
Depends on the anchors added by add_row_anchors.py (<span id="q-..."> inside td.num).

Idempotent: old qtag spans are removed first.
Usage: python add_question_tags.py            (dry run)
       python add_question_tags.py --write
"""
import glob, os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../YouTube_Solutions
WRITE = "--write" in sys.argv

QTAG_CSS = ("<style>.qtag{display:block;margin:3px 0 0;padding:1px 4px;border-radius:3px;"
            "background:#eef2f7;color:#3d4a63;font:10.5px/1.3 Consolas,ui-monospace,monospace;"
            "white-space:nowrap;width:max-content}</style></head>")
ANCHOR_RE = re.compile(r'<td class="num"><span id="(q-[^"]+)"></span>([^<]*)')
OLD_QTAG_RE = re.compile(r'<span class="qtag">[^<]*</span>')


def code_for(anchor):
    """anchor = q-<stem>-<section>-<num>  ->  mock-style code."""
    m = re.match(r"^q-([A-Za-z0-9]+)-(.+)-([^-]+)$", anchor)
    if not m:
        return None
    stem, sec, num = m.group(1), m.group(2), m.group(3)
    sec_l = sec.lower()
    # chapter for combined files: P3L6L7 -> chapter P3 ; Strong Box: P12SB -> keep SB
    chap = re.match(r"^([A-Z]+\d+[A-Z]?)(?=L\d|SB|$)", stem).group(1)
    base = stem if stem.endswith("SB") else None
    # section label
    lec = None
    lm = re.search(r"(?:^|-)l(\d+)(?=[a-z])", sec_l)           # 'other-l6level1' -> lecture 6
    if lm:
        lec = lm.group(1)
    if sec_l in ("sugg",) or "sugg" in sec_l:
        lvl = "Sugg"
    elif sec_l == "board" or "board" in sec_l:
        lvl = "Board"
    elif sec_l == "pyq" or "pyq" in sec_l or "previous" in sec_l:
        lvl = "PYQ"
    elif sec_l == "recap" or "recap" in sec_l:
        lvl = "Recap"
    else:
        lv = re.search(r"level(\d+)", sec_l) or re.fullmatch(r"l(\d+)", sec_l) \
             or re.search(r"-l(\d+)$", sec_l)
        if not lv:
            return None
        lvl = lv.group(1)
    if base is not None:                       # Strong Box page
        return f"{stem}V{lvl}Q{num}"
    if lec is not None:                        # combined lecture file: use the lecture, not the stem
        return f"{chap}L{lec}V{lvl}Q{num}"
    return f"{stem}V{lvl}Q{num}"


def process(path):
    text = open(path, encoding="utf-8").read()
    text = OLD_QTAG_RE.sub("", text)
    counts = Counter()
    bad = []

    def repl(m):
        code = code_for(m.group(1))
        if code is None:
            bad.append(m.group(1))
            return m.group(0)
        counts["tagged"] += 1
        return f'{m.group(0)}<span class="qtag">{code}</span>'

    # insert after the number text; OLD tags were removed so this is idempotent
    new = ANCHOR_RE.sub(repl, text)
    if "qtag{" not in new:
        new = new.replace("</head>", QTAG_CSS, 1)
    return new, counts, bad


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "**", "*_YouTube_Solutions.html"), recursive=True))
    files = [f for f in files if "ExamPapers_YouTube_Solutions" not in f
             and "exam_build" not in f and "PYQ_Audit" not in f]
    total, pages, unparsed = Counter(), 0, []
    for f in files:
        new, counts, bad = process(f)
        if not counts:
            continue
        pages += 1
        total.update(counts)
        if bad:
            unparsed.append((os.path.relpath(f, ROOT), bad[:3]))
        if WRITE:
            old = open(f, encoding="utf-8").read()
            if old != new:
                open(f, "w", encoding="utf-8", newline="").write(new)
    print(f"pages with question rows: {pages}")
    print(f"tags {'written' if WRITE else 'would be written'}: {total['tagged']}")
    print(f"unparsed anchors: {sum(len(b) for _, b in unparsed)} in {len(unparsed)} pages")
    for p, b in unparsed[:10]:
        print("   ", p, b)


if __name__ == "__main__":
    main()
