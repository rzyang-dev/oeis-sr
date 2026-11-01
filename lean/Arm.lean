import Census

namespace OEIS
namespace Rule129

/- ============================================================
   The two-step recursion: the whole counting table is 2-regular.

   The arm of time t is the set of the larger halves of the shell pairs,
   arm t = { t - 2m : m ⊆ r t }, so that  shell t = arm t ∪ (arm t - 1)
   (arm t lies in a single parity class).  Its digit recursions are

       arm (2u)   = 2 * arm u
       arm (2u+1) = (2 * arm u + 1) ∪ (2 * arm u - 1) ,

   and consequently, for ANY level-size function c,

       Z(2u)   = Σ_{m ⊆ r u} [ c(2(u-2m)) + c(2(u-2m)-1) ]
       Z(2u+1) = Σ_{m ⊆ r u} [ (c(2(u-2m)+1) + c(2(u-2m)))
                               + (c(2(u-2m)-1) + c(2(u-2m)-2)) ] .

   These recursions are geometry independent: the geometry enters only
   through c, so every row of the counting table is a 2-regular sequence
   with a linear representation obtained by iterating these two steps.
   ============================================================ -/

/-- **The arm.**  The larger halves of the shell pairs. -/
def arm (t : Nat) : Finset Nat := (subm (r t)).image (fun m => t - 2 * m)

/-- **r(2u) = 2 r(u).** -/
theorem r_two_mul (u : Nat) (hu : 1 ≤ u) : r (2 * u) = 2 * r u := by
  have e : 2 * u = (2 * u - 2) + 2 := by omega
  rw [e, r_add_two, show (2 * u - 2) + 2 = 2 * u from by omega, div_two_mul, mod_two_mul,
    Nat.add_zero]

#print axioms r_two_mul

/-- **r(2u+1) = 2 r(u) + 1.** -/
theorem r_two_mul_add_one (u : Nat) (hu : 1 ≤ u) : r (2 * u + 1) = 2 * r u + 1 := by
  have e : 2 * u + 1 = (2 * u - 1) + 2 := by omega
  rw [e, r_add_two, show (2 * u - 1) + 2 = 2 * u + 1 from by omega, div_two_mul_add_one,
    mod_two_mul_add_one]

#print axioms r_two_mul_add_one

/-- **The shell is the arm together with the arm shifted down by one.** -/
theorem shell_eq_arm (t : Nat) (ht : 1 ≤ t) :
    shell t = arm t ∪ (arm t).image (fun x => x - 1) := by
  rw [arm, shell_eq_image t ht, Finset.image_image]
  rfl

#print axioms shell_eq_arm

