"""282_counting_table.py -- the master counting table.

For each geometry we compute the number of zeroes at time t twice:
  (a) by summing c_d over the shell (the definition),
  (b) by the closed form listed in the table,
and report whether they agree for t = 1..TMAX.
"""

from math import comb

def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def wt(n):
    return bin(n).count("1")

def bits(m):
    return [i for i in range(m) if (m >> i) & 1]

def shell(t):
    rt = r(t)
    return [d for d in range(t + 1) if ((t - d) // 2) & rt == (t - d) // 2]

def N_subm(m):
    return 1 << wt(m)

def Q(m):
    return sum(4 ** i for i in bits(m))

def isM1(t):
    return t > 0 and ((t + 1) & t) == 0

def zeros(c, t):
    return sum(c(d) for d in shell(t))

def sigma(t):                      # sum of d over the shell
    return N_subm(r(t)) * (2 * t - 1 - 2 * r(t))

def cardS(t):
    return 2 * N_subm(r(t))

def eps(t):                        # [0 in shell]
    return 1 if 0 in shell(t) else 0

def M2(t):                         # sum of d^2 over the shell
    K = t - r(t)
    return N_subm(r(t)) * (2 * K * (K - 1) + 2 * Q(r(t)) + 1)

geo = []

geo.append(("1-D line", lambda d: 1 if d == 0 else 2,
            lambda t: 2 ** (1 + wt(t)) - eps(t),
            "2^(1+wt t) - [t=2^i-1]", "Final: `row_zero_win_card`", "A267447"))

geo.append(("1-D ray (orthant)", lambda d: 1,
            lambda t: cardS(t),
            "#shell t = 2^wt t", "Final: `row_zero_pos_card`", "--"))

geo.append(("Z^2 von Neumann (5-nbhd)", lambda d: 1 if d == 0 else 4 * d,
            lambda t: 4 * sigma(t) + eps(t),
            "4 sigma + eps", "Census: `shell_sum_linear_form`", "A169699 (formula wrong)"))

geo.append(("Z^2 Moore (9-nbhd)", lambda d: 1 if d == 0 else 8 * d,
            lambda t: 8 * sigma(t) + eps(t),
            "8 sigma + eps", "Census: `shell_sum_linear_form`", "not in OEIS"))

geo.append(("triangular lattice", lambda d: 1 if d == 0 else 6 * d,
            lambda t: 6 * sigma(t) + eps(t),
            "6 sigma + eps", "Census: `shell_sum_linear_form`", "not in OEIS"))

geo.append(("Z^2 orthant, von Neumann", lambda d: d + 1,
            lambda t: sigma(t) + cardS(t),
            "sigma + #shell = #subm(2t+1-2r)", "analogue of Census", "--"))

geo.append(("Z^2 orthant, Moore", lambda d: 2 * d + 1,
            lambda t: 2 * sigma(t) + cardS(t),
            "2^(1+wt t+floor(log2 t))", "Final: `moore_zero_card_closed`", "A189007 (shifted)"))

geo.append(("Z^3 von Neumann", lambda d: 1 if d == 0 else 4 * d * d + 2,
            lambda t: 4 * M2(t) + 2 * (cardS(t) - eps(t)) + eps(t),
            "4 M2 + 2(#shell - eps) + eps", "Dim3: `zero_count_Z3_vonNeumann`", "not in OEIS"))

geo.append(("Z^3 Moore", lambda d: 1 if d == 0 else 24 * d * d + 2,
            lambda t: 24 * M2(t) + 2 * (cardS(t) - eps(t)) + eps(t),
            "24 M2 + 2(#shell - eps) + eps", "Dim3: `zero_count_Z3_moore`", "not in OEIS"))

def tree_c(b):
    return lambda d: b ** d

def tree_formula(b):
    def f(t):
        if t == 0:
            return 1
        p = 1
        for i in bits(r(t)):
            p *= 1 + b ** (2 ** (i + 1))
        return (b + 1) * b ** (t - 1 - 2 * r(t)) * p
    return f

geo.append(("binary tree", tree_c(2), tree_formula(2),
            "(b+1) b^(t-1-2r) prod(1+b^(2^(i+1)))", "Tree: `shell_sum_pow_factored`", "not in OEIS"))

geo.append(("ternary tree", tree_c(3), tree_formula(3),
            "same, b = 3", "Tree: `shell_sum_pow_factored`", "not in OEIS"))


def M3(t):
    rt = r(t); K = t - rt; q = Q(rt); n = N_subm(rt); k = K - 1
    return n * (2 * k ** 3 + 3 * k ** 2 + 3 * k + 1 + 3 * q * (2 * k + 1))

geo.append(("Z^4 Moore", lambda d: 1 if d == 0 else 64 * d ** 3 + 16 * d,
            lambda t: 64 * M3(t) + 16 * sigma(t) + eps(t),
            "64 M3 + 16 sigma + eps", "Dim4: `zero_count_Z4_moore`", "not in OEIS"))

geo.append(("Z^4 von Neumann", lambda d: 1 if d == 0 else (8 * d * (d * d + 2)) // 3,
            None, "3Z = 8(M3 + 2 sigma) + 3 eps", "Dim4: `zero_count_Z4_vonNeumann`", "not in OEIS"))


def P16(m):
    """sum of 16^i over the set bits of m"""
    return sum(16 ** i for i in bits(m))


def M4(t):
    rt = r(t); q = Q(rt); n = N_subm(rt); p = P16(rt); K = t - rt
    S1 = n * rt // 2
    S2 = n * (rt * rt + q) // 4
    S3 = n * (rt ** 3 + 3 * q * rt) // 8
    S4 = n * (rt ** 4 + 6 * q * rt * rt + 3 * q * q - 2 * p) // 16
    u4 = t ** 4 * n - 8 * t ** 3 * S1 + 24 * t * t * S2 - 32 * t * S3 + 16 * S4
    u3 = t ** 3 * n - 6 * t * t * S1 + 12 * t * S2 - 8 * S3
    u2 = t * t * n - 4 * t * S1 + 4 * S2
    u1 = t * n - 2 * S1
    return 2 * u4 - 4 * u3 + 6 * u2 - 4 * u1 + n


geo.append(("Z^5 Moore", lambda d: 1 if d == 0 else 160 * d ** 4 + 80 * d * d + 2,
            lambda t: 160 * M4(t) + 80 * M2(t) + 2 * (cardS(t) - eps(t)) + eps(t),
            "160 M4 + 80 M2 + 2(#shell-eps) + eps", "(M4 needs P16)", "not in OEIS"))

def l1_5(d):
    if d == 0:
        return 1
    return sum(2 ** k * comb(5, k) * comb(d - 1, k - 1) for k in range(1, 6))

assert all((4 * d ** 4 + 20 * d * d + 6) // 3 == l1_5(d) for d in range(1, 12)), "Z^5 l1 fit failed"

geo.append(("Z^5 von Neumann", lambda d: 1 if d == 0 else (4 * d ** 4 + 20 * d * d + 6) // 3,
            None, "3Z = 4 M4 + 20 M2 + 6 #shell - 3 eps", "(M4 needs P16)", "not in OEIS"))

TMAX = 60
print("| geometry | c_d | closed form | checked | Lean | OEIS |")
print("|---|---|---|---|---|---|")
bad = 0
for name, c, f, shape, lean, oeis in geo:
    if f is None and name.startswith("Z^4"):
        ok = all(3 * zeros(c, t) == 8 * (M3(t) + 2 * sigma(t)) + 3 * eps(t) for t in range(1, TMAX + 1))
    elif f is None:
        ok = all(3 * zeros(c, t) == 4 * M4(t) + 20 * M2(t) + 6 * cardS(t) - 3 * eps(t)
                 for t in range(1, TMAX + 1))
    else:
        ok = all(zeros(c, t) == f(t) for t in range(1, TMAX + 1))
    if not ok:
        bad += 1
        for t in range(1, TMAX + 1):
            if zeros(c, t) != f(t):
                print("   MISMATCH", name, "t =", t, zeros(c, t), f(t))
                break
    print("| %s | %s | %s | t <= %d %s | %s | %s |" % (
        name, str([c(d) for d in range(6)]), shape, TMAX,
        "OK" if ok else "FAIL", lean, oeis))
print()
print("closed forms that failed:", bad)

# also: the sum-form-only check for Z^4 (no closed form yet)
from math import comb
def l1_4(d):
    if d == 0:
        return 1
    return sum(2 ** k * comb(4, k) * comb(d - 1, k - 1) for k in range(1, 5))
print("Z^4 von Neumann zeros, t = 1..12:", [zeros(l1_4, t) for t in range(1, 13)])