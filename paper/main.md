# The unanimity rule on any layered space: a geometry-independent closed form, an exact 2-kernel rank, and a uniqueness theorem

**Abstract.**
We study the binary cellular automaton whose local rule sets a cell to 1 exactly when all of its
neighbours (itself included) carry the same value — elementary rule 129, the "unanimity" rule.
For the line the zero set of the spacetime diagram has a closed form (implicit in OEIS A071051,
2014) and Wolfram observed in 2002 that the centre column enumerates the powers of two.
We prove that the closed form is **independent of the underlying geometry**: it needs only four
abstract hypotheses on the layer structure of the ambient space, and therefore holds simultaneously
for the line, for the plane with the von Neumann or Moore neighbourhood, and for the infinite binary
tree — three spaces whose neighbourhoods have different sizes and different symmetries.
The proof yields a *master law*: the number of zeros at time t is a **linear functional of the
layer-size sequence**, evaluated on a set shell(t) determined by a binary-digit condition.
We then compute the structure of this functional completely: a dual ("top of the dyadic block") form
of the digit condition, an exact formula for the 2-kernel rank of the zero-count sequence of any
level function, the distribution of the zero set over layers, and an exact self-similarity of the
cumulative counts. Finally we classify all 256 rules that depend only on three layer values: all of
them are geometry independent, exactly 8 of them admit a non-trivial dyadic contraction, those 8 form
two complementary orbits of 4, and no rule admits a non-trivial contraction with constant 3.
The whole development is formalised in Lean 4 (21 files, 395 declarations, no sorry, standard axioms
only).

**Keywords**: elementary cellular automaton; rule 129; unanimity rule; closed form; submask
condition; 2-regular sequence; 2-kernel; Stern's diatomic sequence; formal verification.

---

## 1. Introduction

Let (X, lev, N) be a set equipped with an integer *level* function lev: X -> N and a neighbourhood map
N: X -> P(X). Write c_d = #{y : lev(y) = d} for the *layer sizes*. We assume

* **(H1)** N(y) is contained in {z : lev(z) in {lev(y)-1, lev(y), lev(y)+1}};
* **(H2)** y is in N(y);
* **(H3)** if lev(y) >= 1 then N(y) meets layer lev(y)-1;
* **(H4)** every y has a neighbour of level lev(y)+1.

The *unanimity* automaton on such a space is the map on configurations x_t: X -> {0,1} given by

$$x_{t+1}(y) = 1 \iff \text{all values } x_t(z),\ z\in N(y),\ \text{are equal},$$

started from the single-1 configuration x_0(y) = [lev(y) = 0].

On the line this is elementary rule 129 (binary 10000001); on the plane with the von Neumann or Moore
neighbourhood it is the "all neighbours equal" rule used in physics as a caricature of consensus
formation; on the infinite binary tree it is the "parent, self and children all agree" rule. These
three automata have nothing in common at the level of local data: the neighbourhoods have 2-3, 4-9
and 3-4 elements respectively, and the tree has no translation symmetry at all.

We write S(t) for the set of levels that are *entirely zero* at time t, and

$$Z_c(t) := \sum_{d\in S(t)} c_d$$

for the number of zero cells at time t in the geometry whose layer sizes are c = (c_d).

### 1.1 Results

Write r(t) := t - 2^{floor(log2 t)} (so r(0) = r(1) = 0), and for naturals a, b let a subseteq b mean
that a is a *submask* of b, i.e. a AND b = a in binary.

* **Theorem 1 (layer invariance).** For *any* rule that reads only the three layer values, radial
  initial data stay radial and the profile satisfies a three-term recursion. Consequently the
  geometry enters only through the layer sizes c_d.
* **Theorem 2 (closed form).** x_t(y) = 0 iff lev(y) <= t and floor((t - lev(y))/2) subseteq r(t).
* **Theorem 3 (shell).** S(t) is the disjoint union over m subseteq r(t) of {t-2m, t-2m-1}, and
  #S(t) = 2^{wt(t)}, where wt is the binary digit sum.
* **Theorem 4 (master law).** Z_c(t) = sum over d in S(t) of c_d: the zero count is a linear
  functional of the layer-size sequence.
* **Theorem 5 (dual form).** With s := 2^{floor(log2 t)+1} - t,
  d is in S(t) iff (s-1) subseteq floor((s-1+d)/2).
