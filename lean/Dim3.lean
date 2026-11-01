import ShellSq

namespace OEIS
namespace Rule129

/- ============================================================
   Quadratic level sizes: the three-dimensional lattices.

   In Z^3 the von Neumann level d holds 4d^2 + 2 cells (d >= 1) and the
   Moore level holds 24d^2 + 2.  Both are of the form 4k d^2 + 2, and the
   zero count is then  4k M2 + 2 #shell - eps  with M2 = sum of d^2.
   ============================================================ -/

/-- **Quadratic level sizes.**  Level 0 carries the centre, level d >= 1 carries
    4*k*d^2 + 2 cells; the zero count is 4k M2 + 2 #shell - eps. -/
theorem shell_sum_quadratic (k : Nat) (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => if d = 0 then 1 else 4 * k * (d * d) + 2)
      = 4 * k * (shell t).sum (fun d => d * d) + 2 * (shell t).card
        - (if 0 ∈ shell t then 1 else 0) := by
  have hpt : ∀ d : Nat, (if d = 0 then 1 else 4 * k * (d * d) + 2)
      = 4 * k * (d * d) + (if 0 = d then 1 else 2) := by
    intro d
    by_cases h : d = 0
    · subst h; simp
    · simp [h, Ne.symm h]
  have hpt2 : ∀ d : Nat, (if 0 = d then 1 else 2) + (if 0 = d then 1 else 0) = 2 := by
    intro d
    by_cases h : 0 = d <;> simp [h]
  have hsingle : (shell t).sum (fun d => if 0 = d then 1 else 0)
      = if 0 ∈ shell t then 1 else 0 := by
    rw [Finset.sum_ite_eq]
  have hsum2 : (shell t).sum (fun d => (if 0 = d then 1 else 2))
      + (if 0 ∈ shell t then 1 else 0) = 2 * (shell t).card := by
    rw [← hsingle, ← Finset.sum_add_distrib]
    rw [Finset.sum_congr rfl (fun d _ => hpt2 d)]
    simp [Finset.sum_const]
    omega
  calc (shell t).sum (fun d => if d = 0 then 1 else 4 * k * (d * d) + 2)
      = (shell t).sum (fun d => 4 * k * (d * d) + (if 0 = d then 1 else 2)) :=
        Finset.sum_congr rfl (fun d _ => hpt d)
    _ = (shell t).sum (fun d => 4 * k * (d * d))
          + (shell t).sum (fun d => (if 0 = d then 1 else 2)) := Finset.sum_add_distrib
    _ = 4 * k * (shell t).sum (fun d => d * d)
          + (shell t).sum (fun d => (if 0 = d then 1 else 2)) := by
        rw [← Finset.mul_sum]
    _ = 4 * k * (shell t).sum (fun d => d * d) + 2 * (shell t).card
          - (if 0 ∈ shell t then 1 else 0) := by
        rw [Nat.eq_sub_of_add_eq hsum2]
        omega

#print axioms shell_sum_quadratic

/-- **Z^3 von Neumann** (level sizes 4d^2 + 2). -/
theorem zero_count_Z3_vonNeumann (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => if d = 0 then 1 else 4 * (d * d) + 2)
      = 4 * ((subm (r t)).card * (2 * (t - r t) * (t - r t - 1) + 2 * Q (r t) + 1))
        + 2 * (shell t).card - (if 0 ∈ shell t then 1 else 0) := by
  rw [shell_sum_quadratic 1 t ht, shell_sum_sq t ht]

#print axioms zero_count_Z3_vonNeumann

/-- **Z^3 Moore** (level sizes 24d^2 + 2). -/
theorem zero_count_Z3_moore (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => if d = 0 then 1 else 24 * (d * d) + 2)
      = 24 * ((subm (r t)).card * (2 * (t - r t) * (t - r t - 1) + 2 * Q (r t) + 1))
        + 2 * (shell t).card - (if 0 ∈ shell t then 1 else 0) := by
  rw [shell_sum_quadratic 6 t ht, shell_sum_sq t ht]

#print axioms zero_count_Z3_moore

end Rule129
end OEIS