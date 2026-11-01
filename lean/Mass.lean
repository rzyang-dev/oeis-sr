
import Shells
import Tree
import SelfSim

namespace OEIS
namespace Rule129

/-- the finite set of bit positions of n has popcount many elements -/
theorem bits_card_eq_wt (n : Nat) : (bits n).card = wt n := by
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    rcases Nat.eq_zero_or_pos n with h0 | hpos
    · subst h0
      rw [bits_zero, wt_zero]
      simp
    · obtain ⟨m, hm | hm⟩ : ∃ m, n = 2 * m ∨ n = 2 * m + 1 := half_split n
      · have hinj : Function.Injective (fun i : Nat => i + 1) := fun x y h => by change x + 1 = y + 1 at h; omega
        rw [hm, bits_two_mul, wt_two_mul, Finset.card_image_of_injective _ hinj]
        exact ih m (by omega)
      · have hinj : Function.Injective (fun i : Nat => i + 1) := fun x y h => by change x + 1 = y + 1 at h; omega
        have hnot : (0 : Nat) ∉ (bits m).image (fun i => i + 1) := by
          simp only [Finset.mem_image]
          rintro ⟨j, -, hj⟩
          omega
        have hc : (insert 0 ((bits m).image (fun i => i + 1))).card
            = ((bits m).image (fun i => i + 1)).card + 1 := by
          simp [hnot]
        rw [hm, bits_two_mul_add_one, wt_two_mul_add_one, hc,
          Finset.card_image_of_injective _ hinj, ih m (by omega)]

/-- adding a top bit increases the weight by one -/
theorem wt_add_two_pow : ∀ (k i : Nat), i < 2 ^ k → wt (2 ^ k + i) = wt i + 1 := by
  intro k
  induction k with
  | zero => intro i hi; interval_cases i; change wt 1 = wt 0 + 1; rw [wt_one, wt_zero]
  | succ k ih =>
    intro i hi
    obtain ⟨j, hj | hj⟩ : ∃ j, i = 2 * j ∨ i = 2 * j + 1 := half_split i
    · rw [hj]
      have e1 : 2 ^ (k + 1) + 2 * j = 2 * (2 ^ k + j) := by rw [pow_succ]; ring
      rw [e1, wt_two_mul, wt_two_mul, ih j (by omega)]
    · rw [hj]
      have e1 : 2 ^ (k + 1) + (2 * j + 1) = 2 * (2 ^ k + j) + 1 := by rw [pow_succ]; ring
      rw [e1, wt_two_mul_add_one, wt_two_mul_add_one, ih j (by omega)]

/-- the shell has Sierpinski size -/
theorem shell_card_eq (t : Nat) : (shell t).card = 2 ^ (wt t) := by
  rcases Nat.eq_zero_or_pos t with h0 | hpos
  · subst h0
    have hs : shell 0 = {0} := by
      ext d
      rw [mem_shell, Finset.mem_singleton]
      constructor
      · rintro ⟨hd, -⟩; omega
      · rintro rfl
        exact ⟨le_refl 0, by rw [r_zero]; simp⟩
    rw [hs, wt_zero]
    decide
  · have hrr := r_eq_t_sub_pow t hpos
    have hle : 2 ^ Nat.log2 t ≤ t := Nat.log2_self_le (by omega)
    have hlt2 : t < 2 ^ (Nat.log2 t + 1) := Nat.lt_log2_self (n := t)
    have hp : 2 ^ (Nat.log2 t + 1) = 2 * 2 ^ Nat.log2 t := by rw [pow_succ]; ring
    have hk : t = 2 ^ Nat.log2 t + r t := by omega
    have hlt : r t < 2 ^ Nat.log2 t := by omega
    rw [card_shell t hpos, card_subm_eq_pow_bits, bits_card_eq_wt]
    have hw : wt t = wt (r t) + 1 := by
      conv_lhs => rw [hk]
      exact wt_add_two_pow _ _ hlt
    rw [hw, pow_succ]
    ring

/-- **the dead set has Sierpinski mass**: the first 2^k rows carry 3^k dead cells -/
theorem shell_card_sum_pow (k : Nat) :
    (Finset.range (2 ^ k)).sum (fun t => (shell t).card) = 3 ^ k := by
  rw [show (Finset.range (2 ^ k)).sum (fun t => (shell t).card)
      = (Finset.range (2 ^ k)).sum (fun t => 2 ^ (wt t)) from
    Finset.sum_congr rfl fun t _ => shell_card_eq t]
  exact sum_pow_wt k

/-- one dyadic block of the spacetime diagram carries 2 * 3^k dead cells -/
theorem block_shell_mass (k : Nat) :
    (Finset.range (2 ^ (k + 1))).sum (fun t => (shell t).card)
      - (Finset.range (2 ^ k)).sum (fun t => (shell t).card) = 2 * 3 ^ k := by
  rw [shell_card_sum_pow, shell_card_sum_pow, pow_succ]
  omega

#print axioms shell_card_eq
#print axioms shell_card_sum_pow
#print axioms block_shell_mass

end Rule129
end OEIS