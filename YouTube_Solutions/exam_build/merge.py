"""Apply verifier fixes + judge verdicts to rows (keeps rows_pass1 backup). Prints a per-Q summary."""
import json, glob, os, shutil, sys
sys.stdout.reconfigure(encoding="utf-8")
S = sys.argv[1]  # exam work folder holding rows/ and recheck/
os.makedirs(S + "/rows_pass1", exist_ok=True)
ANS_FIELDS = {"ans_letter", "ans_text", "flag", "soln_html"}
summary = []
for f in sorted(glob.glob(S + "/rows/Q*.json")):
    base = os.path.basename(f)
    if not os.path.exists(S + "/rows_pass1/" + base):
        shutil.copy(f, S + "/rows_pass1/" + base)
    r = json.load(open(S + "/rows_pass1/" + base, encoding="utf-8"))   # always merge from the pristine pass-1 row
    n = r["num"]
    vf = S + "/recheck/Q%02d.json" % n
    jf = S + "/recheck/Q%02d_judge.json" % n
    v = json.load(open(vf, encoding="utf-8")) if os.path.exists(vf) else None
    j = json.load(open(jf, encoding="utf-8")) if os.path.exists(jf) else None
    applied = []
    fixes = (v or {}).get("fixes") or {}
    side = (j or {}).get("side")
    for k, val in fixes.items():
        if k not in r and k != "bookref_evidence":
            continue
        if k in ANS_FIELDS and j and side != "verifier":
            continue  # judge did not side with the verifier on the answer → keep solver's answer fields
        r[k] = val; applied.append(k)
    if j:
        if side == "neither" or (side == "verifier" and j.get("corrected_soln_html")):
            if j.get("corrected_soln_html"):
                r["soln_html"] = j["corrected_soln_html"]; applied.append("soln_html(judge)")
        if side == "neither" and j.get("final_answer"):
            fa = str(j["final_answer"]).strip()
            if r.get("ans_letter") is not None and len(fa) == 1:
                r["ans_letter"] = fa; applied.append("ans_letter(judge)")
            elif r.get("ans_letter") is None:
                r["ans_text"] = fa; applied.append("ans_text(judge)")
        if j.get("flag") is not None:
            r["flag"] = j["flag"]; applied.append("flag(judge)")
    json.dump(r, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    summary.append((n, (v or {}).get("ok"), side, applied, (v or {}).get("defects", [])[:3]))
for n, ok, side, applied, defects in summary:
    print(n, "ok" if ok else "NOT-OK", side or "", applied, defects if not ok else "")
print("rows", len(summary), "not-ok", sum(1 for s in summary if not s[1]), "judged", sum(1 for s in summary if s[2]))
