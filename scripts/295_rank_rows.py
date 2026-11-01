from fractions import Fraction as F

def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

def wt(n):
    return bin(n).count("1")

def bits(m):
    return [i for i in range(m.bit_length()) if (m >> i) & 1]

def shell(t):
    rt = r(t)
    return [d for d in range(t + 1) if ((t - d) // 2) & rt == (t - d) // 2]

def rank(matrix, ncol):
    rows = [row[:ncol] for row in matrix]
    m = len(rows); rk = 0
    for col in range(ncol):
        piv = None
        for i in range(rk, m):
            if rows[i][col] != 0:
                piv = i; break
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        pv = F(rows[rk][col])
        for i in range(rk + 1, m):
            if rows[i][col] != 0:
                f = F(rows[i][col]) / pv
                for j in range(col, ncol):
                    rows[i][j] = F(rows[i][j]) - f * F(rows[rk][j])
        rk += 1
        if rk == m:
            break
    return rk

def krank(a, KMAX, M):
    needed = (1 << KMAX) * (M + 2) + 4
    vals = [a(t) for t in range(needed + 1)]
    out = []
    for K in range(3, KMAX + 1):
        elems = []
        for k in range(K + 1):
            for j in range(1 << k):
                elems.append([vals[(1 << k) * n + j] for n in range(1, M + 1)])
        out.append(rank(elems, M))
    return out

def zc(c):
    return lambda t: sum(c(d) for d in shell(t))

tests = {
    "Z^5 von Neumann  (deg 4, patch)": zc(lambda d: 1 if d == 0 else (4*d**4 + 20*d*d + 6)//3),
    "Z^5 Moore        (deg 4, patch)": zc(lambda d: 1 if d == 0 else 160*d**4 + 80*d*d + 2),
    "Z^4 von Neumann  (deg 3, patch)": zc(lambda d: 1 if d == 0 else 8*d*(d*d+2)//3),
    "Z^2 orthant vN   (deg 1, none) ": zc(lambda d: d + 1),
    "Z^3 Moore        (deg 2, patch)": zc(lambda d: 1 if d == 0 else 24*d*d + 2),
}
for name, a in tests.items():
    print(f"{name}: {krank(a, 7, 40)}")
