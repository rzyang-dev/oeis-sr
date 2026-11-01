# Lean formalization: OEIS automatic-sequence identities

## Index of the rule-129 / shell-scaling development (21 files, 395 declarations)

| File | Imported by | Declarations | Content |
|---|---|---|---|
| `Universal.lean` | Shells, Census | 101 | the universal closed form, (H1)-(H4), the radial / Moore / tree instances |
| `Shells.lean` | Final, Census, Parity | 24 | shell set, `card_shell`, `sigma_shell`, zero set = levels in the shell |
| `Instances.lean` | Final | 8 | b-ary tree and d-dimensional Moore middle columns |
| `Final.lean` | — | 16 | zero count = Σ c_d, the full 1-D window, Moore quarter plane, power-of-two layer |
| `Census.lean` | Tree | 6 | submask transform, linear level sizes, observability |
| `Tree.lean` | Moments | 20 | b-ary tree product formula, `bits`, popcount form |
| `Parity.lean` | — | 4 | the alternating kernel (as many even as odd levels) |
| `Moments.lean` | ShellSq, Cubic | 3 | `Q` and the second submask moment |
| `ShellSq.lean` | Dim3, Cubic | 4 | three moment relations + `shell_sum_sq` (second moment of the shell) |
| `Dim3.lean` | — | 3 | quadratic level sizes, Z³ von Neumann and Moore in closed form |
| `Cubic.lean` | Dim4 | 5 | third submask moment, two cube relations, `cube_key`, `shell_sum_cube` |
| `Dim4.lean` | — | 5 | cubic level sizes, Z⁴ Moore and von Neumann in closed form |
| `Arm.lean` | Rep | 19 | the arm, the two-step recursion, arm moments + transfer matrices, the decomposition theorem |
| `Rep.lean` | Digits | 16 | the centre indicator recursion, the refined decomposition, and all 13 polynomial rows through arm moments |
| `Digits.lean` | Matrix | 11 | the state vector, the two transfers, the digit iteration, the finite-state theorem |
| `Matrix.lean` | — | 16 | explicit transfer matrices, the k-fold matrix, the explicit representation, closed forms for the six degree ≤ 1 rows |
| `Brocot.lean` | Dual | 48 | the no-carry lemma, the dead-offset set `sig`, `mem_sig_iff`, the four parity recursions, and **`card_sig_stern : (sig d).card = fusc d + fusc (d+1)`** (see docs/52, docs/53) |
| `Dual.lean` | SelfSim | 12 | the `testBit` API for complements inside `2^k - 1`, the complement lemma `land_pow_sub_eq`, and **`mem_shell_dual`** (the dual closed form) |
| `SelfSim.lean` | — | 16 | `SS_two_mul : S(2N) = 3*S(N)`, `SS_two_pow : S(2^k) = 3^k`, the popcount weight, `sum_pow_wt : Σ_{t<2^k} 2^wt(t) = 3^k` (Gould) and `block_mass : 2*3^k` |
| `Mass.lean` | Hyp | 5 | `bits_card_eq_wt`, `shell_card_eq : (shell t).card = 2^wt(t)`, `shell_card_sum_pow : Σ_{t<2^k} |shell t| = 3^k`, `block_shell_mass : 2*3^k` |
| `Hyp.lean` | — | 19 | hyperbinary representations `Hyp n = {(u,h) : u &&& h = 0, u+2h = n}`; **`card_Hyp : (Hyp n).card = fusc (n+1)`**; `card_sig_split : (sig d).card = (Hyp d).card + (Hyp (d-1)).card` |

Build order: `Universal` (3 min, needs mathlib), then each of the others (40 s each).
`lean -o X.olean X.lean` produces the artifact the later files import.

Toolchain: Lean 4.34.1 + mathlib (already built at
`C:\Users\ginger\my_math_project`). Nothing here downloads or updates
anything: we compile with the local `lean` binary and a `LEAN_PATH` that
points at the existing mathlib build artifacts.

## Build

```powershell
$env:LEAN_PATH="C:\Users\ginger\my_math_project\.lake\build\lib\lean;
C:\Users\ginger\my_math_project\.lake\packages\mathlib\.lake\build\lib\lean;
C:\Users\ginger\my_math_project\.lake\packages\batteries\.lake\build\lib\lean;
C:\Users\ginger\my_math_project\.lake\packages\aesop\.lake\build\lib\lean;
C:\Users\ginger\my_math_project\.lake\packages\Qq\.lake\build\lib\lean;
C:\Users\ginger\my_math_project\.lake\packages\plausible\.lake\build\lib\lean;
C:\Users\ginger\my_math_project\.lake\packages\proofwidgets\.lake\build\lib\lean;
C:\Users\ginger\my_math_project\.lake\packages\importGraph\.lake\build\lib\lean;
C:\Users\ginger\my_math_project\.lake\packages\LeanSearchClient\.lake\build\lib\lean"
lean OEIS.lean
```

## What is proved

Four OEIS conjectures, each stated for **all** n (not finitely many terms).
All are sorry-free; `#print axioms` shows only Lean's standard axioms.

