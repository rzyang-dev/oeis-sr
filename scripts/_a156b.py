import sys
from pathlib import Path
from math import comb
sys.stdout.reconfigure(encoding="utf-8")
f = Path(r"C:\Users\ginger\oeisdata\files\A156\b156886.txt")
v = []
for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
    line=line.strip()
    if not line or line.startswith("#"): continue
    q=line.split()
    if len(q)>=2:
        try: v.append(int(q[1]))
        except ValueError: pass

def c(r):
    # [y^(3r)] (1+y)^(3r) (2+y)^r
    s = 0
    for j in range(0, 3*r+1):
        k = 3*r - j
        if 0 <= k <= r:
            s += comb(3*r, j) * comb(r, k) * 2**(r-k)
    return s
cs = [c(r) for r in range(5)]
print("c_r:", cs, "mod 5:", [x % 5 for x in cs])
bad = 0
for m in range(0, 120):
    for r in range(5):
        n = 5*m + r
        if n < len(v) and v[n] % 5 != (v[m] * cs[r]) % 5:
            bad += 1
            if bad < 5:
                print("mismatch", n, v[n] % 5, (v[m]*cs[r]) % 5)
print("mismatches:", bad)
print("a(5m+1) mod 5 all zero:", all(v[5*m+1] % 5 == 0 for m in range(0, 180) if 5*m+1 < len(v)))
