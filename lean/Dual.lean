
import Brocot
import Shells

namespace OEIS
namespace Rule129


theorem land_eq_zero_iff (x y : Nat) :
    x &&& y = 0 ↔ ∀ i, x.testBit i = true → y.testBit i = false := by
  constructor
  · intro h i hx
    have h1 : (x &&& y).testBit i = (x.testBit i && y.testBit i) := Nat.testBit_land x y i
    rw [h] at h1
    rw [hx] at h1
    simpa using h1.symm
  · intro h
    refine Nat.zero_of_testBit_eq_false fun i => ?_
    rw [Nat.testBit_land]
    cases hx : x.testBit i
    · rfl
    · rw [h i hx]; rfl

theorem land_eq_self_iff (x y : Nat) :
    x &&& y = x ↔ ∀ i, x.testBit i = true → y.testBit i = true := by
  constructor
  · intro h i hx
    have h1 : (x &&& y).testBit i = (x.testBit i && y.testBit i) := Nat.testBit_land x y i
    rw [h] at h1
    rw [hx] at h1
    simpa using h1.symm
  · intro h
    refine Nat.eq_of_testBit_eq fun i => ?_
    rw [Nat.testBit_land]
    cases hx : x.testBit i
    · rfl
    · rw [h i hx]
      rfl

theorem testBit_zero_eq (n : Nat) : n.testBit 0 = decide (n % 2 = 1) := by
  have h := Nat.bit_mod_two_eq_one_iff (n.testBit 0) (n / 2)
  rw [bit_div_two n] at h
  by_cases hc : n % 2 = 1
  · have ht : n.testBit 0 = true := h.mp hc
    rw [ht, hc]; rfl
  · have hf : n.testBit 0 = false := by
      cases hb : n.testBit 0
      · rfl
      · exact absurd (h.mpr hb) hc
    rw [hf]; simp [hc]

theorem not_decide_odd (n : Nat) : (!decide (n % 2 = 1)) = decide (n % 2 = 0) := by
  have h : n % 2 = 0 ∨ n % 2 = 1 := by omega
  rcases h with h | h <;> rw [h] <;> rfl

theorem testBit_succ_div_two (n j : Nat) : n.testBit (j + 1) = (n / 2).testBit j := by
  conv_lhs => rw [← bit_div_two n]
  rw [Nat.testBit_bit_succ]

theorem bit_two_mul_add_one_sub (N w : Nat) (h2 : w / 2 ≤ N) (hw : w ≤ 2 * N + 1) :
    2 * N + 1 - w = Nat.bit (decide (w % 2 = 0)) (N - w / 2) := by
  have h3 := Nat.div_add_mod w 2
  have h4 : w % 2 = 0 ∨ w % 2 = 1 := by omega
  rcases h4 with h4 | h4
  · have hb : decide (w % 2 = 0) = true := by rw [h4]; rfl
    rw [hb]
    show 2 * N + 1 - w = 2 * (N - w / 2) + 1
    omega
  · have hb : decide (w % 2 = 0) = false := by rw [h4]; rfl
    rw [hb]
    show 2 * N + 1 - w = 2 * (N - w / 2)
    omega

theorem testBit_pow_sub_one_sub : ∀ (k : Nat) (w : Nat), w ≤ 2 ^ k - 1 → ∀ i, i < k →
    (2 ^ k - 1 - w).testBit i = !(w.testBit i) := by
  intro k
  induction k with
  | zero => intro w _ i hi; omega
  | succ k ih =>
    intro w hw i hi
    have hp : 2 ^ (k + 1) = 2 * 2 ^ k := by rw [pow_succ]; ring
    have h1 : 1 ≤ 2 ^ k := Nat.one_le_two_pow
    have hN : 2 ^ (k + 1) - 1 = 2 * (2 ^ k - 1) + 1 := by rw [hp]; omega
    have hwk : w / 2 ≤ 2 ^ k - 1 := by
      have hlt : w / 2 < 2 ^ k := by
        rw [Nat.div_lt_iff_lt_mul (by decide : 0 < 2)]
        omega
      omega
    rw [hN, bit_two_mul_add_one_sub (2 ^ k - 1) w hwk (by omega)]
    rcases Nat.eq_zero_or_pos i with h0 | hpos
    · subst h0
      rw [Nat.testBit_bit_zero, testBit_zero_eq w, not_decide_odd w]
    · obtain ⟨j, hj⟩ : ∃ j, i = j + 1 := ⟨i - 1, by omega⟩
      subst hj
      rw [Nat.testBit_bit_succ, ih (w / 2) hwk j (by omega), testBit_succ_div_two w j]


