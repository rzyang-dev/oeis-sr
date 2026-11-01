
import numpy as np, sys
sys.stdout.reconfigure(encoding="utf-8")
N, T = 1400, 620
def simulate(N, T):
    s = np.ones(2*N+1, dtype=np.uint8); s[N-1:N+2] = 0
    rows = np.empty((T+1, 2*N+1), dtype=np.uint8); rows[1] = s
    r0 = np.zeros(2*N+1, dtype=np.uint8); r0[N] = 1; rows[0] = r0
    for t in range(1, T):
        a = s[:-2]; b = s[1:-1]; c = s[2:]
        s[1:-1] = ((a == b) & (b == c)).astype(np.uint8)
        rows[t+1] = s
    return rows
rows = simulate(N, T)
# V(t,j) = rows[t][j+N]  (1 = state 1, 0 = state 0)
V = lambda t,j: int(rows[t, j+N]) if abs(j) <= N - t else 1
# note: for |j| > t, value is 1 anyway; use raw rows for safety where |j| <= N-t
def get(t,j):
    return int(rows[t, j+N])

TMAX = 300
fails = {}
def check(name, t, cond, j, extra=""):
    if not cond:
        fails.setdefault(name, []).append((t,j,extra))

for t in range(1, TMAX+1):
    # (i) V_{2t+1}(2j) == V_t(j)
    for j in range(-t-1, t+2):
        check("i", t, get(2*t+1, 2*j) == get(t,j), j)
    # (ii) V_{2t}(2j+1) == 0 iff V_{t-1}(j) != V_{t-1}(j+1)
    for j in range(-t-2, t+3):
        w = (get(t-1,j) != get(t-1,j+1))
        check("ii", t, (get(2*t, 2*j+1) == 0) == w, j, f"wall={w} val={get(2*t,2*j+1)}")
    # (iii) V_{2t}(2j) == 0 iff V_t(j)==0 and j = t mod 2
    for j in range(-t-1, t+2):
        pred = (get(t,j) == 0) and ((j - t) % 2 == 0)
        check("iii", t, (get(2*t, 2*j) == 0) == pred, j, f"pred={pred} val={get(2*t,2*j)}")
for name in ("i","ii","iii"):
    L = fails.get(name, [])
    print(name, "failures:", len(L), L[:6])