| # | File | Statement | Axioms |
|---|---|---|---|
| 1 | OEIS.lean | `A267442 n = A043545 n`, n ≥ 1 | propext, choice, Quot.sound |
| 2 | OEIS2.lean | `A217586 n = A096268(n-1) XOR A036987(n-1)` | propext, Quot.sound |
| 3 | OEIS3.lean | `A285383 n = A035263(n-1)`, n ≥ 2 | propext, choice, Quot.sound |
| 4 | OEIS3.lean | `A284948 n = A096268(n-2)`, n ≥ 2 | propext, choice, Quot.sound |
| 5 | OEIS4.lean | `A306559(n+5) = A039982 n` | propext, choice, Quot.sound |
| 6 | OEIS5.lean | `A270803 n = A151666((n+1)/2)`, n ≥ 1 | propext, choice, Quot.sound |
| — | Conn.lean | `A043545` automaton = (max digit) − (min digit) | propext, choice, Quot.sound |
| — | PdConn.lean | `A096268` automaton = period-doubling recurrence | propext, choice, Quot.sound |
| — | FrConn.lean | `A036987` automaton = indicator of 2^k − 1 | propext, choice, Quot.sound |
| — | Conn3.lean | `A035263` automaton = morphic word (0→11, 1→10) | propext, choice, Quot.sound |
| — | Conn4.lean | `A039982` automaton = morphic limit S(0)=1, S(n+1)=1·φ(S(n)) | propext, choice, Quot.sound |
| — | **Universal.lean** | **`universal_middle_zero`: middle column = 2^k−1 in ALL convex symmetric geometries** | propext, choice, Quot.sound |
| — | Universal.lean | `universal` (closed form), `universal_middle`, `ustate_dep`, `ustate_one`, `step_preserved` | propext, choice, Quot.sound |
| — | Universal.lean | `radial_middle` — 1D radial instance (X = Nat) | propext, choice, Quot.sound |
| — | Universal.lean | `moore_middle` — 2D 3×3 box instance (X = Nat × Nat) | propext, choice, Quot.sound |
| — | **Universal.lean** | **`tree_middle` — infinite binary tree instance (X = List Bool)** | propext, choice, Quot.sound |
| — | **Universal.lean** | **`centres_agree` — the three centres carry the same value at every t** | propext, choice, Quot.sound |
| — | **R129.lean** | **Rule 129 middle column = indicator of 2^k−1 (A267442)** | propext, choice, Quot.sound |
| — | R129.lean | Rule 129 full closed form (submask of r t) | propext, choice, Quot.sound |

Number 3 uses a verified **shift automaton** (`shift_correct`): a DFA that
reads the binary digits of n and feeds the digits of n+1 into another DFA,
including carries. Number 4 follows from 3 plus the complementary-output
relations A284948 = 1 - A285383 and A035263 = 1 - A096268.

Number 5 iterates the shift automaton four times (composing the +1 shift),
producing a 13-state product with A039982.

Number 6 uses a *halving* automaton (`halveδ`): the first digit becomes the
carry, the remaining digits are shifted, which realises floor((n+1)/2).
## How the proof works

`fold δ s n` runs the binary digits of `n` (LSB first) through a DFA with
transition `δ` from state `s`. Every `n ≥ 1` ends with the digit 1, so its
final state is `δ p true` for some reachable `p`. It therefore suffices to
check that all pairs reachable with a final digit 1 agree on outputs — a
finite check that `decide` performs.

* `fold_last` : the last-digit-1 structure
* `seq_eq_of_inv` : the comparison theorem
* `Rlist`, `R1list` : the finite reachable sets (5 and 2 pairs)

## Rule 129 (A267442), solved

`R129.lean` (777 lines, no sorry) proves: `x(t,0) = 0 ↔ ∃ k ≥ 1, t = 2^k - 1`, where `x` is
the Rule 129 CA from a single cell — this is exactly the OEIS definition of A267442.
It also proves the full closed form `x(t,j) = 0 ↔ |j| ≤ t ∧ sub ⌊(t−|j|)/2⌋ (r t)`
(r t = t with leading bit deleted).

## The OEIS definition, connected

`Conn.lean` proves `A043545_digits`: for all n ≥ 1, the automaton output
equals `maxDig n - minDig n`, the literal OEIS definition. So theorem 1 can be
read unconditionally as `A267442 n = maxDig n - minDig n`.

## Provenance and scope

The transition tables were inferred from OEIS b-files and then validated by
predicting every term (thousands per sequence) with zero errors. Lean then
proves that **these automata** compute equal sequences for all n.

Strictly, this is conditional on the automata being the OEIS sequences. The
next step is to prove that the automata satisfy the defining recurrences of
A267442 (Rule 129) and A043545 (digit extremes).

## Next targets

The other three conjectures need the "shift automaton" (DFA for n ↦ b(n-k),
including binary carries):

* `A284948 n = A096268 (n-2)`
* `A285383 n = A035263 (n-1)`
* `A217586 n = A096268 (n-1) XOR A036987 (n-1)`
## Shells (round 1 of the shell-scaling goal)

`Shells.lean` imports `Universal.olean` and formalizes the combinatorial core
of the shell law (all sorry-free, axioms propext/choice/Quot.sound):

| Lemma | Statement |
|---|---|
| `shell_iff` | `(e/2) &&& r = e/2 ↔ ∃ m, m &&& r = m ∧ (e = 2m ∨ e = 2m+1)` |
| `subm_two_mul` | submasks of 2u = doubles of submasks of u |
| `subm_two_mul_add_one` | submasks of 2u+1 = doubles and doubles+1 of submasks of u |
| `card_subm_two_mul` | `#subm (2u) = #subm u` |
| `card_subm_two_mul_add_one` | `#subm (2u+1) = 2 * #subm u` (the popcount recursion) |
| `r_eq_t_sub_pow` | `r t = t - 2 ^ log2 t` for t ≥ 1 |
| `two_mul_r_le` | `2 * r t ≤ t` |
| `two_mul_r_add_one_le` | `2 * r t + 1 ≤ t` |
| `mem_shell` | `d ∈ shell t ↔ d ≤ t ∧ (t-d)/2 ⊆ r t` |
| **`card_shell`** | **`#(shell t) = 2 * #(subm (r t))`** |
| `sum_subm_two_mul` | `(subm (2u)).sum id = 2 * (subm u).sum id` |
| `sum_subm_two_mul_add_one` | `(subm (2u+1)).sum id = 4 * (subm u).sum id + (subm u).card` |
| **`two_mul_sum_subm`** | **`2 * (subm r).sum id = (subm r).card * r`** |
| `sum_shell_eq_prod` | shell sum = product sum over submasks |
| `shell_pair`, `sum_range_two` | `(t-2a)+(t-2a-1) = 2t-1-4a` 及其内和 |
| **`sigma_shell`** | **`(shell t).sum id = #subm (r t) * (2t - 1 - 2 r t)`** |
| **`universal_zero_iff`** | **`ustate lev nbhd t x = 0 ↔ lev x ∈ shell t`（任意 (H1)-(H4) 几何）** |
| `row_zero_iff_shell` | `row t j = 0 ↔ j.natAbs ∈ shell t` |
| `row_middle_shell` | `row t 0 = 0 ↔ 0 ∈ shell t` |
| **`shell_eq_image`** | **`shell t = (subm (r t)).image (t-2·) ∪ (subm (r t)).image (t-2·-1)`** |
| `zero_mem_shell` | `0 ∈ shell t ↔ ∃ k ≥ 1, t = 2^k - 1` |

