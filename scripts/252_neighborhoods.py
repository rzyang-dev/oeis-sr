import sys
sys.stdout.reconfigure(encoding="utf-8")
N = 300
def run(offsets, T=80):
    s = [0]*(2*N+1); s[N] = 1
    mid = []
    for t in range(T):
        mid.append(s[N])
        ns = [0]*(2*N+1)
        for i in range(2*N+1):
            vals = []
            for d in offsets:
                k = i + d
                vals.append(s[k] if 0 <= k <= 2*N else 0)
            ns[i] = 1 if all(v == vals[0] for v in vals) else 0
        s = ns
    return mid
tests = {
 "{-1,0,1} (r=1)": [-1,0,1],
 "{0,1}": [0,1],
 "{-1,0}": [-1,0],
 "{0}": [0],
 "{-2,0,2}": [-2,0,2],
 "{-2,-1,0,1,2} (r=2)": [-2,-1,0,1,2],
 "{-3,0,3}": [-3,0,3],
 "{-1,1}": [-1,1],
}
for name, off in tests.items():
    m = run(off, 80)
    zeros = [t for t in range(1, 60) if m[t] == 0]
    print(f"{name:24s} zeros={zeros[:10]}")
