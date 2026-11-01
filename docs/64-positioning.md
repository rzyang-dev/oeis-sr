# 64 对外结论单页（positioning）

> 合并 docs/58（边界与新颖性）、docs/61（OEIS 档案）、docs/63（文献 + NKS）。
> 这是整个项目"能声称什么、以什么措辞声称"的唯一结论页。

---

## 一句话

> **把一条元胞自动机（Rule 129，"全体邻居相等"）的零计数，归约成一个与几何无关的数位泛函
> `#Z(t) = Σ_{d∈shell(t)} c_d`，并把这条泛函的全部结构算清楚 —— 矩塔、2-kernel 秩、
> 壳层分解、列分布、以及在 256 条层归约规则中的位置。**

不是"发现了 Stern"，也不是"首次给出 Rule 129 的闭式"（这两件事都已有人做过，见下）。

---

## 二、可以声称的（7 条）

| # | 结论 | 状态 |
|---|---|---|
| 1 | **几何无关闭式**：对任意满足 (H1)–(H4) 的层结构空间，`x_t(v) = 1 − [⌊(t−‖v‖)/2⌋ ⊆ r(t)]` | 已证（纸面 + Lean，三实例） |
| 2 | **主定律**：`#Z(t) = Σ_{d∈shell(t)} c_d` —— 零计数是层大小向量的线性泛函，与几何无关 | 已证 + Lean |
| 3 | **对偶闭式**：`d ∈ shell(t) ⟺ (s−1) ⊆ ⌊(s−1+d)/2⌋`，`s = 2^{⌊log₂t⌋+1} − t` | 已证 + Lean（`mem_shell_dual`） |
| 4 | **秩定理**：`rank₂(Z_c) = #DClose(supp(c(x)+c(x−1))) + [δ≠0]` | 已证（闭式元素 + Vandermonde） |
| 5 | **列分布**：`\|Σ_d\| = fusc(d)+fusc(d+1)`；且**集合级**双射 `Σ_d ≅ Hyp(d) ⊎ Hyp(d−1)` | 已证 + Lean（`card_sig_stern`、`card_Hyp`、`card_sig_split`） |
| 6 | **精确自相似**：`S(2N) = 3·S(N)`；块质量 `2·3^k`；`Σ_{t<2^k}\|shell t\| = 3^k` | 已证 + Lean（`SelfSim`、`Mass`） |
| 7 | **分类**：256 条层归约规则 256/256 几何无关；非平凡 2-收缩**恰 8 条**、2 条轨道；**收缩常数 3 无解**；rule 90 闭式 | 已证 + 穷举（docs/54） |

形式化：`lean/` 21 个文件、395 条声明、无 `sorry`、公理仅 `propext/Classical.choice/Quot.sound`、
**从零重建审计通过**。

---

## 三、不可声称的（已被别人做过）

| 说法 | 谁先做过 |
|---|---|
| "Rule 129 中心列的零点是 `2^k−1`" | **NKS 2002**（"rule 129 can be thought of as enumerating numbers that are powers of 2"）+ **A071035 的 %Y（2002）** + A267442（2016，仍标猜想） |
| "一维零计数闭式 `2^{1+wt(t)} − [t=2^i−1]`" | **A071051**（Sloane, 2014-08-09，comment 就是 Rule 126） |
| "Stern ↔ 超二进制 / Stern ↔ Stirling 奇偶" | **A002487 的注释**（Carlitz；Stirling 那条）+ **A007306**（Cloitre 2004） |
| `A(d)` 本身 | = **A007306(d+1)** |
| Rule 129 的"嵌套/分形"定性、代数形式 | **NKS 2002**（第 3 章归类；p.884 的 Boolean 形式表） |

**我们的增量是"证明 + 推广 + 结构"，不是"发现"。**

---

## 四、检索方法与盲区（必须随结论一起报）

检索过：OEIS 本地快照（400,725 条）+ 现场 oeis.org JSON；arXiv API（元数据）；
DeepSeek 搜索 API（12 条查询）；**NKS 全书 PDF 本地全文**（9.83M 字符，自建 zlib 提取器）。

**没有检索**：MathSciNet / zbMATH（订阅墙，最大盲区）；Google Scholar（限流）；
期刊全文库；"图 CA / 共识动力学"这条线的深水区（只试了 1 条查询）。

所以正确措辞是 **"在有限检索下未找到"**，不是"新"。

---

## 五、给投稿用的 novelty statement（可直接引用）

> We give a closed form for the zero set of the "all neighbours equal" elementary cellular
> automaton (Rule 129) which is **independent of the underlying geometry**: it depends only on
> four abstract layer hypotheses, and therefore holds simultaneously for the line, for the plane
> with the von Neumann or Moore neighbourhood, and for the infinite binary tree — three spaces on
> which the automaton's local neighbourhoods have different sizes and different symmetries.
> The key structural statement is a *master law*: the number of zeros at time `t` is a **linear
> functional of the layer-size sequence**, evaluated on a digit-defined set `shell(t)`.
> For linear rules the analogous theory is algebraic (Martin–Odlyzko–Wolfram 1984); Rule 129 is
> nonlinear and our method is combinatorial (submask / digit DP). Consequences include an exact
> `2`-kernel rank formula for the zero-count sequences, an exact self-similarity `S(2N)=3S(N)`
> for the cumulative level counts, and a census of all layer-reducible rules (exactly eight
> non-trivial dyadic contractions, and no `c=3` analogue). The development is formalised in Lean 4
> (395 declarations, no `sorry`, standard axioms only).
>
> We emphasise what is *not* new: that the centre column of Rule 129 encodes the powers of two is
> stated in Wolfram's *A New Kind of Science* (2002) and in OEIS A071035 (2002); the one-dimensional
> zero-count formula appears in OEIS A071051 (2014); the Stern-number connection of the level
> distribution is implicit in OEIS A002487 / A007306 (Carlitz; Cloitre 2004). Our contribution is
> the proof, the geometry-independent generalisation, and the rank/classification structure.
