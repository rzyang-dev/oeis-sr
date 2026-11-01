#!/usr/bin/env python3
# -*- coding: ascii -*-
"""323_stirling_proof.py -- Stirling numbers mod 2 vs. the Rule-129 dead-shell offsets.

BRIDGE THEOREM (proof in docs/57-stirling.md, section 4):

    S(n,k) odd   <=>   (n-k) & ((k-1)//2) == 0 .

Substituting u := n-k  turns it verbatim into the SIGMA_d criterion
(docs/52 Theorem B, Lean: OEIS.Rule129.mem_sig_iff)

    u in SIGMA_d  <=>  u & ((d-u)//2) == 0 ,

hence for every d >= 0

    { k in [1,d+1] : S(d+1,k) odd } = { d+1-u : u in SIGMA_d }        (*)

an explicit bijection (k <-> u = d+1-k) of index sets, so

    #{k : S(n,k) odd} = |SIGMA_{n-1}| = fusc(n-1) + fusc(n).

This script checks, by direct DP, everything above for n <= 2000:

  C1  #{k : S(n,k) odd} == |SIGMA_{n-1}|                    (counts)
  C2  |SIGMA_d| == fusc(d)+fusc(d+1) == fusc(2d+1)          (Stern, docs/52 Thm C)
  C3  {k : S(n,k) odd} == {n-u : u in SIGMA_{n-1}}          (set identity, not only count)
  C4  pointwise: S(n,k) odd <=> (n-k)&((k-1)//2) == 0
  C5  binomial form: S(n,k) = C(n-ceil((k+1)/2), (k-1)//2) (mod 2)   [Lucas]
  C6  k-parity split: #{k even : odd} = fusc(n-1), #{k odd : odd} = fusc(n)
  C7  central Stirling: S(2h,h) odd <=> h is fibbinary (h & (h>>1) == 0)
  C8  block sums: sum_{d < 2^m} |SIGMA_d| = 3^m
  C9  no-carry lemma: (m & a == 0) <=> (m submask of m+a)   (Lean: land_add_iff)
  C10 two independent DP implementations agree on every row
  C11 the Stern recursion p(2e)=p(e), q(2e)=A(e), p(2e+1)=A(e), q(2e+1)=q(e)
      read directly on the Stirling rows (p = even k, q = odd k)
  C12 the local 2-state digit rule of docs/52 section 4 on the Stirling side:
      u & (gray(d) ^ (u>>1)) == u  with u = n-k, d = n-1
  C12b that closed form == the bit-by-bit rule
  C13 the generating function x^k / prod_{i=1..k}(1 - i*x) really is sum_n S(n,k) x^n

Run:  py -3 scripts/323_stirling_proof.py [N]        (default N = 2000)
"""

import sys
import time
from math import comb

N_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 2000   # largest row index verified
T0 = time.time()


# ---------------------------------------------------------------- utilities
def fusc(n):
    """Stern's diatomic sequence, A002487: fusc(0)=0, fusc(1)=1,
    fusc(2n)=fusc(n), fusc(2n+1)=fusc(n)+fusc(n+1)."""
    a, b = 0, 1
    for bit in bin(n)[2:]:
        if bit == '0':
            b = a + b
        else:
            a = a + b
    return a


