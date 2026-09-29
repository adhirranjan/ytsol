"""Find and crop a question's figure out of the scanned lecture PDFs.

The book PDFs are image-only (no text layer), so a question is located by RENDERING pages
and looking at them, not by searching text.

    python figtool.py pages P6L5              # render every page of that lecture -> PNGs, prints paths
    python figtool.py crop P6L5V3Q2 7 0.12 0.34 0.88 0.61
                                              # crop page 7 using FRACTIONS of page width/height
                                              # (x0 y0 x1 y1, 0-1 from top-left) -> figures/<CODE>.png
    python figtool.py list                     # what has been cropped so far

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
    return re.match(r"([A-Z]+\d+[A-C]?)L", lec).group(1)

def find_pdf(lec):
    """lecture files are named either '<CH>L<n>.pdf' or plain 'L<n>.pdf' depending on the chapter"""
    ch = chapter_of(lec)
    base = [p for p in glob.glob(os.path.join(ROOT, "*", ch)) if os.path.isdir(p)]
    if not base:
        raise SystemExit("no source folder for chapter " + ch)
    base = base[0]
    tail = lec[len(ch):]                      # "L5"
    for cand in ("%s.pdf" % lec, "%s.pdf" % tail):
        p = os.path.join(base, cand)
        if os.path.exists(p):
            return p
    # some lectures share one scan, named e.g. "L2&L3.pdf" or "P3L3L4.pdf" - match on the L-numbers
    want = re.findall(r"L(\d+)", tail)
    for p in sorted(glob.glob(os.path.join(base, "*.pdf"))):
        got = re.findall(r"L(\d+)", os.path.basename(p))
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
            d[i].get_pixmap(dpi=dpi).save(p)
        out.append(p)
    print("%s -> %d pages (%s)" % (pdf, d.page_count, PAGES))
    for i, p in enumerate(out, 1):
        print("  p%02d  %s" % (i, p))

def cmd_crop(code, page, x0, y0, x1, y1, dpi=220):
    """crop by page fractions; re-renders that page at high dpi so the figure stays sharp"""
    lec = re.match(r"([A-Z]+\d+[A-C]?L\d+(?:L\d+)?)V", code).group(1)
    d = fitz.open(find_pdf(lec))
    pg = d[int(page) - 1]
    r = pg.rect
    clip = fitz.Rect(r.x0 + float(x0) * r.width, r.y0 + float(y0) * r.height,
                     r.x0 + float(x1) * r.width, r.y0 + float(y1) * r.height)
    out = os.path.join(FIGS, code + ".png")
    pm = pg.get_pixmap(dpi=int(dpi), clip=clip)
    pm.save(out)
    print("WROTE %s  (%dx%d px, page %s)" % (out, pm.width, pm.height, page))

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
    elif a[0] == "list":
        cmd_list()
    else:
        print(__doc__)
