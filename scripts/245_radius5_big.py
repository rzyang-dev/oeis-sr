import sys
sys.stdout.reconfigure(encoding="utf-8")
N = 2200
def run_all_equal(r, T):
    s = [0]*(2*N+1); s[N] = 1
    mid = []
    for t in range(T):
        mid.append(s[N])
        ns = [0]*(2*N+1)
        lo = max(0, N - r*t - r - 5); hi = min(2*N, N + r*t + r + 5)
        for i in range(lo, hi+1):
            v0 = s[i]
            ok = True
            for d in range(-r, r+1):
                k = i + d
                v = s[k] if 0 <= k <= 2*N else 0
                if v != v0: ok = False; break
            ns[i] = 1 if ok else 0
        s = ns
    return mid
m = run_all_equal(5, 270)
zeros = [t for t in range(1, 270) if m[t] == 0]
print("radius 5 (N=2200): zeros =", zeros[:30])
print("count:", len(zeros), " expected 2^k-1 count:", len([t for t in range(1,270) if t+1 and (t+1)&t == 0]))
