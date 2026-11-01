import Arm

namespace OEIS
namespace Rule129

/-- **The centre is never at an even time.** -/
theorem zero_not_mem_shell_two_mul (u : Nat) (hu : 1 ≤ u) : 0 ∉ shell (2 * u) := by
  rw [mem_shell]
  intro h
  obtain ⟨-, hsub⟩ := h
  have h2 : r (2 * u) = 2 * r u := r_two_mul u hu
  rw [h2, Nat.sub_zero, div_two_mul] at hsub
  have hle : u ≤ 2 * r u := sub_le hsub
  have hb : 2 * r u + 1 ≤ u := two_mul_r_add_one_le u hu
  omega

#print axioms zero_not_mem_shell_two_mul

/-- **The centre at an odd time.**  epsilon(2u+1) = epsilon(u). -/
theorem zero_mem_shell_two_mul_add_one (u : Nat) (hu : 1 ≤ u) :
    0 ∈ shell (2 * u + 1) ↔ 0 ∈ shell u := by
  rw [mem_shell, mem_shell]
  have h2 : r (2 * u + 1) = 2 * r u + 1 := r_two_mul_add_one u hu
  rw [h2, Nat.sub_zero, div_two_mul_add_one]
  constructor
  · rintro ⟨-, hsub⟩
    exact ⟨by omega, (sub_two_mul_add_one (e := u) (u := r u)).mp hsub⟩
  · rintro ⟨-, hsub⟩
    exact ⟨by omega, (sub_two_mul_add_one (e := u) (u := r u)).mpr hsub⟩

#print axioms zero_mem_shell_two_mul_add_one

/-- **The refined decomposition theorem.**  The polynomial identity is only
    needed for x >= 2; the point x = 1 contributes the constant delta. -/