Building: `lean -o Universal.olean Universal.lean` then (with the workspace
`lean` directory on `LEAN_PATH`) `lean Shells.lean` takes seconds instead of the
three minutes a full `Universal.lean` rebuild costs.
## Instances.lean (b-ary tree)

| Lemma | Statement |
|---|---|
| `bnb_cases` | members of the neighbourhood: self, parent, or a child |
| `bnb_bound` | levels differ by at most 1 |
| `bnb_prev` / `bnb_next` | neighbours at level d-1 and d+1 exist |
| **`btree_middle`** | **for every b ≥ 1: `ustate blev (bnb) t [] = 0 ↔ ∃ k ≥ 1, t = 2^k - 1`** |

Numeric check: `scripts/274_btree_b.py`, b = 2,3,4, 0 mismatches.
## Instances.lean (d-dimensional Moore)

| Lemma | Statement |
|---|---|
| `dlev`, `dnb` | Chebyshev level = `Finset.univ.sup`; 3^D box as an image of offset vectors |
| `dnb_mem` / `dnb_bound` | reflexivity; levels differ by at most 1 |
| `dnb_prev` / `dnb_next` | neighbours at level d-1 and d+1 exist (needs `0 < D`) |
| **`mooreD_middle`** | **for every D ≥ 1: the origin's middle column is `2^k - 1`** |

## Final.lean (round 14: the counting layer)

`Final.lean` imports `Shells` and `Instances` (so build those oleans first).
16 theorems, no sorry, axioms `propext, Classical.choice, Quot.sound`.

| Lemma | Statement |
|---|---|
| **`zero_set_eq_biUnion`** | the zero set is the union of the level sets over `shell t` |
| **`zero_card_eq_sum_levels`** | **#zeros = Σ_{d ∈ shell t} #{x | lev x = d}** in any (H1)-(H4) geometry |
| `mem_win` | `j ∈ win t ↔ ∃ d ≤ t, j = d ∨ j = -d` (the full window) |
| `row_zero_win_eq` | the window zeros = `posImg (shell t) ∪ negImg (shell t)` |
| `posImg_inter_negImg` | the two copies meet only in `{0}` |
| **`row_zero_win_card`** | **#Z(t) = 2 #shell t − [0 ∈ shell t]** over `-t ≤ j ≤ t` |
| `level_eq`, `arm_inter` | the Moore level is `armA ∪ armB`, meeting at `(d,d)` |
| **`level_card`** | **a Moore level holds `2d+1` cells** |
| **`moore_zero_card_sum`** | Moore zeros = `Σ_{d ∈ shell t} (2d+1)` |
| **`moore_zero_card_closed`** | **Moore zeros = `4 * #subm (r t) * (t - r t)`** |
| `t_sub_r_eq_pow` | `t - r t = 2 ^ log2 t` |
| **`exists_pow_card_subm`** | **`#subm r` is a power of two** |
| **`exists_pow_card_shell`** | **`#shell t` is a power of two** |
| **`moore_zero_card_pow`** | **the Moore zero count is a power of two** |
| **`row_zero_win_card_pow`** | **the 1-D zero count is `2^k` or `2^k - 1`** |

Closed forms (the `2^wt` step is numerical, `#subm = 2^popcount`, t ≤ 1200):

* one-dimensional window: `2^(1+wt t) - [t = 2^i - 1]`  (= A267447, 71/71 terms)
* quarter-plane Moore: `2^(1+wt t + ⌊log₂ t⌋)`  (= A189007 shifted, 68/68 terms)

Numeric checks: `scripts/275_moore_quarter_counts.py` (t ≤ 29, 90×90 box),
`scripts/276_zero_counts_oeis.py` (t ≤ 1200, plus the OEIS term lists).

## Census.lean (round 15: the geometry census)

`Census.lean` imports `Shells`. 6 theorems, no sorry, standard axioms.

| Lemma | Statement |
|---|---|
| `shell_mem_self` | `t ∈ shell t` |
| **`shell_sum_submask`** | **the shell sum of ANY `c` is a sum over the submasks of `r t`** |
| `shell_sum_mul` | `Σ_{d∈S} k*d = k * Σ_{d∈S} d` |
| **`shell_sum_linear`** | **level sizes `1, k, 2k, 3k, ...` give `k*sigma + eps`** |
| **`shell_sum_linear_form`** | **`k * #subm(r t) * (2t-1-2 r t) + eps`** |
| **`shells_determine_levels`** | **given level 0, the zero counts determine every `c_t`** |

Consequences (see `docs/47`): the zero counts are a linear functional of the
level-size sequence, hence

* `Z^2` von Neumann (c_d = 4d): `A169699` (and its printed formula needs the
  correction "`+1` iff `n = 2^i-1`", not "iff n is a power of 2");
* `Z^2` Moore (c_d = 8d) and the triangular lattice (c_d = 6d): same formula
  with k = 8, 6 — neither sequence is in OEIS;
* the counts cannot see the direction `c + lambda*(-1)^d` (every shell contains
  equally many even and odd levels); fixing `c 0` removes it.

## Tree.lean (round 16: the b-ary tree, product form)

`Tree.lean` imports `Census`. 20 declarations (19 theorems + `bits`), no sorry.

