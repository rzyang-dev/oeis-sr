"""Script 302 -- does the coefficient vector see r only through its popcount?

For each row, compare the coefficient vectors c(k, r) for r < 2^k: if r and r'
have the same popcount, are the coefficients equal?  (They are for Z^2 vN.)
"""
from math import comb

def M0(i, l):
    return (2 ** i) if l == i else 0

def M1(i, l):
    if l <= i and l % 2 == i % 2:
        return comb(i, l) * 2 ** (l + 1)
    return 0

def A(j, k, r):
    if k == 0:
        return [[1 if i == l else 0 for l in range(j + 1)] for i in range(j + 1)]
    prev = A(j, k - 1, r // 2)
    M = M0 if r % 2 == 0 else M1
    return [[sum(M(i, m) * prev[m][l] for m in range(j + 1)) for l in range(j + 1)]
            for i in range(j + 1)]

ROWS = [
    ("1-D line",   0, [4]),
    ("Z^2 vN",     1, [-4, 8]),
    ("Z^2 Moore",  1, [-8, 16]),
    ("Z^3 vN",     2, [8, -8, 8]),
    ("Z^3 Moore",  2, [28, -48, 48]),
    ("Z^4 Moore",  3, [-80, 224, -192, 128]),
    ("Z^5 Moore",  4, [244, -800, 1120, -640, 320]),
]

K = 5
for name, j, gamma in ROWS:
    table = {}
    ok = True
    for rr in range(1 << K):
        Ak = A(j, K, rr)
        coef = tuple(sum(gamma[i] * Ak[i][l] for i in range(j + 1)) for l in range(j + 1))
        w = bin(rr).count("1")
        if w in table and table[w] != coef:
            ok = False
        table.setdefault(w, coef)
    print(f"{name:12s} popcount-only: {'YES' if ok else 'no '}   k={K} table:")
    for w in sorted(table):
        print(f"    wt={w}: {list(table[w])}")
