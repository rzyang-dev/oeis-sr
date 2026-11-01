import sys
sys.stdout.reconfigure(encoding="utf-8")
B = 1200
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
for t in range(400):
    X.append(s[:])
    s = step(s)
def x(t,j):
    if abs(j) > t: return 1 if t >= 1 else 0
    return X[t][B+j]
def r_of(t):
    if t == 0: return 0
    return t - (1 << (t.bit_length()-1))
def is_sub(s, r): return (s & r) == s
# check closed form for t <= 200
bad = 0
for t in range(1, 201):
    rt = r_of(t)
    for j in range(-t, t+1):
        d = t - abs(j)
        pred = 1 if (not is_sub(d//2, rt)) else 0
        if pred != x(t,j):
            bad += 1
            if bad < 5: print("MISMATCH", t, j, pred, x(t,j))
print("closed form mismatches (t<=200):", bad)
# check renormalisation identities
def e(t,j):
    return 1 if x(t,j) != x(t,j+1) else 0
bad1 = bad2 = bad3 = 0
for m in range(1, 150):
    for i in range(-m, m+1):
        if e(2*m, 2*i) != (1 - x(m,i)): bad1 += 1
        if e(2*m+1, 2*i+1) != e(m,i): bad2 += 1
        if e(2*m+1, 2*i) != 0: bad3 += 1
print("even identity mismatches:", bad1)
print("odd identity mismatches:", bad2)
print("odd even-position mismatches:", bad3)
# check |E_t| = 2^popcount(t+1)
bad4 = 0
for t in range(0, 200):
    cnt = sum(e(t,j) for j in range(-t-2, t+3))
    if cnt != 2**bin(t+1).count('1'): bad4 += 1
print("|E_t| mismatches:", bad4)
