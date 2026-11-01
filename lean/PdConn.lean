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

def δY : Nat → Bool → Nat
  | 0, false => 1 | 0, true => 2
  | 1, false => 1 | 1, true => 1
  | 2, false => 3 | 2, true => 0
  | 3, false => 3 | 3, true => 3
  | _, _ => 0

def oY : Nat → Nat
  | 0 => 0 | 1 => 0 | 2 => 1 | 3 => 1 | _ => 0

/-- Period-doubling recurrence (OEIS A096268). -/
def pd : Nat → Nat
  | 0 => 0
  | n + 1 => if (n + 1) % 2 = 0 then 0 else 1 - pd ((n + 1) / 2)

def phi : Nat → Nat
  | 0 => 2 | 1 => 3 | 2 => 0 | 3 => 1 | _ => 0

lemma δY_lt : ∀ s < 4, ∀ d : Bool, δY s d < 4 := by decide
lemma phi_lt : ∀ s < 4, phi s < 4 := by decide
lemma phi_comm : ∀ s < 4, ∀ d : Bool, δY (phi s) d = phi (δY s d) := by decide
lemma oY_phi : ∀ s < 4, oY (phi s) = 1 - oY s := by decide

lemma fold_lt4 : ∀ m s, s < 4 → fold δY s m < 4 := by
  intro m
  induction m using Nat.strong_induction_on with
  | _ m ih =>
    intro s hs
    cases m with
    | zero => simpa [fold] using hs
    | succ k =>
      rw [fold_succ]
      exact ih ((k + 1) / 2) (by omega) (δY s ((k + 1) % 2 == 1)) (δY_lt s hs _)

lemma fold_absorb : ∀ m, fold δY 1 m = 1 := by
  intro m
  induction m using Nat.strong_induction_on with
  | _ m ih =>
    cases m with
    | zero => simp [fold]
    | succ k =>
      rw [fold_succ]
      have h : δY 1 ((k + 1) % 2 == 1) = 1 := by
        cases ((k + 1) % 2 == 1) <;> rfl
      rw [h]
      exact ih ((k + 1) / 2) (by omega)

lemma fold_phi : ∀ m s, s < 4 → fold δY (phi s) m = phi (fold δY s m) := by
  intro m
  induction m using Nat.strong_induction_on with
  | _ m ih =>
    intro s hs
    cases m with
    | zero => simp [fold]
    | succ k =>
      rw [fold_succ, fold_succ]
      rw [phi_comm s hs _]
      exact ih ((k + 1) / 2) (by omega) (δY s ((k + 1) % 2 == 1)) (δY_lt s hs _)

lemma fold_two (m : Nat) : oY (fold δY 2 m) = 1 - oY (fold δY 0 m) := by
  have h0 : (0 : Nat) < 4 := by decide
  have hp := fold_phi m 0 h0
  have hp2 : fold δY 2 m = phi (fold δY 0 m) := by simpa [phi] using hp
  rw [hp2]
  exact oY_phi (fold δY 0 m) (fold_lt4 m 0 h0)

/-- A096268: the automaton computes the period-doubling recurrence. -/
theorem A096268_pd : ∀ n, oY (fold δY 0 n) = pd n := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    cases n with
    | zero => simp [fold, pd, oY]
    | succ k =>
      by_cases h : (k + 1) % 2 = 0
      · have f : fold δY 0 (k + 1) = fold δY 1 ((k + 1) / 2) := by
          rw [fold_succ]; simp [δY, h]
        have hp : pd (k + 1) = 0 := by simp [pd, h]
        rw [f, fold_absorb, hp]
        rfl
      · have h2 : (k + 1) % 2 = 1 := by
          have hlt : (k + 1) % 2 < 2 := Nat.mod_lt _ (by decide)
          omega
        have f : fold δY 0 (k + 1) = fold δY 2 ((k + 1) / 2) := by
          rw [fold_succ]; simp [δY, h2]
        have hp : pd (k + 1) = 1 - pd ((k + 1) / 2) := by simp [pd, h2]
        rw [f, fold_two, hp, ih ((k + 1) / 2) (by omega)]

#eval (List.range 12).map (fun n => oY (fold δY 0 n))
#eval (List.range 12).map pd
#print axioms A096268_pd

end OEIS