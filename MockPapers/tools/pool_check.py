"""Verify every question of a chapter against the printed book BEFORE it enters pool/.

    python tools/pool_check.py manifest P9 P10 P11 C6 M8D M9   -> pool_check/manifest/<LEC>.json
    python tools/pool_check.py status                         -> rows written vs manifest, per lecture
    python tools/pool_check.py missing P10L3                  -> codes still to check in one lecture
    python tools/pool_check.py merge                          -> pool/<LEC>.json from verified rows only

The manifest carries the FULL stem (extract_pool caps it at 400 chars, and agents comparing the book
against a truncated stem report false truncations). Checking agents write ONE file per question,
pool_check/rows/<LEC>/<CODE>.json, so a stalled agent loses one question and a retry is gap-targeted.

Row schema (written by the checking agent):
  code, page            book page (1-based PDF page) where the question is printed
  stem_ok               manifest stem matches the book in every number, condition and option
  stem_book             faithful transcription when stem_ok is false, else null
  figure                null, or {"page": n, "bbox": [x0, y0, x1, y1]} as page fractions
  type                  single | multi | numerical | match | assertion | subjective
  options_printed       the book prints choices for it
  key                   what the book's key says
  derived               the agent's own answer
  verdict               ok | key_wrong | unusable
  correct_answer        the answer to print in our key (= key when ok)
  integer               the correct answer is a single integer (Part-B eligible)
  in_scope              false only for content outside the syllabus (M9: rotation / geometry)
  reason, work          one line each
"""
import collections, glob, io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CK = os.path.join(MP, "pool_check")
nat = lambda s: [int(t) if t.isdigit() else t for t in re.findall(r"\d+|\D+", s)]


def load_extractor():
    src = io.open(os.path.join(MP, "tools", "extract_pool.py"), encoding="utf-8").read()
    src = src.split("files = glob.glob")[0].replace('"stem":qtxt[:400]', '"stem":qtxt')
    g = {"__file__": os.path.join(MP, "tools", "extract_pool.py")}
    exec(compile(src, "extract_pool", "exec"), g)
    return g


def manifest(chapters):
    g = load_extractor()
    os.makedirs(os.path.join(CK, "manifest"), exist_ok=True)
    bylec = collections.defaultdict(list)
    for f in glob.glob(os.path.join(g["ROOT"], "YouTube_Solutions", "**", "*_YouTube_Solutions.html"),
                       recursive=True):
        base = os.path.basename(f).replace("_YouTube_Solutions.html", "")
        if g["chapter_of"](base) in chapters:
            for r in g["parse"](f, base):
                bylec[r["lec"]].append(r)
    for lec, rows in sorted(bylec.items(), key=lambda x: nat(x[0])):
        seen, out = set(), []
        for r in rows:                       # same within-lecture dedup as extract_pool
            k = re.sub(r"[^a-z0-9]", "", r["stem"].lower())[:120]
            if k in seen: continue
            seen.add(k)
            out.append({"code": r["code"], "sec": r["sec"], "num": r["num"],
                        "key": r["answer"], "stem": r["stem"]})
        json.dump(out, io.open(os.path.join(CK, "manifest", lec + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("  %-8s %3d questions" % (lec, len(out)))


def rows_of(lec):
    d = os.path.join(CK, "rows", lec)
    out = {}
    for p in glob.glob(os.path.join(d, "*.json")):
        try: out[os.path.basename(p)[:-5]] = json.load(io.open(p, encoding="utf-8"))
        except ValueError: pass             # half-written file: counts as missing, gets redone
    return out


def lectures():
    return sorted((os.path.basename(p)[:-5] for p in glob.glob(os.path.join(CK, "manifest", "*.json"))), key=nat)


def man(lec):
    return json.load(io.open(os.path.join(CK, "manifest", lec + ".json"), encoding="utf-8"))


def status():
    tot = done = 0
    v = collections.Counter()
    for lec in lectures():
        m, r = man(lec), rows_of(lec)
        have = [c["code"] for c in m if c["code"] in r]
        tot += len(m); done += len(have)
        for c in have: v[r[c].get("verdict")] += 1
        print("  %-8s %3d / %3d %s" % (lec, len(have), len(m), "" if len(have) == len(m) else "<- missing %d" % (len(m) - len(have))))
    print("checked %d / %d · verdicts %s" % (done, tot, dict(v)))


def missing(lec):
    r = rows_of(lec)
    print(" ".join(c["code"] for c in man(lec) if c["code"] not in r))


def merge():
    """pool/<LEC>.json from verified rows: stem_book replaces a wrong stem, correct_answer replaces a
       wrong key, unusable / out-of-scope questions are left out. Refuses while any row is missing."""
    gaps = [(l, len(man(l)) - sum(c["code"] in rows_of(l) for c in man(l))) for l in lectures()]
    gaps = [g for g in gaps if g[1]]
    if gaps: raise SystemExit("not merging - unchecked questions remain: %s" % gaps)
    kept = dropped = 0
    seen = set()                 # across ALL lectures - the book repeats questions between lectures too
    for lec in lectures():
        r, out = rows_of(lec), []
        for c in man(lec):
            x = r[c["code"]]
            if x.get("verdict") == "unusable" or x.get("in_scope") is False:
                dropped += 1; continue
            stem = x.get("stem_book") or c["stem"]
            out.append({"code": c["code"], "lec": lec, "sec": c["sec"], "num": c["num"],
                        "answer": x.get("correct_answer") or c["key"],
                        "format": x.get("type"), "has_opts": bool(x.get("options_printed")),
                        "stem": stem, "verified": x.get("verdict"), "integer": x.get("integer"),
                        "figure": x.get("figure"), "book_key": c["key"]})
        known = {c["code"] for c in man(lec)}
        for code, x in sorted(r.items(), key=lambda kv: nat(kv[0])):   # book questions the manifest missed
            if code in known or not x.get("added"): continue
            if x.get("verdict") == "unusable" or x.get("in_scope") is False:
                dropped += 1; continue
            out.append({"code": code, "lec": lec, "sec": str(x.get("sec")), "num": str(x.get("num")),
                        "answer": x.get("correct_answer") or x.get("key"), "format": x.get("type"),
                        "has_opts": bool(x.get("options_printed")), "stem": x.get("stem_book"),
                        "verified": x.get("verdict"), "integer": x.get("integer"),
                        "figure": x.get("figure"), "book_key": x.get("key"), "added": True})
        # one copy per code and per question text (the book repeats some questions verbatim across
        # levels and lectures; a repeat would otherwise reach two different sets)
        uniq = []
        for q in out:
            k = re.sub(r"[^a-z0-9]", "", (q["stem"] or "").lower())[:120]
            if q["code"] in seen or k in seen: dropped += 1; continue
            seen |= {q["code"], k}; uniq.append(q)
        out = uniq
        json.dump(out, io.open(os.path.join(MP, "pool", lec + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        kept += len(out)
    print("pool: %d verified questions written, %d dropped (unusable / out of scope)" % (kept, dropped))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__)
    elif a[0] == "manifest": manifest(set(a[1:]))
    elif a[0] == "status": status()
    elif a[0] == "missing": missing(a[1])
    elif a[0] == "merge": merge()
