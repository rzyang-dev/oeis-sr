# Rule 129 from a single cell: exact closed form

**Setting.** Infinite line, binary cells. Rule 129: x(t+1,j) = 1 iff x(t,j-1) = x(t,j) = x(t,j+1)
("all three parents equal"). x(0,j) = 1 iff j = 0. Let Z(t) = {j : x(t,j) = 0}, and
E_t = {j : x(t,j) != x(t,j+1)} (edges/domain walls).

**Notation.** s_2(n) = number of 1-bits.  r(t) := t - 2^{floor(log2 t)}  = t with its leading
1-bit deleted ("tail" of t).  "s subset-of r(t)" means the bitwise submask relation s & r(t) == s.
For t = 0, r is undefined and the row is special.

---

## 1. Main theorem

For every t >= 1 and every integer j:

    x(t,j) = 0   <=>   |j| <= t   and   floor((t-|j|)/2)  is a bitwise submask of  r(t),

i.e.  x(t,j) = 1 - [|j| <= t] * [ floor((t-|j|)/2) & r(t) == floor((t-|j|)/2) ].
Special case:  x(0,j) = [j = 0].

### Equivalent forms

(a) **Zero set.**  Z(t) = { +-(t-2s), +-(t-2s-1) : s submask of r(t) }.
    Zeros come in pairs {t-2s-1, t-2s}; pairs from consecutive submasks merge.  The maximal
    zero intervals are  [t-2b-1, t-2a]  for each maximal run a..b of consecutive submasks of r(t).

(b) **Depth profile** (cleanest verbal form).  Put d = t - |j| (depth inside the light cone,
    0 <= d <= t).  Then

        x(t, t-d) = 1 - [ floor(d/2) subset-of r(t) ],
        in particular  x(t,t-2s) = x(t,t-2s-1) = 1 - [s subset-of r(t)].

    Reading inward from either light-cone edge, row t is the complement of the Gould/Sierpinski
    row of r(t), with every bit duplicated:  value 1-[s submask of r(t)] on the pair of depths
    (2s, 2s+1).  (Gould row: G_r(s) = [s submask of r].)

(c) **Era recursion.**  Let R(t) = Z(t) intersect [0,inf).  For t = 2^K + m, 0 <= m < 2^K:

        m <  2^(K-1):   R(t) = 2^(K-1) + R(t - 2^(K-1))          (push the old zero set outward)
        m >= 2^(K-1):   R(t) = R(m) union (2^K + R(m))            (two copies of R(m))

    This is the only non-elementary lemma; (a),(b), the middle-cell result etc. are algebra
    from it.  Case 1 takes each zero j of row t-2^(K-1) to |j| + 2^(K-1) and mirrors it;
    case 2 places copies of R(m) at offsets 0 and 2^K (then mirrors).

---

## 2. Consequences (all verified numerically)

* **Middle cell (A267442).**  x(t,0) = 0  <=>  floor(t/2) submask of r(t)  <=>  t = 2^k - 1.
* **Counts.**  |Z(t) intersect [0,t]| = 2^{s_2(t)};  |E_t| = 2^{s_2(t+1)}.
* **Depth pairs.**  x(t,j) = x(t,j-1) whenever t-j is even (j>=1).  Hence row t is determined
  by its values on the pairs (t-2s, t-2s-1).
* **Light cone.**  x(t,j) = 1 for |j| >= t+1 (t>=1);  x(t,+-t) = 0.
* **Full rows.**  For t = 2^k - 1 the row is all zeros on [-t,t] (r(t)=2^(k-1)-1 has all
  submasks below 2^(k-1)).
* **Edge process.**  E_t evolves by elementary CA rule 18:
      e_{t+1}(j) = (1 - e_t(j)) AND (e_t(j-1) XOR e_t(j+1)),
  from e_0 = {-1,0}.  Equivalently Z(t+1) = E_t union (E_t + 1).
