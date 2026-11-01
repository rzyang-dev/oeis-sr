import sys
sys.stdout.reconfigure(encoding="utf-8")
lo, hi = -3000, 3000
def step(E):
    newE = set()
    for j in range(lo, hi):
        b = (j in E); a = ((j-1) in E); c = ((j+1) in E)
        if (not b) and (a != c): newE.add(j)
    return newE
E = {-1, 0}
T = []
for t in range(300):
    T.append(set(E)); E = step(E)
def pairs(k, m):
    t = (1 << k) + m
    if t >= len(T): return None
    A = sorted(T[t]); B = sorted(T[m])
    # pair up: each p in B gives two points in A, split by sign
    out = []
    leftA = [x for x in A if x < 0]; rightA = [x for x in A if x >= 0]
    leftB = [x for x in B if x < 0]; rightB = [x for x in B if x >= 0]
    # map left points in order: each gets two consecutive from leftA
    for i, p in enumerate(leftB):
        if 2*i+1 < len(leftA):
            out.append((p, leftA[2*i], leftA[2*i+1]))
    for i, p in enumerate(rightB):
        if 2*i+1 < len(rightA):
            out.append((p, rightA[2*i], rightA[2*i+1]))
    return out
for k in (3,4,5):
    print(f"--- k={k} ---")
    for m in range(0, min(2**k, 12)):
        ps = pairs(k, m)
        if ps is None: continue
        desc = "; ".join(f"{p}->({a},{b}) off=({2*p-a},{2*p-b})" for p,a,b in ps)
        print(f"m={m}: {desc}")
