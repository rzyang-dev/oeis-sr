import sys
sys.stdout.reconfigure(encoding="utf-8")
W = 140
T = 45
g = [[0]*(2*W+1) for _ in range(2*W+1)]
g[W][W] = 1
diag = []
for t in range(T):
    diag.append([row[:] for row in g])
    ng = [[0]*(2*W+1) for _ in range(2*W+1)]
    for i in range(2*W+1):
        for j in range(2*W+1):
            v0 = g[i][j]; ok = True
            for di in (-1,0,1):
                for dj in (-1,0,1):
                    a = i+di; b = j+dj
                    v = g[a][b] if 0 <= a <= 2*W and 0 <= b <= 2*W else 0
                    if v != v0: ok = False; break
                if not ok: break
            ng[i][j] = 1 if ok else 0
    g = ng
def r_of(t):
    return 0 if t == 0 else t - (1 << (t.bit_length()-1))
def sub(m, s): return (m & s) == m
bad = 0; tot = 0
for t in range(1, T):
    rt = r_of(t)
    for i in range(-t, t+1):
        for j in range(-t, t+1):
            v = diag[t][W+i][W+j]
            d = max(abs(i), abs(j))
            pred = 1 if (d > t or not sub((t-d)//2, rt)) else 0
            tot += 1
            if pred != v: bad += 1
print(f"2D Moore vs same closed form with Chebyshev norm: {bad} mismatches / {tot}")
