# -*- coding: utf-8 -*-
"""330_rank_closure.py -- closing the rank gap.

Claim under study (docs/55, conjecture A, middle step):

    dim_Q span{ A(k,j)^T p : k >= 0, 0 <= j < 2^k }  =  #DClose(supp p)

with  A(k,j) = M_{b_0} M_{b_1} ... M_{b_{k-1}},  b_t = (j>>t)&1,
      M0[i][l] = 2^i [i=l],   M1[i][l] = C(i,l) 2^{l+1} [l<=i, l=i mod 2].

This script verifies, with exact integer / rational arithmetic:

  [1] the explicit-entry lemma   A(k,j)[i][l] = 2^{k l} C(i,l) S_j(i-l),
      S_j(d) = sum_{m submask j} (j-2m)^d            (needs j < 2^k)
      -- checked against the M0/M1 products, against the arm recursion and
      against the cocycle A(k+k', j+2^k j') = A(k,j) A(k',j').
  [2] S_j(d) = 0 for odd d (parity decoupling), S_j(0) = 2^{wt j}.
  [3] single point p = e_i:  rank = floor(i/2)+1;  (k,j)=(1,1) already covers the
      whole parity chain with nonzero entries, and the k = 1..floor(i/2)+1
      dilations diag(2^{kl}) turn that into a Vandermonde basis.
  [4] general p: exact rank of the full family == #DClose(supp p);  one single
      j = 2^m together with #DClose consecutive k's already spans everything.
      Two sufficient bounds for m:
          m <= A_0(A_0+1)/2 + A_1(A_1+1)/2     (root counting, no size bound)
          m >= A+1+ceil(log2 B)                (2-adic dominance, B = max|p_i|)
      where A_eps = max{a : p_{2a+eps} != 0}, A = max A_eps.
  [5] end to end:  rank_2(Z_c) == #DClose(supp p) + [delta != 0]  from the
      raw shell definition (independent code path).

Run:  py -3 scripts/330_rank_closure.py
"""

import random
import time
from math import comb, gcd

T0 = time.time()


def hdr(s):
    print("\n" + "=" * 78)
    print(s)
    print("=" * 78)


def stamp(s):
    print("   [%6.1fs] %s" % (time.time() - T0, s))


# --------------------------------------------------------------- 0. machinery

def submasks(r):
    out = []
    m = r
    while True:
        out.append(m)
        if m == 0:
            break
        m = (m - 1) & r
    return out


def r_of(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))


def arm(t):
    return [t - 2 * m for m in submasks(r_of(t))]


def shell(t):
    out = []
    for x in arm(t):
        out.append(x)
        out.append(x - 1)
    return out


