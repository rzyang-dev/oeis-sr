#!/usr/bin/env python3
"""Script 321 -- 2-kernel rank of the "all neighbours equal" zero-count sequence.

Z_c(t) = sum_{d in shell t} c_d,   shell t = {t - 2m, t - 2m - 1 : m subset r t},
r t = t - 2^floor(log2 t).

Goal: turn the *observed* law  rank(Z_c) = deg(c) + 1 + [centre correction]
into a reliable statement.  Five things are done here:

 [1]  a reliable rank meter: exact rational Gaussian elimination on the first M
      values of every kernel element  n -> a(2^k n + j),  k <= K,  j < 2^k,
      reported separately for K = 4,5,6,7 (flat profile = converged);
 [2]  numeric re-check of the Lean transfer identity
          Z_c(2^k n + j) = sum_l (A(k,j)^T p)_l Phi_l(n) + delta*[j=2^k-1]*eps(n),
      with p(x) = c(x) + c(x-1) and the arm-moment matrices M0, M1;
 [3]  full census of the polynomial conjecture
          rank(Z_c) = #{i : [x^i] p != 0}                       (naive form)
          rank(Z_c) = #Dclosure(supp p) + [delta != 0]          (refined form)
      on *all* polynomials of degree <= 3 with coefficients in [-2,2] and on
      320 random polynomials of degree <= 6 with coefficients in [-6,6];
 [4]  the centre-corrected version (c_0 forced away from the polynomial value);
 [5]  non-polynomial 2-regular layer functions (popcount, Thue-Morse, periodic,
      floor(d^1.585), ...) together with rank(c) vs rank(Z_c);
 [6]  the lower-bound mechanism: the moment tower (Phi_0..Phi_D, eps) is
      independent, rank(Z_c) = dim span{A(k,j)^T p}, and #supp <= rank <= #Dclosure.

Everything is exact integer / rational arithmetic; no floating point is used
anywhere except in floor(d^1.585) where the value is the integer floor.
"""

from fractions import Fraction
from math import comb
import random
import time

T0 = time.time()

# ============================================================ 0. basic objects

def r_of(t):
    """r(t) = t - 2^floor(log2 t) for t >= 1; r(0) = 0."""
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))


def wt(n):
    return bin(n).count("1")


def submasks(rt):
    """all submasks of rt (including 0 and rt), by the standard (m-1)&rt walk."""
    out = []
    m = rt
    while True:
        out.append(m)
        if m == 0:
            return out
        m = (m - 1) & rt


def arm(t):
    """arm t = {t - 2m : m subset r t};  every entry is >= 1 when t >= 1."""
    return [t - 2 * m for m in submasks(r_of(t))]


def shell(t):
    """shell t = arm t  union  (arm t - 1)  (disjoint: arm is one parity)."""
    out = []
    for x in arm(t):
        out.append(x)
        out.append(x - 1)
    return out


def Phi(k, t):
    """arm moment  Phi_k(t) = sum_{x in arm t} x^k."""
    return sum(x ** k for x in arm(t))


def eps(t):
    """eps(t) = [0 in shell t]  <=>  t+1 is a power of two."""
    return 1 if (t & (t + 1)) == 0 else 0


# ---------------------------------------------------------- fast value engine
# Z_c(t) = sum_{d in shell t} c_d = sum_{x in arm t} (c(x) + c(x-1)), the second
# form is Lean's shell_sum_pair and halves the number of lookups.

_IDX = []       # _IDX[t] = tuple(t - 2m for m subset r t)


def prepare(nmax):
    global _IDX
    _IDX = [None] * (nmax + 1)
    for t in range(nmax + 1):
        _IDX[t] = tuple(t - 2 * m for m in submasks(r_of(t)))


def z_values(cvec):
    """cvec[d] = c_d for d <= NMAX;  returns [Z_c(0), Z_c(1), ...]."""
    h = [cvec[x] + (cvec[x - 1] if x >= 1 else 0) for x in range(len(cvec))]
    get = h.__getitem__
    out = [0] * len(cvec)
    for t in range(1, len(cvec)):
        out[t] = sum(map(get, _IDX[t]))
    return out


_POW = {}


def powlist(i, nmax):
    L = _POW.get(i)
    if L is None or len(L) <= nmax:
        L = [d ** i for d in range(nmax + 1)]
        _POW[i] = L
    return L


def cvec_from_poly(P, c0, nmax):
    """c_d = P(d) for d >= 1 and c_0 = c0."""
    out = [0] * (nmax + 1)
    for i, a in enumerate(P):
        if a:
            out = [x + a * y for x, y in zip(out, powlist(i, nmax))]
    out[0] = c0
    return out


# ============================================================ 1. exact 2-kernel rank

