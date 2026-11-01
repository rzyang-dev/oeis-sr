"""277_geometry_census.py -- zero counts of rule 129 for a library of geometries.

Since the zero set at time t is the union of the shells,

    #Z(t) = sum_{d in S(t)} c_d ,   S(t) = {d <= t : (t-d)/2 subset of r(t)}

where c_d is the number of cells at distance d from the seed, the count for a
geometry only needs its level-size sequence c.  No simulation is required.

Prints one line per geometry: name, c_d (d <= 8), and #Z(t) for t = 1..28.
"""

def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def shell(t):
    rt = r(t)
    return [d for d in range(t + 1) if ((t - d) // 2) & rt == (t - d) // 2]

def counts(c, T=28):
    return [sum(c(d) for d in shell(t)) for t in range(1, T + 1)], [sum(c(d) for d in shell(t)) for t in range(0, T + 1)]

def l1(D):
    "number of integer points in Z^D at L1 distance exactly d"
    def c(d):
        if d == 0:
            return 1
        tot = 0
        for k in range(1, min(D, d) + 1):
            tot += 2 ** k * comb(D, k) * comb(d - 1, k - 1)
        return tot
    return c

def linf(D):
    "number of integer points in Z^D at Chebyshev distance exactly d"
    return lambda d: 1 if d == 0 else (2 * d + 1) ** D - (2 * d - 1) ** D

def tree(b):
    return lambda d: b ** d

def comb(n, k):
    from math import comb as C
    return C(n, k)

lib = [
    ("1-D line            ", lambda d: 1 if d == 0 else 2),
    ("Z^2 von Neumann     ", l1(2)),
    ("Z^2 Moore           ", linf(2)),
    ("Z^3 von Neumann     ", l1(3)),
    ("Z^3 Moore           ", linf(3)),
    ("Z^4 von Neumann     ", l1(4)),
    ("Z^4 Moore           ", linf(4)),
    ("hexagonal lattice   ", lambda d: 1 if d == 0 else 6 * d),
    ("binary tree         ", tree(2)),
    ("ternary tree        ", tree(3)),
    ("4-ary tree          ", tree(4)),
]

print("%-20s %-28s %s" % ("geometry", "c_d (d=0..7)", "#Z(t), t=1..24"))
for name, c in lib:
    _, seq = counts(c)
    print("%-20s %-28s %s" % (name, ",".join(str(c(d)) for d in range(8)), ",".join(str(x) for x in seq[1:25])))

print()
print("quarter-plane variants (nonnegative orthant, same rule):")
def orthant(c, D):
    "level-size of the orthant for the metric whose full-space c is given"
    # c_d(full) = 2^D * c_d(interior of a quadrant) + boundary corrections;
    # instead count orthant levels directly by brute force for small d.
    return None

# orthant level sizes by brute force
from itertools import product
def orthant_counts(D, M):
    out = [0] * (M + 1)
    rng = range(0, M + 1)
    for pt in product(rng, repeat=D):
        lev = sum(pt) if D == 2 else max(pt)
        if lev <= M:
            out[lev] += 1
    return out

for D, metric in [(2, "L1"), (2, "Linf"), (3, "L1"), (3, "Linf")]:
    M = 28
    if metric == "L1":
        cs = orthant_counts(D, M)
    else:
        rng = range(0, M + 1)
        cs = [0] * (M + 1)
        for pt in product(rng, repeat=D):
            lev = max(pt)
            cs[lev] += 1
    c = lambda d, cs=cs: cs[d]
    _, seq = counts(c)
    print("orthant %dD %-4s      c_d=%-24s #Z(t), t=1..24: %s"
          % (D, metric, ",".join(str(x) for x in cs[:8]), ",".join(str(x) for x in seq[1:25])))
