import Digits

namespace OEIS
namespace Rule129

/-- The even transfer matrix. -/
def M0 (i l : Nat) : Int := if l = i then 2 ^ i else 0

/-- The odd transfer matrix. -/
def M1 (i l : Nat) : Int :=
  if l ≤ i ∧ l % 2 = i % 2 then (i.choose l : Int) * 2 ^ (l + 1) else 0

/-- The even transfer, read as a matrix-vector product. -/
theorem T0_apply (v : Nat → Int) (j i : Nat) (hi : i ≤ j) :
    T0 v i = (Finset.range (j + 1)).sum (fun l => M0 i l * v l) := by
  simp only [T0, M0]
  rw [Finset.sum_eq_single i]
  · simp
  · intro l hl hne
    simp [hne]
  · intro hcontra
    rw [Finset.mem_range] at hcontra
    omega

#print axioms T0_apply

/-- The odd transfer, read as a matrix-vector product. -/
theorem T1_apply (v : Nat → Int) (j i : Nat) (hi : i ≤ j) :
    T1 v i = (Finset.range (j + 1)).sum (fun l => M1 i l * v l) := by
  have hsub : (Finset.range (i + 1)) ⊆ (Finset.range (j + 1)) := by
    intro x hx
    rw [Finset.mem_range] at hx ⊢
    omega
  have hstep : (Finset.range (i + 1)).sum (fun l => M1 i l * v l)
      = (Finset.range (j + 1)).sum (fun l => M1 i l * v l) := by
    refine Finset.sum_subset hsub (fun x hx hxnot => ?_)
    rw [Finset.mem_range] at hx hxnot
    simp only [M1]
    rw [if_neg (by omega), zero_mul]
  rw [← hstep]
  simp only [T1, M1]
  refine Finset.sum_congr rfl (fun l hl => ?_)
  rw [Finset.mem_range] at hl
  by_cases h1 : l % 2 = i % 2
  · rw [if_pos h1, if_pos (by omega : l ≤ i ∧ l % 2 = i % 2)]
  · rw [if_neg h1, if_neg (by omega : ¬ (l ≤ i ∧ l % 2 = i % 2)), zero_mul]

#print axioms T1_apply

/-- **The matrix of the composition of k transfers**, truncated to 0..j. -/
def A (j : Nat) : Nat → Nat → Nat → Nat → Int
  | 0, _, i, l => if l = i then 1 else 0
  | k + 1, r, i, l =>
      (Finset.range (j + 1)).sum (fun m =>
        (if r % 2 = 0 then M0 i m else M1 i m) * A j k (r / 2) m l)

