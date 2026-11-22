import re,glob,os,json,html,sys
sys.stdout.reconfigure(encoding='utf-8')
CH=sys.argv[2].split(',') if len(sys.argv)>2 else ['P1','P2','P3','P4','P5','P6','C1','C2','C3','C4','M1','M2','M3','M4','M5A','M5B','M5C','M6','M7']
root='YouTube_Solutions'
out=[]
def clean(x): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x))).strip()
secabbr=lambda s: ('Lvl'+s.split()[-1]) if s.startswith('Level ') and s.split()[-1].isdigit() else {'Level: Board':'Board','Suggested Problems':'Sugg','Quick Recap':'Recap'}.get(s,s)
for ch in CH:
    for f in glob.glob(f'{root}/*/{ch}_YouTube_Solutions/{ch}*_YouTube_Solutions.html'):
        lec=os.path.basename(f).split('_')[0]; L=lec[len(ch):]
        s=open(f,encoding='utf-8').read()
        parts=re.split(r'(<h2[^>]*>.*?</h2>)',s,flags=re.S)
        sec='?'
        for p in parts:
            if p.startswith('<h2'): sec=secabbr(clean(p)); continue
            for tr in re.findall(r'<tr[^>]*>(.*?)</tr>',p,flags=re.S):
                if 'solnrow' in tr or '<th' in tr or 'colspan' in tr: continue
                tds=re.findall(r'<td[^>]*>(.*?)</td>',tr,flags=re.S)
                if len(tds)<3: continue
                a=re.search(r'<a\b[^>]*?href="([^"]+)"[^>]*>(.*?)</a>',tr,flags=re.S)
                m='exact' if 'badge exact' in tr else ('similar' if 'badge sim' in tr else '')
                ans=re.search(r'class="ansval[^"]*">(.*?)</span></td>',tr,flags=re.S)
                out.append(dict(ref=f'{ch} · {L} · {sec} · Q{clean(tds[0])}',q=clean(tds[1])[:600],url=a.group(1) if a else None,title=clean(a.group(2)) if a else None,match=m,ans=clean(ans.group(1)) if ans else None))
json.dump(out,open(sys.argv[1],'w',encoding='utf-8'),ensure_ascii=False,indent=0)
with open(sys.argv[1].replace('.json','.txt'),'w',encoding='utf-8') as g:
    for r in out: g.write(f"{r['ref']} | {r['q']} || ANS: {r['ans']} || VID: {r['url']} [{r['match']}] {r['title']}\n")
print(len(out)); import collections; print(collections.Counter(r['ref'].split(' · ')[0] for r in out))
