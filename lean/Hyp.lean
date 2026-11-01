import Brocot

namespace OEIS
namespace Rule129

/-! ### Counting super-binary representations

A super-binary representation of n is a pair (u, h) of naturals with disjoint
binary expansions (u &&& h = 0) and u + 2 * h = n.  We show that their number
is Stern's diatomic sequence at n + 1. -/

/-- The finset of super-binary representations of n. -/
def Hyp (n : Nat) : Finset (Nat × Nat) :=
  ((Finset.range (n + 1)) ×ˢ (Finset.range (n / 2 + 1))).filter
    (fun p => (p.1 &&& p.2 = 0 ∧ p.1 + 2 * p.2 = n))

/-- the doubling map appearing in the odd recursion -/
def hOdd (p : Nat × Nat) : Nat × Nat := (2 * p.1 + 1, 2 * p.2)

/-- the doubling map with even second coordinate -/
def hEven (p : Nat × Nat) : Nat × Nat := (2 * p.1, 2 * p.2)

/-- the doubling map with odd second coordinate -/
def hEvenOdd (p : Nat × Nat) : Nat × Nat := (2 * p.1, 2 * p.2 + 1)

/-! ### Membership -/

/-- The range bounds in the definition of Hyp are redundant. -/
theorem mem_Hyp {n a b : Nat} : (a, b) ∈ Hyp n ↔ a &&& b = 0 ∧ a + 2 * b = n := by
  simp only [Hyp, Finset.mem_filter, Finset.mem_product, Finset.mem_range]
  constructor
  · rintro ⟨-, h1, h2⟩
    exact ⟨h1, h2⟩
  · rintro ⟨h1, h2⟩
    exact ⟨⟨by omega, by omega⟩, h1, h2⟩

theorem Hyp_zero : Hyp 0 = {(0, 0)} := by
  ext p
  obtain ⟨a, b⟩ := p
  rw [mem_Hyp]
  simp only [Finset.mem_singleton, Prod.mk.injEq]
  constructor
  · rintro ⟨-, h2⟩
    exact ⟨by omega, by omega⟩
  · rintro ⟨rfl, rfl⟩
    exact ⟨by simp, by simp⟩

/-! ### Bit lemmas for the parity patterns -/

theorem land_odd_two_mul (u h : Nat) : (2 * u + 1) &&& (2 * h) = 0 ↔ u &&& h = 0 := by
  have h2 : 2 * h / 2 = h := by omega
  rw [land_odd_left u (2 * h), h2]
  constructor
  · exact fun p => p.2
  · intro p
    exact ⟨by omega, p⟩

theorem land_two_mul_two_mul (u h : Nat) : (2 * u) &&& (2 * h) = 0 ↔ u &&& h = 0 := by
  have h2 : 2 * h / 2 = h := by omega
  rw [land_two_mul u (2 * h), h2]
  constructor <;> intro hh <;> omega

theorem land_two_mul_two_mul_add_one (u h : Nat) :
    (2 * u) &&& (2 * h + 1) = 0 ↔ u &&& h = 0 := by
  have h2 : (2 * h + 1) / 2 = h := by omega
  rw [land_two_mul u (2 * h + 1), h2]
  constructor <;> intro hh <;> omega

/-! ### Injectivity of the three maps -/

theorem hOdd_inj : Function.Injective hOdd := by
  intro p q h
  have h1 : 2 * p.1 + 1 = 2 * q.1 + 1 := congrArg Prod.fst h
  have h2 : 2 * p.2 = 2 * q.2 := congrArg Prod.snd h
  exact Prod.ext (by omega) (by omega)

theorem hEven_inj : Function.Injective hEven := by
  intro p q h
  have h1 : 2 * p.1 = 2 * q.1 := congrArg Prod.fst h
  have h2 : 2 * p.2 = 2 * q.2 := congrArg Prod.snd h
  exact Prod.ext (by omega) (by omega)

theorem hEvenOdd_inj : Function.Injective hEvenOdd := by
  intro p q h
  have h1 : 2 * p.1 = 2 * q.1 := congrArg Prod.fst h
  have h2 : 2 * p.2 + 1 = 2 * q.2 + 1 := congrArg Prod.snd h
  exact Prod.ext (by omega) (by omega)

/-! ### The two recursions -/

theorem Hyp_odd (m : Nat) : Hyp (2 * m + 1) = (Hyp m).image hOdd := by
  ext p
  obtain ⟨a, b⟩ := p
  rw [mem_Hyp, Finset.mem_image]
  constructor
  · rintro ⟨hland, harith⟩
    obtain ⟨u, hu | hu⟩ := half_split a
    · omega
    · rw [hu] at hland
      obtain ⟨hbmod, hkey⟩ := (land_odd_left u b).mp hland
      obtain ⟨h, hb | hb⟩ := half_split b
      · have hdiv : b / 2 = h := by omega
        have hkey' : u &&& h = 0 := by rwa [hdiv] at hkey
        have harith' : u + 2 * h = m := by omega
        refine ⟨(u, h), ?_, ?_⟩
        · rw [mem_Hyp]
          exact ⟨hkey', harith'⟩
        · show (2 * u + 1, 2 * h) = (a, b)
          rw [hu, hb]
      · omega
  · rintro ⟨⟨u, h⟩, hmem, heq⟩
    rw [mem_Hyp] at hmem
    obtain ⟨hland, harith⟩ := hmem
    have heq' : (2 * u + 1, 2 * h) = (a, b) := heq
    simp only [Prod.mk.injEq] at heq'
    obtain ⟨h1, h2⟩ := heq'
    rw [← h1, ← h2]
    exact ⟨(land_odd_two_mul u h).mpr hland, by omega⟩

