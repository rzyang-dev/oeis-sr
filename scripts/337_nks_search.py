
import re, glob, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
def clean(t):
    t = t.replace('\x00',' ')
    # keep printable ascii + latin1 letters
    out=[]
    for ch in t:
        o=ord(ch)
        if 32 <= o < 127 or 0xC0 <= o <= 0xFF or ch in '\n':
            out.append(ch)
    s=''.join(out)
    s=re.sub(r'[ \t]{2,}',' ',s)
    s=re.sub(r'\n{2,}','\n',s)
    return s
files=sorted(glob.glob('nks/txt/*.txt'))
allt={}
for p in files:
    t=clean(open(p,encoding='utf-8').read())
    open(p,'w',encoding='utf-8').write(t)
    allt[os.path.basename(p)]=t
kws=["129","neighbour","neighbor","unanim","submask","closed form","radial","Stern"]
print("=== counts per keyword (over all files)")
for k in kws:
    tot=sum(t.lower().count(k.lower()) for t in allt.values())
    where=[n for n,t in allt.items() if k.lower() in t.lower()]
    print("%-12s total=%5d  files=%s" % (k, tot, ",".join(w.replace('nks-','').replace('.txt','') for w in where[:8])))
print()
print("=== contexts for 129 (first 12)")
n=0
for name,t in allt.items():
    for m in re.finditer(r'129', t):
        a=max(0,m.start()-90); b=min(len(t), m.end()+90)
        print("[%s] ...%s..." % (name, t[a:b].replace('\n',' ')))
        n+=1
        if n>=12: break
    if n>=12: break
print()
print("=== contexts for unanim / neighbour (first 8)")
n=0
for k in ("unanim","neighbour"):
    for name,t in allt.items():
        for m in re.finditer(k, t, re.I):
            a=max(0,m.start()-90); b=min(len(t), m.end()+120)
            print("[%s|%s] ...%s..." % (name,k, t[a:b].replace('\n',' ')))
            n+=1
            if n>=8: break
        if n>=8: break
    if n>=8: break
