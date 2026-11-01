import Rep

namespace OEIS
namespace Rule129

/- ============================================================
   The state vector and its digit recursion.

   X t  =  the vector (Phi_0(t), Phi_1(t), ...) of arm moments,
   T0   =  the even transfer  (v k) |-> 2^k * v k,
   T1   =  the odd transfer   (v k) |-> sum_{i = k mod 2} C(k,i) 2^(i+1) v i.

   Then  X (2u) = T0 (X u),  X (2u+1) = T1 (X u),  X 1 = (1,1,1,...),
   and for every k, r < 2^k and n >= 1,

        X (2^k * n + r) = W k r (X n)

   where W k r is the composition of the k transfers read off the bits of r.
   ============================================================ -/

/-- The vector of arm moments at time t. -/
def X (t : Nat) : Nat → Int := fun k => (Phi k t : Int)

/-- The even transfer: Phi_k(2u) = 2^k Phi_k(u). -/
def T0 (v : Nat → Int) : Nat → Int := fun k => 2 ^ k * v k

/-- The odd transfer: only the same-parity lower moments appear. -/
def T1 (v : Nat → Int) : Nat → Int := fun k =>
  (Finset.range (k + 1)).sum (fun i =>
    if i % 2 = k % 2 then (k.choose i : Int) * 2 ^ (i + 1) * v i else 0)

/-- **The initial state.**  arm 1 = {1}, so every moment is 1. -/
theorem X_one : X 1 = fun _ => 1 := by
  funext k
  have h : subm (r 1) = {0} := by
    rw [r_one]
    decide
  simp [X, Phi, h]

#print axioms X_one

/-- **The even step.** -/
theorem X_two_mul (u : Nat) (hu : 1 ≤ u) : X (2 * u) = T0 (X u) := by
  funext k
  simp only [X, T0]
  exact_mod_cast Phi_two_mul k u hu

#print axioms X_two_mul

/-- **The odd step.** -/
theorem X_two_mul_add_one (u : Nat) (hu : 1 ≤ u) : X (2 * u + 1) = T1 (X u) := by
  funext k
  simp only [X, T1]
  exact Phi_two_mul_add_one k u hu

#print axioms X_two_mul_add_one

/-- **The digit recursion.** -/
theorem X_digit (t : Nat) (ht : 2 ≤ t) :
    X t = (if t % 2 = 0 then T0 (X (t / 2)) else T1 (X (t / 2))) := by
  have hhalf : 1 ≤ t / 2 := by omega
  have hdec : t = 2 * (t / 2) + t % 2 := by omega
  rcases Nat.mod_two_eq_zero_or_one t with h | h
  · rw [if_pos h, ← X_two_mul (t / 2) hhalf]
    conv_lhs => rw [hdec, h, Nat.add_zero]
  · rw [if_neg (by omega), ← X_two_mul_add_one (t / 2) hhalf]
    conv_lhs => rw [hdec, h]

#print axioms X_digit

/-- **The composition of k transfers**, read off the low bits of r. -/
def W : Nat → Nat → (Nat → Int) → (Nat → Int)
  | 0, _, v => v
  | k + 1, r, v => if r % 2 = 0 then T0 (W k (r / 2) v) else T1 (W k (r / 2) v)

/-- **The iteration.**  The state at time 2^k n + r is the state at n followed
    by the k transfers selected by the bits of r. -/
theorem X_iterate (k : Nat) : ∀ (n r : Nat), 1 ≤ n → r < 2 ^ k →
    X (2 ^ k * n + r) = W k r (X n) := by
  induction k with
  | zero =>
    intro n r hn hr
    have hr0 : r = 0 := by omega
    subst hr0
    simp [W]
  | succ k ih =>
    intro n r hn hr
    have hr' : r / 2 < 2 ^ k := by
      have h1 : 2 ^ (k + 1) = 2 * 2 ^ k := by ring
      omega
    have hdec : 2 ^ (k + 1) * n + r = 2 * (2 ^ k * n + r / 2) + r % 2 := by
      rw [show 2 ^ (k + 1) = 2 * 2 ^ k from by ring]
      rw [show 2 * 2 ^ k * n = 2 * (2 ^ k * n) from by ring]
      conv_lhs => rw [show r = 2 * (r / 2) + r % 2 from (Nat.div_add_mod r 2).symm]
      ring
    have hpos : 1 ≤ 2 ^ k * n + r / 2 := by
      have h2k : 0 < 2 ^ k := by positivity
      have hm : 0 < 2 ^ k * n := Nat.mul_pos h2k (by omega)
      omega
    have hIH := ih n (r / 2) hn hr'
    conv_lhs => rw [hdec]
    rcases Nat.mod_two_eq_zero_or_one r with h | h
    · rw [h, Nat.add_zero, X_two_mul _ hpos, hIH]
      simp only [W]
      rw [if_pos h]
    · rw [h, X_two_mul_add_one _ hpos, hIH]
      simp only [W]
      rw [if_neg (by omega)]

