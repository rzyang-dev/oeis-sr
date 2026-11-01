
import Mathlib

namespace OEIS
namespace Rule129

theorem t1 (m n : Nat) : 2 * m + 2 * n = 2 * (m + n) := by ring
theorem t2 (m n : Nat) : 2 * m + (2 * n + 1) = 2 * (m + n) + 1 := by ring
theorem t3 (m n : Nat) : 2 * m + 1 + 2 * n = 2 * (m + n) + 1 := by ring
theorem t4 (m n : Nat) : 2 * m + 1 + (2 * n + 1) = 2 * (m + n + 1) := by ring

theorem bit_div_two (n : Nat) : Nat.bit (n.testBit 0) (n / 2) = n := by
  have h : n / 2 = n >>> 1 := by rw [Nat.shiftRight_eq_div_pow, pow_one]
  rw [h, Nat.bit_testBit_zero_shiftRight_one]

theorem half_split (n : Nat) : ∃ a, n = 2 * a ∨ n = 2 * a + 1 := by
  refine ⟨n / 2, ?_⟩
  have h1 := Nat.div_add_mod n 2
  have h2 := Nat.mod_lt n (by decide : 0 < 2)
  omega

theorem par_iff (X : Nat) : X % 2 = 0 ↔ X.testBit 0 = false := by
  conv_lhs => rw [← bit_div_two X]
  rw [Nat.bit_mod_two_eq_zero_iff]
  simp

/-- odd-shift lemma -/
theorem land_odd_left (v X : Nat) :
    (2 * v + 1) &&& X = 0 ↔ X % 2 = 0 ∧ v &&& (X / 2) = 0 := by
  conv_lhs => rw [← bit_div_two X]
  show Nat.bit true v &&& Nat.bit (X.testBit 0) (X / 2) = 0 ↔
    X % 2 = 0 ∧ v &&& (X / 2) = 0
  rw [Nat.land_bit]
  rw [par_iff]
  cases hb : X.testBit 0
  · simp only [Bool.true_and, true_and]
    show 2 * (v &&& (X / 2)) = 0 ↔ v &&& (X / 2) = 0
    constructor <;> intro h <;> omega
  · simp only [Bool.true_and]
    have hf : (true = false) = False := by simp
    rw [hf, false_and]
    show 2 * (v &&& (X / 2)) + 1 = 0 ↔ False
    have hne : 2 * (v &&& (X / 2)) + 1 ≠ 0 := by omega
    simp

theorem land_add_iff (u h : Nat) : u &&& (u + h) = u ↔ u &&& h = 0 := by
  induction h using Nat.strong_induction_on generalizing u with
  | _ h ih =>
    rcases Nat.eq_zero_or_pos h with h0 | hpos
    · subst h0; simp
    · have haex : ∃ a, u = 2 * a ∨ u = 2 * a + 1 := half_split u
      have hbex : ∃ b, h = 2 * b ∨ h = 2 * b + 1 := half_split h
      obtain ⟨a, ha | ha⟩ := haex
      · obtain ⟨b, hb | hb⟩ := hbex
        · rw [ha, hb, t1]
          show Nat.bit false a &&& Nat.bit false (a + b) = Nat.bit false a ↔
            Nat.bit false a &&& Nat.bit false b = 0
          rw [Nat.land_bit, Nat.land_bit]
          simp only [Bool.false_and]
          show 2 * (a &&& (a + b)) = 2 * a ↔ 2 * (a &&& b) = 0
          have key := ih b (by omega) a
          constructor
          · intro h1
            have h1' : a &&& (a + b) = a := by omega
            have h2' : a &&& b = 0 := key.mp h1'
            omega
          · intro h1
            have h1' : a &&& b = 0 := by omega
            have h2' : a &&& (a + b) = a := key.mpr h1'
            omega
        · rw [ha, hb, t2]
          show Nat.bit false a &&& Nat.bit true (a + b) = Nat.bit false a ↔
            Nat.bit false a &&& Nat.bit true b = 0
          rw [Nat.land_bit, Nat.land_bit]
          simp only [Bool.false_and]
          show 2 * (a &&& (a + b)) = 2 * a ↔ 2 * (a &&& b) = 0
          have key := ih b (by omega) a
          constructor
          · intro h1
            have h1' : a &&& (a + b) = a := by omega
            have h2' : a &&& b = 0 := key.mp h1'
            omega
          · intro h1
            have h1' : a &&& b = 0 := by omega
            have h2' : a &&& (a + b) = a := key.mpr h1'
            omega
      · obtain ⟨b, hb | hb⟩ := hbex
        · rw [ha, hb, t3]
          show Nat.bit true a &&& Nat.bit true (a + b) = Nat.bit true a ↔
            Nat.bit true a &&& Nat.bit false b = 0
          rw [Nat.land_bit, Nat.land_bit]
          simp only [Bool.true_and]
          show 2 * (a &&& (a + b)) + 1 = 2 * a + 1 ↔ 2 * (a &&& b) = 0
          have key := ih b (by omega) a
          constructor
          · intro h1
            have h1' : a &&& (a + b) = a := by omega
            have h2' : a &&& b = 0 := key.mp h1'
            omega
          · intro h1
            have h1' : a &&& b = 0 := by omega
            have h2' : a &&& (a + b) = a := key.mpr h1'
            omega
        · rw [ha, hb, t4]
          show Nat.bit true a &&& Nat.bit false (a + b + 1) = Nat.bit true a ↔
            Nat.bit true a &&& Nat.bit true b = 0
          rw [Nat.land_bit, Nat.land_bit]
          simp only [Bool.true_and]
          show 2 * (a &&& (a + b + 1)) = 2 * a + 1 ↔ 2 * (a &&& b) + 1 = 0
          omega

