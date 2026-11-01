"""Script 299 -- the row functionals of the linear representation.

Arm.lean proves (shell_sum_of_poly):  if  c x + c (x-1) = sum_i gamma_i x^i  for
every x >= 1, then  Z_c(t) = sum_i gamma_i Phi_i(t).

For the table's geometries the level size has the form "the centre carries c0,
every other level carries value(d)", so the polynomial identity holds for x >= 2
and the point x = 1 costs a correction  (c0 - p 0) * [1 in arm t].  Since
0 in shell t <-> 1 in arm t  (Arm.lean: zero_mem_shell_iff), that correction is
exactly (c0 - p 0) * eps.

This script fits gamma for each row and checks the identity for t <= 200.
Rows marked "3x" use the scaled form 3 Z = ... because the level size has a
denominator 3 in closed form.
"""
from fractions import Fraction as F

def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def subm(m):
    out = [0]
    for i in range(m.bit_length()):
        if (m >> i) & 1:
            out = out + [x + (1 << i) for x in out]
    return out

def arm(t):
    return [t - 2 * m for m in subm(r(t))]

def shell(t):
    return sorted(set(arm(t)) | {x - 1 for x in arm(t)})

def Phi(k, t):
    return sum(x ** k for x in arm(t))

def fit_gamma(g, deg):
    n = deg + 1
    A = [[F(x) ** i for i in range(n)] + [F(g(x))] for x in range(1, n + 1)]
    for col in range(n):
        piv = next(i for i in range(col, n) if A[i][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [v / pv for v in A[col]]
        for i in range(n):
            if i != col and A[i][col] != 0:
                f = A[i][col]
                A[i] = [a - f * b for a, b in zip(A[i], A[col])]
    return [A[i][n] for i in range(n)]

# (name, degree, polynomial part p, value at d >= 1, centre value c0, scale)
ROWS = [
    ("1-D line",          0, lambda x: 2,                lambda d: 2,                             1, 1),
    ("1-D ray",           0, lambda x: 1,                lambda d: 1,                             1, 1),
    ("Z^2 vN (A169699)",  1, lambda x: 4 * x,            lambda d: 4 * d,                         1, 1),
    ("Z^2 Moore",         1, lambda x: 8 * x,            lambda d: 8 * d,                         1, 1),
    ("triangular",        1, lambda x: 6 * x,            lambda d: 6 * d,                         1, 1),
    ("Z^2 orthant vN",    1, lambda x: x + 1,            lambda d: d + 1,                         1, 1),
    ("Z^2 orthant Moore", 1, lambda x: 2 * x + 1,        lambda d: 2 * d + 1,                     1, 1),
    ("Z^3 vN",            2, lambda x: 4 * x * x + 2,    lambda d: 4 * d * d + 2,                 1, 1),
    ("Z^3 Moore",         2, lambda x: 24 * x * x + 2,   lambda d: 24 * d * d + 2,                1, 1),
    ("Z^4 Moore",         3, lambda x: 64 * x ** 3 + 16 * x,
                             lambda d: 64 * d ** 3 + 16 * d,                                    1, 1),
    ("Z^4 vN (3x)",       3, lambda x: 8 * x ** 3 + 16 * x,
                             lambda d: 8 * d ** 3 + 16 * d,                                     3, 3),
    ("Z^5 Moore",         4, lambda x: 160 * x ** 4 + 80 * x * x + 2,
                             lambda d: 160 * d ** 4 + 80 * d * d + 2,                           1, 1),
    ("Z^5 vN (3x)",       4, lambda x: 4 * x ** 4 + 20 * x * x + 6,
                             lambda d: 4 * d ** 4 + 20 * d * d + 6,                             3, 3),
]

TMAX = 200
print("| geometry | gamma | delta = c0 - p(0) | rank of the row | check |")
print("|---|---|---|---|---|")
bad = 0
for name, deg, p, val, c0, scale in ROWS:
    g = lambda x, p=p: p(x) + p(x - 1)
    gam = fit_gamma(g, deg)
    delta = F(c0) - F(p(0))
    ok = True
    for t in range(1, TMAX + 1):
        lhs = sum(F(c0) if d == 0 else F(val(d)) for d in shell(t))
        rhs = sum(gam[i] * Phi(i, t) for i in range(deg + 1))
        rhs += delta * (1 if (1 in arm(t)) else 0)
        if lhs != rhs:
            ok = False
            print("  FAIL", name, "t =", t, lhs, rhs)
            break
    if not ok:
        bad += 1
    gs = "[" + ", ".join(str(v) for v in gam) + "]"
    print(f"| {name} | {gs} | {delta} | {deg + 1} + {0 if delta == 0 else 1} | t <= {TMAX} {'OK' if ok else 'FAIL'} |")
print()
print("failures:", bad)
