# -*- coding: utf-8 -*-
"""331_two_threshold.py -- are the three "degree-2 thresholds" one mechanism?

Object: Rule 129 (all-neighbours-equal) closed form
    x_t(v) = 1 - [ floor((t-norm v)/2) subset of r(t) ],  r(t) = t - 2^floor(log2 t)
    shell(t) = { t-2m, t-2m-1 : m subset of r(t) },      |shell t| = 2 * 2^wt(r)

Three places where a "2" shows up:
  P1  submask moments  P_j(r) = sum_{m subset r} m^j  -> minimal invariant set per j
  P2  arm moments      Phi_D(t) = sum_{m subset r(t)} (t-2m)^D, 2-kernel rank = floor(D/2)+1
  P3  representation coefficients c_l (docs/51, "degree <= 1 rows only see popcount")

Sections
  [0] machinery self-checks
  [1] exact power-sum expansion of P_j/N, j = 0..8   (the minimal invariant sets)
  [2] consistency with the known (r,Q) / P16 data, and the trap of dropping P16
  [3] the "Newton explanation": sufficient but NOT minimal (odd cumulants vanish)
  [4] phenomenon 2: what exactly is the "2" in floor(D/2)+1
  [5] phenomenon 3: exact shape of the coefficients c_l (+ correction of the claim)
  [6] verdict support: P-tower has no parity coupling, Phi-tower has; thresholds

Run:  py -3 scripts/331_two_threshold.py       (~ 11 s)
"""
from fractions import Fraction
from math import comb, factorial, lcm

JMAX = 8
FAIL = [0]

def chk(cond, msg):
    if not cond:
        FAIL[0] += 1
        print("    FAIL " + msg)

def bits(x):
    i = 0
    while x:
        if x & 1:
            yield i
        x >>= 1
        i += 1

def pc(x):
    return bin(x).count("1")

def submasks(r):
    m = r
    while True:
        yield m
        if m == 0:
            return
        m = (m - 1) & r

def r_of(t):
    if t == 0:
        return 0
    return t - (1 << (t.bit_length() - 1))

def s_pow(r, k):
    return sum(1 << (k * i) for i in bits(r))

def rat_str(c):
    if c.denominator == 1:
        return str(c.numerator)
    return "%d/%d" % (c.numerator, c.denominator)

# ------------------------------------------------------------------ [0]
def P_brute(r, j):
    return sum(pow(m, j) for m in submasks(r))

def P_table(L, J):
    """P[r][j] = sum_{m subset r} m^j, by the digit recursion
         P_j(2u)   = 2^j P_j(u)
         P_j(2u+1) = 2^j P_j(u) + sum_i C(j,i) 2^i P_i(u)"""
    P = [[0] * (J + 1) for _ in range(1 << L)]
    P[0][0] = 1
    for r in range(1, 1 << L):
        u = r >> 1
        Pu, Pr = P[u], P[r]
        if r & 1:
            for j in range(J + 1):
                tot = (1 << j) * Pu[j]
                for i in range(j + 1):
                    tot += comb(j, i) * (1 << i) * Pu[i]
                Pr[j] = tot
        else:
            for j in range(J + 1):
                Pr[j] = (1 << j) * Pu[j]
    return P

def sec0():
    print("[0] machinery self-checks")
    Pt = P_table(8, JMAX)
    bad = 0
    for r in range(1 << 8):
        for j in range(JMAX + 1):
            if Pt[r][j] != P_brute(r, j):
                bad += 1
    chk(bad == 0, "digit recursion for P_j vs brute force, r < 256")
    print("    P_j digit recursion == brute force, r < 256, j <= 8: %s" % ("OK" if bad == 0 else "FAIL"))
    # shell = arm u (arm-1), |shell t| = 2*2^wt(r)
    bad = 0
    for t in range(1, 2000):
        r = r_of(t)
        arm = {t - 2 * m for m in submasks(r)}
        sh = arm | {x - 1 for x in arm}
        if len(sh) != 2 * (1 << pc(r)) or len(arm) != 1 << pc(r):
            bad += 1
        if any(x <= 0 for x in arm):
            bad += 1
    chk(bad == 0, "shell = arm disjoint (arm-1), sizes, positivity, t < 2000")
    print("    shell = arm u (arm-1), |shell t| = 2*2^wt(r), arm elements >= 1: %s"
          % ("OK" if bad == 0 else "FAIL"))

