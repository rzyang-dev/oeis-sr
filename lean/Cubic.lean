import ShellSq

namespace OEIS
namespace Rule129

/- ============================================================
   The third moments, and the four-dimensional lattices.

       sum_{m subset r} m^3       = #subm r * (r^3 + 3 Q r) / 8
       sum_{d in S(t)} d^3        = #subm(r t) * (2k^3 + 3k^2 + 3k + 1 + 3Q(2k+1))

   with k = t - r t - 1.  Then

       Z^4 Moore:       c_d = 64 d^3 + 16 d      ->  64 M3 + 16 sigma + eps
       Z^4 von Neumann: c_d = 8 d (d^2+2)/3      ->  3 * zeros = 8 M3 + 16 sigma + 3 eps
   ============================================================ -/

/-- **The third moment of the submask set.** -/
theorem eight_mul_card_cube (r : Nat) :
    8 * (subm r).sum (fun m => m * m * m) = (subm r).card * (r * r * r + 3 * Q r * r) := by
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
      have hS2 := four_mul_card_sq ((k + 2) / 2)
      interval_cases h : (k + 2) % 2
      · -- even
        have he : k + 2 = 2 * ((k + 2) / 2) := by omega
        rw [he, card_subm_two_mul, Q_two_mul]
        rw [subm_two_mul, Finset.sum_map]
        have hL : (subm ((k + 2) / 2)).sum (fun m => emb2 m * emb2 m * emb2 m)
            = 8 * (subm ((k + 2) / 2)).sum (fun m => m * m * m) := by
          rw [Finset.mul_sum]
          refine Finset.sum_congr rfl (fun m _ => ?_)
          show 2 * m * (2 * m) * (2 * m) = 8 * (m * m * m)
          ring
        rw [hL, hIH]
        ring
      · -- odd
        have he : k + 2 = 2 * ((k + 2) / 2) + 1 := by omega
        rw [he, card_subm_two_mul_add_one, Q_two_mul_add_one]
        rw [subm_two_mul_add_one, Finset.sum_union (disjoint_subm_doublings ((k + 2) / 2)),
          Finset.sum_map, Finset.sum_map, ← Finset.sum_add_distrib]
        have hL : (subm ((k + 2) / 2)).sum
              (fun m => emb2 m * emb2 m * emb2 m + emb2p1 m * emb2p1 m * emb2p1 m)
            = 16 * (subm ((k + 2) / 2)).sum (fun m => m * m * m)
              + 12 * (subm ((k + 2) / 2)).sum (fun m => m * m)
              + 6 * (subm ((k + 2) / 2)).sum (fun m => m)
              + (subm ((k + 2) / 2)).card := by
          have h1 : ∀ m : Nat, emb2 m * emb2 m * emb2 m + emb2p1 m * emb2p1 m * emb2p1 m
              = 16 * (m * m * m) + 12 * (m * m) + 6 * m + 1 := by
            intro m
            show 2 * m * (2 * m) * (2 * m) + (2 * m + 1) * (2 * m + 1) * (2 * m + 1)
              = 16 * (m * m * m) + 12 * (m * m) + 6 * m + 1
            ring
          rw [Finset.sum_congr rfl (fun m _ => h1 m)]
          rw [Finset.sum_add_distrib, Finset.sum_add_distrib, Finset.sum_add_distrib]
          rw [← Finset.mul_sum, ← Finset.mul_sum, ← Finset.mul_sum]
          simp
        rw [hL]
        have hshape : 8 * (16 * (subm ((k + 2) / 2)).sum (fun m => m * m * m)
              + 12 * (subm ((k + 2) / 2)).sum (fun m => m * m)
              + 6 * (subm ((k + 2) / 2)).sum (fun m => m)
              + (subm ((k + 2) / 2)).card)
            = 16 * (8 * (subm ((k + 2) / 2)).sum (fun m => m * m * m))
              + 24 * (4 * (subm ((k + 2) / 2)).sum (fun m => m * m))
              + 24 * (2 * (subm ((k + 2) / 2)).sum (fun m => m))
              + 8 * (subm ((k + 2) / 2)).card := by ring
        have hS1' : 2 * (subm ((k + 2) / 2)).sum (fun m => m)
            = (subm ((k + 2) / 2)).card * ((k + 2) / 2) := hS1
        rw [hshape, hIH, hS2, hS1']
        ring

#print axioms eight_mul_card_cube

/-- The cube relation for the shifted submask sums. -/
theorem subm_sum_shift_cube (t : Nat) (ht : 1 ≤ t) :
    (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) * (t - 2 * m))
        + 6 * (t * t * (subm (r t)).sum (fun m => m))
        + 8 * (subm (r t)).sum (fun m => m * m * m)
      = (subm (r t)).card * (t * t * t)
        + 12 * (t * (subm (r t)).sum (fun m => m * m)) := by
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  have h1 : ∀ m ∈ subm (r t),
      (t - 2 * m) * (t - 2 * m) * (t - 2 * m) + 6 * (t * t * m) + 8 * (m * m * m)
        = t * t * t + 12 * (t * (m * m)) := by
    intro m hm
    have h2m : 2 * m ≤ t := by
      have := (mem_subm.mp hm).1
      omega
    set u := t - 2 * m with hu
    have ht' : t = u + 2 * m := by rw [hu]; omega
    rw [ht']
    ring
  calc (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) * (t - 2 * m))
        + 6 * (t * t * (subm (r t)).sum (fun m => m))
        + 8 * (subm (r t)).sum (fun m => m * m * m)
      = (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) * (t - 2 * m))
          + 6 * (t * t * (subm (r t)).sum (fun m => m))
          + (subm (r t)).sum (fun m => 8 * (m * m * m)) := by
        simp only [Finset.mul_sum]
    _ = (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) * (t - 2 * m))
          + (subm (r t)).sum (fun m => 6 * (t * t * m))
          + (subm (r t)).sum (fun m => 8 * (m * m * m)) := by
        simp only [Finset.mul_sum]
    _ = (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) * (t - 2 * m)
          + 6 * (t * t * m) + 8 * (m * m * m)) := by
        rw [← Finset.sum_add_distrib, ← Finset.sum_add_distrib]
    _ = (subm (r t)).sum (fun m => t * t * t + 12 * (t * (m * m))) := Finset.sum_congr rfl h1
    _ = (subm (r t)).sum (fun m => t * t * t) + (subm (r t)).sum (fun m => 12 * (t * (m * m))) := by
        rw [Finset.sum_add_distrib]
    _ = (subm (r t)).card * (t * t * t)
          + 12 * (t * (subm (r t)).sum (fun m => m * m)) := by
        simp only [Finset.mul_sum, Finset.sum_const]
        simp