def rank_profile(vals, kmax, M):
    """rank over Q of the kernel elements  n -> vals[2^k n + j],  n = 1..M.

    Returns {k: rank of the span of all levels <= k}.  Exact Fractions.
    """
    basis = []                      # [(pivot column, row of Fractions)]
    out = {}
    for k in range(kmax + 1):
        for j in range(1 << k):
            row = [Fraction(vals[(1 << k) * n + j]) for n in range(1, M + 1)]
            for pc, br in basis:
                if row[pc]:
                    f = row[pc] / br[pc]
                    for l in range(pc, M):
                        row[l] -= f * br[l]
            for l in range(M):
                if row[l]:
                    basis.append((l, row))
                    basis.sort(key=lambda s: s[0])
                    break
        out[k] = len(basis)
    return out


def rank_of_vectors(vecs):
    """plain exact rank of a list of integer vectors."""
    basis = []
    for v in vecs:
        row = [Fraction(x) for x in v]
        n = len(row)
        for pc, br in basis:
            if row[pc]:
                f = row[pc] / br[pc]
                for l in range(pc, n):
                    row[l] -= f * br[l]
        for l in range(n):
            if row[l]:
                basis.append((l, row))
                basis.sort(key=lambda s: s[0])
                break
    return len(basis)


# ============================================================ 2. polynomials

def poly_shift(c):
    """coefficients of c(x-1)."""
    return [sum(c[j] * comb(j, i) * (-1) ** (j - i) for j in range(i, len(c)))
            for i in range(len(c))]


def pvec(c):
    """p(x) = c(x) + c(x-1), with trailing zeros stripped."""
    q = poly_shift(c)
    p = [(c[i] if i < len(c) else 0) + (q[i] if i < len(q) else 0)
         for i in range(max(len(c), len(q)))]
    while p and p[-1] == 0:
        p.pop()
    return p


def supp_of(p):
    return [i for i, x in enumerate(p) if x != 0]


def dclosure(supp):
    """downward closure of supp inside each parity class:
       {l : exists i in supp, l <= i, l = i mod 2}."""
    s = set()
    for i in supp:
        s.update(range(i % 2, i + 1, 2))
    return sorted(s)


def delta_of(P, c0):
    """delta = c(1) + c(0) - p(1)  (the centre correction of Rep.lean)."""
    p = pvec(P)
    return c0 + sum(P) - sum(p)


def poly_str(c):
    if not c:
        return "0"
    terms = []
    for i in range(len(c) - 1, -1, -1):
        a = c[i]
        if a == 0:
            continue
        if i == 0:
            terms.append("%d" % a)
        elif i == 1:
            terms.append(("%d*x" % a) if a != 1 else "x")
        else:
            terms.append(("%d*x^%d" % (a, i)) if a != 1 else ("x^%d" % i))
    return " + ".join(terms).replace("+ -", "- ") if terms else "0"


# ============================================================ 3. transfer matrices
# M0[i][l] = 2^i [i == l]
# M1[i][l] = C(i,l) * 2^(l+1) [l <= i, l = i mod 2]
# X(2u) = M0 X(u), X(2u+1) = M1 X(u), X = (Phi_0, Phi_1, ...)
# A(k,j) = M_{b0} M_{b1} ... M_{b(k-1)},  b_t = (j >> t) & 1.

def mat_mul(A, B):
    n = len(A)
    return [[sum(A[i][k] * B[k][l] for k in range(n)) for l in range(n)]
            for i in range(n)]


def M0mat(n):
    return [[2 ** i if l == i else 0 for l in range(n)] for i in range(n)]


def M1mat(n):
    return [[comb(i, l) * 2 ** (l + 1) if (l <= i and (i - l) % 2 == 0) else 0
             for l in range(n)] for i in range(n)]


def all_A(n, kmax):
    """{(k,j): A(k,j)} via A(k,j) = M_{j&1} * A(k-1, j>>1)."""
    A = {(0, 0): [[1 if i == l else 0 for l in range(n)] for i in range(n)]}
    M = (M0mat(n), M1mat(n))
    for k in range(1, kmax + 1):
        for j in range(1 << k):
            A[(k, j)] = mat_mul(M[j & 1], A[(k - 1, j >> 1)])
    return A


def transfer_span_dim(p, kmax):
    """dim span{ A(k,j)^T p : k <= kmax, j < 2^k }   (exact, small matrices)."""
    n = len(p)
    A = all_A(n, kmax)
    vecs = []
    for (k, j), Ak in A.items():
        vecs.append([sum(p[i] * Ak[i][l] for i in range(n)) for l in range(n)])
    return rank_of_vectors(vecs)


# ============================================================ 4. geometries

