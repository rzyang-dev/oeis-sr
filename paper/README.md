# A case study of the unanimity cellular automaton (rule 129)

Files:

* **main.md** — the manuscript (Markdown with LaTeX display math; convert with pandoc:
  pandoc main.md -o main.pdf --pdf-engine=xelatex ).
* **verification.md** — the verification manifest: what was checked, with which script, over which
  range, and what is *not* verified.
* **../lean/** — the Lean 4 formalisation (21 files, 395 declarations, no sorry).
* **../docs/** — the working notes, one document per round; docs/64-positioning.md is the one-page
  summary of what can and cannot be claimed.
* **../scripts/** — every numerical check quoted in the paper.

Headline results (details in main.md):

1. The closed form x_t(y) = 0 iff lev(y) <= t and floor((t-lev(y))/2) submask of r(t) is **independent
   of the geometry**: it holds on every space satisfying four abstract layer hypotheses, hence on the
   line, on the plane with the von Neumann or Moore neighbourhood, and on the infinite binary tree.
2. The zero count is a **linear functional of the layer-size sequence**: Z_c(t) = sum over d in S(t)
   of c_d, with S(t) a fixed digit-defined set.
3. The 2-kernel rank of that sequence is exactly #DClose(supp(c(x)+c(x-1))) + [delta != 0].
4. Among all 256 layer rules, exactly 8 admit a non-trivial dyadic contraction, and none admits one
   with constant 3.

What is *not* new is stated in section 1.2 of the paper: the powers-of-two centre column is in
Wolfram's A New Kind of Science (2002) and in OEIS A071035 (2002); the one-dimensional zero-count
formula is OEIS A071051 (2014); the Stern-number counts are in OEIS A002487 / A007306.