def sigma_orig(d):
    """SIGMA_d straight from the definition:  u <= d and u subset floor((u+d)/2)."""
    return [u for u in range(d + 1) if (u & ((u + d) // 2)) == u]


def sigma_nocarry(d):
    """Same set in the no-carry form of Theorem B: u & floor((d-u)/2) == 0."""
    return [u for u in range(d + 1) if (u & ((d - u) // 2)) == 0]


def stirling_rows_mod2(nmax):
    """Yield row n of S(n,k) mod 2 as a list of length n+1 (n = 0..nmax).

    Recurrence  S(n,k) = S(n-1,k-1) + k*S(n-1,k),  reduced mod 2:
    the k*S(n-1,k) term survives exactly for odd k.
    """
    prev = [1]                     # row 0
    yield prev
    for n in range(1, nmax + 1):
        cur = [0] * (n + 1)
        prev = prev + [0]              # row n-1 padded with S(n-1,n) = 0
        for k in range(1, n + 1):
            cur[k] = (prev[k - 1] + (k & 1) * prev[k]) & 1
        yield cur
        prev = cur


def stirling_rows_bitmask(nmax):
    """Second, independent implementation: the whole row is one Python int.

    bit k of R_n = S(n,k) mod 2,   R_n = (R_{n-1} << 1) XOR (R_{n-1} & ODD),
    where ODD has 1-bits exactly at odd positions.
    """
    odd = 0
    for k in range(1, nmax + 3, 2):
        odd |= 1 << k
    r = 1
    yield [1]
    for n in range(1, nmax + 1):
        r = (r << 1) ^ (r & odd)
        yield [(r >> k) & 1 for k in range(n + 1)]


def lucas_odd(z, w):
    """Parity of C(z,w) via Lucas' theorem: C(z,w) is odd iff w is a submask of z."""
    return (w & z) == w


# ---------------------------------------------------------------- main scan
def main():
    print("=" * 78)
    print(" 323 -- Stirling numbers of the second kind mod 2  vs.  SIGMA_d")
    print("=" * 78)

    # -- sanity of the Lucas helper against exact big-integer binomials ----
    bad_lucas = 0
    for z in range(0, 61):
        for w in range(0, z + 1):
            if lucas_odd(z, w) != (comb(z, w) & 1 == 1):
                bad_lucas += 1
    print("\n[lucas] parity of C(z,w) via (w & z)==w vs math.comb, 0<=w<=z<=60"
          " : violations = %d" % bad_lucas)

    # -- the two SIGMA forms agree ----------------------------------------
    bad_forms = 0
    for d in range(0, N_MAX):
        if sigma_orig(d) != sigma_nocarry(d):
            bad_forms += 1
    print("[sigma] definition  u subset floor((u+d)/2)  vs  u & floor((d-u)/2)==0,"
          " d < %d : violations = %d" % (N_MAX, bad_forms))

    # -- the main scan -----------------------------------------------------
    bad = dict(c1=0, c2=0, c3=0, c4=0, c5=0, c6=0, c7=0, c12=0)
    A_of_d = []                       # A(d) = |SIGMA_d|
    P = [0] * (N_MAX + 2)             # P[n] = #{k even : S(n,k) odd}
    Q = [0] * (N_MAX + 2)             # Q[n] = #{k odd  : S(n,k) odd}
    first_rows = []                   # small table for the report
    checked_pairs = 0

    for n, row in enumerate(stirling_rows_mod2(N_MAX)):
        if n == 0:
            continue
        d = n - 1
        S = sigma_orig(d)
        A_of_d.append(len(S))
        odd_ks = [k for k in range(1, n + 1) if row[k]]

        # C1: counts agree
        if len(odd_ks) != len(S):
            bad['c1'] += 1

        # C2: Stern closed form for |SIGMA_d|
        if not (len(S) == fusc(d) + fusc(d + 1) == fusc(2 * d + 1)):
            bad['c2'] += 1

        # C3: the index sets are equal, not merely equinumerous
        if set(n - u for u in S) != set(odd_ks):
            bad['c3'] += 1

        # C4/C5: pointwise criteria
        for k in range(1, n + 1):
            checked_pairs += 1
            # C4
            if (((n - k) & ((k - 1) // 2)) == 0) != (row[k] == 1):
                bad['c4'] += 1
            # C5  z = n - ceil((k+1)/2),  w = floor((k-1)/2)
            z = n - (k + 2) // 2
            w = (k - 1) // 2
            if lucas_odd(z, w) != (row[k] == 1):
                bad['c5'] += 1

        # C12: the local 2-state digit rule of docs/52 section 4, written on the
        # Stirling side.  With u = n-k, d = n-1 it reads
        #     bit_i(u)=1  =>  bit_{i+1}(u) ^ bit_{i+1}(d) ^ bit_i(d) = 1,
        # which is equivalent to the closed form  u & (gray(d) ^ (u>>1)) == u,
        # gray(d) = d ^ (d>>1).  (Reformulation checked in C12b below.)
        gray_d = d ^ (d >> 1)
        for k in range(1, n + 1):
            u = n - k
            if ((u & (gray_d ^ (u >> 1))) == u) != (row[k] == 1):
                bad['c12'] += 1

        # C6: parity split of the odd-k positions
        n_even_k = sum(1 for k in odd_ks if k % 2 == 0)
        n_odd_k = len(odd_ks) - n_even_k
        P[n], Q[n] = n_even_k, n_odd_k
        if not (n_even_k == fusc(n - 1) and n_odd_k == fusc(n)):
            bad['c6'] += 1

        # C7: central Stirling number S(2h,h)
        if n % 2 == 0:
            h = n // 2
            if (row[h] == 1) != ((h & (h >> 1)) == 0):
                bad['c7'] += 1

        if d <= 15:
            first_rows.append((d, S, odd_ks))

    # -- C10: independent implementation ----------------------------------
    bad['c10'] = 0
    for n, (r1, r2) in enumerate(zip(stirling_rows_mod2(N_MAX),
                                     stirling_rows_bitmask(N_MAX))):
        if r1 != r2:
            bad['c10'] += 1

    # -- C8: block sums ----------------------------------------------------
    bad['c8'] = 0
    for m in range(0, 11):
        if sum(A_of_d[:2 ** m]) != 3 ** m:
            bad['c8'] += 1

    # -- C12b: bit-by-bit local rule  ==  closed form with the Gray code --
    #     forall i: bit_i(u)=1 => bit_{i+1}(u) ^ bit_{i+1}(d) ^ bit_i(d) = 1
    #     <=>  u & (gray(d) ^ (u>>1)) == u ,  gray(d) = d ^ (d>>1)
    bad['c12b'] = 0
    for d in range(0, 600):
        gd = d ^ (d >> 1)
        for u in range(0, d + 1):
            L = max(u, d).bit_length() + 2
            ok = True
            for i in range(L):
                if (u >> i) & 1:
                    if ((((u >> (i + 1)) ^ (d >> (i + 1)) ^ (d >> i)) & 1) != 1):
                        ok = False
                        break
            if ok != (((u & (gd ^ (u >> 1))) == u)):
                bad['c12b'] += 1

    # -- C13: the generating function behind the proof ---------------------
    #     sum_{n>=k} S(n,k) x^n  =  x^k / prod_{i=1..k} (1 - i*x)      (exact, in Z[[x]])
    # verified by exact integer power-series inversion, then reduced mod 2.
    bad['c13'] = 0
    NG = 40
    exact = [[0] * (NG + 1) for _ in range(9)]
    exact[0][0] = 1
    for n in range(1, NG + 1):
        for k in range(1, min(n, 8) + 1):
            exact[k][n] = exact[k - 1][n - 1] + k * exact[k][n - 1]
    for k in range(1, 9):
        poly = [1]                                  # prod (1 - i x)
        for i in range(1, k + 1):
            new = [0] * (len(poly) + 1)
            for j, c in enumerate(poly):
                new[j] += c
                new[j + 1] -= i * c
            poly = new
        inv = [0] * (NG + 1)                        # 1 / poly
        inv[0] = 1
        for j in range(1, NG + 1):
            s = 0
            for i in range(1, min(j, k) + 1):
                s += poly[i] * inv[j - i]
            inv[j] = -s
        for n in range(k, NG + 1):
            if inv[n - k] != exact[k][n]:
                bad['c13'] += 1

    # -- C11: the Stern recursion read on the Stirling rows ---------------
    #  p(d)=P(d+1), q(d)=Q(d+1), A(d)=P(d+1)+Q(d+1);  docs/52 section 3 gives
    #     p(2e)=p(e), q(2e)=A(e), p(2e+1)=A(e), q(2e+1)=q(e).
    bad['c11'] = 0
    for e in range(0, N_MAX // 2):
        A_e = P[e + 1] + Q[e + 1]
        if 2 * e + 1 <= N_MAX and P[2 * e + 1] != P[e + 1]:
            bad['c11'] += 1
        if 2 * e + 1 <= N_MAX and Q[2 * e + 1] != A_e:
            bad['c11'] += 1
        if 2 * e + 2 <= N_MAX and P[2 * e + 2] != A_e:
            bad['c11'] += 1
        if 2 * e + 2 <= N_MAX and Q[2 * e + 2] != Q[e + 1]:
            bad['c11'] += 1

    # -- C9: no-carry lemma -----------------------------------------------
    bad['c9'] = 0
    lim = 1200
    for m in range(0, lim + 1):
        for a in range(0, lim + 1):
            if (((m & a) == 0)) != ((m & (m + a)) == m):
                bad['c9'] += 1

    # ------------------------------------------------------------ report
    print("\n--- small table (d, SIGMA_d, odd k in row d+1) " + "-" * 24)
    print("  d | |SIGMA_d| | SIGMA_d                    | {k : S(d+1,k) odd}")
    for d, S, ok in first_rows:
        print("  %2d |    %2d    | %-26s | %s" % (d, len(S), str(S), str(ok)))

    print("\n--- checks " + "-" * 62)
    print("  C1  #{k : S(n,k) odd} == |SIGMA_{n-1}|            (n <= %d) : %d violations"
          % (N_MAX, bad['c1']))
    print("  C2  |SIGMA_d| == fusc(d)+fusc(d+1) == fusc(2d+1)  (d <= %d) : %d violations"
          % (N_MAX - 1, bad['c2']))
    print("  C3  {k : odd} == {n-u : u in SIGMA_{n-1}}  (as sets) (n <= %d) : %d violations"
          % (N_MAX, bad['c3']))
    print("  C4  S(n,k) odd <=> (n-k)&((k-1)//2) == 0  (%d pairs)      : %d violations"
          % (checked_pairs, bad['c4']))
    print("  C5  S(n,k) == C(n-ceil((k+1)/2),(k-1)//2) mod 2 (Lucas)   : %d violations"
          % bad['c5'])
    print("  C6  #{k even: odd} == fusc(n-1), #{k odd: odd} == fusc(n) : %d violations"
          % bad['c6'])
    print("  C7  S(2h,h) odd <=> h fibbinary           (h <= %d)      : %d violations"
          % (N_MAX // 2, bad['c7']))
    print("  C8  sum_{d<2^m} |SIGMA_d| == 3^m                 (m <= 10) : %d violations"
          % bad['c8'])
    print("  C9  (m&a)==0 <=> m submask of m+a         (a,m <= %d)     : %d violations"
          % (lim, bad['c9']))
    print("  C10 two independent DP implementations agree  (n <= %d)   : %d violations"
          % (N_MAX, bad['c10']))
    print("  C11 p(2e)=p(e), q(2e)=A(e), p(2e+1)=A(e), q(2e+1)=q(e)  : %d violations"
          % bad['c11'])
    print("  C12 local digit rule  u & (gray(d)^(u>>1)) == u, u=n-k, d=n-1 : %d violations"
          % bad['c12'])
    print("  C12b bit-by-bit local rule == closed Gray-code form (d<=599)  : %d violations"
          % bad['c12b'])
    print("  C13 GF identity x^k/prod(1-ix) reproduces S(n,k) (k<=8, n<=40) : %d violations"
          % bad['c13'])
    print("  aux Lucas parity helper vs math.comb                        : %d violations"
          % bad_lucas)
    print("  aux two SIGMA_d forms                                       : %d violations"
          % bad_forms)

    total = sum(bad.values()) + bad_lucas + bad_forms
    print("\n  max row n = %d, (n,k) pairs checked = %d, A(d) computed for d <= %d"
          % (N_MAX, checked_pairs, N_MAX - 1))
    print("  A(0..20)   = %s" % [len(sigma_orig(d)) for d in range(21)])
    odd_counts = [sum(row[k] for k in range(1, n + 1))
                  for n, row in enumerate(stirling_rows_mod2(20)) if n >= 1]
    print("  #odd in rows 1..20 = %s" % odd_counts)
    print("  fusc(0..20)        = %s" % [fusc(d) for d in range(21)])
    print("\n  RESULT: %s   (total violations = %d, %.1f s)"
          % ("ALL CHECKS PASSED" if total == 0 else "FAILURES PRESENT",
             total, time.time() - T0))
    return 0 if total == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
