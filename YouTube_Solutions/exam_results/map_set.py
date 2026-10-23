"""Re-number a result written on another set (e.g. 1B) onto the set the solutions page is built from (e.g. 1A).

  python map_set.py <Exam> [Q=L ...]   # e.g. RT1-20260713 7=B   (Q = page question, L = your letter in the page set)

The paper PDF bundles every set back to back (key page says "Test No : 1A" / "1B" ...). The result's key column picks
the student's set; each of its questions is matched to the page set's question by text (same subject block, must be
a bijection, both keys must agree in option content), MCQ letters are translated by option text, and the result is
written to <Exam>-Result.json beside this script, which add_exam_results.py then prefers over the PDF.
A letter whose option text is ambiguous (maths garbled by the text layer, image-only options) comes out as '?':
check both page images and pass it as Q=L. A correct answer always maps to the page key."""
import difflib, json, os, re, sys
import fitz

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import add_exam_results as R

HDR = re.compile(r"EXCEL JEE-2028|PART\s*:|^(PHYSICS|CHEMISTRY|MATHEMATICS|MATHS)$|SECTION|NOTE:|CHOOSE THE|NUMERICAL VALUE|^\d[A-D]$")


def sets(pdf):
    """{set code: (key page, [question pages])}. "Test No" is printed on the key page AND the instructions page,
    so a set starts at the first page naming it."""
    starts = []
    for i, p in enumerate(pdf):
        m = re.search(r"Test No\s*:\s*(\d[A-D])", p.get_text())
        if m and m.group(1) not in [c for _, c in starts]:
            starts.append((i, m.group(1)))
    ends = [s for s, _ in starts[1:]] + [pdf.page_count]
    return {code: (s, list(range(s + 1, e))) for (s, code), e in zip(starts, ends)}


def key(page):
    L = [l.strip() for l in page.get_text().splitlines() if l.strip()]
    return {int(m.group(1)): L[i + 1] for i, l in enumerate(L) for m in [re.fullmatch(r"(\d+)\.", l)] if m}


def questions(pdf, pages):
    t = "\n".join(l for p in pages for l in pdf[p].get_text().splitlines() if not HDR.search(l.strip()))
    parts = re.split(r"Q\.?\s*(\d+)\s*[):]", t)
    out = {}
    for i in range(1, len(parts), 2):
        body = parts[i + 1]
        opts = {k: " ".join(v.split()) for k, v in re.findall(r"\(([A-D])\)((?:(?!\([A-D]\)).)*)", body, re.S)}
        out[int(parts[i])] = {"raw": " ".join(body.split()), "opts": opts}
    return out


def same(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def main(exam, *overrides):
    pdf = fitz.open(os.path.join(ROOT, "ExamPapers", f"{exam}-AnswerKey-Question-Paper.pdf"))
    page = next(f for f in os.listdir(os.path.join(ROOT, "YouTube_Solutions", "ExamPapers_YouTube_Solutions")) if f.startswith(exam))
    page_set = re.search(r"-(\d[A-D])_YouTube", page).group(1)
    js = os.path.join(HERE, f"{exam}-Result.json")
    src = os.path.join(ROOT, "ExamPapers", f"{exam}-Result.pdf")
    rows, score = R.parse(src, 75) if os.path.exists(src) else ({}, "")
    if not rows:  # scanned result PDF (no text layer): use the hand transcription, numbered in the student's set
        d = json.load(open(js, encoding="utf-8"))
        assert "set_from" not in d, f"{js} is already mapped - restore the student-set transcription first"
        rows, score = {int(q): r for q, r in d["rows"].items()}, d.get("score", "")
    S = sets(pdf)
    keys = {c: key(pdf[k]) for c, (k, _) in S.items()}
    miss = {c: sum(rows[q]["key"].split("-")[0].upper() != keys[c].get(q, "").upper() for q in rows) for c in keys}
    mine = min(miss, key=miss.get)
    assert miss[mine] == 0, f"no set's key matches the result exactly: {miss}"
    print(f"{exam}: page is set {page_set}, result is set {mine}")
    if mine == page_set:
        return print("  same set - nothing to map")
    QA, QB, kA, kB = questions(pdf, S[page_set][1]), questions(pdf, S[mine][1]), keys[page_set], keys[mine]
    mp = {}
    for b in QB:  # match within the same 25-question subject block
        sc = sorted(((same(QB[b]["raw"], QA[a]["raw"]), a) for a in QA if (a - 1) // 25 == (b - 1) // 25), reverse=True)
        assert sc[0][0] >= 0.8 and sc[0][0] - sc[1][0] >= 0.1, f"weak match for {mine} Q{b}: {sc[:3]}"
        mp[b] = sc[0][1]
    assert len(mp) == 75 and len(set(mp.values())) == 75, "match is not a bijection"
    for b, a in mp.items():  # both keys must name the same answer
        x, y = kB[b], kA[a]
        ok = (same(QB[b]["opts"].get(x, ""), QA[a]["opts"].get(y, "")) >= 0.8) if x in "ABCD" and y in "ABCD" else x == y
        assert ok, f"key content differs: {mine} Q{b}={x} vs {page_set} Q{a}={y}"

    def letter(b, a, your):
        if your not in QB[b]["opts"]:
            return your  # numerical or blank
        sc = sorted(((same(QB[b]["opts"][your], QA[a]["opts"][L]), L) for L in QA[a]["opts"]), reverse=True)
        return sc[0][1] if sc[0][0] >= 0.8 and sc[0][0] - sc[1][0] >= 0.15 else "?"

    fix = dict(x.split("=") for x in overrides)
    out = {}
    for b, r in rows.items():
        a = mp[b]
        your = kA[a] if r["st"] == "c" else letter(b, a, r["your"])
        out[str(a)] = {"st": r["st"], "key": kA[a], "your": fix.get(str(a), your), f"set{mine}": f"Q{b}"}
    unsure = [a for a, r in out.items() if r["your"] == "?"]
    if unsure:
        print("  ambiguous - check both page images, then rerun with Q=L: "
              + ", ".join(f"page Q{a} (= {mine} {out[a]['set' + mine]}, you wrote {rows[int(out[a]['set' + mine][1:])]['your']})" for a in unsure))
    json.dump({"score": score, "set_from": mine, "set_to": page_set,
               "note": f"Student wrote Set {mine}; re-numbered to the Set {page_set} page by question text (map_set.py).",
               "rows": out}, open(js, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  wrote {os.path.basename(js)}: {score}")


if __name__ == "__main__":
    main(*sys.argv[1:])
