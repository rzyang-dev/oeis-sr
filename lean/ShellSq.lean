import Moments

namespace OEIS
namespace Rule129

/- ============================================================
   Moment relations for the pair decomposition of the shell.

   The shell is the disjoint union of the pairs {u, u-1} with
   u = t - 2m running over the submasks of r t.  These are the three
   subtraction-free relations that pin the moments down:

       B + 2 S1            = N t
       A + 4 (t S1)        = N t^2 + 4 S2
       Zsq + 2 B           = 2 A + N

   with B = sum (t-2m), A = sum (t-2m)^2, S1 = sum m, S2 = sum m^2,
   N = #subm (r t) and Zsq the sum of d^2 over the shell.
   ============================================================ -/

theorem subm_sum_shift (t : Nat) (ht : 1 ≤ t) :
    (subm (r t)).sum (fun m => t - 2 * m) + 2 * (subm (r t)).sum (fun m => m)
      = (subm (r t)).card * t := by
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  have h1 : ∀ m ∈ subm (r t), (t - 2 * m) + 2 * m = t := by
    intro m hm
    have := (mem_subm.mp hm).1
    omega
  calc (subm (r t)).sum (fun m => t - 2 * m) + 2 * (subm (r t)).sum (fun m => m)
      = (subm (r t)).sum (fun m => t - 2 * m) + (subm (r t)).sum (fun m => 2 * m) := by
        rw [Finset.mul_sum]
    _ = (subm (r t)).sum (fun m => (t - 2 * m) + 2 * m) := by
        rw [Finset.sum_add_distrib]
    _ = (subm (r t)).sum (fun _ => t) := Finset.sum_congr rfl h1
    _ = (subm (r t)).card * t := by
        rw [Finset.sum_const]
        simp

#print axioms subm_sum_shift

theorem subm_sum_shift_sq (t : Nat) (ht : 1 ≤ t) :
    (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m))
        + 4 * (t * (subm (r t)).sum (fun m => m))
      = (subm (r t)).card * (t * t) + 4 * (subm (r t)).sum (fun m => m * m) := by
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  have h1 : ∀ m ∈ subm (r t), (t - 2 * m) * (t - 2 * m) + 4 * (t * m) = t * t + 4 * (m * m) := by
    intro m hm
    have h2m : 2 * m ≤ t := by
      have := (mem_subm.mp hm).1
      omega
    set u := t - 2 * m with hu
    have ht' : t = u + 2 * m := by rw [hu]; omega
    rw [ht']
    ring
  calc (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m))
        + 4 * (t * (subm (r t)).sum (fun m => m))
      = (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m))
          + (subm (r t)).sum (fun m => 4 * (t * m)) := by
        rw [Finset.mul_sum, Finset.mul_sum]
    _ = (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) + 4 * (t * m)) := by
        rw [Finset.sum_add_distrib]
    _ = (subm (r t)).sum (fun m => t * t + 4 * (m * m)) := Finset.sum_congr rfl h1
    _ = (subm (r t)).sum (fun _ => t * t) + (subm (r t)).sum (fun m => 4 * (m * m)) := by
        rw [Finset.sum_add_distrib]
    _ = (subm (r t)).card * (t * t) + 4 * (subm (r t)).sum (fun m => m * m) := by
        rw [Finset.mul_sum, Finset.sum_const]
        simp

#print axioms subm_sum_shift_sq

/-- **The shell splits into the pairs {u, u-1}.** -/
theorem shell_sum_sq_split (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => d * d) + 2 * (subm (r t)).sum (fun m => t - 2 * m)
      = 2 * (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m)) + (subm (r t)).card := by
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  have hinner : ∀ m ∈ subm (r t),
      (Finset.range 2).sum (fun x => (t - 2 * m - x) * (t - 2 * m - x))
        = (t - 2 * m) * (t - 2 * m) + (t - 2 * m - 1) * (t - 2 * m - 1) := by
    intro m _
    rw [show (2 : Nat) = 1 + 1 from rfl, Finset.sum_range_succ, Finset.sum_range_one,
      Nat.sub_zero]
  have hre : (shell t).sum (fun d => d * d)
      = (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) + (t - 2 * m - 1) * (t - 2 * m - 1)) := by
    rw [shell_sum_submask (fun d => d * d) t ht, Finset.sum_product,
      Finset.sum_congr rfl hinner]
  rw [hre]
  have h1 : ∀ m ∈ subm (r t),
      ((t - 2 * m) * (t - 2 * m) + (t - 2 * m - 1) * (t - 2 * m - 1)) + 2 * (t - 2 * m)
        = 2 * ((t - 2 * m) * (t - 2 * m)) + 1 := by
    intro m hm
    have h2m : 2 * m + 1 ≤ t := by
      have := (mem_subm.mp hm).1
      omega
    set v := t - 2 * m - 1 with hv
    have hstep : t - 2 * m = v + 1 := by rw [hv]; omega
    rw [hstep]
    ring
  calc (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) + (t - 2 * m - 1) * (t - 2 * m - 1))
        + 2 * (subm (r t)).sum (fun m => t - 2 * m)
      = (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) + (t - 2 * m - 1) * (t - 2 * m - 1))
          + (subm (r t)).sum (fun m => 2 * (t - 2 * m)) := by
        rw [Finset.mul_sum]
    _ = (subm (r t)).sum (fun m =>
          ((t - 2 * m) * (t - 2 * m) + (t - 2 * m - 1) * (t - 2 * m - 1)) + 2 * (t - 2 * m)) := by
        rw [← Finset.sum_add_distrib]
    _ = (subm (r t)).sum (fun m => 2 * ((t - 2 * m) * (t - 2 * m)) + 1) := Finset.sum_congr rfl h1
    _ = (subm (r t)).sum (fun m => 2 * ((t - 2 * m) * (t - 2 * m)))
          + (subm (r t)).sum (fun _ => 1) := by
        rw [Finset.sum_add_distrib]
    _ = 2 * (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m)) + (subm (r t)).card := by
        rw [Finset.mul_sum, Finset.sum_const]
        simp

