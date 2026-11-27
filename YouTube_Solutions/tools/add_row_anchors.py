"""Give every question row on a YouTube Solutions page a stable anchor.

Anchor = q-<PAGE>-<SECTION>-<NUM>, e.g. q-C1L3-L1-3 (page stem, section slug, printed number).
The anchor is an empty <span id> placed inside the row's <td class="num">, so existing
<tr id="pyq-level-..."> ids (used by PYQ_Index.html) are left untouched.

Idempotent: old q- spans are removed before the new ones are written.
Also writes tools/row_anchors.json (anchor -> page, section, num, question text, answer)
so mock result sheets can link to  <page>.html#<anchor>.

Usage:  python add_row_anchors.py            (dry run: counts + duplicate check)
        python add_row_anchors.py --write    (rewrite the files)
"""
import glob, html, json, os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../YouTube_Solutions
WRITE = "--write" in sys.argv

SEC_RE = re.compile(r'<h2(?:\s[^>]*)?>(.*?)</h2>', re.I | re.S)
NUM_RE = re.compile(r'<td class="num">([^<]*)')  # exam pages put result overlay markup after the number
OLD_SPAN_RE = re.compile(r'<span id="q-[^"]*"></span>')
TAG_RE = re.compile(r"<[^>]+>")


def slug(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def section_slug(h):
    h = html.unescape(TAG_RE.sub("", h)).replace("\xa0", " ").strip()
    prefix = ""
    if "·" in h:  # Strong Box style "Chemical Equilibrium · Level 7"
        topic, h = h.split("·", 1)
        prefix = slug(topic) + "-"
    h = h.strip()
    u = h.upper()
    return prefix + _base_slug(h, u)


def _base_slug(h, u):
    if u.startswith("QUICK RECAP"):
        return "recap"
    if u.startswith("SUGGESTED"):
        return "sugg"
    if u.startswith("PREVIOUS YEAR"):
        return "pyq"
    if re.match(r"LEVEL\s*:?\s*BOARD", u):
        return "board"
    m = re.match(r"LEVEL[\s-]*(\d+)", u)
    if m:
        return "L" + m.group(1)
    return "other-" + slug(h)[:12]


def question_text(row_html):
    m = re.search(r'<td class="q">(.*?)</td>', row_html, re.S)
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub("", m.group(1)))).strip() if m else ""


def answer_text(row_html):
    m = re.search(r'<td class="ans">(.*?)</td>', row_html, re.S)
    if not m:
        return ""
    lt = re.search(r'<span class="lt">([^<]*)</span>', m.group(1))
    return (lt.group(1).strip() if lt else "")


def process(path, collect):
    text = open(path, encoding="utf-8").read()
    stem = os.path.basename(path).replace("_YouTube_Solutions.html", "")
    text = OLD_SPAN_RE.sub("", text)
    sec = "none"
    out, pos, n = [], 0, 0
    seen = Counter()
    # walk section headings and number cells in document order
    events = [(m.start(), "sec", m) for m in SEC_RE.finditer(text)]
    events += [(m.start(), "num", m) for m in NUM_RE.finditer(text)]
    events.sort(key=lambda e: e[0])
    for start, kind, m in events:
        if kind == "sec":
            sec = section_slug(m.group(1))
            continue
        num = html.unescape(m.group(1)).strip()
        # exam papers: printed numbers are unique within the paper, so no section part
        anchor = f"q-{stem}-{slug(num)}" if "ExamPapers" in path else f"q-{stem}-{sec}-{slug(num)}"
        seen[anchor] += 1
        # row html = from this cell to the next row's start (for question/answer text)
        nxt = text.find("<tr", m.end())
        row = text[start:nxt if nxt != -1 else len(text)]
        collect.append({"anchor": anchor, "page": os.path.basename(path), "stem": stem,
                        "section": sec, "num": num, "question": question_text(row)[:200],
                        "answer": answer_text(row)})
        out.append(text[pos:start])
        out.append(f'<td class="num"><span id="{anchor}"></span>{m.group(1)}')
        pos = m.end()
        n += 1
    out.append(text[pos:])
    dups = [a for a, c in seen.items() if c > 1]
    return "".join(out), n, dups


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "**", "*_YouTube_Solutions.html"), recursive=True))
    files = [f for f in files if "_build" not in f and "exam_build" not in f]
    collect, total, bad, changed = [], 0, [], 0
    for f in files:
        new, n, dups = process(f, collect)
        total += n
        if dups:
            bad.append((os.path.relpath(f, ROOT), dups[:5]))
        if WRITE and not dups:
            old = open(f, encoding="utf-8").read()
            if old != new:
                open(f, "w", encoding="utf-8", newline="").write(new)
                changed += 1
    print(f"pages scanned: {len(files)}")
    print(f"question rows anchored: {total}")
    print(f"pages with duplicate anchors (NOT written): {len(bad)}")
    for p, d in bad[:20]:
        print("   ", p, d)
    if WRITE:
        print(f"pages rewritten: {changed}")
        idx = os.path.join(os.path.dirname(os.path.abspath(__file__)), "row_anchors.json")
        json.dump(collect, open(idx, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print("index written:", idx, len(collect), "entries")


if __name__ == "__main__":
    main()
