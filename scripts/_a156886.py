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
print("terms:", len(v), "first:", v[:8])

# closed form guess: a(n) = [y^(3n)] (1+y)^(3n) (2+y)^n
def coeff(poly1, e1, poly2, e2, target):
    # expand (1+y)^e1 (2+y)^e2 numerically via binomial sums
    s = 0
    for j in range(0, min(e1, target) + 1):
        k = target - j
        if 0 <= k <= e2:
            s += comb(e1, j) * comb(e2, k) * (2 ** (e2 - k))
    return s

ok = all(coeff(1, 3*n, 2, n, 3*n) == v[n] for n in range(0, min(len(v), 60)))
print("closed form matches first 60 terms:", ok)
print("n=1:", coeff(1,3,2,1,3), "n=2:", coeff(1,6,2,2,6), "n=3:", coeff(1,9,2,3,9))
print("actual:", v[1], v[2], v[3])
