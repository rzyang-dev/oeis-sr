import Census

namespace OEIS
namespace Rule129

/- ============================================================
   Trees: the level sizes grow exponentially, and the zero count
   factorizes over the binary digits of r t.

       sum_{d in shell t} b^d
         = (b+1) * b^(t-1-2r) * sum_{m subset r} (b*b)^m

   The two recursion lemmas below show that the last factor factors
   over the bits of r: doubling the argument squares the base, and an
   odd argument adds one factor (1 + y).  Hence the tree count is
   multiplicative in the binary digits of t.
   ============================================================ -/

/-- The submasks of 0. -/
theorem subm_zero : subm 0 = ({0} : Finset Nat) := by
  ext m
  rw [mem_subm, Finset.mem_singleton]
  constructor
  · rintro ⟨h1, h2⟩
    interval_cases m
    rfl
  · rintro rfl
    exact ⟨by decide, by decide⟩

/-- The submasks of 1. -/
theorem subm_one : subm 1 = ({0, 1} : Finset Nat) := by
  ext m
  rw [mem_subm, Finset.mem_insert, Finset.mem_singleton]
  constructor
  · rintro ⟨h1, h2⟩
    interval_cases m
    · exact Or.inl rfl
    · exact Or.inr rfl
  · rintro (rfl | rfl)
    · exact ⟨by decide, by decide⟩
    · exact ⟨by decide, by decide⟩

#print axioms subm_zero
#print axioms subm_one

/-- **Multiplicativity, first case.**  Doubling the argument squares the base. -/
theorem sum_subm_pow_two_mul (u y : Nat) :
    (subm (2 * u)).sum (fun m => y ^ m) = (subm u).sum (fun m => (y * y) ^ m) := by
  have hy : ∀ m : Nat, y ^ (2 * m) = (y * y) ^ m := by
    intro m
    rw [pow_mul, pow_two]
  rw [subm_two_mul, Finset.sum_map]
  exact Finset.sum_congr rfl (fun m _ => hy m)

#print axioms sum_subm_pow_two_mul

/-- **Multiplicativity, second case.**  An odd argument adds one factor (1 + y). -/
theorem sum_subm_pow_two_mul_add_one (u y : Nat) :
    (subm (2 * u + 1)).sum (fun m => y ^ m)
      = (1 + y) * (subm u).sum (fun m => (y * y) ^ m) := by
  have hy : ∀ m : Nat, y ^ (2 * m) = (y * y) ^ m := by
    intro m
    rw [pow_mul, pow_two]
  rw [subm_two_mul_add_one, Finset.sum_union (disjoint_subm_doublings u),
    Finset.sum_map, Finset.sum_map, ← Finset.sum_add_distrib]
  have hcongr : (subm u).sum (fun m => y ^ (emb2 m) + y ^ (emb2p1 m))
      = (subm u).sum (fun m => (1 + y) * (y * y) ^ m) := by
    refine Finset.sum_congr rfl (fun m _ => ?_)
    simp only [emb2_apply, emb2p1_apply]
    show y ^ (2 * m) + y ^ (2 * m + 1) = (1 + y) * (y * y) ^ m
    have hsecond : y ^ (2 * m + 1) = y * (y * y) ^ m := by
      rw [Nat.pow_succ, hy m]
      ring
    rw [hy m, hsecond]
    ring
  rw [hcongr, ← Finset.mul_sum]

#print axioms sum_subm_pow_two_mul_add_one

/-- The descending sum obeys the same doubling recursion. -/
theorem sum_subm_pow_shift_two_mul (u y : Nat) :
    (subm (2 * u)).sum (fun m => y ^ (2 * u - m))
      = (subm u).sum (fun m => (y * y) ^ (u - m)) := by
  rw [subm_two_mul, Finset.sum_map]
  refine Finset.sum_congr rfl (fun m _ => ?_)
  simp only [emb2_apply]
  show y ^ (2 * u - 2 * m) = (y * y) ^ (u - m)
  rw [← Nat.mul_sub, pow_mul, pow_two]

#print axioms sum_subm_pow_shift_two_mul