| Lemma | Statement |
|---|---|
| `subm_zero`, `subm_one` | `subm 0 = {0}`, `subm 1 = {0,1}` |
| **`sum_subm_pow_two_mul`** | **`Σ_{m⊆2u} y^m = Σ_{m⊆u} (y*y)^m`** |
| **`sum_subm_pow_two_mul_add_one`** | **`Σ_{m⊆2u+1} y^m = (1+y) * Σ_{m⊆u} (y*y)^m`** |
| `sum_subm_pow_shift_two_mul(_add_one)` | the descending sum obeys the same recursion |
| **`sum_subm_pow_shift`** | **`Σ_{m⊆r} y^(r-m) = Σ_{m⊆r} y^m`** |
| **`shell_sum_pow`** | **`Σ_{d∈S} b^d = (b+1) * b^(t-1-2r) * Σ_{m⊆r} (b*b)^m`** |
| `lt_two_pow_self`, `testBit_lt` | `j < 2^j`; a set bit implies `j < n` |
| `bits`, `mem_bits`, `bits_two_mul(_add_one)` | the set of 1-bit positions and its recursion |
| `prod_bits_two_mul(_add_one)` | the product over bits obeys the same recursion |
| **`sum_subm_pow_eq_prod`** | **`Σ_{m⊆r} y^m = ∏_{i ∈ bits r} (1 + y^(2^i))`** |
| **`shell_sum_pow_factored`** | **the tree count factorized over the bits of `r t`** |
| **`shell_sum_pow_factored'`** | the same with factors `1 + b^(2^(i+1))` |

Numeric checks: `scripts/279_tree_product.py` (b ≤ 7, t ≤ 200) and
`scripts/280_tree_factored.py` (b ≤ 8, t ≤ 300), both 0 mismatches.

## Parity.lean (round 16: the alternating kernel)

`Parity.lean` imports `Shells`. 4 theorems, no sorry.

| Lemma | Statement |
|---|---|
| `sub_two_mul_mod` | `(t - 2m) % 2 = t % 2` |
| `sub_two_mul_one_mod` | `(t - 2m - 1) % 2 = 1 - t % 2` |
| **`shell_filter_parity_card`** | **the shell levels with the parity of `t` are exactly the first arm** |
| **`shell_even_odd_count`** | **every shell has as many even levels as odd ones** |

Also added to `Tree.lean`:

| Lemma | Statement |
|---|---|
| **`card_subm_eq_pow_bits`** | **`#(subm r) = 2 ^ #(bits r)`** (the popcount form) |
| `card_shell_eq_pow_bits` | `#(shell t) = 2 * 2 ^ #(bits (r t))` |

## Moments.lean (round 17: the second moment of the submask set)

`Moments.lean` imports `Tree`. 3 theorems, no sorry.

| Lemma | Statement |
|---|---|
| `Q` | `Q r = sum_{i in bits r} 4^i` |
| `Q_two_mul` | `Q (2u) = 4 * Q u` |
| `Q_two_mul_add_one` | `Q (2u+1) = 1 + 4 * Q u` (note: `1 + 4*Q u`, not `Q u + 1`) |
| **`four_mul_card_sq`** | **`4 * Σ_{m⊆r} m² = #(subm r) * (r² + Q r)`** |

This is the second submask moment. Verified numerically in
`scripts/281_shell_square_sum.py` (r ≤ 300).

## ShellSq.lean (round 18: moment relations of the shell)

`ShellSq.lean` imports `Moments`. 3 theorems, no sorry.  With
`B = Σ_m (t-2m)`, `A = Σ_m (t-2m)^2`, `S1 = Σ_m m`, `S2 = Σ_m m^2`,
`N = #(subm (r t))` and `Zsq = Σ_{d∈S} d^2`:

| Lemma | Statement |
|---|---|
| `subm_sum_shift` | `B + 2*S1 = N * t` |
| `subm_sum_shift_sq` | `A + 4*(t*S1) = N*(t*t) + 4*S2` |
| **`shell_sum_sq_split`** | **`Zsq + 2*B = 2*A + N`** (the shell splits into pairs {u, u-1}) |

With `two_mul_sum_subm` and `four_mul_card_sq` these pin down the second
moment; the closed form is now `shell_sum_sq` (see below).

## Dim3.lean (round 19: quadratic level sizes) and shell_sum_sq

`ShellSq.lean` now also contains `shell_sum_sq`:

| Lemma | Statement |
|---|---|
| **`shell_sum_sq`** | **`Σ_{d∈S(t)} d² = #(subm (r t)) * (2 K (K-1) + 2 Q(r t) + 1)`**, `K = t - r t` |

Proof strategy: `set` every big sum to an opaque variable, `exact_mod_cast` the
relations to ℤ, close by `nlinarith`, then `push_cast` + `Nat.cast_injective` back.

`Dim3.lean` imports `ShellSq`. 3 theorems, no sorry.

| Lemma | Statement |
|---|---|
| **`shell_sum_quadratic`** | level sizes `1, 4k d² + 2` give `4k * M2 + 2 #shell - eps` |
| **`zero_count_Z3_vonNeumann`** | `c_d = 4d² + 2` (ℤ³ von Neumann) in closed form |
| **`zero_count_Z3_moore`** | `c_d = 24d² + 2` (ℤ³ Moore) in closed form |

## Cubic.lean (round 20 + round 22: the third moment, now closed)

`Cubic.lean` imports `ShellSq`. 5 theorems, no sorry.

| Lemma | Statement |
|---|---|
| **`eight_mul_card_cube`** | **`8 * Σ_{m⊆r} m³ = #(subm r) * (r³ + 3 Q r * r)`** |
| `subm_sum_shift_cube` | `Σ (t-2m)³ + 6 t² Σm + 8 Σm³ = N t³ + 12 t Σm²` |
| **`shell_sum_cube_split`** | **`Σ_S d³ + 3 Σ(t-2m)² + N = 2 Σ(t-2m)³ + 3 Σ(t-2m)`** |
| **`cube_key`** | **pure algebra: the seven relations force `ZC = N(2k³+3k²+3k+1+3Q(2k+1))`** |
| **`shell_sum_cube`** | **`Σ_{d∈S(t)} d³ = #(subm (r t)) * (2k³+3k²+3k+1+3Q(2k+1))`**, `k = t-r t-1` |

