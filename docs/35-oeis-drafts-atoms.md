# OEIS 投稿草案：自动序列的原子分析

> 所有关系均经 DFA 乘积严格验证（非抽样）。
> 按"新颖度"排序。

## A. 全新恒等式（OEIS 中无记载）

### A.1 A267442 与 A267579（Rule 129 ↔ Rule 167）

**提议（A267442 条目，Comments）：**

> a(n) = A267579(n-1) for n >= 2. Both are middle columns of elementary
> cellular automata (Rules 129 and 167). - [Your name], [date]

**提议（A267579 条目，Formula）：**

> a(n) = A267442(n-1) = 1 - A036987(n-1) for n >= 2, where A036987 is the
> Fredholm-Rueppel sequence (indicator of 2^k - 1). Proved in Lean 4.

理由：A267442 的 2016 年猜想（Mathar）已被我们证明；A267579 **完全没有任何
评论或公式**。这条关系由我们的定理立即推出。

### A.2 六对互不引用的平移关系

```
A014707(n) = A038189(n+1)
A035263(n) = A285384(n+1)
A036577(n) = A316826(n+1)
A043545(n) = A347523(n+1)
A092436(n) = A010059(n+1)
A267442(n) = A267579(n+1)   ← 新
```

前五对可能已在别处暗示，但条目间没有显式交叉引用。

## B. XOR 恒等式（27 条依赖关系中的代表）

**提议（A267442 条目）：**

> a(n) = A010059(n) XOR A010060(n) XOR A036987(n) XOR A209229(n) XOR A255738(n).
> (All five are 2-automatic; verified by automaton equivalence.)

**提议（A096268 条目）：**

> a(n) = A010059(n) XOR A010060(n) XOR A035263(n).
> Since A010059 XOR A010060 is constant, this is the complement relation.

**提议（A043545 条目）：**

> a(n) = A010059(n) XOR A010060(n) XOR A036987(n).

**16 条经比对为 OEIS 中无交叉引用的新恒等式**：

```
A014707 = A010059 ⊕ A010060 ⊕ A014577
A092436 = A010059 ⊕ A035263
A164056 = A014577 ⊕ A036987 ⊕ A099395
A254651 = A010059 ⊕ A228495
A267442 = A010059 ⊕ A010060 ⊕ A036987 ⊕ A209229 ⊕ A255738
A268411 = A010060 ⊕ A020987
A275973 = A010059 ⊕ A010060 ⊕ A030300 ⊕ A036987
A285383 = A010059 ⊕ A010060 ⊕ A284948
A285384 = A010059 ⊕ A010060 ⊕ A209229 ⊕ A255738 ⊕ A284948
A292077 = A014577 ⊕ A035263
A298952 = A010059 ⊕ A030300 ⊕ A036987
A328981 = A035263 ⊕ A038189 ⊕ A073089 ⊕ A209229 ⊕ A255738
A341389 = A010060 ⊕ A269723
A342892 = A010059 ⊕ A010060 ⊕ A086483
A359832 = A010059 ⊕ A010060 ⊕ A035263 ⊕ A038189 ⊕ A073089 ⊕ A209229 ⊕ A255738
A379728 = A010059 ⊕ A038189 ⊕ A073089 ⊕ A209229 ⊕ A228495 ⊕ A255738 ⊕ A255817 ⊕ A372258
```

其余 11 条已有交叉引用，见 docs/34-atoms.md。

## C. AND（合取）恒等式

**提议（A231600 条目）：**

> a(n) = A096268(n) AND A267442(n) = A043545(n) AND A096268(n).

**提议（A209229 条目）：**

> a(n) = A010060(n) AND A255738(n) = A255738(n) AND A268411(n).

## D. 结构性的评论（可选）

**提议（任一条目，或作为 OEIS wiki 页）：**

> Among the 195 non-eventually-periodic 2-automatic sequences in the b-file
> atlas, there are exactly 13 shift relations; these form 11 shift classes.
> Restricting to the 75 {0,1}-valued ones, the GF(2) rank is 48.

## 提交注意事项

- 每条评论附上 Lean 文件或脚本的链接（如果 GitHub 仓库已公开）；
- 优先提交 A.1（全新且由已证定理直接推出）；
- B/C 类表达式需要先逐条核对 OEIS 原有公式，避免重复；
- D 类属于"研究性评论"，编辑可能更谨慎，建议放最后。