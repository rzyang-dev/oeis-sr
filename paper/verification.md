# Verification manifest

Every quantitative statement in main.md is backed either by a Lean theorem or by a script that can be
re-run. This file records exactly what was checked, how, and over which range.

## 1. Lean development

Location: lean/. Toolchain: Lean 4.34.1 + Mathlib.

* 21 files, 395 declarations, 0 occurrences of sorry.
* Axioms of every main theorem: propext, Classical.choice, Quot.sound only
  (checked with #print axioms).
* **Audit**: on the final day every .olean was deleted and the 21 files were rebuilt in dependency
  order; all 21 exited with code 0. Total artifact size 19.7 MB.

Build order: Universal, Shells, Instances, Final, Census, Tree, Parity, Moments, ShellSq, Dim3,
Cubic, Dim4, Arm, Rep, Digits, Matrix, Brocot, Dual, SelfSim, Mass, Hyp.

Mapping from the paper to Lean:

| paper | Lean |
|---|---|
| Theorem 2 (abstract space) | row_closed_form, F_step, universal_zero_iff |
| Theorem 2 (instances) | the three instance files (line, plane vN/Moore, binary tree) |
| Theorem 3 | card_shell, shell_eq_image, shell_card_eq |
| Theorem 4 | row_zero_pos_eq_shell, Z_row_linear |
| Theorem 5 | mem_shell_dual |
| Lemma 6.1 | shell_sum_of_poly_correction |
| Lemma 6.2 | X_iterate, W_eq_A |
| Theorem 7.1 | card_sig_stern |
| Theorem 7.2, 7.3 | card_Hyp, card_sig_split |
| Theorem 8 | SS_two_mul, SS_two_pow, sum_pow_wt, block_shell_mass |
| Theorem 9 | not formalised |
| Theorem 6 | not formalised |

Reproduce a single file:

    $env:LEAN_PATH="<lean dir + 9 mathlib paths>"; lean -o FILE.olean FILE.lean

The exact LEAN_PATH string is in lean/README.md.

## 2. Numerical checks

All scripts are run as: py -3 scripts/NAME.py . Nothing outside the standard library is used except
numpy in scripts/320_layer_rules.py.

| claim | script | range | result |
|---|---|---|---|
| Theorem 5 (dual form) | 307_dual_form.py | t <= 16384, all d | 0 violations (1.3e8 cases) |
| Theorem 7.1 | 308_stern.py | d <= 4000 | 0 |
| Theorem 7.4 (parity recursions) | 311_stern_proof.py | d <= 400 | 0 |
| no-carry lemma, Theorem 7.3 | 313_nocarry.py | u,h < 300 and n < 800 | 0 |
| per-block counts | 314b_block_count.py | k <= 15 | 0 |
| block mass and Gould | 315_survey.py | k <= 12 | 0 |
| Theorem 8 | 317b_selfsimilar.py | N < 32768 | 0 |
| Theorem 9 | 320_layer_rules.py | 256 rules, t <= 200 | see report |
| Theorem 6 | 321_rank_measure.py | 1016 polynomials, K <= 7 | 0 counterexamples |
| Theorem 7.2 | 322_brocot_bijection.py | d <= 2000 | 0 |
| independent re-check, 7.2-7.4 | 325_verify_brocot.py | d <= 599 | 0 |
| independent re-check, Thm 6 | 326b_verify_rank.py | 625 polynomials | 0 |
| Lemma 6.2 | 333b_A_formula.py | 1920 entries | 0 |

## 3. The three refuted claims

Recorded in section 12 of the paper and in full in docs/51 and docs/60.

1. rank_2 = #supp(c(x) + c(x-1)): correct on the 13 natural geometries (all have dense support),
   false in 78 of 625 small polynomials. Correct replacement: #DClose.
2. [d in S(t)] = binom(t, (t+d)/2) mod 2: false in 110 of 819 cases. The row direction is count-level
   only.
3. Lemma 6.2 tested with the factors of A(k,j) reversed: 216 spurious mismatches out of 1920.
   The recursion order is b_0 leftmost.

## 4. What is NOT verified

* Theorem 6 is proved on paper and checked numerically; the proof has not been formalised.
* Theorem 9 is a finite enumeration plus a paper induction; not formalised.
* The non-polynomial case of the rank problem (level functions that are not eventually polynomial) is
  open; only conjectures with numerical support exist (docs/55, section 9).
* The literature search was limited (see section 11 of the paper).