theorem shell_sum_of_poly_correction (c : Nat → Nat) (γ : Nat → Int) (j : Nat) (δ : Int)
    (t : Nat) (ht : 1 ≤ t)
    (hγ : ∀ x : Nat, 2 ≤ x →
      (c x : Int) + (c (x - 1) : Int)
        = (Finset.range (j + 1)).sum (fun i => γ i * (x : Int) ^ i))
    (h1 : (c 1 : Int) + (c 0 : Int) = (Finset.range (j + 1)).sum (fun i => γ i) + δ) :
    (((shell t).sum c : Nat) : Int)
      = (Finset.range (j + 1)).sum (fun i => γ i * (Phi i t : Int))
        + δ * (if 1 ∈ arm t then 1 else 0) := by
  rw [shell_sum_arm c t ht, Nat.cast_sum]
  have hpt : ∀ x ∈ arm t, ((c x + c (x - 1) : Nat) : Int)
      = (Finset.range (j + 1)).sum (fun i => γ i * (x : Int) ^ i)
        + δ * (if x = 1 then 1 else 0) := by
    intro x hx
    have hpos : 1 ≤ x := arm_pos t ht x hx
    rw [Nat.cast_add]
    by_cases hx1 : x = 1
    · subst hx1
      rw [if_pos rfl, show (1 : Nat) - 1 = 0 from rfl]
      simpa using h1
    · rw [if_neg hx1]
      have hx2 : 2 ≤ x := by omega
      simpa using hγ x hx2
  rw [Finset.sum_congr rfl hpt, Finset.sum_add_distrib]
  congr 1
  · rw [Finset.sum_comm]
    refine Finset.sum_congr rfl (fun i hi => ?_)
    rw [← Finset.mul_sum]
    simp only [← Nat.cast_pow]
    rw [← Nat.cast_sum, ← Phi_eq_arm i t ht]
  · rw [← Finset.mul_sum]
    congr 1
    rw [Finset.sum_ite_eq']

#print axioms shell_sum_of_poly_correction









/- ---------- the rows of the table, written through arm moments ---------- -/

-- Each theorem says: the zero count is the integer combination of the arm
-- moments given by gamma, plus the centre correction delta * [1 in arm t].

/-- **1-D line (level sizes 1, 2, 2, 2, ...)** through the arm moments. -/
theorem phi_line (t : Nat) (ht : 1 ≤ t) :
    (((shell t).sum (fun d => if d = 0 then 1 else 2) : Nat) : Int)
      = (Finset.range 1).sum (fun i => (fun i => (4 : Int)) i * (Phi i t : Int))
        + (-1 : Int) * (if 1 ∈ arm t then 1 else 0) :=
  shell_sum_of_poly_correction (fun d => if d = 0 then 1 else 2) (fun i => (4 : Int)) 0 (-1 : Int) t ht
    (by
      intro x hx
      have hge : 1 ≤ x := by omega
      have hx0 : ¬ x = 0 := by omega
      have hx1 : ¬ x - 1 = 0 := by omega
      simp only [hx0, hx1, if_false]
      push_cast [hge]
      simp [Finset.sum_range_succ])
    (by norm_num [Finset.sum_range_succ])

#print axioms phi_line

/-- **1-D ray (all levels 1)** through the arm moments. -/
theorem phi_ray (t : Nat) (ht : 1 ≤ t) :
    (((shell t).sum (fun d => if d = 0 then 1 else 1) : Nat) : Int)
      = (Finset.range 1).sum (fun i => (fun i => (2 : Int)) i * (Phi i t : Int))
        + (0 : Int) * (if 1 ∈ arm t then 1 else 0) :=
  shell_sum_of_poly_correction (fun d => if d = 0 then 1 else 1) (fun i => (2 : Int)) 0 (0 : Int) t ht
    (by
      intro x hx
      have hge : 1 ≤ x := by omega
      have hx0 : ¬ x = 0 := by omega
      have hx1 : ¬ x - 1 = 0 := by omega
      simp only [hx0, hx1, if_false]
      push_cast [hge]
      simp [Finset.sum_range_succ])
    (by norm_num [Finset.sum_range_succ])

#print axioms phi_ray

/-- **Z^2 von Neumann (A169699)** through the arm moments. -/
theorem phi_z2vn (t : Nat) (ht : 1 ≤ t) :
    (((shell t).sum (fun d => if d = 0 then 1 else 4 * d) : Nat) : Int)
      = (Finset.range 2).sum (fun i => (fun i => (if i = 0 then (-4 : Int) else (8 : Int))) i * (Phi i t : Int))
        + (1 : Int) * (if 1 ∈ arm t then 1 else 0) :=
  shell_sum_of_poly_correction (fun d => if d = 0 then 1 else 4 * d) (fun i => (if i = 0 then (-4 : Int) else (8 : Int))) 1 (1 : Int) t ht
    (by
      intro x hx
      have hge : 1 ≤ x := by omega
      have hx0 : ¬ x = 0 := by omega
      have hx1 : ¬ x - 1 = 0 := by omega
      simp only [hx0, hx1, if_false]
      push_cast [hge]
      simp [Finset.sum_range_succ]
      ring)
    (by norm_num [Finset.sum_range_succ])

#print axioms phi_z2vn

/-- **Z^2 Moore (9-neighbourhood)** through the arm moments. -/
theorem phi_z2moore (t : Nat) (ht : 1 ≤ t) :
    (((shell t).sum (fun d => if d = 0 then 1 else 8 * d) : Nat) : Int)
      = (Finset.range 2).sum (fun i => (fun i => (if i = 0 then (-8 : Int) else (16 : Int))) i * (Phi i t : Int))
        + (1 : Int) * (if 1 ∈ arm t then 1 else 0) :=
  shell_sum_of_poly_correction (fun d => if d = 0 then 1 else 8 * d) (fun i => (if i = 0 then (-8 : Int) else (16 : Int))) 1 (1 : Int) t ht
    (by
      intro x hx
      have hge : 1 ≤ x := by omega
      have hx0 : ¬ x = 0 := by omega
      have hx1 : ¬ x - 1 = 0 := by omega
      simp only [hx0, hx1, if_false]
      push_cast [hge]
      simp [Finset.sum_range_succ]
      ring)
    (by norm_num [Finset.sum_range_succ])

#print axioms phi_z2moore

/-- **triangular lattice** through the arm moments. -/
theorem phi_tri (t : Nat) (ht : 1 ≤ t) :
    (((shell t).sum (fun d => if d = 0 then 1 else 6 * d) : Nat) : Int)
      = (Finset.range 2).sum (fun i => (fun i => (if i = 0 then (-6 : Int) else (12 : Int))) i * (Phi i t : Int))
        + (1 : Int) * (if 1 ∈ arm t then 1 else 0) :=
  shell_sum_of_poly_correction (fun d => if d = 0 then 1 else 6 * d) (fun i => (if i = 0 then (-6 : Int) else (12 : Int))) 1 (1 : Int) t ht
    (by
      intro x hx
      have hge : 1 ≤ x := by omega
      have hx0 : ¬ x = 0 := by omega
      have hx1 : ¬ x - 1 = 0 := by omega
      simp only [hx0, hx1, if_false]
      push_cast [hge]
      simp [Finset.sum_range_succ]
      ring)
    (by norm_num [Finset.sum_range_succ])

#print axioms phi_tri

/-- **Z^3 von Neumann** through the arm moments. -/
theorem phi_z3vn (t : Nat) (ht : 1 ≤ t) :
    (((shell t).sum (fun d => if d = 0 then 1 else 4 * d * d + 2) : Nat) : Int)
      = (Finset.range 3).sum (fun i => (fun i => (if i = 0 then (8 : Int) else (if i = 1 then (-8 : Int) else (8 : Int)))) i * (Phi i t : Int))
        + (-1 : Int) * (if 1 ∈ arm t then 1 else 0) :=
  shell_sum_of_poly_correction (fun d => if d = 0 then 1 else 4 * d * d + 2) (fun i => (if i = 0 then (8 : Int) else (if i = 1 then (-8 : Int) else (8 : Int)))) 2 (-1 : Int) t ht
    (by
      intro x hx
      have hge : 1 ≤ x := by omega
      have hx0 : ¬ x = 0 := by omega
      have hx1 : ¬ x - 1 = 0 := by omega
      simp only [hx0, hx1, if_false]
      push_cast [hge]
      simp [Finset.sum_range_succ]
      ring)
    (by norm_num [Finset.sum_range_succ])

#print axioms phi_z3vn

/-- **Z^3 Moore** through the arm moments. -/
theorem phi_z3moore (t : Nat) (ht : 1 ≤ t) :
    (((shell t).sum (fun d => if d = 0 then 1 else 24 * d * d + 2) : Nat) : Int)
      = (Finset.range 3).sum (fun i => (fun i => (if i = 0 then (28 : Int) else (if i = 1 then (-48 : Int) else (48 : Int)))) i * (Phi i t : Int))
        + (-1 : Int) * (if 1 ∈ arm t then 1 else 0) :=
  shell_sum_of_poly_correction (fun d => if d = 0 then 1 else 24 * d * d + 2) (fun i => (if i = 0 then (28 : Int) else (if i = 1 then (-48 : Int) else (48 : Int)))) 2 (-1 : Int) t ht
    (by
      intro x hx
      have hge : 1 ≤ x := by omega
      have hx0 : ¬ x = 0 := by omega
      have hx1 : ¬ x - 1 = 0 := by omega
      simp only [hx0, hx1, if_false]
      push_cast [hge]
      simp [Finset.sum_range_succ]
      ring)
    (by norm_num [Finset.sum_range_succ])

#print axioms phi_z3moore

/-- **Z^4 Moore** through the arm moments. -/
theorem phi_z4moore (t : Nat) (ht : 1 ≤ t) :
    (((shell t).sum (fun d => if d = 0 then 1 else 64 * d^3 + 16 * d) : Nat) : Int)
      = (Finset.range 4).sum (fun i => (fun i => (if i = 0 then (-80 : Int) else (if i = 1 then (224 : Int) else (if i = 2 then (-192 : Int) else (128 : Int))))) i * (Phi i t : Int))
        + (1 : Int) * (if 1 ∈ arm t then 1 else 0) :=
  shell_sum_of_poly_correction (fun d => if d = 0 then 1 else 64 * d^3 + 16 * d) (fun i => (if i = 0 then (-80 : Int) else (if i = 1 then (224 : Int) else (if i = 2 then (-192 : Int) else (128 : Int))))) 3 (1 : Int) t ht
    (by
      intro x hx
      have hge : 1 ≤ x := by omega
      have hx0 : ¬ x = 0 := by omega
      have hx1 : ¬ x - 1 = 0 := by omega
      simp only [hx0, hx1, if_false]
      push_cast [hge]
      simp [Finset.sum_range_succ]
      ring)
    (by norm_num [Finset.sum_range_succ])

#print axioms phi_z4moore

/-- **Z^4 von Neumann, scaled by 3** through the arm moments. -/
theorem phi_z4vn (t : Nat) (ht : 1 ≤ t) :
    (((shell t).sum (fun d => if d = 0 then 3 else 8 * d * (d * d + 2)) : Nat) : Int)
      = (Finset.range 4).sum (fun i => (fun i => (if i = 0 then (-24 : Int) else (if i = 1 then (56 : Int) else (if i = 2 then (-24 : Int) else (16 : Int))))) i * (Phi i t : Int))
        + (3 : Int) * (if 1 ∈ arm t then 1 else 0) :=
  shell_sum_of_poly_correction (fun d => if d = 0 then 3 else 8 * d * (d * d + 2)) (fun i => (if i = 0 then (-24 : Int) else (if i = 1 then (56 : Int) else (if i = 2 then (-24 : Int) else (16 : Int))))) 3 (3 : Int) t ht
    (by
      intro x hx
      have hge : 1 ≤ x := by omega
      have hx0 : ¬ x = 0 := by omega
      have hx1 : ¬ x - 1 = 0 := by omega
      simp only [hx0, hx1, if_false]
      push_cast [hge]
      simp [Finset.sum_range_succ]
      ring)
    (by norm_num [Finset.sum_range_succ])

#print axioms phi_z4vn

/-- **Z^5 Moore** through the arm moments. -/
theorem phi_z5moore (t : Nat) (ht : 1 ≤ t) :
    (((shell t).sum (fun d => if d = 0 then 1 else 160 * d^4 + 80 * d * d + 2) : Nat) : Int)
      = (Finset.range 5).sum (fun i => (fun i => (if i = 0 then (244 : Int) else (if i = 1 then (-800 : Int) else (if i = 2 then (1120 : Int) else (if i = 3 then (-640 : Int) else (320 : Int)))))) i * (Phi i t : Int))
        + (-1 : Int) * (if 1 ∈ arm t then 1 else 0) :=
  shell_sum_of_poly_correction (fun d => if d = 0 then 1 else 160 * d^4 + 80 * d * d + 2) (fun i => (if i = 0 then (244 : Int) else (if i = 1 then (-800 : Int) else (if i = 2 then (1120 : Int) else (if i = 3 then (-640 : Int) else (320 : Int)))))) 4 (-1 : Int) t ht
    (by
      intro x hx
      have hge : 1 ≤ x := by omega
      have hx0 : ¬ x = 0 := by omega
      have hx1 : ¬ x - 1 = 0 := by omega
      simp only [hx0, hx1, if_false]
      push_cast [hge]
      simp [Finset.sum_range_succ]
      ring)
    (by norm_num [Finset.sum_range_succ])

#print axioms phi_z5moore

/-- **Z^5 von Neumann, scaled by 3** through the arm moments. -/
theorem phi_z5vn (t : Nat) (ht : 1 ≤ t) :
    (((shell t).sum (fun d => if d = 0 then 3 else 4 * d^4 + 20 * d * d + 6) : Nat) : Int)
      = (Finset.range 5).sum (fun i => (fun i => (if i = 0 then (36 : Int) else (if i = 1 then (-56 : Int) else (if i = 2 then (64 : Int) else (if i = 3 then (-16 : Int) else (8 : Int)))))) i * (Phi i t : Int))
        + (-3 : Int) * (if 1 ∈ arm t then 1 else 0) :=
  shell_sum_of_poly_correction (fun d => if d = 0 then 3 else 4 * d^4 + 20 * d * d + 6) (fun i => (if i = 0 then (36 : Int) else (if i = 1 then (-56 : Int) else (if i = 2 then (64 : Int) else (if i = 3 then (-16 : Int) else (8 : Int)))))) 4 (-3 : Int) t ht
    (by
      intro x hx
      have hge : 1 ≤ x := by omega
      have hx0 : ¬ x = 0 := by omega
      have hx1 : ¬ x - 1 = 0 := by omega
      simp only [hx0, hx1, if_false]
      push_cast [hge]
      simp [Finset.sum_range_succ]
      ring)
    (by norm_num [Finset.sum_range_succ])

#print axioms phi_z5vn

/-- **Z^2 quarter-plane von Neumann (level size d+1)** through the arm moments. -/
theorem phi_z2orthvn (t : Nat) (ht : 1 ≤ t) :
    (((shell t).sum (fun d => d + 1) : Nat) : Int)
      = (Finset.range 2).sum (fun i => (fun i => (if i = 0 then (1 : Int) else (2 : Int))) i * (Phi i t : Int)) :=
  shell_sum_of_poly (fun d => d + 1) (fun i => (if i = 0 then (1 : Int) else (2 : Int))) 1 t ht
    (by
      intro x hx
      have hge : 1 ≤ x := by omega
      push_cast [hge]
      simp [Finset.sum_range_succ]
      ring)

#print axioms phi_z2orthvn

/-- **Z^2 quarter-plane Moore (level size 2d+1)** through the arm moments. -/
theorem phi_z2orthmo (t : Nat) (ht : 1 ≤ t) :
    (((shell t).sum (fun d => 2 * d + 1) : Nat) : Int)
      = (Finset.range 2).sum (fun i => (fun i => (if i = 0 then (0 : Int) else (4 : Int))) i * (Phi i t : Int)) :=
  shell_sum_of_poly (fun d => 2 * d + 1) (fun i => (if i = 0 then (0 : Int) else (4 : Int))) 1 t ht
    (by
      intro x hx
      have hge : 1 ≤ x := by omega
      push_cast [hge]
      simp [Finset.sum_range_succ]
      ring)

#print axioms phi_z2orthmo

end Rule129
end OEIS