**How the assembly was finally done** (it is the same shell-splitting argument as
`shell_sum_sq`, but `nlinarith` is hopeless in degree 3 — it monomializes every
pair of hypotheses).  The fix is to make the algebra *pure*:

1. `set` the seven sums `N S1 S2 S3 B A A3 ZC` to opaque variables (`Nat`);
2. `exact_mod_cast` the seven relations to `Int`;
3. isolate the algebra in `cube_key`, a statement about twelve `Int` variables
   with **no** `Finset`, **no** `Nat` subtraction and **no** big terms;
4. prove `cube_key` by three small `linear_combination` steps (explicit
   coefficients, so no search): `B = N(T-R)`, `A = N((T-R)²+Q)`,
   `A3 = N((T-R)³+3Q(T-R))`, then `ZC = 2A3+3B-3A-N`;
5. bridge back with `set K := t - r t - 1`, `set C := N * (…)`, `push_cast`,
   `Nat.cast_injective`.

The lesson: **move the arithmetic off the sums before automating it.**  Explicit
`linear_combination` coefficients are dramatically more robust than `nlinarith`
as soon as the degree reaches 3.

## Dim4.lean (round 22: cubic level sizes, Z⁴)

`Dim4.lean` imports `Cubic`. 5 theorems, no sorry.  In ℤ⁴ the Moore level holds
`(2d+1)⁴ - (2d-1)⁴ = 64d³ + 16d` and the von Neumann level holds `8d(d²+2)/3`;
both vanish at `d = 0`, where the centre alone sits, so the count gains `eps`.

| Lemma | Statement |
|---|---|
| **`shell_sum_cubic`** | level sizes `1, a d³ + b d` give `a M3 + b sigma + eps` |
| `three_dvd` | `3 ∣ d (d² + 2)` (case split on `d % 3`) |
| `three_mul_level` | `3 * (8 * (d(d²+2)/3)) = 8 d³ + 16 d` |
| **`zero_count_Z4_moore`** | **`c_d = 64d³+16d`:  `Z = 64 M3 + 16 sigma + eps`** |
| **`zero_count_Z4_vonNeumann`** | **`c_d = 8d(d²+2)/3`:  `3 Z = 8 M3 + 16 sigma + 3 eps`** |

Numerically verified in `scripts/285_four_dim.py`: the level sizes by brute-force
enumeration of the ℓ∞ and ℓ¹ spheres in ℤ⁴ for `d ≤ 10`, the two count laws for
`t ≤ 200`, the third shell moment for `t ≤ 2000`, and `three_mul_level` for
`d ≤ 500`.  `scripts/283_third_moments.py` independently checks the third moment
and the associated submask moments for `r, t ≤ 300`.

The counting table (`scripts/282_counting_table.py`) now has **15 geometries**
(ℤ², ℤ³, ℤ⁴, ℤ⁵, the orthants, the triangular lattice, the trees), all matching
for `t ≤ 60` with zero failures.  The ℤ⁵ rows are the first ones whose closed
form really needs `P16` — see `docs/50-invariant-tower.md`.

**Status of the `Σ_{d∈S} d^j` programme: closed for j = 0, 1, 2, 3.**
`j = 0` is `card_shell`, `j = 1` is `sigma_shell`, `j = 2` is `shell_sum_sq`,
`j = 3` is `shell_sum_cube`.

**And j = 3 is where the easy part ends.**  The submask moments are

```
Σ_{m⊆r} m^j = N * P_j(r, Q) / 2^j ,   Q = Σ_{i∈bits r} 4^i
P_1 = r,  P_2 = r^2 + Q,  P_3 = r^3 + 3 Q r
P_4 = r^4 + 6 Q r^2 + 3 Q^2 - 2 P16 ,  P16 = Σ_{i∈bits r} 16^i
```

so `j ≤ 3` needs only `(r, Q)` while `j = 4` needs a **new invariant** `P16`.
The reason is cumulants: the odd cumulants of the symmetric Bernoulli vanish
(`c3 = c5 = 0`), so `j = 3` never sees one; the fourth cumulant `c4 = -P16/8`
is the first survivor.  `P16` is not a polynomial in `Q` (for every degree
`d ≤ 30` the interpolant through the first `d+1` points already misses at the
next one).  Numerics: `scripts/286` (j ≤ 6, r ≤ 300), `scripts/287`,
`scripts/288` (the fourth shell moment, t ≤ 500; the `P16` coefficient is
exactly `-4N`), `scripts/289` (ℤ⁵ Moore — the first lattice that needs `P16`,
t ≤ 60, and its zero counts are not in OEIS).  See `docs/50`.







## Arm.lean (round 23: the two-step recursion = 2-regularity)

`Arm.lean` imports `Census`. 6 theorems, no sorry.  The shell is the union of
the pairs {u, u-1}; the **arm** keeps the larger halves,

```
arm t = { t - 2m : m ⊆ r t } ,        shell t = arm t ∪ (arm t - 1)
```

| Lemma | Statement |
|---|---|
| **`r_two_mul`** | **`r (2u) = 2 * r u`** |
| **`r_two_mul_add_one`** | **`r (2u+1) = 2 * r u + 1`** |
| **`shell_eq_arm`** | **`shell t = arm t ∪ (arm t).image (· - 1)`** |
| `shell_sum_pair` | `Σ_{d∈S(t)} c d = Σ_{m⊆r t} [c(t-2m) + c(t-2m-1)]` |
| **`zero_count_two_mul`** | **`Z(2u) = Σ_{m⊆r u} [c(2(u-2m)) + c(2(u-2m)-1)]`** |
| **`zero_count_two_mul_add_one`** | **`Z(2u+1) = Σ_{m⊆r u} [(c(2(u-2m)+1)+c(2(u-2m))) + (c(2(u-2m)-1)+c(2(u-2m)-2))]`** |

