import sys
sys.stdout.reconfigure(encoding="utf-8")
N = 400
def run(offsets, T):
    s = [0]*(2*N+1); s[N] = 1
    mid = []
    for t in range(T):
        mid.append(s[N])
        ns = [0]*(2*N+1)
        for i in range(2*N+1):
            vals = [s[i+d] if 0 <= i+d <= 2*N else 0 for d in offsets]
            ns[i] = 1 if all(v == vals[0] for v in vals) else 0
        s = ns
    return mid
for name, off in (("{−2,0,2}", [-2,0,2]), ("{−3,0,3}", [-3,0,3]), ("{−1,0,1}", [-1,0,1])):
    m = run(off, 130)
    zeros = [t for t in range(1, 130) if m[t] == 0]
    expected = [2**k-1 for k in range(1, 8)]
    print(f"{name}: zeros={zeros}")
    print(f"    matches 2^k-1: {zeros == expected}")