def brute_layer_counts(D, kind, dmax):
    """count lattice points of Z^D in each norm layer 0..dmax (brute force)."""
    from itertools import product
    counts = [0] * (dmax + 1)
    for v in product(range(-dmax, dmax + 1), repeat=D):
        if kind == "vn":
            nrm = sum(abs(x) for x in v)
        elif kind == "moore":
            nrm = max(abs(x) for x in v)
        else:                       # orthant: x_i >= 0
            nrm = (sum(abs(x) for x in v) if kind == "orthant_vn"
                   else max(abs(x) for x in v))
        if nrm <= dmax:
            counts[nrm] += 1
    return counts


def brute_orthant_counts(kind, dmax):
    from itertools import product
    counts = [0] * (dmax + 1)
    for v in product(range(0, dmax + 1), repeat=2):
        nrm = sum(v) if kind == "vn" else max(v)
        if nrm <= dmax:
            counts[nrm] += 1
    return counts


# geometry rows: (name, polynomial part P, c_0, rank known from docs/51)
GEOM = [
    ("Z^1 line",              [2],                 1, 2),
    ("Z^1 ray",               [1],                 1, 1),
    ("Z^2 vN (5 neighbours)", [0, 4],              1, 3),
    ("Z^2 Moore (9 nbrs)",    [0, 8],              1, 3),
    ("Z^2 triangular",        [0, 6],              1, 3),
    ("Z^2 quarter vN",        [1, 1],              1, 2),
    ("Z^2 quarter Moore",     [1, 2],              1, 1),
    ("Z^3 vN",                [2, 0, 4],           1, 4),
    ("Z^3 Moore",             [2, 0, 24],          1, 4),
    ("Z^4 vN (3x)",           [0, 16, 0, 8],       3, 5),
    ("Z^4 Moore",             [0, 16, 0, 64],      1, 5),
    ("Z^5 vN (3x)",           [6, 0, 20, 0, 4],    3, 6),
    ("Z^5 Moore",             [2, 0, 80, 0, 160],  1, 6),
]


# ------------------------------------------------------------ Stern / fusc

_FUSC = {0: 0, 1: 1}