/-- The descending sum, odd argument. -/
theorem sum_subm_pow_shift_two_mul_add_one (u y : Nat) :
    (subm (2 * u + 1)).sum (fun m => y ^ (2 * u + 1 - m))
      = (1 + y) * (subm u).sum (fun m => (y * y) ^ (u - m)) := by
  rw [subm_two_mul_add_one, Finset.sum_union (disjoint_subm_doublings u),
    Finset.sum_map, Finset.sum_map, ← Finset.sum_add_distrib]
  have hcongr : (subm u).sum (fun m => y ^ (2 * u + 1 - emb2 m) + y ^ (2 * u + 1 - emb2p1 m))
      = (subm u).sum (fun m => (1 + y) * (y * y) ^ (u - m)) := by
    refine Finset.sum_congr rfl (fun m hm => ?_)
    have hmle : m ≤ u := (mem_subm.mp hm).1
    simp only [emb2_apply, emb2p1_apply]
    have h1 : 2 * u + 1 - 2 * m = 2 * (u - m) + 1 := by omega
    have h2 : 2 * u + 1 - (2 * m + 1) = 2 * (u - m) := by omega
    have hy : ∀ k : Nat, y ^ (2 * k) = (y * y) ^ k := by
      intro k
      rw [pow_mul, pow_two]
    show y ^ (2 * u + 1 - 2 * m) + y ^ (2 * u + 1 - (2 * m + 1))
        = (1 + y) * (y * y) ^ (u - m)
    rw [h1, h2, Nat.pow_succ, hy]
    ring
  rw [hcongr, ← Finset.mul_sum]

#print axioms sum_subm_pow_shift_two_mul_add_one

/-- **Palindrome of the submask sum.**  Descending equals ascending. -/
theorem sum_subm_pow_shift (r : Nat) :
    ∀ y : Nat, (subm r).sum (fun m => y ^ (r - m)) = (subm r).sum (fun m => y ^ m) := by
  induction r using Nat.strong_induction_on with
  | _ r ih =>
    intro y
    rcases r with _ | k
    · rw [subm_zero]; simp
    · have hlt : (k + 1) / 2 < k + 1 := by omega
      have hIH := ih ((k + 1) / 2) hlt (y * y)
      have hdm := Nat.div_add_mod (k + 1) 2
      have hlt2 := Nat.mod_lt (k + 1) (by decide : 0 < 2)
      interval_cases h : (k + 1) % 2
      · have he : k + 1 = 2 * ((k + 1) / 2) := by omega
        rw [he, sum_subm_pow_shift_two_mul ((k + 1) / 2) y,
          sum_subm_pow_two_mul ((k + 1) / 2) y]
        exact hIH
      · have he : k + 1 = 2 * ((k + 1) / 2) + 1 := by omega
        rw [he, sum_subm_pow_shift_two_mul_add_one ((k + 1) / 2) y,
          sum_subm_pow_two_mul_add_one ((k + 1) / 2) y]
        exact congrArg (fun z => (1 + y) * z) hIH

#print axioms sum_subm_pow_shift

/- ---------- the tree count ---------- -/

/-- **The zero count on a b-ary tree.**  Every node at level d carries b^d
    cells, so the count is b^d summed over the shell. -/
theorem shell_sum_pow (b t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => b ^ d)
      = (b + 1) * b ^ (t - 1 - 2 * r t) * (subm (r t)).sum (fun m => (b * b) ^ m) := by
  have hb := two_mul_r_add_one_le t ht
  rw [shell_sum_submask (fun d => b ^ d) t ht, Finset.sum_product]
  have hinner : ∀ m ∈ subm (r t),
      (Finset.range 2).sum (fun x => b ^ (t - 2 * m - x)) = (b + 1) * b ^ (t - 1 - 2 * m) := by
    intro m hm
    have hmle : m ≤ r t := (mem_subm.mp hm).1
    have h2m : 2 * m + 1 ≤ t := by omega
    rw [show (2 : Nat) = 1 + 1 from rfl, Finset.sum_range_succ, Finset.sum_range_one]
    have hk1 : t - 2 * m = (t - 1 - 2 * m) + 1 := by omega
    have hk2 : t - 2 * m - 1 = t - 1 - 2 * m := by omega
    show b ^ (t - 2 * m - 0) + b ^ (t - 2 * m - 1) = (b + 1) * b ^ (t - 1 - 2 * m)
    rw [Nat.sub_zero, hk2, hk1, Nat.pow_succ]
    ring
  have hstep1 : (subm (r t)).sum (fun m => (Finset.range 2).sum (fun x => b ^ (t - 2 * m - x)))
      = (subm (r t)).sum (fun m => (b + 1) * b ^ (t - 1 - 2 * m)) :=
    Finset.sum_congr rfl hinner
  rw [hstep1, ← Finset.mul_sum]
  have hshift : ∀ m ∈ subm (r t),
      b ^ (t - 1 - 2 * m) = b ^ (t - 1 - 2 * r t) * (b * b) ^ (r t - m) := by
    intro m hm
    have hmle : m ≤ r t := (mem_subm.mp hm).1
    have hbase : t - 1 - 2 * m = (t - 1 - 2 * r t) + 2 * (r t - m) := by omega
    rw [hbase, Nat.pow_add, pow_mul, pow_two]
  have hstep2 : (subm (r t)).sum (fun m => b ^ (t - 1 - 2 * m))
      = (subm (r t)).sum (fun m => b ^ (t - 1 - 2 * r t) * (b * b) ^ (r t - m)) :=
    Finset.sum_congr rfl hshift
  rw [hstep2, ← Finset.mul_sum, sum_subm_pow_shift (r t) (b * b)]
  ring

