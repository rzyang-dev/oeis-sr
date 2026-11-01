"""Script 301 -- the explicit linear representation, checked end to end.

Matrix.lean defines

    M0 i l = [l = i] * 2^i
    M1 i l = [l <= i and l = i mod 2] * C(i,l) * 2^(l+1)
    A j 0 r     = identity
    A j (k+1) r = (if r even then M0 else M1) * A j k (r/2)
    W k r v i   = sum_{l <= j} A j k r i l * v l
    Z_c(2^k n + r) = sum_l (sum_i gamma i * A j k r i l) * Phi_l(n) + delta * centre

This script rebuilds A and checks the final identity for every polynomial row.
"""
from fractions import Fraction as F
from math import comb

def r_of(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def subm(m):
    out = [0]
    for i in range(m.bit_length()):
        if (m >> i) & 1:
            out = out + [x + (1 << i) for x in out]
    return out

def arm(t):
    return [t - 2 * m for m in subm(r_of(t))]

def shell(t):
    return sorted(set(arm(t)) | {x - 1 for x in arm(t)})

def Phi(k, t):
    return sum(x ** k for x in arm(t))

def M0(i, l):
    return (2 ** i) if l == i else 0

def M1(i, l):
    if l <= i and l % 2 == i % 2:
        return comb(i, l) * 2 ** (l + 1)
    return 0

def A(j, k, r):
    """(j+1)x(j+1) integer matrix of the k-fold transfer at residue r"""
    if k == 0:
        return [[1 if i == l else 0 for l in range(j + 1)] for i in range(j + 1)]
    prev = A(j, k - 1, r // 2)
    M = M0 if r % 2 == 0 else M1
    return [[sum(M(i, m) * prev[m][l] for m in range(j + 1)) for l in range(j + 1)]
            for i in range(j + 1)]

ROWS = [
    ("1-D line",     0, [4],                              -1, lambda d: 1 if d == 0 else 2),
    ("Z^2 vN",       1, [-4, 8],                           1, lambda d: 1 if d == 0 else 4 * d),
    ("Z^2 Moore",    1, [-8, 16],                          1, lambda d: 1 if d == 0 else 8 * d),
    ("triangular",   1, [-6, 12],                          1, lambda d: 1 if d == 0 else 6 * d),
    ("Z^3 vN",       2, [8, -8, 8],                       -1, lambda d: 1 if d == 0 else 4 * d * d + 2),
    ("Z^3 Moore",    2, [28, -48, 48],                    -1, lambda d: 1 if d == 0 else 24 * d * d + 2),
    ("Z^4 Moore",    3, [-80, 224, -192, 128],             1, lambda d: 1 if d == 0 else 64 * d ** 3 + 16 * d),
    ("Z^4 vN (3x)",  3, [-24, 56, -24, 16],                3, lambda d: 3 if d == 0 else 8 * d * (d * d + 2)),
    ("Z^5 Moore",    4, [244, -800, 1120, -640, 320],     -1, lambda d: 1 if d == 0 else 160 * d ** 4 + 80 * d * d + 2),
    ("Z^5 vN (3x)",  4, [36, -56, 64, -16, 8],            -3, lambda d: 3 if d == 0 else 4 * d ** 4 + 20 * d * d + 6),
]

KMAX = 5
NMAX = 40
bad = 0
for name, j, gamma, delta, c in ROWS:
    for k in range(KMAX + 1):
        for rr in range(1 << k):
            Ak = A(j, k, rr)
            coef = [sum(gamma[i] * Ak[i][l] for i in range(j + 1)) for l in range(j + 1)]
            for n in range(1, NMAX + 1):
                t = (1 << k) * n + rr
                lhs = sum(c(d) for d in shell(t))
                rhs = sum(coef[l] * Phi(l, n) for l in range(j + 1))
                rhs += delta * (1 if 1 in arm(t) else 0)
                if lhs != rhs:
                    print(f"FAIL {name} k={k} r={rr} n={n}: {lhs} vs {rhs}")
                    bad += 1
                    break
            if bad:
                break
        if bad:
            break
    if bad:
        break

print(f"[1] explicit representation for {len(ROWS)} rows, k <= {KMAX}, n <= {NMAX}: "
      f"{'OK' if bad == 0 else str(bad) + ' FAILURES'}")

print()
print("[2] the coefficient vectors are eventually periodic in k? showcase for Z^2 vN:")
j, gamma = 1, [-4, 8]
for k in range(4):
    for rr in range(1 << k):
        Ak = A(j, k, rr)
        coef = [sum(gamma[i] * Ak[i][l] for i in range(j + 1)) for l in range(j + 1)]
        print(f"    k={k} r={rr}: c = {coef}")