These two recursions are **geometry independent** — the geometry enters only
through `c` — and they are exactly what "the counting table is 2-regular"
means.  Iterating them gives a finite linear representation of every row.

The arm also satisfies the set-level recursions

```
arm (2u)   = 2 * arm u ,      arm (2u+1) = (2 arm u + 1) ∪ (2 arm u - 1) ,
```

verified numerically (`scripts/291_arm_recursion.py`, u < 300) together with the
arm-moment transfer matrices

```
Φ_k(2u)   = 2^k Φ_k(u) ,      Φ_k(2u+1) = 2 Σ_{i ≡ k (2)} C(k,i) 2^i Φ_i(u) .
```

### What the rank of the 2-kernel says (`scripts/292`, `293`, `294`)

Compute the rank over ℚ of the span of the 2-kernel (exact Gaussian
elimination for the lattice rows, arithmetic mod `2^61-1` for the trees):

| sequence | rank |
|---|---|
| `c = d^j` (no centre patch) | `j + 1` (flat for j ≤ 5, K ≤ 7) |
| `c(0)=1, c(d)=d^j` (d ≥ 1) | `j + 2` |
| ℤ^D lattice rows | **`D + 1`** (D = 1..5) |
| 1-D ray, ℤ² orthant Moore | 1 (the formula factors completely) |
| **b-ary trees** | **grows 3, 4, 5, …, 10 for K = 2..9 — NOT 2-regular** |

So the complexity of each geometry is exactly its dimension (plus the rank-one
indicator `ε = [t = 2^i - 1]`), and the exponential regime is the only one that
escapes: halving a tree squares the base of the exponential, so the state never
closes.  See `docs/51-two-regularity.md`.
### The arm moments and their transfer matrices (round 24)

The formal language of that complexity is the **arm moment**

```lean
def Phi (k t : Nat) : Nat := (subm (r t)).sum (fun m => (t - 2 * m) ^ k)
```

and its two digit recursions, all proved in `Arm.lean`:

| Lemma | Statement |
|---|---|
| `Phi_eq_arm` | `Φ_k(t) = Σ_{x∈arm t} x^k` |
| `Phi_zero` | `Φ_0(t) = #subm (r t)` |
| `sub_inj`, `sum_arm`, `shell_sum_arm` | the arm sums; `Σ_{d∈S(t)} c d = Σ_{x∈arm t} [c x + c (x-1)]` |
| **`Phi_two_mul`** | **`Φ_k(2u) = 2^k Φ_k(u)`** — the even step is `diag(2^k)` |
| `pow_pair` | `(2z+1)^k + (2z-1)^k = 2 Σ_{i ≡ k (2)} C(k,i) (2z)^i` |
| `Phi_two_mul_add_one_nat` | the same identity in `Nat` |
| **`Phi_two_mul_add_one`** | **`Φ_k(2u+1) = Σ_{i≤k, i≡k(2)} C(k,i) 2^{i+1} Φ_i(u)`** |

The odd transfer matrix `M[k][i] = 2^{i+1} C(k,i) [i ≡ k mod 2]` reads

```
k=0: [2, 0,  0,  0,  0,   0,   0]
k=1: [0, 4,  0,  0,  0,   0,   0]
k=2: [2, 0,  8,  0,  0,   0,   0]
k=3: [0, 12, 0, 16,  0,   0,   0]
k=4: [2, 0, 48,  0, 32,   0,   0]
k=5: [0, 20, 0, 160, 0,  64,   0]
k=6: [2, 0, 120, 0, 480,  0, 128]
```

— nonzero only in the same-parity positions.  **These two recursions are the
linear representation**: read the binary digits of `t` after the leading 1,
start from `(Φ_0(1),…,Φ_j(1)) = (1,0,…,0)`, and multiply by `diag(2^k)` for a
0 and by `M` for a 1.  `scripts/298_phi_transfer.py` checks both laws numerically
(k ≤ 8, u ≤ 400) and checks that the digit iteration reproduces `Φ_k(t)`
(t < 300, k ≤ 4).

**Next in this line** (the open half of the goal): turn "Z_c lies in the span of
`Φ_0..Φ_j` whenever `c x + c (x-1)` is a polynomial of degree `j`" into a theorem
(via `shell_sum_arm` + `Phi_eq_arm`, no binomial expansion needed), add the
rank-one correction `[1 ∈ arm t]`, and with it bound the 2-kernel rank by `j+2`
for every row of the table.

### The decomposition theorem (round 24)

If the *shifted* level size is a polynomial, the count is a combination of arm
moments — and no binomial expansion is needed:

```lean
theorem shell_sum_of_poly (c : Nat → Nat) (γ : Nat → Int) (j t : Nat) (ht : 1 ≤ t)
    (hγ : ∀ x, 1 ≤ x → (c x : Int) + (c (x-1) : Int)
        = Σ_{i ∈ range (j+1)} γ i * (x : Int)^i) :
    (((shell t).sum c : Nat) : Int) = Σ_{i ∈ range (j+1)} γ i * (Phi i t : Int)

theorem zero_mem_shell_iff (ht : 1 ≤ t) : 0 ∈ shell t ↔ 1 ∈ arm t
```

The second one identifies the extra dimension of the representation with the
rank-one automatic sequence `ε = [0 ∈ shell t]`: it is literally "[1 is in the
arm]".

Row functionals `γ` computed and verified for all 13 polynomial rows
(`scripts/299_row_functionals.py`, t ≤ 200, 0 failures):

