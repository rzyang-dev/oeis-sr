import io
p = r"C:\Users\ginger\Documents\oeis\lean\Digits.lean"
s = io.open(p, encoding="utf-8").read()
s = s.replace("    exact W_congr_le k r i (fun l hl => hX l (Nat.le_trans hl (Nat.le_of_lt_succ hi))) i le_rfl",
              "    have hw : W k r (X n) i = W k r (X n') i :=\n      W_congr_le k r i (fun l hl => hX l (Nat.le_trans hl (Nat.le_of_lt_succ hi))) i le_rfl\n    rw [hw]")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched")
