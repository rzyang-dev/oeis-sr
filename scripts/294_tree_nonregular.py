"""Script 294 -- the trees are not 2-regular (modular version).

The tree counts grow like b^(t/2), so exact rational elimination is far too
slow; we work modulo a 61-bit prime instead.  A reduction mod p can only
LOWER the rank, so a mod-p rank that grows forces the rational rank to grow.

p = 2^61 - 1 (a Mersenne prime).
"""
P = (1 << 61) - 1

def inv(x):
    return pow(x, P - 2, P)

def rank_mod(matrix, ncol):
    rows = [row[:ncol] for row in matrix]
    m = len(rows)
    rk = 0
    for col in range(ncol):
        piv = None
        for i in range(rk, m):
            if rows[i][col] % P != 0:
                piv = i
                break
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        pv = inv(rows[rk][col] % P)
        rka = rows[rk]
        for i in range(rk + 1, m):
            c = rows[i][col] % P
            if c:
                f = c * pv % P
                ri = rows[i]
                for j in range(col, ncol):
                    ri[j] = (ri[j] - f * rka[j]) % P
        rk += 1
        if rk == m:
            break
    return rk

def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def wt(n):
    return bin(n).count("1")

def bits(m):
    return [i for i in range(m.bit_length()) if (m >> i) & 1]

def Qm(m):
    return sum(pow(4, i, P) for i in bits(m)) % P

def tree_mod(t, b):
    if t == 0:
        return 1
    rt = r(t)
    p = 1
    for i in bits(rt):
        p = p * (1 + pow(b, 2 ** (i + 1), P)) % P
    return (b + 1) % P * pow(b, t - 1 - 2 * rt, P) % P * p % P

def cardS(t):
    return pow(2, wt(t), P)

def sigma_mod(t):
    return cardS(t) * ((2 * t - 1 - 2 * r(t)) % P) % P

def M2_mod(t):
    rt = r(t); K = t - rt
    return cardS(t) * ((2 * K * (K - 1) + 2 * Qm(rt) + 1) % P) % P

def M3_mod(t):
    rt = r(t); k = t - rt - 1; q = Qm(rt)
    return cardS(t) * ((2 * k ** 3 + 3 * k ** 2 + 3 * k + 1 + 3 * q * (2 * k + 1)) % P) % P

def krank(values, KMAX, M, KMIN=2):
    out = []
    for K in range(KMIN, KMAX + 1):
        elems = []
        for k in range(K + 1):
            for j in range(1 << k):
                elems.append([values[(1 << k) * n + j] for n in range(1, M + 1)])
        out.append(rank_mod(elems, M))
    return out

M = 60
KMAX = 9
needed = (1 << KMAX) * (M + 2) + 4
print(f"mod p = 2^61-1, M = {M}, K = 2..{KMAX}, {needed} terms")
print()
print("A. trees: the rank keeps growing (so the counts are NOT 2-regular)")
for b in (2, 3, 4):
    vals = [tree_mod(t, b) for t in range(needed + 1)]
    print(f"   b = {b}: {krank(vals, KMAX, M)}")
print()
print("B. control, c(d) = d^j (flat at j+1)")
for name, fn in (("d", sigma_mod), ("d^2", M2_mod), ("d^3", M3_mod)):
    vals = [fn(t) if t else 0 for t in range(needed + 1)]
    print(f"   {name}: {krank(vals, KMAX, M)}")
print()
print("C. controls for the method itself")
vals = [pow(2, wt(t), P) for t in range(needed + 1)]
print("   2^wt (2-regular, rank 1):", krank(vals, KMAX, M))
vals = [wt(t) * pow(2, wt(t), P) % P for t in range(needed + 1)]
print("   wt*2^wt (should grow):   ", krank(vals, KMAX, M))
