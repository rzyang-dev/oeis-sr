/-
Instances: the all-equal rule on the b-ary tree.

Vertices are words over Fin b; the level is the length (the depth from the
root).  The neighbourhood of x is {x, parent x} together with all b children.
Level sets have size b^d, so the geometry is as far from a lattice as one
can get, yet (H1)-(H4) hold and the root carries the same middle column.
-/
import Universal

namespace OEIS
namespace Rule129

section BTree

variable {b : Nat}

def blev (x : List (Fin b)) : Nat := x.length

def bnb (x : List (Fin b)) : Finset (List (Fin b)) :=
  insert x (insert x.dropLast ((Finset.univ : Finset (Fin b)).image (fun i => x ++ [i])))

theorem bnb_cases {x y : List (Fin b)} (h : y ∈ bnb x) :
    y = x ∨ y = x.dropLast ∨ ∃ i : Fin b, y = x ++ [i] := by
  rw [bnb] at h
  rcases Finset.mem_insert.mp h with h | h
  · exact Or.inl h
  · rcases Finset.mem_insert.mp h with h | h
    · exact Or.inr (Or.inl h)
    · obtain ⟨i, -, hi⟩ := Finset.mem_image.mp h
      exact Or.inr (Or.inr ⟨i, hi.symm⟩)

theorem bnb_mem (x : List (Fin b)) : x ∈ bnb x := by
  rw [bnb]
  exact Finset.mem_insert_self _ _

theorem bnb_bound {x y : List (Fin b)} (h : y ∈ bnb x) :
    blev y + 1 ≥ blev x ∧ blev y ≤ blev x + 1 := by
  rcases bnb_cases h with h | h | ⟨i, h⟩
  · rw [h]; simp [blev]
  · rw [h]; simp only [blev, List.length_dropLast]; omega
  · rw [h]; simp only [blev, List.length_append, List.length_singleton]; omega

theorem bnb_prev (x : List (Fin b)) (h : 1 ≤ blev x) :
    ∃ y ∈ bnb x, blev y = blev x - 1 := by
  refine ⟨x.dropLast, ?_, ?_⟩
  · rw [bnb]
    exact Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)
  · simp only [blev]
    exact List.length_dropLast

theorem bnb_next (hb : 0 < b) (x : List (Fin b)) :
    ∃ y ∈ bnb x, blev y = blev x + 1 := by
  refine ⟨x ++ [⟨0, hb⟩], ?_, ?_⟩
  · rw [bnb]
    exact Finset.mem_insert_of_mem (Finset.mem_insert_of_mem
      (Finset.mem_image.mpr ⟨⟨0, hb⟩, Finset.mem_univ _, rfl⟩))
  · simp [blev]

/-- The all-equal rule on the b-ary tree: the root is 0 exactly at t = 2^k - 1. -/
theorem btree_middle (hb : 0 < b) (t : Nat) (ht : 1 ≤ t) :
    ustate blev (bnb (b := b)) t [] = 0 ↔ ∃ k : Nat, 1 ≤ k ∧ t = 2 ^ k - 1 := by
  have hmem : UMem (bnb (b := b)) := fun x => bnb_mem x
  have hbnd : UBound blev (bnb (b := b)) := fun x y h => bnb_bound h
  have hprev : UPrev blev (bnb (b := b)) := fun x h => bnb_prev x h
  have hnext : UNext blev (bnb (b := b)) := fun x => bnb_next hb x
  exact universal_middle_zero blev (bnb (b := b)) hmem hbnd hprev hnext [] (by simp [blev]) t ht

#print axioms bnb_bound
#print axioms bnb_prev
#print axioms bnb_next
#print axioms btree_middle

end BTree
section MooreD

variable {D : Nat}

/-- The Chebyshev level on the quarter lattice of dimension D. -/
def dlev (x : Fin D → Nat) : Nat := Finset.univ.sup x

/-- The 3^D Moore box around x, written as the image of the offset vectors. -/
def dnb (x : Fin D → Nat) : Finset (Fin D → Nat) :=
  (Finset.univ : Finset (Fin D → Fin 3)).image (fun σ i => x i + (σ i).val - 1)

theorem dnb_mem (x : Fin D → Nat) : x ∈ dnb x := by
  refine Finset.mem_image.mpr ⟨fun _ => ⟨1, by decide⟩, Finset.mem_univ _, ?_⟩
  funext i
  simp