* **Edge renormalisation** (verified m <= 599):
      R_{2m+1} = 2 R_m + 1                    (R_t := E_t intersect [0,inf))
      R_{2m}   = 2 (Z(m) intersect [0,inf)) = 2 ( R_{m-1} union (R_{m-1}+1) ).
  In pointwise form:  e_{2m+1}(2i+1) = e_m(i);   e_{2m}(2i) = 1 - x(m,i).
* **Parity invariant.**  Every edge at time t satisfies: j < 0 => j = t+1 (mod 2);
  j >= 0 => j = t (mod 2).
* **e_t(0) theorem.**  e_t(0) = 1  <=>  t+2 is a power of 2.
* **Full-alternating rows.**  At t = 2^k - 2:
      E_t = { j : -(t+1) <= j <= t, j = t (mod 2) if j>=0, j = t+1 (mod 2) if j<0 },
  and |E_t| = t+2 = 2^k.
* The naive relation "state(2^k+m) is a shifted copy of state(m)" is FALSE in general
  (counterexample: t=9=8+1: R(9)={6,7,8,9} but R(1) union (8+R(1)) = {0,1,8,9});
  it holds only in the second half of a binary era, in the duplicated form (c).

---

## 3. Inductive proof of e_t(0) = 1 <=> t+2 = 2^k

Ingredients (both verified):
  (A) odd times:  R_{2m+1} = 2R_m+1, so no edge sits at 0 (all elements odd);
  (B) even times: e_{2m}(2i) = 1 - x(m,i)  (from the closed form; equivalently R_{2m} = 2(Z(m) cap [0,inf)));
  (C) symmetry/centre:  x(t,0) = 1 - e_{t-1}(0)   (because e_{t-1}(-1) = e_{t-1}(0) by
      reflection symmetry, and x(t,0)=1 iff both those edges vanish).

Proof by strong induction on t.
  * t odd: by (A) e_t(0)=0; and t+2 is odd and > 1, hence not a power of 2.
  * t = 2m >= 2: by (B), e_{2m}(0) = 1 - x(m,0); by (C), 1 - x(m,0) = e_{m-1}(0).
    So e_{2m}(0)=1 <=> e_{m-1}(0)=1 <=> (induction) (m-1)+2 = m+1 = 2^j <=> t+2 = 2^(j+1).
  * base t=0: e_0 = {-1,0}, e_0(0)=1, and 0+2 = 2.

---

## 4. Lemmas a formal proof needs

L1 (light cone).  For t>=1, x(t,j)=1 for |j|>=t+1 and x(t,+-t)=0.  (Easy induction.)

L2 (interior rule / edges).  x(t+1,j)=1 iff the triple at t is constant; hence the 1s at t+1 are
    exactly the interiors of the maximal monochromatic runs of length >= 3 at time t, i.e.
    Z(t+1) = E_t union (E_t+1), and E evolves by rule 18.  (Direct from the definition.)

L3 (era recursion).  The statement in 1(c).  This is the crux.  Two equivalent forms:
    * 2-step renormalisation of the edge CA (rule 18): R_{2m+1} = 2R_m+1 and
      e_{2m}(2i) = 1 - x(m,i), both provable by composing rule 18 twice and using the parity
      structure of E_m;
    * or the run-shrinking dynamics: under one step every maximal run of either colour of
      length L >= 3 becomes a 1-run of length L-2, and every colour boundary becomes 2 zeros,
      so the run-length word transforms by  (l_1,...,l_M) -> 2, l_1-2, 2, l_2-2, ..., l_M-2, 2
      (dropping non-positive entries and merging the neighbouring zero runs).  Iterating this
      over an era yields 1(c).

L4 (submask induction).  Write each zero pair as {t-2s-1, t-2s} and let
    X(t) := { t - 2s - 1 : s submask of r(t) }  be the set of left endpoints, so that
    Z(t) = +-( X(t) union (X(t)+1) ).  Put Y(t) := t - X(t).  Then 1(c) becomes
      Y(t) = Y(t-2^(K-1))                      (case m < 2^(K-1)),
      Y(t) = Y(m) union (2^K + Y(m))           (case m >= 2^(K-1)),
    and induction on the binary digits of t (base Y(1)={1}) gives
      Y(t) = { 2s+1 : s submask of r(t) },   i.e.   X(t) = { t-2s-1 : s submask of r(t) },
    which is the theorem.  (Equivalently, with the full right half W(t) := t - R(t) one gets
    W(t) = { 2s, 2s+1 : s submask of r(t) }.)  Rigorous, purely algebraic.