def rank_int(rows, ncol):
    """Exact rank over Q of a list of integer vectors (integer-only elimination,
    rows rescaled by their gcd so the entries stay small)."""
    rows = [list(r[:ncol]) for r in rows]
    rows = [r for r in rows if any(r)]
    if not rows:
        return 0
    n = len(rows)
    rk = 0
    for col in range(ncol):
        piv = -1
        for i in range(rk, n):
            if rows[i][col]:
                piv = i
                break
        if piv < 0:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        pv = rows[rk][col]
        for i in range(rk + 1, n):
            b = rows[i][col]
            if b:
                row = [pv * x - b * y for x, y in zip(rows[i], rows[rk])]
                g = 0
                for v in row:
                    if v:
                        g = gcd(g, abs(v))
                        if g == 1:
                            break
                if g > 1:
                    row = [v // g for v in row]
                rows[i] = row
        rk += 1
        if rk == n or rk == ncol:
            break
    return rk


def mmul(A, B):
    n = len(A)
    return [[sum(A[i][k] * B[k][l] for k in range(n)) for l in range(n)]
            for i in range(n)]


_MCACHE = {}


def _mats(D):
    if D not in _MCACHE:
        m0 = [[(1 << i) if i == l else 0 for l in range(D + 1)] for i in range(D + 1)]
        m1 = [[comb(i, l) * (1 << (l + 1)) if (l <= i and (i - l) % 2 == 0) else 0
               for l in range(D + 1)] for i in range(D + 1)]
        _MCACHE[D] = (m0, m1)
    return _MCACHE[D]


def M0mat(D):
    return _mats(D)[0]


def M1mat(D):
    return _mats(D)[1]


def ident(D):
    return [[1 if i == l else 0 for l in range(D + 1)] for i in range(D + 1)]


_ACACHE = {}


def A_rec(k, j, D):
    """A(k,j) = M_{b_0} M_{b_1} ... M_{b_{k-1}}  (docs/55 convention)."""
    key = (D, k, j)
    if key in _ACACHE:
        return _ACACHE[key]
    m0, m1 = _mats(D)
    A = ident(D)
    for t in range(k):
        A = mmul(A, m1 if ((j >> t) & 1) else m0)
    _ACACHE[key] = A
    return A


def E_sub(j):
    """the multiset {j-2m : m submask of j}."""
    return [j - 2 * m for m in submasks(j)]


def Sval(E, d):
    if d == 0:
        return len(E)
    return sum(pow(e, d) for e in E)


def A_formula(k, j, D):
    """the explicit-entry lemma:  A(k,j)[i][l] = 2^{k l} C(i,l) S_j(i-l)."""
    E = E_sub(j)
    out = []
    for i in range(D + 1):
        row = []
        for l in range(D + 1):
            if l <= i:
                row.append(comb(i, l) * (1 << (k * l)) * Sval(E, i - l))
            else:
                row.append(0)
        out.append(row)
    return out


def ATp(A, p):
    D = len(p)
    return [sum(p[i] * A[i][l] for i in range(D)) for l in range(D)]


def family(p, K):
    """all vectors A(k,j)^T p with k <= K, j < 2^k."""
    D = len(p) - 1
    out = []
    for k in range(K + 1):
        for j in range(1 << k):
            out.append(ATp(A_rec(k, j, D), p))
    return out


def dclose_list(supp):
    s = set()
    for i in supp:
        s.update(range(i % 2, i + 1, 2))
    return sorted(s)


def supp_of(p):
    return [i for i, x in enumerate(p) if x]


def class_max_a(p):
    """(A_0, A_1):  A_eps = max a with p_{2a+eps} != 0  (None if class empty)."""
    D = len(p) - 1
    A = [None, None]
    for l in range(D + 1):
        if p[l]:
            e = l % 2
            a = (l - e) // 2
            if A[e] is None or a > A[e]:
                A[e] = a
    return A[0], A[1]


def class_vector(p, j, eps):
    """w_a = (B^{(j)T} P)_a = sum_b C(2b+eps,2a+eps) S_j(2(b-a)) p_{2b+eps}."""
    D = len(p) - 1
    E = E_sub(j)
    A = class_max_a(p)[eps]
    if A is None:
        return []
    w = []
    for a in range(A + 1):
        s = 0
        for b in range(a, A + 1):
            s += comb(2 * b + eps, 2 * a + eps) * Sval(E, 2 * (b - a)) * p[2 * b + eps]
        w.append(s)
    return w


def nclass(p):
    """#DClose(supp p)."""
    A0, A1 = class_max_a(p)
    return (0 if A0 is None else A0 + 1) + (0 if A1 is None else A1 + 1)


def single_j_rank(p, j):
    """rank of the j-block { A(k,j)^T p : k = k0 .. k0+#DClose-1 }."""
    D = len(p) - 1
    n = nclass(p)
    k0 = max(1, j.bit_length())
    return rank_int([ATp(A_rec(k, j, D), p) for k in range(k0, k0 + n)], D + 1)


def w_full_support(p, j):
    """True iff every class coordinate of every w(j) is nonzero."""
    out = True
    for eps in (0, 1):
        w = class_vector(p, j, eps)
        if any(x == 0 for x in w):
            out = False
    return out


# ===================================================== 1. explicit-entry lemma
hdr("[1] explicit-entry lemma   A(k,j)[i][l] = 2^{k l} C(i,l) S_j(i-l)")

bad = 0
cnt = 0
for D in (3, 6, 9):
    for k in range(0, 7):
        for j in range(1 << k):
            cnt += 1
            if A_rec(k, j, D) != A_formula(k, j, D):
                bad += 1
                if bad <= 3:
                    print("    MISMATCH D=%d k=%d j=%d" % (D, k, j))
print("  (a) formula vs the M0/M1 product:  %d cases (D<=9, k<=6, all j<2^k), %d mismatches"
      % (cnt, bad))

# the combinatorial heart: arm(2^k n + j) = { 2^k x + (j-2m) : x in arm(n), m submask j }
bad = 0
cnt = 0
for k in range(0, 5):
    for j in range(1 << k):
        for n in range(1, 24):
            cnt += 1
            lhs = sorted(arm((1 << k) * n + j))
            rhs = sorted(set((1 << k) * x + (j - 2 * m)
                             for x in arm(n) for m in submasks(j)))
            if lhs != rhs:
                bad += 1
                if bad <= 3:
                    print("    ARM MISMATCH k=%d j=%d n=%d" % (k, j, n))
print("  (b) arm recursion arm(2^k n+j) = 2^k arm(n) + (j-2m):  %d cases, %d mismatches"
      % (cnt, bad))

# cocycle
bad = 0
cnt = 0
D = 6
for k1 in range(0, 4):
    for j1 in range(1 << k1):
        for k2 in range(0, 4):
            for j2 in range(1 << k2):
                cnt += 1
                if mmul(A_rec(k1, j1, D), A_rec(k2, j2, D)) != A_rec(k1 + k2, j1 + (1 << k1) * j2, D):
                    bad += 1
print("  (c) cocycle A(k1+k2, j1+2^k1 j2) = A(k1,j1)A(k2,j2):  %d cases, %d mismatches"
      % (cnt, bad))
stamp("lemma [1] done")

# ============================================ 2. parity decoupling structure
hdr("[2] S_j(d) = sum_{m submask j} (j-2m)^d :  odd d vanish, S_j(0) = 2^{wt j}")

print("      j  wt(j)   S_j(0)  2^wt   S_j(1)  S_j(2)  S_j(3)  S_j(4)  S_j(6)   #E_j")
for j in range(0, 16):
    E = E_sub(j)
    row = [Sval(E, d) for d in (0, 1, 2, 3, 4, 6)]
    print("    %4d  %4d  %7d  %4d  %6d  %6d  %6d  %6d  %7d   %4d"
          % (j, bin(j).count("1"), row[0], 1 << bin(j).count("1"),
             row[1], row[2], row[3], row[4], row[5], len(E)))
bad = 0
for j in range(0, 1 << 12):
    E = E_sub(j)
    if Sval(E, 0) != 1 << bin(j).count("1"):
        bad += 1
    for d in range(1, 9):
        if d % 2 == 1 and Sval(E, d) != 0:
            bad += 1
print("  j < 4096, d <= 8: odd-d vanishing and S_j(0)=2^wt(j): %d violations" % bad)
print("  (E_j is closed under e -> -e because m -> j-m preserves submasks)")

# ============================================== 3. single point p = e_i
hdr("[3] single point p = e_i :  rank = floor(i/2)+1, one j is enough")

K = 6
print("    i  floor(i/2)+1  rank{all k<=6,j}  rank{j=1,k=1..}  #supp(M1^T e_i)")
bad = 0
for i in range(0, 13):
    p = [0] * (i + 1)
    p[i] = 1
    r_all = rank_int(family(p, K), i + 1)
    A1 = A_rec(1, 1, i)
    v = [A1[i][l] for l in range(i + 1)]
    r_j1 = rank_int([[ (1 << ((k) * l)) * v[l] for l in range(i + 1)]
                     for k in range(1, i // 2 + 2)], i + 1)
    sup = len([x for x in v if x])
    print("  %3d  %10d  %16d  %15d  %14d" % (i, i // 2 + 1, r_all, r_j1, sup))
    if r_all != i // 2 + 1 or r_j1 != i // 2 + 1 or sup != i // 2 + 1:
        bad += 1
print("  violations: %d   (M1^T e_i has support = the whole parity chain, all C(i,l)2^{l+1} != 0;"
      % bad)
print("   the k-family diag(2^{kl}) then turns that single vector into a Vandermonde basis)")
stamp("sections [1]-[3] done")

# ================================================== 4. general p
hdr("[4] general p :   dim span{A(k,j)^T p} = #DClose(supp p)")

# ---------------------------------------------------------------- 4a exhaustive
print("  (4a) exhaustive p in {-1,0,1}^{D+1}")
for D in (4, 5):
    bad = 0
    cnt = 0
    ex = []
    for code in range(3 ** (D + 1)):
        p = []
        c = code
        for _ in range(D + 1):
            p.append(c % 3 - 1)
            c //= 3
        cnt += 1
        got = rank_int(family(p, 6), D + 1)
        pred = len(dclose_list(supp_of(p)))
        if got != pred:
            bad += 1
            if len(ex) < 4:
                ex.append((p, got, pred))
    print("    D=%d: %d vectors, %d mismatches%s"
          % (D, cnt, bad, "" if not bad else "  " + str(ex)))
stamp("4a done")

# ------------------------------------------------------------------ 4b random
print("  (4b) random p, deg <= 9, coefficients in [-9,9], K=6 (and K=7 stability)")
random.seed(330)
bad = 0
cnt = 0
stable = 0
ns = 0
for trial in range(300):
    D = random.randint(0, 9)
    p = [random.randint(-9, 9) for _ in range(D + 1)]
    if not any(p):
        p[0] = 1
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    D = len(p) - 1
    got = rank_int(family(p, 6), D + 1)
    pred = len(dclose_list(supp_of(p)))
    cnt += 1
    if got != pred:
        bad += 1
        if bad <= 4:
            print("    MISMATCH p=%s got=%d pred=%d" % (p, got, pred))
    if trial % 10 == 0:
        ns += 1
        if rank_int(family(p, 7), D + 1) == got:
            stable += 1
print("    %d random p, %d mismatches;  K=6 vs K=7 stable on %d/%d spot checks"
      % (cnt, bad, stable, ns))
stamp("4b done")

# ------------------------------------------- 4c single j and the x^2-1 example
print("  (4c) one j plus #DClose consecutive k's already gives the full rank,")
print("       and that happens iff every class coordinate of w(j) is nonzero:")
examples = [
    ("x^2 - 1        ", [-1, 0, 1]),
    ("x^4 - 1        ", [-1, 0, 0, 0, 1]),
    ("x^2            ", [0, 0, 1]),
    ("x^2 + x - 1    ", [-1, 1, 1]),
    ("x^4 - 3x^2 + 1 ", [1, 0, -3, 0, 1]),
    ("2 - x^2 - x^4  ", [2, 0, -1, 0, -1]),
    ("x^3 - x        ", [0, -1, 0, 1]),
]
for name, p in examples:
    tgt = nclass(p)
    first = None
    for j in range(0, 256):
        if single_j_rank(p, j) == tgt:
            first = j
            break
    w0 = class_vector(p, 0, 0)
    w1 = class_vector(p, 1, 0)
    w2 = class_vector(p, 2, 0)
    print("    p=%-16s #DClose=%-2d first j=%-3s   even-class w: j=0 %s, j=1 %s, j=2 %s"
          % (name, tgt, first, w0, w1, w2))
print("    (a zero in w(j) kills that coordinate for every k; conversely nonzero w(j)")
print("     makes the #DClose vectors independent by a root-counting argument)")
bad = 0
cnt = 0
random.seed(334)
for _ in range(60):
    D = random.randint(2, 7)
    p = [random.randint(-4, 4) for _ in range(D + 1)]
    if not any(p):
        p[0] = 1
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    for j in range(0, 40):
        cnt += 1
        if (single_j_rank(p, j) == nclass(p)) != w_full_support(p, j):
            bad += 1
print("    equivalence 'single-j rank = #DClose  <=>  w(j) has full support' : %d cases, %d violations"
      % (cnt, bad))

# --------------------------------------- 4d explicit family j=2^m, k=m+1..m+A+1
print("  (4d) explicit family  j = 2^m,  k = m+1 .. m+#DClose")
print("       sufficient bound from the 2-adic dominance proof: m >= A+1+ceil(log2 B)")


def explicit_rank(p, m):
    D = len(p) - 1
    n = nclass(p)
    js = 1 << m
    return rank_int([ATp(A_rec(k, js, D), p) for k in range(m + 1, m + n + 1)], D + 1)


def min_m(p):
    A0, A1 = class_max_a(p)
    A = max([x for x in (A0, A1) if x is not None], default=-1)
    B = max(abs(x) for x in p) if any(p) else 0
    for m in range(0, 40):
        if explicit_rank(p, m) == nclass(p):
            return m, A, B
    return None, A, B


random.seed(331)
viol = 0
bound_ok = 0
cnt = 0
slowest = 0
for trial in range(400):
    D = random.randint(0, 11)
    p = [random.randint(-12, 12) for _ in range(D + 1)]
    if not any(p):
        p[0] = 3
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    cnt += 1
    m, A, B = min_m(p)
    if m is None:
        viol += 1
        if viol <= 3:
            A0, A1 = class_max_a(p)
            print("      FAIL p=%s A=(%s,%s) target=%d"
                  % (p, A0, A1, len(dclose_list(supp_of(p)))))
            for mm in range(0, 4):
                print("        m=%d j=%d w_even=%s w_odd=%s rank=%d"
                      % (mm, 1 << mm, class_vector(p, 1 << mm, 0),
                         class_vector(p, 1 << mm, 1), explicit_rank(p, mm)))
        continue
    slowest = max(slowest, m)
    bnd = A + 1 + (max(B, 1) - 1).bit_length()
    if m <= bnd:
        bound_ok += 1
print("    %d random p (deg<=11, |coef|<=12):" % cnt)
print("      explicit family reaches #DClose for every p : %d/%d" % (cnt - viol, cnt))
print("      min m over all cases = %d ; bound A+1+ceil(log2 B) satisfied in %d/%d"
      % (slowest, bound_ok, cnt))

# the bound is what the proof actually gives: full support of w(2^m) at m = A+1+ceil(log2 B)
random.seed(335)
bad = 0
cnt = 0
for _ in range(250):
    D = random.randint(0, 10)
    p = [random.randint(-20, 20) for _ in range(D + 1)]
    if not any(p):
        p[0] = 7
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    A0, A1 = class_max_a(p)
    A = max([x for x in (A0, A1) if x is not None], default=-1)
    B = max(abs(x) for x in p)
    m = A + 1 + (B - 1).bit_length()
    cnt += 1
    if not w_full_support(p, 1 << m):
        bad += 1
        if bad <= 3:
            print("      BOUND FAIL p=%s A=%d B=%d m=%d" % (p, A, B, m))
print("      at m = A+1+ceil(log2 B) the vector w(2^m) has full support : %d/%d"
      % (cnt - bad, cnt))

# --- the uniform bound: m <= A_0(A_0+1)/2 + A_1(A_1+1)/2 (<= A(A+1)) ----
# w_a(m) = 2 sum_b C(2b+eps,2a+eps) p_{2b+eps} z^{b-a} with z = 4^m is a nonzero
# polynomial of degree A_eps - a, so at most A_eps-a values of m kill it, and at
# most sum_eps A_eps(A_eps+1)/2 values of m are bad in total.
print("  (4d') uniform bound  m <= A_0(A_0+1)/2 + A_1(A_1+1)/2  (<= A(A+1)), no")
print("        coefficient bound: root counting on the exponential polynomial w_a(2^m)")
random.seed(338)
bad = 0
cnt = 0
worst = 0
for _ in range(300):
    D = random.randint(0, 10)
    p = [random.randint(-30, 30) for _ in range(D + 1)]
    if not any(p):
        p[0] = 5
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    A0, A1 = class_max_a(p)
    A = max([x for x in (A0, A1) if x is not None], default=-1)
    bm = [m for m in range(0, 48) if not w_full_support(p, 1 << m)]
    cnt += 1
    worst = max(worst, len(bm))
    lim = (0 if A0 is None else A0 * (A0 + 1) // 2) + (0 if A1 is None else A1 * (A1 + 1) // 2)
    if len(bm) > lim:
        bad += 1
        if bad <= 3:
            print("      ROOT-COUNT FAIL p=%s bad m=%s limit=%d" % (p, bm, lim))
print("      #bad m <= A_0(A_0+1)/2 + A_1(A_1+1)/2 : %d/%d   (largest bad count seen %d)"
      % (cnt - bad, cnt, worst))

# adversarial: force w_0 to vanish at m = 0,1,2  (A=3, degree 3 in z)
adv = [-64, 0, 84, 0, -21, 0, 1]
bm = [m for m in range(0, 12) if not w_full_support(adv, 1 << m)]
good = [m for m in range(0, 12) if m not in bm]
print("      adversarial p = -64 + 84x^2 - 21x^4 + x^6  (w_0 = 2(z-1)(z-4)(z-16)):")
print("        bad m = %s   smallest good m = %s   A_0(A_0+1)/2 = 6"
      % (bm, good[0] if good else None))
print("        rank of the m-family: %s   (#DClose = 4)"
      % [explicit_rank(adv, m) for m in range(0, 6)])
adv2 = [-4, 0, 1]
bm2 = [m for m in range(0, 8) if not w_full_support(adv2, 1 << m)]
print("      adversarial p = x^2 - 4 : bad m = %s (w_0 = 2z - 8, root z = 4)" % bm2)

# tightness: one fewer k loses a dimension
random.seed(336)
tight = 0
cnt = 0
for _ in range(120):
    D = random.randint(2, 8)
    p = [random.randint(-5, 5) for _ in range(D + 1)]
    if not any(p):
        p[0] = 1
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    n = nclass(p)
    if n < 2:
        continue
    m, _, _ = min_m(p)
    if m is None:
        continue
    js = 1 << m
    full = rank_int([ATp(A_rec(k, js, D), p) for k in range(m + 1, m + n + 1)], D + 1)
    short = rank_int([ATp(A_rec(k, js, D), p) for k in range(m + 1, m + n)], D + 1)
    cnt += 1
    if full == n and short == n - 1:
        tight += 1
print("      %d vectors (maximal m-family) are tight: dropping one k drops the rank: %d/%d"
      % (cnt, tight, cnt))

# a full blow-by-blow example
p = [1, 0, -3, 0, 1]
print("    worked example p = 1 - 3x^2 + x^4,  #DClose = %d" % len(dclose_list(supp_of(p))))
for m in (0, 1, 2, 3):
    print("      m=%d  j=%-3d  k=%s  rank=%d"
          % (m, 1 << m, list(range(m + 1, m + nclass(p) + 1)), explicit_rank(p, m)))

# ------------------------------------------- 4e support / upper-bound sanity
print("  (4e) supp(A^T p) inside DClose(supp p) for all k<=6, j<2^k")
bad = 0
cnt = 0
random.seed(332)
for trial in range(120):
    D = random.randint(0, 8)
    p = [random.randint(-5, 5) for _ in range(D + 1)]
    if not any(p):
        p[0] = 1
    S = set(dclose_list(supp_of(p)))
    for k in range(0, 7):
        for j in range(1 << k):
            v = ATp(A_rec(k, j, D), p)
            cnt += 1
            for l, x in enumerate(v):
                if x and l not in S:
                    bad += 1
print("    %d vectors checked, %d coordinates outside DClose" % (cnt, bad))
stamp("section [4] done")

# ============================================ 5. end to end: rank_2(Z_c)
hdr("[5] end to end from the raw shell definition:  rank_2(Z_c) = #DClose + [delta!=0]")

_IDX = []


def prepare(nmax):
    global _IDX
    _IDX = [None] * (nmax + 1)
    for t in range(nmax + 1):
        _IDX[t] = tuple(t - 2 * m for m in submasks(r_of(t)))


def z_values(cvec):
    h = [cvec[x] + (cvec[x - 1] if x >= 1 else 0) for x in range(len(cvec))]
    get = h.__getitem__
    out = [0] * len(cvec)
    for t in range(1, len(cvec)):
        out[t] = sum(map(get, _IDX[t]))
    return out


def poly_shift(c):
    return [sum(c[j] * comb(j, i) * (-1) ** (j - i) for j in range(i, len(c)))
            for i in range(len(c))]


def pvec(c):
    q = poly_shift(c)
    p = [(c[i] if i < len(c) else 0) + (q[i] if i < len(q) else 0)
         for i in range(max(len(c), len(q)))]
    while p and p[-1] == 0:
        p.pop()
    return p or [0]


def solve_c_from_p(p):
    """invert c(x) + c(x-1) = p by back substitution (triangular, diagonal 2)."""
    from fractions import Fraction as Fr
    n = len(p)
    c = [Fr(0)] * n
    for i in range(n - 1, -1, -1):
        s = sum(c[j] * comb(j, i) * (-1) ** (j - i) for j in range(i + 1, n))
        c[i] = (Fr(p[i]) - s) / 2
    return c


def cvec_from(P, c0, nmax):
    out = [0] * (nmax + 1)
    for i, a in enumerate(P):
        if a:
            for d in range(nmax + 1):
                out[d] += a * pow(d, i)
    out[0] = c0
    return out


def kernel_rank(vals, K, M):
    rows = []
    for k in range(K + 1):
        for j in range(1 << k):
            rows.append([vals[(1 << k) * n + j] for n in range(1, M + 1)])
    return rank_int(rows, M)


# every p in Q[x] is c(x)+c(x-1) for a unique c: the operator is triangular with
# diagonal 2, so the vector-level theorem really covers every layer polynomial.
random.seed(337)
bad = 0
for _ in range(60):
    D = random.randint(0, 6)
    p = [random.randint(-6, 6) for _ in range(D + 1)]
    c = solve_c_from_p(p)
    back = pvec(c)
    while back and back[-1] == 0:
        back.pop()
    q = list(p)
    while q and q[-1] == 0:
        q.pop()
    if not q:
        q = [0]
    if [x for x in back] != [x for x in q]:
        bad += 1
print("  (5a) c(x)+c(x-1) = p is solvable for every p (triangular, diag 2): %d/60 round trips"
      % (60 - bad))

POOL = []       # census: (P, c0)


def add_census():
    for a0 in range(-2, 3):
        for a1 in range(-2, 3):
            for a2 in range(-2, 3):
                for a3 in range(-2, 3):
                    P = [a0, a1, a2, a3]
                    while len(P) > 1 and P[-1] == 0:
                        P.pop()
                    POOL.append((P, P[0]))


add_census()
random.seed(333)
for _ in range(120):
    D = random.randint(1, 6)
    P = [random.randint(-6, 6) for _ in range(D + 1)]
    while len(P) > 1 and P[-1] == 0:
        P.pop()
    POOL.append((P, P[0]))
for _ in range(80):
    D = random.randint(1, 5)
    P = [random.randint(-4, 4) for _ in range(D + 1)]
    if not any(P):
        P[0] = 2
    while len(P) > 1 and P[-1] == 0:
        P.pop()
    a = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    POOL.append((P, P[0] + a))

K5, M5 = 6, 20
prepare((1 << K5) * (M5 + 1) + 2)
bad = 0
badnc = 0
gapcnt = 0
naive_fail = 0
for P, c0 in POOL:
    p = pvec(P)
    nmax = (1 << K5) * (M5 + 1) + 1
    cv = cvec_from(P, c0, nmax)
    vals = z_values(cv)
    got = kernel_rank(vals, K5, M5)
    pred = len(dclose_list(supp_of(p))) + (1 if c0 - (P[0] if P else 0) else 0)
    naive = len(supp_of(p)) + (1 if c0 - (P[0] if P else 0) else 0)
    if got != pred:
        bad += 1
        if bad <= 5:
            print("    MISMATCH P=%s c0=%d p=%s got=%d pred=%d" % (P, c0, p, got, pred))
    if len(dclose_list(supp_of(p))) != len(supp_of(p)):
        gapcnt += 1
        if got != naive:
            naive_fail += 1
print("    census: %d layer functions (deg<=3 exhaustive |coef|<=2, plus random and"
      % len(POOL))
print("            centre-corrected),  K=%d, M=%d" % (K5, M5))
print("      rank_2(Z_c) == #DClose+[delta!=0] : %d/%d   (mismatches %d)"
      % (len(POOL) - bad, len(POOL), bad))
print("      examples with a parity gap (#supp < #DClose): %d, of which the naive"
      % gapcnt)
print("      #supp+[delta!=0] formula fails: %d" % naive_fail)
stamp("section [5] done")

print("\n" + "=" * 78)
print("SUMMARY")
print("=" * 78)
print("  [1] explicit entries A(k,j)[i][l] = 2^{kl} C(i,l) S_j(i-l): verified")
print("  [2] odd-d vanishing S_j(2r+1)=0, S_j(0)=2^wt(j): verified")
print("  [3] p = e_i  ->  rank = floor(i/2)+1 (j=1, k=1..floor(i/2)+1 suffices)")
print("  [4] general p -> rank = #DClose(supp p); explicit family j=2^m, k=m+1..m+#DClose")
print("      two sufficient bounds for m:  A_0(A_0+1)/2 + A_1(A_1+1)/2   and   A+1+ceil(log2 B)")
print("      (A_eps = max{a : p_{2a+eps} != 0}, A = max_eps A_eps, B = max|p_i|)")
print("  [5] rank_2(Z_c) = #DClose+[delta!=0] from the shell definition")
print("\n  total time %.1f s" % (time.time() - T0))
