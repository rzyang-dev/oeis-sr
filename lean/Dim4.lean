import Cubic

namespace OEIS
namespace Rule129

/- ============================================================
   Cubic level sizes: the four-dimensional lattices.

   In Z^4 the Moore level holds   (2d+1)^4 - (2d-1)^4 = 64 d^3 + 16 d,
   and the von Neumann level holds 8 d (d^2 + 2) / 3 .  Both vanish at
   d = 0, where the centre alone sits, so the zero count picks up the
   correction eps = [0 in shell t]:

       Z^4 Moore:        64 M3 + 16 sigma + eps
       Z^4 von Neumann:  3 Z = 8 M3 + 16 sigma + 3 eps

   with M3 = sum of d^3 over the shell and sigma = sum of d.
   ============================================================ -/

/-- **Cubic level sizes.**  Level 0 carries the centre, level d >= 1 carries
    a d^3 + b d cells; the zero count is a M3 + b sigma + eps. -/
theorem shell_sum_cubic (a b : Nat) (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => if d = 0 then 1 else a * (d * d * d) + b * d)
      = a * (shell t).sum (fun d => d * d * d) + b * (shell t).sum (fun d => d)
        + (if 0 ∈ shell t then 1 else 0) := by
  have hpt : ∀ d : Nat, (if d = 0 then 1 else a * (d * d * d) + b * d)
      = a * (d * d * d) + b * d + (if 0 = d then 1 else 0) := by
    intro d
    by_cases h : d = 0
    · subst h
      simp
    · have h1 : ¬ (0 = d) := Ne.symm h
      simp [h, h1]
  calc (shell t).sum (fun d => if d = 0 then 1 else a * (d * d * d) + b * d)
      = (shell t).sum (fun d => a * (d * d * d) + b * d + (if 0 = d then 1 else 0)) :=
        Finset.sum_congr rfl (fun d _ => hpt d)
    _ = (shell t).sum (fun d => a * (d * d * d) + b * d)
          + (shell t).sum (fun d => (if 0 = d then 1 else 0)) := Finset.sum_add_distrib
    _ = ((shell t).sum (fun d => a * (d * d * d)) + (shell t).sum (fun d => b * d))
          + (shell t).sum (fun d => (if 0 = d then 1 else 0)) := by
        rw [Finset.sum_add_distrib]
    _ = (a * (shell t).sum (fun d => d * d * d) + b * (shell t).sum (fun d => d))
          + (if 0 ∈ shell t then 1 else 0) := by
        rw [← Finset.mul_sum, ← Finset.mul_sum, Finset.sum_ite_eq]

#print axioms shell_sum_cubic

/- ---------- 3 divides d (d^2 + 2) ---------- -/

theorem three_dvd (d : Nat) : 3 ∣ d * (d * d + 2) := by
  set q := d / 3 with hq
  set r := d % 3 with hr
  have hd : d = 3 * q + r := by
    rw [hq, hr]
    exact (Nat.div_add_mod d 3).symm
  have hlt : r < 3 := by
    rw [hr]
    exact Nat.mod_lt d (by decide : 0 < 3)
  rw [hd]
  interval_cases r
  · exact ⟨q * ((3 * q) * (3 * q) + 2), by ring⟩
  · exact ⟨(3 * q + 1) * (3 * (q * q) + 2 * q + 1), by ring⟩
  · exact ⟨(3 * q + 2) * (3 * (q * q) + 4 * q + 2), by ring⟩

#print axioms three_dvd

/-- Three times the von Neumann level size of Z^4 is 8 d^3 + 16 d. -/
theorem three_mul_level (d : Nat) :
    3 * (8 * (d * (d * d + 2) / 3)) = 8 * (d * d * d) + 16 * d := by
  have h : 3 * (d * (d * d + 2) / 3) = d * (d * d + 2) := by
    rw [Nat.mul_comm]
    exact Nat.div_mul_cancel (three_dvd d)
  calc 3 * (8 * (d * (d * d + 2) / 3))
      = 8 * (3 * (d * (d * d + 2) / 3)) := by ring
    _ = 8 * (d * (d * d + 2)) := by rw [h]
    _ = 8 * (d * d * d) + 16 * d := by ring

#print axioms three_mul_level

