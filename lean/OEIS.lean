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

end OEIS