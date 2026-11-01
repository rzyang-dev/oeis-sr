import Universal

namespace OEIS
namespace Rule129

/- ---------- elementary div/mod facts for 2 ---------- -/

theorem div_two_mul (u : Nat) : 2 * u / 2 = u := by
  rw [Nat.mul_comm 2 u]
  exact Nat.mul_div_left u (by decide)

theorem mod_two_mul (u : Nat) : 2 * u % 2 = 0 := by
  rw [Nat.mod_eq_sub_mul_div, div_two_mul]
  omega

theorem div_two_mul_add_one (u : Nat) : (2 * u + 1) / 2 = u :=
  Nat.div_eq_of_lt_le (by omega) (by omega)

theorem mod_two_mul_add_one (u : Nat) : (2 * u + 1) % 2 = 1 := by
  rw [Nat.mod_eq_sub_mul_div, div_two_mul_add_one]
  omega

/- ---------- the two doublings as embeddings ---------- -/

def emb2 : Nat ↪ Nat where
  toFun := fun m => 2 * m
  inj' := by
    intro a b h
    dsimp only at h
    omega

def emb2p1 : Nat ↪ Nat where
  toFun := fun m => 2 * m + 1
  inj' := by
    intro a b h
    dsimp only at h
    omega

@[simp] theorem emb2_apply (m : Nat) : emb2 m = 2 * m := rfl

@[simp] theorem emb2p1_apply (m : Nat) : emb2p1 m = 2 * m + 1 := rfl

/- ---------- submasks ---------- -/

/-- The submasks of r: the numbers m <= r with m &&& r = m. -/
def subm (r : Nat) : Finset Nat := (Finset.range (r + 1)).filter (fun m => m &&& r = m)

theorem mem_subm {r m : Nat} : m ∈ subm r ↔ m ≤ r ∧ m &&& r = m := by
  simp [subm]

