"""281_shell_square_sum.py -- the second moment of the shell.

   S2(r) = sum_{m subset r} m^2      = N*(r^2 + Q)/4
   T2(t) = sum_{d in S(t)} d^2      = N*(2K^2 - 2K + 2Q + 1)

with N = #subm(r) = 2^popcount(r), Q = sum_{i in bits r} 4^i, K = t - r(t).
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

bad = 0
for m in range(0, 301):
    N = len(subm(m)); Q = sum(4 ** i for i in bits(m))
    lhs = sum(x * x for x in subm(m))
    if 4 * lhs != N * (m * m + Q):
        bad += 1
        print("S2 mismatch m =", m, lhs, N * (m * m + Q) // 4)
print("S2(r) = N(r^2+Q)/4 for r <= 300:", "0 mismatches" if bad == 0 else "%d mismatches" % bad)

bad = 0
for t in range(1, 301):
    rt = r(t); N = len(subm(rt)); Q = sum(4 ** i for i in bits(rt)); K = t - rt
    lhs = sum(d * d for d in shell(t))
    rhs = N * (2 * K * K - 2 * K + 2 * Q + 1)
    if lhs != rhs:
        bad += 1
        if bad < 6:
            print("T2 mismatch t =", t, lhs, rhs)
print("T2(t) = N(2K^2-2K+2Q+1) for t <= 300:", "0 mismatches" if bad == 0 else "%d mismatches" % bad)

print()
print(" t   S(t)                  sum d^2   formula")
for t in [1, 2, 3, 5, 7, 8, 15, 16, 21]:
    rt = r(t); N = len(subm(rt)); Q = sum(4 ** i for i in bits(rt)); K = t - rt
    print("%3d   %-20s   %-8d  %d" % (t, str(shell(t))[:20], sum(d*d for d in shell(t)), N*(2*K*K-2*K+2*Q+1)))

print()
print("Z^3 von Neumann zeros = 4*T2 + 2*(#S - eps) + eps:")
for t in range(1, 13):
    rt = r(t); N = len(subm(rt)); Q = sum(4 ** i for i in bits(rt)); K = t - rt
    T2 = N * (2 * K * K - 2 * K + 2 * Q + 1)
    S = shell(t); eps = 1 if 0 in S else 0
    cnt = 4 * T2 + 2 * (len(S) - eps) + eps
    direct = sum((1 if d == 0 else 4 * d * d + 2) for d in S)
    print("  t=%2d  closed=%5d  direct=%5d" % (t, cnt, direct))
