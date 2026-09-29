"""Assemble rankings/rt4/<SUBJ>_final.json for RT-4.
18 chapters come from this exam's own agent passes; 5 are subset from the CAT-5 library
(built after the band-mix fix, so they are not starved) down to RT-4's smaller quotas."""
import json, os, re, sys, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MP  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RT4 = os.path.join(MP, "rankings", "rt4")
CAT5= os.path.join(MP, "rankings", "cat5")

# chapter -> (total picks, partB picks)
NEED = {"P1":(8,2),"P2":(16,3),"P3":(30,6),"P4":(60,12),"P5":(15,3),"P6":(36,7),
        "P7":(30,6),"P8":(55,11),
        "C1":(50,10),"C2":(50,10),"C3":(55,11),"C4":(30,6),"C5":(65,13),
        "M1":(12,2),"M2":(19,4),"M3":(19,4),"M4":(25,5),"M5":(48,10),"M6":(31,6),
        "M7":(24,5),"M8A":(30,6),"M8B":(30,6),"M8C":(12,2)}
SUBJ = {"PHY":["P1","P2","P3","P4","P5","P6","P7","P8"],
        "CHEM":["C1","C2","C3","C4","C5"],
        "MATH":["M1","M2","M3","M4","M5","M6","M7","M8A","M8B","M8C"]}
REUSE = {"P7":"PHY","P8":"PHY","C5":"CHEM","M8A":"MATH","M8B":"MATH"}

def own(ch):
    p = os.path.join(RT4, "final_%s.json" % ch)
    return json.load(open(p, encoding="utf-8"))["picks"] if os.path.exists(p) else None

def from_cat5(ch):
    fin = json.load(open(os.path.join(CAT5, REUSE[ch]+"_final.json"), encoding="utf-8"))
    return fin["chapters"][ch]["picks"]

POOL = os.path.join(MP, "pool")
META = {}
for _f in os.listdir(POOL):
    for _r in json.load(open(os.path.join(POOL, _f), encoding="utf-8")): META[_r["code"]] = _r
def is_hard(p): return META.get(p["code"], {}).get("sec") in ("5", "6")

def subset(picks, n, nb):
    """Take n picks keeping exactly nb partB AND the chapter's original hard-question fraction.

    Taking the top n by tier alone looks right but silently guts the difficulty: tier 1 is the
    core mid-level archetypes and tier 3 is where the Level-5/6 depth lives, so draining tier 1
    first cut M8A from 24 hard questions to 0. Fill the hard quota inside each partB group first,
    then top up with the rest, tier order preserved within every bucket."""
    key = lambda p: (p.get("tier", 2),)
    H = round(sum(1 for p in picks if is_hard(p)) / len(picks) * n)   # keep the source fraction
    out = []
    for group, want in ((            [p for p in picks if p.get("partB")], nb),
            ([p for p in picks if not p.get("partB")], n - nb)):
        want_h = min(round(H * want / n), sum(1 for p in group if is_hard(p)), want)
        hard = sorted([p for p in group if is_hard(p)], key=key)[:want_h]
        rest = sorted([p for p in group if p not in hard], key=key)[:want - len(hard)]
        if len(hard) + len(rest) < want: return None
        out += hard + rest
    return sorted(out, key=key)

ok = True
for subj, chs in SUBJ.items():
    out = {"subject": subj, "chapters": {}}
    for ch in chs:
        n, nb = NEED[ch]
        picks = own(ch)
        src = "rt4"
        if picks is None and ch in REUSE:
            picks, src = subset(from_cat5(ch), n, nb), "cat5-subset"
        if picks is None:
            print("  MISSING  %-4s (no final_%s.json, and no reuse source)" % (ch, ch)); ok = False; continue
        seen = set(); ded = []
        for p in picks:
            if p["code"] in seen: continue
            seen.add(p["code"]); ded.append(p)
        got_b = sum(1 for p in ded if p.get("partB"))
        bad = (len(ded) != n) or (got_b != nb)
        if bad: ok = False
        print("  %-5s %-4s %-12s %3d picks (want %3d) · partB %2d (want %2d)%s"
              % (subj, ch, src, len(ded), n, got_b, nb, "   <-- MISMATCH" if bad else ""))
        out["chapters"][ch] = {"need": n, "picks": sorted(ded, key=lambda p: (p.get("tier", 2),))}
    json.dump(out, open(os.path.join(RT4, subj+"_final.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    tot = sum(len(v["picks"]) for v in out["chapters"].values())
    tb  = sum(1 for v in out["chapters"].values() for p in v["picks"] if p.get("partB"))
    print("  %-5s TOTAL %d picks, %d partB  (want 250 / 50)\n" % (subj, tot, tb))
print("merge", "OK" if ok else "INCOMPLETE - do not build yet")
sys.exit(0 if ok else 1)
