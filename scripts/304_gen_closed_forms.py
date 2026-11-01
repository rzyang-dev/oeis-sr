import io

ROWS = [
    ("z2moore", "(fun d => if d = 0 then 1 else 8 * d)", "-8", "16", "1", "Z^2 Moore"),
    ("tri", "(fun d => if d = 0 then 1 else 6 * d)", "-6", "12", "1", "the triangular lattice"),
    ("z2orthvn", "(fun d => d + 1)", "1", "2", "0", "the Z^2 quarter-plane von Neumann"),
    ("z2orthmo", "(fun d => 2 * d + 1)", "0", "4", "0", "the Z^2 quarter-plane Moore"),
]

def body(name, c, g0, g1, delta, comment):
    lines = []
    lines.append(f"/-- **{comment}**, in closed form.** -/")
    lines.append(f"theorem phi_{name}_explicit (k r n : Nat) (hr : r < 2 ^ k) (hn : 1 ≤ n) :")
    lines.append(f"    (((shell (2 ^ k * n + r)).sum {c} : Nat) : Int)")
    lines.append(f"      = {g0} * ((subm r).card * (Phi 0 n : Int))")
    lines.append(f"        + ({g1} * 2 ^ k * (subm r).card) * (Phi 1 n : Int)")
    lines.append(f"        + {delta} * (if 1 ∈ arm (2 ^ k * n + r) then 1 else 0) := by")
    lines.append("  have hγ : ∀ x : Nat, 2 ≤ x →")
    lines.append(f"      (({c} x : Nat) : Int) + (({c} (x - 1) : Nat) : Int)")
    lines.append("        = (Finset.range (1 + 1)).sum")
    lines.append(f"            (fun i => (if i = 0 then ({g0} : Int) else {g1}) * (x : Int) ^ i) := by")
    lines.append("    intro x hx")
    lines.append("    have hge : 1 ≤ x := by omega")
    lines.append("    have hx0 : ¬ x = 0 := by omega")
    lines.append("    have hx1 : ¬ x - 1 = 0 := by omega")
    lines.append("    simp only [hx0, hx1, if_false]")
    lines.append("    push_cast [hge]")
    lines.append("    simp [Finset.sum_range_succ]")
    lines.append("    ring")
    lines.append("  have h1 :")
    lines.append(f"      ((({c} 1 : Nat)) : Int) + ((({c} (1 - 1 : Nat)) : Nat) : Int)")
    lines.append("        = (Finset.range (1 + 1)).sum")
    lines.append(f"            (fun i => (if i = 0 then ({g0} : Int) else {g1})) + {delta} := by")
    lines.append("    norm_num [Finset.sum_range_succ]")
    lines.append("  have hpos : 1 ≤ 2 ^ k * n + r := by")
    lines.append("    have h2k : 0 < 2 ^ k := by positivity")
    lines.append("    have hmm : 0 < 2 ^ k * n := Nat.mul_pos h2k (by omega)")
    lines.append("    omega")
    lines.append(f"  rw [Z_state {c} (fun i => if i = 0 then ({g0} : Int) else {g1}) 1 {delta}")
    lines.append("    hγ h1 k n r hpos hn hr]")
    lines.append("  rw [Finset.sum_range_succ, Finset.sum_range_one, W_zero k r (X n) hr,")
    lines.append("    W_one k r (X n) hr]")
    lines.append("  simp only [X]")
    lines.append("  push_cast")
    lines.append("  ring")
    lines.append("")
    lines.append(f"#print axioms phi_{name}_explicit")
    lines.append("")
    return "\n".join(lines)

out = ["", "/- ---------- closed forms for the other degree-one rows ---------- -/", ""]
for row in ROWS:
    out.append(body(*row))
body_text = "\n".join(out)

p = r"C:\Users\ginger\Documents\oeis\lean\Matrix.lean"
s = io.open(p, encoding="utf-8").read()
marker = "/- ---------- closed forms for the other degree-one rows ---------- -/"
if marker in s:
    s = s[:s.index(marker)]
s = s.rstrip() + "\n" + body_text + "\nend Rule129\nend OEIS\n"
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("regenerated 4 closed forms")
