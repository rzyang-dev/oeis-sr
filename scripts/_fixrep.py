import io, re
p = r"C:\Users\ginger\Documents\oeis\lean\Rep.lean"
s = io.open(p, encoding="utf-8").read()
old_pos = """  · by_cases hmem : 1 ∈ arm t
    · simp only [Nat.cast_sum, Finset.sum_range_succ, Finset.sum_range_one, if_pos hmem] at h ⊢
      linarith [h]
    · simp only [Nat.cast_sum, Finset.sum_range_succ, Finset.sum_range_one, if_neg hmem] at h ⊢
      linarith [h]"""
new_pos = """  · by_cases hmem : 1 ∈ arm t
    · simp [Finset.sum_range_succ, hmem] at h ⊢
      linarith [h]
    · simp [Finset.sum_range_succ, hmem] at h ⊢
      linarith [h]"""
n = s.count(old_pos)
s = s.replace(old_pos, new_pos)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("replaced", n, "occurrences")
