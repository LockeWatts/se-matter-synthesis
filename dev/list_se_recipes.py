import sys,re,os,glob
ROOT=sys.argv[1]
def blocks(txt):
    # strip comments
    out=[];st=[];i=0;n=len(txt);pairs=[]
    instr=None
    while i<n:
        c=txt[i]
        if instr:
            if c=='\\': i+=2; continue
            if c==instr: instr=None
        elif c in '"\'': instr=c
        elif c=='-' and txt[i:i+2]=='--':
            j=txt.find('\n',i); i=j if j>=0 else n; continue
        elif c=='{': st.append(i)
        elif c=='}':
            if st: s=st.pop(); pairs.append((s,i+1,len(st)))
        i+=1
    return pairs
def clean(s):
    s=re.sub(r'--[^\n]*','',s)
    s=s.replace('data_util.mod_prefix .. "','"se-').replace("data_util.mod_prefix ..\"",'"se-')
    s=re.sub(r'\s+',' ',s)
    s=re.sub(r'type ?= ?"(item|fluid)", ?','',s)
    return s
def field(b,key):
    m=re.search(r'\b'+key+r'\s*=\s*',b)
    if not m: return None
    j=m.end()
    if b[j]=='{':
        d=0
        for k in range(j,len(b)):
            if b[k]=='{': d+=1
            elif b[k]=='}':
                d-=1
                if d==0: return b[j:k+1]
    m2=re.match(r'[^,\n}]+',b[j:]); return m2.group(0).strip()
recs=[]
for f in glob.glob(ROOT+'/**/*.lua',recursive=True):
    txt=open(f,errors='replace').read()
    ps=blocks(txt)
    cand=[(s,e) for s,e,d in ps if re.search(r'\bingredients\s*=',txt[s:e])]
    # innermost
    inner=[(s,e) for s,e in cand if not any((s2>s and e2<e) for s2,e2 in cand)]
    for s,e in inner:
        b=txt[s:e]
        ln=txt.count('\n',0,s)+1
        recs.append(dict(file=os.path.relpath(f,ROOT),line=ln,name=clean(field(b,'name') or '?'),ing=clean(field(b,'ingredients') or ''),res=clean(field(b,'results') or ''),t=field(b,'energy_required'),cat=clean(field(b,'categories') or field(b,'category') or ''),raw=b))
mode=sys.argv[2]; pats=sys.argv[3:]
for r in recs:
    for p in pats:
        tgt = (r['res'] if not re.search(p,r['ing']) else '') if mode=='net' else r['res']+' '+r['name'] if mode=='makes' else (r['ing'] if mode=='uses' else r['name'])
        if re.search(p,tgt):
            print(f"## {r['name']}  [{r['file']}:{r['line']}] t={r['t']} cat={r['cat']}\n   IN : {r['ing']}\n   OUT: {r['res']}")
            break
