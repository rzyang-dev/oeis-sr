"""283_third_moments.py -- the third moments.

   sum_{m subset r} m^3   = N*(r^3 + 3 Q r)/8
   sum_{d in S(t)} d^3   = N*(2K^3 - 3K^2 + 3K - 1 + 3Q(2K-1))
   Z^4 von Neumann: c_d = 8d(d^2+2)/3  ->  3*zeros = 8*(M3 + 2 sigma) + 3 eps
   Z^4 Moore:       c_d = 64d^3 + 16d  ->  zeros = 64 M3 + 16 sigma + eps
"""

def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def bits(m):
    return [i for i in range(m) if (m >> i) & 1]

def subm(m):
    return [x for x in range(m + 1) if x & m == x]

def shell(t):
    rt = r(t)
    return [d for d in range(t + 1) if ((t - d) // 2) & rt == (t - d) // 2]

def Q(m):
    return sum(4 ** i for i in bits(m))

def N(m):
    return 1 << len(bits(m))

bad = 0
for m in range(0, 301):
    lhs = sum(x ** 3 for x in subm(m))
    if 8 * lhs != N(m) * (m ** 3 + 3 * Q(m) * m):
        bad += 1
        if bad < 5: print("S3 mismatch m =", m, lhs, N(m) * (m ** 3 + 3 * Q(m) * m) // 8)
print("sum m^3 = N(r^3+3Qr)/8 for r <= 300:", "0 mismatches" if bad == 0 else str(bad))

bad = 0
for t in range(1, 301):
    rt = r(t); K = t - rt; q = Q(rt); n = N(rt)
    lhs = sum(d ** 3 for d in shell(t))
    rhs = n * (2 * K ** 3 - 3 * K ** 2 + 3 * K - 1 + 3 * q * (2 * K - 1))
    if lhs != rhs:
        bad += 1
        if bad < 5: print("M3 mismatch t =", t, lhs, rhs)
print("sum_{d in S} d^3 = N(2K^3-3K^2+3K-1+3Q(2K-1)) for t <= 300:", "0 mismatches" if bad == 0 else str(bad))

def gamma4(d):
    return 1 if d == 0 else (8 * d * (d * d + 2)) // 3

def moore4(d):
    return 1 if d == 0 else 64 * d ** 3 + 16 * d

bad = 0
for t in range(1, 201):
    rt = r(t); K = t - rt; q = Q(rt); n = N(rt)
    S = shell(t)
    M3 = n * (2 * K ** 3 - 3 * K ** 2 + 3 * K - 1 + 3 * q * (2 * K - 1))
    sig = n * (2 * t - 1 - 2 * rt)
    eps = 1 if 0 in S else 0
    if 3 * sum(gamma4(d) for d in S) != 8 * (M3 + 2 * sig) + 3 * eps:
        bad += 1; print("Z4 vN mismatch", t)
    if sum(moore4(d) for d in S) != 64 * M3 + 16 * sig + eps:
        bad += 1; print("Z4 Moore mismatch", t)
print("Z^4 von Neumann (3x form) and Moore closed forms, t <= 200:", "0 mismatches" if bad == 0 else str(bad))

print()
print(" t  M3        gamma4 zeros   moore4 zeros")
for t in range(1, 11):
    rt = r(t); K = t - rt; q = Q(rt); n = N(rt)
    S = shell(t)
    print("%2d  %-9d %-14d %-14d" % (t, sum(d**3 for d in S), sum(gamma4(d) for d in S), sum(moore4(d) for d in S)))
