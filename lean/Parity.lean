import Shells

namespace OEIS
namespace Rule129

/- ============================================================
   The alternating kernel.

   The shell is a disjoint union of the consecutive pairs
   {t - 2m, t - 2m - 1}, so it always contains as many even levels
   as odd ones.  Hence the zero counts cannot see the direction
   c_d |-> c_d + lambda * (-1)^d.
   ============================================================ -/

/-- The first arm of the shell has the parity of t. -/
theorem sub_two_mul_mod (t m : Nat) (h : 2 * m ≤ t) : (t - 2 * m) % 2 = t % 2 := by
  have hdm := Nat.div_add_mod t 2
  have hlt := Nat.mod_lt t (by decide : 0 < 2)
  interval_cases ht : t % 2
  · have he : t - 2 * m = 2 * (t / 2 - m) := by omega
    rw [he, mod_two_mul]
  · have he : t - 2 * m = 2 * (t / 2 - m) + 1 := by omega
    rw [he, mod_two_mul_add_one]

#print axioms sub_two_mul_mod

/-- The second arm has the opposite parity. -/
theorem sub_two_mul_one_mod (t m : Nat) (h : 2 * m + 1 ≤ t) :
    (t - 2 * m - 1) % 2 = 1 - t % 2 := by
  have hdm := Nat.div_add_mod t 2
  have hlt := Nat.mod_lt t (by decide : 0 < 2)
  interval_cases ht : t % 2
  · have he : t - 2 * m - 1 = 2 * (t / 2 - m - 1) + 1 := by omega
    rw [he, mod_two_mul_add_one]
  · have he : t - 2 * m - 1 = 2 * (t / 2 - m) := by omega
    rw [he, mod_two_mul]

#print axioms sub_two_mul_one_mod

/-- The levels of the shell with the parity of t are exactly the first arm. -/
theorem shell_filter_parity_card (t : Nat) (ht : 1 ≤ t) :
    (subm (r t)).card = ((shell t).filter (fun d => d % 2 = t % 2)).card := by
  have hb : 2 * r t ≤ t := two_mul_r_le t ht
  have hb1 : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  have hlt := Nat.mod_lt t (by decide : 0 < 2)
  refine Finset.card_bij (fun m _ => t - 2 * m) ?_ ?_ ?_
  · intro m hm
    rw [mem_subm] at hm
    obtain ⟨hm1, hm2⟩ := hm
    rw [Finset.mem_filter]
    refine ⟨?_, ?_⟩
    · rw [mem_shell]
      refine ⟨by omega, ?_⟩
      rw [show t - (t - 2 * m) = 2 * m from by omega, div_two_mul]
      exact hm2
    · exact sub_two_mul_mod t m (by omega)
  · intro m1 hm1 m2 hm2 heq
    rw [mem_subm] at hm1 hm2
    omega
  · intro d hd
    rw [Finset.mem_filter] at hd
    obtain ⟨hshell, hpar⟩ := hd
    rw [shell_eq_image t ht] at hshell
    rcases Finset.mem_union.mp hshell with him | him
    · obtain ⟨m, hm, hmc⟩ := Finset.mem_image.mp him
      exact ⟨m, hm, hmc⟩
    · obtain ⟨m, hm, hmc⟩ := Finset.mem_image.mp him
      exfalso
      rw [mem_subm] at hm
      rw [← hmc] at hpar
      rw [sub_two_mul_one_mod t m (by omega)] at hpar
      omega

#print axioms shell_filter_parity_card

/-- **The alternating kernel.**  Every shell has as many even levels as odd ones. -/
theorem shell_even_odd_count (t : Nat) (ht : 1 ≤ t) :
    ((shell t).filter (fun d => d % 2 = 0)).card
      = ((shell t).filter (fun d => d % 2 = 1)).card := by
  have h1 := shell_filter_parity_card t ht
  have hcard : (shell t).card = 2 * (subm (r t)).card := card_shell t ht
  have hlt := Nat.mod_lt t (by decide : 0 < 2)
  have hdisj : Disjoint ((shell t).filter (fun d => d % 2 = 0))
      ((shell t).filter (fun d => d % 2 = 1)) := by
    rw [Finset.disjoint_left]
    intro a ha ha'
    rw [Finset.mem_filter] at ha ha'
    omega
  have hunion : (shell t).filter (fun d => d % 2 = 0)
      ∪ (shell t).filter (fun d => d % 2 = 1) = shell t := by
    ext d
    simp only [Finset.mem_union, Finset.mem_filter]
    constructor
    · rintro (⟨h, _⟩ | ⟨h, _⟩) <;> exact h
    · intro h
      rcases Nat.mod_two_eq_zero_or_one d with h0 | h1
      · exact Or.inl ⟨h, h0⟩
      · exact Or.inr ⟨h, h1⟩
  have hsum : ((shell t).filter (fun d => d % 2 = 0)).card
      + ((shell t).filter (fun d => d % 2 = 1)).card = 2 * (subm (r t)).card := by
    rw [← Finset.card_union_of_disjoint hdisj, hunion, hcard]
  by_cases h0 : t % 2 = 0
  · rw [h0] at h1
    rw [← h1] at hsum
    omega
  · have h1' : t % 2 = 1 := by omega
    rw [h1'] at h1
    rw [← h1] at hsum
    omega

#print axioms shell_even_odd_count

end Rule129
end OEIS
