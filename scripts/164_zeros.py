import sys
sys.stdout.reconfigure(encoding="utf-8")
B = 80
state = [0]*(2*B+1)
state[B] = 1
def step(s):
    n = len(s)
    new = [0]*n
    for i in range(n):
        l = s[i-1] if i-1 >= 0 else 0
        c = s[i]
        r = s[i+1] if i+1 < n else 0
        new[i] = 1 if (l == c == r) else 0
    return new
for t in range(17):
    zeros = [i-B for i in range(2*B+1) if state[i] == 0]
    # summarize as intervals
    iv = []
    for z in zeros:
        if iv and z == iv[-1][1] + 1:
            iv[-1][1] = z
        else:
            iv.append([z, z])
    mid = state[B]
    print(f"t={t:2d} mid={mid} zero-intervals={iv[:12]}")
    state = step(state)
