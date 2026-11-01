"""Script 285 -- independent checks for the fourth-moment/4-D theorems.

1. Enumerate the Moore (l_inf) and von Neumann (l_1) level sizes in Z^4.
2. Check the two Z^4 zero-count laws   Z = 64 M3 + 16 sigma + eps
   and   3 Z = 8 M3 + 16 sigma + 3 eps   from the shell description.
3. Check the third moment of the shell, M3 = N (2k^3+3k^2+3k+1+3Q(2k+1)).
"""
from itertools import product

def r_of(t):
    if t <= 0:
        return 0
    return t - (1 << (t.bit_length() - 1))

def subm(r):
    return [m for m in range(r + 1) if m & r == m]

def shell(t):
    r = r_of(t)
    s = set()
    for m in subm(r):
        s.add(t - 2 * m)
        s.add(t - 2 * m - 1)
    return s

def Q(r):
    return sum(4 ** i for i in range(r.bit_length()) if (r >> i) & 1)

def N(r):
    return len(subm(r))

# ---- 1. level sizes in Z^4 -------------------------------------------------
def moore_level(d):
    if d == 0:
        return 1
    return (2 * d + 1) ** 4 - (2 * d - 1) ** 4

def vn_level(d):
    if d == 0:
        return 1
    return sum(_binom(4, j) * _binom(d - 1, j - 1) * 2 ** j for j in range(1, 5))

def _binom(n, k):
    if k < 0 or k > n:
        return 0
    num = 1
    for i in range(k):
        num = num * (n - i) // (i + 1)
    return num

bad = 0
for d in range(1, 11):
    # brute force over the cube of side 2d+1, count the exact levels
    cnt_moore = 0
    cnt_vn = 0
    for pt in product(range(-d, d + 1), repeat=4):
        m = max(abs(x) for x in pt)
        s = sum(abs(x) for x in pt)
        if m == d:
            cnt_moore += 1
        if s == d:
            cnt_vn += 1
    if cnt_moore != moore_level(d) or cnt_moore != 64 * d**3 + 16 * d:
        print(f"MOORE LEVEL MISMATCH d={d}: brute {cnt_moore} formula {64*d**3+16*d}")
        bad += 1
    if cnt_vn != vn_level(d) or 3 * cnt_vn != 8 * d**3 + 16 * d:
        print(f"VN LEVEL MISMATCH d={d}: brute {cnt_vn} formula {8*d*(d*d+2)//3}")
        bad += 1
print(f"[1] Z^4 level sizes d<=10: {'OK' if bad == 0 else str(bad) + ' FAILURES'}")

# ---- 2. the two zero-count laws ---------------------------------------------
bad = 0
for t in range(1, 201):
    S = shell(t)
    M3 = sum(d**3 for d in S)
    sig = sum(S)
    eps = 1 if 0 in S else 0
    Zm = sum(1 if d == 0 else 64 * d**3 + 16 * d for d in S)
    Zv = sum(1 if d == 0 else 8 * d * (d * d + 2) // 3 for d in S)
    if Zm != 64 * M3 + 16 * sig + eps:
        print(f"MOORE LAW FAIL t={t}")
        bad += 1
    if 3 * Zv != 8 * M3 + 16 * sig + 3 * eps:
        print(f"VN LAW FAIL t={t}")
        bad += 1
print(f"[2] Z^4 zero-count laws t<=200: {'OK' if bad == 0 else str(bad) + ' FAILURES'}")

# ---- 3. third moment of the shell ------------------------------------------
bad = 0
for t in range(1, 2001):
    S = shell(t)
    r = r_of(t)
    k = t - r - 1
    lhs = sum(d**3 for d in S)
    rhs = N(r) * (2 * k**3 + 3 * k**2 + 3 * k + 1 + 3 * Q(r) * (2 * k + 1))
    if lhs != rhs:
        print(f"M3 FAIL t={t}: {lhs} vs {rhs}")
        bad += 1
        if bad > 5:
            break
print(f"[3] shell_sum_cube closed form t<=2000: {'OK' if bad == 0 else str(bad) + ' FAILURES'}")

# ---- 4. three_mul_level for d <= 500 ---------------------------------------
bad = 0
for d in range(0, 501):
    if 3 * (8 * ((d * (d * d + 2)) // 3)) != 8 * d**3 + 16 * d:
        bad += 1
    if (d * (d * d + 2)) % 3 != 0:
        print(f"3 does not divide d(d^2+2) at d={d}")
        bad += 1
print(f"[4] three_mul_level / three_dvd d<=500: {'OK' if bad == 0 else str(bad) + ' FAILURES'}")
