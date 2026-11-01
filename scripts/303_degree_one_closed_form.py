"""Script 303 -- the degree <= 1 rows have a closed-form representation.

For a row of degree at most one, with gamma = (g0, g1), the coefficient vector of
the explicit representation is

    c_0 = g0 * 2^wt(r) ,        c_1 = g1 * 2^(k + wt(r)) .

(The constant coefficient multiplies by 1 or 2 by the parity of the step, and the
top coefficient multiplies by 2 or 4, so both only see the popcount.)
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

def coef(j, k, r, gamma):
    Ak = A(j, k, r)
    return [sum(gamma[i] * Ak[i][l] for i in range(j + 1)) for l in range(j + 1)]

bad = 0
for name, gamma in [("1-D line", [4]), ("Z^2 vN", [-4, 8]), ("Z^2 Moore", [-8, 16]),
                    ("triangular", [-6, 12])]:
    j = len(gamma) - 1
    for k in range(0, 7):
        for rr in range(1 << k):
            c = coef(j, k, rr, gamma)
            w = bin(rr).count("1")
            if j == 0:
                pred = [gamma[0] * 2 ** w]
            else:
                pred = [gamma[0] * 2 ** w, gamma[1] * 2 ** (k + w)]
            if c != pred:
                print(f"FAIL {name} k={k} r={rr}: {c} vs {pred}")
                bad += 1
                break
print(f"[1] closed form for the degree <= 1 rows, k <= 6: {'OK' if bad == 0 else 'FAIL'}")

print()
print("[2] degree 2 already breaks the popcount-only property:")
print("    Z^3 vN, k = 5: c(wt=0) = [8, -256, 8192]  (r = 0)")
print("    but the value for wt = 2 differs between r = 3 and r = 12:")
def show(rr, k=5):
    print(f"      r={rr:2d} (wt={bin(rr).count('1')}): {coef(2, k, rr, [8, -8, 8])}")
show(3); show(12); show(5); show(6)
