"""Merge the per-chapter agent outputs (CAT5 default; pass CAT6) into the <SUBJ>_final.json shape build_sets.py expects."""
import json, os, sys, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
EXAM = (sys.argv[1] if len(sys.argv) > 1 else "CAT5").lower()     # python merge_cat5.py CAT6
R = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rankings", EXAM)
SRC, NEED = {
 "cat5": ({"PHY": {"P7": ["final_P7.json"], "P8": ["final_P8.json"]},
           "CHEM": {"C5": ["final_C5a.json", "final_C5b.json"]},
           "MATH": {"M8A": ["final_M8A.json"], "M8B": ["final_M8B.json"]}},
          {"P7": 54, "P8": 96, "C5": 150, "M8A": 72, "M8B": 78}),
 "cat6": ({"PHY": {"P9": ["final_P9.json"], "P10": ["final_P10.json"], "P11": ["final_P11.json"]},
           "CHEM": {"C6": ["final_C6a.json", "final_C6b.json"]},
           "MATH": {"M8D": ["final_M8D.json"], "M9": ["final_M9.json"]}},
          {"P9": 48, "P10": 54, "P11": 48, "C6": 150, "M8D": 60, "M9": 90}),
}[EXAM]
ok = True
for subj, chs in SRC.items():
    out = {"subject": subj, "chapters": {}}
    for ch, files in chs.items():
        picks, seen = [], set()
        for f in files:
            p = os.path.join(R, f)
            if not os.path.exists(p): print("MISSING", f); ok = False; continue
            for q in json.load(open(p, encoding="utf-8"))["picks"]:
                if q["code"] in seen: print("  dup dropped:", q["code"]); continue
                seen.add(q["code"]); picks.append(q)
        picks.sort(key=lambda q: (q.get("tier", 2),))          # tier-1 first, stable
        nb = sum(1 for q in picks if q.get("partB"))
        flag = "" if len(picks) == NEED[ch] else "  <-- EXPECTED %d" % NEED[ch]
        print("%-5s %-4s %3d picks, %2d partB%s" % (subj, ch, len(picks), nb, flag))
        if len(picks) != NEED[ch]: ok = False
        out["chapters"][ch] = {"need": NEED[ch], "picks": picks}
    json.dump(out, open(os.path.join(R, subj + "_final.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
print("\nmerge", "OK" if ok else "INCOMPLETE - do not build yet")
sys.exit(0 if ok else 1)
