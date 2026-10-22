"""Usage: python match_exam.py RT4-20261012 CAT5-20260928 -> pyq/<page>/candidates.json (top-3 hits per row)"""
import json, os, re, sys
pages = sys.argv[1:]; sys.argv = [sys.argv[0]]
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "match.py"), encoding="utf-8").read().split("for chap in sys.argv[1:]:")[0])
EXD = os.path.join(YT, "ExamPapers_YouTube_Solutions")
for page in pages:
    parts = re.split(r"(<h2[^>]*>.*?</h2>)", open(os.path.join(EXD, page + "_YouTube_Solutions.html"), encoding="utf-8").read(), flags=re.S)
    od = os.path.join(HERE, page); os.makedirs(od, exist_ok=True); cands = []
    for i in range(1, len(parts), 2):
        sec = clean(parts[i]); subj = sec.split()[0]
        ch = corpus(subj); ct = [toks(c[3][:900]) for c in ch]
        for num, q in re.findall(r'<tr><td class="num">([^<]+)</td><td class="q">(.*?)</td>', parts[i + 1], re.S):
            q = clean(q); qt = toks(re.sub(r"\((?:a|A)\).*", "", q))
            if len(qt) < 4: continue
            best = sorted(((len(qt & c) / len(qt), len(qt & c) / max(len(c), 1), k) for k, c in enumerate(ct) if c), reverse=True)[:3]
            for rank, (a, b, k) in enumerate(best, 1):
                if not ((a >= 0.55 and b >= 0.15) or (a >= 0.5 and b >= 0.3)): continue
                kind, p, lab, txt = ch[k]
                cid = f"{page}__Q{num}~{rank}"; png = os.path.join(od, cid + ".png")
                cands.append(dict(id=cid, page=page, section=sec, num=num, q=q, score=[round(a, 2), round(b, 2)],
                                  paper=label(kind, p, txt), url=crop_and_link(kind, p, lab, png), eg=f"{os.path.basename(p)} {lab}", crop=png))
    json.dump(cands, open(os.path.join(od, "candidates.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(page, "candidates", len(cands), "rows", len({c["num"] for c in cands}))
