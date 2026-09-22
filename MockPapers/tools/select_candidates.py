"""Candidate selector (RT-3 default; pass an exam key, e.g. `python select_candidates.py CAT5`). Deterministic ranked shortlist per subject from MockPapers/pool.
RT weighting (newest chapter anchored, tools light/embedded). Book structure = clustering:
spread across (lecture x level) cells -> method diversity + difficulty spread for free.
Output: MockPapers/rankings/<SUBJECT>_candidates.json  (picks + buffer for agent review)."""
import json, os, glob, re, collections, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POOL = os.path.join(ROOT, "MockPapers", "pool")
OUT  = None   # set once the exam config is known

# per-chapter quota = total questions from that chapter across ALL sets (each subject sums to 25*nsets)
EXAMS = {
 # RT-3, 10 sets, cumulative Phase-1 -> 250/subject
 "RT3": {"nsets":10, "out":"rankings", "quota":{
   "PHY": {"P6":70,"P5":35,"P4":60,"P3":40,"P2":25,"P1":20},
   "CHEM":{"C4":70,"C3":65,"C2":60,"C1":55},
   "MATH":{"M7":45,"M6":45,"M5":55,"M4":30,"M3":25,"M2":25,"M1":25}}},
 # CAT-5 (28-09-2026), 6 sets -> 150/subject. Pair test: weight by lectures + pool size.
 # P7 4 lec/206Q vs P8 8 lec/403Q -> 1:2 (matches CAT-4's P5/P6 8:17). C5 is the only Chem chapter.
 # M8A and M8B are structural twins (3 lec, ~200Q, same level spread) -> near-even, mild GP lean.
 "CAT5": {"nsets":6, "out":"rankings/cat5", "quota":{
   "PHY": {"P7":54,"P8":96},
   "CHEM":{"C5":150},
   "MATH":{"M8A":72,"M8B":78}}},
}
EXAM = sys.argv[1].upper() if len(sys.argv) > 1 else "RT3"
CFG  = EXAMS[EXAM]; QUOTA = CFG["quota"]
SUBJ_CH = {s: list(q) for s, q in QUOTA.items()}
# Shortlist band mix. Strict level-preference ordering starved the hard bands: a lecture
# contributes ~18 candidates and L3+L4 alone filled that, so 464 of CAT-5's 554 Level-5/6
# questions never reached the ranking agents (P8 got literally zero). Give every band an
# explicit share of each lecture's slots instead, so the agent can choose the hard end.
LEVELPREF = {"3":0,"4":1,"2":2,"5":3,"Board":4,"1":5,"6":6,"Sugg":7,"Recap":8}
BANDMIX   = {"4":.30,"3":.22,"5":.22,"6":.10,"2":.06,"Sugg":.06,"Board":.04}

def chap_of_lec(lec):
    m = re.match(r"([A-Z]+\d+[A-C]?)", lec); base = m.group(1)
    if base.startswith("M5"): return "M5"      # M5A/B/C are one chapter; M8A/M8B are not
    return base

def numeric(ans):  # Part-B candidate = answer not an (a-d) option letter
    return not re.match(r"^[a-dA-D][\s\).:]", ans.strip())

def load_chapter(chap):
    rows=[]
    for f in glob.glob(POOL+"/*.json"):
        lec=os.path.basename(f)[:-5]
        if chap_of_lec(lec)!=chap: continue
        for r in json.load(open(f,encoding="utf-8")):
            r["chap"]=chap; rows.append(r)
    return rows

def rank_chapter(chap, need):
    rows=load_chapter(chap)
    # dedup cross-lecture by normalized stem
    seen={}; uniq=[]
    for r in rows:
        k=re.sub(r"[^a-z0-9]","",r["stem"].lower())[:110]
        if k in seen: continue
        seen[k]=1; uniq.append(r)
    # bucket by lecture, then by band inside the lecture
    bylec=collections.defaultdict(lambda: collections.defaultdict(list))
    for r in uniq: bylec[r["lec"]][r["sec"]].append(r)
    order=sorted(bylec)
    target=int(need*1.5)+2
    per_lec=-(-target//max(1,len(order)))          # ceil: slots this lecture may contribute

    ranked={}
    for lec,bands in bylec.items():
        for b in bands: bands[b].sort(key=lambda r: r["stem"][:30])
        take=[]
        for b,share in sorted(BANDMIX.items(), key=lambda kv:-kv[1]):
            n=int(round(share*per_lec))
            take += bands.get(b,[])[:n]
        got={id(r) for r in take}                  # top up from preference order if a band was thin
        for b in sorted(bands, key=lambda b: LEVELPREF.get(b,9)):
            for r in bands[b]:
                if len(take)>=per_lec: break
                if id(r) not in got: take.append(r); got.add(id(r))
        take.sort(key=lambda r:(LEVELPREF.get(r["sec"],9), r["stem"][:30]))
        ranked[lec]=take

    # round-robin across lectures (breadth first = ladder)
    picks=[]; idx={l:0 for l in order}; guard=0
    while len(picks)<target and guard<10000:
        guard+=1; progressed=False
        for lec in order:
            i=idx[lec]
            if i<len(ranked[lec]):
                picks.append(ranked[lec][i]); idx[lec]+=1; progressed=True
                if len(picks)>=target: break
        if not progressed: break
    for rank,r in enumerate(picks,1):
        r["chap_rank"]=rank; r["numeric"]=numeric(r["answer"])
    return picks

OUT = os.path.join(ROOT, "MockPapers", *CFG["out"].split("/")); os.makedirs(OUT, exist_ok=True)
print(f"exam {EXAM}: {CFG['nsets']} sets -> {OUT}")
for subj,chs in SUBJ_CH.items():
    out={"subject":subj,"quota":QUOTA[subj],"candidates":{}}
    for ch in chs:
        need=QUOTA[subj][ch]
        picks=rank_chapter(ch,need)
        out["candidates"][ch]={"need":need,"list":[
            {"code":r["code"],"lec":r["lec"],"sec":r["sec"],"style":r["format"],
             "numeric":r["numeric"],"chap_rank":r["chap_rank"],
             "answer":r["answer"][:40],"stem":r["stem"]} for r in picks]}
    json.dump(out, open(OUT+f"/{subj}_candidates.json","w",encoding="utf-8"),
              ensure_ascii=False, indent=1)
    tot=sum(len(v["list"]) for v in out["candidates"].values())
    need=sum(v["need"] for v in out["candidates"].values())
    print(f"{subj}: need {need}, candidates {tot}, chapters "+
          ", ".join(f'{c}:{len(out["candidates"][c]["list"])}/{out["candidates"][c]["need"]}' for c in chs))
