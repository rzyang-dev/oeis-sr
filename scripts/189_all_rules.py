import sys
sys.stdout.reconfigure(encoding="utf-8")
N = 300   # half-width
T = 120   # steps
def evolve(rule):
    W = 2*N+1
    s = [0]*W; s[N] = 1
    rows = []
    for t in range(T):
        rows.append(s[:])
        ns = [0]*W
        for i in range(W):
            l = s[i-1] if i-1 >= 0 else 0
            c = s[i]
            r = s[i+1] if i+1 < W else 0
            ns[i] = (rule >> (4*l+2*c+r)) & 1
        s = ns
    return rows
def val(rows, t, j):
    # reliable only for |j| + t <= N
    if abs(j) + t > N: return None
    return rows[t][N+j]
hits = []
for rule in range(256):
    rows = evolve(rule)
    ok = True; checked = 0
    for t in range(1, T//2):
        for j in range(-t-2, t+3):
            a = val(rows, 2*t+1, j)
            b = val(rows, t, abs(j)//2)
            if a is None or b is None: continue
            checked += 1
            if a != b: ok = False; break
        if not ok: break
    if ok and checked > 200:
        hits.append((rule, checked))
print("rules satisfying V_{2t+1} = S(V_t):", len(hits))
print([r for r,_ in hits])
