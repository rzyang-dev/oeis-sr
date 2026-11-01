import sys
from math import comb
sys.stdout.reconfigure(encoding="utf-8")
B = 1400
W = 2*B+1
def step(s):
    n = len(s); new = [0]*n
    for i in range(n):
        l = s[i-1] if i-1 >= 0 else 0
        c = s[i]
        r = s[i+1] if i+1 < n else 0
        new[i] = 1 if (l == c == r) else 0
    return new
X = []
s = [0]*W; s[B] = 1
for t in range(420):
    X.append(s[:]); s = step(s)
def x(t,j):
    if abs(j) > t: return 1 if t >= 1 else 0
    return X[t][B+j]
def C(n,k):
    if k < 0 or k > n: return 0
    return comb(n,k)
bad = 0
for t in range(1, 400):
    for j in range(-t, t+1):
        pred = 1 - (C(2*t+1, t+1+abs(j)) % 2)
        if pred != x(t,j):
            bad += 1
            if bad <= 3: print("F2 MISMATCH", t, j, pred, x(t,j))
print("F2 mismatches (t<400, all j, window 1400):", bad)
