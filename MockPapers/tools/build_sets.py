"""Assemble 10 RT-3 mock sets from the agent-refined picks -> MockPapers/RT3-Mock-Sets.html.
20 MCQ (Part A) + 5 numerical (Part B) per subject, chapter quotas, breadth-first ladder,
no cross-set dupes, valid book codes. Reuses the CAT deliverable's CSS."""
import json, os, re, sys, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POOL = os.path.join(ROOT,"MockPapers","pool")
RANK = os.path.join(ROOT,"MockPapers","rankings")
NSETS=10
CHORD={"PHY":["P1","P2","P3","P4","P5","P6"],"CHEM":["C1","C2","C3","C4"],
       "MATH":["M1","M2","M3","M4","M5","M6","M7"]}
LVLORD={"Board":7,"Sugg":8,"Recap":9}

# code -> pool row (answer, sec, lec)
META={}
for f in os.listdir(POOL):
    for r in json.load(open(os.path.join(POOL,f),encoding="utf-8")):
        META[r["code"]]=r

def chap_of(code):
    m=re.match(r"([A-Z]+\d+)",code); b=m.group(1)
    return "M5" if b.startswith("M5") else b
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
    Bflat=roundrobin([byB[c] for c in chs])
    Aflat=roundrobin([byA[c] for c in chs])
    # enforce 50 B / 200 A
    while len(Bflat)>NSETS*5:            # too many B -> move tail to A
        Aflat.append(Bflat.pop())
    ai=0
    while len(Bflat)<NSETS*5 and ai<len(Aflat):   # too few B -> borrow numeric-answer A
        c=Aflat[ai]; ans=META[c]["answer"]
        if not re.match(r"^[a-dA-D][\s\).:]",ans.strip()):
            Bflat.append(Aflat.pop(ai))
        else: ai+=1
    Aflat=Aflat[:NSETS*20]
    Bflat=Bflat[:NSETS*5]
    sets=[{"A":[], "B":[]} for _ in range(NSETS)]
    for k,code in enumerate(Aflat): sets[k%NSETS]["A"].append(code)
    for k,code in enumerate(Bflat): sets[k%NSETS]["B"].append(code)
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
def ans_of(code):
    a=META[code]["answer"]; a=re.sub(r"\s+"," ",a).strip()
    return a or "?"
def grid(codes,akey=False):
    cells=[]
    for i,c in enumerate(codes,1):
        if akey:
            cells.append('<div class="cell"><span class="n">%d</span><span class="code">%s</span><span class="ans">%s</span></div>'%(i,c,ans_of(c)))
        else:
            cells.append('<div class="cell"><span class="n">%d</span><span class="code">%s</span></div>'%(i,c))
    return '<div class="grid">'+"".join(cells)+'</div>'
TIER=["Core must-do","+ variants","Depth","Harder variants","Depth","+ variants","Depth","Harder","Depth","Full mock"]
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
 '<meta name="viewport" content="width=device-width, initial-scale=1"><title>ICAD RT-3 Mock Sets</title>'
 +CSS+'</head><body><div class="wrap"><header id="top"><h1>ICAD RT-3 Mock Sets</h1>'
 '<p>Exam 21-09-2026 · 10 sets · 75 Q each (25 Phy · 25 Chem · 25 Maths) · Part A 20 MCQ + Part B 5 Numerical · 4R−1W</p></header>'
 +nav+
 '<div class="legend">Codes are book pointers <code>{Lecture}V{Level}Q{Number}</code> '
 '(<code>VBoard</code>/<code>VSugg</code> = Board/Suggested). Sets are a priority ladder: '
 'Set 1 = the core must-do archetype of every concept; later sets add depth &amp; harder variants. '
 'Answers are the book key (re-verify — ICAD keys are ~1-in-14 defective).</div>'
 +"".join(body)+'</div></body></html>')
open(os.path.join(ROOT,"MockPapers","RT3-Mock-Sets.html"),"w",encoding="utf-8").write(html)
print("WROTE MockPapers/RT3-Mock-Sets.html  (%d bytes)"%len(html))
# chapter distribution report
for subj in ["PHY","CHEM","MATH"]:
    cc=collections.Counter(chap_of(c) for si in range(NSETS) for c in BUILD[subj][si]["A"]+BUILD[subj][si]["B"])
    print(subj, dict(sorted(cc.items())))
