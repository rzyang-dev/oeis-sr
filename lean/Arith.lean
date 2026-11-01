import Mathlib
lemma a1 (k c : Nat) (hc : c ≤ 1) : ((k + 1) % 2 + c) / 2 ≤ 1 := by
  have h : (k + 1) % 2 = 0 ∨ (k + 1) % 2 = 1 := by omega
  rcases h with h | h <;> rw [h] <;> omega

lemma a2 (k c : Nat) : ((k + 1) % 2 + c) % 2 = (k + c + 1) % 2 := by
  have h : (k + 1) % 2 = 0 ∨ (k + 1) % 2 = 1 := by omega
  rcases h with h | h <;> rw [h] <;> omega

lemma a3 (k c : Nat) : (k + 1) / 2 + ((k + 1) % 2 + c) / 2 = (k + c + 1) / 2 := by
  have h : (k + 1) % 2 = 0 ∨ (k + 1) % 2 = 1 := by omega
  rcases h with h | h <;> rw [h] <;> omega
