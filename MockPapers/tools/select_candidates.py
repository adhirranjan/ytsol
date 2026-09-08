"""RT-3 candidate selector. Deterministic ranked shortlist per subject from MockPapers/pool.
RT weighting (newest chapter anchored, tools light/embedded). Book structure = clustering:
spread across (lecture x level) cells -> method diversity + difficulty spread for free.
Output: MockPapers/rankings/<SUBJECT>_candidates.json  (picks + buffer for agent review)."""
import json, os, glob, re, collections, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POOL = os.path.join(ROOT, "MockPapers", "pool")
OUT  = os.path.join(ROOT, "MockPapers", "rankings"); os.makedirs(OUT, exist_ok=True)

# per-chapter quota = total questions from chapter across all 10 sets (subject sums to 250)
QUOTA = {
 "PHY": {"P6":70,"P5":35,"P4":60,"P3":40,"P2":25,"P1":20},
 "CHEM":{"C4":70,"C3":65,"C2":60,"C1":55},
 "MATH":{"M7":45,"M6":45,"M5":55,"M4":30,"M3":25,"M2":25,"M1":25},
}
SUBJ_CH = {"PHY":["P1","P2","P3","P4","P5","P6"],
           "CHEM":["C1","C2","C3","C4"],
           "MATH":["M1","M2","M3","M4","M5","M6","M7"]}
# level pick preference: mid-levels first (exam sweet spot), then edges
LEVELPREF = {"3":0,"4":1,"2":2,"5":3,"Board":4,"1":5,"6":6,"Sugg":7,"Recap":8}

def chap_of_lec(lec):
    m = re.match(r"([A-Z]+\d+)", lec); base = m.group(1)
    # merge M5A/B/C -> M5
    if base.startswith("M5"): return "M5"
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
    # bucket by lecture; within lecture order by level preference
    bylec=collections.defaultdict(list)
    for r in uniq: bylec[r["lec"]].append(r)
    for lec in bylec:
        bylec[lec].sort(key=lambda r: (LEVELPREF.get(r["sec"],9), r["stem"][:30]))
    # round-robin across lectures (breadth first = ladder), collect need*1.5
    target=int(need*1.5)+2
    order=sorted(bylec)  # stable lecture order
    picks=[]; idx={l:0 for l in order}; guard=0
    while len(picks)<target and guard<10000:
        guard+=1; progressed=False
        for lec in order:
            i=idx[lec]
            if i<len(bylec[lec]):
                picks.append(bylec[lec][i]); idx[lec]+=1; progressed=True
                if len(picks)>=target: break
        if not progressed: break
    for rank,r in enumerate(picks,1):
        r["chap_rank"]=rank; r["numeric"]=numeric(r["answer"])
    return picks

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