/-- **The matrix representation** of the k-fold transfer. -/
theorem W_eq_A (j : Nat) : ∀ (k r : Nat) (v : Nat → Int) (i : Nat), i ≤ j →
    W k r v i = (Finset.range (j + 1)).sum (fun l => A j k r i l * v l) := by
  intro k
  induction k with
  | zero =>
    intro r v i hi
    simp only [W, A]
    rw [Finset.sum_eq_single i]
    · simp
    · intro l hl hne
      simp [hne]
    · intro hcontra
      rw [Finset.mem_range] at hcontra
      omega
  | succ k ih =>
    intro r v i hi
    have hIH : ∀ l, l ≤ j → W k (r / 2) v l
        = (Finset.range (j + 1)).sum (fun m => A j k (r / 2) l m * v m) :=
      fun l hl => ih (r / 2) v l hl
    have hstep : W k.succ r v i = (Finset.range (j + 1)).sum
        (fun m => (if r % 2 = 0 then M0 i m else M1 i m) * W k (r / 2) v m) := by
      simp only [W]
      by_cases hr : r % 2 = 0
      · rw [if_pos hr, T0_apply _ j i hi]
        refine Finset.sum_congr rfl (fun m _ => ?_)
        rw [if_pos hr]
      · rw [if_neg hr, T1_apply _ j i hi]
        refine Finset.sum_congr rfl (fun m _ => ?_)
        rw [if_neg hr]
    rw [hstep]
    have hmain : (Finset.range (j + 1)).sum
        (fun m => (if r % 2 = 0 then M0 i m else M1 i m) * W k (r / 2) v m)
        = (Finset.range (j + 1)).sum
            (fun m => (if r % 2 = 0 then M0 i m else M1 i m)
              * (Finset.range (j + 1)).sum (fun l => A j k (r / 2) m l * v l)) := by
      refine Finset.sum_congr rfl (fun m hm => ?_)
      rw [Finset.mem_range] at hm
      rw [hIH m (by omega)]
    rw [hmain]
    have h2 : (Finset.range (j + 1)).sum
        (fun m => (if r % 2 = 0 then M0 i m else M1 i m)
          * (Finset.range (j + 1)).sum (fun l => A j k (r / 2) m l * v l))
        = (Finset.range (j + 1)).sum (fun l => (Finset.range (j + 1)).sum
            (fun m => (if r % 2 = 0 then M0 i m else M1 i m)
              * (A j k (r / 2) m l * v l))) := by
      rw [Finset.sum_comm]
      refine Finset.sum_congr rfl (fun m _ => ?_)
      rw [Finset.mul_sum]
    rw [h2]
    have h3 : (Finset.range (j + 1)).sum (fun l => (Finset.range (j + 1)).sum
        (fun m => (if r % 2 = 0 then M0 i m else M1 i m) * (A j k (r / 2) m l * v l)))
        = (Finset.range (j + 1)).sum (fun l => (Finset.range (j + 1)).sum
            (fun m => (if r % 2 = 0 then M0 i m else M1 i m) * A j k (r / 2) m l) * v l) := by
      refine Finset.sum_congr rfl (fun l _ => ?_)
      rw [Finset.sum_mul]
      refine Finset.sum_congr rfl (fun m _ => ?_)
      ring
    rw [h3]
    refine Finset.sum_congr rfl (fun l _ => ?_)
    simp only [A]


#print axioms W_eq_A

/-- **The explicit linear representation.**  For every k and every r < 2^k, the
    count at time 2^k n + r is the fixed combination of the arm moments of n with
    coefficients  sum_i gamma i * A j k r i l,  plus the centre bit. -/
theorem Z_row_linear (c : Nat → Nat) (γ : Nat → Int) (j : Nat) (δ : Int)
    (hγ : ∀ x : Nat, 2 ≤ x →
      (c x : Int) + (c (x - 1) : Int)
        = (Finset.range (j + 1)).sum (fun i => γ i * (x : Int) ^ i))
    (h1 : (c 1 : Int) + (c 0 : Int) = (Finset.range (j + 1)).sum (fun i => γ i) + δ)
    (k r : Nat) (hr : r < 2 ^ k) (n : Nat) (hn : 1 ≤ n) :
    (((shell (2 ^ k * n + r)).sum c : Nat) : Int)
      = (Finset.range (j + 1)).sum (fun l =>
          ((Finset.range (j + 1)).sum (fun i => γ i * A j k r i l)) * (Phi l n : Int))
        + δ * (if 1 ∈ arm (2 ^ k * n + r) then 1 else 0) := by
  have hpos : 1 ≤ 2 ^ k * n + r := by
    have h2k : 0 < 2 ^ k := by positivity
    have hmm : 0 < 2 ^ k * n := Nat.mul_pos h2k (by omega)
    omega
  rw [Z_state c γ j δ hγ h1 k n r hpos hn hr]
  congr 1
  have hexp : ∀ i, i ≤ j → W k r (X n) i
      = (Finset.range (j + 1)).sum (fun m => A j k r i m * (X n) m) :=
    fun i hi => W_eq_A j k r (X n) i hi
  calc (Finset.range (j + 1)).sum (fun i => γ i * W k r (X n) i)
      = (Finset.range (j + 1)).sum (fun i =>
          γ i * (Finset.range (j + 1)).sum (fun m => A j k r i m * (X n) m)) := by
        refine Finset.sum_congr rfl (fun i hi => ?_)
        rw [Finset.mem_range] at hi
        rw [hexp i (by omega)]
    _ = (Finset.range (j + 1)).sum (fun i =>
          (Finset.range (j + 1)).sum (fun m => γ i * (A j k r i m * (X n) m))) := by
        refine Finset.sum_congr rfl (fun i _ => ?_)
        rw [Finset.mul_sum]
    _ = (Finset.range (j + 1)).sum (fun m =>
          (Finset.range (j + 1)).sum (fun i => γ i * (A j k r i m * (X n) m))) :=
        Finset.sum_comm
    _ = (Finset.range (j + 1)).sum (fun m =>
          (Finset.range (j + 1)).sum (fun i => γ i * A j k r i m) * (X n) m) := by
        refine Finset.sum_congr rfl (fun m _ => ?_)
        rw [Finset.sum_mul]
        refine Finset.sum_congr rfl (fun i _ => ?_)
        ring
    _ = (Finset.range (j + 1)).sum (fun l =>
          (Finset.range (j + 1)).sum (fun i => γ i * A j k r i l) * (Phi l n : Int)) := by
        refine Finset.sum_congr rfl (fun m _ => ?_)
        rfl

