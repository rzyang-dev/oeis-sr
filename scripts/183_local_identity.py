import sys
sys.stdout.reconfigure(encoding="utf-8")
def r_of(t):
    if t <= 0: return 0
    return t - (1 << (t.bit_length()-1))
def is_sub(s, r): return (s & r) == s
def f(t, j):
    if t == 0: return 1 if j == 0 else 0
    if abs(j) > t: return 1
    return 0 if is_sub((t - abs(j)) // 2, r_of(t)) else 1
bad = 0
for t in range(1, 400):
    for j in range(-t-2, t+3):
        lhs = f(t+1, j)
        rhs = 1 if (f(t,j-1) == f(t,j) == f(t,j+1)) else 0
        if lhs != rhs:
            bad += 1
            if bad <= 5: print("LOCAL MISMATCH", t, j, lhs, rhs, [f(t,j-1), f(t,j), f(t,j+1)])
print("local-identity mismatches (t<400):", bad)
# also verify f matches the CA simulation
B = 500
W = 2*B+1
def step(s):
    n = len(s); new = [0]*n
    for i in range(n):
        l = s[i-1] if i-1 >= 0 else 0
        c = s[i]
        r = s[i+1] if i+1 < n else 0
        new[i] = 1 if (l == c == r) else 0
    return new
s = [0]*W; s[B] = 1
bad2 = 0
for t in range(0, 250):
    for j in range(-t, t+1):
        if s[B+j] != f(t,j): bad2 += 1
    s = step(s)
print("formula vs simulation mismatches (t<250):", bad2)