def fusc(n):
    """Stern's diatomic sequence (A002487)."""
    v = _FUSC.get(n)
    if v is None:
        v = fusc(n // 2) + (fusc(n // 2 + 1) if n & 1 else 0)
        _FUSC[n] = v
    return v


# ============================================================ main

def main():
    KMAX = 7
    M = 40
    NMAX = (1 << KMAX) * (M + 2) + 4
    prepare(NMAX)
    rng = random.Random(20240617)

    def profile(vals, kmax=KMAX, MM=M):
        pr = rank_profile(vals, kmax, MM)
        return [pr[k] for k in range(kmax + 1)]

    print("=" * 78)
    print("321  rank measure: 2-kernel rank of Z_c  (KMAX=%d, M=%d, NMAX=%d)"
          % (KMAX, M, NMAX))
    print("=" * 78)

    # ---------------------------------------------------------------- [1] sanity
    print("\n[1] machinery self-checks")
    bad = 0
    for t in range(1, 3000):
        sh = shell(t)
        a = arm(t)
        if len(set(sh)) != len(sh) or len(sh) != 2 * (1 << wt(r_of(t))):
            bad += 1
        if set(a) & set(x - 1 for x in a):
            bad += 1
        if min(sh) < 0:
            bad += 1
    print("  shell = arm u (arm-1) disjoint, |shell t| = 2*2^wt(r t), shell >= 0:",
          "OK" if bad == 0 else "FAIL %d" % bad)
    print("  eps(t) == [0 in shell t] for t < 3000:",
          "OK" if all(eps(t) == (1 if 0 in shell(t) else 0)
                      for t in range(1, 3000)) else "FAIL")

    # ------------------------------------------- [2] transfer identity (numeric)
    print("\n[2] transfer identity  Z_c(2^k n + j) = sum_l (A^T p)_l Phi_l(n)"
          " + delta*[j=2^k-1]*eps(n)")
    ident_bad = 0
    ident_cases = 0
    for P, c0 in ([[0, 1, 1], 0], [[0, 0, 0, 1], 0], [[2, 0, 4], 1],
                  [[0, 16, 0, 64], 1], [[1, 2], 1], [[3, -2, 0, 5], 1],
                  [[0, 1], 7]):
        p = pvec(P)
        d = delta_of(P, c0)
        z = z_values(cvec_from_poly(P, c0, NMAX))
        n = len(P)
        A = all_A(n, 6)
        for (k, j), Ak in A.items():
            coef = [sum(p[i] * Ak[i][l] for i in range(n)) for l in range(n)]
            for nn in range(1, 21):
                t = (1 << k) * nn + j
                rhs = (sum(coef[l] * Phi(l, nn) for l in range(n))
                       + d * (1 if j == (1 << k) - 1 else 0) * eps(nn))
                ident_cases += 1
                if z[t] != rhs:
                    ident_bad += 1
    print("  checked %d (polynomial, k <= 6, j < 2^k, n <= 20) cases: %d mismatches"
          % (ident_cases, ident_bad))

    # --------------------------------------------- [3] moment tower independence
    print("\n[3] moment tower independence (rank of Phi_0..Phi_D, eps in the window)")
    print("  D : rank(Phi_0..Phi_D, eps)  M=40  M=80   D+2")
    for D in range(0, 9):
        row = []
        for MM in (40, 80):
            vecs = []
            for k in range(D + 1):
                vecs.append([Phi(k, n) for n in range(1, MM + 1)])
            vecs.append([eps(n) for n in range(1, MM + 1)])
            row.append(rank_of_vectors(vecs))
        print("  %d : %s   %s   %d" % (D, row[0], row[1], D + 2))

    # ------------------------------------------------------ [4] geometry table
    print("\n[4] the 13 rows of docs/51 (measured ranks for K = 4,5,6,7, M = %d)" % M)
    print("  | geometry | c_d (c_0) | rank K=4,5,6,7 | docs/51 | p | #supp | #Dcl | delta |")
    print("  |---|---|---|---|---|---|---|---|")
    geom_results = []
    for name, P, c0, known in GEOM:
        vals = z_values(cvec_from_poly(P, c0, NMAX))
        prof = profile(vals)
        p = pvec(P)
        sp = supp_of(p)
        dc = dclosure(sp)
        dd = delta_of(P, c0)
        geom_results.append((name, prof, known, p, sp, dc, dd))
        print("  | %s | %s ; c_0=%d | %s | %d | %s | %d | %d | %d |"
              % (name, poly_str(P), c0, ", ".join(str(x) for x in prof[4:]),
                 known, poly_str(p), len(sp), len(dc), dd))
    ok_known = sum(1 for _, prof, kn, _, _, _, _ in geom_results if prof[KMAX] == kn)
    ok_law = sum(1 for _, prof, _, _, sp, dc, dd in geom_results
                 if prof[KMAX] == len(dc) + (1 if dd else 0))
    w_ok = 0
    for name, P, c0, known in GEOM:
        vals = z_values(cvec_from_poly(P, c0, NMAX))
        if rank_profile(vals, 6, 80)[6] == rank_profile(vals, 6, M)[6]:
            w_ok += 1
    print("  window stability: rank(K=6, M=80) == rank(K=6, M=%d) for %d/%d rows"
          % (M, w_ok, len(GEOM)))
    print("  matches docs/51 ranks: %d/%d ;  matches #Dclosure+[delta!=0]: %d/%d"
          % (ok_known, len(GEOM), ok_law, len(GEOM)))

    # geometry layer counts vs brute force
    print("\n  layer counts vs brute force lattice enumeration:")
    checks = [("Z^1 line", 1, "vn", [2], 1, 4),
              ("Z^2 vN", 2, "vn", [0, 4], 1, 4),
              ("Z^2 Moore", 2, "moore", [0, 8], 1, 4),
              ("Z^3 vN", 3, "vn", [2, 0, 4], 1, 3),
              ("Z^3 Moore", 3, "moore", [2, 0, 24], 1, 3),
              ("Z^4 Moore", 4, "moore", [0, 16, 0, 64], 1, 3),
              ("Z^5 Moore", 5, "moore", [2, 0, 80, 0, 160], 1, 3)]
    allcnt_ok = True
    for name, D, kind, P, c0, dmax in checks:
        cnt = brute_layer_counts(D, kind, dmax)
        mine = cvec_from_poly(P, c0, dmax)[:dmax + 1]
        good = cnt == mine
        allcnt_ok &= good
        if not good:
            print("    %-12s brute=%s formula=%s  MISMATCH" % (name, cnt, mine))
    for name, kind, P, c0 in [("Z^2 quarter vN", "vn", [1, 1], 1),
                              ("Z^2 quarter Moore", "moore", [1, 2], 1)]:
        cnt = brute_orthant_counts(kind, 4)
        mine = cvec_from_poly(P, c0, 4)[:5]
        good = cnt == mine
        allcnt_ok &= good
        if not good:
            print("    %-18s brute=%s formula=%s  MISMATCH" % (name, cnt, mine))
    print("    all layer counts agree with brute force: %s" % allcnt_ok)

    # ------------------------------------------------ [5] polynomial census
    print("\n[5] polynomial census: naive  #supp(p)  vs refined  #Dclosure+[delta]")

    def census(rows, kmax, MM, label, maxshow=12):
        stat = {"n": 0, "naive_ok": 0, "ref_ok": 0, "mech_ok": 0, "gap": 0,
                "naive_bad": [], "ref_bad": [], "mech_bad": [], "unstable": [],
                "rows": []}
        for (P, c0) in rows:
            p = pvec(P)
            sp = supp_of(p)
            if not sp:
                continue
            dc = dclosure(sp)
            dd = delta_of(P, c0)
            nv = len(sp) + (1 if dd else 0)
            rf = len(dc) + (1 if dd else 0)
            vals = z_values(cvec_from_poly(P, c0, NMAX))
            pr = rank_profile(vals, kmax, MM)
            meas = pr[kmax]
            stat["n"] += 1
            stat["rows"].append((P, c0, p, len(sp), len(dc), dd, meas))
            if meas != pr[kmax - 1]:
                stat["unstable"].append((P, c0, [pr[k] for k in range(kmax + 1)]))
            if len(sp) < len(dc):
                stat["gap"] += 1
            if meas == nv:
                stat["naive_ok"] += 1
            else:
                stat["naive_bad"].append((P, c0, p, len(sp), len(dc), dd, meas, [pr[k] for k in range(kmax + 1)]))
            if meas == rf:
                stat["ref_ok"] += 1
            else:
                stat["ref_bad"].append((P, c0, p, len(sp), len(dc), dd, meas))
            # mechanism check: transfer span (small matrices), on a subset
        print("  --- %s: %d polynomials, K<=%d, M=%d" % (label, stat["n"], kmax, MM))
        print("      naive #supp(p)            matches in %d/%d" % (stat["naive_ok"], stat["n"]))
        print("      refined #Dcl+[delta!=0]   matches in %d/%d" % (stat["ref_ok"], stat["n"]))
        print("      rank(K=%d) != rank(K=%d)  (not converged): %d"
              % (kmax, kmax - 1, len(stat["unstable"])))
        print("      polys with a parity gap (#supp < #Dclosure): %d  ==  naive failures: %d"
              % (stat["gap"], len(stat["naive_bad"])))
        if stat["naive_bad"]:
            print("      counterexamples to the naive form (c ; p ; #supp #Dcl delta ; K-profile):")
            for (P, c0, p, ns, nd, dd, meas, prof) in stat["naive_bad"][:maxshow]:
                print("        c=%-22s p=%-26s #supp=%-2d #Dcl=%-2d delta=%-3d rank=%d  prof=%s"
                      % (poly_str(P), poly_str(p), ns, nd, dd, meas, prof))
        if stat["ref_bad"]:
            print("      counterexamples to the refined form:")
            for (P, c0, p, ns, nd, dd, meas) in stat["ref_bad"][:maxshow]:
                print("        c=%-22s c0=%-3d p=%-26s #Dcl=%-2d delta=%-3d rank=%d"
                      % (poly_str(P), c0, poly_str(p), nd, dd, meas))
        return stat

    # (a) exhaustive: degree <= 3, coefficients in [-2,2]
    rows_ex = []
    for a0 in range(-2, 3):
        for a1 in range(-2, 3):
            for a2 in range(-2, 3):
                for a3 in range(-2, 3):
                    P = [a0, a1, a2, a3]
                    if all(x == 0 for x in P):
                        continue
                    rows_ex.append((P, a0))
    stat_ex = census(rows_ex, KMAX, M, "exhaustive deg<=3, coeffs in [-2,2], c0=P(0)")

    # (b) random: degree <= 6, coefficients in [-6,6]
    rows_rnd = []
    for _ in range(320):
        deg = rng.randrange(0, 7)
        P = [rng.randrange(-6, 7) for _ in range(deg + 1)]
        while P[-1] == 0:
            P[-1] = rng.randrange(-6, 7)
        if all(x == 0 for x in P):
            continue
        rows_rnd.append((P, P[0]))
    stat_rnd = census(rows_rnd, KMAX, M, "random deg<=6, coeffs in [-6,6], c0=P(0)")

    # (c) mechanism: dim span{A^T p} vs #Dclosure, on all naive counterexamples
    #     from (a) plus a random sample of 40
    print("\n  mechanism check  dim span{A(k,j)^T p}  (k <= 6)  vs  #Dclosure:")
    mech_set = [(P, c0) for (P, c0, p, ns, nd, dd, meas, prof) in stat_ex["naive_bad"][:20]]
    seen = set()
    uniq = []
    for P, c0 in mech_set:
        key = tuple(P)
        if key not in seen:
            seen.add(key)
            uniq.append((P, c0))
    mech_set = uniq[:20] + [rows_rnd[i] for i in range(0, min(len(rows_rnd), 40))]
    m_ok = 0
    m_bad = []
    for (P, c0) in mech_set:
        p = pvec(P)
        sp = supp_of(p)
        dc = dclosure(sp)
        dd = delta_of(P, c0)
        dspan = transfer_span_dim(p, 6)
        if dspan == len(dc):
            m_ok += 1
        else:
            m_bad.append((P, p, dspan, len(dc)))
    print("      dim span{A^T p} == #Dclosure in %d/%d cases" % (m_ok, len(mech_set)))
    for P, p, ds, nd in m_bad[:6]:
        print("        MISMATCH c=%s p=%s span=%d #Dcl=%d" % (poly_str(P), poly_str(p), ds, nd))

    # ---------------------------------------------------- [6] centre correction
    print("\n[6] centre correction: c_d = P(d) for d >= 1, c_0 = P(0) + a  (delta = a)")
    print("  | c (poly part) | c0 shift a | delta | #Dclosure | #Dcl+[delta!=0] | rank K=4..7 |")
    print("  |---|---|---|---|---|---|")
    corr_cases = [([2], 0), ([2], 1), ([0, 4], 0), ([0, 4], 1), ([0, 4], -3),
                  ([2, 0, 4], 1), ([1, 1], 1), ([0, 1, 1], 0), ([0, 1, 1], 2),
                  ([1, 3, 1], 0), ([2, 0, 80, 0, 160], 1), ([0, 16, 0, 64], -2)]
    corr_ok = 0
    for P, a in corr_cases:
        c0 = P[0] + a
        vals = z_values(cvec_from_poly(P, c0, NMAX))
        prof = profile(vals)
        p = pvec(P)
        sp = supp_of(p)
        dc = dclosure(sp)
        dd = delta_of(P, c0)
        pred = len(dc) + (1 if dd else 0)
        ok = (prof[KMAX] == pred)
        corr_ok += ok
        print("  | %s | %+d | %d | %d | %d | %s |%s"
              % (poly_str(P), a, dd, len(dc), pred,
                 ",".join(str(x) for x in prof[4:]), "" if ok else "  <-- MISMATCH"))
    print("  formula rank = #Dclosure + [delta!=0] matches %d/%d" % (corr_ok, len(corr_cases)))

    # random centre-correction batch
    rnd_ok = 0
    rnd_bad = []
    rnd_n = 0
    for _ in range(60):
        deg = rng.randrange(1, 6)
        P = [rng.randrange(-4, 5) for _ in range(deg + 1)]
        while P[-1] == 0:
            P[-1] = rng.randrange(-4, 5)
        a = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        c0 = P[0] + a
        vals = z_values(cvec_from_poly(P, c0, NMAX))
        pr = rank_profile(vals, KMAX, M)
        p = pvec(P)
        sp = supp_of(p)
        dc = dclosure(sp)
        dd = delta_of(P, c0)
        pred = len(dc) + (1 if dd else 0)
        rnd_n += 1
        if pr[KMAX] == pred:
            rnd_ok += 1
        else:
            rnd_bad.append((P, c0, p, len(dc), dd, pr[KMAX]))
    print("  random centre-correction batch (60 cases, a in +-1..4): matches %d/%d"
          % (rnd_ok, rnd_n))
    for (P, c0, p, nd, dd, meas) in rnd_bad[:8]:
        print("    MISMATCH c=%s c0=%d p=%s #Dcl=%d delta=%d rank=%d"
              % (poly_str(P), c0, poly_str(p), nd, dd, meas))

    # ------------------------------------------- [7] non-polynomial layer counts
    print("\n[7] non-polynomial layer functions: rank(c) vs rank(Z_c), K=4,5,6,7")
    NP = [
        ("popcount(d)",            lambda d: wt(d)),
        ("popcount(d)^2",          lambda d: wt(d) ** 2),
        ("d + popcount(d)",        lambda d: d + wt(d)),
        ("d^2 + popcount(d)",      lambda d: d * d + wt(d)),
        ("2^popcount(d)",          lambda d: 2 ** wt(d)),
        ("3^popcount(d)",          lambda d: 3 ** wt(d)),
        ("fusc(d)",                lambda d: fusc(d)),
        ("d + fusc(d)",            lambda d: d + fusc(d)),
        ("(-1)^popcount(d) (TM)",  lambda d: (-1) ** wt(d)),
        ("Thue-Morse parity",      lambda d: ((1 - (-1) ** wt(d)) // 2)),
        ("TM(d) + d",              lambda d: d + (-1) ** wt(d)),
        ("d mod 2",                lambda d: d % 2),
        ("d mod 3",                lambda d: d % 3),
        ("d mod 4",                lambda d: d % 4),
        ("d mod 5",                lambda d: d % 5),
        ("d mod 6",                lambda d: d % 6),
        ("d mod 7",                lambda d: d % 7),
        ("d mod 8",                lambda d: d % 8),
        ("[d even]",               lambda d: 1 - (d % 2)),
        ("floor(d^1.585)",         lambda d: int(d ** 1.585)),
        ("popcount(d)*fusc(d)",   lambda d: wt(d) * fusc(d)),
        ("fusc(d)^2",              lambda d: fusc(d) ** 2),
        ("2^d  (binary tree)",     lambda d: 2 ** d),
    ]
    print("  | c_d | rank(c) K=4,5,6,7 | rank(Z_c) K=4,5,6,7 | rank(c) | rank(Z_c) |")
    print("  |---|---|---|---|---|")
    np_rows = []
    for name, f in NP:
        cv = [f(d) for d in range(NMAX + 1)]
        rc = profile(cv)
        vals = z_values(cv)
        rz = profile(vals)
        np_rows.append((name, rc, rz))
        print("  | %s | %s | %s | %d | %d |"
              % (name, ",".join(str(x) for x in rc[4:]), ",".join(str(x) for x in rz[4:]),
                 rc[KMAX], rz[KMAX]))

    # ratio table
    print("\n  relation between rank(c) and rank(Z_c) at K=%d:" % KMAX)
    for name, rc, rz in np_rows:
        a, b = rc[KMAX], rz[KMAX]
        print("    %-24s rank(c)=%-2d rank(Z)=%-2d  rank(Z)/rank(c)=%s  rank(Z)-rank(c)=%+d  <=2*rank(c)? %s"
              % (name, a, b,
                 ("%.2f" % (b / a)) if a else "-", b - a, b <= 2 * a))

    print("\n  convergence diagnostics (M = 80, K = 6; a flat M=40 profile can be capped at 40):")
    for name, f in NP:
        cv = [f(d) for d in range(NMAX + 1)]
        pc = rank_profile(cv, 6, 80)
        pz = rank_profile(z_values(cv), 6, 80)
        print("    %-24s rank(c)=%-3d rank(Z_c)=%-3d   (M=80,K=6)" % (name, pc[6], pz[6]))

    # ------------------------------------- [7a] periodic layer functions d mod m
    print("\n[7a] periodic layer functions  c_d = d mod m  (K=%d, M=%d)" % (KMAX, M))
    print("     m : rank(c)  rank(Z_c)  ceil(m/2)  (m+1)/2 for odd m")
    for mm in range(2, 13):
        cv = [d % mm for d in range(NMAX + 1)]
        rc = rank_profile(cv, KMAX, M)[KMAX]
        rz = rank_profile(z_values(cv), KMAX, M)[KMAX]
        print("    %2d : %-7d %-9d %d" % (mm, rc, rz, (mm + 1) // 2))

    # ------------------------------- [7b] products of two 2-regular layer functions
    print("\n[7b] products of basic 2-regular layer functions: does rank(c) control rank(Z_c)?")
    bases = [("1", lambda d: 1),
             ("popcount", lambda d: wt(d)),
             ("fusc", lambda d: fusc(d)),
             ("d", lambda d: d),
             ("d^2", lambda d: d * d),
             ("3^popcount", lambda d: 3 ** wt(d)),
             ("TM", lambda d: (-1) ** wt(d))]
    worst_ratio = (0, "")
    worst_diff = (-99, "")
    viol2 = []
    viol_plus = []
    nprod = 0
    for i in range(len(bases)):
        for j in range(i, len(bases)):
            na, fa = bases[i]
            nb, fb = bases[j]
            cv = [fa(d) * fb(d) for d in range(NMAX + 1)]
            rc = rank_profile(cv, KMAX, M)[KMAX]
            rz = rank_profile(z_values(cv), KMAX, M)[KMAX]
            if rc == 0:
                continue
            nprod += 1
            ratio = rz / rc
            if ratio > worst_ratio[0]:
                worst_ratio = (ratio, na + "*" + nb + " (rank %d -> %d)" % (rc, rz))
            if rz - rc > worst_diff[0]:
                worst_diff = (rz - rc, na + "*" + nb + " (rank %d -> %d)" % (rc, rz))
            if rz > 2 * rc:
                viol2.append((na + "*" + nb, rc, rz))
            if rz > rc + 1:
                viol_plus.append((na + "*" + nb, rc, rz))
    print("  %d products tested (K=%d, M=%d)" % (nprod, KMAX, M))
    print("  largest rank(Z)/rank(c) = %.2f  : %s" % (worst_ratio[0], worst_ratio[1]))
    print("  largest rank(Z)-rank(c) = %d     : %s" % (worst_diff[0], worst_diff[1]))
    print("  violations of rank(Z) <= 2*rank(c) : %d" % len(viol2))
    for name, a, b in viol2[:8]:
        print("    %s : rank(c)=%d rank(Z)=%d" % (name, a, b))
    print("  violations of rank(Z) <= rank(c)+1: %d" % len(viol_plus))
    for name, a, b in viol_plus[:8]:
        print("    %s : rank(c)=%d rank(Z)=%d" % (name, a, b))

    # ------------------------------------------------ [8] lower-bound evidence
    print("\n[8] lower-bound evidence")
    allrows = stat_ex["rows"] + stat_rnd["rows"]
    print("  (8a) upper bound  rank <= #Dclosure + [delta!=0]: violations in census:")
    viol = sum(1 for row in allrows if row[6] > row[4] + (1 if row[5] else 0))
    print("    %d violations out of %d polynomials" % (viol, len(allrows)))
    print("  (8b) lower bound  rank >= #supp(p) + [delta!=0]: violations in census:")
    viol2 = sum(1 for row in allrows if row[6] < row[3] + (1 if row[5] else 0))
    print("    %d violations out of %d polynomials" % (viol2, len(allrows)))

    print("\n  (8c) the pure-moment ranks rank(Phi_D) = floor(D/2)+1  (not D+1!):")
    print("    D : rank(Phi_D) K=4..7   floor(D/2)+1")
    for D in range(0, 7):
        vals = [Phi(D, t) for t in range(NMAX + 1)]
        prof = rank_profile(vals, KMAX, M)
        print("    %d : %-18s %d" % (D, ",".join(str(prof[k]) for k in range(4, 8)), D // 2 + 1))

    print("\n  (8d) explicit counterexample to 'rank >= D+1' (D = deg p):")
    for P, c0 in ([[0, 1, 1], 0], [[0, 0, 0, 1], 0], [[0, 0, 0, 0, 1], 0]):
        p = pvec(P)
        sp = supp_of(p)
        dc = dclosure(sp)
        vals = z_values(cvec_from_poly(P, c0, NMAX))
        prof = rank_profile(vals, KMAX, M)
        print("    c=%-14s p=%-22s D=%-2d rank=%-2d  D+1=%-2d  #supp=%-2d #Dcl=%d"
              % (poly_str(P), poly_str(p), len(p) - 1, prof[KMAX], len(p), len(sp), len(dc)))

    print("\n  (8e) moment tower vs eps: rank(Phi_0..Phi_{D-1}, eps) and adding Phi_D")
    for D in (1, 2, 3, 4, 5):
        vecs = [[Phi(k, n) for n in range(1, M + 1)] for k in range(D)]
        vecs.append([eps(n) for n in range(1, M + 1)])
        r1 = rank_of_vectors(vecs)
        vecs2 = [list(v) for v in vecs] + [[Phi(D, n) for n in range(1, M + 1)]]
        r2 = rank_of_vectors(vecs2)
        print("    D=%d: rank(Phi_0..Phi_%d, eps)=%d  -> with Phi_%d: %d  (full: %d)"
              % (D, D - 1, r1, D, r2, D + 2))

    print("\n  (8f) column-support lemma: column l of A(k,j) is supported in {l, l+2, l+4, ...}")
    print("       (this is what makes  #Dclosure  the upper bound)")
    viol_col = 0
    for n in range(2, 10):
        A = all_A(n, 7)
        for (k, j), Ak in A.items():
            for l in range(n):
                for i in range(n):
                    if Ak[i][l] != 0 and not (i >= l and (i - l) % 2 == 0):
                        viol_col += 1
    print("       violations: %d" % viol_col)

    print("\n  (8g) supp(A^T p)  inside  Dclosure(supp p), and the eps coordinate is orthogonal")
    viol_sup = 0
    testps = [[0, 0, 2], [2, 0, 2], [1, -2, 2], [0, 5, -3, 2], [-4, 6, -10, 0],
              [0, 0, 0, 0, 3], [1, 0, 0, 0, 0, 2]]
    for p in testps:
        dcset = set(dclosure(supp_of(p)))
        n = len(p)
        A = all_A(n, 6)
        for (k, j), Ak in A.items():
            v = [sum(p[i] * Ak[i][l] for i in range(n)) for l in range(n)]
            if any(v[l] != 0 and l not in dcset for l in range(n)):
                viol_sup += 1
    print("       violations: %d" % viol_sup)

    print("\n  (8h) rank(c) = deg(c) + 1 for polynomial layer functions (spot check, 60 polys):")
    okdeg = 0
    for _ in range(60):
        deg = rng.randrange(0, 7)
        P = [rng.randrange(-6, 7) for _ in range(deg + 1)]
        while P[-1] == 0:
            P[-1] = rng.randrange(-6, 7)
        if all(x == 0 for x in P):
            continue
        cv = [P and sum(P[i] * d ** i for i in range(len(P))) for d in range(NMAX + 1)]
        rc = rank_profile(cv, KMAX, M)[KMAX]
        if rc == len(P):
            okdeg += 1
    print("       rank(c) == deg(c)+1 : %d/60" % okdeg)

    print("\n" + "=" * 78)
    print("total wall clock: %.1f s" % (time.time() - T0))


if __name__ == "__main__":
    main()