#print axioms shell_sum_sq_split

/- ---------- the closed form for the second moment of the shell ---------- -/

/-- **The second moment of the shell.**
    sum_{d in S(t)} d^2 = #subm(r t) * (2 K (K-1) + 2 Q(r t) + 1),  K = t - r t. -/
theorem shell_sum_sq (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => d * d)
      = (subm (r t)).card * (2 * (t - r t) * (t - r t - 1) + 2 * Q (r t) + 1) := by
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  -- opaque atoms
  set N := (subm (r t)).card with hN
  set S1 := (subm (r t)).sum (fun m => m) with hS1
  set S2 := (subm (r t)).sum (fun m => m * m) with hS2
  set B := (subm (r t)).sum (fun m => t - 2 * m) with hB
  set A := (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m)) with hA
  set Zsq := (shell t).sum (fun d => d * d) with hZ
  -- the five relations, in the atoms
  have rB : B + 2 * S1 = N * t := by
    rw [hB, hS1, hN]; exact subm_sum_shift t ht
  have rA : A + 4 * (t * S1) = N * (t * t) + 4 * S2 := by
    rw [hA, hS1, hS2, hN]; exact subm_sum_shift_sq t ht
  have rZ : Zsq + 2 * B = 2 * A + N := by
    rw [hZ, hB, hA, hN]; exact shell_sum_sq_split t ht
  have rS1 : 2 * S1 = N * r t := by
    rw [hS1, hN]; exact two_mul_sum_subm (r t)
  have rS2 : 4 * S2 = N * (r t * r t + Q (r t)) := by
    rw [hS2, hN]; exact four_mul_card_sq (r t)
  -- cast to Int
  have rB' : (B : Int) + 2 * (S1 : Int) = (N : Int) * (t : Int) := by exact_mod_cast rB
  have rA' : (A : Int) + 4 * ((t : Int) * (S1 : Int))
      = (N : Int) * ((t : Int) * (t : Int)) + 4 * (S2 : Int) := by exact_mod_cast rA
  have rZ' : (Zsq : Int) + 2 * (B : Int) = 2 * (A : Int) + (N : Int) := by exact_mod_cast rZ
  have rS1' : 2 * (S1 : Int) = (N : Int) * (r t : Int) := by exact_mod_cast rS1
  have rS2' : 4 * (S2 : Int) = (N : Int) * ((r t : Int) * (r t : Int) + (Q (r t) : Int)) := by
    exact_mod_cast rS2
  have key : (Zsq : Int) = (N : Int) * (2 * ((t : Int) - (r t : Int))
      * (((t : Int) - (r t : Int)) - 1) + 2 * (Q (r t) : Int) + 1) := by
    nlinarith [rB', rA', rZ', rS1', rS2']
  -- bridge back to Nat
  have hcast : ((N * (2 * (t - r t) * (t - r t - 1) + 2 * Q (r t) + 1) : Nat) : Int)
      = (N : Int) * (2 * ((t : Int) - (r t : Int)) * (((t : Int) - (r t : Int)) - 1)
        + 2 * (Q (r t) : Int) + 1) := by
    have h1 : 1 ≤ t - r t := by omega
    have h2 : r t ≤ t := by omega
    push_cast [h1, h2]
    ring
  have hgoalZ : ((Zsq : Nat) : Int)
      = ((N * (2 * (t - r t) * (t - r t - 1) + 2 * Q (r t) + 1) : Nat) : Int) := by
    rw [hcast]
    exact key
  exact Nat.cast_injective hgoalZ

#print axioms shell_sum_sq

end Rule129
end OEIS