| geometry | γ | δ | dimension |
|---|---|---|---|
| 1-D line | [4] | -1 | 2 |
| 1-D ray | [2] | 0 | 1 |
| ℤ² vN | [-4, 8] | 1 | 3 |
| ℤ² Moore | [-8, 16] | 1 | 3 |
| triangular | [-6, 12] | 1 | 3 |
| ℤ² orthant vN | [1, 2] | 0 | 2 |
| ℤ² orthant Moore | [0, 4] | 0 | **1** (γ₀ = 0) |
| ℤ³ vN | [8, -8, 8] | -1 | 4 |
| ℤ³ Moore | [28, -48, 48] | -1 | 4 |
| ℤ⁴ Moore | [-80, 224, -192, 128] | 1 | 5 |
| ℤ⁴ vN (3×) | [-24, 56, -24, 16] | 3 | 5 |
| ℤ⁵ Moore | [244, -800, 1120, -640, 320] | -1 | 6 |
| ℤ⁵ vN (3×) | [36, -56, 64, -16, 8] | -3 | 6 |

The dimension bound `#(γ ≠ 0) + [δ ≠ 0]` equals the measured 2-kernel rank on
every row — including the collapse of the quarter-plane Moore row, where the
constant term of `γ` vanishes.

**Still open in this line**: the digit induction (`Z_c(2^k n + r) = Σ c_i Φ_i(n) + c ε(n)`
with explicit coefficients) and hence a formal rank bound; the tree
non-2-regularity; and j = 4 / ℤ⁵ inside this frame.

## Rep.lean (round 25: the representation, row by row)

`Rep.lean` imports `Arm`. 16 theorems, no sorry.  It closes the loop between the
two halves of the picture:

```lean
theorem zero_not_mem_shell_two_mul (hu : 1 ≤ u) : 0 ∉ shell (2 * u)
theorem zero_mem_shell_two_mul_add_one (hu : 1 ≤ u) : 0 ∈ shell (2*u+1) ↔ 0 ∈ shell u
```

— the centre indicator is a rank-one automatic sequence with the simplest
possible recursion — and then the *refined* decomposition, where the polynomial
identity is only needed away from the centre:

```lean
theorem shell_sum_of_poly_correction (c) (γ) (j) (δ) (t) (ht : 1 ≤ t)
    (hγ : ∀ x, 2 ≤ x → c x + c (x-1) = Σ_i γ_i x^i)
    (h1 : c 1 + c 0 = Σ_i γ_i + δ) :
    ↑((shell t).sum c) = Σ_i γ_i ↑(Phi i t) + δ * (if 1 ∈ arm t then 1 else 0)
```

Every polynomial row of the counting table is then an instance:

| theorem | level sizes | γ | δ |
|---|---|---|---|
| `phi_line` | 1, 2, 2, … | [4] | −1 |
| `phi_ray` | 1, 1, 1, … | [2] | 0 |
| `phi_z2vn` | 1, 4, 8, 12, … | [−4, 8] | 1 |
| `phi_z2moore` | 1, 8, 16, 24, … | [−8, 16] | 1 |
| `phi_tri` | 1, 6, 12, 18, … | [−6, 12] | 1 |
| `phi_z2orthvn` | 1, 2, 3, 4, … | [1, 2] | 0 |
| `phi_z2orthmo` | 1, 3, 5, 7, … | [0, 4] | 0 |
| `phi_z3vn` | 1, 6, 18, 38, … | [8, −8, 8] | −1 |
| `phi_z3moore` | 1, 26, 98, 218, … | [28, −48, 48] | −1 |
| `phi_z4moore` | 1, 80, 544, … | [−80, 224, −192, 128] | 1 |
| `phi_z4vn` (3×) | 3, 24, 96, … | [−24, 56, −24, 16] | 3 |
| `phi_z5moore` | 1, 242, 2882, … | [244, −800, 1120, −640, 320] | −1 |
| `phi_z5vn` (3×) | 3, 30, 150, … | [36, −56, 64, −16, 8] | −3 |

Together with the transfer matrices of `Arm.lean` this is the whole finite-state
machine: dimension `#(γ ≠ 0) + [δ ≠ 0]`, one matrix per binary digit.
The two tree rows are *not* instances — their level size is exponential, and they
are exactly the rows that are not 2-regular.

## Digits.lean (round 26: the finite-state theorem)

`Digits.lean` imports `Rep`. 11 theorems, no sorry.  This is the piece the whole
thread was pointing at — the count is a fixed functional of a finite state
vector, and the state evolves by one matrix per binary digit.

```lean
def X (t : Nat) : Nat → Int := fun k => (Phi k t : Int)      -- the state vector
def T0 (v : Nat → Int) : Nat → Int := fun k => 2^k * v k      -- even transfer
def T1 (v : Nat → Int) : Nat → Int := fun k =>
  Σ_{i ≤ k, i ≡ k (2)} C(k,i) 2^(i+1) v i                     -- odd transfer
```

| Lemma | Statement |
|---|---|
| `X_one` | `X 1 = (1,1,1,…)` (arm 1 = \{1\}) |
| `X_two_mul` | `X (2u) = T0 (X u)` |
| `X_two_mul_add_one` | `X (2u+1) = T1 (X u)` |
| `X_digit` | `X t` is `T0` or `T1` of `X (t/2)`, by the parity of t |
| **`X_iterate`** | **`X (2^k n + r) = W k r (X n)`**, `r < 2^k`, where `W` composes the k transfers selected by the bits of r |
| `T0_congr`, `T1_congr`, `W_congr_le` | triangularity: index `i` only sees entries `≤ i` |
| `zero_mem_digits` | `0 ∈ shell (2^k n + r) ↔ (r + 1 = 2^k ∧ 0 ∈ shell n)` |
| `Z_state` | the count at `2^k n + r` = γ applied to the transferred state + centre bit |
| **`Z_state_determined`** | **if two times n, n' agree on `Φ_0..Φ_j` and on `0 ∈ shell`, then the counts at `2^k n + r` and `2^k n' + r` agree** |

The last one is the dimension bound `j+2` in *determination* form: the sequence
`n ↦ Z_c(2^k n + r)` is a function of `(Φ_0(n), …, Φ_j(n), ε(n))` alone.  With
`X_iterate` and the 13 row functionals of `Rep.lean` this is the complete
finite-state machine:

```
Z_c(t) = γ · X(t) + δ·ε(t) ,      X(t) = T_{d_0} T_{d_1} ⋯ T_{d_{k-1}} X(n) .
```

The two tree rows have no such description: their level size is exponential and
their 2-kernel rank grows without bound (`scripts/294`) — they are precisely the
rows outside the polynomial frame.

## Matrix.lean (round 27: the explicit matrices)

`Matrix.lean` imports `Digits`. 4 theorems, no sorry.  The two transfers now have
their matrices written down:

```lean
def M0 (i l : Nat) : Int := if l = i then 2^i else 0
def M1 (i l : Nat) : Int :=
  if l ≤ i ∧ l % 2 = i % 2 then (i.choose l : Int) * 2^(l+1) else 0

