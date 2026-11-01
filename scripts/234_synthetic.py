import sys, json, random
sys.stdout.reconfigure(encoding="utf-8")
from collections import Counter
random.seed(42)
def terms_int(tr, ov, N):
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
                return max(j for (i, j) in [names[k] for k in range(len(names)) if dep >> k & 1])
    return None
def is_periodic(f, N=400):
    bits = [(f >> k) & 1 for k in range(N)]
    for p in range(1, 200):
        if all(bits[i] == bits[i+p] for i in range(N-p)): return True
    return False
N = 400
dist = Counter(); tried = 0; skipped = 0
for trial in range(4000):
    n = random.randint(2, 6)
    tr = [[random.randrange(n) for _ in range(2)] for _ in range(n)]
    ov = [random.randint(0, 1) for _ in range(n)]
    # skip if not minimal-ish: start state 0 reachable
    seen = {0}; stack = [0]
    while stack:
        s = stack.pop()
        for b in (0,1):
            t = tr[s][b]
            if t not in seen: seen.add(t); stack.append(t)
    if len(seen) < n: skipped += 1; continue
    f = terms_int(tr, ov, N)
    if f in (0, (1 << N) - 1): skipped += 1; continue
    if is_periodic(f): dist[1] += 1; continue
    tried += 1
    d = guess(f, N, 10, 16)
    if d is None: dist["fail"] += 1
    else: dist[d] += 1
print("non-periodic synthetic tested:", tried)
print("degree distribution:", sorted(dist.items(), key=lambda kv: str(kv[0])))
