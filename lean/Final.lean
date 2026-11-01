import Shells
import Instances

namespace OEIS
namespace Rule129

/- ============================================================
   Part 1.  The zero count is the sum of the level sizes.

   This is the abstract form of  #Z(t) = sum_{d in S(t)} c_d:
   the zero set is exactly the union of the shells, so its size
   is the sum over the shells of the size of each level, and the
   geometry enters only through those level sizes c_d.
   ============================================================ -/

section General

variable {X : Type} [DecidableEq X] [Fintype X]

/-- **The zero set is the disjoint union of the level sets over the shell.** -/
theorem zero_set_eq_biUnion (lev : X → Nat) (nbhd : X → Finset X)
    (hm : UMem nbhd) (hb : UBound lev nbhd) (hp : UPrev lev nbhd) (hn : UNext lev nbhd)
    (t : Nat) (ht : 1 ≤ t) :
    (Finset.univ.filter (fun x => ustate lev nbhd t x = 0))
      = (shell t).biUnion (fun d => Finset.univ.filter (fun x => lev x = d)) := by
  ext x
  simp only [Finset.mem_filter, Finset.mem_univ, true_and, Finset.mem_biUnion]
  constructor
  · intro hz
    exact ⟨lev x, (universal_zero_iff lev nbhd hm hb hp hn t ht x).mp hz, rfl⟩
  · rintro ⟨d, hd, hxd⟩
    have hx : lev x ∈ shell t := by rw [hxd]; exact hd
    exact (universal_zero_iff lev nbhd hm hb hp hn t ht x).mpr hx

/-- **Zeros = sum of the shell sizes.**
    In any geometry satisfying (H1)-(H4) over a finite space, the number of
    0-cells at time t is the sum, over the levels in the shell set, of the
    number of cells on that level. -/
theorem zero_card_eq_sum_levels (lev : X → Nat) (nbhd : X → Finset X)
    (hm : UMem nbhd) (hb : UBound lev nbhd) (hp : UPrev lev nbhd) (hn : UNext lev nbhd)
    (t : Nat) (ht : 1 ≤ t) :
    (Finset.univ.filter (fun x => ustate lev nbhd t x = 0)).card
      = (shell t).sum (fun d => (Finset.univ.filter (fun x => lev x = d)).card) := by
  have hmem : ∀ x ∈ Finset.univ.filter (fun x => ustate lev nbhd t x = 0), lev x ∈ shell t := by
    intro x hx
    rw [Finset.mem_filter] at hx
    exact (universal_zero_iff lev nbhd hm hb hp hn t ht x).mp hx.2
  rw [Finset.card_eq_sum_card_fiberwise hmem]
  refine Finset.sum_congr rfl (fun d hd => ?_)
  have hset : (Finset.univ.filter (fun x => ustate lev nbhd t x = 0)).filter
        (fun x => lev x = d)
      = Finset.univ.filter (fun x => lev x = d) := by
    ext x
    simp only [Finset.mem_filter, Finset.mem_univ, true_and]
    constructor
    · rintro ⟨_, hx⟩
      exact hx
    · intro hx
      refine ⟨?_, hx⟩
      exact (universal_zero_iff lev nbhd hm hb hp hn t ht x).mpr (by rw [hx]; exact hd)
  rw [hset]

#print axioms zero_set_eq_biUnion
#print axioms zero_card_eq_sum_levels

end General

/- ============================================================
   Part 2.  The whole one-dimensional window.

   On the nonnegative half the zeros are exactly the shells.  The
   full window  -t <= j <= t  is the union of the nonnegative copy
   and its mirror image, and the only level that collapses under
   j |-> -j is level 0.  Hence

       #Z(t) = 2 * #shell t - [0 in shell t].
   ============================================================ -/

/-- The nonnegative numbers, as a subset of Int. -/
def posImg (s : Finset Nat) : Finset Int := s.image (fun d : Nat => (d : Int))

/-- The nonpositive numbers, as a subset of Int. -/
def negImg (s : Finset Nat) : Finset Int := s.image (fun d : Nat => -((d : Int)))

/-- The whole window: the integers j with -t <= j <= t. -/
def win (t : Nat) : Finset Int :=
  posImg (Finset.range (t + 1)) ∪ negImg (Finset.range (t + 1))

