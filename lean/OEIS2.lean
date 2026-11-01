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

def δX : Nat → Bool → Nat
  | 0, false => 1 | 0, true => 2
  | 1, false => 1 | 1, true => 3
  | 2, false => 4 | 2, true => 0
  | 3, false => 3 | 3, true => 3
  | 4, false => 4 | 4, true => 5
  | 5, false => 5 | 5, true => 5
  | _, _ => 0

def oX : Nat → Nat
  | 0 => 1 | 1 => 1 | 2 => 0 | 3 => 0 | 4 => 0 | 5 => 1 | _ => 0

def δY : Nat → Bool → Nat
  | 0, false => 1 | 0, true => 2
  | 1, false => 1 | 1, true => 1
  | 2, false => 3 | 2, true => 0
  | 3, false => 3 | 3, true => 3
  | _, _ => 0

def oY : Nat → Nat
  | 0 => 0 | 1 => 0 | 2 => 1 | 3 => 1 | _ => 0

def δZ : Nat → Bool → Nat
  | 0, false => 1 | 0, true => 0
  | 1, false => 1 | 1, true => 2
  | 2, false => 2 | 2, true => 2
  | _, _ => 0

def oZ : Nat → Nat
  | 0 => 1 | 1 => 1 | 2 => 0 | _ => 0

def pairIdx : Nat → Nat → Nat
  | 0, 0 => 0
  | 1, 1 => 1
  | 2, 0 => 2
  | 1, 2 => 3
  | 3, 1 => 4
  | 3, 2 => 5
  | _, _ => 0

def fstOf : Nat → Nat
  | 0 => 0 | 1 => 1 | 2 => 2 | 3 => 1 | 4 => 3 | 5 => 3 | _ => 0

def sndOf : Nat → Nat
  | 0 => 0 | 1 => 1 | 2 => 0 | 3 => 2 | 4 => 1 | 5 => 2 | _ => 0

def δP (s : Nat) (d : Bool) : Nat := pairIdx (δY (fstOf s) d) (δZ (sndOf s) d)

def xorOut (s : Nat) : Nat :=
  if (oY (fstOf s) == 1) != (oZ (sndOf s) == 1) then 1 else 0

def Reach : List (Nat × Nat) := [(0, 0), (1, 1), (2, 0), (1, 2), (3, 1), (3, 2)]

lemma δP_eq_δX : ∀ s < 6, ∀ d : Bool, δP s d = δX s d := by decide
lemma oX_eq_xor : ∀ s < 6, oX s = xorOut s := by decide
lemma δX_lt : ∀ s < 6, ∀ d : Bool, δX s d < 6 := by decide
lemma pairIdx_lt : ∀ y z, pairIdx y z < 6 := by
  intro y z
  unfold pairIdx
  split <;> omega
lemma fst_pair : ∀ p ∈ Reach, fstOf (pairIdx p.1 p.2) = p.1 := by decide
lemma snd_pair : ∀ p ∈ Reach, sndOf (pairIdx p.1 p.2) = p.2 := by decide
lemma reach_closed : ∀ p ∈ Reach, ∀ d : Bool, (δY p.1 d, δZ p.2 d) ∈ Reach := by decide

lemma foldX_eq_foldP : ∀ n, ∀ s, s < 6 → fold δX s n = fold δP s n := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro s hs
    cases n with
    | zero => simp [fold]
    | succ k =>
      rw [fold_succ, fold_succ]
      have hb : δX s ((k + 1) % 2 == 1) = δP s ((k + 1) % 2 == 1) := (δP_eq_δX s hs _).symm
      rw [hb]
      exact ih ((k + 1) / 2) (by omega) (δP s ((k + 1) % 2 == 1)) (by rw [← hb]; exact δX_lt s hs _)

lemma fold_prod : ∀ n, ∀ y z, (y, z) ∈ Reach →
    fold δP (pairIdx y z) n = pairIdx (fold δY y n) (fold δZ z n) := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro y z hp
    cases n with
    | zero => simp [fold]
    | succ k =>
      rw [fold_succ]
      have hstep : δP (pairIdx y z) ((k + 1) % 2 == 1) =
          pairIdx (δY y ((k + 1) % 2 == 1)) (δZ z ((k + 1) % 2 == 1)) := by
        unfold δP
        rw [fst_pair (y, z) hp, snd_pair (y, z) hp]
      rw [hstep]
      have hh := ih ((k + 1) / 2) (by omega) (δY y ((k + 1) % 2 == 1))
          (δZ z ((k + 1) % 2 == 1)) (reach_closed (y, z) hp _)
      simpa [fold_succ] using hh

lemma fold_pair_in_reach : ∀ n, ∀ y z, (y, z) ∈ Reach →
    (fold δY y n, fold δZ z n) ∈ Reach := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro y z hp
    cases n with
    | zero => simpa [fold] using hp
    | succ k =>
      rw [fold_succ, fold_succ]
      exact ih ((k + 1) / 2) (by omega) (δY y ((k + 1) % 2 == 1)) (δZ z ((k + 1) % 2 == 1))
        (reach_closed (y, z) hp _)

/-- The OEIS conjecture A217586(n) = A096268(n-1) XOR A036987(n-1), automaton form. -/
theorem A217586_xor (n : Nat) :
    oX (fold δX 0 n) =
      (if (oY (fold δY 0 n) == 1) != (oZ (fold δZ 0 n) == 1) then 1 else 0) := by
  have h1 : fold δX 0 n = fold δP 0 n := foldX_eq_foldP n 0 (by decide)
  rw [h1]
  have h2 : fold δP (pairIdx 0 0) n = pairIdx (fold δY 0 n) (fold δZ 0 n) :=
    fold_prod n 0 0 (by decide)
  have h3 : pairIdx 0 0 = 0 := rfl
  rw [h3] at h2
  rw [h2]
  have hlt : pairIdx (fold δY 0 n) (fold δZ 0 n) < 6 := pairIdx_lt _ _
  rw [oX_eq_xor _ hlt]
  unfold xorOut
  have hp : (fold δY 0 n, fold δZ 0 n) ∈ Reach := fold_pair_in_reach n 0 0 (by decide)
  rw [fst_pair _ hp, snd_pair _ hp]

#print axioms A217586_xor

end OEIS