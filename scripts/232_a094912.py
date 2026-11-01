import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
rows = json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))
atlas = {r["aid"]: r for r in rows}
def terms_int(rec, N):
    tr, ov = rec["trans"], rec["out"]
    v = 0
    for n in range(N):
        s = 0; m = n
        while m:
            s = tr[s][m & 1]; m >>= 1
        if ov[s]: v |= 1 << n
    return v
def mul(a, b, N):
    r = 0; x = 0; bb = b
    while bb:
        if bb & 1: r ^= a << x
        bb >>= 1; x += 1
    return r & ((1 << N) - 1)
rel = [(0,1),(0,2),(1,8),(3,2),(5,0),(9,8)]
N = 2000
rec = atlas["A094912"]
f = terms_int(rec, N)
val = 0
for (i, j) in rel:
    if j == 0:
        term = (1 << i) & ((1 << N) - 1) if i > 0 else 1
    else:
        p = f
        for _ in range(j-1): p = mul(p, f, N)
        term = (p << i) & ((1 << N) - 1)
    val ^= term
val &= (1 << N) - 1
print("A094912 equation holds at N=2000:", val == 0)
print("terms[0..20]:", [ (f >> k) & 1 for k in range(20)])
