import io
p = r"C:\Users\ginger\Documents\oeis\lean\Matrix.lean"
s = io.open(p, encoding="utf-8").read()
old1 = """    intro x hx
    have hx0 : ¬ x = 0 := by omega
    have hx1 : ¬ x - 1 = 0 := by omega
    simp only [hx0, hx1, if_false]
    push_cast [hx]
    simp [Finset.sum_range_succ]
    ring
  have h1 : ((if 1 = 0 then 1 else 4 * 1 : Nat) : Int)"""
new1 = """    intro x hx
    have hge : 1 ≤ x := by omega
    have hx0 : ¬ x = 0 := by omega
    have hx1 : ¬ x - 1 = 0 := by omega
    simp only [hx0, hx1, if_false]
    push_cast [hge]
    simp [Finset.sum_range_succ]
    ring
  have h1 : ((if 1 = 0 then 1 else 4 * 1 : Nat) : Int)"""
assert old1 in s
s = s.replace(old1, new1)
old2 = """      = (Finset.range (1 + 1)).sum (fun i => (if i = 0 then (-4 : Int) else 8))
        + 1 := by
    norm_num"""
new2 = """      = (Finset.range (1 + 1)).sum (fun i => (if i = 0 then (-4 : Int) else 8))
        + 1 := by
    simp [Finset.sum_range_succ]"""
assert old2 in s
s = s.replace(old2, new2)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched")