theorem testBit_eq_false_of_le (x k i : Nat) (hx : x ≤ 2 ^ k - 1) (hi : k ≤ i) :
    x.testBit i = false := by
  refine Nat.testBit_eq_false_of_lt ?_
  have hp : 1 ≤ 2 ^ k := Nat.one_le_two_pow
  have h1 : x < 2 ^ k := by omega
  have h2 : 2 ^ k ≤ 2 ^ i := Nat.pow_le_pow_right (by decide : 1 ≤ 2) hi
  omega

/-- complement lemma: inside k bits, x is a submask of the complement of w iff x is
a submask of w, both being impossible unless... (the two conditions coincide) -/
theorem land_pow_sub_eq (k x w : Nat) (hx : x ≤ 2 ^ k - 1) (hw : w ≤ 2 ^ k - 1) :
    x &&& (2 ^ k - 1 - w) = 0 ↔ x &&& w = x := by
  rw [land_eq_zero_iff, land_eq_self_iff]
  constructor
  · intro h i hxi
    by_cases hi : i < k
    · have h2 : (2 ^ k - 1 - w).testBit i = !(w.testBit i) := testBit_pow_sub_one_sub k w hw i hi
      have h3 := h i hxi
      rw [h2] at h3
      cases hb : w.testBit i
      · simp [hb] at h3
      · rfl
    · have hx0 : x.testBit i = false := testBit_eq_false_of_le x k i hx (by omega)
      rw [hx0] at hxi
      exact absurd hxi (by simp)
  · intro h i hxi
    by_cases hi : i < k
    · have h2 : (2 ^ k - 1 - w).testBit i = !(w.testBit i) := testBit_pow_sub_one_sub k w hw i hi
      rw [h2, h i hxi]
      rfl
    · rw [testBit_eq_false_of_le (2 ^ k - 1 - w) k i (by omega) (by omega)]



/-- the division identity behind the dual closed form -/
theorem div_two_pow_sub (k X : Nat) (h1 : 1 ≤ X) (h2 : X ≤ 2 ^ (k + 1)) :
    (2 ^ (k + 1) - X) / 2 = 2 ^ k - (X + 1) / 2 := by
  have hp : 2 ^ (k + 1) = 2 * 2 ^ k := by rw [pow_succ]; ring
  have h3 : 1 ≤ 2 ^ k := Nat.one_le_two_pow
  omega




theorem land_le_right (a b : Nat) : a &&& b ≤ b := by
  induction b using Nat.strong_induction_on generalizing a with
  | _ b ih =>
    rcases Nat.eq_zero_or_pos b with hb0 | hbpos
    · subst hb0; simp
    · conv_lhs => rw [← bit_div_two a]; rw [← bit_div_two b]
      conv_rhs => rw [← bit_div_two b]
      rw [Nat.land_bit]
      have h1 : a / 2 &&& b / 2 ≤ b / 2 := ih (b / 2) (by omega) (a / 2)
      cases hA : a.testBit 0 <;> cases hB : b.testBit 0
      · simp only [hA, hB, Bool.false_and]
        show 2 * (a / 2 &&& b / 2) ≤ 2 * (b / 2)
        omega
      · simp only [hA, hB, Bool.false_and]
        show 2 * (a / 2 &&& b / 2) ≤ 2 * (b / 2) + 1
        omega
      · simp only [hA, hB, Bool.true_and, Bool.and_false]
        show 2 * (a / 2 &&& b / 2) ≤ 2 * (b / 2)
        omega
      · simp only [hA, hB, Bool.true_and]
        show 2 * (a / 2 &&& b / 2) + 1 ≤ 2 * (b / 2) + 1
        omega

