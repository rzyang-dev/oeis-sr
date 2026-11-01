
import numpy as np, sys, zlib, struct
sys.stdout.reconfigure(encoding="utf-8")

N, T = 1400, 620
def simulate(N, T):
    s = np.ones(2*N+1, dtype=np.uint8)
    s[N-1:N+2] = 0            # t=1: zeros at -1,0,1
    rows = np.empty((T+1, 2*N+1), dtype=np.uint8)
    rows[1] = s
    # t=0 is special: single 1 at 0, 0 elsewhere
    r0 = np.zeros(2*N+1, dtype=np.uint8); r0[N] = 1; rows[0] = r0
    for t in range(1, T):
        a = s[:-2]; b = s[1:-1]; c = s[2:]
        s[1:-1] = ((a == b) & (b == c)).astype(np.uint8)
        rows[t+1] = s
    return rows
rows = simulate(N, T)
def ok(t): return N - t          # trusted |j| <= ok(t)
# sanity: check middle column
mid = rows[:T+1, N]
print("middle col 0-40:", "".join(map(str, mid[:41])))
print("middle zeros t<=200:", [t for t in range(201) if mid[t]==0])
# consistency with bigger window
rows2 = simulate(N+200, T)
print("window agreement:", all(np.array_equal(rows[t, :], rows2[t, 200:200+2*N+1]) for t in range(T+1)))

def zeros_intervals(t):
    j0, j1 = -ok(t), ok(t)
    seg = rows[t, j0+N:j1+N+1]
    idx = np.flatnonzero(seg == 0)
    if len(idx)==0: return []
    out=[]; a=idx[0]; b=a
    for x in idx[1:]:
        if x==b+1: b=x
        else: out.append((a+j0,b+j0)); a=x; b=x
    out.append((a+j0,b+j0))
    return out
print()
for t in list(range(0,49)):
    z = zeros_intervals(t)
    txt = " ".join(f"[{a},{b}]" if a!=b else f"{{{a}}}" for a,b in z)
    print(f"D_{t}: {txt}")
