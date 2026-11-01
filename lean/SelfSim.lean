
import Brocot

namespace OEIS
namespace Rule129

/-- partial sums of Stern's sequence -/
def FF (N : Nat) : Nat := (Finset.range N).sum fusc

/-- the cumulative dead-level count: sum of A(d) = fusc d + fusc (d+1) -/
def SS (N : Nat) : Nat := (Finset.range N).sum (fun d => fusc d + fusc (d + 1))

theorem sum_range_two_mul (f : Nat → Nat) (N : Nat) :
    (Finset.range (2 * N)).sum f
      = (Finset.range N).sum (fun i => f (2 * i)) + (Finset.range N).sum (fun i => f (2 * i + 1)) := by
  induction N with
  | zero => simp
  | succ n ih =>
    have h1 : (Finset.range (2 * (n + 1))).sum f
        = (Finset.range (2 * n)).sum f + f (2 * n) + f (2 * n + 1) := by
      rw [show 2 * (n + 1) = 2 * n + 1 + 1 from by ring, Finset.sum_range_succ,
        Finset.sum_range_succ]
    rw [h1, ih, Finset.sum_range_succ, Finset.sum_range_succ]
    ring

theorem FF_two_mul (N : Nat) : FF (2 * N) = FF N + SS N := by
  rw [FF, sum_range_two_mul]
  have h1 : (Finset.range N).sum (fun i => fusc (2 * i)) = FF N := by
    rw [FF]
    exact Finset.sum_congr rfl fun i _ => fusc_two_mul i
  have h2 : (Finset.range N).sum (fun i => fusc (2 * i + 1)) = SS N := by
    rw [SS]
    exact Finset.sum_congr rfl fun i _ => fusc_two_mul_add_one i
  rw [h1, h2]

theorem SS_eq (N : Nat) : SS N = 2 * FF N + fusc N := by
  have h0 : SS N = FF N + (Finset.range N).sum (fun d => fusc (d + 1)) := by
    rw [SS, FF, Finset.sum_add_distrib]
  have h1 : (Finset.range N).sum (fun d => fusc (d + 1))
      = (Finset.range (N + 1)).sum fusc - fusc 0 := by
    rw [Finset.sum_range_succ']
    omega
  have h2 : (Finset.range (N + 1)).sum fusc = FF N + fusc N := by
    rw [FF, Finset.sum_range_succ]
  rw [h0, h1, h2, fusc_zero]
  omega

/-- **the exact self-similarity**: S(2N) = 3 S(N) -/
theorem SS_two_mul (N : Nat) : SS (2 * N) = 3 * SS N := by
  have h1 := FF_two_mul N
  have h2 : SS (2 * N) = 2 * FF (2 * N) + fusc (2 * N) := SS_eq (2 * N)
  have h3 : SS N = 2 * FF N + fusc N := SS_eq N
  have h4 : fusc (2 * N) = fusc N := fusc_two_mul N
  omega

/-- iterated: S(2^k N) = 3^k S(N) -/
theorem SS_two_pow_mul (k N : Nat) : SS (2 ^ k * N) = 3 ^ k * SS N := by
  induction k with
  | zero => simp
  | succ k ih =>
    have h : 2 ^ (k + 1) * N = 2 * (2 ^ k * N) := by rw [pow_succ]; ring
    rw [h, SS_two_mul, ih, pow_succ]
    ring

/-- the block identity: S(1) = 1 and S(2^k) = 3^k -/
theorem SS_one : SS 1 = 1 := by
  rw [SS, Finset.sum_range_one, fusc_zero, fusc_one]

theorem SS_two_pow (k : Nat) : SS (2 ^ k) = 3 ^ k := by
  have h := SS_two_pow_mul k 1
  rw [Nat.mul_one, SS_one, Nat.mul_one] at h
  exact h



/-! ### the row side: the Gould/Sierpinski mass -/

/-- binary weight (popcount) -/
def wt : Nat → Nat
  | 0 => 0
  | 1 => 1
  | n + 2 => if (n + 2) % 2 = 0 then wt ((n + 2) / 2) else wt ((n + 2) / 2) + 1
termination_by n => n
decreasing_by all_goals omega

theorem wt_zero : wt 0 = 0 := wt.eq_1
theorem wt_one : wt 1 = 1 := wt.eq_2

theorem wt_two_mul (e : Nat) : wt (2 * e) = wt e := by
  rcases e with _ | e
  · rfl
  · have h : 2 * (e + 1) = 2 * e + 2 := by ring
    rw [h, wt.eq_3, if_pos (by omega : (2 * e + 2) % 2 = 0),
      show (2 * e + 2) / 2 = e + 1 from by omega]

theorem wt_two_mul_add_one (e : Nat) : wt (2 * e + 1) = wt e + 1 := by
  rcases e with _ | e
  · rw [wt.eq_2, wt_zero]
  · have h : 2 * (e + 1) + 1 = (2 * e + 1) + 2 := by ring
    rw [h, wt.eq_3, if_neg (by omega : ¬ ((2 * e + 1) + 2) % 2 = 0),
      show ((2 * e + 1) + 2) / 2 = e + 1 from by omega]

/-- **Gould / Sierpinski**: the number of odd entries in the first 2^k rows -/
theorem sum_pow_wt (k : Nat) : (Finset.range (2 ^ k)).sum (fun t => 2 ^ (wt t)) = 3 ^ k := by
  induction k with
  | zero => simp [wt_zero]
  | succ k ih =>
    have h : 2 ^ (k + 1) = 2 * 2 ^ k := by rw [pow_succ]; ring
    rw [h, sum_range_two_mul (fun t => 2 ^ (wt t)) (2 ^ k)]
    have h1 : (Finset.range (2 ^ k)).sum (fun i => 2 ^ (wt (2 * i)))
        = (Finset.range (2 ^ k)).sum (fun i => 2 ^ (wt i)) :=
      Finset.sum_congr rfl fun i _ => by rw [wt_two_mul]
    have h2 : (Finset.range (2 ^ k)).sum (fun i => 2 ^ (wt (2 * i + 1)))
        = 2 * (Finset.range (2 ^ k)).sum (fun i => 2 ^ (wt i)) := by
      rw [Finset.mul_sum]
      exact Finset.sum_congr rfl fun i _ => by rw [wt_two_mul_add_one, pow_succ]; ring
    rw [h1, h2, ih]
    ring

/-- the mass of one dyadic block: 2 * 3^k -/
theorem block_mass (k : Nat) :
    (Finset.range (2 ^ (k + 1))).sum (fun t => 2 ^ (wt t))
      - (Finset.range (2 ^ k)).sum (fun t => 2 ^ (wt t)) = 2 * 3 ^ k := by
  rw [sum_pow_wt, sum_pow_wt, pow_succ]
  omega

#print axioms sum_pow_wt
#print axioms block_mass
#print axioms SS_two_mul

end Rule129
end OEIS