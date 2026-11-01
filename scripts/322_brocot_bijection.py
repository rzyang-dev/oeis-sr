# -*- coding: utf-8 -*-
"""
322_brocot_bijection.py

Explicit bijections for the "dead offset" set of the Rule-129 ("all neighbours equal")
cellular automaton:

    SIGMA_d = { u : 0 <= u <= d,  u & ((d - u)//2) == 0 }.

Known (docs/45, docs/52, lean/Brocot.lean):
    |SIGMA_d| = fusc(d) + fusc(d+1) = fusc(2d+1)          (fusc = A002487)

This script builds the *explicit* bijections and checks them numerically.

  T1  Psi_d : SIGMA_d -> Hyp(d) + Hyp(d-1),   u |-> (u, (d-u)//2)  tagged by (d-u) % 2
      where Hyp(n) = {(u,h) : u & h == 0, u + 2h == n}  (hyperbinary representations of n).
      Corollary: {u in SIGMA_d : u = d mod 2} <-> Hyp(d) (size fusc(d+1)),
                 {u in SIGMA_d : u != d mod 2} <-> Hyp(d-1) (size fusc(d)).

  T2  Hyp(2m)   = 2*Hyp(m)  +  (2*Hyp(m-1) + (0,1))
      Hyp(2m-1) = 2*Hyp(m-1) + (1,0)
      => HB(n) := |Hyp(n)| = fusc(n+1)   (PROOF, upgrades the earlier numeric check).
      The counting matrices N_0 = [[1,0],[1,1]], N_1 = [[1,1],[0,1]] are the
      Stern-Brocot left/right matrices, read along the bits of n from LSB to MSB.

  T3  Run-length / continued-fraction normal form.  With
        T(d) = {i >= 0 : bit_i(d) != bit_{i+1}(d)}   (d-run boundaries)
      we have   u in SIGMA_d  <=>  every maximal 1-run [a,b] of u has
                                   b in T(d) and d constant on [a,b].
      Hence SIGMA_d <-> "weighted independent sets" on the run-length sequence
      L_1..L_k of d (LSB -> MSB), and that count is K(L) + K(L[1:]) (continuants),
      i.e. numerator + denominator of the continued fraction [L_1; L_2; ...; L_k].
      Indeed  fusc(d)/fusc(d+1) = [L_1;...;L_k] if d is odd, = [0;L_1;...;L_k] if d even.

  T4  Doubling u -> 2u is injective  Sigma_e -> Sigma_{2e}  and  Sigma_e -> Sigma_{2e+1},
      with image = the even part (the SAME set in both targets).  The Calkin-Wilf
      "left child" (p,q)(2e) = (p(e), p(e)+q(e)) therefore matches only on *sizes*:
      |Sigma_{2e}| = |Sigma_e| + fusc(e) > |Sigma_e|.  The residual half is the
      parity class {v in Sigma_e : v+e odd}, which is Hyp(e-1), not Sigma_e.

Results (this run, d <= 2000, cheapest identities to 4096): 22 checks, 0 violations,
~21 s.  Candidate maps that FAIL are reported separately, with smallest counterexamples
(C1 run-length vector alone, C2 u -> (d-u)//2, C5 Sigma_d -> Hyp(d) alone).

Run:  py -3 scripts/322_brocot_bijection.py
"""

from fractions import Fraction

LIM = 2000          # main verification bound for d
LIM_N = 2000        # bound for n in Hyp(n) / fusc(n+1)
LIM_BIG = 4096      # bound for the cheapest identities

CHECKS = []         # (label, range, violations) -- these must all be 0
OBS = []            # (label, value) -- observations, some of them deliberately non-zero

def note(label, rng, bad):
    CHECKS.append((label, rng, bad))

def obs(label, value):
    OBS.append((label, value))

# ----------------------------------------------------------------------------- basics
def fusc(n):
    """Stern's diatomic series A002487."""
    a, b = 0, 1
    for ch in bin(n)[2:]:
        if ch == '0':
            b = a + b
        else:
            a = a + b
    return a

def bit(x, i):
    return (x >> i) & 1