#print axioms subm_sum_shift_cube

/-- The shell splits into pairs: the cube relation. -/
theorem shell_sum_cube_split (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => d * d * d)
        + 3 * (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m))
        + (subm (r t)).card
      = 2 * (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) * (t - 2 * m))
        + 3 * (subm (r t)).sum (fun m => t - 2 * m) := by
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  have hinner : ∀ m ∈ subm (r t),
      (Finset.range 2).sum (fun x => (t - 2 * m - x) * (t - 2 * m - x) * (t - 2 * m - x))
        = (t - 2 * m) * (t - 2 * m) * (t - 2 * m)
          + (t - 2 * m - 1) * (t - 2 * m - 1) * (t - 2 * m - 1) := by
    intro m _
    rw [show (2 : Nat) = 1 + 1 from rfl, Finset.sum_range_succ, Finset.sum_range_one,
      Nat.sub_zero]
  have hre : (shell t).sum (fun d => d * d * d)
      = (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) * (t - 2 * m)
          + (t - 2 * m - 1) * (t - 2 * m - 1) * (t - 2 * m - 1)) := by
    rw [shell_sum_submask (fun d => d * d * d) t ht, Finset.sum_product,
      Finset.sum_congr rfl hinner]
  rw [hre]
  have h1 : ∀ m ∈ subm (r t),
      ((t - 2 * m) * (t - 2 * m) * (t - 2 * m)
        + (t - 2 * m - 1) * (t - 2 * m - 1) * (t - 2 * m - 1))
        + 3 * ((t - 2 * m) * (t - 2 * m)) + 1
      = 2 * ((t - 2 * m) * (t - 2 * m) * (t - 2 * m)) + 3 * (t - 2 * m) := by
    intro m hm
    have h2m : 2 * m + 1 ≤ t := by
      have := (mem_subm.mp hm).1
      omega
    set v := t - 2 * m - 1 with hv
    have hstep : t - 2 * m = v + 1 := by rw [hv]; omega
    rw [hstep]
    ring
  calc (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) * (t - 2 * m)
          + (t - 2 * m - 1) * (t - 2 * m - 1) * (t - 2 * m - 1))
        + 3 * (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m))
        + (subm (r t)).card
      = (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) * (t - 2 * m)
            + (t - 2 * m - 1) * (t - 2 * m - 1) * (t - 2 * m - 1))
          + (subm (r t)).sum (fun m => 3 * ((t - 2 * m) * (t - 2 * m)))
          + (subm (r t)).sum (fun _ => 1) := by
        simp only [Finset.mul_sum, Finset.sum_const]
        simp
    _ = (subm (r t)).sum (fun m => ((t - 2 * m) * (t - 2 * m) * (t - 2 * m)
            + (t - 2 * m - 1) * (t - 2 * m - 1) * (t - 2 * m - 1))
            + 3 * ((t - 2 * m) * (t - 2 * m)) + 1) := by
        rw [← Finset.sum_add_distrib, ← Finset.sum_add_distrib]
    _ = (subm (r t)).sum (fun m => 2 * ((t - 2 * m) * (t - 2 * m) * (t - 2 * m))
            + 3 * (t - 2 * m)) := Finset.sum_congr rfl h1
    _ = 2 * (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) * (t - 2 * m))
          + 3 * (subm (r t)).sum (fun m => t - 2 * m) := by
        simp only [Finset.sum_add_distrib, Finset.mul_sum]