theorem land_of_le {u B : Nat} (h : u ≤ B) :
    u &&& B = u ↔ u &&& (B - u) = 0 := by
  have hB : B = u + (B - u) := by omega
  conv_lhs => rw [hB]
  exact land_add_iff u (B - u)

theorem land_two_mul (a b : Nat) : (2 * a) &&& b = 2 * (a &&& (b / 2)) := by
  conv_lhs => rw [← bit_div_two b]
  show Nat.bit false a &&& Nat.bit (b.testBit 0) (b / 2) = 2 * (a &&& (b / 2))
  rw [Nat.land_bit]
  cases b.testBit 0
  · rfl
  · rfl

theorem land_two_mul_iff (a b : Nat) : (2 * a) &&& b = 0 ↔ a &&& (b / 2) = 0 := by
  rw [land_two_mul]
  omega

/-- the dead-offset set of distance d -/
def sig (d : Nat) : Finset Nat :=
  (Finset.range (d + 1)).filter (fun u => u &&& ((d - u) / 2) = 0)

theorem mem_sig {d u : Nat} : u ∈ sig d ↔ u ≤ d ∧ u &&& ((d - u) / 2) = 0 := by
  simp [sig]

theorem mem_sig_iff {d u : Nat} :
    u ∈ sig d ↔ u ≤ d ∧ u &&& ((u + d) / 2) = u := by
  rw [mem_sig]
  have hle : (u ≤ (u + d) / 2) ↔ (u ≤ d) := by omega
  have hsub : (u + d) / 2 - u = (d - u) / 2 := by omega
  constructor
  · rintro ⟨h1, h2⟩
    refine ⟨h1, ?_⟩
    rw [← hsub] at h2
    exact (land_of_le (u := u) (B := (u + d) / 2) (hle.mpr h1)).mpr h2
  · rintro ⟨h1, h2⟩
    refine ⟨h1, ?_⟩
    have h3 := (land_of_le (u := u) (B := (u + d) / 2) (hle.mpr h1)).mp h2
    rwa [hsub] at h3

theorem mem_sig_two_mul {e v : Nat} : 2 * v ∈ sig (2 * e) ↔ v ∈ sig e := by
  rw [mem_sig, mem_sig]
  have hd : (2 * e - 2 * v) / 2 = e - v := by omega
  rw [hd]
  have hb : 2 * v ≤ 2 * e ↔ v ≤ e := by omega
  constructor
  · rintro ⟨h1, h2⟩
    exact ⟨hb.mp h1, (land_two_mul_iff v (e - v)).mp h2⟩
  · rintro ⟨h1, h2⟩
    exact ⟨hb.mpr h1, (land_two_mul_iff v (e - v)).mpr h2⟩

theorem mem_sig_two_mul_add_one {e v : Nat} : 2 * v ∈ sig (2 * e + 1) ↔ v ∈ sig e := by
  rw [mem_sig, mem_sig]
  have hd : (2 * e + 1 - 2 * v) / 2 = e - v := by omega
  rw [hd]
  have hb : 2 * v ≤ 2 * e + 1 ↔ v ≤ e := by omega
  constructor
  · rintro ⟨h1, h2⟩
    exact ⟨hb.mp h1, (land_two_mul_iff v (e - v)).mp h2⟩
  · rintro ⟨h1, h2⟩
    exact ⟨hb.mpr h1, (land_two_mul_iff v (e - v)).mpr h2⟩


