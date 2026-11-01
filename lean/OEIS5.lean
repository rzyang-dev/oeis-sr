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

def δA : Nat → Bool → Nat
  | 0, false => 1 | 0, true => 2
  | 1, false => 3 | 1, true => 4
  | 2, false => 4 | 2, true => 5
  | 3, false => 1 | 3, true => 6
  | 4, false => 7 | 4, true => 6
  | 5, false => 6 | 5, true => 2
  | 6, false => 6 | 6, true => 6
  | 7, false => 4 | 7, true => 4
  | _, _ => 0

def oA : Nat → Nat
  | 0 => 0 | 1 => 0 | 2 => 1 | 3 => 0 | 4 => 1 | 5 => 0 | 6 => 0 | 7 => 1 | _ => 0

def δB : Nat → Bool → Nat
  | 0, false => 1 | 0, true => 1
  | 1, false => 0 | 1, true => 2
  | 2, false => 2 | 2, true => 2
  | _, _ => 0

def oB : Nat → Nat
  | 0 => 1 | 1 => 1 | 2 => 0 | _ => 0

def halveδ (δ : Nat → Bool → Nat) (s : Nat) (d : Bool) : Nat :=
  if s % 2 = 0 then
    (s / 4) * 4 + (if d then 1 else 0) * 2 + 1
  else
    2 * shiftδ δ ((s / 4) * 2 + (s / 2) % 2) d + 1

def halveOut (δ : Nat → Bool → Nat) (o : Nat → Nat) (s : Nat) : Nat :=
  if s % 2 = 1 then shiftOut δ o ((s / 4) * 2 + (s / 2) % 2) else o (s / 4)

lemma h2 (s : Nat) : (2 * s + 1) / 2 = s := by omega
lemma h4 (s : Nat) : (2 * s + 1) / 4 = s / 2 := by omega
lemma hm (s : Nat) : (2 * s + 1) % 2 = 1 := by omega
lemma halve_step (δ : Nat → Bool → Nat) (s : Nat) (d : Bool) :
    halveδ δ (2 * s + 1) d = 2 * shiftδ δ s d + 1 := by
  unfold halveδ
  rw [if_neg (by rw [hm]; decide), h4, h2]
  rw [show s / 2 * 2 + s % 2 = s by omega]

lemma halve_out_two (δ : Nat → Bool → Nat) (o : Nat → Nat) (s : Nat) :
    halveOut δ o (2 * s + 1) = shiftOut δ o s := by
  unfold halveOut
  rw [if_pos (hm s), h4, h2]
  rw [show s / 2 * 2 + s % 2 = s by omega]

lemma halve_shift (δ : Nat → Bool → Nat) (o : Nat → Nat) :
    ∀ n s, halveOut δ o (fold (halveδ δ) (2 * s + 1) n) = shiftOut δ o (fold (shiftδ δ) s n) := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro s
    cases n with
    | zero => rw [fold_zero, fold_zero, halve_out_two]
    | succ k =>
      rw [fold_succ, fold_succ, halve_step]
      exact ih ((k + 1) / 2) (by omega) (shiftδ δ s ((k + 1) % 2 == 1))

lemma bitval (k : Nat) : (if ((k + 1) % 2 == 1) then (1 : Nat) else 0) = (k + 1) % 2 := by
  rcases mod2_cases (k + 1) with h | h <;> rw [h] <;> simp

lemma halve_correct (δ : Nat → Bool → Nat) (o : Nat → Nat) :
    ∀ n, halveOut δ o (fold (halveδ δ) 0 n) = o (fold δ 0 ((n + 1) / 2)) := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    cases n with
    | zero => simp [fold, halveOut]
    | succ k =>
      rw [fold_succ]
      have h0 : halveδ δ 0 ((k + 1) % 2 == 1) = 2 * ((k + 1) % 2) + 1 := by
        unfold halveδ
        rw [if_pos (by omega : (0 : Nat) % 2 = 0)]
        simp only [Nat.zero_div, Nat.zero_mul, Nat.zero_add]
        rw [bitval]
        omega
      rw [h0, halve_shift]
      have hsc := shift_correct δ o ((k + 1) / 2) 0 ((k + 1) % 2) (by omega)
      simp only [enc2, Nat.zero_mul, Nat.zero_add] at hsc
      rw [hsc]
      rw [show (k + 1) / 2 + (k + 1) % 2 = (k + 1 + 1) / 2 by omega]

def RR : List (Nat × Nat) :=
  [(0, 0), (1, 1), (2, 3), (3, 5), (4, 5), (5, 7), (6, 9), (7, 1)]

lemma RR_start : ((0 : Nat), (0 : Nat)) ∈ RR := by decide
lemma RR_closed : ∀ p ∈ RR, ∀ d : Bool, (δA p.1 d, halveδ δB p.2 d) ∈ RR := by decide
lemma RR_agree : ∀ p ∈ RR, oA (δA p.1 true) = halveOut δB oB (halveδ δB p.2 true) := by decide

lemma fold_last_digit : ∀ n, 1 ≤ n → ∀ a h, (a, h) ∈ RR →
    ∃ q, q ∈ RR ∧ fold δA a n = δA q.1 true ∧ fold (halveδ δB) h n = halveδ δB q.2 true := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro hn a h hah
    cases n with
    | zero => omega
    | succ m =>
      cases m with
      | zero =>
        refine ⟨(a, h), hah, ?_, ?_⟩
        · rw [fold_succ]; simp [fold]
        · rw [fold_succ]; simp [fold]
      | succ k =>
        have hq : 1 ≤ (k + 1 + 1) / 2 := by omega
        rw [fold_succ, fold_succ]
        exact ih ((k + 1 + 1) / 2) (by omega) hq _ _ (RR_closed (a, h) hah _)

/-- A270803(n) = A151666(floor((n+1)/2)) for n >= 1. -/
theorem A270803_eq_A151666 (n : Nat) (hn : 1 ≤ n) :
    oA (fold δA 0 n) = oB (fold δB 0 ((n + 1) / 2)) := by
  obtain ⟨q, hq, h1, h2⟩ := fold_last_digit n hn 0 0 RR_start
  have h3 := halve_correct δB oB n
  rw [h1, ← h3, h2]
  exact RR_agree q hq

#eval (List.range 10).map (fun n => oA (fold δA 0 (n + 1)))
#eval (List.range 10).map (fun n => oB (fold δB 0 ((n + 2) / 2)))
#print axioms A270803_eq_A151666

end OEIS