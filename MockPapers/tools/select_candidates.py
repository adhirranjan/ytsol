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
 # RT-4 (12-10-2026), 10 sets -> 250/subject. Cumulative: newest chapters anchor,
 # BMT tool chapters (P1/P2) suppressed - they appear embedded in other chapters' problems.
 "RT4": {"nsets":10, "out":"rankings/rt4", "quota":{
   "PHY": {"P1":8,"P2":16,"P3":30,"P4":60,"P5":15,"P6":36,"P7":30,"P8":55},
   "CHEM":{"C1":50,"C2":50,"C3":55,"C4":30,"C5":65},
   "MATH":{"M1":12,"M2":19,"M3":19,"M4":25,"M5":48,"M6":31,"M7":24,
           "M8A":30,"M8B":30,"M8C":12}}},
 "CAT5": {"nsets":6, "out":"rankings/cat5", "quota":{
   "PHY": {"P7":54,"P8":96},
   "CHEM":{"C5":150},
   "MATH":{"M8A":72,"M8B":78}}},
}
EXAM = sys.argv[1].upper() if len(sys.argv) > 1 else "RT3"
ONLY = sys.argv[2].upper() if len(sys.argv) > 2 else None   # regenerate just this subject
CFG  = EXAMS[EXAM]; QUOTA = CFG["quota"]
SUBJ_CH = {s: list(q) for s, q in QUOTA.items()}
# Shortlist band mix. Strict level-preference ordering starved the hard bands: a lecture
# contributes ~18 candidates and L3+L4 alone filled that, so 464 of CAT-5's 554 Level-5/6
# questions never reached the ranking agents (P8 got literally zero). Give every band an
# explicit share of each lecture's slots instead, so the agent can choose the hard end.
LEVELPREF = {"3":0,"4":1,"2":2,"5":3,"Board":4,"1":5,"6":6,"Sugg":7,"Recap":8}
BANDMIX   = {"4":.30,"3":.22,"5":.22,"6":.10,"2":.06,"Sugg":.06,"Board":.04}
# default shortlist is 1.5x the quota. Figure-heavy chapters lose so many candidates to
# undescribed-figure / truncated-composite rejects that the agent ends up with no real choice
# (P6 had 16 of 56 unusable, leaving 1.11x). Widen those so clustering is a genuine selection.
WIDEN     = {"P5":2.5,"P6":2.5,"C1":2.0,"C2":2.0,"C3":2.0,"C4":2.0,"M5":2.0}
# Chapters whose first pass came out >50% Level-5/6. The default BANDMIX hands the agent a ~43%-hard
# shortlist, so "take at least 22% hard" turned into "took nearly all of them" and the mid-level band
# - which is where this student actually loses marks - had almost nothing left to choose between.
# These get a mid-weighted mix AND a wider list, so the L3/L4 selection is a real one.
MIDMIX    = {"4":.32,"3":.26,"5":.18,"6":.10,"2":.06,"Sugg":.05,"Board":.03}
MIDCHAP   = {"C1","C2","C3","C4","M5"}

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

UNUSABLE_ANS = re.compile(r"^[\s—–\-?]*$")   # "", "-", em/en dash: the book prints no key

def rank_chapter(chap, need):   # chap drives WIDEN
    rows=load_chapter(chap)
    # a question with no printed answer cannot go in a mock paper - drop before the agent sees it.
    # 412 of the 7113 pooled questions are like this (mostly Board); three slipped into RT-4's first build.
    rows=[r for r in rows if not UNUSABLE_ANS.match(r.get("answer") or "")]
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
    target=int(need*WIDEN.get(chap,1.5))+2
    per_lec=-(-target//max(1,len(order)))          # ceil: slots this lecture may contribute

    def alloc_bands(avail, slots, chap=None):
        MIX = MIDMIX if chap in MIDCHAP else BANDMIX
        """largest-remainder split of `slots` across BANDMIX; small shares must not vanish"""
        want={b:MIX[b]*slots for b in MIX}
        base={b:int(w) for b,w in want.items()}
        short=slots-sum(base.values())
        for b in sorted(want,key=lambda b:-(want[b]-base[b]))[:max(0,short)]: base[b]+=1
        return {b:min(n,len(avail.get(b,[]))) for b,n in base.items()}

    ranked={}
    for lec,bands in bylec.items():
        for b in bands: bands[b].sort(key=lambda r: r["stem"][:30])
        quota=alloc_bands(bands, per_lec, chap)
        take=[]
        for b,n in quota.items():
            for pos,r in enumerate(bands.get(b,[])[:n]): take.append((pos,LEVELPREF.get(b,9),r))
        got={id(t[2]) for t in take}
        for b in sorted(bands, key=lambda b: LEVELPREF.get(b,9)):   # top up a thin band
            for pos,r in enumerate(bands[b]):
                if len(take)>=per_lec: break
                if id(r) not in got: take.append((99,LEVELPREF.get(b,9),r)); got.add(id(r))
        # interleave by position-within-band, NOT by level preference: a plain preference sort
        # pushes every L5/L6 to the tail, and the round-robin below truncates before reaching them
        take.sort(key=lambda t:(t[0],t[1]))
        ranked[lec]=[t[2] for t in take]

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
    if ONLY and subj!=ONLY: continue
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