/-- (C): the odd part of sig (2e) -/
theorem mem_sig_odd_two_mul {e v : Nat} :
    2 * v + 1 ∈ sig (2 * e) ↔ v ∈ sig e ∧ (v + e) % 2 = 1 := by
  rw [mem_sig, mem_sig]
  have hd : (2 * e - (2 * v + 1)) / 2 = e - v - 1 := by omega
  have hb : 2 * v + 1 ≤ 2 * e ↔ v < e := by omega
  rw [hd, hb]
  constructor
  · rintro ⟨h1, h2⟩
    obtain ⟨hp, hq⟩ := (land_odd_left v (e - v - 1)).mp h2
    have hhalf : (e - v - 1) / 2 = (e - v) / 2 := by omega
    have hodd : (v + e) % 2 = 1 := by omega
    exact ⟨⟨by omega, by rwa [hhalf] at hq⟩, hodd⟩
  · rintro ⟨⟨h1, hq⟩, hp⟩
    have hlt : v < e := by omega
    have hhalf : (e - v - 1) / 2 = (e - v) / 2 := by omega
    have hpar : (e - v - 1) % 2 = 0 := by omega
    exact ⟨hlt, (land_odd_left v (e - v - 1)).mpr ⟨hpar, by rwa [hhalf]⟩⟩

/-- (D): the odd part of sig (2e+1) -/
theorem mem_sig_odd_two_mul_add_one {e v : Nat} :
    2 * v + 1 ∈ sig (2 * e + 1) ↔ v ∈ sig e ∧ (v + e) % 2 = 0 := by
  rw [mem_sig, mem_sig]
  have hd : (2 * e + 1 - (2 * v + 1)) / 2 = e - v := by omega
  have hb : 2 * v + 1 ≤ 2 * e + 1 ↔ v ≤ e := by omega
  rw [hd, hb]
  constructor
  · rintro ⟨h1, h2⟩
    obtain ⟨hp, hq⟩ := (land_odd_left v (e - v)).mp h2
    have hev : (e - v) % 2 = (v + e) % 2 := by omega
    exact ⟨⟨h1, hq⟩, by omega⟩
  · rintro ⟨⟨h1, hq⟩, hp⟩
    have hev : (e - v) % 2 = (v + e) % 2 := by omega
    exact ⟨h1, (land_odd_left v (e - v)).mpr ⟨by omega, hq⟩⟩



/-- the "odd" half of sig d: u with u+d odd -/
def pp (d : Nat) : Finset Nat := (sig d).filter (fun v => (v + d) % 2 = 1)
/-- the "even" half of sig d: u with u+d even -/
def qq (d : Nat) : Finset Nat := (sig d).filter (fun v => (v + d) % 2 = 0)

def dblEmb : Nat ↪ Nat := ⟨fun v => 2 * v, by intro x y h; change 2 * x = 2 * y at h; omega⟩
def dbl1Emb : Nat ↪ Nat := ⟨fun v => 2 * v + 1, by
  intro x y h; change 2 * x + 1 = 2 * y + 1 at h; omega⟩

/-! ### the four set decompositions -/