/-- **The shell sum splits into pairs.** -/
theorem shell_sum_pair (c : Nat → Nat) (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum c = (subm (r t)).sum (fun m => c (t - 2 * m) + c (t - 2 * m - 1)) := by
  rw [shell_sum_submask c t ht, Finset.sum_product]
  refine Finset.sum_congr rfl (fun m _ => ?_)
  rw [show (2 : Nat) = 1 + 1 from rfl, Finset.sum_range_succ, Finset.sum_range_one, Nat.sub_zero]

#print axioms shell_sum_pair

/-- **The even two-step recursion.** -/
theorem zero_count_two_mul (c : Nat → Nat) (u : Nat) (hu : 1 ≤ u) :
    (shell (2 * u)).sum c
      = (subm (r u)).sum (fun m => c (2 * (u - 2 * m)) + c (2 * (u - 2 * m) - 1)) := by
  have hb : 2 * r u + 1 ≤ u := two_mul_r_add_one_le u hu
  rw [shell_sum_pair c (2 * u) (by omega), r_two_mul u hu, subm_two_mul, Finset.sum_map]
  refine Finset.sum_congr rfl (fun m hm => ?_)
  obtain ⟨h1, -⟩ := mem_subm.mp hm
  have h2m : 2 * m ≤ u := by omega
  show c (2 * u - 2 * (2 * m)) + c (2 * u - 2 * (2 * m) - 1)
      = c (2 * (u - 2 * m)) + c (2 * (u - 2 * m) - 1)
  have e : 2 * (u - 2 * m) = 2 * u - 2 * (2 * m) := by omega
  rw [e]

#print axioms zero_count_two_mul

/-- **The odd two-step recursion.** -/
theorem zero_count_two_mul_add_one (c : Nat → Nat) (u : Nat) (hu : 1 ≤ u) :
    (shell (2 * u + 1)).sum c
      = (subm (r u)).sum (fun m =>
          (c (2 * (u - 2 * m) + 1) + c (2 * (u - 2 * m)))
            + (c (2 * (u - 2 * m) - 1) + c (2 * (u - 2 * m) - 2))) := by
  have hb : 2 * r u + 1 ≤ u := two_mul_r_add_one_le u hu
  rw [shell_sum_pair c (2 * u + 1) (by omega), r_two_mul_add_one u hu, subm_two_mul_add_one,
    Finset.sum_union (disjoint_subm_doublings (r u)), Finset.sum_map, Finset.sum_map,
    ← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl (fun m hm => ?_)
  obtain ⟨h1, -⟩ := mem_subm.mp hm
  have h2m : 2 * m ≤ u := by omega
  simp only [emb2_apply, emb2p1_apply]
  show (c (2 * u + 1 - 2 * (2 * m)) + c (2 * u + 1 - 2 * (2 * m) - 1))
      + (c (2 * u + 1 - 2 * (2 * m + 1)) + c (2 * u + 1 - 2 * (2 * m + 1) - 1))
      = (c (2 * (u - 2 * m) + 1) + c (2 * (u - 2 * m)))
        + (c (2 * (u - 2 * m) - 1) + c (2 * (u - 2 * m) - 2))
  have e1 : 2 * (u - 2 * m) + 1 = 2 * u + 1 - 2 * (2 * m) := by omega
  have e2 : 2 * (u - 2 * m) = 2 * u + 1 - 2 * (2 * m) - 1 := by omega
  have e3 : 2 * (u - 2 * m) - 1 = 2 * u + 1 - 2 * (2 * m + 1) := by omega
  have e4 : 2 * (u - 2 * m) - 2 = 2 * u + 1 - 2 * (2 * m + 1) - 1 := by omega
  rw [e1, e3, e4, e2]

#print axioms zero_count_two_mul_add_one


/- ---------- the arm as a sum, and the arm moments ---------- -/

/-- The submask map m ↦ t - 2m is injective on the submasks. -/
theorem sub_inj (t : Nat) (ht : 1 ≤ t) :
    Set.InjOn (fun m => t - 2 * m) ↑(subm (r t)) := by
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  intro a ha b hb' hab
  have hab' : t - 2 * a = t - 2 * b := hab
  have ha1 : a ≤ r t := (mem_subm.mp ha).1
  have hb1 : b ≤ r t := (mem_subm.mp hb').1
  omega

#print axioms sub_inj

/-- The sum over the arm is a sum over the submasks. -/
theorem sum_arm (c : Nat → Nat) (t : Nat) (ht : 1 ≤ t) :
    (arm t).sum c = (subm (r t)).sum (fun m => c (t - 2 * m)) := by
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  rw [arm, Finset.sum_image (sub_inj t ht)]

#print axioms sum_arm

/-- **The zero count is the arm moment of the shifted sum c x + c (x-1).** -/
theorem shell_sum_arm (c : Nat → Nat) (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum c = (arm t).sum (fun x => c x + c (x - 1)) := by
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  have hR : (arm t).sum (fun x => c x + c (x - 1))
      = (subm (r t)).sum (fun m => c (t - 2 * m) + c (t - 2 * m - 1)) := by
    rw [arm, Finset.sum_image (sub_inj t ht)]
  rw [shell_sum_pair c t ht, hR]

#print axioms shell_sum_arm

/-- **The k-th arm moment.** -/
def Phi (k t : Nat) : Nat := (subm (r t)).sum (fun m => (t - 2 * m) ^ k)

/-- The arm moment is a sum over the arm. -/
theorem Phi_eq_arm (k t : Nat) (ht : 1 ≤ t) :
    Phi k t = (arm t).sum (fun x => x ^ k) := by
  rw [Phi, arm, Finset.sum_image (sub_inj t ht)]

#print axioms Phi_eq_arm

/-- **The even step is diagonal.**  Phi_k(2u) = 2^k Phi_k(u). -/
theorem Phi_two_mul (k u : Nat) (hu : 1 ≤ u) : Phi k (2 * u) = 2 ^ k * Phi k u := by
  have hb : 2 * r u + 1 ≤ u := two_mul_r_add_one_le u hu
  rw [Phi, Phi, r_two_mul u hu, subm_two_mul, Finset.sum_map, Finset.mul_sum]
  refine Finset.sum_congr rfl (fun m hm => ?_)
  obtain ⟨h1, -⟩ := mem_subm.mp hm
  have h2m : 2 * m ≤ u := by omega
  show (2 * u - 2 * (2 * m)) ^ k = 2 ^ k * (u - 2 * m) ^ k
  have e : 2 * u - 2 * (2 * m) = 2 * (u - 2 * m) := by omega
  rw [e, mul_pow]

#print axioms Phi_two_mul

/-- The zeroth arm moment is the number of submasks. -/
theorem Phi_zero (t : Nat) : Phi 0 t = (subm (r t)).card := by
  rw [Phi]
  simp

#print axioms Phi_zero



theorem neg_one_pow_mod (m : Nat) :
    (-1 : Int) ^ m = if m % 2 = 0 then 1 else -1 := by
  induction m with
  | zero => simp
  | succ m ih =>
    have hlt := Nat.mod_lt m (by decide : 0 < 2)
    rw [pow_succ, ih]
    by_cases h : m % 2 = 0
    · rw [if_pos h, if_neg (by omega : ¬ (m + 1) % 2 = 0)]
      ring
    · rw [if_neg h, if_pos (by omega : (m + 1) % 2 = 0)]
      ring

/-- Twice the same-parity part of the binomial expansion of (2z+1)^k. -/
theorem pow_pair (k : Nat) (z : Int) :
    (2 * z + 1) ^ k + (2 * z + -1) ^ k
      = 2 * ((Finset.range (k + 1)).sum (fun i =>
          if i % 2 = k % 2 then (k.choose i : Int) * (2 * z) ^ i else 0)) := by
  have h1 : (2 * z + 1) ^ k
      = (Finset.range (k + 1)).sum
          (fun i => (2 * z) ^ i * (1 : Int) ^ (k - i) * (k.choose i : Int)) :=
    add_pow (2 * z) 1 k
  have h2 : (2 * z + -1) ^ k
      = (Finset.range (k + 1)).sum
          (fun i => (2 * z) ^ i * (-1 : Int) ^ (k - i) * (k.choose i : Int)) :=
    add_pow (2 * z) (-1) k
  rw [h1, h2, ← Finset.sum_add_distrib, Finset.mul_sum]
  refine Finset.sum_congr rfl (fun i hi => ?_)
  rw [Finset.mem_range] at hi
  have hlt := Nat.mod_lt i (by decide : 0 < 2)
  have hlt2 := Nat.mod_lt k (by decide : 0 < 2)
  by_cases hpar : i % 2 = k % 2
  · have hki : (k - i) % 2 = 0 := by omega
    rw [if_pos hpar, neg_one_pow_mod, if_pos hki, one_pow]
    ring
  · have hki : (k - i) % 2 = 1 := by omega
    rw [if_neg hpar, neg_one_pow_mod, if_neg (by omega : ¬ (k - i) % 2 = 0), one_pow]
    ring

#print axioms pow_pair

/-- The arm moment at an odd time, as a sum of the two shifted powers. -/
theorem Phi_two_mul_add_one_nat (k u : Nat) (hu : 1 ≤ u) :
    Phi k (2 * u + 1)
      = (subm (r u)).sum (fun m => (2 * (u - 2 * m) + 1) ^ k + (2 * (u - 2 * m) - 1) ^ k) := by
  have hb : 2 * r u + 1 ≤ u := two_mul_r_add_one_le u hu
  rw [Phi, r_two_mul_add_one u hu, subm_two_mul_add_one,
      Finset.sum_union (disjoint_subm_doublings (r u)), Finset.sum_map, Finset.sum_map,
      ← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl (fun m hm => ?_)
  obtain ⟨h1, -⟩ := mem_subm.mp hm
  have h2m : 2 * m ≤ u := by omega
  simp only [emb2_apply, emb2p1_apply]
  show (2 * u + 1 - 2 * (2 * m)) ^ k + (2 * u + 1 - 2 * (2 * m + 1)) ^ k
      = (2 * (u - 2 * m) + 1) ^ k + (2 * (u - 2 * m) - 1) ^ k
  have e1 : 2 * u + 1 - 2 * (2 * m) = 2 * (u - 2 * m) + 1 := by omega
  have e2 : 2 * u + 1 - 2 * (2 * m + 1) = 2 * (u - 2 * m) - 1 := by omega
  rw [e1, e2]

#print axioms Phi_two_mul_add_one_nat

/-- **The odd step: only same-parity lower moments appear.** -/
theorem Phi_two_mul_add_one (k u : Nat) (hu : 1 ≤ u) :
    (Phi k (2 * u + 1) : Int)
      = (Finset.range (k + 1)).sum (fun i =>
          if i % 2 = k % 2 then (k.choose i : Int) * 2 ^ (i + 1) * (Phi i u : Int) else 0) := by
  have hb : 2 * r u + 1 ≤ u := two_mul_r_add_one_le u hu
  have hcast : ∀ m ∈ subm (r u),
      (((2 * (u - 2 * m) + 1) ^ k + (2 * (u - 2 * m) - 1) ^ k : Nat) : Int)
      = (Finset.range (k + 1)).sum (fun i =>
          if i % 2 = k % 2 then
            (k.choose i : Int) * 2 ^ (i + 1) * (((u - 2 * m : Nat)) : Int) ^ i else 0) := by
    intro m hm
    obtain ⟨h1, -⟩ := mem_subm.mp hm
    have h2m : 2 * m ≤ u := by omega
    have hy : 1 ≤ u - 2 * m := by omega
    have h2y : 1 ≤ 2 * (u - 2 * m) := by omega
    have hc : (((2 * (u - 2 * m) + 1) ^ k + (2 * (u - 2 * m) - 1) ^ k : Nat) : Int)
        = (2 * (((u - 2 * m : Nat)) : Int) + 1) ^ k
          + (2 * (((u - 2 * m : Nat)) : Int) + -1) ^ k := by
      push_cast [h2m, h2y]
      ring
    rw [hc, pow_pair k (((u - 2 * m : Nat)) : Int), Finset.mul_sum]
    refine Finset.sum_congr rfl (fun i hi => ?_)
    by_cases hp : i % 2 = k % 2
    · rw [if_pos hp, if_pos hp, mul_pow]
      ring
    · rw [if_neg hp, if_neg hp]
      ring
  rw [Phi_two_mul_add_one_nat k u hu, Nat.cast_sum,
    Finset.sum_congr rfl hcast, Finset.sum_comm]
  refine Finset.sum_congr rfl (fun i hi => ?_)
  by_cases hp : i % 2 = k % 2
  · rw [if_pos hp]
    simp only [if_pos hp, ← Nat.cast_pow]
    rw [← Finset.mul_sum, ← Nat.cast_sum]
    rfl
  · rw [if_neg hp]
    simp only [if_neg hp, Finset.sum_const_zero]

#print axioms Phi_two_mul_add_one


/- ---------- the zero count as a functional of the arm moments ---------- -/

/-- Every element of the arm is positive. -/
theorem arm_pos (t : Nat) (ht : 1 ≤ t) : ∀ x ∈ arm t, 1 ≤ x := by
  intro x hx
  rw [arm, Finset.mem_image] at hx
  obtain ⟨m, hm, rfl⟩ := hx
  obtain ⟨h1, -⟩ := mem_subm.mp hm
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  omega

#print axioms arm_pos

/-- **The zero count is a linear functional of the arm moments.**
    If the shifted sum c x + c (x-1) is a polynomial of degree at most j on the
    positive integers, with coefficients gamma, then the zero count is the same
    combination of Phi_0, ..., Phi_j. -/
theorem shell_sum_of_poly (c : Nat → Nat) (γ : Nat → Int) (j t : Nat) (ht : 1 ≤ t)
    (hγ : ∀ x : Nat, 1 ≤ x →
      (c x : Int) + (c (x - 1) : Int)
        = (Finset.range (j + 1)).sum (fun i => γ i * (x : Int) ^ i)) :
    (((shell t).sum c : Nat) : Int)
      = (Finset.range (j + 1)).sum (fun i => γ i * (Phi i t : Int)) := by
  rw [shell_sum_arm c t ht, Nat.cast_sum]
  have h1 : ∀ x ∈ arm t, ((c x + c (x - 1) : Nat) : Int)
      = (Finset.range (j + 1)).sum (fun i => γ i * (x : Int) ^ i) := by
    intro x hx
    rw [Nat.cast_add]
    exact hγ x (arm_pos t ht x hx)
  rw [Finset.sum_congr rfl h1, Finset.sum_comm]
  refine Finset.sum_congr rfl (fun i hi => ?_)
  rw [← Finset.mul_sum]
  simp only [← Nat.cast_pow]
  rw [← Nat.cast_sum, ← Phi_eq_arm i t ht]

#print axioms shell_sum_of_poly


/-- **0 is never in the arm.** -/
theorem zero_not_mem_arm (t : Nat) (ht : 1 ≤ t) : 0 ∉ arm t := by
  intro h
  rw [arm, Finset.mem_image] at h
  obtain ⟨m, hm, h0⟩ := h
  obtain ⟨h1, -⟩ := mem_subm.mp hm
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  omega

#print axioms zero_not_mem_arm

/-- **The centre indicator is the indicator of 1 in the arm.**
    So the extra dimension of the linear representation is exactly
    the automatic sequence [1 in arm t]. -/
theorem zero_mem_shell_iff (t : Nat) (ht : 1 ≤ t) : 0 ∈ shell t ↔ 1 ∈ arm t := by
  constructor
  · intro h
    rw [shell_eq_arm t ht, Finset.mem_union, Finset.mem_image] at h
    rcases h with h | ⟨x, hx, hx1⟩
    · exact absurd h (zero_not_mem_arm t ht)
    · have hxpos : 1 ≤ x := arm_pos t ht x hx
      have hx1' : x = 1 := by omega
      rw [← hx1']
      exact hx
  · intro h
    rw [shell_eq_arm t ht, Finset.mem_union]
    exact Or.inr (Finset.mem_image.mpr ⟨1, h, by omega⟩)

#print axioms zero_mem_shell_iff

end Rule129
end OEIS