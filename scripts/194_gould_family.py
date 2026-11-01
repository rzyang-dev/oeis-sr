import sys
sys.stdout.reconfigure(encoding="utf-8")
N = 200; T = 90
def rows_of(rule):
    W = 2*N+1
    s = [0]*W; s[N] = 1
    rows = []
    for t in range(T):
        rows.append(s[:])
        ns = [0]*W
        for i in range(W):
            l = s[i-1] if i-1 >= 0 else 0
            c = s[i]
            r = s[i+1] if i+1 < W else 0
            ns[i] = (rule >> (4*l+2*c+r)) & 1
        s = ns
    return rows
def r_of(t):
    return 0 if t == 0 else t - (1 << (t.bit_length()-1))
rules = list(range(256))
interesting = []
for rule in rules:
    rows = rows_of(rule)
    table = {}
    ok = True
    for t in range(1, T):
        for j in range(-t, t+1):
            if abs(j) + t > N: continue
            d = t - abs(j)
            key = (d//2, r_of(t))
            v = rows[t][N+j]
            if key in table:
                if table[key] != v: ok = False; break
            else:
                table[key] = v
        if not ok: break
    if ok and len(table) > 30:
        interesting.append(rule)
print("rules whose diagram depends only on (floor(d/2), r(t)):", interesting)