def sig(d):
    """SIGMA_d straight from the definition."""
    return [u for u in range(d + 1) if (u & ((d - u) // 2)) == 0]

def hyp(n):
    """Hyp(n) = {(u,h) : u & h == 0, u + 2h == n}, sorted."""
    return [(n - 2 * h, h) for h in range(n // 2 + 1) if ((n - 2 * h) & h) == 0]

def one_runs(u):
    """Maximal runs [a,b] of 1-bits in u (LSB first)."""
    out, i = [], 0
    while (1 << i) <= u:
        if bit(u, i):
            j = i
            while bit(u, j + 1):
                j += 1
            out.append((i, j))
            i = j + 1
        else:
            i += 1
    return out

def T_set(d):
    """d-run boundaries: positions i with bit_i(d) != bit_{i+1}(d)."""
    L = d.bit_length() + 2
    return set(i for i in range(L) if bit(d, i) != bit(d, i + 1))

def run_data(d):
    """Maximal constant runs of d as (start, end, value), LSB first."""
    L, out, i = d.bit_length(), [], 0
    while i < L:
        b = bit(d, i)
        j = i
        while j + 1 < L and bit(d, j + 1) == b:
            j += 1
        out.append((i, j, b))
        i = j + 1
    return out

def run_lens(d):
    """Run lengths of d, LSB -> MSB."""
    return [e - s + 1 for (s, e, _v) in run_data(d)]

def continuant(a):
    """K(a_1..a_k): K()=1, K(a1)=a1, K(a1..ak)=ak*K(a1..a_{k-1})+K(a1..a_{k-2})."""
    p, q = 1, 0
    for x in a:
        p, q = x * p + q, p
    return p

def cf_eval(a):
    """Exact value of the finite continued fraction [a_0; a_1, ..., a_k]."""
    x = Fraction(a[-1])
    for t in reversed(a[:-1]):
        x = t + 1 / x
    return x

# =============================================================================
# T1  the canonical bijection  SIGMA_d  <->  Hyp(d) + Hyp(d-1)
# =============================================================================
def psi(d, u):
    """Forward map of T1 (only valid for u in SIGMA_d)."""
    return (u, (d - u) // 2, (d - u) % 2)

def psi_inv(d, rec):
    """Inverse map of T1."""
    return rec[0]

def test_T1(lim):
    bad = 0
    bad_par = 0
    bad_size = 0
    for d in range(0, lim + 1):
        S = sig(d)
        recs = [psi(d, u) for u in S]
        # injective
        if len(set(recs)) != len(recs):
            bad += 1
            continue
        # image = Hyp(d) x {0}  union  Hyp(d-1) x {1}
        img0 = set((u, h) for (u, h, t) in recs if t == 0)
        img1 = set((u, h) for (u, h, t) in recs if t == 1)
        if img0 != set(hyp(d)):
            bad += 1
        if img1 != (set(hyp(d - 1)) if d > 0 else set()):
            bad += 1
        # inverse
        for r in recs:
            if psi(d, psi_inv(d, r)) != r or psi_inv(d, psi(d, psi_inv(d, r))) != psi_inv(d, r):
                bad += 1
        # parity split sizes  (Stern pair)
        q = sum(1 for u in S if (u + d) % 2 == 0)
        p = len(S) - q
        if (p, q) != (fusc(d), fusc(d + 1)):
            bad_par += 1
        if len(S) != len(set(hyp(d))) + len(set(hyp(d - 1))):
            bad_size += 1
    note("T1 bijection Sigma_d -> Hyp(d)+Hyp(d-1) (inj + image + inverse)", "d <= %d" % lim, bad)
    note("T1 cor: #(u+d odd)=fusc(d), #(u+d even)=fusc(d+1)", "d <= %d" % lim, bad_par)
    note("T1 cor: |Sigma_d| = |Hyp(d)|+|Hyp(d-1)|", "d <= %d" % lim, bad_size)

# =============================================================================
# T2  Hyp recursion  =>  |Hyp(n)| = fusc(n+1)
# =============================================================================
def test_T2(lim):
    bad_even = 0
    bad_odd = 0
    bad_size = 0
    for m in range(0, lim + 1):
        # Hyp(2m) = 2*Hyp(m)  +  (2*Hyp(m-1) + (0,1))
        A = set(hyp(2 * m))
        B = set((2 * u, 2 * h) for (u, h) in hyp(m))
        if m > 0:
            B |= set((2 * u, 2 * h + 1) for (u, h) in hyp(m - 1))
        if A != B:
            bad_even += 1
        if 2 * m - 1 >= 0 and m > 0:
            A2 = set(hyp(2 * m - 1))
            B2 = set((2 * u + 1, 2 * h) for (u, h) in hyp(m - 1))
            if A2 != B2:
                bad_odd += 1
        if len(A) != fusc(2 * m + 1):
            bad_size += 1
        if m > 0 and len(hyp(2 * m - 1)) != fusc(2 * m):
            bad_size += 1
    note("T2a Hyp(2m) = 2Hyp(m) + (2Hyp(m-1)+(0,1))", "m <= %d" % lim, bad_even)
    note("T2b Hyp(2m-1) = 2Hyp(m-1)+(1,0)", "m <= %d" % lim, bad_odd)
    note("T2c |Hyp(n)| = fusc(n+1)", "n <= %d" % (2 * lim), bad_size)

def test_stern_matrices(lim):
    """(fusc(n), fusc(n+1)) = (1,1) * prod N_{bit_i(n)}, bits read MSB -> LSB,
    skipping the leading 1.  N_0 = L = [[1,0],[1,1]], N_1 = R = [[1,1],[0,1]]."""
    N0 = ((1, 0), (1, 1))   # "L": (p,q) -> (p, p+q)
    N1 = ((1, 1), (0, 1))   # "R": (p,q) -> (p+q, q)
    bad = 0
    for n in range(1, lim + 1):
        p, q = 1, 1
        for i in range(n.bit_length() - 2, -1, -1):
            m = N0 if bit(n, i) == 0 else N1
            p, q = m[0][0] * p + m[0][1] * q, m[1][0] * p + m[1][1] * q
        if (p, q) != (fusc(n), fusc(n + 1)):
            bad += 1
    note("T2d (fusc(n),fusc(n+1)) = (1,1)*prod N_{bit_i(n)}, bits MSB->LSB (Stern-Brocot matrices)",
         "n <= %d" % lim, bad)

# =============================================================================
# T3  run-length / continued-fraction normal form
# =============================================================================
def run_ok(u, d):
    """Every maximal 1-run [a,b] of u has b in T(d) and d constant on [a,b]."""
    T = T_set(d)
    for (a, b) in one_runs(u):
        if b not in T:
            return False
        for i in range(a, b):
            if bit(d, i) != bit(d, i + 1):
                return False
    return True

def test_T3a(lim):
    bad = 0
    for d in range(1, lim + 1):
        if [u for u in range(0, d + 1) if run_ok(u, d)] != sig(d):
            bad += 1
    note("T3a u in Sigma_d <=> every 1-run [a,b] of u has b in T(d), d const on [a,b]",
         "d <= %d" % lim, bad)
    # the two digit identities used by the induction proof of T3a
    bad2 = 0
    for e in range(1, lim + 1):
        Te = T_set(e)
        want_even = set(i + 1 for i in Te) | (set([0]) if e % 2 == 1 else set())
        want_odd = set(i + 1 for i in Te) | (set([0]) if e % 2 == 0 else set())
        if T_set(2 * e) != want_even:
            bad2 += 1
        if T_set(2 * e + 1) != want_odd:
            bad2 += 1
    note("T3a' T(2e) = {i+1: i in T(e)} (+{0} iff e odd), T(2e+1) likewise (iff e even)",
         "e <= %d" % lim, bad2)

def wi_objects(d):
    """All 'weighted independent set' data allowed by the run structure of d.

    A datum is a pair (chosen, lows): the indices j of the d-runs that u 'hits'
    and, for each, the low bit a_j in [start_j, end_j] of the corresponding 1-run
    [a_j, end_j] of u.  Two consecutive hits j < j' need a_{j'} >= end_j + 2.

    Returns (list of data, run_starts, run_ends).
    """
    L = run_lens(d)
    starts, ends = [], []
    pos = 0
    for x in L:
        starts.append(pos)
        ends.append(pos + x - 1)
        pos += x
    res = []

    def rec(j, chosen, lows, low):
        # low = smallest start allowed for the next hit run
        if j == len(L):
            res.append((tuple(chosen), tuple(lows)))
            return
        rec(j + 1, chosen, lows, low)                      # d-run j is not hit
        for a in range(max(starts[j], low), ends[j] + 1):  # d-run j is hit, 1-run [a, end_j]
            rec(j + 1, chosen + [j], lows + [a], ends[j] + 2)

    rec(0, [], [], 0)
    return res, starts, ends

def test_T3b(lim):
    bad_bij = 0
    bad_count = 0
    bad_K = 0
    bad_cf = 0
    for d in range(1, lim + 1):
        objs, starts, ends = wi_objects(d)
        # map SIGMA_d -> objects: 1-runs of u end at ends[j], start at a
        T = T_set(d)
        S = sig(d)
        fwd = {}
        for u in S:
            chosen, lows = [], []
            for (a, b) in one_runs(u):
                assert b in T
                j = ends.index(b) if b in ends else -1
                chosen.append(j)
                lows.append(a)
            fwd[u] = (tuple(chosen), tuple(lows))
        if sorted(fwd.values()) != sorted(objs) or len(set(fwd.values())) != len(S):
            bad_bij += 1
        # reconstruct u from the object
        for (chosen, lows) in objs:
            u = 0
            for j, a in zip(chosen, lows):
                for i in range(a, ends[j] + 1):
                    u |= (1 << i)
            if u not in S:
                bad_bij += 1
                break
        if len(objs) != len(S):
            bad_count += 1
        Lrun = run_lens(d)
        if len(objs) != continuant(Lrun) + continuant(Lrun[1:]):
            bad_K += 1
        # continued fraction of fusc(d)/fusc(d+1)
        pred = ([0] + Lrun) if d % 2 == 0 else Lrun
        if cf_eval(pred) != Fraction(fusc(d), fusc(d + 1)):
            bad_cf += 1
    note("T3b SIGMA_d <-> weighted-independent-set data (explicit, bijective)",
         "d <= %d" % lim, bad_bij)
    note("T3c #objects = |Sigma_d|", "d <= %d" % lim, bad_count)
    note("T3d #objects = K(L) + K(L[1:]) (continuants)", "d <= %d" % lim, bad_K)
    note("T3e fusc(d)/fusc(d+1) = [L_1;..;L_k] (d odd) / [0;L_1;..;L_k] (d even)",
         "d <= %d" % lim, bad_cf)

# =============================================================================
# T4  doubling: what works, what fails
# =============================================================================
def test_T4(lim):
    bad_even = 0
    bad_odd = 0
    bad_size = 0
    bad_chain = 0
    for e in range(0, lim + 1):
        Se = sig(e)
        dbl = set(2 * v for v in Se)
        for d in (2 * e, 2 * e + 1):
            if set(u for u in sig(d) if u % 2 == 0) != dbl:
                bad_even += 1
        # odd parts
        A = set(2 * v + 1 for v in Se if (v + e) % 2 == 1)
        B = set(2 * v + 1 for v in Se if (v + e) % 2 == 0)
        if A != set(u for u in sig(2 * e) if u % 2 == 1):
            bad_odd += 1
        if B != set(u for u in sig(2 * e + 1) if u % 2 == 1):
            bad_odd += 1
        # sizes
        if len(sig(2 * e)) - len(Se) != fusc(e):
            bad_size += 1
        if len(sig(2 * e + 1)) - len(Se) != fusc(e + 1):
            bad_size += 1
        # iterated (Calkin-Wilf ancestor chain) decomposition:
        #   Sigma_d  ~  {0} + sum_i Hyp(c_i),   n_0=d, n_{i+1}=floor(n_i/2),
        #   c_i = n_{i+1}-1 if n_i even else n_{i+1}
        n, pieces = e, []
        while n > 0:
            nxt = n // 2
            pieces.append(nxt - 1 if n % 2 == 0 else nxt)
            n = nxt
        if 1 + sum(len(hyp(c)) for c in pieces) != len(Se):
            bad_chain += 1
    note("T4a even part of Sigma_{2e} and of Sigma_{2e+1} both = 2*Sigma_e",
         "e <= %d" % lim, bad_even)
    note("T4b odd part of Sigma_{2e} = 2{v in Sigma_e: v+e odd}+1, of Sigma_{2e+1} = 2{v: v+e even}+1",
         "e <= %d" % lim, bad_odd)
    note("T4c |Sigma_{2e}|-|Sigma_e| = fusc(e), |Sigma_{2e+1}|-|Sigma_e| = fusc(e+1)",
         "e <= %d" % lim, bad_size)
    note("T4d |Sigma_d| = 1 + sum_i |Hyp(c_i)| along the CW ancestor chain",
         "d <= %d" % lim, bad_chain)

def test_lift(lim):
    """The canonical 'recursive lifting': the odd half of Sigma_d is a hyperbinary set.

        {v in Sigma_e : v+e odd }  <->  Hyp(e-1),   v |-> (v, (e-1-v)//2)
        {v in Sigma_e : v+e even}  <->  Hyp(e),     v |-> (v, (e-v)//2)

    Composed with u -> 2u+1 this gives the explicit recursive construction of
    Psi_d out of Psi_e, i.e. the induction step of theorem T1.
    """
    bad = 0
    for e in range(1, lim + 1):
        Se = sig(e)
        odd = set(v for v in Se if (v + e) % 2 == 1)
        even = set(v for v in Se if (v + e) % 2 == 0)
        img_odd = set((v, (e - 1 - v) // 2) for v in odd)
        img_even = set((v, (e - v) // 2) for v in even)
        if img_odd != set(hyp(e - 1)):
            bad += 1
        if img_even != set(hyp(e)):
            bad += 1
        # the two halves are exactly the even and odd parts of Sigma_{2e}, Sigma_{2e+1}
        if set(2 * v + 1 for v in odd) != set(u for u in sig(2 * e) if u % 2 == 1):
            bad += 1
        if set(2 * v + 1 for v in even) != set(u for u in sig(2 * e + 1) if u % 2 == 1):
            bad += 1
    note("T4f {v in Sig_e: v+e odd} <-> Hyp(e-1) and {v: v+e even} <-> Hyp(e) (lift)",
         "e <= %d" % lim, bad)

def test_shell_sum(lim):
    bad = 0
    S = [0]
    for d in range(0, 2 * lim + 1):
        S.append(S[-1] + len(sig(d)))
    for N in range(0, lim + 1):
        if S[2 * N] != 3 * S[N]:
            bad += 1
    note("T4e S(2N) = 3 S(N) for S(N) = sum_{d<N} |Sigma_d|", "N <= %d" % lim, bad)

# =============================================================================
# candidate maps that FAIL (with smallest counterexample)
# =============================================================================
def test_failures(lim):
    # (C1) u -> lengths of maximal 1-runs (i.e. the continued fraction of fusc(u)/fusc(u+1))
    first = None
    bad = 0
    for d in range(0, lim + 1):
        S = sig(d)
        im = [tuple(b - a + 1 for (a, b) in one_runs(u)) for u in S]
        if len(set(im)) != len(im):
            bad += 1
            if first is None:
                seen = {}
                for u, x in zip(S, im):
                    if x in seen:
                        first = (d, seen[x], u, x)
                        break
                    seen[x] = u
    obs("C1 u -> 1-run length vector is NOT injective: d with collisions", "%d of %d" % (bad, lim + 1))
    obs("C1 smallest collision", "d=%d: u=%d and u=%d both -> %s"
        % (first[0], first[1], first[2], first[3]))
    # (C2) u -> h = (d-u)//2
    first2 = None
    for d in range(0, lim + 1):
        seen = {}
        for u in sig(d):
            h = (d - u) // 2
            if h in seen:
                first2 = (d, seen[h], u, h)
                break
            seen[h] = u
        if first2:
            break
    obs("C2 u -> (d-u)//2 is NOT injective, smallest collision",
        "d=%d: u=%d and u=%d both -> h=%d" % first2)
    # (C3) u -> floor(u/2)  (the doubling projection): fibre sizes
    fib = {}
    for d in range(0, lim + 1):
        cnt = {}
        for u in sig(d):
            cnt[u // 2] = cnt.get(u // 2, 0) + 1
        for v in cnt.values():
            fib[v] = fib.get(v, 0) + 1
    obs("C3 fibre-size histogram of u -> floor(u/2) over all d",
        dict(sorted(fib.items())))
    # (C4) u -> (fusc(u), fusc(u+1))
    bad4 = 0
    for d in range(0, lim + 1):
        im = set((fusc(u), fusc(u + 1)) for u in sig(d))
        if len(im) != len(sig(d)):
            bad4 += 1
    note("C4 u -> (fusc(u),fusc(u+1)) injective (image not a natural set)",
         "d <= %d" % lim, bad4)
    # (C5) no bijection Sigma_d -> Hyp(d) alone
    same = [d for d in range(0, lim + 1) if len(sig(d)) == len(hyp(d))]
    obs("C5 d with |Sigma_d| = |Hyp(d)| (necessary for a bijection onto Hyp(d) alone)",
        str(same))
    # (C6) u -> fusc(u)/fusc(u+1): image description is not canonical
    obs("C6 image of u -> fusc(u)/fusc(u+1) for d=8",
        sorted(set("%d/%d" % (fusc(u), fusc(u + 1)) for u in sig(8))))

# =============================================================================
# further sanity identities
# =============================================================================
def test_sanity(lim):
    bad1 = 0
    bad2 = 0
    for d in range(0, lim + 1):
        if len(sig(d)) != fusc(d) + fusc(d + 1):
            bad1 += 1
        if len(sig(d)) != fusc(2 * d + 1):
            bad2 += 1
    note("|Sigma_d| = fusc(d)+fusc(d+1)", "d <= %d" % lim, bad1)
    note("|Sigma_d| = fusc(2d+1)", "d <= %d" % lim, bad2)

# =============================================================================
# demo tables
# =============================================================================
def demo():
    print("\n--- small table -----------------------------------------------")
    print(" d  |Sig|  (p,q)      Sigma_d                      Psi_d (u,h,tag)")
    for d in range(0, 13):
        S = sig(d)
        recs = [psi(d, u) for u in S]
        print(" %2d  %2d   (%d,%d)   %-26s %s"
              % (d, len(S), fusc(d), fusc(d + 1), S,
                 " ".join("(%d,%d,%d)" % r for r in recs)))
    print("\n--- run / CF normal form -------------------------------------")
    print(" d  runs L (LSB->MSB)   T(d)        CF(fusc(d)/fusc(d+1))  K(L)  K(L[1:])  |Sig|")
    for d in [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 13, 21, 42, 100, 127, 128]:
        Lr = run_lens(d)
        cf = [0] + Lr if d % 2 == 0 else list(Lr)
        print(" %3d  %-16s %-11s %-22s %4d  %6d  %4d"
              % (d, Lr, sorted(T_set(d)), cf, continuant(Lr), continuant(Lr[1:]), len(sig(d))))
    print("\n--- run data of one d (d = 42 = 101010) ----------------------")
    d = 42
    L = run_lens(d)
    ends = []
    pos = 0
    for x in L:
        ends.append(pos + x - 1)
        pos += x
    print("  runs of d:", run_data(d), " L =", L, " T(d) =", sorted(T_set(d)))
    for (chosen, lows) in sorted(wi_objects(d)[0])[:8]:
        u = 0
        for j, a in zip(chosen, lows):
            for i in range(a, ends[j] + 1):
                u |= (1 << i)
        print("    (hit %s | low bits %s)  <->  u = %-3d = %s"
              % (list(chosen), list(lows), u, bin(u)[2:]))
    print("  |Sigma_42| =", len(sig(42)), " fusc(42)+fusc(43) =", fusc(42) + fusc(43))

# =============================================================================
def main():
    print("=" * 78)
    print("322_brocot_bijection.py   --  explicit bijections for SIGMA_d")
    print("=" * 78)
    test_sanity(LIM_BIG)
    test_T1(LIM)
    test_T2(LIM_N)
    test_stern_matrices(LIM)
    test_T3a(LIM)
    test_T3b(LIM)
    test_T4(LIM)
    test_lift(LIM)
    test_shell_sum(LIM)
    test_failures(LIM)
    demo()
    print("\n" + "=" * 78)
    print("VERIFICATION SUMMARY   (every line must show 0 violations)")
    print("=" * 78)
    total = 0
    for (label, rng, bad) in CHECKS:
        total += bad
        print("  [%s]  %s\n      violations = %d" % (rng, label, bad))
    print("-" * 78)
    print("TOTAL VIOLATIONS:", total)
    print("STATUS:", "ALL CHECKS PASS" if total == 0 else "FAILURE")
    print("=" * 78)
    print("OBSERVATIONS (candidate maps that FAIL, and other side notes)")
    print("=" * 78)
    for (label, value) in OBS:
        print("  %s\n      -> %s" % (label, value))
    print("=" * 78)

if __name__ == "__main__":
    main()
