import Shells

namespace OEIS
namespace Rule129

/- ============================================================
   The submask transform.

   The zero set at time t is the union of the shells, so the number
   of zeroes of ANY geometry is a linear functional of the level-size
   sequence c_d:

       #Z(t) = sum_{d in shell t} c_d .

   Everything here follows from that single identity:

   * the master formula: the shell sum is a sum over the submasks of r t,
   * constant and linear level sizes (lines, plane lattices),
   * and the inverse direction: given the level below the centre, the
     counts determine the level size at every time.
   ============================================================ -/

/-- Every time t is itself a shell level (it is where the centre sits). -/
theorem shell_mem_self (t : Nat) (ht : 1 ≤ t) : t ∈ shell t := by
  rw [mem_shell]
  refine ⟨le_rfl, ?_⟩
  rw [Nat.sub_self]
  simp

#print axioms shell_mem_self

/-- **The submask transform.**  The shell sum of an arbitrary level-size
    sequence is the sum over the submasks of r t of the two levels
    t - 2m and t - 2m - 1. -/
theorem shell_sum_submask (c : Nat → Nat) (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum c
      = ((subm (r t)) ×ˢ (Finset.range 2)).sum (fun p => c (t - 2 * p.1 - p.2)) := by
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  refine Finset.sum_bij (fun d _ => ((t - d) / 2, (t - d) % 2)) ?_ ?_ ?_ ?_
  · intro d hd
    rw [mem_shell] at hd
    obtain ⟨hdt, hcond⟩ := hd
    simp only [Finset.mem_product, Finset.mem_range, mem_subm]
    exact ⟨⟨sub_le (show sub ((t - d) / 2) (r t) from hcond), hcond⟩, by omega⟩
  · intro d1 hd1 d2 hd2 heq
    rw [mem_shell] at hd1 hd2
    obtain ⟨hdt1, _⟩ := hd1
    obtain ⟨hdt2, _⟩ := hd2
    have h1 : (t - d1) / 2 = (t - d2) / 2 := by
      simpa using congrArg Prod.fst heq
    have h2 : (t - d1) % 2 = (t - d2) % 2 := by
      simpa using congrArg Prod.snd heq
    have e1 := Nat.div_add_mod (t - d1) 2
    have e2 := Nat.div_add_mod (t - d2) 2
    omega
  · intro p hp
    simp only [Finset.mem_product, Finset.mem_range, mem_subm] at hp
    obtain ⟨⟨hp1, hp2⟩, hp3⟩ := hp
    have hdiv : (2 * p.1 + p.2) / 2 = p.1 := Nat.div_eq_of_lt_le (by omega) (by omega)
    have hmod : (2 * p.1 + p.2) % 2 = p.2 := by
      rw [Nat.mod_eq_sub_mul_div, hdiv]; omega
    have hd : t - (t - 2 * p.1 - p.2) = 2 * p.1 + p.2 := by omega
    refine ⟨t - 2 * p.1 - p.2, ?_, ?_⟩
    · rw [mem_shell]
      exact ⟨by omega, by rw [hd, hdiv]; exact hp2⟩
    · simp only [hd, hdiv, hmod]
  · intro d hd
    rw [mem_shell] at hd
    obtain ⟨hdt, _⟩ := hd
    have e := Nat.div_add_mod (t - d) 2
    show c d = c (t - 2 * ((t - d) / 2) - (t - d) % 2)
    congr 1
    omega

#print axioms shell_sum_submask

/- ---------- level sizes that grow linearly: lattices ---------- -/

/-- The sum of a constant multiple of the level over a shell. -/
theorem shell_sum_mul (k : Nat) (t : Nat) :
    (shell t).sum (fun d => k * d) = k * (shell t).sum id := by
  rw [Finset.mul_sum]
  rfl

#print axioms shell_sum_mul

/-- **Plane lattices.**  If level 0 carries the single centre and every level
    d >= 1 carries k * d cells (von Neumann k = 4, Moore k = 8, the triangular
    lattice k = 6), the number of zeroes is k * sigma + eps. -/
theorem shell_sum_linear (k : Nat) (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => if d = 0 then 1 else k * d)
      = k * (shell t).sum id + (if 0 ∈ shell t then 1 else 0) := by
  have hpt : ∀ d : Nat, (if d = 0 then 1 else k * d) = k * d + (if 0 = d then 1 else 0) := by
    intro d
    by_cases h : d = 0
    · subst h; simp
    · simp [h, Ne.symm h]
  calc (shell t).sum (fun d => if d = 0 then 1 else k * d)
      = (shell t).sum (fun d => k * d + (if 0 = d then 1 else 0)) :=
        Finset.sum_congr rfl (fun d _ => hpt d)
    _ = (shell t).sum (fun d => k * d) + (shell t).sum (fun d => if 0 = d then 1 else 0) :=
        Finset.sum_add_distrib
    _ = k * (shell t).sum id + (if 0 ∈ shell t then 1 else 0) := by
        rw [shell_sum_mul]
        simp [Finset.sum_ite_eq]

#print axioms shell_sum_linear

/-- The same with sigma evaluated: k * #subm(r t) * (2t - 1 - 2 r t) + eps. -/
theorem shell_sum_linear_form (k : Nat) (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => if d = 0 then 1 else k * d)
      = k * ((subm (r t)).card * (2 * t - 1 - 2 * r t)) + (if 0 ∈ shell t then 1 else 0) := by
  rw [shell_sum_linear k t ht, sigma_shell t ht]

#print axioms shell_sum_linear_form

/- ---------- the inverse direction ---------- -/

/-- **Triangularity.**  If two level-size sequences agree on level 0 and have
    the same number of zeroes at every time, they agree on every level: level t
    is the only unknown in the equation at time t. -/
theorem shells_determine_levels (c c' : Nat → Nat) (h0 : c 0 = c' 0)
    (h : ∀ t : Nat, 1 ≤ t → (shell t).sum c = (shell t).sum c') :
    ∀ t : Nat, c t = c' t := by
  intro t
  induction t using Nat.strong_induction_on with
  | _ t ih =>
    rcases t with _ | n
    · exact h0
    · have ht : 1 ≤ n + 1 := by omega
      have hT : n + 1 ∈ shell (n + 1) := shell_mem_self (n + 1) ht
      have e1 := Finset.add_sum_erase (shell (n + 1)) c hT
      have e2 := Finset.add_sum_erase (shell (n + 1)) c' hT
      have hrest : ((shell (n + 1)).erase (n + 1)).sum c
          = ((shell (n + 1)).erase (n + 1)).sum c' := by
        refine Finset.sum_congr rfl (fun d hd => ?_)
        rw [Finset.mem_erase] at hd
        obtain ⟨hne, hmem⟩ := hd
        have hle : d ≤ n + 1 := (mem_shell.mp hmem).1
        rcases d with _ | m
        · exact h0
        · exact ih (m + 1) (by omega)
      have hh := h (n + 1) ht
      rw [← e1, ← e2, hrest] at hh
      exact Nat.add_right_cancel hh

#print axioms shells_determine_levels

end Rule129
end OEIS
