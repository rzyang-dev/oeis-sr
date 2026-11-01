
import sys
sys.setrecursionlimit(10000)

def r(t):
    if t == 0: return 0
    if t == 1: return 0
    return 2*r(t//2) + t % 2

def sub(m, s):
    return (m & s) == m

def bit(p):
    return 1 if p else 0

def G(t, d):
    return 1 - bit(sub(d//2, r(t)))

def H(t, n):
    return G(t, t-n) if n <= t else 1

def F(t, j):
    return H(t, abs(j))

# row per the Lean definition
def row_step(prev):
    return {j: (1 if (prev.get(j-1,0) == prev.get(j,0) == prev.get(j+1,0)) else 0) for j in range(-200,201)}

rows = {}
cur = {j: (1 if j == 0 else 0) for j in range(-200, 201)}
rows[0] = cur
for t in range(1, 60):
    cur = row_step(cur)
    rows[t] = cur

bad = 0
for t in range(1, 60):
    for j in range(-70, 71):
        if rows[t].get(j, 0) != F(t, j):
            bad += 1
            if bad < 5: print("MISMATCH", t, j, rows[t].get(j,0), F(t,j))
print("row vs F mismatches (t<60):", bad)

# r equals t minus leading bit
def rref(t):
    if t == 0: return 0
    return t - (1 << (t.bit_length()-1))
print("r mismatches:", [t for t in range(0,3000) if r(t) != rref(t)][:5])

# middle column
badm = []
for t in range(1, 400):
    lhs = (rows[t][0] == 0) if t < 59 else None
    if t < 59:
        rhs = any(t == 2**k - 1 for k in range(1, 20))
        if lhs != rhs: badm.append(t)
print("middle column mismatches (t<59):", badm)

# closed form check (the literal statement)
badc = 0
for t in range(1, 59):
    for j in range(-70, 71):
        lhs = (rows[t].get(j,0) == 0)
        rhs = (abs(j) <= t and sub((t-abs(j))//2, r(t)))
        if lhs != rhs: badc += 1
print("closed form mismatches:", badc)
