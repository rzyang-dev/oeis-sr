import sys
sys.stdout.reconfigure(encoding="utf-8")
N = 700
def run_all_equal(r, T):
    s = [0]*(2*N+1); s[N] = 1
    mid = []
    for t in range(T):
        mid.append(s[N])
        ns = [0]*(2*N+1)
        for i in range(2*N+1):
            v0 = s[i] if 0 <= i <= 2*N else 0
            ok = True
            for d in range(-r, r+1):
                k = i + d
                v = s[k] if 0 <= k <= 2*N else 0
                if v != v0: ok = False; break
            ns[i] = 1 if ok else 0
        s = ns
    return mid
for r in (1, 5):
    m = run_all_equal(r, 270)
    zeros = [t for t in range(1, 270) if m[t] == 0]
    print(f"radius {r}: zeros = {zeros}")