#print axioms Z_row_linear


/- ---------- the constant component: an explicit popcount formula ---------- -/

theorem T0_zero (v : Nat → Int) : T0 v 0 = v 0 := by
  simp [T0]

#print axioms T0_zero

theorem T1_zero (v : Nat → Int) : T1 v 0 = 2 * v 0 := by
  simp [T1]

#print axioms T1_zero

/-- **The constant component of the transferred state.**
    It only sees the popcount of the residue: (W k r v) 0 = #subm r * v 0. -/
theorem W_zero (k : Nat) : ∀ (r : Nat) (v : Nat → Int), r < 2 ^ k →
    W k r v 0 = (subm r).card * v 0 := by
  induction k with
  | zero =>
    intro r v hr
    have hr0 : r = 0 := by omega
    subst hr0
    have h0 : subm 0 = {0} := by decide
    rw [h0]
    simp [W]
  | succ k ih =>
    intro r v hr
    have hr' : r / 2 < 2 ^ k := by
      have h1 : 2 ^ (k + 1) = 2 * 2 ^ k := by ring
      omega
    have hIH := ih (r / 2) v hr'
    rcases Nat.mod_two_eq_zero_or_one r with h | h
    · have he : r = 2 * (r / 2) := by omega
      have hd : 2 * (r / 2) / 2 = r / 2 := by
        rw [Nat.mul_comm]
        exact Nat.mul_div_left _ (by decide : 0 < 2)
      rw [he] at ⊢
      have key : W (k + 1) (2 * (r / 2)) v 0 = T0 (W k (r / 2) v) 0 := by
        simp only [W, hd]
        split_ifs with hc
        · rfl
        · exact absurd (by omega : (2 * (r / 2)) % 2 = 0) hc
      rw [key, T0_zero, hIH, card_subm_two_mul]
    · have he : r = 2 * (r / 2) + 1 := by omega
      have hd : (2 * (r / 2) + 1) / 2 = r / 2 := div_two_mul_add_one _
      rw [he] at ⊢
      have key : W (k + 1) (2 * (r / 2) + 1) v 0 = T1 (W k (r / 2) v) 0 := by
        simp only [W, hd]
        split_ifs with hc
        · exact absurd hc (by omega)
        · rfl
      rw [key, T1_zero, hIH, card_subm_two_mul_add_one]
      push_cast
      ring

#print axioms W_zero

/-- **The 1-D line, in closed form.**  The count at time 2^k n + r is
    4 * #subm r * Phi_0(n) minus the centre bit. -/