#print axioms X_iterate


/- ---------- triangularity: the state at index i only needs the entries <= i ---------- -/

theorem T0_congr {a b : Nat → Int} {i : Nat} (h : ∀ l ≤ i, a l = b l) :
    ∀ l ≤ i, T0 a l = T0 b l := by
  intro l hl
  simp only [T0]
  rw [h l hl]

#print axioms T0_congr

theorem T1_congr {a b : Nat → Int} {i : Nat} (h : ∀ l ≤ i, a l = b l) :
    ∀ l ≤ i, T1 a l = T1 b l := by
  intro l hl
  simp only [T1]
  refine Finset.sum_congr rfl (fun j hj => ?_)
  rw [Finset.mem_range] at hj
  rw [h j (by omega)]

#print axioms T1_congr

/-- **Triangularity of the transfer.**  The i-th component after k steps only
    sees the entries 0, ..., i of the starting vector. -/
theorem W_congr_le (k : Nat) : ∀ (r : Nat) {v w : Nat → Int}, ∀ i,
    (∀ l ≤ i, v l = w l) → ∀ l ≤ i, W k r v l = W k r w l := by
  induction k with
  | zero =>
    intro r v w i h l hl
    exact h l hl
  | succ k ih =>
    intro r v w i h l hl
    simp only [W]
    by_cases hr : r % 2 = 0
    · rw [if_pos hr, if_pos hr]
      exact T0_congr (ih (r / 2) i h) l hl
    · rw [if_neg hr, if_neg hr]
      exact T1_congr (ih (r / 2) i h) l hl

#print axioms W_congr_le

/-- **The finite-state form of the zero count.**  At time t = 2^k n + r the count
    is the functional gamma applied to the state obtained from the state at n by
    the k transfers selected by the bits of r, plus the centre bit. -/
theorem Z_state (c : Nat → Nat) (γ : Nat → Int) (j : Nat) (δ : Int)
    (hγ : ∀ x : Nat, 2 ≤ x →
      (c x : Int) + (c (x - 1) : Int)
        = (Finset.range (j + 1)).sum (fun i => γ i * (x : Int) ^ i))
    (h1 : (c 1 : Int) + (c 0 : Int) = (Finset.range (j + 1)).sum (fun i => γ i) + δ)
    (k n r : Nat) (ht : 1 ≤ 2 ^ k * n + r) (hn : 1 ≤ n) (hr : r < 2 ^ k) :
    (((shell (2 ^ k * n + r)).sum c : Nat) : Int)
      = (Finset.range (j + 1)).sum (fun i => γ i * (W k r (X n) i))
        + δ * (if 1 ∈ arm (2 ^ k * n + r) then 1 else 0) := by
  rw [shell_sum_of_poly_correction c γ j δ _ ht hγ h1]
  congr 1
  refine Finset.sum_congr rfl (fun i hi => ?_)
  rw [← X_iterate k n r hn hr]
  rfl

#print axioms Z_state


/-- **The centre bit is a digit function.**  For r < 2^k,
    0 ∈ shell (2^k n + r) iff r = 2^k - 1 and 0 ∈ shell n. -/
