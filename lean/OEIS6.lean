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

/-- Does the binary expansion of n contain the digit 0? -/
def hasZero : Nat → Bool
  | 0 => false
  | n + 1 => if (n + 1) % 2 = 0 then true else hasZero ((n + 1) / 2)

/-- Does the binary expansion of n contain the digit 1? -/
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
  rw [show 2 * m + 1 = 2 * m + 1 by rfl]
  simp [hasZero]

lemma hasOne_even (m : Nat) : hasOne (2 * m) = hasOne m := by
  cases m with
  | zero => simp [hasOne]
  | succ k => simp [hasOne]; omega

lemma hasOne_odd (m : Nat) : hasOne (2 * m + 1) = true := by
  simp [hasOne]

lemma hasZero_even (m : Nat) (hm : 1 ≤ m) : hasZero (2 * m) = true := by
  cases m with
  | zero => omega
  | succ k => simp [hasZero]

lemma hasOne_pos (m : Nat) (hm : 1 ≤ m) : hasOne m = true := by
  cases m with
  | zero => omega
  | succ k =>
    rw [hasOne]
    split <;> simp_all

end OEIS
