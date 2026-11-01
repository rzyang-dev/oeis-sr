import Tree

namespace OEIS
namespace Rule129

/- ============================================================
   Moments of the submask set.

   The submasks of r are the numbers obtained by choosing, for each
   set bit of r, whether to keep it.  Hence

       #subm r             = 2^(#bits r)
       sum_{m subset r} m  = r * 2^(#bits r) / 2
       sum_{m subset r} m^2 = (r^2 + Q r) * 2^(#bits r) / 4

   with Q r = sum_{i in bits r} 4^i.  This file proves the first in
   Tree.lean and the last in the division-free form

       4 * sum_{m subset r} m^2 = #subm r * (r^2 + Q r) .
   ============================================================ -/

/-- The sum of the squares of the powers of two in the bit decomposition. -/
def Q (r : Nat) : Nat := (bits r).sum (fun i => 4 ^ i)

theorem Q_two_mul (u : Nat) : Q (2 * u) = 4 * Q u := by
  show (bits (2 * u)).sum (fun i => 4 ^ i) = 4 * (bits u).sum (fun i => 4 ^ i)
  rw [bits_two_mul, Finset.sum_image (fun a _ b _ h => by simp at h; omega), Finset.mul_sum]
  refine Finset.sum_congr rfl (fun i _ => ?_)
  show 4 ^ (i + 1) = 4 * 4 ^ i
  rw [pow_succ]
  ring

#print axioms Q_two_mul

theorem Q_two_mul_add_one (u : Nat) : Q (2 * u + 1) = 1 + 4 * Q u := by
  show (bits (2 * u + 1)).sum (fun i => 4 ^ i) = 1 + 4 * (bits u).sum (fun i => 4 ^ i)
  rw [bits_two_mul_add_one]
  rw [Finset.sum_insert (by
    intro h
    rw [Finset.mem_image] at h
    obtain ⟨j, _, hj⟩ := h
    omega)]
  rw [Finset.sum_image (fun a _ b _ h => by simp at h; omega)]
  rw [Finset.mul_sum, Nat.pow_zero]
  congr 1
  refine Finset.sum_congr rfl (fun i _ => ?_)
  show 4 ^ (i + 1) = 4 * 4 ^ i
  rw [pow_succ]
  ring

#print axioms Q_two_mul_add_one

/-- **The second moment of the submask set.**
    Four times the sum of the squares is #subm times (r^2 + Q r). -/
theorem four_mul_card_sq (r : Nat) :
    4 * (subm r).sum (fun m => m * m) = (subm r).card * (r * r + Q r) := by
  induction r using Nat.strong_induction_on with
  | _ r ih =>
    rcases r with _ | _ | k
    · rw [subm_zero, Q, bits_zero]
      simp
    · rw [subm_one]
      decide
    · have hlt : (k + 2) / 2 < k + 2 := Nat.div_lt_self (by omega) (by decide)
      have hdm := Nat.div_add_mod (k + 2) 2
      have hlt2 := Nat.mod_lt (k + 2) (by decide : 0 < 2)
      have hIH := ih ((k + 2) / 2) hlt
      have hS1 := two_mul_sum_subm ((k + 2) / 2)
      interval_cases h : (k + 2) % 2
      · -- even case: k + 2 = 2u
        have he : k + 2 = 2 * ((k + 2) / 2) := by omega
        rw [he, card_subm_two_mul, Q_two_mul]
        rw [subm_two_mul, Finset.sum_map]
        have hL : (subm ((k + 2) / 2)).sum (fun m => emb2 m * emb2 m)
            = 4 * (subm ((k + 2) / 2)).sum (fun m => m * m) := by
          rw [Finset.mul_sum]
          refine Finset.sum_congr rfl (fun m _ => ?_)
          show 2 * m * (2 * m) = 4 * (m * m)
          ring
        rw [hL, hIH]
        ring
      · -- odd case: k + 2 = 2u + 1
        have he : k + 2 = 2 * ((k + 2) / 2) + 1 := by omega
        rw [he, card_subm_two_mul_add_one, Q_two_mul_add_one]
        rw [subm_two_mul_add_one, Finset.sum_union (disjoint_subm_doublings ((k + 2) / 2)),
          Finset.sum_map, Finset.sum_map, ← Finset.sum_add_distrib]
        have hL : (subm ((k + 2) / 2)).sum
              (fun m => emb2 m * emb2 m + emb2p1 m * emb2p1 m)
            = 8 * (subm ((k + 2) / 2)).sum (fun m => m * m)
              + 4 * (subm ((k + 2) / 2)).sum id
              + (subm ((k + 2) / 2)).card := by
          have h1 : ∀ m : Nat, emb2 m * emb2 m + emb2p1 m * emb2p1 m
              = 8 * (m * m) + 4 * m + 1 := by
            intro m
            show 2 * m * (2 * m) + (2 * m + 1) * (2 * m + 1) = 8 * (m * m) + 4 * m + 1
            ring
          rw [Finset.sum_congr rfl (fun m _ => h1 m)]
          rw [Finset.sum_add_distrib, Finset.sum_add_distrib]
          rw [← Finset.mul_sum, ← Finset.mul_sum]
          simp
        rw [hL]
        have hshape : 4 * (8 * (subm ((k + 2) / 2)).sum (fun m => m * m)
              + 4 * (subm ((k + 2) / 2)).sum id
              + (subm ((k + 2) / 2)).card)
            = 8 * (4 * (subm ((k + 2) / 2)).sum (fun m => m * m))
              + 8 * (2 * (subm ((k + 2) / 2)).sum id)
              + 4 * (subm ((k + 2) / 2)).card := by ring
        rw [hshape, hIH, hS1]
        ring

#print axioms four_mul_card_sq

end Rule129
end OEIS
