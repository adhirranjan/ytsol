"""Collect 'same' verdicts -> YouTube_Solutions/pyq_tags/<Ch>.json; print per-chapter summary."""
import collections, glob, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = r"E:\Adhir\AdWinUser\Desktop\icad-dps\ICAD\BooksScanned\YouTube_Solutions\pyq_tags"
for ch in sys.argv[1:]:
    cands = json.load(open(os.path.join(HERE, ch, "candidates.json"), encoding="utf-8"))
    p2 = os.path.join(HERE, ch, "candidates2.json")
    if os.path.exists(p2): cands += json.load(open(p2, encoding="utf-8"))
    seen = set()
    cnt, rows, missing, nourl = collections.Counter(), [], [], []
    for c in cands:
        f = os.path.join(HERE, "verdicts", c["id"] + ".json")
        if not os.path.exists(f): missing.append(c["id"]); continue
        v = json.load(open(f, encoding="utf-8"))["verdict"]; cnt[v] += 1
        if v != "same": continue
        if not c["url"]: nourl.append(c["id"]); continue
        key = (c["page"], c["section"], c["num"])
        if key in seen: continue
        seen.add(key)
        m = re.match(r"JEE Advanced (\d{4})( · Paper \d)", c["paper"])
        paper = f"IIT-JEE {m[1]}{m[2]}" if m and int(m[1]) < 2013 else c["paper"]
        rows.append(dict(page=c["page"], section=re.sub(r"\s*\d+\s*Q$", "", c["section"]), num=c["num"], paper=paper, url=c["url"]))
    json.dump(rows, open(os.path.join(OUT, ch + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{ch}: {len(cands)} candidates {dict(cnt)} -> {len(rows)} tags; missing verdicts {len(missing)}; same-without-link {nourl}")
