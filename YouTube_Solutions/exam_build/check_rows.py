"""Gate every row: JSON fields, skeleton, length, <pre> width, fraction entities, tag balance."""
import json,glob,re,sys,os
sys.stdout.reconfigure(encoding='utf-8')
S=sys.argv[1]  # exam work folder holding rows/
KEYS="num q_html topic video_url video_title match key ans_letter ans_text flag bookref_tag bookref soln_html".split()
FRAC=re.compile(r'&frac\d\d;|&#85(2[8-9]|3\d|4[0-6]);|[\u00bc-\u00be\u2150-\u215e]')
bad=0; lens=[]
for f in sorted(glob.glob(S+'/rows/Q*.json')):
    r=json.load(open(f,encoding='utf-8')); n=r.get('num'); errs=[]
    errs+=[f'missing {k}' for k in KEYS if k not in r]
    s=r.get('soln_html','')
    for need in ('<span class="lbl">Concept','<span class="lbl">Formula','<span class="lbl">Solution','JEE Trick','<div class="final">'):
        if need not in s: errs.append('no '+need)
    if s.count('class="step"')<3: errs.append('steps<3')
    for t in ('div','pre','span'):
        if len(re.findall(f'<{t}\\b',s))!=s.count(f'</{t}>'): errs.append(f'{t} imbalance')
    for pre in re.findall(r'<pre>(.*?)</pre>',s+r.get('q_html',''),re.S):  # question tables too
        if any(len(re.sub(r'<[^>]+>','',l))>62 for l in pre.split('\n')): errs.append('pre>62')
    for k in ('q_html','ans_text','soln_html','flag','topic','video_title'):
        if r.get(k) and FRAC.search(str(r[k])): errs.append('fraction glyph in '+k)
    if r.get('flag') and '<' in r['flag']: errs.append('html in flag')
    L=len(s); lens.append(L)
    if not 1400<=L<=2800: errs.append(f'len {L}')
    if r.get('video_url') and not re.match(r'https://www\.youtube\.com/watch\?v=[\w-]{11}$',r['video_url']): errs.append('bad url')
    if errs: bad+=1; print(f'Q{n:02d}',errs)
lens.sort()
print('rows',len(lens),'bad',bad,'median len',lens[len(lens)//2] if lens else '-')
