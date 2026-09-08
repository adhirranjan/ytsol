"""Per-chapter drills (mock-style, code-pointer), TWO versions each, grouped by level band.
  1. <CH>-Coverage.html : 1 rep per (lecture x band) across all 8 bands + mid-level (L3/L4) top-up
                          from the mock archetypes -> full difficulty coverage + method density.
  2. <CH>-Mock.html     : the chapter's mock-paper picks only (high-yield, mid-level sample).
Also writes ChapterPapers/Chapter_Index.html.
Usage: python build_chapter.py [CH]   (no arg = all 17 + index)."""
import json, os, re, sys, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POOL = os.path.join(ROOT,"MockPapers","pool"); RANK=os.path.join(ROOT,"MockPapers","rankings")
OUT  = os.path.join(ROOT,"MockPapers","ChapterPapers"); os.makedirs(OUT, exist_ok=True)
BANDS=["1","2","3","4","5","6","Board","Sugg"]          # coverage bands (Recap = theory, excluded there)
DISPLAY=BANDS+["Recap"]                                  # Mock version shows everything, incl. any Recap
BANDNAME={"1":"Level 1","2":"Level 2","3":"Level 3","4":"Level 4","5":"Level 5","6":"Level 6",
          "Board":"Level: Board","Sugg":"Suggested Problems","Recap":"Quick Recap"}
BANDSHORT={"1":"L1","2":"L2","3":"L3","4":"L4","5":"L5","6":"L6","Board":"Board","Sugg":"Sugg","Recap":"Recap"}
SUBJ={"PHY":["P1","P2","P3","P4","P5","P6"],"CHEM":["C1","C2","C3","C4"],
      "MATH":["M1","M2","M3","M4","M5","M6","M7"]}
SUBJ_OF={c:s for s,cs in SUBJ.items() for c in cs}
CHNAME={"P1":"BMT-1","P2":"BMT-2","P3":"Vectors","P4":"Motion in 1D & 2D","P5":"Force System",
 "P6":"Newton's Laws of Motion","C1":"States of Matter","C2":"Structure of Atom",
 "C3":"Basics of Chemistry","C4":"Classification of Elements — Periodicity",
 "M1":"Angle Measurement","M2":"Set Theory","M3":"Trig Ratios & Identity","M4":"Function-I",
 "M5":"Compound Angles → Conditional Identities","M6":"Functions-2","M7":"Exp & Log Eqn/Ineqn"}
def chap(lec):
    b=re.match(r'([A-Z]+\d+)',lec).group(1); return 'M5' if b.startswith('M5') else b
def qnum(c):
    m=re.search(r'Q(\d+)$',c); return int(m.group(1)) if m else 0
def norm(s): return re.sub(r'[^a-z0-9]','',s.lower())[:80]

# global pool meta
META={}; CH_ROWS=collections.defaultdict(list)
for f in os.listdir(POOL):
    lec=f[:-5]
    for r in json.load(open(os.path.join(POOL,f),encoding="utf-8")):
        META[r["code"]]=r
        if r["sec"] in BANDS: CH_ROWS[chap(lec)].append(r)
CAT=open(os.path.join(ROOT,"MockPapers","CAT4-Mock-Sets.html"),encoding="utf-8",errors="replace").read()
CSS=CAT[CAT.find("<style>"):CAT.find("</style>")+8]

def mock_codes(ch):
    # EVERY pick for this chapter that is in the mock (== all its questions across the 10 sets).
    # No band filter -> nothing can be silently dropped.
    fin=json.load(open(os.path.join(RANK,SUBJ_OF[ch]+"_final.json"),encoding="utf-8"))
    seen=set(); out=[]
    for p in fin["chapters"][ch]["picks"]:
        c=p["code"]
        if c in META and c not in seen: seen.add(c); out.append(c)
    return out

def coverage_rows(ch):
    cells=collections.defaultdict(list)
    for r in CH_ROWS[ch]: cells[(r["sec"],r["lec"])].append(r)
    chosen=[]; used=set(); usedstem=set()
    # 1 rep per (band,lecture) cell
    lecs=sorted(set(r["lec"] for r in CH_ROWS[ch]))
    for band in BANDS:
        for lec in lecs:
            rows=sorted(cells.get((band,lec),[]),key=lambda r:qnum(r["code"]))
            for r in rows:
                if norm(r["stem"]) in usedstem: continue
                chosen.append(r); used.add(r["code"]); usedstem.add(norm(r["stem"])); break
    # top-up: mock archetypes at L3/L4 not already present
    for c in mock_codes(ch):
        r=META[c]
        if r["sec"] in ("3","4") and c not in used and norm(r["stem"]) not in usedstem:
            chosen.append(r); used.add(c); usedstem.add(norm(r["stem"]))
    return chosen

