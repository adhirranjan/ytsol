"""Per-chapter COVERAGE drill (mock-style, code-pointer). Full coverage = 1 representative per
(lecture x level-band) cell, grouped by level band so every lecture at every difficulty shows.
Usage: python build_chapter.py <CHAPTER>   e.g. C4, P6, M5.  Out: MockPapers/ChapterPapers/<CH>-Chapter-Paper.html"""
import json, os, re, sys, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POOL = os.path.join(ROOT,"MockPapers","pool")
OUT  = os.path.join(ROOT,"MockPapers","ChapterPapers"); os.makedirs(OUT, exist_ok=True)
BANDS=["1","2","3","4","5","6","Board","Sugg"]            # Recap excluded
BANDNAME={"1":"Level 1","2":"Level 2","3":"Level 3","4":"Level 4","5":"Level 5","6":"Level 6",
          "Board":"Level: Board","Sugg":"Suggested Problems"}
PERCELL=1                                                  # representatives per (lecture,band) cell
CHNAME={"P1":"BMT-1","P2":"BMT-2","P3":"Vectors","P4":"Motion in 1D & 2D","P5":"Force System",
 "P6":"Newton's Laws of Motion","C1":"States of Matter","C2":"Structure of Atom",
 "C3":"Basics of Chemistry","C4":"Classification of Elements — Periodicity",
 "M1":"Angle Measurement","M2":"Set Theory","M3":"Trig Ratios & Identity","M4":"Function-I",
 "M5":"Compound Angles → Conditional Identities","M6":"Functions-2","M7":"Exp & Log Eqn/Ineqn"}
def chap(lec):
    b=re.match(r'([A-Z]+\d+)',lec).group(1); return 'M5' if b.startswith('M5') else b

def build(ch):
    cells=collections.defaultdict(list)      # (band,lec) -> rows
    lecs=set()
    for f in os.listdir(POOL):
        lec=f[:-5]
        if chap(lec)!=ch: continue
        lecs.add(lec)
        for r in json.load(open(os.path.join(POOL,f),encoding="utf-8")):
            if r["sec"] in BANDS: cells[(r["sec"],lec)].append(r)
    # 1 (or PERCELL) representative per cell, deduped by stem
    chosen=[]
    for band in BANDS:
        for lec in sorted(lecs):
            rows=cells.get((band,lec))
            if not rows: continue
            seen=set(); reps=[]
            rows=sorted(rows,key=lambda r:int(re.search(r'Q(\d+)$',r['code']).group(1)) if re.search(r'Q(\d+)$',r['code']) else 0)
            for r in rows:
                k=re.sub(r'[^a-z0-9]','',r['stem'].lower())[:80]
                if k in seen: continue
                seen.add(k); reps.append(r)
                if len(reps)>=PERCELL: break
            for r in reps: chosen.append((band,lec,r))
    # css
    cat=open(os.path.join(ROOT,"MockPapers","CAT4-Mock-Sets.html"),encoding="utf-8",errors="replace").read()
    CSS=cat[cat.find("<style>"):cat.find("</style>")+8]
    def ansof(c,META):
        a=re.sub(r"\s+"," ",META[c]).strip(); return a or "?"
    META={r['code']:r['answer'] for _,_,r in chosen}
    # group for display by band
    byband=collections.defaultdict(list)
    for band,lec,r in chosen: byband[band].append(r)
    total=len(chosen)
    def grid(rows,akey=False):
        cells_html=[]
        for i,r in enumerate(rows,1):
            c=r['code']; extra='<span class="ans">%s</span>'%ansof(c,META) if akey else ''
            cells_html.append('<div class="cell"><span class="n">%d</span><span class="code">%s</span>%s</div>'%(i,c,extra))
        return '<div class="grid">'+"".join(cells_html)+'</div>'
    body=[]; nav=[]
    for band in BANDS:
        if band not in byband: continue
        rows=byband[band]; bid="b_"+band
        nav.append('<a href="#%s">%s</a>'%(bid,BANDNAME[band].replace("Level ","L").replace("Suggested Problems","Sugg").replace("Level: Board","Board")))
        body.append('<div class="subj" id="%s"><h3>%s <span style="color:var(--mut);font-weight:400;font-size:.85rem">(%d)</span></h3>%s</div>'%(bid,BANDNAME[band],len(rows),grid(rows)))
    # answer key (all, grouped)
    ak=['<details class="ansbox"><summary>Answer key (%d)</summary>'%total]
    for band in BANDS:
        if band not in byband: continue
        ak.append('<div class="akey subj"><h4>%s</h4>%s</div>'%(BANDNAME[band],grid(byband[band],True)))
    ak.append('</details>')
    html=('<!doctype html><html lang="en"><head><meta charset="utf-8">'
     '<meta name="viewport" content="width=device-width, initial-scale=1"><title>ICAD %s Chapter Paper</title>'%ch
     +CSS+'</head><body><div class="wrap"><header id="top"><h1>%s · %s</h1>'%(ch,CHNAME.get(ch,ch))
     +'<p>Full-coverage chapter drill · %d questions · every lecture at every level (Levels 1–6 + Board + Suggested) · 4R−1W</p></header>'%total
     +'<nav><b>Levels</b>'+"".join(nav)+'</nav>'
     +'<div class="legend">Codes are book pointers <code>{Lecture}V{Level}Q{Number}</code>. '
      'One representative per (lecture × level) cell — clear the whole sheet and you have covered every concept in the chapter at every difficulty. '
      'Answers are the book key — re-verify (ICAD keys ~1-in-14 defective).</div>'
     +'<div class="setcard">'+"".join(body)+"".join(ak)+'</div></div></body></html>')
    p=os.path.join(OUT,ch+"-Chapter-Paper.html"); open(p,"w",encoding="utf-8").write(html)
    covered=collections.Counter(b for b,_,_ in chosen)
    print("WROTE",os.path.relpath(p,ROOT),"| total",total,"| lectures",len(lecs),"| by band",dict(covered))

if __name__=="__main__":
    build(sys.argv[1] if len(sys.argv)>1 else "C4")