/-- **Z^4 Moore** (level sizes 64 d^3 + 16 d). -/
theorem zero_count_Z4_moore (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => if d = 0 then 1 else 64 * (d * d * d) + 16 * d)
      = 64 * ((subm (r t)).card
          * (2 * (t - r t - 1) ^ 3 + 3 * (t - r t - 1) ^ 2 + 3 * (t - r t - 1) + 1
            + 3 * Q (r t) * (2 * (t - r t - 1) + 1)))
        + 16 * ((subm (r t)).card * (2 * t - 1 - 2 * r t))
        + (if 0 ∈ shell t then 1 else 0) := by
  rw [shell_sum_cubic 64 16 t ht, shell_sum_cube t ht]
  rw [show (shell t).sum (fun d => d) = (shell t).sum id from rfl, sigma_shell t ht]

#print axioms zero_count_Z4_moore

/-- **Z^4 von Neumann** (level sizes 8 d (d^2+2)/3): three times the count. -/
theorem zero_count_Z4_vonNeumann (t : Nat) (ht : 1 ≤ t) :
    3 * (shell t).sum (fun d => if d = 0 then 1 else 8 * (d * (d * d + 2) / 3))
      = 8 * ((subm (r t)).card
          * (2 * (t - r t - 1) ^ 3 + 3 * (t - r t - 1) ^ 2 + 3 * (t - r t - 1) + 1
            + 3 * Q (r t) * (2 * (t - r t - 1) + 1)))
        + 16 * ((subm (r t)).card * (2 * t - 1 - 2 * r t))
        + 3 * (if 0 ∈ shell t then 1 else 0) := by
  have hpt : ∀ d : Nat, 3 * (if d = 0 then 1 else 8 * (d * (d * d + 2) / 3))
      = (if d = 0 then 1 else 8 * (d * d * d) + 16 * d)
        + 2 * (if 0 = d then 1 else 0) := by
    intro d
    by_cases h : d = 0
    · subst h
      simp
    · have h1 : ¬ (0 = d) := Ne.symm h
      simp [h, h1, three_mul_level]
  calc 3 * (shell t).sum (fun d => if d = 0 then 1 else 8 * (d * (d * d + 2) / 3))
      = (shell t).sum (fun d => 3 * (if d = 0 then 1 else 8 * (d * (d * d + 2) / 3))) := by
        rw [Finset.mul_sum]
    _ = (shell t).sum (fun d => (if d = 0 then 1 else 8 * (d * d * d) + 16 * d)
          + 2 * (if 0 = d then 1 else 0)) := Finset.sum_congr rfl (fun d _ => hpt d)
    _ = (shell t).sum (fun d => (if d = 0 then 1 else 8 * (d * d * d) + 16 * d))
          + (shell t).sum (fun d => 2 * (if 0 = d then 1 else 0)) := Finset.sum_add_distrib
    _ = (shell t).sum (fun d => (if d = 0 then 1 else 8 * (d * d * d) + 16 * d))
          + 2 * (if 0 ∈ shell t then 1 else 0) := by
        rw [← Finset.mul_sum, Finset.sum_ite_eq]
    _ = (8 * ((subm (r t)).card
            * (2 * (t - r t - 1) ^ 3 + 3 * (t - r t - 1) ^ 2 + 3 * (t - r t - 1) + 1
              + 3 * Q (r t) * (2 * (t - r t - 1) + 1)))
          + 16 * ((subm (r t)).card * (2 * t - 1 - 2 * r t))
          + (if 0 ∈ shell t then 1 else 0))
        + 2 * (if 0 ∈ shell t then 1 else 0) := by
        rw [shell_sum_cubic 8 16 t ht, shell_sum_cube t ht]
        rw [show (shell t).sum (fun d => d) = (shell t).sum id from rfl, sigma_shell t ht]
    _ = 8 * ((subm (r t)).card
            * (2 * (t - r t - 1) ^ 3 + 3 * (t - r t - 1) ^ 2 + 3 * (t - r t - 1) + 1
              + 3 * Q (r t) * (2 * (t - r t - 1) + 1)))
          + 16 * ((subm (r t)).card * (2 * t - 1 - 2 * r t))
          + 3 * (if 0 ∈ shell t then 1 else 0) := by
        ring

#print axioms zero_count_Z4_vonNeumann

end Rule129
end OEIS
