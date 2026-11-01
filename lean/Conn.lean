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
  | 0, false => 1 | 0, true => 0
  | 1, false => 1 | 1, true => 2
  | 2, false => 2 | 2, true => 2
  | _, _ => 0

def oB : Nat → Nat
  | 0 => 0 | 1 => 0 | 2 => 1 | _ => 0

def hasZero : Nat → Bool
  | 0 => false
  | n + 1 => if (n + 1) % 2 = 0 then true else hasZero ((n + 1) / 2)

def hasOne : Nat → Bool
  | 0 => false
  | n + 1 => if (n + 1) % 2 = 1 then true else hasOne ((n + 1) / 2)

def maxDig : Nat → Nat
  | 0 => 0
  | n + 1 => max ((n + 1) % 2) (maxDig ((n + 1) / 2))

def minDig : Nat → Nat
  | 0 => 1
  | n + 1 => min ((n + 1) % 2) (minDig ((n + 1) / 2))

lemma hasZero_odd (m : Nat) : hasZero (2 * m + 1) = hasZero m := by
  have h : (2 * m + 1) % 2 = 1 := by omega
  have h2 : (2 * m + 1) / 2 = m := by omega
  simp [hasZero, h, h2]

lemma hasOne_even (m : Nat) : hasOne (2 * m) = hasOne m := by
  cases m with
  | zero => rfl
  | succ k =>
    have e : 2 * (k + 1) = (2 * k + 1) + 1 := by omega
    rw [e]
    have h : (2 * k + 1 + 1) % 2 = 0 := by omega
    have h2 : (2 * k + 1 + 1) / 2 = k + 1 := by omega
    simp [hasOne, h, h2]

lemma hasOne_odd (m : Nat) : hasOne (2 * m + 1) = true := by
  have h : (2 * m + 1) % 2 = 1 := by omega
  simp [hasOne, h]

lemma hasOne_pos : ∀ m, 1 ≤ m → hasOne m = true := by
  intro m
  induction m using Nat.strong_induction_on with
  | _ m ih =>
    intro hm
    cases m with
    | zero => omega
    | succ k =>
      by_cases h : (k + 1) % 2 = 1
      · simp [hasOne, h]
      · have h2 : (k + 1) % 2 = 0 := by omega
        simp [hasOne, h2]
        exact ih ((k + 1) / 2) (by omega) (by omega)
lemma maxDig_le : ∀ n, maxDig n ≤ 1 := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    cases n with
    | zero => simp [maxDig]
    | succ k =>
      have hm : maxDig ((k + 1) / 2) ≤ 1 := ih ((k + 1) / 2) (by omega)
      simp [maxDig]
      omega

lemma maxDig_one : ∀ n, 1 ≤ n → maxDig n = 1 := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro hn
    cases n with
    | zero => omega
    | succ k =>
      by_cases h : (k + 1) % 2 = 1
      · have hm := maxDig_le ((k + 1) / 2)
        simp [maxDig, h]
        omega
      · have h2 : (k + 1) % 2 = 0 := by omega
        have hm : 1 ≤ (k + 1) / 2 := by omega
        simp [maxDig, h2, ih ((k + 1) / 2) (by omega) hm]
lemma minDig_spec : ∀ n, 1 ≤ n → minDig n = (if hasZero n then 0 else 1) := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro hn
    cases n with
    | zero => omega
    | succ k =>
      by_cases h : (k + 1) % 2 = 0
      · have hz : hasZero (k + 1) = true := by simp [hasZero, h]
        unfold minDig
        rw [h]
        simp [hz]
      · have h2 : (k + 1) % 2 = 1 := by
          have hlt : (k + 1) % 2 < 2 := Nat.mod_lt _ (by decide)
          omega
        have hz : hasZero (k + 1) = hasZero ((k + 1) / 2) := by simp [hasZero, h2]
        by_cases hm0 : (k + 1) / 2 = 0
        · -- k + 1 = 1
          have hk : k = 0 := by omega
          subst hk
          simp [minDig, hasZero]
        · have hm : 1 ≤ (k + 1) / 2 := by omega
          unfold minDig
          rw [h2, ih ((k + 1) / 2) (by omega) hm, hz]
          split <;> simp

lemma aut_spec : ∀ n,
    (oB (fold δB 0 n) = (if hasZero n then 1 else 0)) ∧
    (oB (fold δB 1 n) = (if hasOne n then 1 else 0)) ∧
    (oB (fold δB 2 n) = 1) := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    cases n with
    | zero => simp [fold, hasZero, hasOne, oB]
    | succ k =>
      obtain ⟨i1, i2, i3⟩ := ih ((k + 1) / 2) (by omega)
      by_cases h : (k + 1) % 2 = 0
      · have hz : hasZero (k + 1) = true := by simp [hasZero, h]
        have ho : hasOne (k + 1) = hasOne ((k + 1) / 2) := by simp [hasOne, h]
        have hm : 1 ≤ (k + 1) / 2 := by omega
        have hop : hasOne ((k + 1) / 2) = true := hasOne_pos _ hm
        have f0 : fold δB 0 (k + 1) = fold δB 1 ((k + 1) / 2) := by
          rw [fold_succ]; simp [δB, h]
        have f1 : fold δB 1 (k + 1) = fold δB 1 ((k + 1) / 2) := by
          rw [fold_succ]; simp [δB, h]
        have f2 : fold δB 2 (k + 1) = fold δB 2 ((k + 1) / 2) := by
          rw [fold_succ]; simp [δB, h]
        refine ⟨?_, ?_, ?_⟩
        · simp [f0, i2, hop, hz]
        · simp [f1, i2, ho, hop]
        · simp [f2, i3]
      · have h2 : (k + 1) % 2 = 1 := by
          have hlt : (k + 1) % 2 < 2 := Nat.mod_lt _ (by decide)
          omega
        have hz : hasZero (k + 1) = hasZero ((k + 1) / 2) := by simp [hasZero, h2]
        have ho : hasOne (k + 1) = true := by simp [hasOne, h2]
        have f0 : fold δB 0 (k + 1) = fold δB 0 ((k + 1) / 2) := by
          rw [fold_succ]; simp [δB, h2]
        have f1 : fold δB 1 (k + 1) = fold δB 2 ((k + 1) / 2) := by
          rw [fold_succ]; simp [δB, h2]
        have f2 : fold δB 2 (k + 1) = fold δB 2 ((k + 1) / 2) := by
          rw [fold_succ]; simp [δB, h2]
        refine ⟨?_, ?_, ?_⟩
        · simp [f0, i1, hz]
        · simp [f1, i3, ho]
        · rw [f2, i3]

/-- A043545: the automaton computes (max binary digit) - (min binary digit). -/
theorem A043545_digits (n : Nat) (hn : 1 ≤ n) :
    oB (fold δB 0 n) = maxDig n - minDig n := by
  have h1 := (aut_spec n).1
  rw [h1, maxDig_one n hn, minDig_spec n hn]
  split <;> rfl

#eval (List.range 10).map (fun n => oB (fold δB 0 (n + 1)))
#eval (List.range 10).map (fun n => maxDig (n + 1) - minDig (n + 1))
#print axioms A043545_digits

end OEIS
