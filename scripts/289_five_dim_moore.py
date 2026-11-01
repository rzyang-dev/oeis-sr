"""Script 289 -- Z^5 is the first lattice whose zero count needs P16.

The Moore sphere of radius d in Z^5 has

    (2d+1)^5 - (2d-1)^5 = 160 d^4 + 80 d^2 + 2      cells,

so the fifth-dimensional Moore count is   160 M4 + 80 M2 + 2 * #shell - eps,
and M4 is exactly the moment that needs the extra invariant P16 (script 288).
This script checks the identity, and checks that dropping P16 breaks it.
"""
from fractions import Fraction as F

def bits(r):
    return [i for i in range(r.bit_length()) if (r >> i) & 1]

def subm(r):
    out = [0]
    for i in bits(r):
        out = out + [x + (1 << i) for x in out]
    return out

def r_of(t):
    return 0 if t <= 0 else t - (1 << (t.bit_length() - 1))

def shell(t):
    s = set()
    for m in subm(r_of(t)):
        s.add(t - 2 * m)
        s.add(t - 2 * m - 1)
    return s

def Q(r):
    return sum(4 ** i for i in bits(r))

def P16(r):
    return sum(16 ** i for i in bits(r))

def N(r):
    return len(subm(r))

def moments(t, use_p16=True):
    """M2 and M4 over the shell, as exact Fractions."""
    r = r_of(t)
    n, q = N(r), Q(r)
    p = P16(r) if use_p16 else 0
    S1 = F(n * r, 2)
    S2 = F(n * (r * r + q), 4)
    S3 = F(n * (r ** 3 + 3 * q * r), 8)
    S4 = F(n * (r ** 4 + 6 * q * r * r + 3 * q * q - 2 * p), 16)
    u4 = t ** 4 * n - 8 * t ** 3 * S1 + 24 * t * t * S2 - 32 * t * S3 + 16 * S4
    u3 = t ** 3 * n - 6 * t * t * S1 + 12 * t * S2 - 8 * S3
    u2 = t * t * n - 4 * t * S1 + 4 * S2
    u1 = t * n - 2 * S1
    M4 = 2 * u4 - 4 * u3 + 6 * u2 - 4 * u1 + n
    # second moment: sum over pairs of (u^2 + (u-1)^2) = 2u^2 - 2u + 1
    a2 = t * t * n - 4 * t * S1 + 4 * S2
    a1 = u1
    M2v = 2 * a2 - 2 * a1 + n
    return M2v, M4

def moore5_level(d):
    return 1 if d == 0 else (2 * d + 1) ** 5 - (2 * d - 1) ** 5

TMAX = 60
bad = []
bad_nop16 = []
for t in range(1, TMAX + 1):
    S = shell(t)
    eps = 1 if 0 in S else 0
    direct = sum(moore5_level(d) for d in S)
    M2v, M4 = moments(t)
    closed = 160 * M4 + 80 * M2v + 2 * len(S) - eps
    if direct != closed:
        bad.append(t)
    M2n, M4n = moments(t, use_p16=False)
    if direct != 160 * M4n + 80 * M2n + 2 * len(S) - eps:
        bad_nop16.append(t)

print(f"[1] Z^5 Moore (160 d^4 + 80 d^2 + 2), t<={TMAX}: "
      f"{'OK' if not bad else str(len(bad)) + ' FAILURES'}")
print(f"[2] same with the P16 term dropped: wrong for {len(bad_nop16)} of {TMAX} t")
print(f"    (first failing t = {bad_nop16[0] if bad_nop16 else '-'})")
print()
print("[3] sanity: the level sizes are 1, 242, 2882, 13682, ...")
print("    ", [moore5_level(d) for d in range(4)])
print("[4] the first few Z^5 Moore zero counts:",
      [sum(moore5_level(d) for d in shell(t)) for t in range(1, 8)])