theorem mem_win {t : Nat} {j : Int} :
    j ∈ win t ↔ ∃ d : Nat, d ≤ t ∧ (j = (d : Int) ∨ j = -((d : Int))) := by
  simp only [win, posImg, negImg, Finset.mem_union, Finset.mem_image, Finset.mem_range]
  constructor
  · rintro (⟨d, hd, h⟩ | ⟨d, hd, h⟩)
    · exact ⟨d, by omega, Or.inl h.symm⟩
    · exact ⟨d, by omega, Or.inr h.symm⟩
  · rintro ⟨d, hd, h | h⟩
    · exact Or.inl ⟨d, by omega, h.symm⟩
    · exact Or.inr ⟨d, by omega, h.symm⟩

#print axioms mem_win

/-- **The zeros of the window are two copies of the shell, one on each side.** -/
theorem row_zero_win_eq (t : Nat) (ht : 1 ≤ t) :
    (win t).filter (fun j => row t j = 0) = posImg (shell t) ∪ negImg (shell t) := by
  ext j
  constructor
  · intro hj
    rw [Finset.mem_filter] at hj
    obtain ⟨hjw, hjz⟩ := hj
    obtain ⟨d, hd, h | h⟩ := mem_win.mp hjw
    · refine Finset.mem_union.mpr (Or.inl ?_)
      have hsh : d ∈ shell t := by
        have hz' := (row_zero_iff_shell t ht j).mp hjz
        rwa [h, Int.natAbs_natCast] at hz'
      exact Finset.mem_image.mpr ⟨d, hsh, h.symm⟩
    · refine Finset.mem_union.mpr (Or.inr ?_)
      have hsh : d ∈ shell t := by
        have hz' := (row_zero_iff_shell t ht j).mp hjz
        rwa [h, Int.natAbs_neg, Int.natAbs_natCast] at hz'
      exact Finset.mem_image.mpr ⟨d, hsh, h.symm⟩
  · intro hj
    rw [Finset.mem_union] at hj
    rcases hj with him | him
    · obtain ⟨d, hd, h⟩ := Finset.mem_image.mp him
      refine Finset.mem_filter.mpr ⟨mem_win.mpr ⟨d, (mem_shell.mp hd).1, Or.inl h.symm⟩, ?_⟩
      rw [row_zero_iff_shell t ht, ← h, Int.natAbs_natCast]
      exact hd
    · obtain ⟨d, hd, h⟩ := Finset.mem_image.mp him
      refine Finset.mem_filter.mpr ⟨mem_win.mpr ⟨d, (mem_shell.mp hd).1, Or.inr h.symm⟩, ?_⟩
      rw [row_zero_iff_shell t ht, ← h, Int.natAbs_neg, Int.natAbs_natCast]
      exact hd

#print axioms row_zero_win_eq

/-- The two copies of the shell meet only in the origin. -/
theorem posImg_inter_negImg (s : Finset Nat) :
    posImg s ∩ negImg s = if 0 ∈ s then {(0 : Int)} else ∅ := by
  ext j
  constructor
  · intro hj
    rw [Finset.mem_inter] at hj
    obtain ⟨h1, h2⟩ := hj
    obtain ⟨d, hd, hdj⟩ := Finset.mem_image.mp h1
    obtain ⟨e, he, hej⟩ := Finset.mem_image.mp h2
    have heq : (d : Int) = -((e : Int)) := by rw [hdj, ← hej]
    have he0 : (0 : Int) ≤ (e : Int) := by exact_mod_cast Nat.zero_le e
    have hd0 : d = 0 := by omega
    have h0 : (0 : Nat) ∈ s := hd0 ▸ hd
    have hj0 : j = 0 := by rw [← hdj, hd0]; simp
    rw [if_pos h0, hj0]
    simp
  · intro hj
    by_cases h0 : 0 ∈ s
    · rw [if_pos h0, Finset.mem_singleton] at hj
      subst hj
      rw [Finset.mem_inter]
      exact ⟨Finset.mem_image.mpr ⟨0, h0, rfl⟩, Finset.mem_image.mpr ⟨0, h0, rfl⟩⟩
    · rw [if_neg h0] at hj
      exact absurd hj (by simp)

#print axioms posImg_inter_negImg

