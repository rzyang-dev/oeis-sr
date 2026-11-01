import Mathlib

namespace OEIS

/-- Read the binary digits of n (LSB first) through a DFA. -/
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
lemma fold_last (δ₁ δ₂ : Nat → Bool → Nat) (R : List (Nat × Nat))
    (hR : ∀ p ∈ R, ∀ d : Bool, (δ₁ p.1 d, δ₂ p.2 d) ∈ R) :
    ∀ q, 1 ≤ q → ∀ s₁ s₂, (s₁, s₂) ∈ R →
      ∃ p, p ∈ R ∧ fold δ₁ s₁ q = δ₁ p.1 true ∧ fold δ₂ s₂ q = δ₂ p.2 true := by
  intro q
  induction q using Nat.strong_induction_on with
  | _ q ih =>
    intro hq s₁ s₂ hs
    cases q with
    | zero => omega
    | succ m =>
      cases m with
      | zero =>
        exact ⟨(s₁, s₂), hs, by simp [fold], by simp [fold]⟩
      | succ k =>
        have hq2 : 1 ≤ (k + 1 + 1) / 2 := by omega
        have hmem : (δ₁ s₁ ((k + 1 + 1) % 2 == 1), δ₂ s₂ ((k + 1 + 1) % 2 == 1)) ∈ R :=
          hR (s₁, s₂) hs _
        obtain ⟨p, hp, hf1, hf2⟩ := ih ((k + 1 + 1) / 2) (by omega) hq2 _ _ hmem
        refine ⟨p, hp, ?_, ?_⟩
        · rw [fold_succ, hf1]
        · rw [fold_succ, hf2]

/-- Main comparison theorem: if all pairs reachable with a final digit 1
agree on outputs, the two sequences agree for all n >= 1. -/
theorem seq_eq_of_inv
    (δ₁ δ₂ : Nat → Bool → Nat) (o₁ o₂ : Nat → Nat)
    (R R1 : List (Nat × Nat)) (s₁ s₂ : Nat)
    (hR : ∀ p ∈ R, ∀ d : Bool, (δ₁ p.1 d, δ₂ p.2 d) ∈ R)
    (hs : (s₁, s₂) ∈ R)
    (hR1 : ∀ p ∈ R, (δ₁ p.1 true, δ₂ p.2 true) ∈ R1)
    (hout : ∀ q ∈ R1, o₁ q.1 = o₂ q.2) :
    ∀ n, 1 ≤ n → o₁ (fold δ₁ s₁ n) = o₂ (fold δ₂ s₂ n) := by
  intro n hn
  cases n with
  | zero => omega
  | succ m =>
    cases m with
    | zero =>
      have h1 : fold δ₁ s₁ 1 = δ₁ s₁ true := by simp [fold]
      have h2 : fold δ₂ s₂ 1 = δ₂ s₂ true := by simp [fold]
      rw [h1, h2]
      exact hout (δ₁ s₁ true, δ₂ s₂ true) (hR1 (s₁, s₂) hs)
    | succ k =>
      have hq : 1 ≤ (k + 1 + 1) / 2 := by omega
      have hmem : (δ₁ s₁ ((k + 1 + 1) % 2 == 1), δ₂ s₂ ((k + 1 + 1) % 2 == 1)) ∈ R :=
        hR (s₁, s₂) hs _
      obtain ⟨p, hp, hf1, hf2⟩ :=
        fold_last δ₁ δ₂ R hR ((k + 1 + 1) / 2) hq _ _ hmem
      rw [fold_succ δ₁ s₁ (k + 1), fold_succ δ₂ s₂ (k + 1), hf1, hf2]
      exact hout (δ₁ p.1 true, δ₂ p.2 true) (hR1 p hp)

/-- A267442: middle column of the Rule 129 elementary cellular automaton. -/
def δA : Nat → Bool → Nat
  | 0, false => 1
  | 0, true => 2
  | 1, false => 1
  | 1, true => 1
  | 2, false => 3
  | 2, true => 2
  | 3, false => 3
  | 3, true => 1
  | _, _ => 0

def oA : Nat → Nat
  | 0 => 1
  | 1 => 1
  | 2 => 0
  | 3 => 0
  | _ => 0

/-- A043545: (maximal base-2 digit) - (minimal base-2 digit). -/
def δB : Nat → Bool → Nat
  | 0, false => 1
  | 0, true => 0
  | 1, false => 1
  | 1, true => 2
  | 2, false => 2
  | 2, true => 2
  | _, _ => 0

