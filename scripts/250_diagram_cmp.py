import sys
sys.stdout.reconfigure(encoding="utf-8")
N = 200
def diagram(r, T):
    s = [0]*(2*N+1); s[N] = 1
    rows = []
    for t in range(T):
        rows.append(s[N-t-2:N+t+3])
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
    return rows
T = 60
d1 = diagram(1, T)
d2 = diagram(2, T)
d3 = diagram(3, T)
def cmp(a, b):
    same = 0; tot = 0
    for t in range(1, T):
        w = t+2
        for k in range(len(a[t])):
            tot += 1
            if a[t][k] == b[t][k]: same += 1
    return same, tot
print("r1 vs r2: ", cmp(d1, d2))
print("r1 vs r3: ", cmp(d1, d3))
# show a few rows
for t in (2, 5, 10):
    print("t=", t, "r1:", d1[t][:2*t+5])
    print("       r2:", d2[t][:2*t+5])
