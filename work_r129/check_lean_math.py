
def r(t):
    if t == 0: return 0
    k = t.bit_length() - 1
    return t - (1 << k)

def sub(m, s):
    return (m & s) == m

def F(t, j):
    if t == 0:
        return 1 if j == 0 else 0
    if abs(j) <= t and sub((t - abs(j))//2, r(t)):
        return 0
    return 1

# (1) local identity
bad = []
for t in range(1, 250):
    for j in range(-260, 261):
        lhs = F(t+1, j) == 1
        rhs = (F(t, j-1) == F(t, j) == F(t, j+1))
        if lhs != rhs:
            bad.append((t, j, lhs, rhs))
print("local identity failures:", len(bad), bad[:10])

# (2) star identity: sub(e, s+1) <=> (sub(e,s) != sub(e-1,s)) for e>=1
bad2 = []
for e in range(1, 400):
    for s in range(0, 400):
        lhs = sub(e, s+1)
        rhs = (sub(e, s) != sub(e-1, s))
        if lhs != rhs:
            bad2.append((e, s))
print("star failures:", len(bad2), bad2[:10])
