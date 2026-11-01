import sys
from pathlib import Path
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
f = Path(r"C:\Users\ginger\oeisdata\files\A338\b338464.txt")
v = {}
for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
    line=line.strip()
    if not line or line.startswith("#"): continue
    q=line.split()
    if len(q)>=2:
        try: v[int(q[0])]=int(q[1])
        except ValueError: pass
print("terms:", len(v), "max n:", max(v))
for p in (5, 7, 11):
    cnt = Counter(n % p for n, x in v.items() if x % p == 0)
    tot = Counter(n % p for n in v)
    print(f"p={p}: zero counts by n mod p:", {r: (cnt[r], tot[r]) for r in range(p)})
# density of zeros
z = sum(1 for x in v.values() if x % 5 == 0)
print("zero density mod 5:", z/len(v))
# mod 25 depth on n=1 mod 5
def vp(x,p):
    if x==0: return -1
    k=0
    while x%p==0: x//=p; k+=1
    return k
for res, mod in ((1,5),(6,25),(31,125)):
    ns=[n for n in v if n%mod==res and v[n]!=0]
    if ns:
        vals=[vp(v[n],5) for n in ns]
        print(f"n≡{res} mod {mod}: {len(ns)} nonzero terms, min v5={min(vals)}, histogram={Counter(vals)}")
