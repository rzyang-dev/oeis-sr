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

def enc2 (b c : Nat) : Nat := b * 2 + c

def shiftδ (δ : Nat → Bool → Nat) (s : Nat) (d : Bool) : Nat :=
  let c := s % 2
  let t := (if d then 1 else 0) + c
  enc2 (δ (s / 2) (t % 2 == 1)) (t / 2)

def shiftOut (δ : Nat → Bool → Nat) (o : Nat → Nat) (s : Nat) : Nat :=
  if s % 2 = 1 then o (δ (s / 2) true) else o (s / 2)

lemma fold_zero (δ : Nat → Bool → Nat) (s : Nat) : fold δ s 0 = s := by simp [fold]

lemma fold_one (δ : Nat → Bool → Nat) (s : Nat) : fold δ s 1 = δ s true := by
  rw [fold_succ]; simp [fold]

lemma mod2_cases (n : Nat) : n % 2 = 0 ∨ n % 2 = 1 := by omega

lemma carry_bd (k c : Nat) (hc : c ≤ 1) : ((k + 1) % 2 + c) / 2 ≤ 1 := by
  rcases mod2_cases (k + 1) with h | h <;> rw [h] <;> omega

lemma carry_mod (k c : Nat) : ((k + 1) % 2 + c) % 2 = (k + c + 1) % 2 := by
  rcases mod2_cases (k + 1) with h | h <;> rw [h] <;> omega

lemma carry_div (k c : Nat) : (k + 1) / 2 + ((k + 1) % 2 + c) / 2 = (k + c + 1) / 2 := by
  rcases mod2_cases (k + 1) with h | h <;> rw [h] <;> omega

lemma bit_eq (k : Nat) : (if ((k + 1) % 2 == 1) then (1 : Nat) else 0) = (k + 1) % 2 := by
  rcases mod2_cases (k + 1) with h | h <;> rw [h] <;> simp

lemma shift_correct (δ : Nat → Bool → Nat) (o : Nat → Nat) :
    ∀ n b c, c ≤ 1 → shiftOut δ o (fold (shiftδ δ) (enc2 b c) n) = o (fold δ b (n + c)) := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro b c hc
    cases n with
    | zero =>
      rw [fold_zero]
      interval_cases c
      · have h1 : (enc2 b 0) % 2 = 0 := by unfold enc2; omega
        have h2 : (enc2 b 0) / 2 = b := by unfold enc2; omega
        simp [shiftOut, h1, h2, fold_zero]
      · have h1 : (enc2 b 1) % 2 = 1 := by unfold enc2; omega
        have h2 : (enc2 b 1) / 2 = b := by unfold enc2; omega
        rw [shiftOut, if_pos h1, h2]
        rw [show (0 : Nat) + 1 = (0 + 1) by rfl, fold_one]
    | succ k =>
      have hsc : (enc2 b c) % 2 = c := by unfold enc2; omega
      have hsd : (enc2 b c) / 2 = b := by unfold enc2; omega
      have hstep : fold (shiftδ δ) (enc2 b c) (k + 1) =
          fold (shiftδ δ) (enc2 (δ b (((k + 1) % 2 + c) % 2 == 1)) (((k + 1) % 2 + c) / 2))
            ((k + 1) / 2) := by
        rw [fold_succ]
        congr 1
        simp only [shiftδ]
        rw [hsc, hsd, bit_eq]
      rw [hstep]
      rw [ih ((k + 1) / 2) (by omega) (δ b (((k + 1) % 2 + c) % 2 == 1))
            (((k + 1) % 2 + c) / 2) (carry_bd k c hc)]
      congr 1
      rw [show k + 1 + c = (k + c) + 1 by omega, fold_succ]
      rw [carry_mod, carry_div]

def δU : Nat → Bool → Nat
  | 0, false => 1 | 0, true => 2
  | 1, false => 3 | 1, true => 4
  | 2, false => 5 | 2, true => 6
  | 3, false => 7 | 3, true => 7
  | 4, false => 8 | 4, true => 6
  | 5, false => 5 | 5, true => 9
  | 6, false => 6 | 6, true => 9
  | 7, false => 7 | 7, true => 10
  | 8, false => 4 | 8, true => 7
  | 9, false => 9 | 9, true => 9
  | 10, false => 10 | 10, true => 10
  | _, _ => 0