theorem zero_mem_digits (k : Nat) : ∀ (n r : Nat), 1 ≤ n → r < 2 ^ k →
    (0 ∈ shell (2 ^ k * n + r) ↔ (r + 1 = 2 ^ k ∧ 0 ∈ shell n)) := by
  induction k with
  | zero =>
    intro n r hn hr
    have hr0 : r = 0 := by omega
    subst hr0
    simp
  | succ k ih =>
    intro n r hn hr
    have hr' : r / 2 < 2 ^ k := by
      have h1 : 2 ^ (k + 1) = 2 * 2 ^ k := by ring
      omega
    have hdec : 2 ^ (k + 1) * n + r = 2 * (2 ^ k * n + r / 2) + r % 2 := by
      rw [show 2 ^ (k + 1) = 2 * 2 ^ k from by ring]
      rw [show 2 * 2 ^ k * n = 2 * (2 ^ k * n) from by ring]
      conv_lhs => rw [show r = 2 * (r / 2) + r % 2 from (Nat.div_add_mod r 2).symm]
      ring
    have hpos : 1 ≤ 2 ^ k * n + r / 2 := by
      have h2k : 0 < 2 ^ k := by positivity
      have hm : 0 < 2 ^ k * n := Nat.mul_pos h2k (by omega)
      omega
    rw [hdec]
    rcases Nat.mod_two_eq_zero_or_one r with h | h
    · rw [h, Nat.add_zero]
      constructor
      · intro hc
        exact absurd hc (zero_not_mem_shell_two_mul _ hpos)
      · rintro ⟨hr1, -⟩
        have h1 : 2 ^ (k + 1) = 2 * 2 ^ k := by ring
        omega
    · rw [h]
      rw [zero_mem_shell_two_mul_add_one _ hpos, ih n (r / 2) hn hr']
      constructor
      · rintro ⟨h1, h2⟩
        exact ⟨by have := h; omega, h2⟩
      · rintro ⟨h1, h2⟩
        exact ⟨by have := h; omega, h2⟩

#print axioms zero_mem_digits

/-- **The finite-state determination.**  The count at time 2^k n + r is determined
    by the (j+1) arm moments of n and the single bit [0 in shell n]: that is the
    dimension bound of the representation, in determination form. -/
theorem Z_state_determined (c : Nat → Nat) (γ : Nat → Int) (j : Nat) (δ : Int)
    (hγ : ∀ x : Nat, 2 ≤ x →
      (c x : Int) + (c (x - 1) : Int)
        = (Finset.range (j + 1)).sum (fun i => γ i * (x : Int) ^ i))
    (h1 : (c 1 : Int) + (c 0 : Int) = (Finset.range (j + 1)).sum (fun i => γ i) + δ)
    (k r : Nat) (hr : r < 2 ^ k) (n n' : Nat) (hn : 1 ≤ n) (hn' : 1 ≤ n')
    (hPhi : ∀ i, i ≤ j → Phi i n = Phi i n')
    (hEps : (0 ∈ shell n) ↔ (0 ∈ shell n')) :
    (shell (2 ^ k * n + r)).sum c = (shell (2 ^ k * n' + r)).sum c := by
  have hX : ∀ l, l ≤ j → X n l = X n' l := by
    intro l hl
    simp only [X]
    rw [hPhi l hl]
  have hpos : ∀ m : Nat, 1 ≤ m → 1 ≤ 2 ^ k * m + r := by
    intro m hm
    have h2k : 0 < 2 ^ k := by positivity
    have hmm : 0 < 2 ^ k * m := Nat.mul_pos h2k (by omega)
    omega
  have hmain : (Finset.range (j + 1)).sum (fun i => γ i * (W k r (X n)) i)
      = (Finset.range (j + 1)).sum (fun i => γ i * (W k r (X n')) i) := by
    refine Finset.sum_congr rfl (fun i hi => ?_)
    rw [Finset.mem_range] at hi
    have hw : W k r (X n) i = W k r (X n') i :=
      W_congr_le k r i (fun l hl => hX l (Nat.le_trans hl (Nat.le_of_lt_succ hi))) i le_rfl
    rw [hw]
  have hbit : (1 ∈ arm (2 ^ k * n + r)) ↔ (1 ∈ arm (2 ^ k * n' + r)) := by
    rw [← zero_mem_shell_iff (2 ^ k * n + r) (hpos n hn),
      ← zero_mem_shell_iff (2 ^ k * n' + r) (hpos n' hn'),
      zero_mem_digits k n r hn hr, zero_mem_digits k n' r hn' hr, hEps]
  apply Nat.cast_injective (R := Int)
  rw [Z_state c γ j δ hγ h1 k n r (hpos n hn) hn hr,
    Z_state c γ j δ hγ h1 k n' r (hpos n' hn') hn' hr, hmain]
  by_cases hb : 1 ∈ arm (2 ^ k * n + r)
  · have hb' : 1 ∈ arm (2 ^ k * n' + r) := hbit.mp hb
    rw [if_pos hb, if_pos hb']
  · have hb' : ¬ 1 ∈ arm (2 ^ k * n' + r) := fun h => hb (hbit.mpr h)
    rw [if_neg hb, if_neg hb']

#print axioms Z_state_determined

end Rule129
end OEIS