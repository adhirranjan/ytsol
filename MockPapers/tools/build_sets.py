"""Assemble mock sets from the agent-refined picks (RT-3 default; pass CAT5 for CAT-5).
20 MCQ (Part A) + 5 numerical (Part B) per subject, chapter quotas, breadth-first ladder,
no cross-set dupes, valid book codes. Reuses the CAT deliverable's CSS."""
import json, os, re, sys, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POOL = os.path.join(ROOT,"MockPapers","pool")
EXAMS={
 "RT3": {"nsets":10,"rank":"rankings","out":"RT3-Mock-Sets.html","date":"21-09-2026",
   "title":"ICAD RT-3 Mock Sets",
   "chord":{"PHY":["P1","P2","P3","P4","P5","P6"],"CHEM":["C1","C2","C3","C4"],
            "MATH":["M1","M2","M3","M4","M5","M6","M7"]},
   "tiers":["Core must-do","+ variants","Depth","Harder variants","Depth","+ variants",
            "Depth","Harder","Depth","Full mock"]},
 "CAT5":{"nsets":6,"rank":"rankings/cat5","out":"CAT5-Mock-Sets.html","date":"28-09-2026",
   "title":"ICAD CAT-5 Mock Sets",
   "chord":{"PHY":["P7","P8"],"CHEM":["C5"],"MATH":["M8A","M8B"]},
   "tiers":["Core must-do","+ variants","Depth","Harder variants","Depth","Full mock"]},
}
EXAM=sys.argv[1].upper() if len(sys.argv)>1 else "RT3"
CFG=EXAMS[EXAM]; NSETS=CFG["nsets"]; CHORD=CFG["chord"]
RANK = os.path.join(ROOT,"MockPapers",*CFG["rank"].split("/"))
LVLORD={"Board":7,"Sugg":8,"Recap":9}

# code -> pool row (answer, sec, lec)
META={}
for f in os.listdir(POOL):
    for r in json.load(open(os.path.join(POOL,f),encoding="utf-8")):
        META[r["code"]]=r

def chap_of(code):
    m=re.match(r"([A-Z]+\d+[A-C]?)",code); b=m.group(1)
    return "M5" if b.startswith("M5") else b   # M5A/B/C are one chapter; M8A/M8B are not
def lvl(code):
    s=META.get(code,{}).get("sec","9"); return LVLORD.get(s,int(s) if s.isdigit() else 9)
def skey(code):
    m=META.get(code,{}); lec=m.get("lec","");
    ln=re.findall(r"L(\d+)",lec); n=re.search(r"Q(\d+)$",code)
    return (int(ln[0]) if ln else 99, lec, lvl(code), int(n.group(1)) if n else 0)

def roundrobin(chapters_lists):
    out=[]; i=0
    while True:
        got=False
        for lst in chapters_lists:
            if i<len(lst): out.append(lst[i]); got=True
        if not got: break
        i+=1
    return out

