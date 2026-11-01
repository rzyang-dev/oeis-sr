import sys
sys.stdout.reconfigure(encoding="utf-8")
N = 120
def diagram(r, T):
    s = [0]*(2*N+1); s[N] = 1
    rows = []
    for t in range(T):
        rows.append(s[:])
        ns = [0]*(2*N+1)
        for i in range(2*N+1):
            v0 = s[i]; ok = True
            for d in range(-r, r+1):
                k = i + d
                v = s[k] if 0 <= k <= 2*N else 0
                if v != v0: ok = False; break
            ns[i] = 1 if ok else 0
        s = ns
    return rows
def r_of(t):
    return 0 if t == 0 else t - (1 << (t.bit_length()-1))
def sub(m, s): return (m & s) == m
for r in (1, 2, 3):
    rows = diagram(r, 40)
    bad = 0; tot = 0
    for t in range(1, 40):
        rt = r_of(t)
        for j in range(-t, t+1):
            v = rows[t][N+j]
            d = abs(j) / r
            if d > t:
                pred = 1
            else:
                pred = 1 if not sub(int((t - d) // 2), rt) else 0
            tot += 1
            if pred != v: bad += 1
    print(f"radius {r}: formula with norm |j|/{r}: {bad} mismatches / {tot}")
