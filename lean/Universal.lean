/-
Rule 129 of the elementary cellular automata.

The automaton is the map on configurations  x : Int -> {0,1}  given by

    x(t+1, j) = 1  <=>  x(t, j-1) = x(t, j) = x(t, j+1)

("all three neighbours are equal"), started from the single 1 configuration
x(0,j) = 1 <=> j = 0.

Write  r t  for the number obtained from t by deleting its leading binary digit
(so r 0 = r 1 = 0), and  sub m s  for "m is a submask of s", i.e. m &&& s = m.

Main results proved below (no sorry; the only axioms used are
propext, Classical.choice and Quot.sound):

* row_eq_F        : x(t,j) = F(t,j) for all t >= 1, where F is the closed form;
* row_closed_form : x(t,j) = 0  <=>  |j| <= t and sub (floor((t-|j|)/2)) (r t);
* F_step          : F(t+1,j) = 1 <=> F(t,j-1) = F(t,j) = F(t,j+1)
                    (the closed form satisfies the CA recursion);
* row_middle      : x(t,0) = 0  <=>  exists k >= 1, t = 2^k - 1.

Proof outline.
1. sub is characterised by test bits; this yields
     sub e (2u+1) <=> sub (e/2) u,    sub e (2u) <=> e even and sub (e/2) u.
2. Strong induction on s yields the key identity
     sub e (s+1) <=> not (sub e s <=> sub (e-1) s)      (e >= 1),
   which is exactly where the carry in s+1 is absorbed.
3. r is defined by r 0 = r 1 = 0 and r (n+2) = 2 * r ((n+2)/2) + (n+2) % 2, and it
   is proved that r t = s whenever t = 2^K + s with s < 2^K.
4. Combining 2 and 3 gives the local identity H_step for the closed form (the
   three depths d, d-1, d-2 of the two neighbouring cells); the middle cell
   j = 0 is the only case needing separate treatment, boundary cases are easy.
5. Induction on t upgrades H_step to x(t,.) = F(t,.).
6. Middle column: x(t,0) = 0 <=> sub (t/2) (r t); writing t = 2^K + s with
   s < 2^K, sub (t/2) s forces 2^(K-1) + s/2 <= s, hence s >= 2^K - 1.
-/

import Mathlib

namespace OEIS
namespace Rule129

/-! ### Submasks -/

/-- sub m s : every bit set in m is set in s. -/
def sub (m s : Nat) : Prop := m &&& s = m

instance subDecidable (m s : Nat) : Decidable (sub m s) := by unfold sub; infer_instance

theorem bool_and_eq_left {a b : Bool} (h : a = true → b = true) : (a && b) = a := by
  cases a <;> cases b <;> simp_all

theorem sub_iff_testBit {m s : Nat} :
    sub m s ↔ ∀ i, m.testBit i = true → s.testBit i = true := by
  unfold sub
  rw [Nat.eq_iff_testBit_eq]
  constructor
  · rintro h i hi
    have h' := h i
    rw [Nat.testBit_and] at h'
    rw [hi] at h'
    simpa using h'
  · intro h i
    rw [Nat.testBit_and]
    exact bool_and_eq_left (h i)

theorem sub_le {m s : Nat} (h : sub m s) : m ≤ s := by
  unfold sub at h
  calc m = m &&& s := h.symm
    _ ≤ s := Nat.and_le_right

theorem sub_zero (s : Nat) : sub 0 s := by unfold sub; simp

theorem sub_self (m : Nat) : sub m m := by unfold sub; simp

theorem sub_trans {a b c : Nat} (hab : sub a b) (hbc : sub b c) : sub a c := by
  rw [sub_iff_testBit] at *
  intro i hi
  exact hbc i (hab i hi)

theorem sub_bot {m : Nat} : sub m 0 ↔ m = 0 := by
  unfold sub
  constructor
  · intro h; rw [← h]; simp
  · intro h; subst h; simp

theorem sub_of_lt_two_pow {m n : Nat} (h : m < 2 ^ n) : sub m (2 ^ n - 1) := by
  unfold sub
  exact Nat.and_two_pow_sub_one_of_lt_two_pow h

/-! ### Bit lemmas for doubling -/

theorem testBit_two_mul_succ (u i : Nat) : (2 * u).testBit (i + 1) = u.testBit i := by
  rw [Nat.testBit_succ, show (2 * u) / 2 = u by omega]

theorem testBit_two_mul_zero (u : Nat) : (2 * u).testBit 0 = false := by
  rw [← Nat.mod_two_eq_zero_iff_testBit_zero]; omega

theorem testBit_two_mul_add_one_succ (u i : Nat) :
    (2 * u + 1).testBit (i + 1) = u.testBit i := by
  rw [Nat.testBit_succ, show (2 * u + 1) / 2 = u by omega]

theorem testBit_two_mul_add_one_zero (u : Nat) : (2 * u + 1).testBit 0 = true := by
  rw [← Nat.mod_two_eq_one_iff_testBit_zero]; omega

theorem sub_two_mul_add_one {e u : Nat} : sub e (2 * u + 1) ↔ sub (e / 2) u := by
  rw [sub_iff_testBit, sub_iff_testBit]
  constructor
  · intro h j hj
    have h1 : e.testBit (j + 1) = true := by
      rw [Nat.testBit_succ]; exact hj
    have h2 := h (j + 1) h1
    rwa [testBit_two_mul_add_one_succ] at h2
  · intro h i hi
    cases i with
    | zero => rw [testBit_two_mul_add_one_zero]
    | succ j =>
      have h1 : (e / 2).testBit j = true := by
        rw [← Nat.testBit_succ]; exact hi
      have h2 := h j h1
      rwa [testBit_two_mul_add_one_succ]

theorem sub_two_mul {e u : Nat} : sub e (2 * u) ↔ (e % 2 = 0 ∧ sub (e / 2) u) := by
  rw [sub_iff_testBit, sub_iff_testBit]
  constructor
  · intro h
    refine ⟨?_, ?_⟩
    · rw [Nat.mod_two_eq_zero_iff_testBit_zero]
      cases hv : e.testBit 0
      · rfl
      · have hh := h 0 hv
        rw [testBit_two_mul_zero] at hh
        simp at hh
    · intro j hj
      have h1 : e.testBit (j + 1) = true := by
        rw [Nat.testBit_succ]; exact hj
      have h2 := h (j + 1) h1
      rwa [testBit_two_mul_succ] at h2
  · rintro ⟨he, h⟩ i hi
    cases i with
    | zero =>
      have h0 : e.testBit 0 = false := by
        rw [← Nat.mod_two_eq_zero_iff_testBit_zero]; exact he
      rw [h0] at hi
      simp at hi
    | succ j =>
      have h1 : (e / 2).testBit j = true := by
        rw [← Nat.testBit_succ]; exact hi
      have h2 := h j h1
      rwa [testBit_two_mul_succ]

/-! ### The parity dichotomy -/

theorem two_mul_or_two_mul_add_one (d : Nat) : ∃ e, d = 2 * e ∨ d = 2 * e + 1 := by
  have hdm : 2 * (d / 2) + d % 2 = d := Nat.div_add_mod d 2
  rcases Nat.mod_two_eq_zero_or_one d with h | h
  · exact ⟨d / 2, Or.inl (by omega)⟩
  · exact ⟨d / 2, Or.inr (by omega)⟩

/-! ### r : the number with the leading binary digit removed -/

def r (t : Nat) : Nat :=
  match t with
  | 0 => 0
  | 1 => 0
  | n + 2 => 2 * r ((n + 2) / 2) + (n + 2) % 2
termination_by t
decreasing_by omega

theorem r_zero : r 0 = 0 := by rw [r]

theorem r_one : r 1 = 0 := by rw [r]

theorem r_add_two (n : Nat) : r (n + 2) = 2 * r ((n + 2) / 2) + (n + 2) % 2 := by rw [r]

