import sys
sys.stdout.reconfigure(encoding="utf-8")
B = 60
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
for t in range(9):
    s = state_at(t)
    d = [s[B+j] ^ s[B+j+1] for j in range(-8, 8)]
    mid = s[B]
    print(f"t={t} mid={mid} d[-8..7]={d}")