#print axioms shell_sum_pow

/- ---------- the product form: the submask sum factors over the bits ---------- -/

/-- j is smaller than 2^j. -/
theorem lt_two_pow_self : ∀ j : Nat, j < 2 ^ j := by
  intro j
  induction j with
  | zero => simp
  | succ n ih =>
    have h1 : 1 ≤ 2 ^ n := Nat.one_le_two_pow
    rw [Nat.pow_succ]
    omega

#print axioms lt_two_pow_self

/-- A set bit makes the position smaller than the number. -/
theorem testBit_lt {u j : Nat} (h : u.testBit j = true) : j < u := by
  have h2 : ¬ (u < 2 ^ j) := by
    intro hlt
    rw [Nat.testBit_eq_false_of_lt hlt] at h
    exact absurd h (by decide)
  have h3 : 2 ^ j ≤ u := by omega
  have h4 : j < 2 ^ j := lt_two_pow_self j
  omega

#print axioms testBit_lt

/-- The positions of the 1-bits of r. -/
def bits (r : Nat) : Finset Nat := (Finset.range r).filter (fun i => r.testBit i)

theorem mem_bits {r i : Nat} : i ∈ bits r ↔ i < r ∧ r.testBit i := by
  simp [bits]

#print axioms mem_bits

theorem bits_zero : bits 0 = ∅ := by decide

#print axioms bits_zero

theorem bits_two_mul (u : Nat) : bits (2 * u) = (bits u).image (fun i => i + 1) := by
  ext i
  rw [mem_bits, Finset.mem_image]
  constructor
  · rintro ⟨hlt, hbit⟩
    rcases i with _ | j
    · rw [testBit_two_mul_zero] at hbit
      exact absurd hbit (by decide)
    · rw [testBit_two_mul_succ] at hbit
      exact ⟨j, by rw [mem_bits]; exact ⟨testBit_lt hbit, hbit⟩, rfl⟩
  · rintro ⟨j, hj, rfl⟩
    rw [mem_bits] at hj
    refine ⟨by omega, ?_⟩
    rw [testBit_two_mul_succ]
    exact hj.2

#print axioms bits_two_mul

theorem bits_two_mul_add_one (u : Nat) :
    bits (2 * u + 1) = insert 0 ((bits u).image (fun i => i + 1)) := by
  ext i
  rw [mem_bits, Finset.mem_insert, Finset.mem_image]
  constructor
  · rintro ⟨hlt, hbit⟩
    rcases i with _ | j
    · exact Or.inl rfl
    · rw [testBit_two_mul_add_one_succ] at hbit
      exact Or.inr ⟨j, by rw [mem_bits]; exact ⟨testBit_lt hbit, hbit⟩, rfl⟩
  · rintro (rfl | ⟨j, hj, rfl⟩)
    · exact ⟨by omega, testBit_two_mul_add_one_zero u⟩
    · rw [mem_bits] at hj
      refine ⟨by omega, ?_⟩
      rw [testBit_two_mul_add_one_succ]
      exact hj.2

#print axioms bits_two_mul_add_one

/-- The product over the bits doubles: squaring the base. -/
theorem prod_bits_two_mul (u y : Nat) :
    (bits (2 * u)).prod (fun i => 1 + y ^ 2 ^ i)
      = (bits u).prod (fun i => 1 + (y * y) ^ 2 ^ i) := by
  rw [bits_two_mul, Finset.prod_image (fun a _ b _ h => by simp at h; omega)]
  refine Finset.prod_congr rfl (fun i _ => ?_)
  congr 1
  rw [show (2 : Nat) ^ (i + 1) = 2 * 2 ^ i from by rw [Nat.pow_succ]; ring]
  rw [pow_mul, pow_two]

