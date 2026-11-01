import sys, json, sqlite3
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
N = 2200
T = 420
def run_all_equal(r, T):
    s = [0]*(2*N+1); s[N] = 1
    mid = []
    for t in range(T):
        mid.append(s[N])
        ns = [0]*(2*N+1)
        for i in range(2*N+1):
            v0 = s[i]
            ok = True
            for d in range(-r, r+1):
                k = i + d
                v = s[k] if 0 <= k <= 2*N else 0
                if v != v0: ok = False; break
            ns[i] = 1 if ok else 0
        s = ns
    return mid
m = run_all_equal(5, T)
print("first 32:", m[:32])
# OEIS prefix search
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
key = tuple(m[:20])
hits = []
for aid, tms in con.execute("select aid, terms from seq where terms is not null"):
    parts = tms.split(",")[:20]
    try: vals = tuple(int(x) for x in parts)
    except ValueError: continue
    if vals == key: hits.append(aid)
print("OEIS matches:", hits[:10])
# algebraic degree
def mul(a, b, N):
    r = 0; x = 0; bb = b
    while bb:
        if bb & 1: r ^= a << x
        bb >>= 1; x += 1
    return r & ((1 << N) - 1)
def guess(f, N, dxmax=10, dymax=16):
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
                return dy
    return None
f = 0
for t in range(min(T, 400)):
    if m[t]: f |= 1 << t
print("algebraic degree (dy<=16, N=400):", guess(f, 400))
