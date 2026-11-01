import sys
sys.stdout.reconfigure(encoding="utf-8")
W = 220
def run2d(T):
    g = [[0]*(2*W+1) for _ in range(2*W+1)]
    g[W][W] = 1
    mid = []
    for t in range(T):
        mid.append(g[W][W])
        ng = [[0]*(2*W+1) for _ in range(2*W+1)]
        for i in range(2*W+1):
            for j in range(2*W+1):
                v0 = g[i][j]
                ok = True
                for di in (-1,0,1):
                    for dj in (-1,0,1):
                        a = i+di; b = j+dj
                        v = g[a][b] if 0 <= a <= 2*W and 0 <= b <= 2*W else 0
                        if v != v0: ok = False; break
                    if not ok: break
                ng[i][j] = 1 if ok else 0
        g = ng
    return mid
m = run2d(60)
zeros = [t for t in range(1, 60) if m[t] == 0]
print("2D all-equal (Moore) center:", m[:20])
print("zeros:", zeros[:10])