def oB : Nat → Nat
  | 0 => 0
  | 1 => 0
  | 2 => 1
  | _ => 0

def Rlist : List (Nat × Nat) := [(0, 0), (1, 1), (1, 2), (2, 0), (3, 1)]
def R1list : List (Nat × Nat) := [(1, 2), (2, 0)]

/-- OEIS conjecture (R. J. Mathar, 2016), proved for all n >= 1. -/
theorem A267442_eq_A043545 (n : Nat) (hn : 1 ≤ n) :
    oA (fold δA 0 n) = oB (fold δB 0 n) :=
  seq_eq_of_inv δA δB oA oB Rlist R1list 0 0
    (by decide) (by decide) (by decide) (by decide) n hn

#eval (List.range 12).map (fun n => oA (fold δA 0 n))
#eval (List.range 12).map (fun n => oB (fold δB 0 n))

#print axioms A267442_eq_A043545

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

def δS : Nat → Bool → Nat
  | 0, false => 1 | 0, true => 2
  | 1, false => 0 | 1, true => 3
  | 2, false => 2 | 2, true => 2
  | 3, false => 3 | 3, true => 3
  | _, _ => 0

def oS : Nat → Nat
  | 0 => 0 | 1 => 0 | 2 => 1 | 3 => 0 | _ => 0

def δT : Nat → Bool → Nat
  | 0, false => 1 | 0, true => 2
  | 1, false => 1 | 1, true => 1
  | 2, false => 3 | 2, true => 0
  | 3, false => 3 | 3, true => 3
  | _, _ => 0

def oT : Nat → Nat
  | 0 => 1 | 1 => 1 | 2 => 0 | 3 => 0 | _ => 0

def pairStep (p : Nat × Nat) (d : Bool) : Nat × Nat := (shiftδ δS p.1 d, δT p.2 d)

def ReachS : List (Nat × Nat) := [(1, 0), (3, 2), (4, 1), (6, 3)]

lemma reachS_start : ((1 : Nat), (0 : Nat)) ∈ ReachS := by decide
lemma reachS_closed : ∀ p ∈ ReachS, ∀ d : Bool, pairStep p d ∈ ReachS := by decide
lemma reachS_out : ∀ p ∈ ReachS, shiftOut δS oS p.1 = oT p.2 := by decide

lemma fold_pairS : ∀ n, ∀ s t, (s, t) ∈ ReachS →
    (fold (shiftδ δS) s n, fold δT t n) ∈ ReachS := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro s t hst
    cases n with
    | zero =>
      rw [fold_zero, fold_zero]
      exact hst
    | succ k =>
      rw [fold_succ, fold_succ]
      exact ih ((k + 1) / 2) (by omega) (shiftδ δS s ((k + 1) % 2 == 1)) (δT t ((k + 1) % 2 == 1))
        (reachS_closed (s, t) hst _)

/-- A285383(n) = A035263(n-1); automaton form: a(n+2) = b(n+1). -/
theorem A285383_eq_A035263 (n : Nat) :
    oS (fold δS 0 (n + 1)) = oT (fold δT 0 n) := by
  rw [← shift_correct δS oS n 0 1 (by decide)]
  have h := fold_pairS n 1 0 reachS_start
  exact reachS_out _ h

#eval (List.range 10).map (fun n => oS (fold δS 0 (n + 1)))
#eval (List.range 10).map (fun n => oT (fold δT 0 n))
#print axioms A285383_eq_A035263

/-- A284948 has the same transition table as A285383 and complementary outputs. -/
def oM (s : Nat) : Nat := 1 - oS s
/-- A096268 has the same transition table as A035263 and complementary outputs. -/
def oN (s : Nat) : Nat := 1 - oT s

/-- A284948(n) = A096268(n-2); automaton form: autM(x) = autN(x-1). -/
theorem A284948_eq_A096268 (x : Nat) (hx : 1 ≤ x) :
    oM (fold δS 0 x) = oN (fold δT 0 (x - 1)) := by
  unfold oM oN
  have h1 : oS (fold δS 0 x) = oT (fold δT 0 (x - 1)) := by
    have h2 := A285383_eq_A035263 (x - 1)
    rwa [Nat.sub_add_cancel hx] at h2
  rw [h1]

#eval (List.range 10).map (fun n => oM (fold δS 0 (n + 1)))
#eval (List.range 10).map (fun n => oN (fold δT 0 n))
#print axioms A284948_eq_A096268

end OEIS
