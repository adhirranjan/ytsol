import re, os
Q = r"E:/Adhir/AdWinUser/Desktop/icad-dps/ICAD/BooksScanned/Quiz"

# volume groupings (subject, volume-label, ordered chapter codes)
GROUPS = [
 ("Chemistry · Volume 1", ["C1","C2","C3"]),
 ("Chemistry · Volume 2", ["C4","C5","C6"]),
 ("Chemistry · Volume 3", ["C7"]),
 ("Mathematics · Volume 1", ["M1","M2","M3","M4","M5A","M5B","M5C","M6","M7"]),
 ("Mathematics · Volume 2", ["M8A","M8B","M8C"]),
 ("Physics · Volume 1", ["P1","P2","P3","P4","P5"]),
 ("Physics · Volume 2", ["P6","P7"]),
]

def parse(code):
    f = os.path.join(Q, code+"_Quiz.html")
    s = open(f, encoding="utf-8").read()
    h1 = re.search(r'<h1>(.*?)</h1>', s, re.S).group(1)
    # split "C-7 · Chemical and Ionic Equilibrium" -> tag, name
    tag, name = [x.strip() for x in h1.split("·", 1)]
    qs = int(re.search(r'(\d+) questions selected', s).group(1))
    # lecture block
    lb = s[s.index("const LECTURES"):s.index("const QUIZ")]
    lec_names = re.findall(r'name:"([^"]*)"', lb)
    units = len(lec_names)
    has_sb = any(n.startswith("Strong Box") for n in lec_names)
    # short descriptions: strip "L-n · " / "Strong Box · " prefixes
    shorts=[]
    for n in lec_names:
        n2 = re.sub(r'^(L-[0-9A-Za-z]+|Strong Box)\s*·\s*', '', n)
        shorts.append(n2)
    ds = " · ".join(shorts)
    return dict(tag=tag,name=name,qs=qs,units=units,ds=ds)

cards={}
totQ=totU=0
for _,codes in GROUPS:
    for c in codes:
        d=parse(c); cards[c]=d; totQ+=d["qs"]; totU+=d["units"]
nchap=len(cards)
expl=totQ*4

def esc(x): return x  # names already have &amp; where needed from files