theorem dnb_bound {x y : Fin D → Nat} (h : y ∈ dnb x) :
    dlev y + 1 ≥ dlev x ∧ dlev y ≤ dlev x + 1 := by
  obtain ⟨σ, -, rfl⟩ := Finset.mem_image.mp h
  have hup : ∀ i, x i + (σ i).val - 1 ≤ x i + 1 := by
    intro i
    have := (σ i).isLt
    omega
  have hdn : ∀ i, x i ≤ x i + (σ i).val - 1 + 1 := by
    intro i; omega
  constructor
  · simp only [dlev]
    refine Finset.sup_le_iff.mpr ?_
    intro i _
    have hlow : x i + (σ i).val - 1 ≤ Finset.univ.sup (fun j => x j + (σ j).val - 1) :=
      Finset.le_sup (f := fun j => x j + (σ j).val - 1) (Finset.mem_univ i)
    have := hdn i
    omega
  · simp only [dlev]
    refine Finset.sup_le_iff.mpr ?_
    intro i _
    have hle : x i ≤ Finset.univ.sup x := Finset.le_sup (f := x) (Finset.mem_univ i)
    have := hup i
    omega

theorem dnb_prev (hD : 0 < D) (x : Fin D → Nat) (h : 1 ≤ dlev x) :
    ∃ y ∈ dnb x, dlev y = dlev x - 1 := by
  haveI : Nonempty (Fin D) := ⟨⟨0, hD⟩⟩
  obtain ⟨i₀, -, hi₀⟩ := Finset.exists_mem_eq_sup (s := Finset.univ) Finset.univ_nonempty x
  have h1 : 1 ≤ Finset.univ.sup x := by simpa [dlev] using h
  refine ⟨fun i => x i - 1, ?_, ?_⟩
  · refine Finset.mem_image.mpr ⟨fun _ => ⟨0, by decide⟩, Finset.mem_univ _, ?_⟩
    funext i
    simp
  · simp only [dlev] at hi₀ ⊢
    refine le_antisymm ?_ ?_
    · refine Finset.sup_le_iff.mpr ?_
      intro i _
      have hle : x i ≤ Finset.univ.sup x := Finset.le_sup (f := x) (Finset.mem_univ i)
      exact Nat.sub_le_sub_right hle 1
    · have hle : x i₀ - 1 ≤ Finset.univ.sup (fun j => x j - 1) :=
        Finset.le_sup (f := fun j => x j - 1) (Finset.mem_univ i₀)
      have he : Finset.univ.sup x - 1 = x i₀ - 1 := by rw [hi₀]
      rw [he]
      exact hle

theorem dnb_next (hD : 0 < D) (x : Fin D → Nat) :
    ∃ y ∈ dnb x, dlev y = dlev x + 1 := by
  haveI : Nonempty (Fin D) := ⟨⟨0, hD⟩⟩
  obtain ⟨i₀, -, hi₀⟩ := Finset.exists_mem_eq_sup (s := Finset.univ) Finset.univ_nonempty x
  refine ⟨fun i => x i + 1, ?_, ?_⟩
  · refine Finset.mem_image.mpr ⟨fun _ => ⟨2, by decide⟩, Finset.mem_univ _, ?_⟩
    funext i
    simp
  · simp only [dlev] at hi₀ ⊢
    refine le_antisymm ?_ ?_
    · refine Finset.sup_le_iff.mpr ?_
      intro i _
      have hle : x i ≤ Finset.univ.sup x := Finset.le_sup (f := x) (Finset.mem_univ i)
      exact Nat.add_le_add_right hle 1
    · have hle : x i₀ + 1 ≤ Finset.univ.sup (fun j => x j + 1) :=
        Finset.le_sup (f := fun j => x j + 1) (Finset.mem_univ i₀)
      have he : Finset.univ.sup x + 1 = x i₀ + 1 := by rw [hi₀]
      rw [he]
      exact hle

/-- The 3^D Moore box in every dimension D >= 1 carries the same middle column. -/
theorem mooreD_middle (hD : 0 < D) (t : Nat) (ht : 1 ≤ t) :
    ustate dlev (dnb (D := D)) t (fun _ => 0) = 0 ↔ ∃ k : Nat, 1 ≤ k ∧ t = 2 ^ k - 1 := by
  have hmem : UMem (dnb (D := D)) := fun x => dnb_mem x
  have hbnd : UBound dlev (dnb (D := D)) := fun x y h => dnb_bound h
  have hprev : UPrev dlev (dnb (D := D)) := fun x h => dnb_prev hD x h
  have hnext : UNext dlev (dnb (D := D)) := fun x => dnb_next hD x
  exact universal_middle_zero dlev (dnb (D := D)) hmem hbnd hprev hnext _
    (by simp [dlev]) t ht

#print axioms dnb_bound
#print axioms dnb_prev
#print axioms dnb_next
#print axioms mooreD_middle

end MooreD

end Rule129
end OEIS