theorem Hyp_even (m : Nat) (hm : 1 ≤ m) :
    Hyp (2 * m) = (Hyp m).image hEven ∪ (Hyp (m - 1)).image hEvenOdd := by
  ext p
  obtain ⟨a, b⟩ := p
  rw [mem_Hyp, Finset.mem_union, Finset.mem_image, Finset.mem_image]
  constructor
  · rintro ⟨hland, harith⟩
    obtain ⟨u, hu | hu⟩ := half_split a
    · rw [hu] at hland
      have hkey : u &&& (b / 2) = 0 := (land_two_mul_iff u b).mp hland
      obtain ⟨h, hb | hb⟩ := half_split b
      · left
        have hdiv : b / 2 = h := by omega
        have harith' : u + 2 * h = m := by omega
        refine ⟨(u, h), ?_, ?_⟩
        · rw [mem_Hyp]
          exact ⟨by rwa [hdiv] at hkey, harith'⟩
        · show (2 * u, 2 * h) = (a, b)
          rw [hu, hb]
      · right
        have hdiv : b / 2 = h := by omega
        have harith' : u + 2 * h = m - 1 := by omega
        refine ⟨(u, h), ?_, ?_⟩
        · rw [mem_Hyp]
          exact ⟨by rwa [hdiv] at hkey, harith'⟩
        · show (2 * u, 2 * h + 1) = (a, b)
          rw [hu, hb]
    · omega
  · rintro (⟨⟨u, h⟩, hmem, heq⟩ | ⟨⟨u, h⟩, hmem, heq⟩)
    · rw [mem_Hyp] at hmem
      obtain ⟨hland, harith⟩ := hmem
      have heq' : (2 * u, 2 * h) = (a, b) := heq
      simp only [Prod.mk.injEq] at heq'
      obtain ⟨h1, h2⟩ := heq'
      rw [← h1, ← h2]
      exact ⟨(land_two_mul_two_mul u h).mpr hland, by omega⟩
    · rw [mem_Hyp] at hmem
      obtain ⟨hland, harith⟩ := hmem
      have heq' : (2 * u, 2 * h + 1) = (a, b) := heq
      simp only [Prod.mk.injEq] at heq'
      obtain ⟨h1, h2⟩ := heq'
      rw [← h1, ← h2]
      exact ⟨(land_two_mul_two_mul_add_one u h).mpr hland, by omega⟩

/-! ### Cardinalities -/

theorem disjoint_Hyp_images (m : Nat) :
    Disjoint ((Hyp m).image hEven) ((Hyp (m - 1)).image hEvenOdd) := by
  rw [Finset.disjoint_left]
  intro x hx hy
  rw [Finset.mem_image] at hx hy
  obtain ⟨⟨a, b⟩, -, hp⟩ := hx
  obtain ⟨⟨c, d⟩, -, hq⟩ := hy
  have hp' : (2 * a, 2 * b) = x := hp
  have hq' : (2 * c, 2 * d + 1) = x := hq
  have hcon : (2 * a, 2 * b) = (2 * c, 2 * d + 1) := by rw [hp', hq']
  simp only [Prod.mk.injEq] at hcon
  omega

theorem card_Hyp_odd (m : Nat) : (Hyp (2 * m + 1)).card = (Hyp m).card := by
  rw [Hyp_odd m, Finset.card_image_of_injective _ hOdd_inj]

theorem card_Hyp_even (m : Nat) (hm : 1 ≤ m) :
    (Hyp (2 * m)).card = (Hyp m).card + (Hyp (m - 1)).card := by
  rw [Hyp_even m hm, Finset.card_union_of_disjoint (disjoint_Hyp_images m),
    Finset.card_image_of_injective _ hEven_inj,
    Finset.card_image_of_injective _ hEvenOdd_inj]

/-! ### Main theorem -/

theorem card_Hyp (n : Nat) : (Hyp n).card = fusc (n + 1) := by
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    obtain ⟨m, hm | hm⟩ := half_split n
    · rcases Nat.eq_zero_or_pos m with h0 | hmpos
      · have hn : n = 0 := by omega
        subst hn
        rw [Hyp_zero]
        simp [fusc_one]
      · rw [hm, card_Hyp_even m hmpos, ih m (by omega), ih (m - 1) (by omega)]
        have hsub : (m - 1) + 1 = m := by omega
        rw [hsub, fusc_two_mul_add_one m]
        exact Nat.add_comm _ _
    · rw [hm, card_Hyp_odd m, ih m (by omega)]
      rw [show 2 * m + 1 + 1 = 2 * (m + 1) from by ring, fusc_two_mul]

#print axioms card_Hyp


/-- the cardinality form of the explicit bijection SIGMA_d = Hyp(d) + Hyp(d-1) -/
theorem card_sig_split {d : Nat} (hd : 1 ≤ d) :
    (sig d).card = (Hyp d).card + (Hyp (d - 1)).card := by
  have h1 := card_sig_stern d
  have h2 := card_Hyp d
  have h3 := card_Hyp (d - 1)
  have h4 : d - 1 + 1 = d := by omega
  rw [h4] at h3
  omega

#print axioms card_sig_split

end Rule129
end OEIS