html=[]
html.append('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">')
html.append('<title>ICAD JEE Mastery Quizzes — Chapter Index</title>')
html.append('''<style>
  :root{
    --bg:#0f1420; --card:#171e2e; --card2:#1e2739; --ink:#e8edf7; --muted:#9aa7bd;
    --line:#2a3550; --brand:#5b8cff; --brand2:#7aa2ff; --accent:#25b06b; --chip:#243049;
  }
  @media (prefers-color-scheme: light){
    :root{ --bg:#eef1f7; --card:#ffffff; --card2:#f5f7fb; --ink:#141a27; --muted:#5c6880;
      --line:#dde3ee; --brand:#2f6bff; --brand2:#2f6bff; --accent:#128a4f; --chip:#eef2fa; }
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    line-height:1.55;-webkit-font-smoothing:antialiased}
  .wrap{max-width:900px;margin:0 auto;padding:22px 18px 80px}
  header.hero{background:linear-gradient(135deg,#1a2a52,#12706a);border-radius:16px;padding:22px 24px;color:#eafff9}
  header.hero h1{margin:.1rem 0;font-size:1.55rem}
  header.hero p{margin:5px 0 0;opacity:.92;font-size:.9rem}
  .stats{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0}
  .stat{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:11px 18px;flex:1 1 150px}
  .stat b{display:block;font-size:1.5rem;font-weight:800;color:var(--brand2);line-height:1.2}
  .stat span{font-size:.78rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;font-weight:700}
  .howto{background:var(--card2);border:1px solid var(--line);border-radius:12px;padding:14px 18px;margin:16px 0;font-size:.9rem}
  .howto h2{margin:0 0 6px;font-size:1.02rem;color:var(--brand2)}
  .howto ol{margin:6px 0 0;padding-left:20px}
  h2.sub{margin:26px 0 8px;font-size:1.05rem;color:var(--brand2);border-bottom:1px solid var(--line);padding-bottom:5px}
  a.card{display:flex;gap:12px;align-items:flex-start;text-decoration:none;color:inherit;background:var(--card);
    border:1px solid var(--line);border-radius:12px;padding:13px 16px;margin:9px 0;transition:.14s}
  a.card:hover{border-color:var(--brand);transform:translateY(-1px);box-shadow:0 5px 16px rgba(0,0,0,.18)}
  .card .tag{flex:none;font-weight:800;color:#fff;background:var(--brand);border-radius:7px;padding:3px 10px;font-size:.8rem;min-width:44px;text-align:center}
  .card .nm{font-weight:700;font-size:.98rem}
  .card .ds{display:block;font-size:.82rem;color:var(--muted);margin-top:3px}
  .card .ct{margin-left:auto;flex:none;font-size:.78rem;font-weight:800;color:var(--brand2);
    background:var(--chip);border-radius:999px;padding:3px 11px;white-space:nowrap;align-self:center}
  .soon{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:10px;
    padding:12px 16px;margin:22px 0 0;font-size:.86rem;color:var(--muted)}
  .soon b{color:var(--ink)}
  .foot{text-align:center;color:var(--muted);font-size:.8rem;margin-top:30px}
</style>
</head>
<body>
<div class="wrap">''')
html.append(f'''  <header class="hero">
    <p>ICAD · JEE Foundation</p>
    <h1>🎯 Chapter Mastery Quizzes</h1>
    <p>Pick the lectures you want, answer, review what you missed, then be re-quizzed on exactly those questions — until every answer is right.</p>
  </header>

  <div class="stats">
    <div class="stat"><b>{nchap}</b><span>Chapters</span></div>
    <div class="stat"><b>{totQ}</b><span>Questions</span></div>
    <div class="stat"><b>{expl}</b><span>Option explanations</span></div>
    <div class="stat"><b>{totU}</b><span>Lecture units</span></div>
  </div>

  <div class="howto">
    <h2>How each quiz works</h2>
    <ol>
      <li>Choose the lectures to be quizzed on (all selected by default).</li>
      <li>Answer the round and <b>Submit</b>.</li>
      <li>Work through the <b>compulsory review</b> — why the right option is right and why each wrong option is wrong.</li>
      <li><b>Re-quiz</b> on exactly the questions you missed, with the options reshuffled.</li>
      <li>Repeat until <b>every selected question is correct</b> 🏆.</li>
    </ol>
  </div>
''')

for label, codes in GROUPS:
    html.append(f'  <h2 class="sub">{label}</h2>')
    for c in codes:
        d=cards[c]
        html.append(f'''  <a class="card" href="{c}_Quiz.html">
    <span class="tag">{d["tag"]}</span>
    <span>
      <span class="nm">{d["name"]}</span>
      <span class="ds">{d["ds"]}</span>
    </span>
    <span class="ct">{d["qs"]} Q · {d["units"]} units</span>
  </a>''')

html.append('''
  <p class="soon"><b>26 chapters live · more on the way.</b> Remaining to build: Mathematics M-8D, M-9, M-10, M-11 and Physics P-8, P-9, P-10. Every answer is re-derived and numerically checked rather than transcribed, and a few questions deliberately surface printing errors found in the modules themselves.</p>

  <div class="foot">ICAD · chapter mastery quizzes · built from the lecture PDFs and their YouTube solutions · every answer re-derived, not transcribed.</div>
</div>
</body>
</html>''')

out = "\n".join(html)
open(os.path.join(Q,"Quiz_Index.html"),"w",encoding="utf-8").write(out)
print("rebuilt Quiz_Index.html:", len(out), "bytes")
print("chapters", nchap, "Q", totQ, "units", totU, "explanations", expl)
