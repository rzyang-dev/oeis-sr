# Rule 129 from a single 1: closed form, renormalization lemma, and proof

Status: every statement below is verified on a fixed window (N = 2400 cells either side,
T = 1150 steps, boundary all-1; only |j| <= N-t is read). The renormalization lemma has a
complete proof modulo two *universal local lemmas* checked exhaustively over all 2048 local
patterns on 11 cells.

A parallel report by another agent in this folder (`REPORT_rule129.md`) proposes a closed form.
Section 1 below records that I verified it **independently** (separate implementation, 0 failures
for all t <= 1150 and all |j| <= t). It supersedes the recurrence as a description and makes
Theorem 1 a corollary.

---

## 0. Conventions

* `V_t(j) ∈ {0,1}` = cell value; `V_0(j) = [j=0]`; `V_{t+1}(j)=1 ⇔ V_t(j-1)=V_t(j)=V_t(j+1)`.
* `V_t(j) = 1` for `|j| > t`, `t ≥ 1`.
* `[P] ∈ {0,1}` is an indicator. `s_2(n)` = number of 1-bits.
* Edges (parent's `e_t`): `E_t = {j : V_t(j) ≠ V_t(j+1)}`, `e_t(j)=[j∈E_t]`, `R_t = E_t ∩ [0,∞)`.
* Half-line operators: `(ΦW)(j) = [W(j-1)=W(j)=W(j+1)]`, `W(-j):=W(j)` (even extension);
  `(SW)(j) = W(⌊j/2⌋)` ("2-fold stretch"); `S W` is always even.

---

## 1. Closed form (independently verified)

Let `r(t) = t - 2^{⌊log2 t⌋}` (t with its leading 1-bit deleted) for `t ≥ 1`, and let
`m ⊆ r` denote the bitwise submask relation `m & r = m`.

> **Theorem 0.** For every `t ≥ 1` and every `j ∈ Z`:
> `V_t(j) = 0 ⇔ |j| ≤ t` and `⌊(t-|j|)/2⌋ ⊆ r(t)`.
> Equivalently, with depth `d = t-|j|`: `V_t(t-d) = 1 - [⌊d/2⌋ ⊆ r(t)]`.

Consequences (each verified separately, t <= 1150 / 600):
* `V_t` is constant on the depth pairs `(2s, 2s+1)`: `V_t(t-2s) = V_t(t-2s-1) = 1 - [s ⊆ r(t)]`.
* `|Z(t) ∩ [0,t]| = 2^{s_2(t)}` and `|E_t| = 2^{s_2(t+1)}`.
* `V_t(0) = 0 ⇔ ⌊t/2⌋ ⊆ r(t) ⇔ t = 2^k - 1`.
* "Era recursion" for `R^{(Z)}_t := Z(t) ∩ [0,∞)`, `t = 2^K + m`, `0 ≤ m < 2^K`:
  `m < 2^{K-1} ⇒ R^{(Z)}_t = 2^{K-1} + R^{(Z)}_{t-2^{K-1}}`,
  `m ≥ 2^{K-1} ⇒ R^{(Z)}_t = R^{(Z)}_m ∪ (2^K + R^{(Z)}_m)`.
  Verified for K <= 10, all m, 0 failures.

Independent evidence: all `t ≤ 1150`, all `|j| ≤ t`: **0 failures**; depth form `t ≤ 299` all d:
0 failures; counts `t ≤ 599`: exact; era recursion `K ≤ 10`: exact.

Note Theorem 0 ⟹ Theorem 1 below, because for odd `T = 2t+1` one has `r(T) = 2r(t)+1` and
`n ⊆ 2r+1 ⇔ ⌊n/2⌋ ⊆ r`.

---

## 2. Renormalization lemma (odd-time self-similarity)

> **Theorem 1.** For every `t ≥ 1` and `j ∈ Z`: `V_{2t+1}(j) = V_t(⌊|j|/2⌋)`.
> Equivalently (V_t even): `V_{2t+1}(2j) = V_{2t+1}(2j+1) = V_t(j)` for `j ≥ 0`.

So odd rows are exact 2-fold stretches of earlier rows. Verified: all `t ≤ 574` and `|j| ≤ 2t+1`,
**0 failures**. Corollaries: `V_{2^k-1}` is all-zero on `[-(2^k-1), 2^k-1]`; the parity invariant
of edges (`j<0 ⇒ j ≡ t+1`, `j≥0 ⇒ j ≡ t` mod 2); and the parent's (4) `R_{2t+1} = 2R_t+1`.

The naive identity is *not* the right statement: `state(2^k+m-1)` and `state(m-1)` are different
times. Re-checked: it holds only for `k=3, m∈{5,6,7}` and `k=4, m∈{9,10,11,12}` (and no `m ≤ 12`
for `k=5`) — an accident.

---

## 3. Even-time formula

> **Theorem 2.** For `t ≥ 2`, all `j ∈ Z`:
> `V_{2t}(0)=1`; `V_{2t}(2j) = 1 ⇔ V_{t-1}(j-1)=V_{t-1}(j)` (`j≥1`);
> `V_{2t}(2j+1) = 1 ⇔ V_{t-1}(j)=V_{t-1}(j+1)` (`j≥0`); and `V_{2t}(-j)=V_{2t}(j)`.
> In edges: `e_{2t}(2j+1)=0`, `e_{2t}(2j) = e_{t-1}(j-1) ⊕ e_{t-1}(j)`.

Verified `t ≤ 575`, **0 failures**. It is Theorem 1 at `t-1` plus one CA step.

---

## 4. Complete recursive description

Define rows `R(t)` on `j ≥ 0` (`1`-tail):

    R(1) = (0,0,1,1,1,...)
    R(2) = (1,0,0,1,1,1,...)
    R(3) = S(R(1))
    t >= 4 odd :  R(t) = S( R((t-1)/2) )
    t >= 4 even:  R(t) = Φ( S( R(t/2 - 1) ) )

> **Theorem 3.** `R(t)(j) = V_t(j)` for all `t ≥ 1`, `j ≥ 0`.

Equivalently, for all `t ≥ 1`: `V_{2t+1} = S(V_t)` and `V_{2t+2} = Φ(S(V_t))`.
Verified end-to-end against direct simulation for **all `t ≤ 1150`: 0 failures**.
The recursion halves the index each level, so `V_t(j)` is computable in `O(log t)`.

---

## 5. Edge recurrences and counts

With `∂R = {n ≥ 0 : [n-1 ∈ R] ≠ [n ∈ R]}` and `[-1 ∈ R] := 0`:

> **Theorem 4.** `R_{2t+1} = 2R_t + 1` (`t ≥ 1`);  `R_{2t} = 2·∂R_{t-1}` (`t ≥ 2`).

(The first is the parent's (4); the second is the even-time recursion asked for.)
Verified `t ≤ 574`, **0 failures**.

> **Corollary 5.** `|E_{2t+1}| = |E_t|`, `|E_{2t}| = 2|E_{t-1}|`; sharp form `|E_t| = 2^{s_2(t+1)}`,
> `|Z(t)∩[0,t]| = 2^{s_2(t)}`. Values `|E_t|`, t=0..16: 2,2,4,2,4,4,8,2,4,4,8,4,8,8,16,2,4.

WARNING: the parent's (6) `|E_{2^k+m}| = 2|E_m|` is false (k=1, m=1: `|E_3|=2` but `2|E_1|=4`).
Corollary 5 is the correct statement.

---

## 6. Middle cell / middle edge

> **Theorem 6.** For `t ≥ 0`: `e_t(0) = 1 ⇔ t+2` is a power of 2 (`t = 2^k-2`);
> `V_t(0) = 0 ⇔ t+1` is a power of 2; and `V_t(0) = 1 - e_{t-1}(0)`.

Proof from Theorem 4:
* `R_{2t+1} = 2R_t+1` has only odd elements `≥ 1`, so `e_{2t+1}(0)=0`.
* `R_{2t} = 2∂R_{t-1}` gives `e_{2t}(0) = [0 ∈ ∂R_{t-1}] = [0 ∈ R_{t-1}] = e_{t-1}(0)`
  (as `-1 ∉ R_{t-1}`).
* Base `e_0(0)=1`, `0+2=2`. Induction: t odd ⇒ 0; t = 2s ⇒ `e_{s-1}(0)=1 ⇔ s+1=2^k ⇔ t+2=2^{k+1}`.
  QED.  (Verified t <= 1100, 0 failures.)

---

## 7. Full alternating states

> **Theorem 7.** For `k ≥ 1`, `t = 2^k-2`: `R_t = {0,2,...,2^k-2}` and
> `E_t = {j : |j| ≤ 2^k-1, j ≡ 2^k-1 (mod 2) for j<0, j ≡ 2^k-2 (mod 2) for j≥0}`.

Verified `k ≤ 10`, 0 failures. Follows from Theorem 4 by induction (`R_0 = {0}`).

---

## 8. Proof of Theorem 1

8.1 Reduction to the half line. `V_t(-j)=V_t(j)` (reflection symmetry of rule + initial state,
by induction). So the row is determined by `j ≥ 0`, and the CA step there is `Φ` with `W(-j):=W(j)`.

8.2 Two universal lemmas (local; verified for *all* `2^{11}=2048` patterns on `[0,10]` with
1-tail, all positions in window, 0 failures):

> **(L1)** `Φ²(S(S(W))) = S(Φ(S(W)))` for every `W`.
>
> **(L2)** For every `X`, put `W = Φ(S(X))`, i.e. `W(0)=1`, `W(2j) = [X(j-1)=X(j)]` (`j≥1`),
> `W(2j+1) = [X(j)=X(j+1)]` (`j≥0`). Then `Φ²(S(W)) = S(Φ(W))`.

`W = Φ(S(X))` is exactly the even-row formula, so (L2) says the one-step commutation
`Φ²∘S = S∘Φ` — false for almost every configuration (counterexample: `W = [1,0,0,0,...]`,
the single 1) — nevertheless holds on **all** even rows. This is the reason a naive
block-substitution proof fails and these two lemmas are the right inductive invariants.

8.3 Induction for `C(t) :=` Theorem 1.
* Base: `V_3 = S(V_1)`, `V_5 = S(V_2)`, `V_7 = S(V_3)` (finite checks).
* Step `t ≥ 4`: `V_{2t+1} = Φ²(V_{2t-1}) = Φ²(S(V_{t-1}))` by `C(t-1)`; show it equals
  `S(Φ(V_{t-1})) = S(V_t)`.
  - `t` even: `t-1 = 2u+1` with `u=(t-2)/2 < t`; `C(u)` gives `V_{t-1}=S(V_u)`; apply (L1).
  - `t` odd: `t-1 = 2s`, `s=(t-1)/2`; `C(s-1)` gives `V_{t-1}=Φ(S(V_{s-1}))`; apply (L2).
  Only smaller instances of `C` are used; strong induction closes. QED.

8.4 Consequences: Theorem 2 = expand `V_{2t}=Φ(S(V_{t-1}))`; Theorem 4 = edge translation of
Theorems 1–2; Theorems 6,7 = induction on Theorem 4; Theorem 0 is equivalent to Theorem 1's
iterated form (or can be proved directly by the same induction).

---

## 9. Numerical evidence summary

| statement | range | failures |
|---|---|---|
| Thm 0 closed form | `t ≤ 1150`, all `|j| ≤ t` | 0 |
| Thm 0 depth form | `t ≤ 299`, all d | 0 |
| `|Z(t)∩[0,t]| = 2^{s_2(t)}`, `|E_t| = 2^{s_2(t+1)}` | `t ≤ 599` | 0 |
| Thm 0 era recursion (Z, right half) | `K ≤ 10`, all m | 0 |
| Thm 1 `V_{2t+1}=S(V_t)` | `t ≤ 574`, `|j| ≤ 2t+1` | 0 |
| Thm 2 even-row formula | `t ≤ 575` | 0 |
| Thm 3 recursion `R(t)=V_t` | `t ≤ 1150` | 0 |
| Thm 4 `R`-recursions | `t ≤ 574` | 0 |
| Cor 5 counts | `t ≤ 574` | 0 |
| Thm 6 middle cell/edge | `t ≤ 1100` | 0 |
| Thm 7 full alternating | `k ≤ 10` | 0 |
| (L1),(L2) | all 2048 patterns on 11 cells | 0 |
| unrestricted `Φ²S = SΦ` | 63 of 64 patterns on 6 cells | FAILS (expected) |

---

## 10. Files

* `work_r129/summary.py` — simulation + all identity checks of section 9.
* `work_r129/final_check.py` — end-to-end recursion vs simulation (`t ≤ 1150`) and (L1),(L2).
* `work_r129/lemmas_large.py` — (L1),(L2) on 1024/2048 patterns.
* `work_r129/verify_closedform.py` — independent verification of Theorem 0, counts, era recursion.
* `work_r129/verify_final.py` — unrestricted-commutation counterexample, R-recursions, middle cell.
* `work_r129/rule129_zerosef.png` — zero set, `t ≤ 340`, black = 0 (nested self-similar triangles).

Run `py -3 <file>` in that directory (Python 3.13 + numpy).
