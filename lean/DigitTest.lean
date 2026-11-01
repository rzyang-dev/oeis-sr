import Mathlib

namespace OEIS

def hasZero : Nat → Bool
  | 0 => false
  | n + 1 => if (n + 1) % 2 = 0 then true else hasZero ((n + 1) / 2)

def hasOne : Nat → Bool
  | 0 => false
  | n + 1 => if (n + 1) % 2 = 1 then true else hasOne ((n + 1) / 2)

lemma hasZero_odd (m : Nat) : hasZero (2 * m + 1) = hasZero m := by
  have h : (2 * m + 1) % 2 = 1 := by omega
  have h2 : (2 * m + 1) / 2 = m := by omega
  simp [hasZero, h, h2]

lemma hasOne_even (m : Nat) : hasOne (2 * m) = hasOne m := by
  cases m with
  | zero => rfl
  | succ k =>
    have h : (2 * (k + 1)) % 2 = 0 := by omega
    have h2 : (2 * (k + 1)) / 2 = k + 1 := by omega
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

end OEIS