Alternative self-contained route: prove form 1(b) by induction on t.  In depth coordinates the
one-step rule is v'(d) = [v(d-1)=v(d)=v(d+1)] with v(d)=1 for d<0 and v(d)=v(2t-d) (reflection
through the centre).  Since r(t+1) = r(t)+1 except when t+1 is a power of two, the induction
step splits into three cases: r(t) even, r(t) odd, r(t) = 2^j - 1; in each case the doubled
Gould row of r(t) is carried to that of r(t)+1 by the local rule (a finite check).

---

## 5. Evidence (what was actually verified)

Simulation: bit-arithmetic implementation on a fixed window [-W,W] (cells outside set to 0),
trusting a cell only when its dependency cone fits: |j| + t <= W.  Two independent
implementations (big-int bitmask; plain list-based) agree for t <= 300.

| check | range | result |
|---|---|---|
| closed form, every cell | t <= 2000, all j, 0<=j<=t (and mirrored j<0), W=4200 | 0 mismatches |
| closed form, random cells | 250 random t <= 20000 x 120 random j, W=40001 | 0 mismatches in 30000 cells |
| window independence | W vs W+300, t<=500, |j|<=430 | identical |
| light cone (no zeros with t<|j|<=W-t-2) | t <= 2000 | 0 violations |
| middle column (A267442) | t <= 2000 | 0 violations |
| |Z(t) cap [0,t]| = 2^s_2(t) | t <= 2000 | 0 violations |
| era recursion 1(c) from simulation | t <= 999 | 0 violations |
| depth-pair property | t <= 2000 (direct check) | 0 violations |
| zero intervals = [t-2b-1,t-2a] over runs of submasks | t <= 700 | exact (ordering aside) |
| edge CA = rule 18 | t <= 1199 | 0 violations |
| R_{2m+1} = 2R_m+1 | m <= 599 | 0 violations |
| R_{2m} = 2(R_{m-1} u (R_{m-1}+1)) | m <= 599 | 0 violations |
| parity invariant | t <= 1199 | 0 violations |
| x(t,0) = 1 - e_{t-1}(0) | t <= 1199 | 0 violations |
| e_t(0)=1 <=> t+2 = 2^k | t <= 1199 | 0 violations |
| full-alternating at t=2^k-2 | k <= 10 | exact |
| |E_t| = 2^{s_2(t+1)} | t <= 2000 | 0 violations |
| closed-form edge formula | t <= 1000 | 0 violations |

Counterexample to the parent's claim "|E_{2^k+m}| = 2|E_m|": k=1, m=1 gives |E_3| = 2 but
2|E_1| = 4.  The exact law is |E_t| = 2^{s_2(t+1)}; the claim holds iff m+1 < 2^k (no carry),
and the failures are the full-alternating rows m = 2^k - 1 (and other carry cases).

Counterexample to naive form (iv): t=9=2^3+1: R(9)={6,7,8,9}, R(1)={0,1}; neither a shift nor
a union of copies reproduces R(9).  The correct statement is 1(c) (second half only).

Pitfall confirmed: a window whose boundary is treated as 0 produces spurious zeros on the
boundary ring; e.g. at time 2 a radius-20 window shows extra zeros at +-20.  All checks above
respect the dependency cone.

---

## 6. Confidence

High.  The closed form is exact, has a short algebraic derivation from one combinatorial lemma
(era recursion), and was checked exhaustively on every cell of the light cone for t <= 2000,
plus random cells up to t = 20000, with two independent simulators.  The only unproved step is
L3; it is reduced either to a two-step local computation for rule 18 or to the stated
run-length dynamics.
