import sys
sys.stdout.reconfigure(encoding="utf-8")
B = 200
def state_at(t):
    s = [0]*(2*B+1); s[B] = 1
    for _ in range(t):
        n = len(s); new = [0]*n
        for i in range(n):
            l = s[i-1] if i-1 >= 0 else 0
            c = s[i]
            r = s[i+1] if i+1 < n else 0
            new[i] = 1 if (l == c == r) else 0
        s = new
    return s
cache = {}
def get(t):
    if t not in cache: cache[t] = state_at(t)
    return cache[t]
def win(t, m):
    s = get(t)
    return [s[B+j] for j in range(-m, m+1)]
print("compare state(2^k+m-1) vs state(m-1) on |j|<=m")
for k in (3, 4):
    for m in range(1, 9):
        a = win(2**k + m - 1, m)
        b = win(m - 1, m)
        same = a == b
        print(f"k={k} m={m}: match={same}  A={a}  B={b}")