* **Theorem 6 (rank).** Let c: N -> Q and suppose c(x) + c(x-1) = p(x) for all x >= 2, with
  p = sum_i gamma_i x^i. Put delta := c(1) + c(0) - sum_i gamma_i. Then
  rank_2(Z_c) = dim_Q span{A(k,j)^T gamma} + [delta != 0] = #DClose(supp gamma) + [delta != 0],
  where DClose(S) = {l : there is i in S with l <= i and l = i mod 2} and the matrices A(k,j) are
  defined in section 6.
* **Theorem 7 (columns).** #S_d = fusc(d) + fusc(d+1), where S_d := {u <= d : u subseteq
  floor((d-u)/2)} and fusc is Stern's diatomic sequence; moreover there is an explicit *bijection of
  sets* S_d -> H(d) disjoint-union H(d-1) with H(n) = {(u,h) : u AND h = 0, u + 2h = n}.
* **Theorem 8 (self-similarity).** T(N) := sum over d < N of (fusc(d) + fusc(d+1)) satisfies
  T(2N) = 3 T(N) for all N; equivalently T(N) = N^{log_2 3} F(log_2 N) with F exactly 1-periodic.
  The mass of one dyadic block of the spacetime diagram is 2 * 3^k.
* **Theorem 9 (rigidity).** Among the 256 rules that depend only on three layer values: all are
  geometry independent (Theorem 1); exactly 8 admit a non-trivial 2-contraction, forming two
  complementary orbits of four; and no rule admits a non-trivial c-contraction for c = 3, 5, 6, 7.

### 1.2 What is *not* new

Intellectual honesty requires recording the following before anything else.

