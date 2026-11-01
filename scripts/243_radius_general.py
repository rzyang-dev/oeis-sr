import sys
sys.stdout.reconfigure(encoding="utf-8")
N = 600
def run_all_equal(r, T=130):
    s = [0]*(2*N+1); s[N] = 1
    mid = []
    for t in range(T):
        mid.append(s[N])
        ns = [0]*(2*N+1)
        for i in range(2*N+1):
            vals = []
            for d in range(-r, r+1):
                k = i + d
                vals.append(s[k] if 0 <= k <= 2*N else 0)
            ns[i] = 1 if all(v == vals[0] for v in vals) else 0
        s = ns
    return mid
for r in (1, 2, 3, 4):
    m = run_all_equal(r, 130)
    zeros = [t for t in range(1, 130) if m[t] == 0]
    print(f"radius {r}: zeros = {zeros[:12]}")
    print(f"          first 16 = {m[:16]}")
