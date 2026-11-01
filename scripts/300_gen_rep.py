import io

ROWS_PATCHED = [
    # name, j, polynomial P (Lean syntax in d), gamma, delta, c0, comment
    ("line",      0, "2",                     [4],                              -1, 1, "1-D line (level sizes 1, 2, 2, 2, ...)"),
    ("ray",       0, "1",                     [2],                               0, 1, "1-D ray (all levels 1)"),
    ("z2vn",      1, "4 * d",                 [-4, 8],                           1, 1, "Z^2 von Neumann (A169699)"),
    ("z2moore",   1, "8 * d",                 [-8, 16],                          1, 1, "Z^2 Moore (9-neighbourhood)"),
    ("tri",       1, "6 * d",                 [-6, 12],                          1, 1, "triangular lattice"),
    ("z3vn",      2, "4 * d * d + 2",         [8, -8, 8],                       -1, 1, "Z^3 von Neumann"),
    ("z3moore",   2, "24 * d * d + 2",        [28, -48, 48],                    -1, 1, "Z^3 Moore"),
    ("z4moore",   3, "64 * d^3 + 16 * d",     [-80, 224, -192, 128],             1, 1, "Z^4 Moore"),
    ("z4vn",      3, "8 * d * (d * d + 2)",   [-24, 56, -24, 16],                3, 3, "Z^4 von Neumann, scaled by 3"),
    ("z5moore",   4, "160 * d^4 + 80 * d * d + 2", [244, -800, 1120, -640, 320], -1, 1, "Z^5 Moore"),
    ("z5vn",      4, "4 * d^4 + 20 * d * d + 6",   [36, -56, 64, -16, 8],       -3, 3, "Z^5 von Neumann, scaled by 3"),
]

ROWS_PLAIN = [
    ("z2orthvn",  1, "d + 1",   [1, 2], "Z^2 quarter-plane von Neumann (level size d+1)"),
    ("z2orthmo",  1, "2 * d + 1", [0, 4], "Z^2 quarter-plane Moore (level size 2d+1)"),
]

def gamma_fn(g):
    s = f"({g[-1]} : Int)"
    for i in range(len(g) - 2, -1, -1):
        s = f"(if i = {i} then ({g[i]} : Int) else {s})"
    if len(g) == 1:
        s = f"({g[0]} : Int)"
    return "fun i => " + s

def gamma_sum(g):
    return " + ".join(f"({v} : Int)" for v in g)

def lean_int(v):
    return f"({v} : Int)" if v >= 0 else f"({v} : Int)"

out = []
out.append("")
out.append("/- ---------- the rows of the table, written through arm moments ---------- -/")
out.append("")
out.append("-- Each theorem says: the zero count is the integer combination of the arm")
out.append("-- moments given by gamma, plus the centre correction delta * [1 in arm t].")
out.append("")

for name, j, P, g, delta, c0, comment in ROWS_PATCHED:
    c = f"(fun d => if d = 0 then {c0} else {P})"
    out.append(f"/-- **{comment}** through the arm moments. -/")
    out.append(f"theorem phi_{name} (t : Nat) (ht : 1 ≤ t) :")
    out.append(f"    (((shell t).sum {c} : Nat) : Int)")
    out.append(f"      = (Finset.range {j+1}).sum (fun i => ({gamma_fn(g)}) i * (Phi i t : Int))")
    out.append(f"        + {lean_int(delta)} * (if 1 ∈ arm t then 1 else 0) :=")
    out.append(f"  shell_sum_of_poly_correction {c} ({gamma_fn(g)}) {j} {lean_int(delta)} t ht")
    out.append("    (by")
    out.append("      intro x hx")
    out.append("      have hge : 1 ≤ x := by omega")
    out.append("      have hx0 : ¬ x = 0 := by omega")
    out.append("      have hx1 : ¬ x - 1 = 0 := by omega")
    out.append("      simp only [hx0, hx1, if_false]")
    out.append("      push_cast [hge]")
    if j >= 1:
        out.append("      simp [Finset.sum_range_succ]")
        out.append("      ring)")
    else:
        out.append("      simp [Finset.sum_range_succ])")
    out.append(f"    (by norm_num [Finset.sum_range_succ])")
    out.append("")
    out.append(f"#print axioms phi_{name}")
    out.append("")

for name, j, P, g, comment in ROWS_PLAIN:
    c = f"(fun d => {P})"
    out.append(f"/-- **{comment}** through the arm moments. -/")
    out.append(f"theorem phi_{name} (t : Nat) (ht : 1 ≤ t) :")
    out.append(f"    (((shell t).sum {c} : Nat) : Int)")
    out.append(f"      = (Finset.range {j+1}).sum (fun i => ({gamma_fn(g)}) i * (Phi i t : Int)) :=")
    out.append(f"  shell_sum_of_poly {c} ({gamma_fn(g)}) {j} t ht")
    out.append("    (by")
    out.append("      intro x hx")
    out.append("      have hge : 1 ≤ x := by omega")
    out.append("      push_cast [hge]")
    out.append("      simp [Finset.sum_range_succ]")
    out.append("      ring)")
    out.append("")
    out.append(f"#print axioms phi_{name}")
    out.append("")

body = "\n".join(out)

p = r"C:\Users\ginger\Documents\oeis\lean\Rep.lean"
s = io.open(p, encoding="utf-8").read()
marker = "/- ---------- the rows of the table, written through arm moments ---------- -/"
idx = s.index(marker)
endm = "end Rule129"
idx2 = s.index(endm)
s = s[:idx] + body + "\n" + s[idx2:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("regenerated instantiation block:", len(out), "lines")