/-- **the dual closed form**: the shell seen from the top of the dyadic block -/
theorem mem_shell_dual {t d : Nat} (ht : 1 ≤ t) (hd : d ≤ t) :
    d ∈ shell t ↔ (2 ^ (Nat.log2 t + 1) - t - 1) ∈ sig d := by
  set k := Nat.log2 t with hk
  set s := 2 ^ (k + 1) - t with hs
  have h1 : 2 ^ k ≤ t := Nat.log2_self_le (by omega)
  have h2 : t < 2 ^ (k + 1) := Nat.lt_log2_self (n := t)
  have hs1 : 1 ≤ s := by omega
  have hs2 : s ≤ 2 ^ k := by omega
  have hpow : 2 ^ (k + 1) = 2 * 2 ^ k := by rw [Nat.pow_succ]; ring
  have hr : r t = 2 ^ k - s := by rw [r_eq_t_sub_pow t ht, ← hk]; omega
  have hX : ∀ A : Nat, A = (s + d + 1) / 2 → (t - d) / 2 = 2 ^ k - A := by
    intro A hA
    have hX2 : s + d ≤ 2 ^ (k + 1) := by omega
    have hdiv := div_two_pow_sub k (s + d) (by omega) hX2
    have htd : t - d = 2 ^ (k + 1) - (s + d) := by omega
    rw [htd, hdiv]
    omega
  have hshell : d ∈ shell t ↔ ((t - d) / 2) &&& (r t) = (t - d) / 2 := by
    rw [mem_shell]; exact ⟨fun h => h.2, fun h => ⟨hd, h⟩⟩
  rw [hshell, hr]
  by_cases hgood : s ≤ d + 1
  · set A := (s + d + 1) / 2 with hAdef
    have hm : (t - d) / 2 = 2 ^ k - 1 - (A - 1) := by
      have h := hX A hAdef
      omega
    have hAd : s ≤ A := by omega
    have hA2 : A ≤ 2 ^ k := by omega
    have hA1 : 1 ≤ A := by omega
    have hu : s - 1 ≤ d := by omega
    have hlow : (t - d) / 2 ≤ 2 ^ k - s := by omega
    have hsub : (2 ^ k - s) - ((t - d) / 2) = A - s := by omega
    have heq : (d - (s - 1)) / 2 = A - s := by omega
    have hsig : (2 ^ (k + 1) - t - 1) ∈ sig d ↔
        ((s - 1) &&& ((d - (s - 1)) / 2) = 0) := by
      rw [mem_sig]
      exact ⟨fun h => h.2, fun h => ⟨hu, h⟩⟩
    rw [hsig, heq]
    have e0 : ((t - d) / 2) &&& (2 ^ k - s) = (t - d) / 2 ↔
        ((t - d) / 2) &&& (A - s) = 0 := by
      have h := land_of_le (u := (t - d) / 2) (B := 2 ^ k - s) hlow
      rwa [hsub] at h
    rw [e0]
    have e1 : ((t - d) / 2) &&& (A - s) = 0 ↔ (A - s) &&& ((t - d) / 2) = 0 := by
      rw [Nat.land_comm]
    rw [e1, hm]
    have e2 : (A - s) &&& (2 ^ k - 1 - (A - 1)) = 0 ↔ (A - s) &&& (A - 1) = (A - s) :=
      land_pow_sub_eq k (A - s) (A - 1) (by omega) (by omega)
    rw [e2]
    have e3 : (A - s) &&& (A - 1) = (A - s) ↔ (A - s) &&& (s - 1) = 0 := by
      have h := land_add_iff (A - s) (s - 1)
      rwa [show (A - s) + (s - 1) = A - 1 from by omega] at h
    rw [e3]
    exact ⟨fun h => by rwa [Nat.land_comm] at h, fun h => by rwa [Nat.land_comm]⟩
  · have hlt : d + 1 < s := by omega
    have hA := hX ((s + d + 1) / 2) rfl
    have hgt : 2 ^ k - s < (t - d) / 2 := by omega
    have hsig : (2 ^ (k + 1) - t - 1) ∈ sig d ↔
        ((2 ^ (k + 1) - t - 1) ≤ d ∧ ((2 ^ (k + 1) - t - 1) &&& ((d - (2 ^ (k + 1) - t - 1)) / 2) = 0)) := by
      rw [mem_sig]
    rw [hsig]
    constructor
    · intro h
      have hle : (t - d) / 2 ≤ 2 ^ k - s := by
        rw [← h]; exact land_le_right _ _
      omega
    · rintro ⟨hle, -⟩
      omega

#print axioms mem_shell_dual

end Rule129
end OEIS