def build_subject(subj):
    fin=json.load(open(os.path.join(RANK,subj+"_final.json"),encoding="utf-8"))
    chs=CHORD[subj]
    # gather picks with chapter, dedup codes globally within subject
    seen=set(); byB={c:[] for c in chs}; byA={c:[] for c in chs}
    for c in chs:
        picks=fin["chapters"][c]["picks"]
        picks=sorted(picks,key=lambda p:(p.get("tier",2),))  # tier1 first, stable
        for p in picks:
            code=p["code"]
            if code in seen or code not in META: continue
            seen.add(code)
            (byB if p.get("partB") else byA)[c].append(code)
    # deal each PART separately, per chapter, with exact per-set quotas.
    # NB: do NOT flatten chapters then deal k%NSETS - when NSETS shares a factor with the
    # chapter count the chapter parity aliases onto the set index and whole chapters vanish
    # from half the sets (6 sets x 2 chapters put zero P7 in sets 2/4/6).
    def alloc(sizes, target):
        """integer matrix q[c][s]: column sums = sizes[c], every row sum = target"""
        n = len(sizes); rem = list(sizes)
        q = [[0]*NSETS for _ in range(n)]
        for st in range(NSETS):
            left = NSETS - st
            want = [r / left for r in rem]                       # ideal share this set
            base = [int(w) for w in want]
            short = target - sum(base)
            order = sorted(range(n), key=lambda c: -(want[c] - base[c]))   # largest remainder
            for c in order[:short]: base[c] += 1
            for c in range(n):
                base[c] = min(base[c], rem[c])
            while sum(base) < target:                            # top up from whatever is left
                for c in sorted(range(n), key=lambda c: -(rem[c] - base[c])):
                    if base[c] < rem[c]: base[c] += 1; break
                else: break
            while sum(base) > target:
                for c in sorted(range(n), key=lambda c: base[c] - rem[c]):
                    if base[c] > 0: base[c] -= 1; break
                else: break
            for c in range(n):
                q[c][st] = base[c]; rem[c] -= base[c]
        assert all(r == 0 for r in rem), (sizes, target, rem)
        return q

    assert sum(len(v) for v in byB.values())==NSETS*5,  (subj,"partB",sum(len(v) for v in byB.values()))
    assert sum(len(v) for v in byA.values())==NSETS*20, (subj,"partA",sum(len(v) for v in byA.values()))
    sets=[{"A":[], "B":[]} for _ in range(NSETS)]
    for part, byc, target in (("A", byA, 20), ("B", byB, 5)):
        lists=[byc[c] for c in chs]
        q=alloc([len(l) for l in lists], target)
        for ci,lst in enumerate(lists):                          # round-robin inside a chapter
            cap=list(q[ci]); si=0
            for code in lst:
                while cap[si]==0: si=(si+1)%NSETS
                sets[si][part].append(code); cap[si]-=1; si=(si+1)%NSETS
    for s in sets:
        s["A"].sort(key=lambda c:(chs.index(chap_of(c)),)+skey(c))
        s["B"].sort(key=lambda c:(chs.index(chap_of(c)),)+skey(c))
    return sets

BUILD={s:build_subject(s) for s in ["PHY","CHEM","MATH"]}

# ---- validation ----
allcodes=[];
for si in range(NSETS):
    for subj in ["PHY","CHEM","MATH"]:
        s=BUILD[subj][si]
        assert len(s["A"])==20, (subj,si,"A",len(s["A"]))
        assert len(s["B"])==5, (subj,si,"B",len(s["B"]))
        allcodes+=s["A"]+s["B"]
assert len(allcodes)==NSETS*75, len(allcodes)
assert len(set(allcodes))==len(allcodes), "cross-set duplicate codes!"
for c in allcodes: assert c in META, "invalid code "+c
print("VALID: %d codes, %d unique, all valid book pointers"%(len(allcodes),len(set(allcodes))))

# ---- HTML (reuse CAT css) ----
cat=open(os.path.join(ROOT,"MockPapers","CAT4-Mock-Sets.html"),encoding="utf-8",errors="replace").read()
CSS=cat[cat.find("<style>"):cat.find("</style>")+8]
# house rule: no vulgar-fraction code points - they are a known source of wrong-glyph bugs
# (an agent once wrote 7/8 for 2/5) and they mix badly with plain "5/2" in the same answer.
VULGAR={"¼":"1/4","½":"1/2","¾":"3/4","⅐":"1/7","⅑":"1/9","⅒":"1/10",
        "⅓":"1/3","⅔":"2/3","⅕":"1/5","⅖":"2/5","⅗":"3/5","⅘":"4/5",
        "⅙":"1/6","⅚":"5/6","⅛":"1/8","⅜":"3/8","⅝":"5/8","⅞":"7/8"}