theorem phi_line_explicit (k r n : Nat) (hr : r < 2 ^ k) (hn : 1 ≤ n) :
    (((shell (2 ^ k * n + r)).sum (fun d => if d = 0 then 1 else 2) : Nat) : Int)
      = 4 * ((subm r).card * (Phi 0 n : Int))
        - (if 1 ∈ arm (2 ^ k * n + r) then 1 else 0) := by
  have hγ : ∀ x : Nat, 2 ≤ x →
      ((if x = 0 then 1 else 2 : Nat) : Int) + ((if x - 1 = 0 then 1 else 2 : Nat) : Int)
        = (Finset.range (0 + 1)).sum (fun i => (4 : Int) * (x : Int) ^ i) := by
    intro x hx
    have hx0 : ¬ x = 0 := by omega
    have hx1 : ¬ x - 1 = 0 := by omega
    simp only [hx0, hx1, if_false]
    norm_num
  have h1 : ((if 1 = 0 then 1 else 2 : Nat) : Int)
        + ((if 1 - 1 = 0 then 1 else 2 : Nat) : Int)
      = (Finset.range (0 + 1)).sum (fun i => (4 : Int) * (1 : Int) ^ i) + (-1) := by
    norm_num
  have hpos : 1 ≤ 2 ^ k * n + r := by
    have h2k : 0 < 2 ^ k := by positivity
    have hmm : 0 < 2 ^ k * n := Nat.mul_pos h2k (by omega)
    omega
  rw [Z_state (fun d => if d = 0 then 1 else 2) (fun _ => (4 : Int)) 0 (-1)
    hγ h1 k n r hpos hn hr]
  rw [Finset.sum_range_one, W_zero k r (X n) hr]
  simp only [X]
  ring

#print axioms phi_line_explicit


/- ---------- the first component: degree one rows ---------- -/

theorem T0_one (v : Nat → Int) : T0 v 1 = 2 * v 1 := by
  simp [T0]

#print axioms T0_one

theorem T1_one (v : Nat → Int) : T1 v 1 = 4 * v 1 := by
  simp [T1, Finset.sum_range_succ, mul_assoc]

#print axioms T1_one

/-- **The first component of the transferred state.** -/
theorem W_one (k : Nat) : ∀ (r : Nat) (v : Nat → Int), r < 2 ^ k →
    W k r v 1 = 2 ^ k * ((subm r).card * v 1) := by
  induction k with
  | zero =>
    intro r v hr
    have hr0 : r = 0 := by omega
    subst hr0
    have h0 : subm 0 = {0} := by decide
    rw [h0]
    simp [W]
  | succ k ih =>
    intro r v hr
    have hr' : r / 2 < 2 ^ k := by
      have h1 : 2 ^ (k + 1) = 2 * 2 ^ k := by ring
      omega
    have hIH := ih (r / 2) v hr'
    rcases Nat.mod_two_eq_zero_or_one r with h | h
    · have he : r = 2 * (r / 2) := by omega
      have hd : 2 * (r / 2) / 2 = r / 2 := by
        rw [Nat.mul_comm]
        exact Nat.mul_div_left _ (by decide : 0 < 2)
      rw [he] at ⊢
      have key : W (k + 1) (2 * (r / 2)) v 1 = T0 (W k (r / 2) v) 1 := by
        simp only [W, hd]
        split_ifs with hc
        · rfl
        · exact absurd (by omega : (2 * (r / 2)) % 2 = 0) hc
      rw [key, T0_one, hIH, card_subm_two_mul]
      push_cast
      ring
    · have he : r = 2 * (r / 2) + 1 := by omega
      have hd : (2 * (r / 2) + 1) / 2 = r / 2 := div_two_mul_add_one _
      rw [he] at ⊢
      have key : W (k + 1) (2 * (r / 2) + 1) v 1 = T1 (W k (r / 2) v) 1 := by
        simp only [W, hd]
        split_ifs with hc
        · exact absurd hc (by omega)
        · rfl
      rw [key, T1_one, hIH, card_subm_two_mul_add_one]
      push_cast
      ring

