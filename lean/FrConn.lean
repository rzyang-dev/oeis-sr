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

def δZ : Nat → Bool → Nat
  | 0, false => 1 | 0, true => 0
  | 1, false => 1 | 1, true => 2
  | 2, false => 2 | 2, true => 2
  | _, _ => 0

def oZ : Nat → Nat
  | 0 => 1 | 1 => 0 | 2 => 0 | _ => 0

/-- Is n of the form 2^k - 1? -/
def isMersenne : Nat → Bool
  | 0 => true
  | n + 1 => if (n + 1) % 2 = 1 then isMersenne ((n + 1) / 2) else false

lemma fold2 : ∀ m, fold δZ 2 m = 2 := by
  intro m
  induction m using Nat.strong_induction_on with
  | _ m ih =>
    cases m with
    | zero => simp [fold]
    | succ k =>
      rw [fold_succ]
      have h : δZ 2 ((k + 1) % 2 == 1) = 2 := by cases ((k + 1) % 2 == 1) <;> rfl
      rw [h]
      exact ih ((k + 1) / 2) (by omega)

lemma fold1 : ∀ m, fold δZ 1 m = 1 ∨ fold δZ 1 m = 2 := by
  intro m
  induction m using Nat.strong_induction_on with
  | _ m ih =>
    cases m with
    | zero => left; simp [fold]
    | succ k =>
      rw [fold_succ]
      cases h : ((k + 1) % 2 == 1)
      · rw [show δZ 1 false = 1 from rfl]
        exact ih ((k + 1) / 2) (by omega)
      · rw [show δZ 1 true = 2 from rfl]
        right
        exact fold2 ((k + 1) / 2)

/-- A036987: characteristic function of the numbers 2^k - 1. -/
theorem A036987_fr : ∀ n, oZ (fold δZ 0 n) = (if isMersenne n then 1 else 0) := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    cases n with
    | zero => simp [fold, isMersenne, oZ]
    | succ k =>
      have hlt : (k + 1) % 2 < 2 := Nat.mod_lt _ (by decide)
      interval_cases h : (k + 1) % 2
      · have hz : isMersenne (k + 1) = false := by simp [isMersenne, h]
        have f : fold δZ 0 (k + 1) = fold δZ 1 ((k + 1) / 2) := by
          rw [fold_succ]; simp [δZ, h]
        have o1 : oZ (fold δZ 1 ((k + 1) / 2)) = 0 := by
          rcases fold1 ((k + 1) / 2) with h1 | h2
          · rw [h1]; rfl
          · rw [h2]; rfl
        rw [f, o1, hz]
        simp
      · have hz : isMersenne (k + 1) = isMersenne ((k + 1) / 2) := by simp [isMersenne, h]
        have f : fold δZ 0 (k + 1) = fold δZ 0 ((k + 1) / 2) := by
          rw [fold_succ]; simp [δZ, h]
        rw [f, hz, ih ((k + 1) / 2) (by omega)]

#eval (List.range 12).map (fun n => oZ (fold δZ 0 n))
#eval (List.range 12).map (fun n => if isMersenne n then 1 else 0)
#print axioms A036987_fr

end OEIS