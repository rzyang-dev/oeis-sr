import Mathlib

namespace OEIS

def fold (δ : Nat → Bool → Nat) (s : Nat) : Nat → Nat
  | 0 => s
  | n + 1 => fold δ (δ s ((n + 1) % 2 == 1)) ((n + 1) / 2)
  termination_by n => n
  decreasing_by omega

lemma fold_succ (δ : Nat → Bool → Nat) (s n : Nat) :
    fold δ s (n + 1) = fold δ (δ s ((n + 1) % 2 == 1)) ((n + 1) / 2) := by
  rw [fold]

/-- Every n >= 1 ends (in LSB-first order) with the digit 1, so the final
state is delta p true for some reachable state p. -/

def δB : Nat → Bool → Nat
  | 0, false => 1 | 0, true => 2
  | 1, false => 3 | 1, true => 4
  | 2, false => 2 | 2, true => 2
  | 3, false => 3 | 3, true => 5
  | 4, false => 6 | 4, true => 1
  | 5, false => 5 | 5, true => 5
  | 6, false => 6 | 6, true => 2
  | _, _ => 0

def oB : Nat → Nat
  | 0 => 1 | 1 => 1 | 2 => 1 | 3 => 1 | 4 => 0 | 5 => 0 | 6 => 0 | _ => 0

/-- A039982: limit of S(0)=1, S(n+1) = 1 . phi(S(n)) with phi(0)=11, phi(1)=10. -/
def w39 : Nat → Nat
  | 0 => 1
  | n + 1 => if (n + 1) % 2 = 1 then 1 else 1 - w39 ((n + 1) / 2 - 1)

lemma w39_odd (m : Nat) : w39 (2 * m + 1) = 1 := by
  have h : (2 * m + 1) % 2 = 1 := by omega
  simp [w39, h]

lemma w39_even (m : Nat) : w39 (2 * m + 2) = 1 - w39 m := by
  have e : 2 * m + 2 = (2 * m + 1) + 1 := by omega
  rw [e, w39]
  have h : ¬ ((2 * m + 1 + 1) % 2 = 1) := by omega
  rw [if_neg h]
  have h2 : (2 * m + 1 + 1) / 2 - 1 = m := by omega
  rw [h2]

lemma w39_four (m : Nat) (hm : 1 ≤ m) : w39 (4 * m) = 0 := by
  have e : 4 * m = 2 * (2 * m - 1) + 2 := by omega
  rw [e, w39_even]
  have h : 2 * m - 1 = 2 * (m - 1) + 1 := by omega
  rw [h, w39_odd]

lemma w39_le : ∀ n, w39 n ≤ 1 := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    cases n with
    | zero => simp [w39]
    | succ k =>
      have hlt : (k + 1) % 2 < 2 := Nat.mod_lt _ (by decide)
      interval_cases h : (k + 1) % 2
      · have h1 : w39 (k + 1) = 1 - w39 ((k + 1) / 2 - 1) := by simp [w39, h]
        rw [h1]
        have hh := ih ((k + 1) / 2 - 1) (by omega)
        omega
      · have h1 : w39 (k + 1) = 1 := by simp [w39, h]
        rw [h1]

lemma all_states : ∀ n,
    (oB (fold δB 0 n) = w39 n) ∧
    (oB (fold δB 1 n) = w39 (2 * n)) ∧
    (oB (fold δB 2 n) = 1) ∧
    (oB (fold δB 3 n) = if n = 0 then 1 else 0) ∧
    (oB (fold δB 4 n) = 1 - w39 (2 * n)) ∧
    (oB (fold δB 5 n) = 0) ∧
    (oB (fold δB 6 n) = if n = 0 then 0 else 1) := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    cases n with
    | zero => simp [fold, w39, oB]
    | succ k =>
      obtain ⟨i0, i1, i2, i3, i4, i5, i6⟩ := ih ((k + 1) / 2) (by omega)
      have hlt : (k + 1) % 2 < 2 := Nat.mod_lt _ (by decide)
      have hk0 : k + 1 ≠ 0 := by omega
      interval_cases h : (k + 1) % 2
      · have hm : 1 ≤ (k + 1) / 2 := by omega
        have hm0 : ¬ ((k + 1) / 2 = 0) := by omega
        have hb : ((k + 1) % 2 == 1) = false := by simp [h]
        refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
        · rw [fold_succ, hb]; change oB (fold δB 1 ((k+1)/2)) = w39 (k+1)
          rw [i1]; congr 1; omega
        · rw [fold_succ, hb]; change oB (fold δB 3 ((k+1)/2)) = w39 (2*(k+1))
          rw [i3, if_neg hm0, show 2*(k+1) = 4*((k+1)/2) by omega, w39_four _ hm]
        · rw [fold_succ, hb]; change oB (fold δB 2 ((k+1)/2)) = 1
          rw [i2]
        · rw [fold_succ, hb]; change oB (fold δB 3 ((k+1)/2)) = (if k+1 = 0 then 1 else 0)
          rw [i3, if_neg hm0, if_neg hk0]
        · rw [fold_succ, hb]; change oB (fold δB 6 ((k+1)/2)) = 1 - w39 (2*(k+1))
          rw [i6, if_neg hm0, show 2*(k+1) = 4*((k+1)/2) by omega, w39_four _ hm]
        · rw [fold_succ, hb]; change oB (fold δB 5 ((k+1)/2)) = 0
          rw [i5]
        · rw [fold_succ, hb]; change oB (fold δB 6 ((k+1)/2)) = (if k+1 = 0 then 0 else 1)
          rw [i6, if_neg hm0, if_neg hk0]
      · have hb : ((k + 1) % 2 == 1) = true := by simp [h]
        refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
        · rw [fold_succ, hb]; change oB (fold δB 2 ((k+1)/2)) = w39 (k+1)
          rw [i2, show k+1 = 2*((k+1)/2)+1 by omega, w39_odd]
        · rw [fold_succ, hb]; change oB (fold δB 4 ((k+1)/2)) = w39 (2*(k+1))
          rw [i4, show 2*(k+1) = 2*(2*((k+1)/2))+2 by omega, w39_even]
        · rw [fold_succ, hb]; change oB (fold δB 2 ((k+1)/2)) = 1
          rw [i2]
        · rw [fold_succ, hb]; change oB (fold δB 5 ((k+1)/2)) = (if k+1 = 0 then 1 else 0)
          rw [i5, if_neg hk0]
        · rw [fold_succ, hb]; change oB (fold δB 1 ((k+1)/2)) = 1 - w39 (2*(k+1))
          rw [i1, show 2*(k+1) = 2*(2*((k+1)/2))+2 by omega, w39_even]
          have hle := w39_le (2 * ((k+1)/2))
          omega
        · rw [fold_succ, hb]; change oB (fold δB 5 ((k+1)/2)) = 0
          rw [i5]
        · rw [fold_succ, hb]; change oB (fold δB 2 ((k+1)/2)) = (if k+1 = 0 then 0 else 1)
          rw [i2, if_neg hk0]

/-- A039982: the automaton computes the morphic limit word. -/
theorem A039982_morphic (n : Nat) : oB (fold δB 0 n) = w39 n := (all_states n).1

#eval (List.range 12).map (fun n => oB (fold δB 0 n))
#eval (List.range 12).map w39
#print axioms A039982_morphic

end OEIS