#print axioms prod_bits_two_mul

/-- The product over the bits, odd case: one extra factor (1 + y). -/
theorem prod_bits_two_mul_add_one (u y : Nat) :
    (bits (2 * u + 1)).prod (fun i => 1 + y ^ 2 ^ i)
      = (1 + y) * (bits u).prod (fun i => 1 + (y * y) ^ 2 ^ i) := by
  rw [bits_two_mul_add_one, Finset.prod_insert (by
    intro h
    rw [Finset.mem_image] at h
    obtain ⟨j, _, hj⟩ := h
    omega)]
  rw [Finset.prod_image (fun a _ b _ h => by simp at h; omega)]
  have h0 : 1 + y ^ 2 ^ 0 = 1 + y := by norm_num
  rw [h0]
  congr 1
  refine Finset.prod_congr rfl (fun i _ => ?_)
  congr 1
  rw [show (2 : Nat) ^ (i + 1) = 2 * 2 ^ i from by rw [Nat.pow_succ]; ring]
  rw [pow_mul, pow_two]

#print axioms prod_bits_two_mul_add_one

/-- **The factorization.**  The submask sum of a geometric sequence is the
    product over the positions of the 1-bits of r. -/
theorem sum_subm_pow_eq_prod (r : Nat) :
    ∀ y : Nat, (subm r).sum (fun m => y ^ m) = (bits r).prod (fun i => 1 + y ^ 2 ^ i) := by
  induction r using Nat.strong_induction_on with
  | _ r ih =>
    intro y
    rcases r with _ | k
    · rw [subm_zero, bits_zero]
      simp
    · have hlt : (k + 1) / 2 < k + 1 := by omega
      have hIH := ih ((k + 1) / 2) hlt (y * y)
      have hdm := Nat.div_add_mod (k + 1) 2
      have hlt2 := Nat.mod_lt (k + 1) (by decide : 0 < 2)
      interval_cases h : (k + 1) % 2
      · have he : k + 1 = 2 * ((k + 1) / 2) := by omega
        rw [he, sum_subm_pow_two_mul ((k + 1) / 2) y,
          prod_bits_two_mul ((k + 1) / 2) y]
        exact hIH
      · have he : k + 1 = 2 * ((k + 1) / 2) + 1 := by omega
        rw [he, sum_subm_pow_two_mul_add_one ((k + 1) / 2) y,
          prod_bits_two_mul_add_one ((k + 1) / 2) y]
        exact congrArg (fun z => (1 + y) * z) hIH

#print axioms sum_subm_pow_eq_prod

/-- **The tree count, factorized over the bits of r t.** -/
theorem shell_sum_pow_factored (b t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => b ^ d)
      = (b + 1) * b ^ (t - 1 - 2 * r t)
          * (bits (r t)).prod (fun i => 1 + (b * b) ^ 2 ^ i) := by
  rw [shell_sum_pow b t ht, sum_subm_pow_eq_prod (r t) (b * b)]

#print axioms shell_sum_pow_factored

/-- The same, with each factor written as a power of b itself. -/
theorem shell_sum_pow_factored' (b t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => b ^ d)
      = (b + 1) * b ^ (t - 1 - 2 * r t)
          * (bits (r t)).prod (fun i => 1 + b ^ 2 ^ (i + 1)) := by
  rw [shell_sum_pow_factored b t ht]
  congr 1
  refine Finset.prod_congr rfl (fun i _ => ?_)
  congr 1
  rw [show (2 : Nat) ^ (i + 1) = 2 * 2 ^ i from by rw [Nat.pow_succ]; ring]
  rw [pow_mul, pow_two]

#print axioms shell_sum_pow_factored'

/-- **The popcount form.**  The number of submasks is 2 to the number of 1-bits. -/
theorem card_subm_eq_pow_bits (r : Nat) : (subm r).card = 2 ^ (bits r).card := by
  have h := sum_subm_pow_eq_prod r 1
  simp only [one_pow] at h
  rw [Finset.sum_const, Finset.prod_const] at h
  simpa using h

#print axioms card_subm_eq_pow_bits

/-- The shell size in popcount form: two copies of the submask set. -/
theorem card_shell_eq_pow_bits (t : Nat) (ht : 1 ≤ t) :
    (shell t).card = 2 * 2 ^ (bits (r t)).card := by
  rw [card_shell t ht, card_subm_eq_pow_bits]

end Rule129
end OEIS