theorem sig_even_two_mul (e : Nat) :
    (sig (2 * e)).filter (fun u => u % 2 = 0) = (sig e).map dblEmb := by
  ext u
  rw [Finset.mem_filter, Finset.mem_map]
  constructor
  · rintro ⟨h1, h2⟩
    have hu : u = 2 * (u / 2) := by
      have h := Nat.div_add_mod u 2
      omega
    have h3 : 2 * (u / 2) ∈ sig (2 * e) := by rw [← hu]; exact h1
    refine ⟨u / 2, mem_sig_two_mul.mp h3, ?_⟩
    show 2 * (u / 2) = u
    omega
  · rintro ⟨v, hv, hvu⟩
    have hvu' : 2 * v = u := hvu
    refine ⟨?_, by omega⟩
    rw [← hvu']
    exact mem_sig_two_mul.mpr hv

theorem sig_odd_two_mul (e : Nat) :
    (sig (2 * e)).filter (fun u => ¬ u % 2 = 0) = (pp e).map dbl1Emb := by
  ext u
  rw [Finset.mem_filter, Finset.mem_map]
  simp only [pp, Finset.mem_filter]
  constructor
  · rintro ⟨h1, h2⟩
    have hu : u = 2 * (u / 2) + 1 := by
      have h := Nat.div_add_mod u 2
      omega
    have h3 : 2 * (u / 2) + 1 ∈ sig (2 * e) := by rw [← hu]; exact h1
    exact ⟨u / 2, mem_sig_odd_two_mul.mp h3, by show 2 * (u / 2) + 1 = u; omega⟩
  · rintro ⟨v, ⟨hv, hp⟩, hvu⟩
    have hvu' : 2 * v + 1 = u := hvu
    refine ⟨?_, by omega⟩
    rw [← hvu']
    exact mem_sig_odd_two_mul.mpr ⟨hv, hp⟩

theorem sig_even_two_mul_add_one (e : Nat) :
    (sig (2 * e + 1)).filter (fun u => u % 2 = 0) = (sig e).map dblEmb := by
  ext u
  rw [Finset.mem_filter, Finset.mem_map]
  constructor
  · rintro ⟨h1, h2⟩
    have hu : u = 2 * (u / 2) := by
      have h := Nat.div_add_mod u 2
      omega
    have h3 : 2 * (u / 2) ∈ sig (2 * e + 1) := by rw [← hu]; exact h1
    refine ⟨u / 2, mem_sig_two_mul_add_one.mp h3, ?_⟩
    show 2 * (u / 2) = u
    omega
  · rintro ⟨v, hv, hvu⟩
    have hvu' : 2 * v = u := hvu
    refine ⟨?_, by omega⟩
    rw [← hvu']
    exact mem_sig_two_mul_add_one.mpr hv

theorem sig_odd_two_mul_add_one (e : Nat) :
    (sig (2 * e + 1)).filter (fun u => ¬ u % 2 = 0) = (qq e).map dbl1Emb := by
  ext u
  rw [Finset.mem_filter, Finset.mem_map]
  simp only [qq, Finset.mem_filter]
  constructor
  · rintro ⟨h1, h2⟩
    have hu : u = 2 * (u / 2) + 1 := by
      have h := Nat.div_add_mod u 2
      omega
    have h3 : 2 * (u / 2) + 1 ∈ sig (2 * e + 1) := by rw [← hu]; exact h1
    exact ⟨u / 2, mem_sig_odd_two_mul_add_one.mp h3, by show 2 * (u / 2) + 1 = u; omega⟩
  · rintro ⟨v, ⟨hv, hp⟩, hvu⟩
    have hvu' : 2 * v + 1 = u := hvu
    refine ⟨?_, by omega⟩
    rw [← hvu']
    exact mem_sig_odd_two_mul_add_one.mpr ⟨hv, hp⟩

/-! ### the four cardinality recursions -/

theorem card_sig_two_mul (e : Nat) :
    (sig (2 * e)).card = (sig e).card + (pp e).card := by
  have h := Finset.card_filter_add_card_filter_not (s := sig (2 * e)) (p := fun u => u % 2 = 0)
  rw [sig_even_two_mul, sig_odd_two_mul, Finset.card_map, Finset.card_map] at h
  omega

theorem card_sig_two_mul_add_one (e : Nat) :
    (sig (2 * e + 1)).card = (sig e).card + (qq e).card := by
  have h := Finset.card_filter_add_card_filter_not (s := sig (2 * e + 1)) (p := fun u => u % 2 = 0)
  rw [sig_even_two_mul_add_one, sig_odd_two_mul_add_one, Finset.card_map, Finset.card_map] at h
  omega

theorem pp_two_mul_eq (e : Nat) :
    pp (2 * e) = (sig (2 * e)).filter (fun u => ¬ u % 2 = 0) := by
  rw [pp]
  apply Finset.filter_congr
  intro u _
  constructor <;> intro h <;> omega

theorem qq_two_mul_eq (e : Nat) :
    qq (2 * e) = (sig (2 * e)).filter (fun u => u % 2 = 0) := by
  rw [qq]
  apply Finset.filter_congr
  intro u _
  constructor <;> intro h <;> omega

theorem pp_two_mul_add_one_eq (e : Nat) :
    pp (2 * e + 1) = (sig (2 * e + 1)).filter (fun u => u % 2 = 0) := by
  rw [pp]
  apply Finset.filter_congr
  intro u _
  constructor <;> intro h <;> omega

theorem qq_two_mul_add_one_eq (e : Nat) :
    qq (2 * e + 1) = (sig (2 * e + 1)).filter (fun u => ¬ u % 2 = 0) := by
  rw [qq]
  apply Finset.filter_congr
  intro u _
  constructor <;> intro h <;> omega

theorem card_pp_two_mul (e : Nat) : (pp (2 * e)).card = (pp e).card := by
  rw [pp_two_mul_eq, sig_odd_two_mul, Finset.card_map]

theorem card_qq_two_mul (e : Nat) : (qq (2 * e)).card = (sig e).card := by
  rw [qq_two_mul_eq, sig_even_two_mul, Finset.card_map]

theorem card_pp_two_mul_add_one (e : Nat) : (pp (2 * e + 1)).card = (sig e).card := by
  rw [pp_two_mul_add_one_eq, sig_even_two_mul_add_one, Finset.card_map]

theorem card_qq_two_mul_add_one (e : Nat) : (qq (2 * e + 1)).card = (qq e).card := by
  rw [qq_two_mul_add_one_eq, sig_odd_two_mul_add_one, Finset.card_map]


/-! ### Stern's diatomic sequence -/

/-- Stern's diatomic sequence (A002487). -/
def fusc : Nat → Nat
  | 0 => 0
  | 1 => 1
  | n + 2 =>
      if (n + 2) % 2 = 0 then fusc ((n + 2) / 2)
      else fusc ((n + 2) / 2) + fusc ((n + 2) / 2 + 1)
termination_by n => n
decreasing_by all_goals omega

theorem fusc_zero : fusc 0 = 0 := fusc.eq_1

theorem fusc_one : fusc 1 = 1 := fusc.eq_2

theorem fusc_two_mul (e : Nat) : fusc (2 * e) = fusc e := by
  rcases e with _ | e
  · rfl
  · have h2 : 2 * (e + 1) = 2 * e + 2 := by ring
    rw [h2, fusc.eq_3, if_pos (by omega : (2 * e + 2) % 2 = 0),
      show (2 * e + 2) / 2 = e + 1 from by omega]

theorem fusc_two_mul_add_one (e : Nat) : fusc (2 * e + 1) = fusc e + fusc (e + 1) := by
  rcases e with _ | e
  · rw [fusc.eq_2, fusc_zero]
  · have h2 : 2 * (e + 1) + 1 = (2 * e + 1) + 2 := by ring
    rw [h2, fusc.eq_3, if_neg (by omega : ¬ ((2 * e + 1) + 2) % 2 = 0),
      show ((2 * e + 1) + 2) / 2 = e + 1 from by omega]

/-! ### the triple recursion -/

theorem sig_zero : sig 0 = {0} := by decide
theorem pp_zero : pp 0 = ∅ := by decide
theorem qq_zero : qq 0 = {0} := by decide

/-- **Stern's recursion**: the three counts at once. -/
theorem stern_triple (d : Nat) :
    (sig d).card = fusc d + fusc (d + 1) ∧
    (pp d).card = fusc d ∧ (qq d).card = fusc (d + 1) := by
  induction d using Nat.strong_induction_on with
  | _ d ih =>
    rcases Nat.eq_zero_or_pos d with h0 | hpos
    · subst h0
      refine ⟨?_, ?_, ?_⟩
      · rw [sig_zero, fusc_zero, fusc_one]; simp
      · rw [pp_zero, fusc_zero]; simp
      · rw [qq_zero, fusc_one]; simp
    · obtain ⟨e, he | he⟩ := half_split d
      · rw [he] at hpos ⊢
        obtain ⟨hA, hp, hq⟩ := ih e (by omega)
        have h1 := card_sig_two_mul e
        have h2 := fusc_two_mul e
        have h3 := fusc_two_mul_add_one e
        have h4 := card_pp_two_mul e
        have h5 := card_qq_two_mul e
        refine ⟨?_, ?_, ?_⟩
        · rw [h1, hA, hp, h2, h3]; ring
        · rw [h4, hp, h2]
        · rw [h5, hA, h3]
      · rw [he] at hpos ⊢
        obtain ⟨hA, hp, hq⟩ := ih e (by omega)
        have h1 := card_sig_two_mul_add_one e
        have h2 := fusc_two_mul_add_one e
        have h7 : 2 * e + 1 + 1 = 2 * e + 2 := by ring
        have h6 : fusc (2 * e + 2) = fusc (e + 1) := by
          rw [show 2 * e + 2 = 2 * (e + 1) from by ring, fusc_two_mul]
        have h4 := card_pp_two_mul_add_one e
        have h5 := card_qq_two_mul_add_one e
        refine ⟨?_, ?_, ?_⟩
        · rw [h7, h1, hA, hq, h2, h6]
        · rw [h4, hA, h2]
        · rw [h7, h5, hq, h6]

/-- **the theorem**: the number of dead moments per block at distance d. -/
theorem card_sig_stern (d : Nat) : (sig d).card = fusc d + fusc (d + 1) :=
  (stern_triple d).1

theorem card_pp_stern (d : Nat) : (pp d).card = fusc d := (stern_triple d).2.1
theorem card_qq_stern (d : Nat) : (qq d).card = fusc (d + 1) := (stern_triple d).2.2

#print axioms card_sig_stern

end Rule129
end OEIS