
import re, glob, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
files=sorted(glob.glob('nks/txt/*.txt'))
def show(pat, label, width=240, maxn=8, flags=re.I):
    print("\n=== %s" % label)
    n=0
    for p in files:
        t=open(p,encoding='utf-8').read()
        for m in re.finditer(pat, t, flags):
            a=max(0,m.start()-width//2); b=min(len(t), m.end()+width//2)
            print("[%s] ...%s..." % (os.path.basename(p).replace('.txt',''), t[a:b].replace('\n',' ')))
            n+=1
            if n>=maxn: return
show(r'Stern', 'Stern', maxn=6)
show(r'center column', 'center column', maxn=10)
show(r'nested', 'nested (ch3 only)', maxn=4)