theorem subm_two_mul (u : Nat) : subm (2 * u) = (subm u).map emb2 := by
  ext m
  simp only [mem_subm, Finset.mem_map, emb2_apply]
  constructor
  · rintro ⟨h1, h2⟩
    obtain ⟨hev, hsu⟩ := (sub_two_mul (e := m) (u := u)).mp h2
    refine ⟨m / 2, ⟨?_, hsu⟩, ?_⟩
    · have hdle : m / 2 ≤ 2 * u / 2 := Nat.div_le_div_right h1
      rwa [div_two_mul] at hdle
    · have hdm := Nat.div_add_mod m 2
      omega
  · rintro ⟨m', ⟨h1, h2⟩, hm⟩
    have h2' : m' &&& u = m' := h2
    have hm' : 2 * m' = m := hm
    rw [← hm'] at *
    refine ⟨by omega, ?_⟩
    exact (sub_two_mul (e := 2 * m') (u := u)).mpr ⟨mod_two_mul m', by rwa [div_two_mul]⟩

theorem subm_two_mul_add_one (u : Nat) :
    subm (2 * u + 1) = (subm u).map emb2 ∪ (subm u).map emb2p1 := by
  ext m
  simp only [mem_subm, Finset.mem_map, Finset.mem_union, emb2_apply, emb2p1_apply]
  constructor
  · rintro ⟨h1, h2⟩
    have hsu := (sub_two_mul_add_one (e := m) (u := u)).mp h2
    have hdle : m / 2 ≤ (2 * u + 1) / 2 := Nat.div_le_div_right h1
    rw [div_two_mul_add_one] at hdle
    have hdm := Nat.div_add_mod m 2
    have hlt := Nat.mod_lt m (by decide : 0 < 2)
    interval_cases h : m % 2
    · exact Or.inl ⟨m / 2, ⟨hdle, hsu⟩, by omega⟩
    · exact Or.inr ⟨m / 2, ⟨hdle, hsu⟩, by omega⟩
  · rintro (⟨m', ⟨h1, h2⟩, hm⟩ | ⟨m', ⟨h1, h2⟩, hm⟩)
    · have hm' : 2 * m' = m := hm
      rw [← hm'] at *
      refine ⟨by omega, ?_⟩
      exact (sub_two_mul_add_one (e := 2 * m') (u := u)).mpr (by rwa [div_two_mul])
    · have hm' : 2 * m' + 1 = m := hm
      rw [← hm'] at *
      refine ⟨by omega, ?_⟩
      exact (sub_two_mul_add_one (e := 2 * m' + 1) (u := u)).mpr (by rwa [div_two_mul_add_one])

theorem disjoint_subm_doublings (u : Nat) :
    Disjoint ((subm u).map emb2) ((subm u).map emb2p1) := by
  rw [Finset.disjoint_left]
  intro a ha hb
  simp only [Finset.mem_map] at ha hb
  obtain ⟨x, -, hx⟩ := ha
  obtain ⟨y, -, hy⟩ := hb
  have h1 : emb2 x = emb2p1 y := by rw [hx, hy]
  simp only [emb2_apply, emb2p1_apply] at h1
  have hm := congrArg (fun n => n % 2) h1
  rw [mod_two_mul, mod_two_mul_add_one] at hm
  exact absurd hm (by decide)

theorem card_subm_two_mul (u : Nat) : (subm (2 * u)).card = (subm u).card := by
  rw [subm_two_mul, Finset.card_map]

theorem card_subm_two_mul_add_one (u : Nat) :
    (subm (2 * u + 1)).card = 2 * (subm u).card := by
  rw [subm_two_mul_add_one, Finset.card_union_of_disjoint (disjoint_subm_doublings u),
    Finset.card_map, Finset.card_map]
  omega


/- ---------- the size of r t: t = 2^K + r t with r t < 2^K ---------- -/

theorem r_eq_t_sub_pow (t : Nat) (ht : 1 ≤ t) : r t = t - 2 ^ Nat.log2 t := by
  set K := Nat.log2 t with hK
  have hKle : 2 ^ K ≤ t := Nat.log2_self_le (by omega)
  have hKlt : t < 2 ^ (K + 1) := Nat.lt_log2_self (n := t)
  have hpow : 2 ^ (K + 1) = 2 * 2 ^ K := by rw [Nat.pow_succ]; ring
  have hs : t - 2 ^ K < 2 ^ K := by omega
  exact r_eq_of t K (t - 2 ^ K) ht (by omega) hs

theorem two_mul_r_le (t : Nat) (ht : 1 ≤ t) : 2 * r t ≤ t := by
  rw [r_eq_t_sub_pow t ht]
  have hKle : 2 ^ Nat.log2 t ≤ t := Nat.log2_self_le (by omega)
  have hKlt : t < 2 ^ (Nat.log2 t + 1) := Nat.lt_log2_self (n := t)
  have hpow : 2 ^ (Nat.log2 t + 1) = 2 * 2 ^ Nat.log2 t := by rw [Nat.pow_succ]; ring
  omega

theorem two_mul_r_add_one_le (t : Nat) (ht : 1 ≤ t) : 2 * r t + 1 ≤ t := by
  rw [r_eq_t_sub_pow t ht]
  have hKle : 2 ^ Nat.log2 t ≤ t := Nat.log2_self_le (by omega)
  have hKlt : t < 2 ^ (Nat.log2 t + 1) := Nat.lt_log2_self (n := t)
  have hpow : 2 ^ (Nat.log2 t + 1) = 2 * 2 ^ Nat.log2 t := by rw [Nat.pow_succ]; ring
  omega

#print axioms r_eq_t_sub_pow
#print axioms two_mul_r_le
#print axioms two_mul_r_add_one_le



/- ---------- sums of submasks ---------- -/

theorem sum_subm_two_mul (u : Nat) : (subm (2 * u)).sum id = 2 * (subm u).sum id := by
  have h1 : (subm (2 * u)).sum id = (subm u).sum (fun x => 2 * x) := by
    rw [subm_two_mul, Finset.sum_map]
    simp
  rw [h1, ← Finset.mul_sum]
  simp

theorem sum_subm_two_mul_add_one (u : Nat) :
    (subm (2 * u + 1)).sum id = 4 * (subm u).sum id + (subm u).card := by
  have h0 : (subm (2 * u + 1)).sum id
      = (subm u).sum (fun x => 2 * x) + (subm u).sum (fun x => 2 * x + 1) := by
    rw [subm_two_mul_add_one, Finset.sum_union (disjoint_subm_doublings u),
      Finset.sum_map, Finset.sum_map]
    simp
  have h2 : (subm u).sum (fun x => 2 * x + 1) = 2 * (subm u).sum id + (subm u).card := by
    rw [Finset.sum_add_distrib, ← Finset.mul_sum]
    simp
  rw [h0, h2, ← Finset.mul_sum]
  rw [show (∑ i ∈ subm u, i) = (subm u).sum id from rfl]
  ring

/-- Twice the sum of the submasks of r is (number of submasks) times r. -/
theorem two_mul_sum_subm (r : Nat) : 2 * (subm r).sum id = (subm r).card * r := by
  induction r using Nat.strong_induction_on with
  | _ r ih =>
    rcases r with _ | _ | k
    · simp [subm]
    · decide
    · have hlt : (k + 2) / 2 < k + 2 := Nat.div_lt_self (by omega) (by decide)
      have hIH := ih ((k + 2) / 2) hlt
      have hdm := Nat.div_add_mod (k + 2) 2
      have hlt2 := Nat.mod_lt (k + 2) (by decide : 0 < 2)
      interval_cases h : (k + 2) % 2
      · have he : k + 2 = 2 * ((k + 2) / 2) := by omega
        have hsub : subm (k + 2) = subm (2 * ((k + 2) / 2)) := by
          rw [he, div_two_mul]
        rw [hsub, sum_subm_two_mul, card_subm_two_mul]
        calc 2 * (2 * (subm ((k + 2) / 2)).sum id)
            = 2 * ((subm ((k + 2) / 2)).card * ((k + 2) / 2)) := by rw [hIH]
          _ = (subm ((k + 2) / 2)).card * (2 * ((k + 2) / 2)) := by ring
          _ = (subm ((k + 2) / 2)).card * (k + 2) := by rw [← he]
      · have he : k + 2 = 2 * ((k + 2) / 2) + 1 := by omega
        have hsub : subm (k + 2) = subm (2 * ((k + 2) / 2) + 1) := by
          rw [he, div_two_mul_add_one]
        rw [hsub, sum_subm_two_mul_add_one, card_subm_two_mul_add_one]
        calc 2 * (4 * (subm ((k + 2) / 2)).sum id + (subm ((k + 2) / 2)).card)
            = 4 * (2 * (subm ((k + 2) / 2)).sum id) + 2 * (subm ((k + 2) / 2)).card := by ring
          _ = 4 * ((subm ((k + 2) / 2)).card * ((k + 2) / 2)) + 2 * (subm ((k + 2) / 2)).card := by rw [hIH]
          _ = (2 * (subm ((k + 2) / 2)).card) * (2 * ((k + 2) / 2) + 1) := by ring
          _ = (2 * (subm ((k + 2) / 2)).card) * (k + 2) := by rw [← he]

#print axioms sum_subm_two_mul
#print axioms sum_subm_two_mul_add_one
#print axioms two_mul_sum_subm

/- ---------- the shell set ---------- -/

/-- The levels that carry a 0 at time t: d <= t and (t-d)/2 a submask of r t. -/
def shell (t : Nat) : Finset Nat :=
  (Finset.range (t + 1)).filter (fun d => (t - d) / 2 &&& r t = (t - d) / 2)

theorem mem_shell {t d : Nat} :
    d ∈ shell t ↔ d ≤ t ∧ (t - d) / 2 &&& r t = (t - d) / 2 := by
  simp [shell]

/-- The zero set is a union of 2 * (#subm (r t)) complete shells. -/
theorem card_shell (t : Nat) (ht : 1 ≤ t) :
    (shell t).card = 2 * (subm (r t)).card := by
  have hb1 : 2 * r t ≤ t := two_mul_r_le t ht
  have hb2 : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  have key : ((subm (r t)) ×ˢ (Finset.range 2)).card = (shell t).card := by
    refine Finset.card_bij (fun p _ => t - 2 * p.1 - p.2) ?_ ?_ ?_
    · intro p hp
      simp only [Finset.mem_product, Finset.mem_range, mem_subm] at hp
      obtain ⟨⟨hp1, hp2⟩, hp3⟩ := hp
      rw [mem_shell]
      have hdiv : (2 * p.1 + p.2) / 2 = p.1 :=
        Nat.div_eq_of_lt_le (by omega) (by omega)
      have hd : t - (t - 2 * p.1 - p.2) = 2 * p.1 + p.2 := by omega
      exact ⟨by omega, by rw [hd, hdiv]; exact hp2⟩
    · intro p hp q hq heq
      simp only [Finset.mem_product, Finset.mem_range, mem_subm] at hp hq
      obtain ⟨⟨hp1, hp2⟩, hp3⟩ := hp
      obtain ⟨⟨hq1, hq2⟩, hq3⟩ := hq
      have he : 2 * p.1 + p.2 = 2 * q.1 + q.2 := by omega
      have hdivp : (2 * p.1 + p.2) / 2 = p.1 :=
        Nat.div_eq_of_lt_le (by omega) (by omega)
      have hdivq : (2 * q.1 + q.2) / 2 = q.1 :=
        Nat.div_eq_of_lt_le (by omega) (by omega)
      have hmp : (2 * p.1 + p.2) % 2 = p.2 := by
        rw [Nat.mod_eq_sub_mul_div, hdivp]; omega
      have hmq : (2 * q.1 + q.2) % 2 = q.2 := by
        rw [Nat.mod_eq_sub_mul_div, hdivq]; omega
      have h1 : p.1 = q.1 := by rw [← hdivp, he, hdivq]
      have h2 : p.2 = q.2 := by rw [← hmp, he, hmq]
      exact Prod.ext h1 h2
    · intro d hd
      rw [mem_shell] at hd
      obtain ⟨hdt, hcond⟩ := hd
      refine ⟨((t - d) / 2, (t - d) % 2), ?_, ?_⟩
      · simp only [Finset.mem_product, Finset.mem_range, mem_subm]
        refine ⟨⟨?_, hcond⟩, by omega⟩
        exact sub_le (show sub ((t - d) / 2) (r t) from hcond)
      · have hdm := Nat.div_add_mod (t - d) 2
        omega
  rw [← key, Finset.card_product, Finset.card_range]
  omega

#print axioms mem_shell
#print axioms card_shell


/- ---------- transporting the shell sum to the submasks ---------- -/

/-- The shell sum is the same sum over the submask product: the bijection is
    d |-> ((t-d)/2, (t-d)%2), with inverse (m,b) |-> t - 2m - b. -/
theorem sum_shell_eq_prod (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum id
      = ((subm (r t)) ×ˢ (Finset.range 2)).sum (fun p => t - 2 * p.1 - p.2) := by
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
    show d = t - 2 * ((t - d) / 2) - (t - d) % 2
    omega

#print axioms sum_shell_eq_prod


/- ---------- pairwise arithmetic for sigma ---------- -/

/-- Each pair (t-2m, t-2m-1) of one submask contributes exactly 2t-1-4m. -/
theorem shell_pair (t a : Nat) (h : 2 * a + 1 ≤ t) :
    (t - 2 * a) + (t - 2 * a - 1) = 2 * t - 1 - 4 * a := by
  omega

/-- The inner sum over the two halves of a submask. -/
theorem sum_range_two (t a : Nat) :
    (Finset.range 2).sum (fun b => t - 2 * a - b) = (t - 2 * a) + (t - 2 * a - 1) := by
  rw [show (2 : Nat) = 1 + 1 from rfl, Finset.sum_range_succ, Finset.sum_range_one]
  omega

#print axioms shell_pair
#print axioms sum_range_two


/-- The additive (subtraction-free) form of the sigma formula:
    the shell sum plus four times the submask sum is N * (2t-1). -/
theorem sigma_shell_add (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum id + 4 * (subm (r t)).sum id = (subm (r t)).card * (2 * t - 1) := by
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  rw [sum_shell_eq_prod t ht, Finset.sum_product]
  rw [Finset.sum_congr rfl (fun a _ => sum_range_two t a)]
  have hconst : (subm (r t)).sum (fun _ => 2 * t - 1) = (subm (r t)).card * (2 * t - 1) := by
    simp
  rw [← hconst, Finset.mul_sum, ← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro a ha
  have ha' : a ≤ r t := (mem_subm.mp ha).1
  have h1 : 2 * a + 1 ≤ t := by omega
  show (t - 2 * a) + (t - 2 * a - 1) + 4 * a = 2 * t - 1
  rw [shell_pair t a h1]
  omega

#print axioms sigma_shell_add


/-- The sigma formula: the sum of the levels carrying a zero is
    (#submasks) * (2t - 1 - 2 r t), i.e. 2^(wt (r t)) * (2t - 1 - 2 r t). -/
theorem sigma_shell (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum id = (subm (r t)).card * (2 * t - 1 - 2 * r t) := by
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  have h1 := sigma_shell_add t ht
  have h4 : 4 * (subm (r t)).sum id = (subm (r t)).card * (2 * r t) := by
    have h2 := two_mul_sum_subm (r t)
    calc 4 * (subm (r t)).sum id = 2 * (2 * (subm (r t)).sum id) := by ring
      _ = 2 * ((subm (r t)).card * r t) := by rw [h2]
      _ = (subm (r t)).card * (2 * r t) := by ring
  have hX : (shell t).sum id
      = (subm (r t)).card * (2 * t - 1) - 4 * (subm (r t)).sum id := by omega
  have hm := Nat.mul_sub (subm (r t)).card (2 * t - 1) (2 * r t)
  rw [hX, h4, ← hm]

#print axioms sigma_shell


/- ---------- the zero set is exactly the union of the shells ---------- -/

/-- In any geometry satisfying (H1)-(H4), the zero set at time t is exactly
    the union of the levels in shell t. -/
theorem universal_zero_iff {X : Type} (lev : X → Nat) (nbhd : X → Finset X)
    (hm : UMem nbhd) (hb : UBound lev nbhd) (hp : UPrev lev nbhd) (hn : UNext lev nbhd)
    (t : Nat) (ht : 1 ≤ t) (x : X) :
    ustate lev nbhd t x = 0 ↔ lev x ∈ shell t := by
  rw [universal lev nbhd hm hb hp hn t ht x, mem_shell]
  by_cases h : lev x ≤ t
  · rw [H_of_le h, G_zero_iff]
    exact ⟨fun hh => ⟨h, hh⟩, fun hh => hh.2⟩
  · rw [H_of_gt (by omega)]
    exact ⟨fun hz => absurd hz (by decide), fun hh => absurd hh.1 h⟩

/-- The one-dimensional rule 129: the zeros sit exactly at the depths in shell t. -/
theorem row_zero_iff_shell (t : Nat) (ht : 1 ≤ t) (j : Int) :
    row t j = 0 ↔ j.natAbs ∈ shell t := by
  rw [row_closed_form t ht j, mem_shell]
  exact Iff.rfl

/-- The middle column again, now read off from the shell set. -/
theorem row_middle_shell (t : Nat) (ht : 1 ≤ t) :
    row t 0 = 0 ↔ 0 ∈ shell t := by
  rw [row_zero_iff_shell t ht]
  simp

#print axioms universal_zero_iff
#print axioms row_zero_iff_shell
#print axioms row_middle_shell


/-- **The shell set in the form of the identity**
    S(t) = { t - 2m, t - 2m - 1 : m a submask of r t }. -/
theorem shell_eq_image (t : Nat) (ht : 1 ≤ t) :
    shell t = (subm (r t)).image (fun m => t - 2 * m)
      ∪ (subm (r t)).image (fun m => t - 2 * m - 1) := by
  have hb : 2 * r t + 1 ≤ t := two_mul_r_add_one_le t ht
  ext d
  simp only [mem_shell, Finset.mem_union, Finset.mem_image, mem_subm]
  constructor
  · rintro ⟨hdt, hcond⟩
    have hm : (t - d) / 2 ≤ r t := sub_le (show sub ((t - d) / 2) (r t) from hcond)
    have hdm := Nat.div_add_mod (t - d) 2
    have hlt := Nat.mod_lt (t - d) (by decide : 0 < 2)
    interval_cases h : (t - d) % 2
    · left
      exact ⟨(t - d) / 2, ⟨hm, hcond⟩, by omega⟩
    · right
      exact ⟨(t - d) / 2, ⟨hm, hcond⟩, by omega⟩
  · rintro (⟨m, ⟨hm1, hm2⟩, he⟩ | ⟨m, ⟨hm1, hm2⟩, he⟩)
    · rw [← he]
      refine ⟨by omega, ?_⟩
      rw [show t - (t - 2 * m) = 2 * m from by omega, div_two_mul]
      exact hm2
    · rw [← he]
      refine ⟨by omega, ?_⟩
      rw [show t - (t - 2 * m - 1) = 2 * m + 1 from by omega, div_two_mul_add_one]
      exact hm2

/-- The level 0 is a zero level exactly at the times 2^k - 1. -/
theorem zero_mem_shell (t : Nat) (ht : 1 ≤ t) :
    0 ∈ shell t ↔ ∃ k : Nat, 1 ≤ k ∧ t = 2 ^ k - 1 := by
  rw [← row_middle_shell t ht]
  exact row_middle t ht

#print axioms shell_eq_image
#print axioms zero_mem_shell


/- ---------- the nonnegative half of the zero set ---------- -/

/-- On the nonnegative half, the zero cells are indexed exactly by the shells. -/
theorem row_zero_pos_eq_shell (t : Nat) (ht : 1 ≤ t) :
    (Finset.range (t + 1)).filter (fun d => row t ((d : Nat) : Int) = 0) = shell t := by
  ext d
  simp [Finset.mem_filter, Finset.mem_range, mem_shell, row_zero_iff_shell t ht]

/-- Hence the number of zero cells on the nonnegative half is #shell t,
    which is the c_d = 2 case of "zeros = sum of the shell sizes". -/
theorem row_zero_pos_card (t : Nat) (ht : 1 ≤ t) :
    ((Finset.range (t + 1)).filter (fun d => row t ((d : Nat) : Int) = 0)).card
      = (shell t).card := by
  rw [row_zero_pos_eq_shell t ht]

#print axioms row_zero_pos_eq_shell
#print axioms row_zero_pos_card

/- ---------- the bit identity behind the shell set ---------- -/

/-- (e / 2) is a submask of r  <=>  e is 2m or 2m+1 for a submask m of r. -/
theorem shell_iff (e r : Nat) :
    (e / 2 &&& r = e / 2) ↔ ∃ m : Nat, m &&& r = m ∧ (e = 2 * m ∨ e = 2 * m + 1) := by
  constructor
  · intro h
    refine ⟨e / 2, h, ?_⟩
    have hdm := Nat.div_add_mod e 2
    have hlt := Nat.mod_lt e (by decide : 0 < 2)
    interval_cases h2 : e % 2
    · exact Or.inl (by omega)
    · exact Or.inr (by omega)
  · rintro ⟨m, hm, h | h⟩
    · rw [h, div_two_mul]; exact hm
    · rw [h, div_two_mul_add_one]; exact hm

#print axioms subm_two_mul
#print axioms subm_two_mul_add_one
#print axioms card_subm_two_mul_add_one
#print axioms shell_iff

end Rule129
end OEIS