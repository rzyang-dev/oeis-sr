"""Script 292 -- how many parameters does each counting sequence need?

A sequence a is 2-regular when the Z-module spanned by its 2-kernel

    K2(a) = { n |-> a(2^k n + j) : k >= 0, 0 <= j < 2^k }

is finitely generated; the rank is the dimension over Q of its span.
We estimate the rank by exact Gaussian elimination over Q on the first
M values of every kernel element for k <= K.

Because Arm.lean gives the two-step recursion

    Z(2u)   = sum_{m subset r u} [ c(2(u-2m)) + c(2(u-2m)-1) ]
    Z(2u+1) = sum_{m subset r u} [ (c(2(u-2m)+1)+c(2(u-2m)))
                                   + (c(2(u-2m)-1)+c(2(u-2m)-2)) ]

every row of the table must be 2-regular.  The numbers below are the ranks.
"""
from fractions import Fraction as F
from math import comb

def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def wt(n):
    return bin(n).count("1")

def bits(m):
    return [i for i in range(m.bit_length()) if (m >> i) & 1]

def shell(t):
    rt = r(t)
    return [d for d in range(t + 1) if ((t - d) // 2) & rt == (t - d) // 2]

def Q(m):
    return sum(4 ** i for i in bits(m))

def P16(m):
    return sum(16 ** i for i in bits(m))

def N(m):
    return 1 << wt(m)

def sigma(t):
    return N(r(t)) * (2 * t - 1 - 2 * r(t))

def cardS(t):
    return 2 * N(r(t))

def eps(t):
    return 1 if 0 in shell(t) else 0

def M2(t):
    K = t - r(t)
    return N(r(t)) * (2 * K * (K - 1) + 2 * Q(r(t)) + 1)

def M3(t):
    rt = r(t); K = t - rt; q = Q(rt); n = N(rt); k = K - 1
    return n * (2 * k ** 3 + 3 * k ** 2 + 3 * k + 1 + 3 * q * (2 * k + 1))

def M4(t):
    rt = r(t); q = Q(rt); n = N(rt); p = P16(rt)
    S1 = n * rt // 2
    S2 = n * (rt * rt + q) // 4
    S3 = n * (rt ** 3 + 3 * q * rt) // 8
    S4 = n * (rt ** 4 + 6 * q * rt * rt + 3 * q * q - 2 * p) // 16
    u4 = t ** 4 * n - 8 * t ** 3 * S1 + 24 * t * t * S2 - 32 * t * S3 + 16 * S4
    u3 = t ** 3 * n - 6 * t * t * S1 + 12 * t * S2 - 8 * S3
    u2 = t * t * n - 4 * t * S1 + 4 * S2
    u1 = t * n - 2 * S1
    return 2 * u4 - 4 * u3 + 6 * u2 - 4 * u1 + n

def tree(b):
    def f(t):
        if t == 0:
            return 1
        p = 1
        for i in bits(r(t)):
            p *= 1 + b ** (2 ** (i + 1))
        return (b + 1) * b ** (t - 1 - 2 * r(t)) * p
    return f

SEQ = {
    "1-D line":        lambda t: 2 ** (1 + wt(t)) - eps(t),
    "1-D ray":         cardS,
    "Z^2 vN  (A169699)": lambda t: 4 * sigma(t) + eps(t),
    "Z^2 Moore":       lambda t: 8 * sigma(t) + eps(t),
    "triangular":      lambda t: 6 * sigma(t) + eps(t),
    "Z^2 orthant Moore": lambda t: 2 * sigma(t) + cardS(t),
    "Z^3 vN":          lambda t: 4 * M2(t) + 2 * (cardS(t) - eps(t)) + eps(t),
    "Z^3 Moore":       lambda t: 24 * M2(t) + 2 * (cardS(t) - eps(t)) + eps(t),
    "binary tree":     tree(2),
    "ternary tree":    tree(3),
    "Z^4 Moore":       lambda t: 64 * M3(t) + 16 * sigma(t) + eps(t),
    "Z^5 Moore":       lambda t: 160 * M4(t) + 80 * M2(t) + 2 * (cardS(t) - eps(t)) + eps(t),
    "#shell (2^wt)":   cardS,
    "sigma":           sigma,
    "Q(r t)":          lambda t: Q(r(t)),
    "P16(r t)":        lambda t: P16(r(t)),
}

def rank(matrix):
    """exact rank over Q, fraction-free-ish Gaussian elimination"""
    rows = [row[:] for row in matrix]
    if not rows:
        return 0
    m, n = len(rows), len(rows[0])
    rk = 0
    for col in range(n):
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
                for j in range(col, n):
                    rows[i][j] = F(rows[i][j]) - f * F(rows[rk][j])
        rk += 1
        if rk == m:
            break
    return rk

KMAX = 7
M = 40          # window length per kernel element
needed = (1 << KMAX) * (M + 2) + 4

print(f"kernel window M = {M}, depth K <= {KMAX}")
print(f"| sequence | rank(K=4) | rank(K=5) | rank(K=6) | rank(K=7) |")
print("|---|---|---|---|---|")
for name, a in SEQ.items():
    vals = [a(t) for t in range(needed + 1)]
    out = []
    for K in range(4, KMAX + 1):
        elems = []
        for k in range(K + 1):
            for j in range(1 << k):
                vec = [vals[(1 << k) * n + j] for n in range(1, M + 1)]
                elems.append(vec)
        out.append(rank(elems))
    print(f"| {name} | " + " | ".join(str(x) for x in out) + " |")
