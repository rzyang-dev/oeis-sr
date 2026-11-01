"""Script 293 -- the rank law.

Claim: for a level-size function c of polynomial degree j, the zero-count
sequence Z_c has 2-kernel rank

    rank(Z_c) = (j + 1) + [ eps correction ] ,

where eps = [0 in shell t] appears exactly when the value at level 0 has to
be patched (c(0) replaced by the centre's own count).  The (j+1) part is the
span of the arm moments Phi_0, ..., Phi_j; the extra 1 is the rank-one
automatic sequence eps = [t = 2^i - 1].

We also check that the trees are NOT 2-regular: their rank keeps growing.
"""
from fractions import Fraction as F

def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def wt(n):
    return bin(n).count("1")

def bits(m):
    return [i for i in range(m.bit_length()) if (m >> i) & 1]

def shell(t):
    rt = r(t)
    return [d for d in range(t + 1) if ((t - d) // 2) & rt == (t - d) // 2]

def rank(matrix, ncol):
    rows = [row[:ncol] for row in matrix]
    m = len(rows)
    rk = 0
    for col in range(ncol):
        piv = None
        for i in range(rk, m):
            if rows[i][col] != 0:
                piv = i
                break
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        pv = F(rows[rk][col])
        for i in range(rk + 1, m):
            if rows[i][col] != 0:
                f = F(rows[i][col]) / pv
                for j in range(col, ncol):
                    rows[i][j] = F(rows[i][j]) - f * F(rows[rk][j])
        rk += 1
        if rk == m:
            break
    return rk

def krank(a, KMAX, M):
    needed = (1 << KMAX) * (M + 2) + 4
    vals = [a(t) for t in range(needed + 1)]
    out = []
    for K in range(3, KMAX + 1):
        elems = []
        for k in range(K + 1):
            for j in range(1 << k):
                elems.append([vals[(1 << k) * n + j] for n in range(1, M + 1)])
        out.append(rank(elems, M))
    return out

def zc(c):
    return lambda t: sum(c(d) for d in shell(t))

print("A. pure powers c(d) = d^j  (no eps correction, so expect rank = j+1)")
print("| j | rank(K=4..7) | j+1 |")
print("|---|---|---|")
for j in range(0, 6):
    out = krank(zc(lambda d, j=j: d ** j), 7, 40)
    print(f"| {j} | {out} | {j+1} |")

print()
print("B. powers with the level-0 patch  c(0)=1, c(d)=d^j (d>=1)  ->  expect j+2")
print("| j | rank(K=4..7) | j+2 |")
print("|---|---|---|")
for j in range(0, 6):
    out = krank(zc(lambda d, j=j: 1 if d == 0 else d ** j), 7, 40)
    print(f"| {j} | {out} | {j+2} |")

print()
print("C. the trees: not 2-regular (rank grows with the depth K)")
print("| tree | rank(K=4) | rank(K=5) | rank(K=6) | rank(K=7) | rank(K=8) |")
print("|---|---|---|---|---|---|")
for b in (2, 3, 4):
    def tree(t, b=b):
        if t == 0:
            return 1
        p = 1
        for i in bits(r(t)):
            p *= 1 + b ** (2 ** (i + 1))
        return (b + 1) * b ** (t - 1 - 2 * r(t)) * p
    out = krank(tree, 8, 40)
    print(f"| b = {b} | " + " | ".join(str(x) for x in out) + " |")

print()
print("D. window-size stability (the lattice ranks do not depend on M)")
for name, a in [("1-D line", lambda t: 2 ** (1 + wt(t)) - (1 if 0 in shell(t) else 0)),
                ("Z^3 vN", None),
                ("Z^5 Moore", None)]:
    if a is None:
        continue
    print("  ", name, "M=20:", krank(a, 6, 20), " M=60:", krank(a, 6, 60))
