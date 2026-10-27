"""Find and crop a question's figure out of the scanned lecture PDFs.

The book PDFs are image-only (no text layer), so a question is located by RENDERING pages
and looking at them, not by searching text.

    python figtool.py pages P6L5              # render every page of that lecture -> PNGs, prints paths
                                              # (P6SB = its Strong Box, RT4 = the real RT-4 paper)
    python figtool.py crop P6L5V3Q2 7 0.12 0.34 0.88 0.61
                                              # crop page 7 using FRACTIONS of page width/height
                                              # (x0 y0 x1 y1, 0-1 from top-left) -> figures/<CODE>.png
    python figtool.py list                     # what has been cropped so far
    python figtool.py paper CAT6-Mock-Sets.html   # crop every figure that paper needs, from pool/ bboxes

Fractions are used rather than pixels so a crop does not depend on the dpi you previewed at.
"""
import os, re, sys, glob, json

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import fitz

MP    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT  = os.path.dirname(MP)
PAGES = os.path.join(os.environ.get("TEMP", "."), "icad_pages")
FIGS  = os.path.join(MP, "figures")
os.makedirs(PAGES, exist_ok=True)
os.makedirs(FIGS, exist_ok=True)

def chapter_of(lec):
    return re.match(r"([A-Z]+\d+[A-D]?)(?:L|SB)", lec).group(1)

def exam_pdf(exam):
    """a real ICAD paper, e.g. RT4 -> ExamPapers/RT4-20261012-AnswerKey-Question-Paper.pdf"""
    p = [p for p in glob.glob(os.path.join(ROOT, "ExamPapers", exam + "-*-AnswerKey-Question-Paper.pdf"))]
    if not p: raise SystemExit("no exam paper for " + exam)
    return p[0]

def find_pdf(lec):
    if re.fullmatch(r"(?:RT|CAT)\d+", lec): return exam_pdf(lec)      # past-paper codes <CH>XV<EXAM>Q<n>
    """lecture files are named either '<CH>L<n>.pdf' or plain 'L<n>.pdf' depending on the chapter"""
    ch = chapter_of(lec)
    base = [p for p in glob.glob(os.path.join(ROOT, "*", ch)) if os.path.isdir(p)]
    if not base:
        raise SystemExit("no source folder for chapter " + ch)
    base = base[0]
    tail = lec[len(ch):]                      # "L5", or "SB" for the Strong Box
    if tail == "SB":
        sb = glob.glob(os.path.join(base, "*Strong*Box*.pdf"))
        if sb: return sorted(sb)[0]
    for cand in ("%s.pdf" % lec, "%s.pdf" % tail):
        p = os.path.join(base, cand)
        if os.path.exists(p):
            return p
    # some lectures share one scan, named e.g. "L2&L3.pdf" or "P3L3L4.pdf" - match on the L-numbers
    want = re.findall(r"L(\d+)", tail)
    for p in sorted(glob.glob(os.path.join(base, "*.pdf"))):
        got = re.findall(r"(?:L|&)(\d+)", os.path.basename(p))   # "L5L6", "L2&L3", "L6&7"
        if got and all(w in got for w in want):
            return p
    raise SystemExit("no PDF for %s in %s -> %s" % (lec, base, os.listdir(base)))

def cmd_pages(lec, dpi=130):
    pdf = find_pdf(lec)
    d = fitz.open(pdf)
    out = []
    for i in range(d.page_count):
        p = os.path.join(PAGES, "%s_p%02d.png" % (lec, i + 1))
        if not os.path.exists(p):
            d[i].get_pixmap(dpi=int(dpi)).save(p)
        out.append(p)
    print("%s -> %d pages (%s)" % (pdf, d.page_count, PAGES))
    for i, p in enumerate(out, 1):
        print("  p%02d  %s" % (i, p))

def cmd_crop(code, page, x0, y0, x1, y1, dpi=220):
    """crop by page fractions; re-renders that page at high dpi so the figure stays sharp"""
    x = re.match(r"[A-Z]+\d+[A-D]?XV((?:RT|CAT)\d+)Q\d+$", code)
    lec = x.group(1) if x else re.match(r"([A-Z]+\d+[A-D]?(?:L\d+(?:L\d+)?|SB))V", code).group(1)
    d, page = fitz.open(find_pdf(lec)), int(page)
    if lec.endswith("SB"):        # a Strong Box split over "Strong Box 1.pdf", "... 2.pdf": pages run on
        rest = sorted(glob.glob(os.path.join(os.path.dirname(find_pdf(lec)), "*Strong*Box*.pdf")))[1:]
        while page > d.page_count and rest:
            page -= d.page_count; d = fitz.open(rest.pop(0))
    pg = d[page - 1]
    r = pg.rect
    clip = fitz.Rect(r.x0 + float(x0) * r.width, r.y0 + float(y0) * r.height,
                     r.x0 + float(x1) * r.width, r.y0 + float(y1) * r.height)
    out = os.path.join(FIGS, code + ".png")
    pm = pg.get_pixmap(dpi=int(dpi), clip=clip)
    pm.save(out)
    print("WROTE %s  (%dx%d px, page %s)" % (out, pm.width, pm.height, page))

def cmd_paper(html):
    """crop every figure a paper needs, from the bbox the book-check recorded in pool/ (skips crops
       that already exist, so a hand-tuned crop is never overwritten)"""
    meta = {}
    for f in glob.glob(os.path.join(MP, "pool", "*.json")):
        for r in json.load(open(f, encoding="utf-8")): meta[r["code"]] = r
    codes = re.findall(r'<span class="code">([^<]+)</span>', open(os.path.join(MP, html), encoding="utf-8").read())
    done = 0
    for c in dict.fromkeys(codes):
        fig = (meta.get(c) or {}).get("figure")
        if fig and not os.path.exists(os.path.join(FIGS, c + ".png")):
            cmd_crop(c, fig["page"], *fig["bbox"]); done += 1
    print("%d figures cropped for %s" % (done, html))

def cmd_list():
    f = sorted(glob.glob(os.path.join(FIGS, "*.png")))
    print("%d figures cropped:" % len(f))
    for p in f:
        print("  %-16s %6.1f KB" % (os.path.basename(p)[:-4], os.path.getsize(p) / 1024))

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
    elif a[0] == "pages":
        cmd_pages(a[1], *(a[2:]))
    elif a[0] == "crop":
        cmd_crop(*a[1:])
    elif a[0] == "paper":
        cmd_paper(a[1])
    elif a[0] == "list":
        cmd_list()
    else:
        print(__doc__)
