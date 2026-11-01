import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
atlas = {r["aid"]: r for r in json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))}
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
    r = 0
    m = 1
    bb = b
    while bb and m < N:
        if bb & 1:
            r ^= a << (m-1) if False else 0
        bb >>= 1; m += 1
    # simple schoolbook on bits
    r = 0
    x = 0
    bb = b
    while bb:
        if bb & 1: r ^= a << x
        bb >>= 1; x += 1
    return r & ((1 << N) - 1)
def powers(f, dy, N):
    ps = [1]
    for j in range(1, dy+1):
        ps.append(mul(ps[-1], f, N))
    return ps
def guess(f, N, dxmax=10, dymax=12):
    # columns: x^i * f^j for i<=dxmax, j<=dymax (skip constant column i=0,j=0)
    for dy in range(0, dymax+1):
        ps = powers(f, dy, N)
        for dx in range(0, dxmax+1):
            cols = []
            names = []
            for j in range(0, dy+1):
                for i in range(0, dx+1):
                    if i == 0 and j == 0: continue
                    v = (ps[j] << i) & ((1 << N) - 1)
                    if v:
                        cols.append(v); names.append((i, j))
            if len(cols) < 3: continue
            # gaussian elimination over GF(2)
            basis = {}
            for idx, v in enumerate(cols):
                w = v; expr = 1 << idx
                while w:
                    p = w.bit_length() - 1
                    if p in basis:
                        w ^= basis[p][0]; expr ^= basis[p][1]
                    else:
                        basis[p] = (w, expr); break
            if not basis: continue
            # check if the 'constant' column (i=0,j=0) - we didn't include it; a relation among cols
            # means sum c_k col_k = 0 => polynomial relation with no constant term.
            # Try: find relation among cols plus the constant 1 column.
            cols2 = cols + [1 << 0]  # f^0 * x^0 = 1
            basis2 = {}
            dep = None
            for idx, v in enumerate(cols2):
                w = v; expr = 1 << idx
                while w:
                    p = w.bit_length() - 1
                    if p in basis2:
                        w ^= basis2[p][0]; expr ^= basis2[p][1]
                    else:
                        basis2[p] = (w, expr); break
                if w == 0:
                    dep = expr; break
            if dep is not None:
                names2 = names + [(0,0)]
                rel = [names2[k] for k in range(len(names2)) if dep >> k & 1]
                return (dy, dx, rel)
    return None
for aid in ("A010060", "A096268", "A035263", "A036987"):
    rec = atlas[aid]; N = 600
    f = terms_int(rec, N)
    res = guess(f, N)
    print(aid, "states", rec["states"], "->", res)
