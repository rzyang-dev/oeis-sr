"""Script 287 -- P16 = sum_{i in bits r} 16^i is NOT a polynomial in Q.

Q r = sum_{i in bits r} 4^i is injective (base-4 digits are 0/1), so every
bit-set invariant is *some* function of Q.  The question is whether P16 is a
POLYNOMIAL function of Q.  We test every degree d <= 30: interpolate the
polynomial through the first d+1 data points (Q(r), P16(r)) and check whether
it predicts the rest.
"""
from fractions import Fraction

def bits(r):
    return [i for i in range(r.bit_length()) if (r >> i) & 1]

def Q(r):
    return sum(4 ** i for i in bits(r))

def P16(r):
    return sum(16 ** i for i in bits(r))

RMAX = 300
data = [(Q(r), P16(r)) for r in range(1, RMAX + 1)]

def poly_fit(points):
    """Lagrange interpolation; returns a coeff list (ascending) or None."""
    n = len(points)
    # Newton form on fractions
    xs = [Fraction(x) for x, _ in points]
    ys = [Fraction(y) for _, y in points]
    coef = ys[:]
    for k in range(1, n):
        for i in range(n - 1, k - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) / (xs[i] - xs[i - k])
    # evaluate Newton form
    def ev(t):
        t = Fraction(t)
        acc = coef[-1]
        for k in range(len(coef) - 2, -1, -1):
            acc = acc * (t - xs[k]) + coef[k]
        return acc
    return ev

fails = []
for d in range(1, 31):
    pts = data[:d + 1]
    ev = poly_fit(pts)
    bad = [r for r in range(1, RMAX + 1) if ev(Q(r)) != P16(r)]
    fails.append((d, bad[0] if bad else None, len(bad)))
    print(f"degree <= {d:2d}: first mismatch at r = {str(bad[0]) if bad else '-'}"
          f"  ({len(bad)} of {RMAX} wrong)")
print()
if all(f[1] is not None for f in fails):
    print("[1] every degree 1..30 fails: an interpolant matching the first d+1")
    print("    values (Q(r), P16(r)) already misses at small r, so P16 is not a")
    print("    polynomial in Q of degree <= 30.")
else:
    ok = [f for f in fails if f[1] is None]
    print("[1] degrees that DO fit:", ok)
print()
print("[1b] the 'polynomial in (r, Q)' claim is equivalent to 'poly in Q':")
print("     the map bits(r) |-> Q(r) is injective (base-4 digits are 0/1),")
print("     so Q determines r and every bit-set invariant.")
print()
print("[2] the j = 4 term in the fourth moment:")
for r in [3, 5, 6, 7, 10, 11]:
    print(f"    r={r:3d}  Q={Q(r):5d}  P16={P16(r):8d}  "
          f"E[m^4]*(16/N) part from P16 = {-2*P16(r)}")
