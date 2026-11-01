import sys
sys.stdout.reconfigure(encoding="utf-8")
N = 400
def run(rulefn, T=120):
    s = [0]*(2*N+1); s[N] = 1
    mid = []
    for t in range(T):
        mid.append(s[N])
        ns = [0]*(2*N+1)
        for i in range(N, 2*N+1):
            l2 = s[i-2] if i-2 >= 0 else 0
            l1 = s[i-1] if i-1 >= 0 else 0
            c = s[i]
            r1 = s[i+1] if i+1 <= 2*N else 0
            r2 = s[i+2] if i+2 <= 2*N else 0
            ns[i] = rulefn(l2,l1,c,r1,r2)
        # mirror for negative side
        for i in range(0, N):
            l2 = s[i-2] if i-2 >= 0 else 0
            l1 = s[i-1] if i-1 >= 0 else 0
            c = s[i]
            r1 = s[i+1]
            r2 = s[i+2]
            ns[i] = rulefn(l2,l1,c,r1,r2)
        s = ns
    return mid
def allsame(l2,l1,c,r1,r2):
    return 1 if (l2==l1==c==r1==r2) else 0
def allsame_c(l2,l1,c,r1,r2):
    return 1 - (1 if (l2==l1==c==r1==r2) else 0)
def threshold2(l2,l1,c,r1,r2):
    return 1 if sum([l2,l1,c,r1,r2]) >= 2 else 0
for name, f in [("all-5-equal", allsame), ("complement", allsame_c), ("sum>=2", threshold2)]:
    m = run(f, 100)
    zeros = [t for t in range(1, 100) if m[t] == 0]
    print(f"{name}: first 24 = {m[:24]}")
    print(f"   zeros at t = {zeros[:15]}")