/-- **#Z(t) = 2 #shell t - [0 in shell t]**  in the full one-dimensional window. -/
theorem row_zero_win_card (t : Nat) (ht : 1 ≤ t) :
    ((win t).filter (fun j => row t j = 0)).card
      = 2 * (shell t).card - (if 0 ∈ shell t then 1 else 0) := by
  rw [row_zero_win_eq t ht]
  have hpos : (posImg (shell t)).card = (shell t).card :=
    Finset.card_image_of_injective (shell t) (fun a b h => by exact_mod_cast h)
  have hneg : (negImg (shell t)).card = (shell t).card :=
    Finset.card_image_of_injective (shell t) (fun a b h => by
      have h' : ((a : Int)) = ((b : Int)) := by
        exact neg_inj.mp h
      exact_mod_cast h')
  by_cases h0 : 0 ∈ shell t
  · have hinter : posImg (shell t) ∩ negImg (shell t) = {(0 : Int)} := by
      rw [posImg_inter_negImg, if_pos h0]
    have hcard := Finset.card_union_add_card_inter (posImg (shell t)) (negImg (shell t))
    rw [hinter, hpos, hneg, Finset.card_singleton] at hcard
    rw [if_pos h0]
    omega
  · have hinter : posImg (shell t) ∩ negImg (shell t) = ∅ := by
      rw [posImg_inter_negImg, if_neg h0]
    have hcard := Finset.card_union_add_card_inter (posImg (shell t)) (negImg (shell t))
    rw [hinter, hpos, hneg, Finset.card_empty] at hcard
    rw [if_neg h0]
    omega

#print axioms row_zero_win_card

/- ============================================================
   Part 3.  The quadratic Moore geometry.

   Here the levels are the L-shaped quarter shells of the squares,
   so a level holds exactly 2d+1 cells, and the zero count is

       #Z(t) = sum_{d in shell t} (2d+1) = 2 sigma(t) + #shell t
             = 4 * #subm(r t) * (t - r t).
   ============================================================ -/

/-- The quarter-plane box of side t+1. -/
def mbox (t : Nat) : Finset (Nat × Nat) :=
  (Finset.range (t + 1)) ×ˢ (Finset.range (t + 1))

/-- The two arms of the L-shaped level. -/
def armA (d : Nat) : Finset (Nat × Nat) := (Finset.range (d + 1)).image (fun a => (a, d))

def armB (d : Nat) : Finset (Nat × Nat) := (Finset.range (d + 1)).image (fun b => (d, b))

/-- The level d inside the box is the union of the two arms. -/
theorem level_eq (t d : Nat) (hd : d ≤ t) :
    (mbox t).filter (fun p => qlev p = d) = armA d ∪ armB d := by
  ext p
  constructor
  · intro hp
    rw [Finset.mem_filter] at hp
    obtain ⟨hbox, hlev⟩ := hp
    rw [mbox, Finset.mem_product, Finset.mem_range, Finset.mem_range] at hbox
    have hmax : nmax p.1 p.2 = d := hlev
    have hle1 : p.1 ≤ d := by
      unfold nmax at hmax
      by_cases hc : p.1 ≤ p.2
      · rw [if_pos hc] at hmax; omega
      · rw [if_neg hc] at hmax; omega
    have hle2 : p.2 ≤ d := by
      unfold nmax at hmax
      by_cases hc : p.1 ≤ p.2
      · rw [if_pos hc] at hmax; omega
      · rw [if_neg hc] at hmax; omega
    have hone : p.1 = d ∨ p.2 = d := by
      unfold nmax at hmax
      by_cases hc : p.1 ≤ p.2
      · rw [if_pos hc] at hmax; exact Or.inr hmax
      · rw [if_neg hc] at hmax; exact Or.inl hmax
    rcases hone with h | h
    · exact Finset.mem_union.mpr (Or.inr (Finset.mem_image.mpr
        ⟨p.2, Finset.mem_range.mpr (by omega), Prod.ext h.symm rfl⟩))
    · exact Finset.mem_union.mpr (Or.inl (Finset.mem_image.mpr
        ⟨p.1, Finset.mem_range.mpr (by omega), Prod.ext rfl h.symm⟩))
  · intro hp
    rw [Finset.mem_union] at hp
    rcases hp with him | him
    · obtain ⟨a, ha, rfl⟩ := Finset.mem_image.mp him
      rw [Finset.mem_range] at ha
      rw [Finset.mem_filter, mbox, Finset.mem_product, Finset.mem_range, Finset.mem_range]
      refine ⟨⟨by omega, by omega⟩, ?_⟩
      show nmax a d = d
      unfold nmax
      rw [if_pos (by omega)]
    · obtain ⟨b, hb, rfl⟩ := Finset.mem_image.mp him
      rw [Finset.mem_range] at hb
      rw [Finset.mem_filter, mbox, Finset.mem_product, Finset.mem_range, Finset.mem_range]
      refine ⟨⟨by omega, by omega⟩, ?_⟩
      show nmax d b = d
      unfold nmax
      by_cases hc : d ≤ b
      · rw [if_pos hc]; omega
      · rw [if_neg hc]

#print axioms level_eq

/-- The two arms of a level meet only in the corner. -/
theorem arm_inter (d : Nat) : armA d ∩ armB d = {(d, d)} := by
  ext p
  constructor
  · intro hp
    rw [Finset.mem_inter] at hp
    obtain ⟨h1, h2⟩ := hp
    obtain ⟨a, ha, hpa⟩ := Finset.mem_image.mp h1
    obtain ⟨b, hb, hpb⟩ := Finset.mem_image.mp h2
    have hpair : (a, d) = (d, b) := by rw [hpa, hpb]
    have ha' : a = d := congrArg Prod.fst hpair
    rw [Finset.mem_singleton, ← hpa]
    exact Prod.ext ha' rfl
  · intro hp
    rw [Finset.mem_singleton] at hp
    rw [hp, Finset.mem_inter]
    exact ⟨Finset.mem_image.mpr ⟨d, by simp, rfl⟩, Finset.mem_image.mpr ⟨d, by simp, rfl⟩⟩

#print axioms arm_inter

/-- A level of the Moore geometry holds exactly 2d+1 cells. -/
theorem level_card (t d : Nat) (hd : d ≤ t) :
    ((mbox t).filter (fun p => qlev p = d)).card = 2 * d + 1 := by
  rw [level_eq t d hd]
  have hA : (armA d).card = d + 1 := by
    have h := Finset.card_image_of_injective (Finset.range (d + 1))
      (fun a b (hab : ((a : Nat), d) = ((b : Nat), d)) => congrArg Prod.fst hab)
    rw [armA, h, Finset.card_range]
  have hB : (armB d).card = d + 1 := by
    have h := Finset.card_image_of_injective (Finset.range (d + 1))
      (fun a b (hab : ((d : Nat), a) = ((d : Nat), b)) => congrArg Prod.snd hab)
    rw [armB, h, Finset.card_range]
  have hcard := Finset.card_union_add_card_inter (armA d) (armB d)
  rw [arm_inter, Finset.card_singleton, hA, hB] at hcard
  omega

#print axioms level_card

/-- **The Moore zero count is the sum of the level sizes over the shells.** -/
theorem moore_zero_card_sum (t : Nat) (ht : 1 ≤ t) :
    ((mbox t).filter (fun p => ustate qlev qnb t p = 0)).card
      = (shell t).sum (fun d => 2 * d + 1) := by
  set Z := (mbox t).filter (fun p => ustate qlev qnb t p = 0) with hZ
  have hmem : ∀ p ∈ Z, qlev p ∈ shell t := by
    intro p hp
    rw [hZ, Finset.mem_filter] at hp
    exact (universal_zero_iff qlev qnb qnb_mem qnb_bound qnb_prev qnb_next t ht p).mp hp.2
  rw [Finset.card_eq_sum_card_fiberwise hmem]
  refine Finset.sum_congr rfl (fun d hd => ?_)
  have hset : Z.filter (fun p => qlev p = d) = (mbox t).filter (fun p => qlev p = d) := by
    ext p
    simp only [hZ, Finset.mem_filter]
    constructor
    · rintro ⟨⟨hbox, _⟩, hlev⟩
      exact ⟨hbox, hlev⟩
    · rintro ⟨hbox, hlev⟩
      refine ⟨⟨hbox, ?_⟩, hlev⟩
      exact (universal_zero_iff qlev qnb qnb_mem qnb_bound qnb_prev qnb_next t ht p).mpr
        (by rw [hlev]; exact hd)
  rw [hset, level_card t d (mem_shell.mp hd).1]

#print axioms moore_zero_card_sum

/-- **#Z(t) = 4 #subm(r t) (t - r t)**  in the quarter plane. -/
theorem moore_zero_card_closed (t : Nat) (ht : 1 ≤ t) :
    ((mbox t).filter (fun p => ustate qlev qnb t p = 0)).card
      = 4 * (subm (r t)).card * (t - r t) := by
  rw [moore_zero_card_sum t ht]
  have hsplit : (shell t).sum (fun d => 2 * d + 1)
      = 2 * (shell t).sum id + (shell t).card := by
    rw [Finset.sum_add_distrib, ← Finset.mul_sum]
    simp
  rw [hsplit, sigma_shell t ht, card_shell t ht]
  have hb := two_mul_r_add_one_le t ht
  set N := (subm (r t)).card with hN
  set X := 2 * t - 1 - 2 * r t with hX
  have hA : X + 1 = 2 * (t - r t) := by rw [hX]; omega
  calc 2 * (N * X) + 2 * N = N * (2 * X + 2) := by ring
    _ = N * (2 * (X + 1)) := by ring
    _ = N * (2 * (2 * (t - r t))) := by rw [hA]
    _ = 4 * N * (t - r t) := by ring

#print axioms moore_zero_card_closed

/- ============================================================
   Part 4.  Every one of these counts is a power of two.

   The submasks of r come in doubling pairs, so #subm r is 2^k;
   the shell is two copies of the submask set, the window is two
   copies of the shell minus the origin, and t - r t is a power
   of two, so the Moore count is a power of two as well.
   ============================================================ -/

/-- t - r t is the largest power of two not exceeding t. -/
theorem t_sub_r_eq_pow (t : Nat) (ht : 1 ≤ t) : t - r t = 2 ^ Nat.log2 t := by
  have hle : 2 ^ Nat.log2 t ≤ t := Nat.log2_self_le (by omega)
  rw [r_eq_t_sub_pow t ht, Nat.sub_sub_self hle]

#print axioms t_sub_r_eq_pow

/-- **The number of submasks of r is a power of two.** -/
theorem exists_pow_card_subm (r : Nat) : ∃ k : Nat, (subm r).card = 2 ^ k := by
  induction r using Nat.strong_induction_on with
  | _ r ih =>
    rcases r with _ | _ | k
    · exact ⟨0, by decide⟩
    · exact ⟨1, by decide⟩
    · have hlt : (k + 2) / 2 < k + 2 := Nat.div_lt_self (by omega) (by decide)
      obtain ⟨j, hj⟩ := ih ((k + 2) / 2) hlt
      have hdm := Nat.div_add_mod (k + 2) 2
      have hlt2 := Nat.mod_lt (k + 2) (by decide : 0 < 2)
      interval_cases h : (k + 2) % 2
      · have he : k + 2 = 2 * ((k + 2) / 2) := by omega
        rw [he, card_subm_two_mul, hj]
        exact ⟨j, rfl⟩
      · have he : k + 2 = 2 * ((k + 2) / 2) + 1 := by omega
        rw [he, card_subm_two_mul_add_one, hj]
        exact ⟨j + 1, by rw [Nat.pow_succ, Nat.mul_comm (2 ^ j) 2]⟩

#print axioms exists_pow_card_subm

/-- **The shell size is a power of two.** -/
theorem exists_pow_card_shell (t : Nat) (ht : 1 ≤ t) :
    ∃ k : Nat, (shell t).card = 2 ^ k := by
  obtain ⟨j, hj⟩ := exists_pow_card_subm (r t)
  rw [card_shell t ht, hj]
  exact ⟨j + 1, by rw [Nat.pow_succ, Nat.mul_comm (2 ^ j) 2]⟩

#print axioms exists_pow_card_shell

/-- **The Moore zero count is a power of two.** -/
theorem moore_zero_card_pow (t : Nat) (ht : 1 ≤ t) :
    ∃ k : Nat, ((mbox t).filter (fun p => ustate qlev qnb t p = 0)).card = 2 ^ k := by
  obtain ⟨j, hj⟩ := exists_pow_card_subm (r t)
  refine ⟨j + 2 + Nat.log2 t, ?_⟩
  rw [moore_zero_card_closed t ht, hj, t_sub_r_eq_pow t ht]
  have e : j + 2 + Nat.log2 t = 2 + j + Nat.log2 t := by omega
  rw [e, show (4 : Nat) = 2 ^ 2 from rfl, ← Nat.pow_add, ← Nat.pow_add]

#print axioms moore_zero_card_pow

/-- **The one-dimensional zero count is a power of two, except at t = 2^i - 1,
    where it is one less.** -/
theorem row_zero_win_card_pow (t : Nat) (ht : 1 ≤ t) :
    ∃ k : Nat,
      ((win t).filter (fun j => row t j = 0)).card = 2 ^ k
        ∨ ((win t).filter (fun j => row t j = 0)).card + 1 = 2 ^ k := by
  obtain ⟨j, hj⟩ := exists_pow_card_shell t ht
  by_cases h0 : 0 ∈ shell t
  · refine ⟨j + 1, Or.inr ?_⟩
    have hpos : 0 < 2 * 2 ^ j := by positivity
    rw [row_zero_win_card t ht, if_pos h0, hj, Nat.pow_succ, Nat.mul_comm (2 ^ j) 2]
    exact Nat.sub_add_cancel (Nat.succ_le_of_lt hpos)
  · refine ⟨j + 1, Or.inl ?_⟩
    rw [row_zero_win_card t ht, if_neg h0, hj, Nat.pow_succ]
    omega

#print axioms row_zero_win_card_pow

end Rule129
end OEIS