# ------------------------------------------------------------------ polys
def zero_mono():
    return tuple([0] * (JMAX + 1))

def mono(m, e=1):
    t = [0] * (JMAX + 1)
    t[m] = e
    return tuple(t)

def pmul(p, q):
    out = {}
    for a, ca in p.items():
        for b, cb in q.items():
            key = tuple(x + y for x, y in zip(a, b))
            out[key] = out.get(key, Fraction(0)) + ca * cb
    return {k: v for k, v in out.items() if v != 0}

def padd(p, q, c=Fraction(1)):
    out = dict(p)
    for k, v in q.items():
        out[k] = out.get(k, Fraction(0)) + c * v
    return {k: v for k, v in out.items() if v != 0}

def pscale(p, c):
    return {k: v * c for k, v in p.items() if v * c != 0}

def log_cosh_coeffs(K):
    """log cosh(u) = sum_{k>=1} b[k] u^(2k);  cosh = sum v^k/(2k)! with v = u^2."""
    a = [Fraction(1, factorial(2 * k)) for k in range(K + 1)]
    b = [Fraction(0)] * (K + 1)
    for n in range(1, K + 1):
        s = Fraction(0)
        for k in range(1, n):
            s += k * b[k] * a[n - k]
        b[n] = a[n] - s / n
    return b

