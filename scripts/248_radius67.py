import sys
sys.stdout.reconfigure(encoding="utf-8")
def run(r, N, T):
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
for r in (6, 7):
    N = r*160 + 50
    m = run(r, N, 140)
    zeros = [t for t in range(1, 140) if m[t] == 0]
    print(f"radius {r} (N={N}): zeros = {zeros[:10]}")
    print(f"   first 16 = {m[:16]}")
