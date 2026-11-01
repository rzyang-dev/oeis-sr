import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
rows = json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))
atlas = {r["aid"]: r for r in rows}
per = json.load(open(ROOT/"reports"/"periodicity930.json", encoding="utf-8"))
nonper = {r["aid"] for r in per if r["period"] is None}
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
def guess(f, N, dxmax, dymax):
    ps = [1]
    for j in range(1, dymax+1): ps.append(mul(ps[-1], f, N))
    for dy in range(1, dymax+1):
        for dx in range(0, dxmax+1):
            cols = []; names = []
            for j in range(0, dy+1):
                for i in range(0, dx+1):
                    if i == 0 and j == 0: continue
                    v = (ps[j] << i) & ((1 << N) - 1)
                    if v: cols.append(v); names.append((i, j))
            cols.append(1); names.append((0, 0))
            basis = {}; dep = None
            for idx, v in enumerate(cols):
                w = v; expr = 1 << idx
                while w:
                    p = w.bit_length() - 1
                    if p in basis:
                        w ^= basis[p][0]; expr ^= basis[p][1]
                    else:
                        basis[p] = (w, expr); break
                if w == 0:
                    dep = expr; break
            if dep is not None:
                rel = [names[k] for k in range(len(names)) if dep >> k & 1]
                return max(j for (_, j) in rel), sorted(rel)
    return None
# find a degree-1 non-periodic example
found = None
for rec in rows:
    if rec["aid"] in nonper and rec["states"] <= 6:
        r = guess(terms_int(rec, 400), 400, 10, 14)
        if r and r[0] == 1:
            found = (rec["aid"], r[1]); break
print("degree-1 non-periodic example:", found)
if found:
    aid, rel = found
    f = terms_int(atlas[aid], 3000)
    ok_at = None
    for N2 in (400, 800, 1600, 3000):
        g = f & ((1 << N2) - 1)
        val = 0
        ps = {}
        for (i, j) in rel:
            v = (1 if j == 0 else mul((lambda: (lambda base: None)())(), 1, 1)) if False else None
        # recompute relation value at N2
        val = 0
        for (i, j) in rel:
            if j == 0:
                term = 1 << i if i > 0 else 1
            else:
                p = g
                for _ in range(j-1): p = mul(p, g, N2)
                term = (p << i) & ((1 << N2) - 1)
            if i == 0 and j == 0: term = 1
            val ^= term
        val &= (1 << N2) - 1
        print(f"  N={N2}: relation holds? {val == 0}")