def ans_of(code):
    a=META[code]["answer"]; a=re.sub(r"\s+"," ",a).strip()
    # "1/2bd" would read as 1/(2bd); parenthesise when the fraction is glued to a variable
    out=[]
    for i,chx in enumerate(a):
        if chx in VULGAR:
            nxt=a[i+1] if i+1<len(a) else ""
            out.append("(%s)"%VULGAR[chx] if nxt.isalnum() else VULGAR[chx])
        else: out.append(chx)
    a="".join(out)
    return a or "?"
def grid(codes,akey=False):
    cells=[]
    for i,c in enumerate(codes,1):
        if akey:
            cells.append('<div class="cell"><span class="n">%d</span><span class="code">%s</span><span class="ans">%s</span></div>'%(i,c,ans_of(c)))
        else:
            cells.append('<div class="cell"><span class="n">%d</span><span class="code">%s</span></div>'%(i,c))
    return '<div class="grid">'+"".join(cells)+'</div>'
TIER=CFG["tiers"]
nav='<nav><b>Sets</b>'+"".join('<a href="#s%d">%d</a>'%(i+1,i+1) for i in range(NSETS))+'</nav>'
body=[]
for si in range(NSETS):
    parts=['<div class="setcard" id="s%d"><div class="sethead"><h2>Set %d <span class="tier">%s</span></h2><a class="top" href="#top">top ↑</a></div>'%(si+1,si+1,TIER[si])]
    for subj,label in [("PHY","Physics"),("CHEM","Chemistry"),("MATH","Mathematics")]:
        s=BUILD[subj][si]
        parts.append('<div class="subj"><h3>%s</h3>'%label)
        parts.append('<div class="subj"><h4>Part A · 20 MCQ (4R−1W)</h4>%s</div>'%grid(s["A"]))
        parts.append('<div class="subj"><h4>Part B · 5 Numerical (4R−1W)</h4>%s</div></div>'%grid(s["B"]))
    # answer key
    ak=['<details class="ansbox"><summary>Answer key — Set %d</summary>'%(si+1)]
    for subj,label in [("PHY","Physics"),("CHEM","Chemistry"),("MATH","Mathematics")]:
        s=BUILD[subj][si]
        ak.append('<div class="akey subj"><h4>%s · Part A</h4>%s</div>'%(label,grid(s["A"],True)))
        ak.append('<div class="akey subj"><h4>%s · Part B</h4>%s</div>'%(label,grid(s["B"],True)))
    ak.append('</details>')
    parts.append("".join(ak)+'</div>')
    body.append("".join(parts))
html=('<!doctype html><html lang="en"><head><meta charset="utf-8">'
 '<meta name="viewport" content="width=device-width, initial-scale=1"><title>%s</title>'%CFG["title"]
 +CSS+'</head><body><div class="wrap"><header id="top"><h1>%s</h1>'%CFG["title"]+
 '<p>Exam %s · %d sets · 75 Q each (25 Phy · 25 Chem · 25 Maths) · Part A 20 MCQ + Part B 5 Numerical · 4R−1W</p></header>'%(CFG["date"],NSETS)
 +nav+
 '<div class="legend">Codes are book pointers <code>{Lecture}V{Level}Q{Number}</code> '
 '(<code>VBoard</code>/<code>VSugg</code> = Board/Suggested). Sets are a priority ladder: '
 'Set 1 = the core must-do archetype of every concept; later sets add depth &amp; harder variants. '
 'Answers are the book key (re-verify — ICAD keys are ~1-in-14 defective).</div>'
 +"".join(body)+'</div></body></html>')
open(os.path.join(ROOT,"MockPapers",CFG["out"]),"w",encoding="utf-8").write(html)
print("WROTE MockPapers/%s  (%d bytes)"%(CFG["out"],len(html)))
# chapter distribution report
for subj in ["PHY","CHEM","MATH"]:
    cc=collections.Counter(chap_of(c) for si in range(NSETS) for c in BUILD[subj][si]["A"]+BUILD[subj][si]["B"])
    print(subj, dict(sorted(cc.items())))