#print axioms shell_sum_cube_split

/- ---------- the closed form for the third moment of the shell ---------- -/

/-- **Pure algebra.**  The seven relations among the submask sums force the cube.
    With K = T - R one gets A3 = N (K^3 + 3 Q K), B = N K, A = N (K^2 + Q),
    and then ZC = 2 A3 + 3 B - 3 A - N. -/
theorem cube_key (N S1 S2 S3 B A A3 ZC T R Q : Int)
    (h1 : B + 2 * S1 = N * T)
    (h2 : A + 4 * (T * S1) = N * (T * T) + 4 * S2)
    (h3 : A3 + 6 * ((T * T) * S1) + 8 * S3 = N * ((T * T) * T) + 12 * (T * S2))
    (h4 : ZC + 3 * A + N = 2 * A3 + 3 * B)
    (h5 : 2 * S1 = N * R)
    (h6 : 4 * S2 = N * (R * R + Q))
    (h7 : 8 * S3 = N * ((R * R) * R + 3 * Q * R)) :
    ZC = N * (2 * (T - R - 1) ^ 3 + 3 * (T - R - 1) ^ 2 + 3 * (T - R - 1) + 1
      + 3 * Q * (2 * (T - R - 1) + 1)) := by
  have eB : B = N * (T - R) := by
    linear_combination h1 - h5
  have eA : A = N * ((T - R) * (T - R) + Q) := by
    linear_combination h2 - (2 * T) * h5 + h6
  have eA3 : A3 = N * ((T - R) * (T - R) * (T - R) + 3 * Q * (T - R)) := by
    linear_combination h3 - (3 * (T * T)) * h5 + (3 * T) * h6 - h7
  linear_combination h4 + 2 * eA3 + 3 * eB - 3 * eA

#print axioms cube_key

/-- **The third moment of the shell.**
    sum over the shell of d^3 equals #subm(r t) * (2k^3 + 3k^2 + 3k + 1 + 3Q(2k+1)),
    where k = t - r t - 1. -/