#print axioms W_one

/-- **Z^2 von Neumann, in closed form.**  The count at time 2^k n + r is
    (-4 #subm r) Phi_0(n) + (8 * 2^k * #subm r) Phi_1(n) plus the centre bit. -/
theorem phi_z2vn_explicit (k r n : Nat) (hr : r < 2 ^ k) (hn : 1 ≤ n) :
    (((shell (2 ^ k * n + r)).sum (fun d => if d = 0 then 1 else 4 * d) : Nat) : Int)
      = (-4) * ((subm r).card * (Phi 0 n : Int))
        + (8 * 2 ^ k * (subm r).card) * (Phi 1 n : Int)
        + (if 1 ∈ arm (2 ^ k * n + r) then 1 else 0) := by
  have hγ : ∀ x : Nat, 2 ≤ x →
      ((if x = 0 then 1 else 4 * x : Nat) : Int)
        + ((if x - 1 = 0 then 1 else 4 * (x - 1) : Nat) : Int)
        = (Finset.range (1 + 1)).sum (fun i => (if i = 0 then (-4 : Int) else 8) * (x : Int) ^ i) := by
    intro x hx
    have hge : 1 ≤ x := by omega
    have hx0 : ¬ x = 0 := by omega
    have hx1 : ¬ x - 1 = 0 := by omega
    simp only [hx0, hx1, if_false]
    push_cast [hge]
    simp [Finset.sum_range_succ]
    ring
  have h1 : ((if 1 = 0 then 1 else 4 * 1 : Nat) : Int)
        + ((if 1 - 1 = 0 then 1 else 4 * (1 - 1) : Nat) : Int)
      = (Finset.range (1 + 1)).sum (fun i => (if i = 0 then (-4 : Int) else 8))
        + 1 := by
    simp [Finset.sum_range_succ]
  have hpos : 1 ≤ 2 ^ k * n + r := by
    have h2k : 0 < 2 ^ k := by positivity
    have hmm : 0 < 2 ^ k * n := Nat.mul_pos h2k (by omega)
    omega
  rw [Z_state (fun d => if d = 0 then 1 else 4 * d)
    (fun i => if i = 0 then (-4 : Int) else 8) 1 1 hγ h1 k n r hpos hn hr]
  rw [Finset.sum_range_succ, Finset.sum_range_one, W_zero k r (X n) hr,
    W_one k r (X n) hr]
  simp only [X]
  push_cast
  ring

#print axioms phi_z2vn_explicit

/- ---------- closed forms for the other degree-one rows ---------- -/

/-- **Z^2 Moore**, in closed form.** -/
theorem phi_z2moore_explicit (k r n : Nat) (hr : r < 2 ^ k) (hn : 1 ≤ n) :
    (((shell (2 ^ k * n + r)).sum (fun d => if d = 0 then 1 else 8 * d) : Nat) : Int)
      = -8 * ((subm r).card * (Phi 0 n : Int))
        + (16 * 2 ^ k * (subm r).card) * (Phi 1 n : Int)
        + 1 * (if 1 ∈ arm (2 ^ k * n + r) then 1 else 0) := by
  have hγ : ∀ x : Nat, 2 ≤ x →
      (((fun d => if d = 0 then 1 else 8 * d) x : Nat) : Int) + (((fun d => if d = 0 then 1 else 8 * d) (x - 1) : Nat) : Int)
        = (Finset.range (1 + 1)).sum
            (fun i => (if i = 0 then (-8 : Int) else 16) * (x : Int) ^ i) := by
    intro x hx
    have hge : 1 ≤ x := by omega
    have hx0 : ¬ x = 0 := by omega
    have hx1 : ¬ x - 1 = 0 := by omega
    simp only [hx0, hx1, if_false]
    push_cast [hge]
    simp [Finset.sum_range_succ]
    ring
  have h1 :
      ((((fun d => if d = 0 then 1 else 8 * d) 1 : Nat)) : Int) + ((((fun d => if d = 0 then 1 else 8 * d) (1 - 1 : Nat)) : Nat) : Int)
        = (Finset.range (1 + 1)).sum
            (fun i => (if i = 0 then (-8 : Int) else 16)) + 1 := by
    norm_num [Finset.sum_range_succ]
  have hpos : 1 ≤ 2 ^ k * n + r := by
    have h2k : 0 < 2 ^ k := by positivity
    have hmm : 0 < 2 ^ k * n := Nat.mul_pos h2k (by omega)
    omega
  rw [Z_state (fun d => if d = 0 then 1 else 8 * d) (fun i => if i = 0 then (-8 : Int) else 16) 1 1
    hγ h1 k n r hpos hn hr]
  rw [Finset.sum_range_succ, Finset.sum_range_one, W_zero k r (X n) hr,
    W_one k r (X n) hr]
  simp only [X]
  push_cast
  ring

#print axioms phi_z2moore_explicit

/-- **the triangular lattice**, in closed form.** -/
theorem phi_tri_explicit (k r n : Nat) (hr : r < 2 ^ k) (hn : 1 ≤ n) :
    (((shell (2 ^ k * n + r)).sum (fun d => if d = 0 then 1 else 6 * d) : Nat) : Int)
      = -6 * ((subm r).card * (Phi 0 n : Int))
        + (12 * 2 ^ k * (subm r).card) * (Phi 1 n : Int)
        + 1 * (if 1 ∈ arm (2 ^ k * n + r) then 1 else 0) := by
  have hγ : ∀ x : Nat, 2 ≤ x →
      (((fun d => if d = 0 then 1 else 6 * d) x : Nat) : Int) + (((fun d => if d = 0 then 1 else 6 * d) (x - 1) : Nat) : Int)
        = (Finset.range (1 + 1)).sum
            (fun i => (if i = 0 then (-6 : Int) else 12) * (x : Int) ^ i) := by
    intro x hx
    have hge : 1 ≤ x := by omega
    have hx0 : ¬ x = 0 := by omega
    have hx1 : ¬ x - 1 = 0 := by omega
    simp only [hx0, hx1, if_false]
    push_cast [hge]
    simp [Finset.sum_range_succ]
    ring
  have h1 :
      ((((fun d => if d = 0 then 1 else 6 * d) 1 : Nat)) : Int) + ((((fun d => if d = 0 then 1 else 6 * d) (1 - 1 : Nat)) : Nat) : Int)
        = (Finset.range (1 + 1)).sum
            (fun i => (if i = 0 then (-6 : Int) else 12)) + 1 := by
    norm_num [Finset.sum_range_succ]
  have hpos : 1 ≤ 2 ^ k * n + r := by
    have h2k : 0 < 2 ^ k := by positivity
    have hmm : 0 < 2 ^ k * n := Nat.mul_pos h2k (by omega)
    omega
  rw [Z_state (fun d => if d = 0 then 1 else 6 * d) (fun i => if i = 0 then (-6 : Int) else 12) 1 1
    hγ h1 k n r hpos hn hr]
  rw [Finset.sum_range_succ, Finset.sum_range_one, W_zero k r (X n) hr,
    W_one k r (X n) hr]
  simp only [X]
  push_cast
  ring

#print axioms phi_tri_explicit

/-- **the Z^2 quarter-plane von Neumann**, in closed form.** -/
theorem phi_z2orthvn_explicit (k r n : Nat) (hr : r < 2 ^ k) (hn : 1 ≤ n) :
    (((shell (2 ^ k * n + r)).sum (fun d => d + 1) : Nat) : Int)
      = 1 * ((subm r).card * (Phi 0 n : Int))
        + (2 * 2 ^ k * (subm r).card) * (Phi 1 n : Int)
        + 0 * (if 1 ∈ arm (2 ^ k * n + r) then 1 else 0) := by
  have hγ : ∀ x : Nat, 2 ≤ x →
      (((fun d => d + 1) x : Nat) : Int) + (((fun d => d + 1) (x - 1) : Nat) : Int)
        = (Finset.range (1 + 1)).sum
            (fun i => (if i = 0 then (1 : Int) else 2) * (x : Int) ^ i) := by
    intro x hx
    have hge : 1 ≤ x := by omega
    have hx0 : ¬ x = 0 := by omega
    have hx1 : ¬ x - 1 = 0 := by omega
    simp only [hx0, hx1, if_false]
    push_cast [hge]
    simp [Finset.sum_range_succ]
    ring
  have h1 :
      ((((fun d => d + 1) 1 : Nat)) : Int) + ((((fun d => d + 1) (1 - 1 : Nat)) : Nat) : Int)
        = (Finset.range (1 + 1)).sum
            (fun i => (if i = 0 then (1 : Int) else 2)) + 0 := by
    norm_num [Finset.sum_range_succ]
  have hpos : 1 ≤ 2 ^ k * n + r := by
    have h2k : 0 < 2 ^ k := by positivity
    have hmm : 0 < 2 ^ k * n := Nat.mul_pos h2k (by omega)
    omega
  rw [Z_state (fun d => d + 1) (fun i => if i = 0 then (1 : Int) else 2) 1 0
    hγ h1 k n r hpos hn hr]
  rw [Finset.sum_range_succ, Finset.sum_range_one, W_zero k r (X n) hr,
    W_one k r (X n) hr]
  simp only [X]
  push_cast
  ring

#print axioms phi_z2orthvn_explicit

/-- **the Z^2 quarter-plane Moore**, in closed form.** -/
theorem phi_z2orthmo_explicit (k r n : Nat) (hr : r < 2 ^ k) (hn : 1 ≤ n) :
    (((shell (2 ^ k * n + r)).sum (fun d => 2 * d + 1) : Nat) : Int)
      = 0 * ((subm r).card * (Phi 0 n : Int))
        + (4 * 2 ^ k * (subm r).card) * (Phi 1 n : Int)
        + 0 * (if 1 ∈ arm (2 ^ k * n + r) then 1 else 0) := by
  have hγ : ∀ x : Nat, 2 ≤ x →
      (((fun d => 2 * d + 1) x : Nat) : Int) + (((fun d => 2 * d + 1) (x - 1) : Nat) : Int)
        = (Finset.range (1 + 1)).sum
            (fun i => (if i = 0 then (0 : Int) else 4) * (x : Int) ^ i) := by
    intro x hx
    have hge : 1 ≤ x := by omega
    have hx0 : ¬ x = 0 := by omega
    have hx1 : ¬ x - 1 = 0 := by omega
    simp only [hx0, hx1, if_false]
    push_cast [hge]
    simp [Finset.sum_range_succ]
    ring
  have h1 :
      ((((fun d => 2 * d + 1) 1 : Nat)) : Int) + ((((fun d => 2 * d + 1) (1 - 1 : Nat)) : Nat) : Int)
        = (Finset.range (1 + 1)).sum
            (fun i => (if i = 0 then (0 : Int) else 4)) + 0 := by
    norm_num [Finset.sum_range_succ]
  have hpos : 1 ≤ 2 ^ k * n + r := by
    have h2k : 0 < 2 ^ k := by positivity
    have hmm : 0 < 2 ^ k * n := Nat.mul_pos h2k (by omega)
    omega
  rw [Z_state (fun d => 2 * d + 1) (fun i => if i = 0 then (0 : Int) else 4) 1 0
    hγ h1 k n r hpos hn hr]
  rw [Finset.sum_range_succ, Finset.sum_range_one, W_zero k r (X n) hr,
    W_one k r (X n) hr]
  simp only [X]
  push_cast
  ring

#print axioms phi_z2orthmo_explicit

end Rule129
end OEIS
