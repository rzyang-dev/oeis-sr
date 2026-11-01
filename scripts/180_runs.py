import sys
sys.stdout.reconfigure(encoding="utf-8")
B = 300
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
for t in range(16):
    s = state_at(t)
    # runs over [-t-1, t+1]
    vals = [s[B+j] for j in range(-t-1, t+2)]
    runs = []
    cur = vals[0]; ln = 1
    for v in vals[1:]:
        if v == cur: ln += 1
        else: runs.append((cur, ln)); cur = v; ln = 1
    runs.append((cur, ln))
    print(f"t={t:2d}: {runs}")