def render(ch, rows, version, subtitle):
    byband=collections.defaultdict(list)
    for r in rows: byband[r["sec"]].append(r)
    for b in byband: byband[b].sort(key=lambda r:(r["lec"],qnum(r["code"])))
    total=len(rows)
    def grid(rs,akey=False):
        out=[]
        for i,r in enumerate(rs,1):
            a='<span class="ans">%s</span>'%re.sub(r"\s+"," ",r["answer"]).strip() if akey else ''
            out.append('<div class="cell"><span class="n">%d</span><span class="code">%s</span>%s</div>'%(i,r["code"],a))
        return '<div class="grid">'+"".join(out)+'</div>'
    nav=[]; body=[]; ak=['<details class="ansbox"><summary>Answer key (%d)</summary>'%total]
    for band in DISPLAY:
        if band not in byband: continue
        rs=byband[band]; bid="b_"+band
        nav.append('<a href="#%s">%s (%d)</a>'%(bid,BANDSHORT[band],len(rs)))
        body.append('<div class="subj" id="%s"><h3>%s <span style="color:var(--mut);font-weight:400;font-size:.85rem">(%d)</span></h3>%s</div>'%(bid,BANDNAME[band],len(rs),grid(rs)))
        ak.append('<div class="akey subj"><h4>%s</h4>%s</div>'%(BANDNAME[band],grid(rs,True)))
    ak.append('</details>')
    tag=" · ".join("%s %d"%(BANDSHORT[b],len(byband[b])) for b in BANDS if b in byband)
    html=('<!doctype html><html lang="en"><head><meta charset="utf-8">'
     '<meta name="viewport" content="width=device-width, initial-scale=1"><title>ICAD %s %s</title>'%(ch,version)
     +CSS+'</head><body><div class="wrap"><header id="top"><h1>%s · %s <span class="tier">%s</span></h1>'%(ch,CHNAME.get(ch,ch),version)
     +'<p>%s · %d questions · %s</p></header>'%(subtitle,total,tag)
     +'<nav><b>Levels</b>'+"".join(nav)+' &nbsp; <a href="Chapter_Index.html">all chapters ↗</a></nav>'
     +'<div class="legend">Codes are book pointers <code>{Lecture}V{Level}Q{Number}</code>. '
      'Answers are the book key — re-verify (ICAD keys ~1-in-14 defective).</div>'
     +'<div class="setcard">'+"".join(body)+"".join(ak)+'</div></div></body></html>')
    p=os.path.join(OUT,"%s-%s.html"%(ch,version)); open(p,"w",encoding="utf-8").write(html)
    return total

def build(ch):
    cov=coverage_rows(ch)
    codes=mock_codes(ch); mk=[META[c] for c in codes]
    # invariant: Mock version == ALL of this chapter's questions across the 10 mock sets
    fin=json.load(open(os.path.join(RANK,SUBJ_OF[ch]+"_final.json"),encoding="utf-8"))
    want={p["code"] for p in fin["chapters"][ch]["picks"] if p["code"] in META}
    assert want.issubset(set(codes)), (ch,"Mock dropped",want-set(codes))
    n1=render(ch,cov,"Coverage","Full-coverage drill — every lecture at every level + mid-level depth")
    n2=render(ch,mk,"Mock","All of this chapter's questions from the 10 mock sets")
    print(f"{ch:4} Coverage {n1:3}  Mock {n2:3}")
    return n1,n2

def build_index(stats):
    rows=[]
    for s,chs in SUBJ.items():
        cards=[]
        for ch in chs:
            n1,n2=stats[ch]
            cards.append('<div class="cell" style="flex-direction:column;align-items:stretch;gap:4px;padding:8px 10px">'
              '<b>%s · %s</b>'
              '<span><a href="%s-Coverage.html">Coverage (%d)</a> &nbsp;·&nbsp; <a href="%s-Mock.html">Mock (%d)</a></span></div>'%(ch,CHNAME[ch],ch,n1,ch,n2))
        rows.append('<div class="subj"><h3>%s</h3><div class="grid" style="grid-template-columns:repeat(2,1fr)">%s</div></div>'%(
            {"PHY":"Physics","CHEM":"Chemistry","MATH":"Mathematics"}[s],"".join(cards)))
    html=('<!doctype html><html lang="en"><head><meta charset="utf-8">'
     '<meta name="viewport" content="width=device-width, initial-scale=1"><title>ICAD Chapter Papers</title>'
     +CSS+'</head><body><div class="wrap"><header id="top"><h1>ICAD Chapter Papers</h1>'
     '<p>RT-3 syllabus · per-chapter drills · two versions each</p></header>'
     '<div class="legend"><b>Coverage</b> = every lecture at every level (1–6 + Board + Suggested) + mid-level depth — master the whole chapter. '
     '<b>Mock</b> = the chapter\'s mock-paper picks only (high-yield, mid-level). Number in ( ) = question count.</div>'
     +"".join(rows)+'</div></body></html>')
    open(os.path.join(OUT,"Chapter_Index.html"),"w",encoding="utf-8").write(html)
    print("WROTE ChapterPapers/Chapter_Index.html")

if __name__=="__main__":
    if len(sys.argv)>1:
        build(sys.argv[1])
    else:
        stats={}
        for s,chs in SUBJ.items():
            for ch in chs: stats[ch]=build(ch)
        build_index(stats)
        print("TOTAL files:", len(stats)*2+1)
