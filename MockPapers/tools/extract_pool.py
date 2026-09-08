"""Extract in-scope question pool per lecture -> MockPapers/pool/<LEC>.json (durable).
Rebuilt from source HTML (scratchpad wiped). h2-based sections; merged files split by sub-lecture prefix.
Codes: {lec}V{token}Q{num}  token = level N | Board | Sugg | Recap.  SB excluded.
"""
import re, os, glob, json, html, sys, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "MockPapers", "pool")
os.makedirs(OUT, exist_ok=True)

ALLOWED = {"P1","P2","P3","P4","P5","P6","C1","C2","C3","C4",
           "M1","M2","M3","M4","M5A","M5B","M5C","M6","M7"}

def chapter_of(base):
    m = re.match(r"^([A-Z]+\d+)([A-Z])?L", base)
    if not m: return None
    return m.group(1) + (m.group(2) or "")

def sec_token(h):
    h = re.sub(r"<span.*?</span>", "", h, flags=re.S)
    h = h.strip()
    sub = None
    m = re.match(r"L(\d+)\s*[—\-–]\s*(.*)", h)   # merged sub-lecture prefix "L2 — Level 2"
    if m:
        sub = int(m.group(1)); h = m.group(2).strip()
    hl = h.lower()
    if "suggested" in hl: tok = "Sugg"
    elif "board" in hl:   tok = "Board"
    elif "recap" in hl:   tok = "Recap"
    else:
        m = re.search(r"level\s*[-–]?\s*(\d+)", hl)
        tok = m.group(1) if m else None
    return sub, tok

def strip(t):
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()

LEAK = re.compile(r"\(\s*Ans[^)]*\)?.*$", re.I|re.S)   # trailing answer leak
LVL  = re.compile(r"\(\s*Level[\s\-–]*\d+\s*\)", re.I)

def clean_q(t):
    t = LEAK.sub("", t); t = LVL.sub("", t)
    return re.sub(r"\s+", " ", t).strip()

# row = num, q, topic, ans in order; capture with positions to bucket under h2
ROW = re.compile(r'<td class="num">(.*?)</td>\s*<td class="q">(.*?)</td>\s*<td class="topic">(.*?)</td>\s*<td class="ans">(.*?)</td>', re.S)
H2  = re.compile(r"<h2[^>]*>(.*?)</h2>", re.S)

def parse(path, base):
    ch = chapter_of(base)
    t = open(path, encoding="utf-8", errors="replace").read()
    # positions of h2 headers
    heads = [(m.start(), m.group(1)) for m in H2.finditer(t)]
    def head_for(pos):
        cur = (None, None)
        for hp, hraw in heads:
            if hp < pos: cur = sec_token(hraw)
            else: break
        return cur
    out = []
    for m in ROW.finditer(t):
        sub, tok = head_for(m.start())
        if tok is None: continue
        num = strip(m.group(1))
        if not re.match(r"^\d+$", num):
            num = re.sub(r"\D", "", num) or num
        lec = ch + ("L%d" % sub if sub else base[len(ch):].split("_")[0] if sub is None and re.match(r"^[A-Z]+\d+[A-Z]?L\d+$", base) else base[len(ch):])
        # simpler: if sub known -> chapter+Lsub ; else use full filename base
        lec = (ch + "L%d" % sub) if sub else base
        qraw = m.group(2); qtxt = clean_q(strip(qraw))
        ans = strip(m.group(4))
        opts = bool(re.search(r"\([a-dA-D]\)", strip(qraw)))
        low = qtxt.lower()
        fmt = ("match" if ("match" in low and "column" in low) else
               "statement" if ("statement" in low or "assertion" in low) else
               "mcq" if opts else "open")
        code = "%sV%sQ%s" % (lec, tok, num)
        out.append({"code":code,"lec":lec,"sec":tok,"num":num,
                    "answer":ans,"format":fmt,"has_opts":opts,"stem":qtxt[:400]})
    return out

files = glob.glob(os.path.join(ROOT, "**", "*_YouTube_Solutions.html"), recursive=True)
bylec = collections.defaultdict(list)
skipped = collections.Counter()
for f in files:
    base = os.path.basename(f).replace("_YouTube_Solutions.html","")
    if "CAT4-2026" in base or "RT2-2026" in base or "RT3" in base: continue
    if re.match(r"[A-Z]+\d+[A-Z]?SB$", base):   # Strong Box excluded
        skipped["SB"]+=1; continue
    ch = chapter_of(base)
    if ch not in ALLOWED:
        skipped["out-of-scope"]+=1; continue
    for row in parse(f, base):
        bylec[row["lec"]].append(row)

# dedup within lecture by normalized stem
total=0
for lec, rows in bylec.items():
    seen={}; uniq=[]
    for r in rows:
        k=re.sub(r"[^a-z0-9]","",r["stem"].lower())[:120]
        if k in seen: continue
        seen[k]=1; uniq.append(r)
    json.dump(uniq, open(os.path.join(OUT,lec+".json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    total+=len(uniq)

print("lectures:",len(bylec),"questions:",total,"skipped:",dict(skipped))
# chapter summary
chap=collections.Counter()
for lec,rows in bylec.items():
    c=chapter_of(lec+"L0") or re.match(r"[A-Z]+\d+[A-Z]?",lec).group(0)
    chap[re.match(r"[A-Z]+\d+[A-Z]?",lec).group(0)]+=len(set(r["code"] for r in rows))
for c in sorted(chap): print(f"  {c:4} {chap[c]}")