theorem exists_pow_add : ∀ t : Nat, 1 ≤ t → ∃ K s, t = 2 ^ K + s ∧ s < 2 ^ K := by
  intro t
  induction t using Nat.strongRecOn with
  | _ t ih =>
    intro ht
    match t with
    | 0 => omega
    | 1 => exact ⟨0, 0, by simp, by simp⟩
    | k + 2 =>
      have h1 : 1 ≤ (k + 2) / 2 := by omega
      have h2 : (k + 2) / 2 < k + 2 := by omega
      obtain ⟨K, s, hs, hlt⟩ := ih ((k + 2) / 2) h2 h1
      have hdm : 2 * ((k + 2) / 2) + (k + 2) % 2 = k + 2 := Nat.div_add_mod (k + 2) 2
      refine ⟨K + 1, 2 * s + (k + 2) % 2, ?_, ?_⟩
      · rw [Nat.pow_succ']; omega
      · rw [Nat.pow_succ']; omega

theorem r_eq_of : ∀ (t K s : Nat), 1 ≤ t → t = 2 ^ K + s → s < 2 ^ K → r t = s := by
  intro t
  induction t using Nat.strongRecOn with
  | _ t ih =>
    intro K s ht h hs
    match t with
    | 0 => omega
    | 1 =>
      have hs0 : s = 0 := by
        rcases Nat.eq_zero_or_pos K with hK | hK
        · subst hK; simp at h; omega
        · have h2 : 2 ≤ 2 ^ K := by
            have h3 : 2 ^ 1 ≤ 2 ^ K := Nat.pow_le_pow_right (by omega) hK
            simpa using h3
          omega
      subst hs0
      rw [r_one]
    | k + 2 =>
      have hK : 1 ≤ K := by
        rcases Nat.eq_zero_or_pos K with h0 | h0
        · subst h0; simp at h; omega
        · exact h0
      obtain ⟨K', rfl⟩ : ∃ K', K = K' + 1 := ⟨K - 1, by omega⟩
      have h2 : (k + 2) / 2 = 2 ^ K' + s / 2 := by
        rw [h, Nat.pow_succ']; omega
      have h3 : s / 2 < 2 ^ K' := by
        rw [Nat.pow_succ'] at hs; omega
      have h4 : 1 ≤ (k + 2) / 2 := by omega
      have h5 : (k + 2) / 2 < k + 2 := by omega
      have h6 : r ((k + 2) / 2) = s / 2 := ih ((k + 2) / 2) h5 K' (s / 2) h4 h2 h3
      have h7 : (k + 2) % 2 = s % 2 := by
        rw [Nat.pow_succ'] at h; omega
      rw [r_add_two, h6, h7]
      omega


/-! ### The closed form: depth values -/

/-- bit p is 1 when p holds and 0 otherwise. -/
def bit (p : Prop) [Decidable p] : Nat := if p then 1 else 0

theorem bit_one_iff {p : Prop} [Decidable p] : bit p = 1 ↔ p := by
  unfold bit; by_cases h : p <;> simp [h]

theorem bit_zero_iff {p : Prop} [Decidable p] : bit p = 0 ↔ ¬ p := by
  unfold bit; by_cases h : p <;> simp [h]

/-- G t d : the value of the configuration at depth d in row t. -/
def G (t d : Nat) : Nat := 1 - bit (sub (d / 2) (r t))

theorem G_val (t d : Nat) : G t d = if sub (d / 2) (r t) then 0 else 1 := by
  unfold G bit
  by_cases h : sub (d / 2) (r t) <;> simp [h]

theorem G_one_iff (t d : Nat) : G t d = 1 ↔ ¬ sub (d / 2) (r t) := by
  rw [G_val]; by_cases h : sub (d / 2) (r t) <;> simp [h]

theorem G_zero_iff (t d : Nat) : G t d = 0 ↔ sub (d / 2) (r t) := by
  rw [G_val]; by_cases h : sub (d / 2) (r t) <;> simp [h]

theorem G_eq_G_iff (t a b : Nat) :
    G t a = G t b ↔ (sub (a / 2) (r t) ↔ sub (b / 2) (r t)) := by
  rw [G_val, G_val]
  by_cases h1 : sub (a / 2) (r t) <;> by_cases h2 : sub (b / 2) (r t) <;> simp [h1, h2]

theorem G_zero_depth (t : Nat) : G t 0 = 0 := by
  rw [G_zero_iff]; exact sub_zero _

/-- H t n : the value at (signed) distance n from the centre in row t. -/
def H (t n : Nat) : Nat := if n ≤ t then G t (t - n) else 1

theorem H_of_le {t n : Nat} (h : n ≤ t) : H t n = G t (t - n) := by
  unfold H; rw [if_pos h]

theorem H_of_gt {t n : Nat} (h : t < n) : H t n = 1 := by
  unfold H; rw [if_neg (by omega)]

theorem H_one_iff (t n : Nat) (h : n ≤ t) :
    H t n = 1 ↔ ¬ sub ((t - n) / 2) (r t) := by
  rw [H_of_le h, G_one_iff]

theorem H_eq_H_iff (t a b : Nat) (ha : a ≤ t) (hb : b ≤ t) :
    H t a = H t b ↔ (sub ((t - a) / 2) (r t) ↔ sub ((t - b) / 2) (r t)) := by
  rw [H_of_le ha, H_of_le hb, G_eq_G_iff]

/-- F t j : the closed form for row t at (integer) position j. -/
def F (t : Nat) (j : Int) : Nat := H t j.natAbs

theorem F_neg (t : Nat) (j : Int) : F t (-j) = F t j := by
  unfold F; rw [Int.natAbs_neg]

/-! ### The key submask identity -/

theorem sub_succ_xor : ∀ (s e : Nat), 1 ≤ e →
    (sub e (s + 1) ↔ ¬ (sub e s ↔ sub (e - 1) s)) := by
  intro s
  induction s using Nat.strongRecOn with
  | ind s ih =>
    intro e he
    have hdm : 2 * (e / 2) + e % 2 = e := Nat.div_add_mod e 2
    obtain ⟨u, hu | hu⟩ := two_mul_or_two_mul_add_one s
    · subst hu
      have h1 : sub e (2 * u + 1) ↔ sub (e / 2) u := sub_two_mul_add_one
      have h2 : sub e (2 * u) ↔ (e % 2 = 0 ∧ sub (e / 2) u) := sub_two_mul
      have h3 : sub (e - 1) (2 * u) ↔ ((e - 1) % 2 = 0 ∧ sub ((e - 1) / 2) u) :=
        sub_two_mul
      rcases Nat.mod_two_eq_zero_or_one e with hpar | hpar
      · obtain ⟨f, rfl⟩ : ∃ f, e = 2 * f := ⟨e / 2, by omega⟩
        have hm0 : (2 * f) % 2 = 0 := by omega
        have hm1 : (2 * f - 1) % 2 = 1 := by omega
        have hd1 : (2 * f - 1) / 2 = f - 1 := by omega
        have hd0 : (2 * f) / 2 = f := by omega
        rw [h1, h2, h3, hm0, hm1, hd1, hd0]
        by_cases hP : sub f u <;> simp [hP]
      · obtain ⟨f, rfl⟩ : ∃ f, e = 2 * f + 1 := ⟨e / 2, by omega⟩
        have hm0 : (2 * f + 1) % 2 = 1 := by omega
        have hm1 : (2 * f + 1 - 1) % 2 = 0 := by omega
        have hd1 : (2 * f + 1 - 1) / 2 = f := by omega
        have hd0 : (2 * f + 1) / 2 = f := by omega
        rw [h1, h2, h3, hm0, hm1, hd1, hd0]
        by_cases hP : sub f u <;> simp [hP]
    · subst hu
      have h1 : sub e (2 * u + 1 + 1) ↔ (e % 2 = 0 ∧ sub (e / 2) (u + 1)) := by
        have h := sub_two_mul (e := e) (u := u + 1)
        rwa [show 2 * (u + 1) = 2 * u + 1 + 1 by omega] at h
      have h2 : sub e (2 * u + 1) ↔ sub (e / 2) u := sub_two_mul_add_one
      have h3 : sub (e - 1) (2 * u + 1) ↔ sub ((e - 1) / 2) u := sub_two_mul_add_one
      rcases Nat.mod_two_eq_zero_or_one e with hpar | hpar
      · obtain ⟨f, rfl⟩ : ∃ f, e = 2 * f := ⟨e / 2, by omega⟩
        have hf : 1 ≤ f := by omega
        have hm0 : (2 * f) % 2 = 0 := by omega
        have hd0 : (2 * f) / 2 = f := by omega
        have hd1 : (2 * f - 1) / 2 = f - 1 := by omega
        rw [h1, h2, h3, hm0, hd0, hd1]
        simpa using ih u (by omega) f hf
      · obtain ⟨f, rfl⟩ : ∃ f, e = 2 * f + 1 := ⟨e / 2, by omega⟩
        have hm0 : (2 * f + 1) % 2 = 1 := by omega
        have hd0 : (2 * f + 1) / 2 = f := by omega
        have hd1 : (2 * f + 1 - 1) / 2 = f := by omega
        rw [h1, h2, h3, hm0, hd0, hd1]
        by_cases hP : sub f u <;> simp [hP]

theorem not_sub_succ {e s : Nat} (he : 1 ≤ e) :
    (¬ sub e (s + 1) ↔ (sub e s ↔ sub (e - 1) s)) := by
  have h := sub_succ_xor s e he
  by_cases hC : (sub e s ↔ sub (e - 1) s)
  · have h1 : ¬ sub e (s + 1) := fun hh => h.mp hh hC
    simp [hC, h1]
  · have h1 : sub e (s + 1) := h.mpr hC
    simp [hC, h1]


/-! ### The local identity for the closed form -/

theorem H_step (t : Nat) (ht : 1 ≤ t) (n : Nat) :
    H (t + 1) n = 1 ↔ H t (n - 1) = H t n ∧ H t n = H t (n + 1) := by
  obtain ⟨K, s, hK, hsK⟩ := exists_pow_add t ht
  have hrt : r t = s := r_eq_of t K s ht hK hsK
  have hs1 : s + 1 ≤ 2 ^ K := by omega
  rcases n with _ | m
  · -- n = 0
    have hL : H (t + 1) 0 = 1 ↔ ¬ sub ((t + 1) / 2) (r (t + 1)) := by
      have h := H_one_iff (t + 1) 0 (by omega)
      simpa using h
    have heq : (H t 0 = H t 1) ↔ (sub (t / 2) s ↔ sub ((t - 1) / 2) s) := by
      have h := H_eq_H_iff t 0 1 (by omega) ht
      rw [hrt] at h
      simpa using h
    have hgoal : (H (t + 1) 0 = 1 ↔ H t (0 - 1) = H t 0 ∧ H t 0 = H t (0 + 1))
        ↔ (H (t + 1) 0 = 1 ↔ H t 0 = H t 1) := by simp
    rw [hgoal, hL, heq]
    obtain ⟨u, hu | hu⟩ := two_mul_or_two_mul_add_one t
    · subst hu
      have hu1 : 1 ≤ u := by omega
      have hh1 : (2 * u + 1) / 2 = u := by omega
      have hh2 : (2 * u) / 2 = u := by omega
      have hh3 : (2 * u - 1) / 2 = u - 1 := by omega
      rw [hh1, hh2, hh3]
      rcases Nat.lt_or_eq_of_le hs1 with hcarry | hcarry
      · have hr1 : r (2 * u + 1) = s + 1 :=
          r_eq_of (2 * u + 1) K (s + 1) (by omega) (by omega) hcarry
        rw [hr1]
        exact not_sub_succ hu1
      · exfalso
        omega
    · subst hu
      have hh1 : (2 * u + 1 + 1) / 2 = u + 1 := by omega
      have hh2 : (2 * u + 1) / 2 = u := by omega
      have hh3 : (2 * u + 1 - 1) / 2 = u := by omega
      rw [hh1, hh2, hh3]
      rw [show ((¬ sub (u + 1) (r (2 * u + 1 + 1)) ↔ (sub u s ↔ sub u s))
            ↔ ¬ sub (u + 1) (r (2 * u + 1 + 1))) from
        ⟨fun h => h.mpr Iff.rfl, fun h => ⟨fun _ => Iff.rfl, fun _ => h⟩⟩]
      rcases Nat.lt_or_eq_of_le hs1 with hcarry | hcarry
      · have hr1 : r (2 * u + 1 + 1) = s + 1 :=
          r_eq_of (2 * u + 1 + 1) K (s + 1) (by omega) (by omega) hcarry
        rw [hr1]
        intro hcon
        have hle := sub_le hcon
        have hsS : s + 1 = 2 * u + 2 - 2 ^ K := by omega
        omega
      · have hr0 : r (2 * u + 1 + 1) = 0 := by
          apply r_eq_of (2 * u + 1 + 1) (K + 1) 0 (by omega)
          · rw [Nat.pow_succ']; omega
          · exact Nat.two_pow_pos _
        rw [hr0, sub_bot]
        omega
  · -- n = m + 1
    rcases Nat.lt_or_ge (m + 1) t with hlt | hge
    · -- main case: 1 ≤ m+1 < t
      have eL : H (t + 1) (m + 1) = 1 ↔ ¬ sub (((t + 1) - (m + 1)) / 2) (r (t + 1)) :=
        H_one_iff (t + 1) (m + 1) (by omega)
      have e1 : H t (m + 1 - 1) = H t (m + 1) ↔
          (sub ((t - (m + 1 - 1)) / 2) s ↔ sub ((t - (m + 1)) / 2) s) := by
        have h := H_eq_H_iff t (m + 1 - 1) (m + 1) (by omega) (by omega)
        rw [hrt] at h
        exact h
      have e2 : H t (m + 1) = H t (m + 1 + 1) ↔
          (sub ((t - (m + 1)) / 2) s ↔ sub ((t - (m + 1 + 1)) / 2) s) := by
        have h := H_eq_H_iff t (m + 1) (m + 1 + 1) (by omega) (by omega)
        rw [hrt] at h
        exact h
      rw [eL, e1, e2]
      have hA : (t + 1) - (m + 1) = t - m := by omega
      have hB : t - (m + 1 - 1) = t - m := by omega
      have hC : t - (m + 1) = t - m - 1 := by omega
      have hD : t - (m + 1 + 1) = t - m - 2 := by omega
      rw [hA, hB, hC, hD]
      obtain ⟨e, hd | hd⟩ := two_mul_or_two_mul_add_one (t - m)
      · rw [hd]
        have he1 : 1 ≤ e := by omega
        have h1' : (2 * e) / 2 = e := by omega
        have h2' : (2 * e - 1) / 2 = e - 1 := by omega
        have h3' : (2 * e - 2) / 2 = e - 1 := by omega
        rw [h1', h2', h3']
        rw [show ((¬ sub e (r (t + 1)) ↔ (sub e s ↔ sub (e - 1) s) ∧ (sub (e - 1) s ↔ sub (e - 1) s))
              ↔ (¬ sub e (r (t + 1)) ↔ (sub e s ↔ sub (e - 1) s))) from
            ⟨fun h => ⟨fun hp => (h.mp hp).1, fun hab => h.mpr ⟨hab, Iff.rfl⟩⟩,
             fun h => ⟨fun hp => ⟨h.mp hp, Iff.rfl⟩, fun hx => h.mpr hx.1⟩⟩]
        rcases Nat.lt_or_eq_of_le hs1 with hcarry | hcarry
        · have hr1 : r (t + 1) = s + 1 :=
            r_eq_of (t + 1) K (s + 1) (by omega) (by omega) hcarry
          rw [hr1]
          exact not_sub_succ he1
        · have hr0 : r (t + 1) = 0 := by
            apply r_eq_of (t + 1) (K + 1) 0 (by omega)
            · rw [Nat.pow_succ']; omega
            · exact Nat.two_pow_pos _
          have hseq : s = 2 ^ K - 1 := by omega
          have hse : sub e s := by rw [hseq]; exact sub_of_lt_two_pow (by omega)
          have hse1 : sub (e - 1) s := by rw [hseq]; exact sub_of_lt_two_pow (by omega)
          have hne : e ≠ 0 := by omega
          rw [hr0]
          simp [sub_bot, hse, hse1, hne]
      · rw [hd]
        have he1 : 1 ≤ e := by omega
        have h1' : (2 * e + 1) / 2 = e := by omega
        have h2' : (2 * e + 1 - 1) / 2 = e := by omega
        have h3' : (2 * e + 1 - 2) / 2 = e - 1 := by omega
        rw [h1', h2', h3']
        rw [show ((¬ sub e (r (t + 1)) ↔ (sub e s ↔ sub e s) ∧ (sub e s ↔ sub (e - 1) s))
              ↔ (¬ sub e (r (t + 1)) ↔ (sub e s ↔ sub (e - 1) s))) from
            ⟨fun h => ⟨fun hp => (h.mp hp).2, fun hab => h.mpr ⟨Iff.rfl, hab⟩⟩,
             fun h => ⟨fun hp => ⟨Iff.rfl, h.mp hp⟩, fun hx => h.mpr hx.2⟩⟩]
        rcases Nat.lt_or_eq_of_le hs1 with hcarry | hcarry
        · have hr1 : r (t + 1) = s + 1 :=
            r_eq_of (t + 1) K (s + 1) (by omega) (by omega) hcarry
          rw [hr1]
          exact not_sub_succ he1
        · have hr0 : r (t + 1) = 0 := by
            apply r_eq_of (t + 1) (K + 1) 0 (by omega)
            · rw [Nat.pow_succ']; omega
            · exact Nat.two_pow_pos _
          have hseq : s = 2 ^ K - 1 := by omega
          have hse : sub e s := by rw [hseq]; exact sub_of_lt_two_pow (by omega)
          have hse1 : sub (e - 1) s := by rw [hseq]; exact sub_of_lt_two_pow (by omega)
          have hne : e ≠ 0 := by omega
          rw [hr0]
          simp [sub_bot, hse, hse1, hne]
    · rcases Nat.lt_or_eq_of_le hge with hgt | heqt
      · -- n > t
        rcases Nat.lt_or_eq_of_le (by omega : t + 1 ≤ m + 1) with h2 | h2
        · -- n > t+1
          have g1 : H (t + 1) (m + 1) = 1 := H_of_gt (by omega)
          have g2 : H t (m + 1 - 1) = 1 := H_of_gt (by omega)
          have g3 : H t (m + 1) = 1 := H_of_gt (by omega)
          have g4 : H t (m + 1 + 1) = 1 := H_of_gt (by omega)
          rw [g1, g2, g3, g4]
          simp
        · -- n = t+1
          rw [← h2]
          have g1 : H (t + 1) (t + 1) = 0 := by
            rw [H_of_le (t := t + 1) (n := t + 1) (by omega), Nat.sub_self]
            exact G_zero_depth (t + 1)
          have g2 : H t (t + 1 - 1) = 0 := by
            have hh : t + 1 - 1 = t := by omega
            rw [hh, H_of_le (t := t) (n := t) (by omega), Nat.sub_self]
            exact G_zero_depth t
          have g3 : H t (t + 1) = 1 := H_of_gt (by omega)
          have g4 : H t (t + 1 + 1) = 1 := H_of_gt (by omega)
          rw [g1, g2, g3, g4]
          simp
      · -- n = t
        rw [← heqt]
        have g1 : H (t + 1) t = 0 := by
          rw [H_of_le (t := t + 1) (n := t) (by omega)]
          have hh : t + 1 - t = 1 := by omega
          rw [hh, G_zero_iff]
          have h0 : (1 : Nat) / 2 = 0 := by omega
          rw [h0]
          exact sub_zero _
        have g2 : H t (t - 1) = 0 := by
          rw [H_of_le (t := t) (n := t - 1) (by omega)]
          have hh : t - (t - 1) = 1 := by omega
          rw [hh, G_zero_iff]
          have h0 : (1 : Nat) / 2 = 0 := by omega
          rw [h0]
          exact sub_zero _
        have g3 : H t t = 0 := by
          rw [H_of_le (t := t) (n := t) (by omega), Nat.sub_self]
          exact G_zero_depth t
        have g4 : H t (t + 1) = 1 := H_of_gt (by omega)
        rw [g1, g2, g3, g4]
        simp



/-! ### Rule 129 : the evolution -/

/-- Row t of the Rule 129 evolution started from a single 1 at the origin. -/
def row : Nat → (Int → Nat)
  | 0 => fun j => if j = 0 then 1 else 0
  | t + 1 => fun j => if row t (j - 1) = row t j ∧ row t j = row t (j + 1) then 1 else 0

theorem row_zero : row 0 = fun j => if j = 0 then 1 else 0 := rfl

theorem row_succ (t : Nat) (j : Int) :
    row (t + 1) j = if row t (j - 1) = row t j ∧ row t j = row t (j + 1) then 1 else 0 :=
  rfl

theorem row0_of_ne {x : Int} (h : x ≠ 0) : row 0 x = 0 := by
  rw [row_zero]; simp [h]

theorem row_symm : ∀ (t : Nat) (j : Int), row t (-j) = row t j := by
  intro t
  induction t with
  | zero =>
    intro j
    by_cases h : j = 0
    · subst h; rfl
    · have h' : -j ≠ (0 : Int) := by omega
      rw [row0_of_ne h, row0_of_ne h']
  | succ t ih =>
    intro j
    rw [row_succ, row_succ]
    have e1 : -j - 1 = -(j + 1) := by omega
    have e2 : -j + 1 = -(j - 1) := by omega
    rw [e1, e2, ih, ih, ih]
    have hiff : (row t (j + 1) = row t j ∧ row t j = row t (j - 1)) ↔
        (row t (j - 1) = row t j ∧ row t j = row t (j + 1)) := by
      constructor
      · rintro ⟨a, b⟩; exact ⟨b.symm, a.symm⟩
      · rintro ⟨a, b⟩; exact ⟨b.symm, a.symm⟩
    by_cases h : row t (j - 1) = row t j ∧ row t j = row t (j + 1)
    · rw [if_pos h, if_pos (hiff.mpr h)]
    · rw [if_neg h, if_neg (fun hh => h (hiff.mp hh))]

theorem row_one_val (x : Int) :
    row 1 x = if (x = -1 ∨ x = 0 ∨ x = 1) then 0 else 1 := by
  rw [row_succ]
  have h0 : ∀ y : Int, row 0 y = if y = 0 then 1 else 0 := fun y => rfl
  rw [h0, h0, h0]
  by_cases h : x = -1 ∨ x = 0 ∨ x = 1
  · rcases h with h | h | h <;> (subst h; decide)
  · rw [if_neg h]
    have h1 : x - 1 ≠ 0 := by omega
    have h2 : x ≠ 0 := by omega
    have h3 : x + 1 ≠ 0 := by omega
    rw [if_neg h1, if_neg h2, if_neg h3]
    simp

theorem H_one_val (n : Nat) : H 1 n = if n ≤ 1 then 0 else 1 := by
  by_cases h : n ≤ 1
  · rw [if_pos h, H_of_le (t := 1) h, G_zero_iff]
    have h0 : (1 - n) / 2 = 0 := by omega
    rw [h0]
    exact sub_zero _
  · rw [if_neg h, H_of_gt (by omega)]

theorem H_le_one (t n : Nat) : H t n ≤ 1 := by
  by_cases h : n ≤ t
  · rw [H_of_le h]; unfold G; omega
  · rw [H_of_gt (by omega)]

theorem ite_one_zero_eq {c : Prop} [Decidable c] {a : Nat} (ha : a ≤ 1) (h : c ↔ a = 1) :
    (if c then 1 else 0) = a := by
  by_cases hc : c
  · have h1 : a = 1 := h.mp hc
    rw [if_pos hc]; omega
  · have h1 : a ≠ 1 := fun hh => hc (h.mpr hh)
    rw [if_neg hc]; omega

/-! ### x(t,j) equals the closed form -/

theorem row_eq_H : ∀ (t : Nat), 1 ≤ t → ∀ n : Nat, row t (n : Int) = H t n := by
  intro t
  induction t using Nat.strongRecOn with
  | ind t ih =>
    intro ht n
    match t with
    | 0 => omega
    | 1 =>
      rw [row_one_val, H_one_val]
      by_cases h : n ≤ 1
      · have h' : ((n : Int) = -1 ∨ (n : Int) = 0 ∨ (n : Int) = 1) := by
          rcases Nat.lt_or_eq_of_le h with h0 | h1
          · right; left; omega
          · right; right; omega
        rw [if_pos h', if_pos h]
      · have h' : ¬ ((n : Int) = -1 ∨ (n : Int) = 0 ∨ (n : Int) = 1) := by
          rintro (h1 | h2 | h3) <;> omega
        rw [if_neg h', if_neg h]
    | k + 2 =>
      have ih' : ∀ n : Nat, row (k + 1) (n : Int) = H (k + 1) n :=
        ih (k + 1) (by omega) (by omega)
      have ih2 : ∀ x : Int, 0 ≤ x → row (k + 1) x = H (k + 1) x.natAbs := by
        intro x hx
        have hx' : x = ((x.natAbs : Nat) : Int) := by
          rw [Int.natAbs_of_nonneg hx]
        rw [hx']
        exact ih' x.natAbs
      rw [row_succ]
      rcases n with _ | m
      · have e1 : row (k + 1) (((0 : Nat) : Int) - 1) = H (k + 1) 1 := by
          have h : (((0 : Nat) : Int) - 1) = -((1 : Int)) := by omega
          rw [h, row_symm]
          simpa using ih2 (1 : Int) (by omega)
        have e2 : row (k + 1) ((0 : Nat) : Int) = H (k + 1) 0 := ih' 0
        have e3 : row (k + 1) (((0 : Nat) : Int) + 1) = H (k + 1) 1 := by
          have h : (((0 : Nat) : Int) + 1) = ((1 : Nat) : Int) := by omega
          rw [h, ih']
        rw [e1, e2, e3]
        refine ite_one_zero_eq (H_le_one _ _) ?_
        have hstep := H_step (k + 1) (by omega) 0
        simp only [Nat.zero_sub] at hstep
        rw [hstep]
        constructor
        · rintro ⟨a, b⟩; exact ⟨trivial, b⟩
        · rintro ⟨_, b⟩; exact ⟨b.symm, b⟩
      · have e1 : row (k + 1) (((m + 1 : Nat) : Int) - 1) = H (k + 1) m := by
          have h : (((m + 1 : Nat) : Int) - 1) = ((m : Nat) : Int) := by omega
          rw [h, ih']
        have e2 : row (k + 1) ((m + 1 : Nat) : Int) = H (k + 1) (m + 1) := ih' (m + 1)
        have e3 : row (k + 1) (((m + 1 : Nat) : Int) + 1) = H (k + 1) (m + 1 + 1) := by
          have h : (((m + 1 : Nat) : Int) + 1) = ((m + 1 + 1 : Nat) : Int) := by omega
          rw [h, ih']
        rw [e1, e2, e3]
        refine ite_one_zero_eq (H_le_one _ _) ?_
        simpa using (H_step (k + 1) (by omega) (m + 1)).symm

theorem row_eq_F (t : Nat) (ht : 1 ≤ t) (j : Int) : row t j = F t j := by
  obtain ⟨n, hn | hn⟩ := Int.eq_nat_or_neg j
  · rw [hn, row_eq_H t ht n]
    unfold F
    rw [Int.natAbs_natCast]
  · rw [hn, row_symm, row_eq_H t ht n]
    unfold F
    rw [Int.natAbs_neg, Int.natAbs_natCast]

/-- The local identity : the closed form satisfies the Rule 129 recursion. -/
theorem F_step (t : Nat) (ht : 1 ≤ t) (j : Int) :
    F (t + 1) j = 1 ↔ F t (j - 1) = F t j ∧ F t j = F t (j + 1) := by
  have hrow : row (t + 1) j = if (F t (j - 1) = F t j ∧ F t j = F t (j + 1)) then 1 else 0 := by
    rw [row_succ, row_eq_F t ht (j - 1), row_eq_F t ht j, row_eq_F t ht (j + 1)]
  have hF : F (t + 1) j = row (t + 1) j := (row_eq_F (t + 1) (by omega) j).symm
  rw [hF, hrow]
  by_cases h : (F t (j - 1) = F t j ∧ F t j = F t (j + 1))
  · rw [if_pos h]; simp [h]
  · rw [if_neg h]; simp [h]

/-! ### The middle column -/

theorem row_middle (t : Nat) (ht : 1 ≤ t) :
    row t (0 : Int) = 0 ↔ ∃ k : Nat, 1 ≤ k ∧ t = 2 ^ k - 1 := by
  have hF : row t (0 : Int) = H t 0 := row_eq_H t ht 0
  rw [hF]
  have hH : H t 0 = G t t := by
    rw [H_of_le (t := t) (n := 0) (by omega)]
    congr 1
  rw [hH, G_zero_iff]
  constructor
  · intro hsub
    obtain ⟨K, s, hK, hsK⟩ := exists_pow_add t ht
    have hrs : r t = s := r_eq_of t K s ht hK hsK
    rw [hrs] at hsub
    rcases Nat.eq_zero_or_pos K with hK0 | hKpos
    · subst hK0
      have hs1 : s < 1 := by simpa using hsK
      have hs : s = 0 := by omega
      subst hs
      have ht1 : t = 1 := by simpa using hK
      exact ⟨1, by omega, by rw [ht1]; simp⟩
    · obtain ⟨K', rfl⟩ : ∃ K', K = K' + 1 := ⟨K - 1, by omega⟩
      have ht2 : t / 2 = 2 ^ K' + s / 2 := by
        rw [hK, Nat.pow_succ']; omega
      rw [ht2] at hsub
      have hle := sub_le hsub
      have hdm : 2 * (s / 2) + s % 2 = s := Nat.div_add_mod s 2
      have hs : s = 2 ^ (K' + 1) - 1 := by rw [Nat.pow_succ']; omega
      refine ⟨K' + 2, by omega, ?_⟩
      have hp : 2 ^ (K' + 2) = 2 * 2 ^ (K' + 1) := by
        rw [show K' + 2 = (K' + 1) + 1 from by omega, Nat.pow_succ']
      rw [hp]
      omega
  · rintro ⟨k, hk, rfl⟩
    rcases k with _ | k'
    · omega
    · rcases k' with _ | k''
      · have h1 : (2 : Nat) ^ (0 + 1) - 1 = 1 := by decide
        rw [h1, r_one]
        have h0 : (1 : Nat) / 2 = 0 := by decide
        rw [h0]
        exact sub_zero _
      · have hp : 2 ^ (k'' + 2) = 2 * 2 ^ (k'' + 1) := by
          rw [show k'' + 2 = (k'' + 1) + 1 from by omega, Nat.pow_succ']
        have hp1 : 2 ≤ 2 ^ (k'' + 1) := by
          have h2 : 2 ^ 1 ≤ 2 ^ (k'' + 1) := Nat.pow_le_pow_right (by omega) (by omega)
          simpa using h2
        have hK : 2 ^ (k'' + 2) - 1 = 2 ^ (k'' + 1) + (2 ^ (k'' + 1) - 1) := by rw [hp]; omega
        have hs : 2 ^ (k'' + 1) - 1 < 2 ^ (k'' + 1) := by omega
        rw [hK]
        have hr : r (2 ^ (k'' + 1) + (2 ^ (k'' + 1) - 1)) = 2 ^ (k'' + 1) - 1 :=
          r_eq_of _ (k'' + 1) (2 ^ (k'' + 1) - 1) (by omega) rfl hs
        rw [hr]
        have hd : (2 ^ (k'' + 1) + (2 ^ (k'' + 1) - 1)) / 2 = 2 ^ (k'' + 1) - 1 := by omega
        rw [hd]
        exact sub_self _



theorem row_le_one (t : Nat) (j : Int) : row t j ≤ 1 := by
  rcases Nat.eq_zero_or_pos t with h | h
  · subst h
    rw [row_zero]
    by_cases hj : j = 0 <;> simp [hj]
  · rw [row_eq_F t h j]
    exact H_le_one t j.natAbs

/-- The closed form, in the form stated in the problem: for t >= 1,

    x(t,j) = 0  <=>  |j| <= t  and  floor((t-|j|)/2) is a submask of r t. -/
theorem row_closed_form (t : Nat) (ht : 1 ≤ t) (j : Int) :
    row t j = 0 ↔ j.natAbs ≤ t ∧ sub ((t - j.natAbs) / 2) (r t) := by
  rw [row_eq_F t ht j]
  unfold F
  by_cases h : j.natAbs ≤ t
  · rw [H_of_le h, G_zero_iff]
    exact ⟨fun hh => ⟨h, hh⟩, fun hh => hh.2⟩
  · rw [H_of_gt (by omega)]
    exact ⟨fun hh => absurd hh (by omega), fun hh => absurd hh.1 h⟩

/-- The depth form: at depth d (i.e. at position t - d) the cell is 1 exactly when
d/2 is not a submask of r t. -/
theorem row_depth_form (t : Nat) (ht : 1 ≤ t) (d : Nat) (hd : d ≤ t) :
    row t ((t - d : Nat) : Int) = 1 ↔ ¬ sub (d / 2) (r t) := by
  have hle := row_le_one t ((t - d : Nat) : Int)
  have h0 : row t ((t - d : Nat) : Int) = 0 ↔ sub (d / 2) (r t) := by
    rw [row_closed_form t ht]
    rw [Int.natAbs_natCast]
    have h2 : t - (t - d) = d := by omega
    rw [h2]
    exact ⟨fun hh => hh.2, fun hh => ⟨by omega, hh⟩⟩
  have hr : row t ((t - d : Nat) : Int) = 1 ↔ ¬ row t ((t - d : Nat) : Int) = 0 := by
    constructor <;> intro hh <;> omega
  rw [hr, h0]

#print axioms row_eq_F
#print axioms F_step
#print axioms row_closed_form
#print axioms row_depth_form
#print axioms row_middle


/- ============================================================
    Universal (geometric) form of the closed form.

    The "all equal" rule on an abstract levelled structure:
    a point of level d is set to 1 iff its whole neighbourhood
    carries the same value as itself.  Hypotheses:
      (H1) the neighbourhood of a level-d point meets only levels
           d-1, d, d+1;
      (H2) every point belongs to its own neighbourhood;
      (H3) a point of level >= 1 has a neighbour of level d-1;
      (H4) every point has a neighbour of level d+1.
    (H4) for all points forces the structure to be infinite, which
    is exactly the case for lattices with convex neighbourhoods.

    Conjecture (verified numerically on 210k cells, not yet
    formalised): the state at time t equals H t (level x).
    ============================================================ -/

section Universal

variable {X : Type}

/-- One step of the all-equal rule. -/
noncomputable def ustep (nbhd : X → Finset X) (f : X → Nat) : X → Nat :=
  fun x => if ∀ y ∈ nbhd x, f y = f x then 1 else 0

/-- Initial configuration: 1 at level 0, 0 elsewhere. -/
noncomputable def uinit (lev : X → Nat) : X → Nat := fun x => if lev x = 0 then 1 else 0

variable (lev : X → Nat) (nbhd : X → Finset X)

/-- The state after t steps (recursive form, so that the successor equation is rfl). -/
noncomputable def ustate : Nat → X → Nat
  | 0 => uinit lev
  | (t+1) => ustep nbhd (ustate t)

theorem ustate_succ (t : Nat) :
    ustate lev nbhd (t+1) = ustep nbhd (ustate lev nbhd t) := rfl

theorem ustate_zero : ustate lev nbhd 0 = uinit lev := rfl

/-- (H1) the neighbourhood only meets the three adjacent levels. -/
def UBound : Prop := ∀ x y, y ∈ nbhd x → lev y + 1 ≥ lev x ∧ lev y ≤ lev x + 1

/-- (H2) reflexivity. -/
def UMem : Prop := ∀ x, x ∈ nbhd x

/-- (H3) a point of positive level has a neighbour one level below. -/
def UPrev : Prop := ∀ x, 1 ≤ lev x → ∃ y ∈ nbhd x, lev y = lev x - 1

/-- (H4) every point has a neighbour one level above. -/
def UNext : Prop := ∀ x, ∃ y ∈ nbhd x, lev y = lev x + 1

/-  Proof plan for the main theorem

      theorem universal (t : Nat) (ht : 1 ≤ t) (x : X) :
          ustate lev nbhd t x = H t (lev x)

    (1) Level constancy:  ∀ t x y, lev x = lev y → ustate t x = ustate t y.
        Induction on t.  Step: the condition "all neighbours equal"
        at a point of level d reduces, by (H1)-(H4) and the induction
        hypothesis, to the conjunction
            phi (d-1) = phi d  ∧  phi d = phi (d+1)     (d ≥ 1)
            phi 0 = phi 1                               (d = 0)
        where phi e is the (well defined) value on level e.  Hence it
        depends on d only.

    (2) The main theorem then follows by induction on t, using
        H_step (proved above for the one-dimensional case) to identify
        the three-level conjunction with H (t+1) d = 1.
-/

/-- Level constancy: the state at time t depends only on the level. -/
theorem ustate_dep (hm : UMem nbhd) (hb : UBound lev nbhd)
    (hp : UPrev lev nbhd) (hn : UNext lev nbhd) :
    ∀ t : Nat, ∀ x y : X, lev x = lev y → ustate lev nbhd t x = ustate lev nbhd t y := by
  intro t
  induction t with
  | zero =>
    intro x y h
    show uinit lev x = uinit lev y
    simp only [uinit, h]
  | succ t ih =>
    intro x y hxy
    show ustep nbhd (ustate lev nbhd t) x = ustep nbhd (ustate lev nbhd t) y
    simp only [ustep]
    have key : (∀ z ∈ nbhd x, ustate lev nbhd t z = ustate lev nbhd t x)
             ↔ (∀ z ∈ nbhd y, ustate lev nbhd t z = ustate lev nbhd t y) := by
      constructor
      · intro h z hz
        have hbzy := hb y z hz
        rw [← hxy] at hbzy
        by_cases e1 : lev z = lev x
        · rw [ih z x e1, ih x y hxy]
        · by_cases e2 : lev z = lev x + 1
          · obtain ⟨w, hw, hwlev⟩ := hn x
            have hzw : lev z = lev w := by rw [e2, hwlev]
            rw [ih z w hzw, h w hw, ih x y hxy]
          · have hd : lev z + 1 = lev x := by omega
            have hge : 1 ≤ lev x := by omega
            obtain ⟨w, hw, hwlev⟩ := hp x hge
            have hzw : lev z = lev w := by rw [hwlev]; omega
            rw [ih z w hzw, h w hw, ih x y hxy]
      · intro h z hz
        have hbzx := hb x z hz
        rw [hxy] at hbzx
        by_cases e1 : lev z = lev x
        · rw [ih z y (by rw [e1, hxy]), ih x y hxy]
        · by_cases e2 : lev z = lev x + 1
          · obtain ⟨w, hw, hwlev⟩ := hn y
            have hzw : lev z = lev w := by rw [e2, hwlev, hxy]
            rw [ih z w hzw, h w hw, ih x y hxy]
          · have hd : lev z + 1 = lev x := by omega
            have hge : 1 ≤ lev x := by omega
            obtain ⟨w, hw, hwlev⟩ := hp y (by omega)
            have hzw : lev z = lev w := by rw [hwlev]; omega
            rw [ih z w hzw, h w hw, ih x y hxy]
    by_cases hc : ∀ z ∈ nbhd x, ustate lev nbhd t z = ustate lev nbhd t x
    · rw [if_pos hc, if_pos (key.mp hc)]
    · rw [if_neg hc, if_neg (fun hh => hc (key.mpr hh))]
theorem step_preserved (hm : UMem nbhd) (hb : UBound lev nbhd)
    (hp : UPrev lev nbhd) (hn : UNext lev nbhd) (t : Nat) (ht : 1 ≤ t)
    (h : ∀ x : X, ustate lev nbhd t x = H t (lev x)) :
    ∀ x : X, ustate lev nbhd (t+1) x = H (t+1) (lev x) := by
  intro x
  rw [ustate_succ]
  simp only [ustep]
  simp only [h]
  by_cases hc : ∀ y ∈ nbhd x, H t (lev y) = H t (lev x)
  · have h3 : H t (lev x - 1) = H t (lev x) ∧ H t (lev x) = H t (lev x + 1) := by
      constructor
      · by_cases h0 : lev x = 0
        · rw [h0]
        · obtain ⟨w, hw, hwlev⟩ := hp x (by omega)
          have hw1 := hc w hw
          have hsub : lev x - 1 = lev w := by omega
          rw [hsub]
          exact hw1
      · obtain ⟨w, hw, hwlev⟩ := hn x
        have hw1 := hc w hw
        have hsub : lev x + 1 = lev w := by omega
        rw [hsub]
        exact hw1.symm
    rw [if_pos hc, (H_step t ht (lev x)).mpr h3]
  · rw [if_neg hc]
    have h3 : ¬ (H t (lev x - 1) = H t (lev x) ∧ H t (lev x) = H t (lev x + 1)) := by
      intro hh
      apply hc
      intro y hy
      have hbxy := hb x y hy
      by_cases e1 : lev y = lev x
      · rw [e1]
      · by_cases e2 : lev y = lev x + 1
        · rw [e2]; exact hh.2.symm
        · have hge : lev y = lev x - 1 := by omega
          rw [hge]; exact hh.1
    have hne : H (t+1) (lev x) ≠ 1 := fun hh => h3 ((H_step t ht (lev x)).mp hh)
    have hle : H (t+1) (lev x) ≤ 1 := H_le_one (t+1) (lev x)
    omega
/-- Equation lemmas for ustep, avoiding if-rewriting on the goal. -/
theorem ustep_pos {nbhd : X → Finset X} {f : X → Nat} {x : X}
    (h : ∀ y ∈ nbhd x, f y = f x) : ustep nbhd f x = 1 := by
  unfold ustep
  rw [if_pos h]

theorem ustep_neg {nbhd : X → Finset X} {f : X → Nat} {x : X}
    (h : ¬ ∀ y ∈ nbhd x, f y = f x) : ustep nbhd f x = 0 := by
  unfold ustep
  rw [if_neg h]

/-- Base case: at time 1 the value is H 1 (level x). -/
theorem ustate_one (hm : UMem nbhd) (hb : UBound lev nbhd)
    (hp : UPrev lev nbhd) (hn : UNext lev nbhd) (x : X) :
    ustate lev nbhd 1 x = H 1 (lev x) := by
  have h1 : ustate lev nbhd 1 x = ustep nbhd (uinit lev) x := rfl
  rw [h1, H_one_val]
  by_cases h0 : lev x = 0
  · have hne : ¬ ∀ y ∈ nbhd x, uinit lev y = uinit lev x := by
      intro hc
      obtain ⟨w, hw, hwlev⟩ := hn x
      have hw0 : lev w ≠ 0 := by omega
      have hu : uinit lev w ≠ uinit lev x := by
        simp only [uinit]
        simp [hw0, h0]
      exact hu (hc w hw)
    rw [ustep_neg hne]
    rw [if_pos (by omega : lev x ≤ 1)]
  · by_cases h1c : lev x = 1
    · have hne : ¬ ∀ y ∈ nbhd x, uinit lev y = uinit lev x := by
        intro hc
        obtain ⟨w, hw, hwlev⟩ := hp x (by omega)
        have hw0 : lev w = 0 := by omega
        have hu : uinit lev w ≠ uinit lev x := by
          simp only [uinit]
          simp [hw0, h1c]
        exact hu (hc w hw)
      rw [ustep_neg hne]
      rw [if_pos (by omega : lev x ≤ 1)]
    · have hge : 2 ≤ lev x := by omega
      have hpos : ∀ y ∈ nbhd x, uinit lev y = uinit lev x := by
        intro y hy
        have hbxy := hb x y hy
        have hy0 : lev y ≠ 0 := by omega
        simp only [uinit]
        simp [hy0, h0]
      rw [ustep_pos hpos]
      rw [if_neg (by omega : ¬ lev x ≤ 1)]
/-- Main theorem: the state at time t is H t (level x), for every geometry
    satisfying (H1)-(H4). -/
theorem universal (hm : UMem nbhd) (hb : UBound lev nbhd)
    (hp : UPrev lev nbhd) (hn : UNext lev nbhd) :
    ∀ t : Nat, 1 ≤ t → ∀ x : X, ustate lev nbhd t x = H t (lev x) := by
  intro t
  induction t with
  | zero => intro h; omega
  | succ t ih =>
    intro ht
    cases t with
    | zero => exact ustate_one lev nbhd hm hb hp hn
    | succ t =>
      exact step_preserved lev nbhd hm hb hp hn (t+1) (by omega) (ih (by omega))

#print axioms ustate_dep
#print axioms ustate_one
#print axioms step_preserved
#print axioms universal
/-- The middle column is the SAME in every geometry satisfying (H1)-(H4). -/
theorem universal_middle (hm : UMem nbhd) (hb : UBound lev nbhd)
    (hp : UPrev lev nbhd) (hn : UNext lev nbhd)
    (x : X) (hx : lev x = 0) (t : Nat) (ht : 1 ≤ t) :
    ustate lev nbhd t x = row t (0 : Int) := by
  rw [universal lev nbhd hm hb hp hn t ht x, hx]
  exact (row_eq_H t ht 0).symm

/-- Geometric invariance: the middle column vanishes exactly at 2^k - 1,
    in every geometry satisfying (H1)-(H4). -/
theorem universal_middle_zero (hm : UMem nbhd) (hb : UBound lev nbhd)
    (hp : UPrev lev nbhd) (hn : UNext lev nbhd)
    (x : X) (hx : lev x = 0) (t : Nat) (ht : 1 ≤ t) :
    ustate lev nbhd t x = 0 ↔ ∃ k : Nat, 1 ≤ k ∧ t = 2 ^ k - 1 := by
  rw [universal_middle lev nbhd hm hb hp hn x hx t ht]
  exact row_middle t ht

#print axioms universal_middle
#print axioms universal_middle_zero
/- ============================================================
    First concrete instance: the radial dynamics on Nat.
    Level = the point itself; the neighbourhood of d is
    {d-1, d, d+1} (with the obvious modification at 0).
    ============================================================ -/

section Radial

def rlev (d : Nat) : Nat := d

def rnb (d : Nat) : Finset Nat := if d = 0 then {0, 1} else {d - 1, d, d + 1}

theorem rnb_mem (d : Nat) : d ∈ rnb d := by
  by_cases h : d = 0
  · simp [rnb, h]
  · simp [rnb, h]

theorem rnb_bound (p q : Nat) (h : q ∈ rnb p) : rlev q + 1 ≥ rlev p ∧ rlev q ≤ rlev p + 1 := by
  simp only [rlev]
  by_cases hp : p = 0
  · subst hp
    simp [rnb] at h
    rcases h with h | h <;> (subst h; omega)
  · simp [rnb, hp] at h
    rcases h with h | h | h <;> (subst h; omega)

theorem rnb_prev (p : Nat) (h : 1 ≤ rlev p) : ∃ q ∈ rnb p, rlev q = rlev p - 1 := by
  have hp : p ≠ 0 := by simp [rlev] at h; omega
  refine ⟨p - 1, ?_, ?_⟩
  · simp [rnb, hp]
  · simp [rlev]

theorem rnb_next (p : Nat) : ∃ q ∈ rnb p, rlev q = rlev p + 1 := by
  refine ⟨p + 1, ?_, ?_⟩
  · by_cases hp : p = 0
    · simp [rnb, hp]
    · simp [rnb, hp]
  · simp [rlev]

/-- The radial dynamics reproduces the Rule 129 middle column. -/
theorem radial_middle (t : Nat) (ht : 1 ≤ t) :
    ustate rlev rnb t 0 = 0 ↔ ∃ k : Nat, 1 ≤ k ∧ t = 2 ^ k - 1 := by
  exact universal_middle_zero rlev rnb rnb_mem rnb_bound rnb_prev rnb_next 0 rfl t ht

#print axioms radial_middle

end Radial

/- ============================================================
    Second concrete instance: the quadratic Moore geometry on
    Nat x Nat.  Level = max a b (the Chebyshev norm on the
    quarter plane, so the level sets are the L-shaped quarter
    shells of the squares); the neighbourhood is the 9-cell
    square {a-1,a,a+1} x {b-1,b,b+1}, truncated at the axes.
    ============================================================ -/

section MooreNat

/-- max, written out explicitly so that the arithmetic is transparent. -/
def nmax (a b : Nat) : Nat := if a ≤ b then b else a

theorem nmax_mono {a b c d : Nat} (h1 : a ≤ c) (h2 : b ≤ d) :
    nmax a b ≤ nmax c d := by
  unfold nmax
  by_cases hab : a ≤ b <;> by_cases hcd : c ≤ d <;> simp [hab, hcd] <;> omega

theorem nmax_pre (a b : Nat) : nmax (a - 1) (b - 1) = nmax a b - 1 := by
  unfold nmax
  by_cases hab : a - 1 ≤ b - 1 <;> by_cases hcd : a ≤ b <;> simp [hab, hcd] <;> omega

theorem nmax_succ (a b : Nat) : nmax (a + 1) (b + 1) = nmax a b + 1 := by
  unfold nmax
  by_cases hab : a + 1 ≤ b + 1 <;> by_cases hcd : a ≤ b <;> simp [hab, hcd] <;> omega

def qlev (p : Nat × Nat) : Nat := nmax p.1 p.2


/-- The 3 x 3 box around p, truncated at the axes: offsets -1, 0, +1
    in each coordinate. -/
def qnb (p : Nat × Nat) : Finset (Nat × Nat) :=
  ((Finset.range 3).product (Finset.range 3)).image
    (fun k : Nat × Nat => (p.1 + k.1 - 1, p.2 + k.2 - 1))

theorem qnb_mem (p : Nat × Nat) : p ∈ qnb p := by
  refine Finset.mem_image.mpr ⟨(1, 1), ?_, ?_⟩
  · simp
  · simp

theorem qnb_coord (p q : Nat × Nat) (h : q ∈ qnb p) :
    q.1 ≤ p.1 + 1 ∧ p.1 ≤ q.1 + 1 ∧ q.2 ≤ p.2 + 1 ∧ p.2 ≤ q.2 + 1 := by
  obtain ⟨k, hk, hq⟩ := Finset.mem_image.mp h
  obtain ⟨hk1, hk2⟩ := Finset.mem_product.mp hk
  rw [Finset.mem_range] at hk1 hk2
  rw [← hq]
  refine ⟨?_, ?_, ?_, ?_⟩ <;> omega

theorem qnb_bound (p q : Nat × Nat) (h : q ∈ qnb p) :
    qlev q + 1 ≥ qlev p ∧ qlev q ≤ qlev p + 1 := by
  obtain ⟨ha1, ha2, hb1, hb2⟩ := qnb_coord p q h
  simp only [qlev]
  constructor
  · calc nmax p.1 p.2 ≤ nmax (q.1 + 1) (q.2 + 1) := nmax_mono ha2 hb2
      _ = nmax q.1 q.2 + 1 := nmax_succ _ _
  · calc nmax q.1 q.2 ≤ nmax (p.1 + 1) (p.2 + 1) := nmax_mono ha1 hb1
      _ = nmax p.1 p.2 + 1 := nmax_succ _ _

theorem qnb_prev (p : Nat × Nat) (h : 1 ≤ qlev p) :
    ∃ q ∈ qnb p, qlev q = qlev p - 1 := by
  refine ⟨(p.1 - 1, p.2 - 1), ?_, ?_⟩
  · refine Finset.mem_image.mpr ⟨(0, 0), ?_, ?_⟩
    · simp
    · simp
  · simp only [qlev]
    exact nmax_pre p.1 p.2

theorem qnb_next (p : Nat × Nat) : ∃ q ∈ qnb p, qlev q = qlev p + 1 := by
  refine ⟨(p.1 + 1, p.2 + 1), ?_, ?_⟩
  · refine Finset.mem_image.mpr ⟨(2, 2), ?_, ?_⟩
    · simp
    · simp
  · simp only [qlev]
    exact nmax_succ p.1 p.2

/-- The 9-cell Moore dynamics on the quarter plane has the same middle
    column: it vanishes exactly at 2^k - 1. -/
theorem moore_middle (t : Nat) (ht : 1 ≤ t) :
    ustate qlev qnb t (0, 0) = 0 ↔ ∃ k : Nat, 1 ≤ k ∧ t = 2 ^ k - 1 := by
  refine universal_middle_zero qlev qnb qnb_mem qnb_bound qnb_prev qnb_next (0, 0) ?_ t ht
  simp [qlev, nmax]

#print axioms qnb_bound
#print axioms qnb_prev
#print axioms qnb_next
#print axioms moore_middle

end MooreNat

/- ============================================================
    Third concrete instance: the infinite binary tree.
    Vertices are binary strings; the level is the depth, and the
    neighbourhood of x is {x, parent x, two children x}.
    Level sets are exponentially large and the geometry is not a
    lattice at all, yet (H1)-(H4) hold, so the root sees exactly
    the same middle column as every lattice.
    ============================================================ -/

section Tree

def tlev (x : List Bool) : Nat := x.length

def tnb (x : List Bool) : Finset (List Bool) :=
  (Finset.range 4).image (fun k : Nat =>
    if k = 0 then x
    else if k = 1 then x.dropLast
    else if k = 2 then x ++ [false]
    else x ++ [true])

theorem tnb_mem (x : List Bool) : x ∈ tnb x := by
  refine Finset.mem_image.mpr ⟨0, by simp, ?_⟩
  simp

theorem tnb_bound (x y : List Bool) (h : y ∈ tnb x) :
    tlev y + 1 ≥ tlev x ∧ tlev y ≤ tlev x + 1 := by
  obtain ⟨k, hk, hy⟩ := Finset.mem_image.mp h
  rw [Finset.mem_range] at hk
  rw [← hy]
  interval_cases k <;> simp [tlev, List.length_dropLast] <;> omega

theorem tnb_prev (x : List Bool) (h : 1 ≤ tlev x) :
    ∃ y ∈ tnb x, tlev y = tlev x - 1 := by
  refine ⟨x.dropLast, ?_, ?_⟩
  · refine Finset.mem_image.mpr ⟨1, by simp, ?_⟩
    simp
  · simp only [tlev]
    exact List.length_dropLast

theorem tnb_next (x : List Bool) : ∃ y ∈ tnb x, tlev y = tlev x + 1 := by
  refine ⟨x ++ [true], ?_, ?_⟩
  · refine Finset.mem_image.mpr ⟨3, by simp, ?_⟩
    simp
  · simp [tlev]

/-- The all-equal rule on the infinite binary tree, started from a single
    1 at the root, is 0 at the root exactly at the times 2^k - 1. -/
theorem tree_middle (t : Nat) (ht : 1 ≤ t) :
    ustate tlev tnb t [] = 0 ↔ ∃ k : Nat, 1 ≤ k ∧ t = 2 ^ k - 1 := by
  refine universal_middle_zero tlev tnb tnb_mem tnb_bound tnb_prev tnb_next [] ?_ t ht
  simp [tlev]

#print axioms tnb_bound
#print axioms tnb_prev
#print axioms tnb_next
#print axioms tree_middle

end Tree

/-- The punchline: the centre of the radial 1D dynamics, of the 9-cell
    Moore box on the quarter plane, and of the infinite binary tree all
    carry the SAME value at every time t >= 1.  The geometry is invisible
    at the centre. -/
theorem centres_agree (t : Nat) (ht : 1 ≤ t) :
    ustate rlev rnb t 0 = ustate qlev qnb t (0, 0) ∧
    ustate rlev rnb t 0 = ustate tlev tnb t [] := by
  have h1 : ustate rlev rnb t 0 = H t 0 := by
    rw [universal rlev rnb rnb_mem rnb_bound rnb_prev rnb_next t ht 0]
    rfl
  have h2 : ustate qlev qnb t (0, 0) = H t 0 := by
    rw [universal qlev qnb qnb_mem qnb_bound qnb_prev qnb_next t ht (0, 0)]
    simp [qlev, nmax]
  have h3 : ustate tlev tnb t [] = H t 0 := by
    rw [universal tlev tnb tnb_mem tnb_bound tnb_prev tnb_next t ht []]
    simp [tlev]
  exact ⟨h1.trans h2.symm, h1.trans h3.symm⟩

#print axioms centres_agree

end Universal
end Rule129
end OEIS