theorem shell_sum_cube (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => d * d * d)
      = (subm (r t)).card
        * (2 * (t - r t - 1) ^ 3 + 3 * (t - r t - 1) ^ 2 + 3 * (t - r t - 1) + 1
          + 3 * Q (r t) * (2 * (t - r t - 1) + 1)) := by
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  set N := (subm (r t)).card with hN
  set S1 := (subm (r t)).sum (fun m => m) with hS1
  set S2 := (subm (r t)).sum (fun m => m * m) with hS2
  set S3 := (subm (r t)).sum (fun m => m * m * m) with hS3
  set B := (subm (r t)).sum (fun m => t - 2 * m) with hB
  set A := (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m)) with hA
  set A3 := (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) * (t - 2 * m)) with hA3
  set Zc := (shell t).sum (fun d => d * d * d) with hZ
  set K := t - r t - 1 with hKdef
  have rB : B + 2 * S1 = N * t := by
    rw [hB, hS1, hN]; exact subm_sum_shift t ht
  have rA : A + 4 * (t * S1) = N * (t * t) + 4 * S2 := by
    rw [hA, hS1, hS2, hN]; exact subm_sum_shift_sq t ht
  have rA3 : A3 + 6 * ((t * t) * S1) + 8 * S3 = N * ((t * t) * t) + 12 * (t * S2) := by
    rw [hA3, hS1, hS2, hS3, hN]; exact subm_sum_shift_cube t ht
  have rZ : Zc + 3 * A + N = 2 * A3 + 3 * B := by
    rw [hZ, hB, hA, hA3, hN]; exact shell_sum_cube_split t ht
  have rS1 : 2 * S1 = N * r t := by
    rw [hS1, hN]; exact two_mul_sum_subm (r t)
  have rS2 : 4 * S2 = N * (r t * r t + Q (r t)) := by
    rw [hS2, hN]; exact four_mul_card_sq (r t)
  have rS3 : 8 * S3 = N * (r t * r t * r t + 3 * Q (r t) * r t) := by
    rw [hS3, hN]; exact eight_mul_card_cube (r t)
  have rB' : (B : Int) + 2 * (S1 : Int) = (N : Int) * (t : Int) := by exact_mod_cast rB
  have rA' : (A : Int) + 4 * ((t : Int) * (S1 : Int))
      = (N : Int) * ((t : Int) * (t : Int)) + 4 * (S2 : Int) := by exact_mod_cast rA
  have rA3' : (A3 : Int) + 6 * (((t : Int) * (t : Int)) * (S1 : Int)) + 8 * (S3 : Int)
      = (N : Int) * (((t : Int) * (t : Int)) * (t : Int)) + 12 * ((t : Int) * (S2 : Int)) := by
    exact_mod_cast rA3
  have rZ' : (Zc : Int) + 3 * (A : Int) + (N : Int) = 2 * (A3 : Int) + 3 * (B : Int) := by
    exact_mod_cast rZ
  have rS1' : 2 * (S1 : Int) = (N : Int) * (r t : Int) := by exact_mod_cast rS1
  have rS2' : 4 * (S2 : Int) = (N : Int) * ((r t : Int) * (r t : Int) + (Q (r t) : Int)) := by
    exact_mod_cast rS2
  have rS3' : 8 * (S3 : Int)
      = (N : Int) * ((r t : Int) * (r t : Int) * (r t : Int) + 3 * (Q (r t) : Int) * (r t : Int)) := by
    exact_mod_cast rS3
  have key := cube_key (N : Int) (S1 : Int) (S2 : Int) (S3 : Int) (B : Int) (A : Int)
    (A3 : Int) (Zc : Int) (t : Int) (r t : Int) (Q (r t) : Int) rB' rA' rA3' rZ' rS1' rS2' rS3'
  set C := N * (2 * K ^ 3 + 3 * K ^ 2 + 3 * K + 1 + 3 * Q (r t) * (2 * K + 1)) with hC
  have hKi : (K : Int) = (t : Int) - (r t : Int) - 1 := by
    have h1 : 1 ≤ t - r t := by
      have := two_mul_r_add_one_le t ht
      omega
    have h2 : r t ≤ t := by omega
    rw [hKdef]
    push_cast [h1, h2]
    ring
  have hcast : (C : Int) = (N : Int) * (2 * ((t : Int) - (r t : Int) - 1) ^ 3
      + 3 * ((t : Int) - (r t : Int) - 1) ^ 2 + 3 * ((t : Int) - (r t : Int) - 1) + 1
      + 3 * (Q (r t) : Int) * (2 * ((t : Int) - (r t : Int) - 1) + 1)) := by
    rw [hC]
    push_cast
    rw [hKi]
  have hgoalZ : ((Zc : Nat) : Int) = (C : Int) := by
    rw [hcast]
    exact key
  have hfin := Nat.cast_injective hgoalZ
  rw [hZ, hC, hN] at hfin
  exact hfin

#print axioms shell_sum_cube

end Rule129
end OEIS