* That the centre column of rule 129 encodes the powers of two is **stated in Wolfram's book
  A New Kind of Science (2002)** ("rule 129 can be thought of as enumerating numbers that are powers
  of 2", ch. 11) and is recorded in **OEIS A071035 (2002)** through the cross-reference
  "Cf. A036987 (central column)". The same fact was re-entered as a *conjecture* in A267442 (2016).
* The one-dimensional zero-count formula 2^{1+wt(t)} - [t = 2^i - 1] is **OEIS A071051**
  (N. J. A. Sloane, 2014-08-09), whose comment already identifies it as the number of ON cells of
  rule 126 (the colour-complement of 129).
* The fact that the per-layer counts are fusc(d) + fusc(d+1) is implicit in **OEIS A007306**
  (Cloitre, 2004: "number of odd entries in row n of the triangle of Stirling numbers of the second
  kind") and **A002487** (Carlitz's hyperbinary comment; and a comment counting odd Stirling numbers).
  The 2-regularity of these sequences is standard.
* Rule 129's Boolean form and its classification among "nested or fractal" rules are in
  A New Kind of Science (2002).

What is new is therefore **not a discovery but a proof, a generalisation and a structure**: the
geometry independence (Theorem 1 with Theorem 2), the master law (Theorem 4), the rank formula
(Theorem 6), the set-level bijection of Theorem 7, the exact self-similarity (Theorem 8) and the
rigidity statement (Theorem 9). We know of no statement of Theorems 1, 4, 6, 8 or 9 in the literature;
section 11 records the search we performed and its limitations.

---

## 2. Setting and the layer recursion

Fix a layered space (X, lev, N) satisfying (H1)-(H4). A configuration is x: X -> {0,1}. Call x
*radial* if x(y) depends only on lev(y); write p(d) := x(y) for any y of level d.

**Theorem 1 (layer invariance).** Let f: {0,1}^3 -> {0,1} be arbitrary, and let the automaton be
x_{t+1}(y) = f(x_t at level d-1, x_t at level d, x_t at level d+1) where d = lev(y) and, for d = 0,
the missing level -1 is replaced by the cell's own value. Then radial data stay radial, and the
profile obeys

$$p_{t+1}(d) = f(p_t(d-1), p_t(d), p_t(d+1))\ \ (d\ge 1),\qquad
  p_{t+1}(0) = f(p_t(0), p_t(0), p_t(1)).$$

*Proof.* Induction on t. By (H1) the neighbours of y lie in the three levels d-1, d, d+1; by the
induction hypothesis the multiset of their values is determined by d alone. The *number* of
neighbours in each layer is irrelevant because f reads values, not counts. ∎

**Corollary 1.1.** For a rule of this kind the profile is the same on every layered space; the
geometry appears only in c_d, i.e. in the weights of the master law below. In particular the
"geometry independence" of the unanimity automaton is a property of *layer rules*, not a miracle
attached to rule 129.

**Remark 2.1** (the boundary convention). For d = 0 the missing level -1 must be specified; we
replace it by the cell's own value ("dup"). This convention is part of the rule. With zero fill
instead, the closed form of Theorem 2 already fails at t = 5 on the line (dup gives the row 110000110
at t = 5, zero fill gives 010000110). Theorem 1 and the 256/256 statement of section 9 are independent
of the convention, but the classification of section 9 is not.

---

## 3. The closed form

For the unanimity rule f(a,b,c) = [a = b = c] the recursion of Theorem 1 becomes

$$p_{t+1}(d) = 1 \iff p_t(d-1) = p_t(d) = p_t(d+1).$$

**Theorem 2.** With x_0(y) = [lev(y) = 0] and r(t) = t - 2^{floor(log2 t)},

$$x_t(y) = 0 \iff \mathrm{lev}(y)\le t \ \text{ and }\ \left\lfloor\frac{t-\mathrm{lev}(y)}{2}\right\rfloor\subseteq r(t).$$

*Proof.* By Theorem 1 it suffices to prove the statement for the profile. This is an induction on t:
one checks that the right-hand side satisfies the three-term recursion of Theorem 1 at every level
d <= t, and that it equals 1 for d > t. The verification is purely a statement about binary digits:
the two cases t even and t odd correspond to r(t+1) = 2r(t) and r(t+1) = 2r(t) + 1, and
floor(((t+1)-d)/2) is obtained from floor((t-d')/2) by a shift. ∎

The formal proof is in the Lean development (F_step, row_closed_form); it is checked there for an
abstract layered space, so it covers the line, the plane with von Neumann or Moore neighbourhood and
the infinite binary tree simultaneously.

**Remark 3.1.** The formula is a statement about the *light cone* only. For lev(y) > t the value is 1:
the unanimity rule does not leave a uniformly zero exterior alone, it "ignites" it (whereas, e.g., the
parity rule 90 keeps it at zero). This is the reason why the shell below only contains levels d <= t.

**Remark 3.2.** The centre column (lev(y) = 0) vanishes exactly when floor(t/2) is a submask of r(t),
which happens exactly at t = 2^k - 1 (there both sides equal 2^{k-1} - 1; conversely, if floor(t/2) is
a submask of r(t) then every 1-bit of t below the leading one is already a 1-bit of r(t), and an
induction on the digit length shows t = 2^k - 1). This is the observation of Wolfram (2002) and of
A071035 (2002); Theorem 2 embeds it into a closed form for the whole diagram.

---

## 4. The shell and the master law

Define the *arm* and the *shell* of t by

$$\mathrm{arm}(t) := \{t-2m : m\subseteq r(t)\},\qquad
  S(t) := \mathrm{arm}(t)\cup(\mathrm{arm}(t)-1).$$

**Theorem 3.** S(t) is the disjoint union over m subseteq r(t) of {t-2m, t-2m-1}, and
#S(t) = 2^{wt(t)}.

*Proof.* Immediate from the definitions, using wt(t) = wt(r(t)) + 1 for t >= 1. ∎

**Theorem 4 (master law).** For every level-size sequence c: N -> Z,

$$Z_c(t) = \sum_{d\in S(t)} c_d.$$

*Proof.* By Theorem 2 the set of zero levels at time t is exactly S(t); sum the layer sizes. ∎

Theorem 4 is the reason the subject is tractable: the automaton's zero set is a *fixed* set of
levels, independent of the geometry, and the geometry enters only through the weights c_d. Every
statement below is a statement about the functional c -> sum over d in S(t) of c_d.

**Remark 4.1.** Theorem 3 gives the size of the zero set as Gould's sequence 2^{wt(t)} (OEIS A001316),
so Theorem 4 says that the zero count of any geometry is a weighted Gould sum.

---

## 5. The dual form

**Theorem 5.** Let t >= 1 and s := 2^{floor(log2 t)+1} - t (so 1 <= s <= 2^{floor(log2 t)}). Then for
every d <= t,

$$d\in S(t) \iff (s-1)\subseteq \left\lfloor\frac{s-1+d}{2}\right\rfloor.$$

*Proof.* Put k = floor(log2 t), so t = 2^k + r(t) and s = 2^k - r(t). By Theorem 2, d is in S(t) iff
m := floor((t-d)/2) is a submask of r(t). Now t - d = 2^{k+1} - s - d, hence
m = 2^k - ceil((s+d)/2). Since 2^k - x is the k-bit complement of x - 1, the submask relation
2^k - a subseteq 2^k - b is equivalent to b - 1 subseteq a - 1. Taking a = ceil((s+d)/2), b = s, and
using ceil((s+d)/2) - 1 = floor((s-1+d)/2), the claim follows. ∎

Theorem 5 says that the time t enters the state only through the distance s to the *next* power of
two. Equivalently, the radial spacetime diagram is periodic in the dyadic direction: the inner part
of the light cone at time 2^{k+1} - s is the same for all k. This is what makes the *columns* of the
diagram, as opposed to its rows, tractable.

---

## 6. The 2-kernel rank

Let T_c(N) := Z_c(N) be the zero-count sequence of Theorem 4. Its 2-kernel is
{N -> T_c(2^k N + j) : k >= 0, 0 <= j < 2^k}, and rank_2(T_c) denotes the dimension over Q of its
span (equivalently: T_c is 2-regular of that rank in the sense of Allouche and Shallit).

Define the *arm moments* Phi_i(t) := sum over m subseteq r(t) of (t-2m)^i and the centre indicator
eps(t) := [1 is in arm(t)] (equivalently [0 is in S(t)]; eps(t) = 1 iff t = 2^i - 1).

**Lemma 6.1** (decomposition; proved in Lean as shell_sum_of_poly_correction). Let c: N -> Q and
suppose that for all x >= 2

$$c(x)+c(x-1) = p(x) = \sum_{i=0}^{D}\gamma_i x^i .$$

Put delta := c(1) + c(0) - sum_i gamma_i, the defect of the polynomial description at the single point
x = 1. Then

$$Z_c(t) = \sum_{i=0}^{D}\gamma_i\,\Phi_i(t) \;+\; \delta\,\varepsilon(t).$$

If c is a polynomial then delta = 0; if c_d equals a polynomial c-hat(d) for d >= 1 while c_0 differs
from c-hat(0) — the case of a genuine geometry with a single centre cell — then delta is non-zero in
general.

**Lemma 6.2** (transfer). Let j = sum_{i<k} b_i 2^i and A(k,j) := M_{b_0} M_{b_1} ... M_{b_{k-1}},
with the leftmost factor b_0, where

$$M_0 = \mathrm{diag}(2^i),\qquad
M_1[i][l] = \binom{i}{l}2^{l+1}\ \ (l\le i,\ l\equiv i \pmod 2),\quad M_1[i][l]=0\ \text{otherwise}.$$

Then, in closed form,

$$A(k,j)[i][l] \;=\; 2^{kl}\,\binom{i}{l}\,S_j(i-l),\qquad
  S_j(d) := \sum_{m\subseteq j}(j-2m)^d .$$

*Proof.* The arm recursion arm(2^k n + j) = {2^k x + (j-2m) : x in arm(n), m subseteq j} gives, for the
exponential generating function phi(t;y) := sum over x in arm(t) of e^{xy}, the identity
phi(2^k n + j; y) = sum over m subseteq j of e^{(j-2m)y} phi(n; 2^k y); comparing coefficients of y^i
yields the formula. ∎

Two consequences do all the work.

* **(C1)** k enters only through the diagonal factors 2^{kl}; hence, for fixed j, the vectors
  A(k,j)^T gamma are the values of a *weighted Vandermonde* at the nodes 2^l.
* **(C2)** S_j(d) = 0 for odd d, because m -> j - m is an involution of the submasks with
  j - 2(j-m) = -(j-2m). Hence the l-th coordinate of A(k,j)^T gamma only involves gamma_i with i >= l
  and i = l mod 2, i.e. supp(A^T gamma) is contained in DClose(supp gamma).

**Theorem 6.** With the notation of Lemmas 6.1 and 6.2,

$$\mathrm{rank}_2(T_c) = \#\mathrm{DClose}(\mathrm{supp}\,\gamma) + [\delta\ne0].$$

*Proof (sketch).* The Phi_i and eps are linearly independent, and eps(2^m) = 0, so eps contributes
exactly one dimension iff delta is non-zero; hence the rank is dim span{A(k,j)^T gamma} + [delta != 0].
By (C2) the span sits inside Q^{DClose(supp gamma)}. For the reverse inequality take j = 2^m: the
coefficients w_a^{(eps)}(2^m) of A(2^m,j)^T gamma in the two parity classes are, as functions of
z = 4^m, polynomials of degree exactly A_eps - a, where A_eps = max{i in supp gamma : i = eps mod 2}.
Hence at most A_0(A_0+1)/2 + A_1(A_1+1)/2 values of m are bad, and for every other m the
#DClose vectors obtained for k = m+1, ..., m + #DClose form a Vandermonde system with non-zero
weights, hence are independent. ∎

**Remark 6.3.** The frequently quoted rule of thumb "rank = deg c + 1 + [centre patch]" is the special
case in which supp gamma is *dense*, i.e. contains every second exponent up to its maximum. All
thirteen geometries tabulated in our earlier reports happen to have dense support, which is why the
rule of thumb survived so long. It is false in general: for c(x) = x^2 + x one has p(x) = 2x^2 and
rank 2, not 1; for c(x) = 2x^2 + 4x + 1 one has p(x) = 4x^2 + 4x and rank 3, not 2.

---
## 7. The columns: layer distribution and a set-level bijection

For a single level d let S_d := {u <= d : u subseteq floor((d-u)/2)} be the set of *dead offsets*:
u is in S_d iff level d is dead at the times t whose distance to the next power of two is u+1
(Theorem 5).

**Theorem 7.** Let fusc be Stern's diatomic sequence (fusc(0) = 0, fusc(1) = 1, fusc(2n) = fusc(n),
fusc(2n+1) = fusc(n) + fusc(n+1)) and H(n) := {(u,h) : u AND h = 0, u + 2h = n}. Then

1. #S_d = fusc(d) + fusc(d+1) = fusc(2d+1);
2. the map u -> ((u, floor((d-u)/2)), (d-u) mod 2) is a **bijection** from S_d onto the disjoint union
   of H(d) and H(d-1) (the inverse is the projection to the first coordinate);
3. #H(n) = fusc(n+1);
4. u is in S_d iff every maximal block of 1's [a,b] of u satisfies b in T(d) and d is constant on
   [a,b], where T(d) = {i : d_i != d_{i+1}} is the set of positions where two consecutive binary
   digits of d differ.

*Proof.* (2) is immediate from the definition: u is in S_d iff u AND floor((d-u)/2) = 0, and
h = floor((d-u)/2) satisfies u + 2h = d or d-1 according to the parity of d-u. (3) follows from the
recursions H(2m) = 2H(m) disjoint-union (2H(m-1) + (0,1)) and H(2m-1) = 2H(m-1) + (1,0), whose
transfer matrices are [[1,0],[1,1]] and [[1,1],[0,1]] — the left and right children of the
Stern-Brocot tree. (1) follows from (2) and (3). (4) is an induction on d from the parity recursion
S_{2e} = 2S_e disjoint-union {2v+1 : v in S_e, v+e odd}, S_{2e+1} = 2S_e disjoint-union
{2v+1 : v in S_e, v+e even}. ∎

**Remark 7.1.** Statements (1) and (3) are classical (Cloitre 2004, Carlitz; section 1.2).
Statement (2) is the *set-level* statement that turns them into statements about the automaton, and
(4) is a structural description of the dead offsets that we have not found elsewhere.

---

## 8. Exact self-similarity

**Theorem 8.** Let T(N) := sum over d < N of (fusc(d) + fusc(d+1)) and W(N) := sum over t < N of
2^{wt(t)}. Then

1. T(2N) = 3 T(N) for all N, hence T(N) = N^{log_2 3} F(log_2 N) with F exactly 1-periodic;
2. T(2^k) = 3^k; W(2^k) = 3^k; and the mass of one dyadic block,
   sum over 2^k <= t < 2^{k+1} of 2^{wt(t)}, equals 2 * 3^k.

*Proof.* Write U(N) := sum over d < N of fusc(d); then T(N) = 2U(N) + fusc(N). Splitting U(2N) into
even and odd indices and using the two Stern recursions gives U(2N) = U(N) + T(N) = 3U(N) + fusc(N),
whence T(2N) = 2U(2N) + fusc(2N) = 6U(N) + 3 fusc(N) = 3T(N). For W, split the sum over t < 2^{k+1}
into even and odd t and use wt(2t) = wt(t), wt(2t+1) = wt(t) + 1. ∎

The point of Theorem 8 is the word *exactly*: for the classical summatory function of the digit sum
there is a Delange-type asymptotic with a non-trivial fractal error term, whereas here the normalised
summatory function is exactly a periodic function of log_2 N — there is no error term at all.

---

## 9. Rigidity: the census of layer rules

By Theorem 1, geometry independence is not special. What *is* special is the existence of a closed
form of dyadic type. To say what "the 2^k - 1 pattern" means, we use the following.

**Definition 9.1.** A rule r has *contraction constant c with base t_0* if for all t >= t_0

$$\mathrm{row}[ct+c-1] = D_c(\mathrm{row}[t]),$$

where D_c duplicates every cell c times. The epoch times are then t_k = (t_0+1)c^k - 1; for
c = 2, t_0 = 1 these are 1, 3, 7, 15, ... = 2^k - 1, and for c = 3, t_0 = 2 they are 2, 8, 26, 80, ...
= 3^k - 1. A rule is *trivial* for this purpose if its row is eventually constant on the cone.

**Theorem 9.** Among the 256 rules f: {0,1}^3 -> {0,1} (all rules that depend only on three layer
values), with the boundary convention of Remark 2.1:

1. all 256 are geometry independent (Theorem 1);
2. exactly 8 have a non-trivial contraction with c = 2: {90, 94, 122, 126, 129, 133, 161, 165};
3. these split into two orbits of four, {129, 133, 161, 165} and {90, 94, 122, 126}, within which the
   four rules have *identical* spacetime diagrams (the free truth-table entries f(010), f(101) are
   never read); the two orbits are colour complements of each other, and
   x_t^{129}(d) = 1 - [floor((t-d)/2) subseteq r(t)], x_t^{90}(d) = [floor((t-d)/2) subseteq r(t)];
4. every rule satisfying the c-law for c = 3 (respectively 5, 6, 7) is trivial; for c = 4 the law is
   implied by the c = 2 law.

*Proof.* (1) is Theorem 1. For (2)-(4) the argument is a finite case analysis on the eight truth-table
entries together with an induction along the "constant row" criterion: if the profile is eventually
constant with value cc on background bb, it stays constant iff f(cc,cc,cc) = f(cc,cc,bb) = f(cc,bb,bb),
and the pair (cc,bb) then evolves on a two-element cycle. Checking this criterion for all 256 rules
and the candidate bases yields (2)-(4); the enumeration is in scripts/320_layer_rules.py. The closed
forms in (3) are Theorem 2 and its complement. ∎

**Remark 9.2.** Clause (4) is the precise sense in which "there is no 3^k - 1 family": not only does
the scan find none, but a c-law that holds from t = 0 forces the cone to be identically 1. The
unanimity rule escapes because its law starts at t = 1.

---

## 10. Formal verification

The development is formalised in Lean 4 with Mathlib. All files are in the directory lean/; the build
order and the per-file content are in lean/README.md.

| item | value |
|---|---|
| files / declarations | 21 / 395 |
| axioms | propext, Classical.choice, Quot.sound only |
| occurrences of sorry | none |
| audit | every .olean deleted and rebuilt from scratch; exit code 0 |

Main formalised statements (Lean names): row_closed_form and F_step (Theorem 2, for an abstract
layered space and for the three instances); card_shell and shell_eq_image (Theorem 3);
row_zero_pos_eq_shell (Theorem 4); mem_shell_dual (Theorem 5); shell_sum_of_poly_correction, X_iterate,
W_eq_A and Z_row_linear (Lemmas 6.1 and 6.2); card_sig_stern (Theorem 7.1), card_Hyp and
card_sig_split (Theorem 7.2 and 7.3); SS_two_mul, SS_two_pow, sum_pow_wt and block_shell_mass
(Theorem 8). The rank formula of Theorem 6 is proved on paper (section 6) and checked numerically, but
it is *not* yet formalised; neither is Theorem 9.

---

## 11. Literature and its limits

We searched: the OEIS (a local snapshot of 400,725 sequences, plus live queries), the arXiv API
(metadata only), a web search API, and the full text of A New Kind of Science, extracted locally from
the chapter PDFs (9.8 million characters). We did **not** search MathSciNet or zbMATH (subscription
walls), nor journal full texts. The phrase "all neighbours equal" occurs in no OEIS entry, and the
arXiv query all:"rule 129" returns zero hits. The closest works are Martin, Odlyzko and Wolfram (1984)
on algebraic properties of *linear* cellular automata — rule 129 is nonlinear, so that theory does not
apply — and the recent study "Cellular automata that generate symmetrical patterns give singular
functions" (arXiv:2203.05236), which concerns limit functions of linear rules. Both are
methodologically disjoint from Theorem 1.

We therefore describe the results above as *new as far as our search reached*, and not as new.

---

## 12. A methodological note

Three of our own claims were refuted during this work. We record them because they are the most
transferable part of the experience.

1. **A rank formula calibrated on dense examples is false in general.** The formula
   rank_2 = #supp(c(x)+c(x-1)) holds on every example in which the support is dense, and fails in 78
   of 625 small polynomials; the correct quantity is #DClose (Remark 6.3).
2. **A set-level guess based on counting can fail.** We conjectured
   [d in S(t)] = binom(t, (t+d)/2) mod 2; it fails in 110 of 819 cases. The row direction of the
   diagram is a statement about *counts* (Gould), not about sets.
3. **A transfer-matrix product must be assembled in the recursion order.** Testing the formula of
   Lemma 6.2 with the factors reversed produced 216 spurious counterexamples out of 1920 entries.

The pattern is the same in all three cases: a formula that is correct on a *generic* sample can be
wrong exactly where the sample is degenerate, and dense or generic samples are precisely the ones that
occur in the natural geometries.

---

## Appendix A. Verification scripts

| script | what it checks | range |
|---|---|---|
| scripts/265_tree.py | tree middle column | t <= 60 |
| scripts/291_arm_recursion.py | the arm recursion | — |
| scripts/292_two_kernel_rank.py | 2-kernel ranks of fifteen level functions | K <= 7, M = 40 |
| scripts/307_dual_form.py | Theorem 5 | all t <= 16384, all d (1.3e8 cases) |
| scripts/308_stern.py | Theorem 7.1 and the block sums | d <= 4000, k <= 11 |
| scripts/311_stern_proof.py | the four parity recursions of Theorem 7.4 | d <= 400 |
| scripts/313_nocarry.py | the no-carry lemma and Theorem 7.3 | u,h < 300; n < 800 |
| scripts/314b_block_count.py | per-block counts from the shell | k <= 15 |
| scripts/315_survey.py | block mass, the Gould identity, hyperbinary representations | k <= 12 |
| scripts/317b_selfsimilar.py | T(2N) = 3 T(N) | N < 32768 |
| scripts/320_layer_rules.py | Theorem 9 | all 256 rules, t <= 200 |
| scripts/321_rank_measure.py | Theorem 6 | 1016 polynomials, K <= 7 |
| scripts/322_brocot_bijection.py | Theorem 7.2 | d <= 2000 |
| scripts/323_stirling_proof.py | the Stirling side of Theorem 7.1 | n <= 4000 |
| scripts/325_verify_brocot.py | Theorems 7.2-7.4, independently | d <= 599 |
| scripts/326b_verify_rank.py | Theorem 6, independently | 625 polynomials |
| scripts/333b_A_formula.py | Lemma 6.2 | 1920 matrix entries |

Every number quoted in the text is reproduced by one of these scripts, run as "py -3 <script>"; none
of them needs a third-party package except numpy, used by one.

## Appendix B. OEIS cross-references

| ours | OEIS |
|---|---|
| #S(t) = 2^{wt(t)} | A001316 (Gould) |
| Z_{1D}(t) = 2^{1+wt(t)} - [t = 2^i - 1] | A071051 (Sloane 2014) |
| centre column of rule 129 | A267442 (Price 2016), zeros at 2^k - 1; cf. A267444 |
| ON-cell count of rule 129 | A267445 = 2t + 1 - Z_{1D}(t) |
| fusc | A002487 (Stern) |
| #S_d = fusc(2d+1) | A007306, offset d+1 (Cloitre 2004) |