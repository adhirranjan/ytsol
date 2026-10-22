"""Usage: python match.py P10 P11 C6 M8D M9  -> pyq/<Ch>/candidates.json + crops"""
import fitz, glob, html, json, os, pickle, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
EG = r"E:\Adhir\AdWinUser\Desktop\icad-dps\ICAD\ThirdPartySolutions-ExamGoal"
YT = r"E:\Adhir\AdWinUser\Desktop\icad-dps\ICAD\BooksScanned\YouTube_Solutions"
HERE = os.path.dirname(os.path.abspath(__file__))
SUBJ = {"P": "Physics", "C": "Chemistry", "M": "Mathematics"}
MON = dict(January="Jan", February="Feb", March="Mar", April="Apr", May="May", June="Jun", July="Jul", August="Aug", September="Sep", October="Oct", November="Nov", December="Dec")

def corpus(subj):
    cache = os.path.join(HERE, f"corpus_{subj}.pkl")
    if os.path.exists(cache): return pickle.load(open(cache, "rb"))
    ch = []
    for p in glob.glob(os.path.join(EG, "jee_main_chapterwise_pdfs", subj, "*.pdf")):
        parts = re.split(r"\n(Q\d+\.)\n", "".join(pg.get_text() for pg in fitz.open(p)))
        ch += [("main", p, parts[i], parts[i + 1]) for i in range(1, len(parts) - 1, 2)]
    for p in glob.glob(os.path.join(EG, "jee_advanced_pdfs", "*.pdf")):
        parts = re.split(r"\n(Q\d+\.)\n", "".join(pg.get_text() for pg in fitz.open(p)))
        ch += [("adv", p, parts[i], parts[i + 1]) for i in range(1, len(parts) - 1, 2)]
    pickle.dump(ch, open(cache, "wb"))
    return ch

STOP = set("the a an of is to and in with on at by from be it its as which that this after before will are find value if then".split())
toks = lambda s: {w for w in re.findall(r"[a-z]+|\d+(?:\.\d+)?", s.lower()) if w not in STOP and len(w) > 1}
clean = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()

def rows_of(chap):
    out = []
    for f in sorted(glob.glob(os.path.join(YT, "*", f"{chap}_YouTube_Solutions", "*.html"))):
        page = os.path.basename(f).split("_")[0]
        parts = re.split(r"(<h2[^>]*>.*?</h2>)", open(f, encoding="utf-8").read(), flags=re.S)
        for i in range(1, len(parts), 2):
            sec = clean(parts[i])
            for num, q in re.findall(r'<tr><td class="num">([^<]+)</td><td class="q">(.*?)</td>', parts[i + 1], re.S):
                out.append(dict(page=page, section=sec, num=num, q=clean(q)))
    return out

def label(kind, p, txt):
    if kind == "adv":
        y = os.path.basename(p)[:-4].split("_", 1)[1]
        m = re.search(r"(\d{4}) Paper (\d)", y)
        return f"JEE Advanced {m[1]} · Paper {m[2]}" if m else y.replace("IIT-JEE", "IIT-JEE")
    first = txt.strip().split("\n")[0]
    m = re.match(r"JEE Main (\d{4}) \((?:Online|Offline)\) (\d+)\w\w (\w+) (Morning|Evening)", first)
    if m: return f"JEE Main {m[1]} · {m[2]} {MON.get(m[3], m[3])} · {m[4]}"
    return re.sub(r" \((?:Online|Offline)\)", "", first)

def crop_and_link(kind, p, lab, out_png):
    for pg in fitz.open(p):
        hs = [h for h in pg.search_for(lab) if h.x0 < 80]
        if not hs: continue
        y0 = hs[0].y0 - 4
        labs = [b for b in pg.get_text("blocks") if re.match(r"Q\d+\.", b[4].strip()) and b[1] > y0 + 20]
        y1 = min([b[1] for b in labs] + [pg.rect.y1 - 60]) - 2
        pg.get_pixmap(dpi=80, clip=fitz.Rect(30, y0, pg.rect.x1 - 90, y1)).save(out_png)
        ls = sorted([l for l in pg.get_links() if l.get("uri") and l["from"].y1 > hs[0].y0 and l["from"].y0 < hs[0].y0 + 130], key=lambda l: l["from"].y0)
        return ls[0]["uri"].split("?")[0] if ls else ""
    return ""

for chap in sys.argv[1:]:
    ch = corpus(SUBJ[chap[0]])
    ct = [toks(c[3][:900]) for c in ch]
    rows = rows_of(chap)
    od = os.path.join(HERE, chap); os.makedirs(od, exist_ok=True)
    cands = []
    for r in rows:
        stem = re.sub(r"\(a\).*", "", re.split(r" — | &mdash; ", r["q"])[0])
        qt = toks(stem)
        if len(qt) < 4: continue
        named = re.search(r"JEE|AIEEE|IIT", r["q"])
        ranked = sorted(((len(qt & c) / len(qt), len(qt & c) / max(len(c), 1), i) for i, c in enumerate(ct) if c), reverse=True)[:3]
        for rank, (a, b, i) in enumerate(ranked, 1):
            ok = (named or (a >= 0.55 and b >= 0.15) or (a >= 0.5 and b >= 0.3)) if rank == 1 else ((a >= 0.55 and b >= 0.2) or (named and a >= 0.5))
            if not ok: continue
            kind, p, lab, txt = ch[i]
            cid = f"{r['page']}__{len(cands):04d}~{rank}"
            png = os.path.join(od, cid + ".png")
            url = crop_and_link(kind, p, lab, png)
            cands.append(dict(id=cid, **r, score=[round(a, 2), round(b, 2)], paper=label(kind, p, txt), url=url,
                              eg=f"{os.path.basename(p)} {lab}", crop=png))
    json.dump(cands, open(os.path.join(od, "candidates.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{chap}: {len(rows)} rows, {len(cands)} candidates")
