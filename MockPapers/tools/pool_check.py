"""Verify every question of a chapter against the printed book BEFORE it enters pool/.

    python tools/pool_check.py manifest P9 P10 P11 C6 M8D M9   -> pool_check/manifest/<LEC>.json
    python tools/pool_check.py status                         -> rows written vs manifest, per lecture
    python tools/pool_check.py missing P10L3                  -> codes still to check in one lecture
    python tools/pool_check.py merge [LEC...]                 -> pool/<LEC>.json from verified rows only
    python tools/pool_check.py sbmanifest P9 P10 ...          -> manifest/<CH>SB.json (Strong Box pages)

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


def sbmanifest(chapters):
    """Strong Box pages (<CH>SB_YouTube_Solutions.html) -> manifest/<CH>SB.json, codes <CH>SBV<7..11|PYQ>Q<n>.
       extract_pool's parse() does not read these pages: their rows sit under plain Level-n h2s."""
    g = load_extractor()
    for f in glob.glob(os.path.join(g["ROOT"], "YouTube_Solutions", "**", "*SB_YouTube_Solutions.html"),
                       recursive=True):
        ch = os.path.basename(f).replace("SB_YouTube_Solutions.html", "")
        if ch not in chapters: continue
        t = io.open(f, encoding="utf-8").read()
        out = []
        parts = re.split(r"<h2[^>]*>", t)[1:]
        for p in parts:
            h = g["strip"](p.split("</h2>")[0]).upper()
            lv = re.search(r"LEVEL[\s-]*(\d+)", h)
            sec = lv.group(1) if lv else "PYQ" if "PREVIOUS" in h else None
            if not sec: continue
            for num, q, rest in re.findall(r'<td class="num">([^<]*)</td><td class="q">(.*?)</td>(.*?)</tr>', p, re.S):
                a = re.search(r'<td class="ans">(.*?)</td>', rest, re.S)
                out.append({"code": "%sSBV%sQ%s" % (ch, sec, re.sub(r"\D", "", num)), "sec": sec,
                            "num": re.sub(r"\D", "", num), "key": g["strip"](a.group(1)) if a else "",
                            "stem": g["clean_q"](re.sub(r"\(\s*\d{4}\s+Level[\s-]*\d+\s*\)", "",
                                    g["strip"](re.sub(r'<div class="pyq">.*?</div>', "", q, flags=re.S))))})
        json.dump(out, io.open(os.path.join(CK, "manifest", ch + "SB.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("  %-8s %3d questions  %s" % (ch + "SB", len(out), dict(collections.Counter(r["sec"] for r in out))))


def pastmanifest():
    """the real ICAD papers (ExamPapers_YouTube_Solutions/<EXAM>-<date>*.html) -> manifest/<CH>X.json,
       codes <CH>XV<EXAM>Q<n> (chapter from the page's bookref, P0/C0/M0 when untagged), plus
       past_meta.json: code -> exam, question number, the student's result (c/w/u/x), bookref."""
    g = load_extractor()
    bylec, meta = collections.defaultdict(list), {}
    for f in sorted(glob.glob(os.path.join(g["ROOT"], "YouTube_Solutions", "ExamPapers_YouTube_Solutions", "*.html"))):
        exam = os.path.basename(f).split("-")[0]
        t = io.open(f, encoding="utf-8").read()
        for tr in re.findall(r'<tr([^>]*)>\s*<td class="num">(\d+).*?</td>\s*<td class="q">(.*?)</td>(.*?)</tr>', t, re.S):
            st, n, q, rest = tr
            st = (re.search(r'data-st="(\w*)"', st) or [None, ""])[1]
            pyq = re.search(r'<span class="paper">(.*?)</span>', q, re.S)
            q = re.sub(r'<div class="pyq">.*?</div>', "", q, flags=re.S)
            a = re.search(r'<td class="ans">(.*?)</td>', rest, re.S)
            ref = g["strip"]((re.search(r'<td class="bookref">(.*?)</td>', rest, re.S) or [None, ""])[1])
            ch = re.search(r"([PCM]\d+[A-D]?)\s*·", ref)
            ch = ch.group(1) if ch else "PCM"[(int(n) - 1) // 25] + "0"
            code = "%sXV%sQ%s" % (ch, exam, n)
            bylec[ch + "X"].append({"code": code, "sec": exam, "num": n,
                                    "key": g["strip"](a.group(1)) if a else "", "stem": g["strip"](q)})
            meta[code] = {"exam": exam, "q": int(n), "st": st, "bookref": ref,
                          "pyq": g["strip"](pyq.group(1)).replace("📝 PYQ:", "").strip() if pyq else ""}
    for lec, rows in sorted(bylec.items(), key=lambda x: nat(x[0])):
        json.dump(rows, io.open(os.path.join(CK, "manifest", lec + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    json.dump(meta, io.open(os.path.join(CK, "past_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("%d past questions in %d chapter manifests · %s" % (len(meta), len(bylec),
          dict(collections.Counter(m["exam"] for m in meta.values()))))


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


def merge(only=()):
    """pool/<LEC>.json from verified rows: stem_book replaces a wrong stem, correct_answer replaces a
       wrong key, unusable / out-of-scope questions are left out. Refuses while any row is missing.
       With lecture names, only those pool files are (re)written; the rest of pool/ seeds the dedup."""
    lecs = [l for l in lectures() if not only or l in only]
    gaps = [(l, len(man(l)) - sum(c["code"] in rows_of(l) for c in man(l))) for l in lecs]
    gaps = [g for g in gaps if g[1]]
    if gaps: raise SystemExit("not merging - unchecked questions remain: %s" % gaps)
    kept = dropped = 0
    seen = set()                 # across ALL lectures - the book repeats questions between lectures too
    for p in glob.glob(os.path.join(MP, "pool", "*.json")) if only else ():
        if os.path.basename(p)[:-5] in only: continue
        for q in json.load(io.open(p, encoding="utf-8")):
            seen |= {q["code"], re.sub(r"[^a-z0-9]", "", (q["stem"] or "").lower())[:120]}
    for lec in lecs:
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


def pastfix():
    """past-paper rows whose checker gave a different `chapter` than the code carries (P0/C0/M0 = the
       solution page had no book reference) move to <NEWCH>XV<EXAM>Q<n>: row file, manifest entry and
       past_meta key. Idempotent."""
    mp = os.path.join(CK, "past_meta.json")
    meta = json.load(io.open(mp, encoding="utf-8"))
    mans = {l: man(l) for l in lectures() if l.endswith("X")}
    moved = 0
    for lec in list(mans):
        for code, x in rows_of(lec).items():
            old, new = code.split("XV")[0], (x.get("chapter") or "").strip()
            if not re.fullmatch(r"[PCM]\d+[A-D]?", new) or new == old: continue
            nc = new + code[len(old):]
            x["code"] = nc
            os.makedirs(os.path.join(CK, "rows", new + "X"), exist_ok=True)
            json.dump(x, io.open(os.path.join(CK, "rows", new + "X", nc + ".json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            os.remove(os.path.join(CK, "rows", lec, code + ".json"))
            e = next(m for m in mans[lec] if m["code"] == code)
            mans[lec].remove(e); e["code"] = nc
            mans.setdefault(new + "X", []).append(e)
            meta[nc] = meta.pop(code)
            moved += 1
    for l, rows in mans.items():
        p = os.path.join(CK, "manifest", l + ".json")
        if rows: json.dump(sorted(rows, key=lambda r: nat(r["code"])), io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        elif os.path.exists(p): os.remove(p)
    json.dump(meta, io.open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("moved %d past questions to their checked chapter" % moved)


def patch(only=()):
    """older, unchecked pools: write the verdicts for the shortlisted codes in manifest_patch/<LEC>.json
       back INTO pool/<LEC>.json, leaving every other row alone (merge would drop them). Unusable or
       out-of-scope rows stay in the file, marked, so no selector picks them again."""
    d = os.path.join(CK, "manifest_patch")
    lecs = [os.path.basename(p)[:-5] for p in glob.glob(os.path.join(d, "*.json"))]
    lecs = sorted((l for l in lecs if not only or l in only), key=nat)
    want = {l: [c["code"] for c in json.load(io.open(os.path.join(d, l + ".json"), encoding="utf-8"))] for l in lecs}
    gaps = {l: [c for c in want[l] if c not in rows_of(l)] for l in lecs}
    gaps = {l: g for l, g in gaps.items() if g}
    if gaps: raise SystemExit("not patching - unchecked: %d codes in %s" % (sum(map(len, gaps.values())), sorted(gaps, key=nat)))
    v = collections.Counter()
    for l in lecs:
        p = os.path.join(MP, "pool", l + ".json")
        pool, r = json.load(io.open(p, encoding="utf-8")), rows_of(l)
        for q in pool:
            x = r.get(q["code"])
            if not x or q["code"] not in want[l]: continue
            bad = x.get("verdict") == "unusable" or x.get("in_scope") is False
            q.update({"stem": x.get("stem_book") or q["stem"], "answer": x.get("correct_answer") or q["answer"],
                      "format": x.get("type"), "has_opts": bool(x.get("options_printed")),
                      "verified": "unusable" if bad else x.get("verdict"), "integer": x.get("integer"),
                      "figure": x.get("figure"), "book_key": q.get("book_key") or q["answer"]})
            v[q["verified"]] += 1
        json.dump(pool, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("patched %d lectures: %s" % (len(lecs), dict(v)))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__)
    elif a[0] == "manifest": manifest(set(a[1:]))
    elif a[0] == "sbmanifest": sbmanifest(set(a[1:]))
    elif a[0] == "pastmanifest": pastmanifest()
    elif a[0] == "patch": patch(set(a[1:]))
    elif a[0] == "pastfix": pastfix()
    elif a[0] == "status": status()
    elif a[0] == "missing": missing(a[1])
    elif a[0] == "merge": merge(set(a[1:]))
