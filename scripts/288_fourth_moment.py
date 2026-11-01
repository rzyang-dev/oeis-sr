"""Script 288 -- the FOURTH moment of the shell, and what it costs.

With  u = t - 2m  and the shell pairs {u, u-1},

    d^4 summed over a pair  =  u^4 + (u-1)^4  =  2u^4 - 4u^3 + 6u^2 - 4u + 1

so  M4 = 2 sum u^4 - 4 sum u^3 + 6 sum u^2 - 4 sum u + N  and each  sum u^j
expands through the submask moments

    sum m   = N r / 2
    sum m^2 = N (r^2 + Q) / 4
    sum m^3 = N (r^3 + 3 Q r) / 8
    sum m^4 = N (r^4 + 6 Q r^2 + 3 Q^2 - 2 P16) / 16 .

The point: P16 = sum_{i in bits r} 16^i is genuinely needed -- it is NOT a
polynomial in r and Q (scripts/287).  So the moment tower is
r, Q, P16, P64, ... and order 4 is the first one that leaves {r, Q}.
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

def M4(t, use_p16=True):
    """The closed form for sum of d^4 over the shell (exact rationals)."""
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
    return 2 * u4 - 4 * u3 + 6 * u2 - 4 * u1 + n

TMAX = 500
bad = [t for t in range(1, TMAX + 1) if M4(t) != sum(d ** 4 for d in shell(t))]
print(f"[1] fourth shell moment closed form, t<={TMAX}: "
      f"{'OK' if not bad else str(len(bad)) + ' FAILURES'}")

bad2 = [t for t in range(1, TMAX + 1)
        if M4(t) != M4(t, use_p16=False)]
print(f"[2] with the P16 term deleted: wrong for {len(bad2)} of the {TMAX} t")
print(f"    (smallest failing t = {bad2[0]}; it survives only when r t = 0)")

ref = all(sum(d ** 4 for d in shell(t)) - M4(t, use_p16=False)
          == -4 * N(r_of(t)) * P16(r_of(t)) for t in range(1, TMAX + 1))
print(f"[3] the correction is exactly -4 * N * P16: "
      f"{'OK - exact for all t <= 500' if ref else 'NOT exact'}")

print()
print("[4] the invariant tower of the submask moments:")
print("    order j = 1 needs r")
print("    order j = 2 needs r, Q          (Q = sum 4^i)")
print("    order j = 3 needs r, Q          (the 'sum 8^i' term cancels: odd cumulants vanish)")
print("    order j = 4 needs r, Q, P16     (fourth cumulant survives)")
print("    order j = 6 needs r, Q, P16, P64")
print()
print("    cumulants: mu = r/2, c2 = Q/4, c3 = 0, c4 = -P16/8, c5 = 0, c6 = P64/4")