def cumulant_polys(J):
    """K[m] = kappa_m / m!  as a polynomial in the power sums s_1..s_J.
    kappa_1 = s_1/2, kappa_{2k} = (2k)! b[k] / 4^k * s_{2k}, kappa_odd>=3 = 0."""
    b = log_cosh_coeffs(J // 2 + 1)
    K = {1: {mono(1): Fraction(1, 2)}}
    for m in range(3, J + 1, 2):
        K[m] = {}
    for k in range(1, J // 2 + 1):
        m = 2 * k
        a = Fraction(factorial(m)) * b[k] / (4 ** k)
        K[m] = {mono(m): a / factorial(m)}
    return K

def moment_polys(J):
    """P_j / N for j = 0..J, as a dict {exponent tuple: Fraction}."""
    K = cumulant_polys(J)
    g = [dict() for _ in range(J + 1)]
    g[0] = {zero_mono(): Fraction(1)}
    for n in range(1, J + 1):
        acc = {}
        for k in range(1, n + 1):
            if not K.get(k):
                continue
            acc = padd(acc, pmul(K[k], g[n - k]), Fraction(k))
        g[n] = pscale(acc, Fraction(1, n))
    P = [dict() for _ in range(J + 1)]
    P[0] = {zero_mono(): Fraction(1)}
    for j in range(1, J + 1):
        P[j] = pscale(g[j], Fraction(factorial(j)))
    return P

def peval_int(terms, s, N):
    """integer evaluation: terms = {mono: integer}, returns N * sum terms * prod s^e"""
    tot = 0
    for key, c in terms.items():
        v = c
        for m in range(1, JMAX + 1):
            e = key[m]
            if e:
                v *= s[m] ** e
        tot += v
    return N * tot

def int_form(p):
    D = 1
    for c in p.values():
        D = lcm(D, c.denominator)
    return {k: int(v * D) for k, v in p.items()}, D

NAMES = {1: "r", 2: "Q", 4: "P16", 6: "P64", 8: "P256"}

def poly_str(p):
    terms = []
    for key in sorted(p.keys(), key=lambda k: (-sum(k), k)):
        c = p[key]
        parts = []
        for m in range(1, JMAX + 1):
            e = key[m]
            if e:
                parts.append(NAMES[m] if e == 1 else "%s^%d" % (NAMES[m], e))
        mono = "*".join(parts) if parts else "1"
        terms.append((c, mono))
    out = ""
    for i, (c, mono) in enumerate(terms):
        sign = "-" if c < 0 else "+"
        a = -c if c < 0 else c
        body = rat_str(a) if mono == "1" else (mono if a == 1 else "%s*%s" % (rat_str(a), mono))
        if i == 0:
            out = ("-" if c < 0 else "") + body
        else:
            out += " %s %s" % (sign, body)
    return out

# ------------------------------------------------------------------ [1]
def sec1():
    print()
    print("[1] exact expansion of P_j / N in the power sums s_k, j = 0..8")
    print("    s_k(r) = sum_{i in bits r} 2^(k i) ;  s1 = r, s2 = Q, s4 = P16, s6 = P64, s8 = P256")
    POL = moment_polys(JMAX)
    # verify numerically (integer arithmetic) for r < 2^12
    Pt = P_table(12, JMAX)
    bad = 0
    for j in range(JMAX + 1):
        terms, D = int_form(POL[j])
        for r in range(1 << 12):
            s = [0] + [s_pow(r, k) for k in range(1, JMAX + 1)]
            N = 1 << pc(r)
            if peval_int(terms, s, N) != D * Pt[r][j]:
                bad += 1
                break
    chk(bad == 0, "P_j expansion vs digit recursion, r < 4096")
    print("    verified against the digit recursion for r < 4096, j <= 8: %s"
          % ("OK" if bad == 0 else "FAIL"))
    # random large r as a second check
    import random
    random.seed(7)
    bad2 = 0
    for _ in range(300):
        r = random.randrange(0, 1 << 20)
        s = [0] + [s_pow(r, k) for k in range(1, JMAX + 1)]
        N = 1 << pc(r)
        Ps = [P_brute(r, j) for j in range(JMAX + 1)]
        for j in range(JMAX + 1):
            terms, D = int_form(POL[j])
            if peval_int(terms, s, N) != D * Ps[j]:
                bad2 += 1
    chk(bad2 == 0, "P_j expansion on 300 random r < 2^20")
    print("    verified on 300 random r < 2^20: %s" % ("OK" if bad2 == 0 else "FAIL"))
    print()
    print("    P_j / N  (N = 2^wt(r)):")
    for j in range(JMAX + 1):
        print("      j=%d : %s" % (j, poly_str(POL[j])))
    print()
    print("    minimal invariant set (= power sums that really occur):")
    print("      j | P_j/N = polynomial in        | #extra | new at this j")
    prev = set()
    for j in range(JMAX + 1):
        used = set()
        for key, c in POL[j].items():
            for m in range(1, JMAX + 1):
                if key[m]:
                    used.add(m)
        new = used - prev
        prev = used
        print("      %d | %-28s | %d | %s"
              % (j, ",".join("s%d" % m for m in sorted(used)) or "-",
                 len(used), ",".join("s%d" % m for m in sorted(new)) or "-"))
    print()
    print("    number of invariants needed (N counted):  1 + 1 + floor(j/2)")
    for j in range(JMAX + 1):
        used = set()
        for key in POL[j]:
            for m in range(1, JMAX + 1):
                if key[m]:
                    used.add(m)
        print("      j=%d : %d   (N + %s)" % (j, 1 + len(used), ",".join("s%d" % m for m in sorted(used)) or "-"))
    # explicit coefficients of the "new" invariants
    print()
    print("    coefficient of the new invariant s_j (j even) in P_j/N:")
    for j in range(2, JMAX + 1, 2):
        c = POL[j].get(mono(j), Fraction(0))
        print("      j=%d : coeff(s%d) = %s" % (j, j, rat_str(c)))
        chk(c != 0, "s_%d must occur in P_%d" % (j, j))
    return POL

# ------------------------------------------------------------------ [2]
def sec2(POL):
    print()
    print("[2] consistency with the known (r,Q) / P16 data")
    print("    P_2 = N*(%s)" % poly_str(POL[2]))
    print("    P_3 = N*(%s)" % poly_str(POL[3]))
    print("    P_4 = N*(%s)" % poly_str(POL[4]))
    print("    P_5 = N*(%s)" % poly_str(POL[5]))
    print("    P_6 = N*(%s)" % poly_str(POL[6]))
    # P3 : no s3
    used3 = {m for m, e in enumerate(next(iter(POL[3].keys()))) if e}
    chk(3 not in used3, "P_3 must not contain s3")
    used4 = set()
    for key in POL[4]:
        for m, e in enumerate(key):
            if e:
                used4.add(m)
    chk(4 in used4 and 3 not in used4, "P_4 uses s4 (P16) and not s3")
    print("    every s_m occurring in P_3: %s ; in P_4: %s"
          % (sorted(used3), sorted(used4)))
    # dropping the P16 term in P_4: how many r go wrong
    terms, D = int_form(POL[4])
    drop = {k: v for k, v in terms.items() if not k[4]}
    bad = 0
    first = None
    for r in range(1 << 12):
        s = [0] + [s_pow(r, k) for k in range(1, JMAX + 1)]
        N = 1 << pc(r)
        if peval_int(drop, s, N) != D * P_brute(r, 4):
            bad += 1
            if first is None:
                first = r
    print("    P_4 with the P16 monomial deleted: wrong for %d of 4096 r (first r = %s)"
          % (bad, first))
    chk(bad > 0, "deleting P16 must break P_4")
    # same for P_6 without P64
    terms6, D6 = int_form(POL[6])
    drop6 = {k: v for k, v in terms6.items() if not k[6]}
    bad6 = 0
    for r in range(1 << 12):
        s = [0] + [s_pow(r, k) for k in range(1, JMAX + 1)]
        N = 1 << pc(r)
        if peval_int(drop6, s, N) != D6 * P_brute(r, 6):
            bad6 += 1
    print("    P_6 with the P64 monomial deleted: wrong for %d of 4096 r" % bad6)
    chk(bad6 > 0, "deleting P64 must break P_6")

# ------------------------------------------------------------------ [3]
def sec3(POL):
    print()
    print("[3] the 'Newton explanation' -- sufficient, but not minimal")
    print("    Newton: e_j in Q[s_1..s_j], and P_j is symmetric of degree j,")
    print("    so P_j in Q[s_1..s_j].  Prediction of the naive reading:")
    print("    'P_j needs s_1..s_j' -- i.e. s_3 = P8 = sum 2^(3i) at j = 3.")
    print()
    print("    reality (from [1]): the odd power sums s_3,s_5,s_7 never occur.")
    print("    reason: log E[e^(zW)] = z s_1/2 + sum_i log cosh(z 2^i/2), and")
    print("            log cosh is even  ==>  kappa_m = 0 for odd m >= 3,")
    print("            kappa_{2k} = (2k)! b_k / 4^k * s_{2k}  (b_k != 0).")
    print("            Odd cumulants die because the Bernoulli(1/2) is symmetric")
    print("            about its mean, i.e. because m -> r-m is a bijection.")
    print()
    print("    j | naive set s_1..s_j | minimal set      | difference (not needed)")
    for j in range(JMAX + 1):
        used = set()
        for key in POL[j]:
            for m in range(1, JMAX + 1):
                if key[m]:
                    used.add(m)
        naive = set(range(1, j + 1))
        print("    %d | %-17s | %-16s | %s"
              % (j, "s1..s%d" % j if j else "-",
                 ",".join("s%d" % m for m in sorted(used)) or "-",
                 ",".join("s%d" % m for m in sorted(naive - used)) or "-"))
    # the cumulant table: only even orders survive (m = 1 excepted)
    print()
    print("    kappa_m / s_m  (the coefficient of the NEW invariant at j = m):")
    b = log_cosh_coeffs(4)
    line = []
    for m in range(1, 9):
        if m == 1:
            v = Fraction(1, 2)
        elif m % 2 == 1:
            v = Fraction(0)
        else:
            v = Fraction(factorial(m)) * b[m // 2] / (4 ** (m // 2))
        line.append("m=%d:%s" % (m, rat_str(v)))
    print("      " + "  ".join(line))
    # algebraic independence certificate: the linear forms s_1..s_8 restricted to
    # the bits 0..7 form a Vandermonde matrix with nodes 2^1..2^8
    det = 1
    for i in range(1, 9):
        for j in range(i + 1, 9):
            det *= (1 << j) - (1 << i)
    print("    s_1..s_8 on bits 0..7: Vandermonde det = prod (2^j - 2^i) != 0 -> %s"
          % ("OK" if det != 0 else "FAIL"))
    chk(det != 0, "s_1..s_8 linearly independent on bits 0..7")
    # the naive prediction is falsified at j = 3 by the explicit formula
    print()
    print("    so the naive Newton reading fails first at j = 3: it predicts")
    print("    s_3 = sum 4^(i)*2^i = sum 8^i is needed, but P_3 = N*(%s)." % poly_str(POL[3]))
    # check: is s_3 independent of s1,s2?  yes (Vandermonde on bit sets)
    print("    (s_3 is a genuine independent invariant -- it is simply not used.)")

# ------------------------------------------------------------------ [4]
def phi_values(Dmax, Tmax):
    tab = [[0] * (Tmax + 1) for _ in range(Dmax + 1)]
    for t in range(Tmax + 1):
        r = r_of(t)
        for m in submasks(r):
            x = t - 2 * m
            p = 1
            for D in range(Dmax + 1):
                tab[D][t] += p
                p *= x
    return tab

def M0m(i, l):
    return (1 << i) if i == l else 0

def M1m(i, l):
    if l <= i and (l - i) % 2 == 0:
        return comb(i, l) * (1 << (l + 1))
    return 0

def M1c(i, l):
    """control: the pair {2y, 2y+2} instead of {2y-1, 2y+1}.
    (2y)^i + (2y+2)^i = sum_{l<i} C(i,l) 2^i y^l + 2^(i+1) y^i   -- full coupling"""
    if l > i:
        return 0
    return comb(i, l) * (1 << i) * (2 if l == i else 1)

def rank_q(rows, ncols):
    basis = []
    for v in rows:
        row = [Fraction(x) for x in v]
        for piv, b in basis:
            if row[piv]:
                f = row[piv] / b[piv]
                for i in range(piv, ncols):
                    row[i] -= f * b[i]
        piv = -1
        for i in range(ncols):
            if row[i]:
                piv = i
                break
        if piv < 0:
            continue
        f = row[piv]
        row = [x / f for x in row]
        basis.append((piv, row))
    return len(basis)

def kernel_vectors(f, K, M):
    """2-kernel: t -> f(2^k n + j), n = 1..M (the transfer theorem needs n >= 1)."""
    vecs = []
    for k in range(K + 1):
        base = 1 << k
        for j in range(base):
            vecs.append(tuple(f(base * n + j) for n in range(1, M + 1)))
    return vecs

def sec4():
    print()
    print("[4] phenomenon 2: the 2-kernel rank of Phi_D is floor(D/2)+1 -- which 2?")
    K, M = 7, 40
    Tmax = (1 << K) * (M + 1) + (1 << K)
    tab = phi_values(JMAX, Tmax)
    # (a) transfer laws   (the recursions need u >= 1, i.e. t >= 2 even / t >= 3 odd)
    bad = 0
    for t in range(2, 301):
        u = t >> 1
        if t % 2 == 0:
            for D in range(JMAX + 1):
                if tab[D][t] != (1 << D) * tab[D][u]:
                    bad += 1
        else:
            for D in range(JMAX + 1):
                rhs = sum(comb(D, i) * (1 << (i + 1)) * tab[i][u]
                          for i in range(D + 1) if (i - D) % 2 == 0)
                if tab[D][t] != rhs:
                    bad += 1
    chk(bad == 0, "transfer laws for Phi_k, t < 301")
    print("    Phi_k(2u) = 2^k Phi_k(u) ;  Phi_k(2u+1) = sum_{i<k, i=k mod 2} C(k,i)2^(i+1)Phi_i(u): %s"
          % ("OK" if bad == 0 else "FAIL"))
    print("    (the second law couples only orders of the SAME PARITY)")
    # (b) upper bound: column support, parity
    bad = 0
    for k in range(0, 7):
        for r in range(1 << k):
            A = [[1 if i == l else 0 for l in range(JMAX + 1)] for i in range(JMAX + 1)]
            rr = r
            for _ in range(k):
                Mx = (lambda i, l: M0m(i, l)) if (rr & 1) == 0 else (lambda i, l: M1m(i, l))
                A = [[sum(A[i][m] * Mx(m, l) for m in range(JMAX + 1))
                      for l in range(JMAX + 1)] for i in range(JMAX + 1)]
                rr >>= 1
            for i in range(JMAX + 1):
                for l in range(JMAX + 1):
                    if A[i][l] != 0 and not (l <= i and (i - l) % 2 == 0):
                        bad += 1
    chk(bad == 0, "column support of A: l <= i and l = i mod 2")
    print("    A(k,r)[i][l] = 0 unless l <= i and l = i (mod 2): %s  (this is the upper bound)"
          % ("OK" if bad == 0 else "FAIL"))
    # (c) measured ranks
    print()
    print("    D | rank K=6,M=40 | rank K=7,M=40 | floor(D/2)+1 | chain {l <= D, l = D mod 2}")
    ranks = {}
    for D in range(JMAX + 1):
        r6 = rank_q(kernel_vectors(lambda t: tab[D][t], 6, M), M)
        r7 = rank_q(kernel_vectors(lambda t: tab[D][t], 7, M), M)
        ranks[D] = r7
        chk(r7 == D // 2 + 1, "rank(Phi_%d) = floor(D/2)+1" % D)
        print("    %d | %d | %d | %d | %s"
              % (D, r6, r7, D // 2 + 1,
                 ",".join(str(l) for l in range(D, -1, -2))))
    # containment: kernel of Phi_D inside span{Phi_l : l = D mod 2, l <= D}
    print()
    bad = 0
    for D in range(1, JMAX + 1):
        cls = [l for l in range(D, -1, -2)]
        base = []
        for l in cls:
            base += kernel_vectors(lambda t, l=l: tab[l][t], 7, M)
        r_base = rank_q(base, M)
        r_union = rank_q(base + kernel_vectors(lambda t: tab[D][t], 7, M), M)
        if r_base != len(cls) or r_union != r_base:
            bad += 1
        print("    D=%d : rank(Phi_l, l in chain) = %d (= #chain) ; adding Phi_%d's kernel -> %d"
              % (D, r_base, D, r_union))
    chk(bad == 0, "kernel(Phi_D) contained in span of the same-parity chain")
    # (d) the mechanism: (c+1)^D + (c-1)^D keeps only powers of parity D
    bad = 0
    for D in range(JMAX + 1):
        for c in range(-15, 16):
            lhs = (c + 1) ** D + (c - 1) ** D
            rhs = 2 * sum(comb(D, i) * c ** i for i in range(D + 1) if (D - i) % 2 == 0)
            if lhs != rhs:
                bad += 1
    chk(bad == 0, "(c+1)^D+(c-1)^D parity identity")
    print()
    print("    the mechanism: (c+1)^D + (c-1)^D = 2 * sum_{i = D (2)} C(D,i) c^i")
    print("    i.e. the pair {c-1,c+1} is symmetric about c, so the ODD part in c dies.")
    print("    verified for D <= 8, |c| <= 15: %s" % ("OK" if bad == 0 else "FAIL"))
    # (e) control: pair {2y, 2y+2} (no +-1 symmetry) -> full coupling
    print()
    print("    control experiment: replace the symmetric pair {2y-1,2y+1} by {2y,2y+2}")
    print("    (same size, but not symmetric): then all orders l <= i couple, and")
    Tctrl = (1 << K) * (M + 1) + (1 << K)
    print("    D | rank (control) | rank (true Phi_D) | D+1")
    for D in range(0, JMAX + 1):
        ys = [None] * (Tctrl + 1)
        ys[0] = [1] * (D + 1)
        for t in range(1, Tctrl + 1):
            u = t >> 1
            v = ys[u]
            if t % 2 == 0:
                ys[t] = [(1 << i) * v[i] for i in range(D + 1)]
            else:
                ys[t] = [sum(M1c(i, l) * v[l] for l in range(i + 1)) for i in range(D + 1)]
        vals = [0] * (Tctrl + 1)
        for t in range(Tctrl + 1):
            vals[t] = ys[t][D]
        rc = rank_q(kernel_vectors(lambda t: vals[t], 7, M), M)
        print("    %d | %d | %d | %d" % (D, rc, D // 2 + 1, D + 1))
        if D >= 2:
            chk(rc > D // 2 + 1, "control rank must exceed floor(D/2)+1 at D=%d" % D)
    return ranks

# ------------------------------------------------------------------ [5]
def Amat(J, k, r):
    A = [[1 if i == l else 0 for l in range(J + 1)] for i in range(J + 1)]
    rr = r
    for _ in range(k):
        Mx = (lambda i, l: M0m(i, l)) if (rr & 1) == 0 else (lambda i, l: M1m(i, l))
        A = [[sum(A[i][m] * Mx(m, l) for m in range(J + 1)) for l in range(J + 1)]
             for i in range(J + 1)]
        rr >>= 1
    return A

ROWS = [
    ("Z^1 line", [4]),
    ("Z^1 ray", [2]),
    ("Z^2 vN", [-4, 8]),
    ("Z^2 Moore", [-8, 16]),
    ("Z^2 triangular", [-6, 12]),
    ("Z^2 quarter vN", [1, 2]),
    ("Z^2 quarter Moore", [0, 4]),
    ("Z^3 vN", [8, -8, 8]),
    ("Z^3 Moore", [28, -48, 48]),
    ("Z^4 Moore", [-80, 224, -192, 128]),
    ("Z^4 vN (3x)", [-24, 56, -24, 16]),
    ("Z^5 Moore", [244, -800, 1120, -640, 320]),
    ("Z^5 vN (3x)", [36, -56, 64, -16, 8]),
]

def sec5():
    print()
    print("[5] phenomenon 3: the exact shape of the representation coefficients c_l")
    J = 4
    # (a) three structural facts about A
    bad_diag = bad_sup = 0
    for k in range(0, 7):
        for r in range(1 << k):
            A = Amat(J, k, r)
            w = pc(r)
            for i in range(J + 1):
                for l in range(J + 1):
                    if A[i][l] != 0 and not (l <= i and (i - l) % 2 == 0):
                        bad_sup += 1
            for l in range(J + 1):
                if A[l][l] != (1 << (l * k + w)):
                    bad_diag += 1
    chk(bad_sup == 0 and bad_diag == 0, "A structure facts")
    print("    (i)   A[i][l] = 0 unless l <= i and l = i (mod 2)     violations: %d" % bad_sup)
    print("    (ii)  A[l][l] = 2^(l*k + wt(r))  (diagonal)           violations: %d" % bad_diag)
    print("    so c_l = gamma_l * 2^(l*k+wt) + sum_{i>=l+2, i=l(2)} gamma_i * A[i][l]")
    # (b) superset check: X(t) = A X(n) with X(1) = (1,...,1)
    bad = 0
    for k in range(0, 5):
        for r in range(1 << k):
            A = Amat(J, k, r)
            for n in range(1, 21):
                t = (1 << k) * n + r
                Xn = [sum((n - 2 * mm) ** m for mm in submasks(r_of(n))) for m in range(J + 1)]
                for l in range(J + 1):
                    rhs = sum(A[l][m] * Xn[m] for m in range(J + 1))
                    if rhs != sum((t - 2 * mm) ** l for mm in submasks(r_of(t))):
                        bad += 1
    chk(bad == 0, "X(2^k n + r) = A(k,r) X(n)")
    print("    (iii) X(2^k n + r) = A(k,r) X(n), X(1) = (1,...,1)      violations: %d" % bad)
    # (c) the clean/polluted criterion, per row
    print()
    print("    c_l is popcount-only (for fixed k)  <=>  gamma_i = 0 for all i >= l+2, i = l (mod 2)")
    print("    row               D | clean l values | polluted l values | highest two orders")
    for name, gam in ROWS:
        D = len(gam) - 1
        J2 = D
        gam = list(gam) + [0] * (J2 - D)
        clean, dirty = [], []
        for l in range(J2 + 1):
            cond = all(gam[i] == 0 for i in range(l + 2, J2 + 1) if (i - l) % 2 == 0)
            ok = True
            for k in range(0, 7):
                for r in range(1 << k):
                    A = Amat(J2, k, r)
                    c = sum(gam[i] * A[i][l] for i in range(J2 + 1))
                    pred = gam[l] * (1 << (l * k + pc(r)))
                    if c != pred:
                        ok = False
                        break
                if not ok:
                    break
            if cond:
                chk(ok, "clean prediction for %s l=%d" % (name, l))
                clean.append(l)
            else:
                chk(not ok, "dirty prediction for %s l=%d" % (name, l))
                dirty.append(l)
        print("    %-16s %d | %-14s | %-17s | %s"
              % (name, D, ",".join(map(str, clean)), ",".join(map(str, dirty)) or "-",
                 "%d,%d" % (D, D - 1) if D >= 1 else "%d" % D))
    # (d) the concrete counterexample: Z^3 vN, k = 5
    print()
    print("    counterexample to the literal claim 'l <= 1 only sees popcount':")
    gam = [8, -8, 8]
    k = 5
    print("    Z^3 vN, gamma = (8,-8,8), k = 5:")
    print("      r   wt | c_0    c_1     c_2   | A[2][0]")
    for r in [0, 3, 5, 6, 12]:
        A = Amat(2, k, r)
        c = [sum(gam[i] * A[i][l] for i in range(3)) for l in range(3)]
        print("      %2d  %2d | %-6d %-7d %-6d | %d" % (r, pc(r), c[0], c[1], c[2], A[2][0]))
    print("    -> c_1 and c_2 only see wt, but c_0 does NOT (192 vs 2592 at wt = 2).")
    print("       (c_2 = gamma_2 * 2^(2k+wt) is clean because gamma_4 = 0 is absent;")
    print("        c_0 is polluted because gamma_2 = 8 != 0 and A[2][0] != 0.)")
    gam4 = [-80, 224, -192, 128]
    print()
    print("    and for a degree-3 row c_1 is polluted too: Z^4 Moore, k = 5")
    print("      r   wt | c_1     | A[3][1]")
    for r in [3, 5, 6, 12]:
        A = Amat(3, k, r)
        c1 = sum(gam4[i] * A[i][1] for i in range(4))
        print("      %2d  %2d | %-8d | %d" % (r, pc(r), c1, A[3][1]))
    return

# ------------------------------------------------------------------ [6]
def sec6(POL):
    print()
    print("[6] verdict support")
    # (a) the P-tower digit recursion has NO parity coupling
    print("    (a) P_j(2u+1) = sum_{i=0..j} C(j,i) 2^i P_i(u) + 2^j P_j(u):")
    print("        every i = 0..j couples (all coefficients are non-zero):")
    for j in range(1, 7):
        coeffs = [comb(j, i) * (1 << i) for i in range(j)]
        print("        j=%d : P_i coeffs i=0..%d = %s ; i=j coeff = %d"
              % (j, j - 1, coeffs, (1 << (j + 1))))
    print("    contrast: M1 keeps only i = k (mod 2).")
    print("    => the parity that matters in P1 is NOT the parity of the transfer.")
    # (b) the reflection behind P1: m -> r-m
    bad = 0
    for r in range(1 << 12):
        for e in range(1, 10, 2):
            if sum((2 * m - r) ** e for m in submasks(r)) != 0:
                bad += 1
    chk(bad == 0, "complement symmetry kills odd central moments")
    print()
    print("    (b) the reflection behind P1: m -> r-m is a bijection of subm(r), so")
    print("        sum_{m subset r} (2m-r)^e = 0 for every odd e  (checked r < 4096, e <= 9): %s"
          % ("OK" if bad == 0 else "FAIL"))
    print("        => only even central moments survive => only even cumulants survive")
    print("        => only even power sums s_{2k} are needed.")
    # (c) P and Phi are triangularly related
    bad = 0
    for t in range(1, 301):
        r = r_of(t)
        for j in range(JMAX + 1):
            lhs = sum((t - 2 * m) ** j for m in submasks(r))
            rhs = sum(comb(j, i) * t ** (j - i) * (-2) ** i * P_brute(r, i) for i in range(j + 1))
            if lhs != rhs:
                bad += 1
    chk(bad == 0, "Phi_j = sum_i C(j,i) t^(j-i) (-2)^i P_i")
    print()
    print("    (c) Phi_j(t) = sum_i C(j,i) t^(j-i) (-2)^i P_i(r(t)), t < 301, j <= 8: %s"
          % ("OK" if bad == 0 else "FAIL"))
    print("        the two towers carry the SAME information (triangular, diagonal (-2)^j),")
    print("        yet their digit recursions have different parity structure.")
    # (d) the three thresholds, side by side
    print()
    print("    (d) the three thresholds, on their own indices")
    print("        P1: first j with a new invariant: ", end="")
    prev = set()
    news = []
    for j in range(JMAX + 1):
        used = set()
        for key in POL[j]:
            for m in range(1, JMAX + 1):
                if key[m]:
                    used.add(m)
        if used - prev:
            news.append((j, sorted(used - prev)))
        prev = used
    print(", ".join("j=%d adds s%d" % (j, s[0]) for j, s in news))
    print("        P2: rank(D) - rank(D-1) = 1 iff D even; the chain is D, D-2, D-4, ...")
    print("        P3: smallest polluted order l is D-2 (needs gamma_D != 0), i.e. distance 2")
    print()
    print("    (e) 'position' enters the P-tower ALREADY at j = 2 (so P1's j=3|4 line is")
    print("        not about quadratic terms): Q = s_2 is itself positional")
    for r in (3, 5, 6, 9, 10, 12):
        N = 1 << pc(r)
        print("        r=%2d  wt=%d  Q=%3d  P16=%4d  P_2=%4d  P_3=%6d"
              % (r, pc(r), s_pow(r, 2), s_pow(r, 4), P_brute(r, 2), P_brute(r, 3)))

def main():
    sec0()
    POL = sec1()
    sec2(POL)
    sec3(POL)
    sec4()
    sec5()
    sec6(POL)
    print()
    print("FAIL count: %d" % FAIL[0])

if __name__ == "__main__":
    main()