def oU : Nat → Nat
  | 0 => 1 | 1 => 1 | 2 => 2 | 3 => 1 | 4 => 3 | 5 => 2
  | 6 => 0 | 7 => 1 | 8 => 3 | 9 => 1 | 10 => 0 | _ => 0

def δV : Nat → Bool → Nat
  | 0, false => 1 | 0, true => 2
  | 1, false => 3 | 1, true => 4
  | 2, false => 2 | 2, true => 2
  | 3, false => 3 | 3, true => 5
  | 4, false => 6 | 4, true => 1
  | 5, false => 5 | 5, true => 5
  | 6, false => 6 | 6, true => 2
  | _, _ => 0

def oV : Nat → Nat
  | 0 => 1 | 1 => 1 | 2 => 1 | 3 => 1 | 4 => 0 | 5 => 0 | 6 => 0 | _ => 0

def δU1 : Nat → Bool → Nat := shiftδ δU
def u1 : Nat → Nat := shiftOut δU oU
def δU2 : Nat → Bool → Nat := shiftδ δU1
def u2 : Nat → Nat := shiftOut δU1 u1
def δU3 : Nat → Bool → Nat := shiftδ δU2
def u3 : Nat → Nat := shiftOut δU2 u2
def δU4 : Nat → Bool → Nat := shiftδ δU3
def u4 : Nat → Nat := shiftOut δU3 u3

lemma shift4_U (n : Nat) : u4 (fold δU4 15 n) = oU (fold δU 0 (n + 4)) := by
  have h4 : u4 (fold δU4 15 n) = u3 (fold δU3 7 (n + 1)) :=
    shift_correct δU3 u3 n 7 1 (by decide)
  have h3 : u3 (fold δU3 7 (n + 1)) = u2 (fold δU2 3 (n + 1 + 1)) :=
    shift_correct δU2 u2 (n + 1) 3 1 (by decide)
  have h2 : u2 (fold δU2 3 (n + 1 + 1)) = u1 (fold δU1 1 (n + 1 + 1 + 1)) :=
    shift_correct δU1 u1 (n + 1 + 1) 1 1 (by decide)
  have h1 : u1 (fold δU1 1 (n + 1 + 1 + 1)) = oU (fold δU 0 (n + 1 + 1 + 1 + 1)) :=
    shift_correct δU oU (n + 1 + 1 + 1) 0 1 (by decide)
  rw [h4, h3, h2, h1]

def Reach4 : List (Nat × Nat) :=
  [(15, 0), (26, 1), (37, 2), (56, 3), (66, 4), (84, 2), (96, 6), (97, 2),
   (112, 3), (120, 5), (130, 1), (144, 2), (160, 5)]

lemma reach4_start : ((15 : Nat), (0 : Nat)) ∈ Reach4 := by decide
lemma reach4_closed : ∀ p ∈ Reach4, ∀ d : Bool, (δU4 p.1 d, δV p.2 d) ∈ Reach4 := by decide
lemma reach4_out : ∀ p ∈ Reach4, u4 p.1 = oV p.2 := by decide

lemma fold_pair4 : ∀ n, ∀ s t, (s, t) ∈ Reach4 →
    (fold δU4 s n, fold δV t n) ∈ Reach4 := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro s t hst
    cases n with
    | zero => rw [fold_zero, fold_zero]; exact hst
    | succ k =>
      rw [fold_succ, fold_succ]
      exact ih ((k + 1) / 2) (by omega) (δU4 s ((k + 1) % 2 == 1)) (δV t ((k + 1) % 2 == 1))
        (reach4_closed (s, t) hst _)

/-- A306559(n+5) = A039982(n), automaton form (A306559 has shift 1). -/
theorem A306559_eq_A039982 (n : Nat) :
    oU (fold δU 0 (n + 4)) = oV (fold δV 0 n) := by
  rw [← shift4_U n]
  have h := fold_pair4 n 15 0 reach4_start
  exact reach4_out _ h

#eval (List.range 10).map (fun n => oU (fold δU 0 (n + 4)))
#eval (List.range 10).map (fun n => oV (fold δV 0 n))
#print axioms A306559_eq_A039982

end OEIS