theorem T0_apply (hi : i ≤ j) : T0 v i = Σ_{l ≤ j} M0 i l * v l
theorem T1_apply (hi : i ≤ j) : T1 v i = Σ_{l ≤ j} M1 i l * v l
```

and the k-fold matrix (composing one factor per binary digit) is

```lean
def A (j : Nat) : Nat → Nat → Nat → Nat → Int
  | 0, _, i, l => if l = i then 1 else 0
  | k + 1, r, i, l =>
      Σ_{m ≤ j} (if r % 2 = 0 then M0 i m else M1 i m) * A j k (r / 2) m l

theorem W_eq_A (hi : i ≤ j) : W k r v i = Σ_{l ≤ j} A j k r i l * v l
```

**The explicit linear representation** — the goal of this whole thread:

```lean
theorem Z_row_linear (k r) (hr : r < 2^k) (n) (hn : 1 ≤ n) :
    ↑(Z_c (2^k n + r))
      = Σ_{l ≤ j} (Σ_{i ≤ j} γ i * A j k r i l) * ↑(Phi l n)
        + δ * (if 1 ∈ arm (2^k n + r) then 1 else 0)
```

The coefficient of `Φ_l(n)` is `c_l = Σ_i γ_i A j k r i l` — an explicit,
computable integer.  `scripts/301` checks the identity end to end for 10 rows
(k ≤ 5, n ≤ 40, all residues).

**A new phenomenon at degree two** (`scripts/302`, `303`): for rows of degree ≤ 1
the coefficient vector closes up completely —

```
c_0 = γ_0 * 2^wt(r) ,        c_1 = γ_1 * 2^(k + wt(r)) ,
```

i.e. it only sees `r` through its popcount (`wt(r)` = number of binary ones).
From degree 2 on this fails: at `k = 5` and popcount 2, the constant coefficient
of ℤ³ von Neumann is `192, 2592, 576, 672` for `r = 3, 12, 5, 6` — the actual
digit pattern matters, not just its weight.  So "degree 2" is the threshold here
too (just as it was for the invariant tower and for the rank law).

### Closed forms for the degree 0 and 1 rows (round 28)

Two more theorems turn the general representation into a *formula*:

```lean
theorem W_zero (hr : r < 2^k) : W k r v 0 = #subm r * v 0
theorem W_one  (hr : r < 2^k) : W k r v 1 = 2^k * (#subm r * v 1)
```

(the constant component only sees the popcount of the residue, the first
component additionally picks up `2^k`), hence

```lean
theorem phi_line_explicit (hr : r < 2^k) (hn : 1 ≤ n) :
    Z_line (2^k n + r) = 4 * (#subm r * Phi_0(n)) - [1 ∈ arm (2^k n + r)]

theorem phi_z2vn_explicit (hr : r < 2^k) (hn : 1 ≤ n) :
    Z_vN (2^k n + r) = -4 * (#subm r * Phi_0(n))
                     + (8 * 2^k * #subm r) * Phi_1(n) + [1 ∈ arm (2^k n + r)]
```

These are exactly the coefficient formulas `c_0 = γ_0·2^wt(r)`,
`c_1 = γ_1·2^(k+wt(r))` found numerically in round 27 (since
`#subm r = 2^wt(r)`), now proved.  The same `W_zero`/`W_one` give the closed
form for every row of degree ≤ 1 (ℤ² von Neumann, ℤ² Moore, triangular,
the two quarter planes) by substituting their `γ` from `Rep.lean`.

## Round 29-30: the Stern-Brocot connection (Brocot.lean)

Companion to `docs/52-stern-brocot.md` and `docs/53-cross-domain-survey.md`.
48 declarations, alone in the dependency graph (imports Mathlib only),
compiled with `lean -o Brocot.olean Brocot.lean`.

Axioms: `[propext, Classical.choice, Quot.sound]`, no `sorry` anywhere.

Milestones:

* `land_add_iff` --- **the no-carry lemma**: `u &&& (u + h) = u ↔ u &&& h = 0`
  (strong induction on `h`, four parity cases, each one `omega` step).
* `mem_sig_iff` --- the dead-offset set `sig d` is exactly
  `{u ≤ d : u &&& ((u+d)/2) = u}`, i.e. `u` is a submask of `⌊(u+d)/2⌋`.
* four membership recursions `mem_sig_two_mul`, `mem_sig_two_mul_add_one`,
  `mem_sig_odd_two_mul`, `mem_sig_odd_two_mul_add_one`; four Finset
  decompositions; six cardinality recursions.
* `fusc` (Stern, A002487) with `fusc_two_mul` and `fusc_two_mul_add_one`.
* **`card_sig_stern`** --- `(sig d).card = fusc d + fusc (d + 1)`, by strong
  induction on the triple `(A, p, q)` (`stern_triple`).

`Dual.lean` then proves the dual closed form (theorem A of docs/52) on top of a hand-built
`testBit` API: `mem_shell_dual : d ∈ shell t ↔ (2^(log2 t + 1) - t - 1) ∈ sig d`.