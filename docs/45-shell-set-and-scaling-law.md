# 45 壳层集合与几何标度律（附 A169699 公式的修正）

## 出发点

通用闭式（docs/42、Universal.lean 机器验证）：

    x_t(v) = 1 − [ ⌊(t − ‖v‖)/2⌋ ⊆ r(t) ],     r(t) = t − 2^⌊log₂ t⌋

其中 `⊆` 是二进制子掩码。据此，"0 的集合"（等价地：补规则的 ON 集合）
**永远是若干完整壳层的并**，而哪些壳层出现只由 t 的二进制决定：

    S(t) = { d : 0 ≤ d ≤ t, ⌊(t−d)/2⌋ ⊆ r(t) }
         = { t − 2m, t − 2m − 1 : m ⊆ r(t) }        （集合恒等式）

第二条等式是新的化简：把"⌊·/2⌋ 的子掩码条件"换成了"对 r 的所有子掩码求和"。
数值验证：t ≤ 2000 全部吻合（scripts/268_sigma_formula.py）。

于是**任意几何**的零点数都是壳层求和：

    N(t) = Σ_{d ∈ S(t)} c_d ,      c_d = 第 d 层的点数 .

## 标度律

记 σ(t) = Σ_{d ∈ S(t), d ≥ 1} d，ε(t) = [0 ∈ S(t)]。则

    σ(t) = 2^{wt(r)} · (2t − 1 − 2r) ,      ε(t) = [t = 2^k − 1] ,

（wt = 二进制重量；ε 就是 R129.lean 的中列定理 `row_middle`）。

| 几何 | c_d | N(t) = 零点数（t ≥ 1） | t = 1,2,3,… |
|---|---|---|---|
| 一维 Rule 126（补规则） | c₀=1, c_d=2 | 2^{1+wt(t)} − ε | 3,4,7,4,8,8,15,4,… |
| ℤ² 5-邻居（von Neumann） | c₀=1, c_d=4d | 4σ + ε | 5,12,25,28,56,56,113,… |
| ℤ² 3×3（Moore） | c₀=1, c_d=8d | 8σ + ε | 9,24,49,56,112,112,225,… |
| 无限二叉树 | c_d = 2^d | Σ_{d∈S} 2^d | 3,6,15,24,60,102,255,… |

注意 t = 0 是退化情形：此时只有一个 1，零点集是无限的（树上也如此），
所以所有计数都从 t = 1 开始；OEIS 那几条把 a(0)=1 当作"ON 格数"的约定值。
对 t ≥ 1，"全体邻居相等"规则的**零点集**恰好等于补规则（Rule 126 / Rule 510）
的 **ON 集合**，这正是下面对照 OEIS 的依据。

一维的 c_d 是常数 2，所以用 |S| 而不是 σ；这正是"±1 修正"符号不同的原因（见下）。

## 与 OEIS 的对照：三个已存在的序列 + 一个新序列

* **A071051**（一维 Rule 126 的 ON 数）：OEIS 给出
  `a(n) = 2^(1+wt(n))，若 n = 2^i − 1 则减 1` —— 正确，
  和我们的一维行完全一致。我们的推导给出了它**为什么**长这样。
* **A169699**（二维 5-邻居 Rule 510 的 ON 数）：OEIS 给出
  `a(n) = (2^(k+1)−1)·2^(1+wt(n))，若 n 是 2 的幂则加 1`。
  **这条公式是错的**：用它算前 52 项（OEIS 自己列出的数据）有 **9 处不符**：
  n = 2,4,8,16,32（2 的幂）与 n = 3,7,15,31（2^k−1）。
  正确形式是

      a(n) = (2^{k+1} − 1)·2^{1+wt(n)} + [n = 2^i − 1] ,   n ≥ 1,

  即"加 1"的条件是 **n 恰好是 2^i−1**，而不是"n 是 2 的幂"。
  用我们的公式 4σ+ε 检验 52 项：**0 处不符**（scripts/270_a169699.py）。
* **二维 3×3（9 邻居）版本**：1,9,24,49,56,112,112,225,120,240,… **不在 OEIS 中**
  （2025 年检索返回空）。它是一个有明确闭式的新序列：
  `a(0)=1, a(n) = 8σ(n) + ε(n)`，或用 wt 写：

      a(n) = 2·(2^{k+1} − 1)·2^{1+wt(n)} + [n = 2^i − 1] .

## 为什么"+1 的位置"必然是中列

第 0 层只有一个格子，而公式 c_d = c·d 在 d=0 处给 0。所以求和里必须补上
`[0 ∈ S(t)]` 这一项 —— 而 0 ∈ S(t) 当且仅当中心格子是 0，当且仅当
t = 2^k−1（`row_middle` / A267442）。**A169699 的错误恰好是把这一项挂到了
错误的条件上**：它挂到"n 是 2 的幂"，正确的位置是"n 是 2^k−1"。
一维情形同理，只是 c_d=2（常数）使得 d=0 的修正方向变成减 1。

## 验证清单

| 检查 | 脚本 | 结果 |
|---|---|---|
| S(t) 的集合恒等式与 σ 闭式，t ≤ 2000 | `268_sigma_formula.py` | 0 处不符 |
| ℤ² Moore / von Neumann 的壳层结构（缺陷集模拟，t ≤ 32） | `266_shells.py` | 0 处违规，0 处计数不符 |
| A169699 的 52 项 | `270_a169699.py` | 公式 4σ+ε 全中；OEIS 现公式 9 处错 |
| 三种几何的计数与壳层求和 | `269_geometry_counts.py` | 见上表 |
| 二叉树上"整棵树 = 层剖面" | `265_tree.py` | 130 个 (t,d) 对全中 |

## 这一节的新东西是什么

1. **集合层面的陈述**：ON/OFF 集合是壳层的并，且壳层索引集有显式形状
   `S(t) = {t−2m, t−2m−1 : m ⊆ r(t)}`。文献（Packard–Wolfram, NKS）
   只有计数，没有集合形状。
2. **几何无关性**：同一个 S(t) 同时描述一维、二维两种邻域、以及二叉树；
   计数差异只来自 c_d。这一点由 Lean 定理 `universal` 保证。
3. **A169699 的修正**：一个可核对的具体勘误 + 一个"为什么"。
4. **一个新序列**：9 邻居版本有闭式但不在 OEIS 中。

## 下一步

* 在 Lean 里把壳层求和形式化：定义 `S(t)`，证明
  `S(t) = {t−2m, t−2m−1 : m ⊆ r}` 与 `σ(t) = 2^{wt(r)}(2t−1−2r)`，
  再证"任意壳层可加统计量 = Σ c_d"。这需要 `Finset` 求和与子掩码枚举的组合引理。
* 对 d 维 Moore（c_d = (2d+1)^D − (2d−1)^D）给出同一标度律；
  这是"几何只通过 c_d 进入"的最强展示。
* 检查是否还有其它 OEIS 序列是这套壳层结构的实例（Rule 126/510 的亲属、
  一维半径 2 的规则等）。

## Lean 形式化进度（rounds 1-2）

文件 `lean/Shells.lean`（`import Universal`，编译 ~40 秒；`Universal.lean` 只需在
改动时用 `lean -o Universal.olean Universal.lean` 重编一次）。以下全部无 sorry，
公理为 `[propext, Classical.choice, Quot.sound]`：

| 定理 | 内容 |
|---|---|
| `shell_iff` | `(e/2) &&& r = e/2 ↔ ∃ m, m &&& r = m ∧ (e = 2m ∨ e = 2m+1)` —— 零集恒等式的逐点形式 |
| `subm_two_mul` | `subm (2u) = (subm u).map (·*2)` |
| `subm_two_mul_add_one` | `subm (2u+1) = (subm u).map (·*2) ∪ (subm u).map (·*2+1)` |
| `card_subm_two_mul` | `#subm (2u) = #subm u` |
| `card_subm_two_mul_add_one` | `#subm (2u+1) = 2 · #subm u`（popcount 递推） |
| `r_eq_t_sub_pow` | `r t = t − 2^(log2 t)`（t ≥ 1） |
| `two_mul_r_le` | `2·r t ≤ t` |
| `two_mul_r_add_one_le` | `2·r t + 1 ≤ t` |
| `mem_shell` | `d ∈ shell t ↔ d ≤ t ∧ (t−d)/2 ⊆ r t` |
| **`card_shell`** | **`#(shell t) = 2 · #(subm (r t))`** —— 零集是 `2·#subm(r t)` 个完整壳层的并 |

`card_shell` 的证明用 `Finset.card_bij`，双射是

    (m, b) ↦ t − 2m − b ,    m ∈ subm (r t),  b < 2

单射性靠 `(2m+b)/2 = m`、`(2m+b)%2 = b`（b < 2），满射性靠 `t−d = 2·((t−d)/2) + (t−d)%2`。
数值核对（`scripts/271_card_shell_check.py`，t ≤ 2000）：`#shell t = 2·#subm(r t) = 2^(1+wt(r t))`，0 处不符。

### 下一轮

* **σ 的闭式**：`σ(t) = Σ_{d∈shell t} d`。路线：`Finset.sum_bij`（由 `to_additive` 生成，
  源码里查不到名字，需要按其签名试）把和搬到 univ × {m ⊆ r, b < 2} 上，
  得 `σ = 2t·N − 4·Σm − N`；再用 `2·Σ_{m⊆r} m = N·r` 得 `σ = N·(2t−1−2r)`，
  `N = #subm (r t) = 2^wt(r t)`。
* `Σ_{m⊆r} m` 的递推：`sum_subm_two_mul`、`sum_subm_two_mul_add_one`（后者 = `4Σ + N`）。
* d 维 Moore 与 b 叉树实例：放在新文件 `Instances.lean`（`import Universal`），避免重编大文件。
### Round 3 追加

| 定理 | 内容 |
|---|---|
| `sum_subm_two_mul` | `(subm (2u)).sum id = 2 · (subm u).sum id` |
| `sum_subm_two_mul_add_one` | `(subm (2u+1)).sum id = 4 · (subm u).sum id + (subm u).card` |
| **`two_mul_sum_subm`** | **`2 · Σ_{m ⊆ r} m = (#subm r) · r`** |

即 `Σ_{m⊆r} m = N·r/2`（N = #subm r = 2^wt(r)）。这条加上 `card_shell` 的双射，立刻给出

    σ(t) = Σ_{d∈shell t} d = Σ_{m⊆r} [(t−2m) + (t−2m−1)] = N(2t−1) − 4·(N·r/2) = N·(2t−1−2r),

也就是 `σ(t) = 2^{wt(r(t))}·(2t−1−2r(t))`。**唯一还缺的一步是把和从 shell 搬到子掩码上**
（`Finset.sum_bij`，或 `shell t = image₁ ∪ image₂` + `sum_image` + `sum_union`）。

工程细节：这个 Lean 版本里 `∑ i in s, f i` 不合法，必须写 `∑ i ∈ s, f i`；此外
`∑ i ∈ s, i` 与 `s.sum id` 是定义相等但语法不同，omega/ring 会把它们当成两个原子，
必须显式 `rw [show (∑ i ∈ s, i) = s.sum id from rfl]`。
### Round 4 追加：搬运完成

```lean
theorem sum_shell_eq_prod (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum id
      = ((subm (r t)) ×ˢ (Finset.range 2)).sum (fun p => t - 2 * p.1 - p.2)
```

用 `Finset.sum_bij`（签名是先 `i : ∀ a ∈ s, β`，再 `hi`、`i_inj`、`i_surj`、
最后 `h : ∀ a ha, f a = g (i a ha)`；它由 `prod_bij` 经 `to_additive` 生成，
所以源码里 grep 不到）。双射取 `d ↦ ((t−d)/2, (t−d)%2)`，逆映射 `(m,b) ↦ t−2m−b`。

**于是 σ 的闭式只剩一次纯算术**：

    σ(t) = Σ_{m⊆r} [(t−2m) + (t−2m−1)]
         = Σ_{m⊆r} (2t − 1 − 4m)              [需 2m+1 ≤ t，已证]
         = N(2t−1) − 4·(N·r/2)                [two_mul_sum_subm]
         = N·(2t − 1 − 2r) ,   N = #subm (r t) = 2^wt(r t) .

剩下的工作是把 `Finset.sum_product` + `range 2` 的内和展开，再消去 Nat 减法
（建议先证 `(t−2a) + (t−2a−1) = 2t−1−4a` 作为单点引理，避免和大运算符角力）。
### Round 5 追加：σ 的两个记账引理

```lean
theorem shell_pair (t a : Nat) (h : 2 * a + 1 ≤ t) :
    (t - 2 * a) + (t - 2 * a - 1) = 2 * t - 1 - 4 * a

theorem sum_range_two (t a : Nat) :
    (Finset.range 2).sum (fun b => t - 2 * a - b) = (t - 2 * a) + (t - 2 * a - 1)
```

第一条是关键的单点恒等式：一个子掩码 m 贡献的两个壳层 `t−2m`、`t−2m−1`
之和恰为 `2t−1−4m`（代价是必须知道 `2m+1 ≤ t`，这正是 `two_mul_r_add_one_le` 给的）。
第二条把 `range 2` 上的内和摊开，用 `Finset.sum_range_succ` + `Finset.sum_range_one`
两次展开即可；注意这里 **不能用 `ring`**（Nat 减法），要用 `omega`。

于是在 `sum_shell_eq_prod`、`shell_pair`、`sum_range_two` 三者之上，只剩
`Finset.sum_product` 的调用与最后一步 `Nat.mul_sub`：

    X + 4·Σm = Σ_{m⊆r} [(t−2m)+(t−2m−1)+4m] = Σ_{m⊆r} (2t−1) = N(2t−1)
    ⇒ X = N(2t−1) − 4·(Nr/2) = N(2t−1−2r)      [Nat.mul_sub，需 2r ≤ 2t−1]

写成**无减法**的形式（更省事、也更接近 OEIS 的写法）：

    theorem sigma_shell_add : (shell t).sum id + 4 * (subm (r t)).sum id
                              = (subm (r t)).card * (2 * t - 1)
### Round 6：σ 闭式完成 ✅

```lean
theorem sigma_shell_add (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum id + 4 * (subm (r t)).sum id = (subm (r t)).card * (2 * t - 1)

theorem sigma_shell (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum id = (subm (r t)).card * (2 * t - 1 - 2 * r t)
```

即 **σ(t) = N·(2t − 1 − 2r t)**，N = #subm (r t) = 2^{wt(r t)}，正是目标里的
`σ(t) = 2^{wt(r)}(2t−1−2r)`。证明链条：

1. `sum_shell_eq_prod`：把 shell 上的和搬到子掩码乘积；
2. `Finset.sum_product` + `sum_range_two`：摊开 `range 2` 的内和；
3. `shell_pair`：每个子掩码贡献 `2t−1−4m`，与 `4m` 配平得 `Σ(2t−1) = N(2t−1)`；
4. `two_mul_sum_subm`：`2Σm = N·r`，故 `4Σm = N·(2r)`；
5. `Nat.mul_sub`：`N(2t−1) − N(2r) = N(2t−1−2r)`。

工程坑（本轮全部踩到并解决）：
* `Finset.mul_sum` 的方向是 `a * Σ f = Σ (a * f)`，所以要 **正向** `rw [Finset.mul_sum]`
  （我一开始写了 `←`，报 "pattern not found"，附带把目标打印出来，正好提示了方向）；
* `sum_add_distrib` 要用 `←`（把两个和并成一个，才能逐点用 `shell_pair`）；
* 最后一步先 `rw [hX, h4]` 把左边化成 `N(2t−1) − N(2r)`，再 `rw [← Nat.mul_sub]` 收尾，
  比直接和 Nat 减法搏斗省事得多。
### Round 7：零集 = 壳层并（几何层）

```lean
/-- 任何满足 (H1)-(H4) 的几何：零集恰好是 shell t 里那些层的并。 -/
theorem universal_zero_iff {X : Type} (lev : X → Nat) (nbhd : X → Finset X)
    (hm : UMem nbhd) (hb : UBound lev nbhd) (hp : UPrev lev nbhd) (hn : UNext lev nbhd)
    (t : Nat) (ht : 1 ≤ t) (x : X) :
    ustate lev nbhd t x = 0 ↔ lev x ∈ shell t

/-- 一维 Rule 129：零点恰好出现在 shell t 的深度上。 -/
theorem row_zero_iff_shell (t : Nat) (ht : 1 ≤ t) (j : Int) :
    row t j = 0 ↔ j.natAbs ∈ shell t

/-- 中列再一次被读出：row t 0 = 0 ↔ 0 ∈ shell t。 -/
theorem row_middle_shell (t : Nat) (ht : 1 ≤ t) : row t 0 = 0 ↔ 0 ∈ shell t
```

这三条把"零点计数 = Σ c_d"的**数学内容**落到了机上：几何只通过"每层有多少点"
(c_d) 进入计数，而*哪些层*出现由 `shell t` 唯一决定。剩下的计数工作纯属有限集
基数运算：对每个几何取 `#{x : lev x = d} = c_d`，求和即得。
一维的下一个目标是把

    #(Icc (−t) t 中的零点) = 2·#(shell t) − [0 ∈ shell t]

证出来（每层 d ≥ 1 有两个点 ±d，d = 0 只有一个）；工具是
`Finset.card_eq_sum_card_fiberwise`（按 `j ↦ j.natAbs` 分纤维）。
### Round 8：目标里的恒等式，字面形式

```lean
/-- S(t) = { t - 2m, t - 2m - 1 : m ⊆ r t }  —— 作为 Finset 恒等式 -/
theorem shell_eq_image (t : Nat) (ht : 1 ≤ t) :
    shell t = (subm (r t)).image (fun m => t - 2 * m)
      ∪ (subm (r t)).image (fun m => t - 2 * m - 1)

/-- 第 0 层是零层，当且仅当 t = 2^k - 1。 -/
theorem zero_mem_shell (t : Nat) (ht : 1 ≤ t) :
    0 ∈ shell t ↔ ∃ k : Nat, 1 ≤ k ∧ t = 2 ^ k - 1
```

至此，目标的第一项 **`S(t) = {t−2m, t−2m−1 : m ⊆ r(t)}`** 以两种形式落地：
逐点的 `shell_iff`，和集合的 `shell_eq_image`。`zero_mem_shell` 则把
"哪一层会是零层" 与 2^k−1 直接连起来（它其实是 `row_middle` 的壳层版）。

### 一维零点计数的数值核对（待形式化）

`scripts/272_row_zero_count.py` 用直接模拟（半径 2T+3 的窗口）核对

    #zeros(t) = 2·#(shell t) − [0 ∈ shell t]

t ≤ 30 全部吻合（0 处不符）。前 16 项：`3,4,7,4,8,8,15,4,8,8,16,8,16,16,31,4`，
与 OEIS A071051（一维 Rule 126 的 ON 格数，偏移 1）一致。形式化路线：
`Finset.card_eq_sum_card_fiberwise`（按 `j ↦ j.natAbs` 分纤维），或把零集写成
`(shell t).image (·:Int) ∪ (shell t).image (−·:Int)` 再数基数。
### Round 9：OEIS 交叉核对做成可复跑脚本

`scripts/273_oeis_crosscheck.py` 用 OEIS 的**已发布项**核对三个公式：

| 目标 | 数据 | 结果 |
|---|---|---|
| A169699 的壳层公式 `4σ+ε` | 52 项 | **0 处不符** |
| A169699 的 wt 形式 `(2^(k+1)−1)·2^(1+wt(n)) + [n=2^i−1]` | 52 项 | **0 处不符** |
| A169699 **条目里现写的**公式（`+1 若 n 是 2 的幂`） | 52 项 | **9 处不符** |
| A071051 的一维公式 `2^(1+wt(n)) − [n=2^i−1]` | 20 项 | **0 处不符** |

错误位置恰好是 `n = 2, 3, 4, 7, 8, 15, 16, 31, 32` —— 也就是**全部的 2 的幂与 2^k−1**
（前 52 项里各有 5 个和 4 个，合计 9）。例：n=2 时 OEIS 数据是 12，条目公式给 13。

脚本还打印了一张对照表（n ≤ 16）：壳层集合、`#S`、σ、一维零点数、vN 零点数、
A169699 已发布值，逐行一致。

**为什么错误必然出现在这两类 n 上**（形式化依据）：
`+1` 这一项来自第 0 层是单点而 `c_d = 4d` 在 d=0 处给 0。第 0 层非空当且仅当
`0 ∈ shell n`，由 `zero_mem_shell`（本轮前一轮刚证）等价于 `n = 2^i − 1`。
把它挂在 `n 是 2 的幂` 上，就正好在两类数上各错一次。
### Round 10：任意分支数树（`Instances.lean`）

```lean
def blev (x : List (Fin b)) : Nat := x.length
def bnb (x : List (Fin b)) : Finset (List (Fin b)) :=
  insert x (insert x.dropLast ((Finset.univ : Finset (Fin b)).image (fun i => x ++ [i])))

theorem bnb_bound  : y ∈ bnb x → blev y + 1 ≥ blev x ∧ blev y ≤ blev x + 1
theorem bnb_prev   : 1 ≤ blev x → ∃ y ∈ bnb x, blev y = blev x - 1
theorem bnb_next   : 0 < b → ∃ y ∈ bnb x, blev y = blev x + 1

/-- 所有分支数 b ≥ 1：根处的中列都是 2^k − 1。 -/
theorem btree_middle (hb : 0 < b) (t : Nat) (ht : 1 ≤ t) :
    ustate blev (bnb (b := b)) t [] = 0 ↔ ∃ k : Nat, 1 ≤ k ∧ t = 2 ^ k - 1
```

记号：`variable {b : Nat}`；层 d 有 `b^d` 个点，邻域 `{自身, 父, 全部 b 个子}`。
四条假设逐条验证：`(H1)` 由 `bnb_cases`（三分情形 + 长度计算）、`(H2)` 由
`Finset.mem_insert_self`、`(H3)` 取 `x.dropLast`（`List.length_dropLast`）、
`(H4)` 取 `x ++ [⟨0, hb⟩]`。

数值核对（`scripts/274_btree_b.py`，b = 2,3,4，深度 8、时间 6）：
每个 b 各 42 个 (t,d) 对，**0 处不符、0 个非一致层**，根为 0 的时刻都是 {1, 3}。

工程坑：`universal_middle_zero` 的第二个参数要求 `UBound lev nbhd`（一个 `def`），
直接传 `bnb_bound`（隐式参数的 ∀ 形式）会报 "Application type mismatch"；
解决办法是先把四条假设各自显式打包：

```lean
have hbnd : UBound blev (bnb (b := b)) := fun x y h => bnb_bound h
have hnext : UNext blev (bnb (b := b)) := fun x => bnb_next hb x
```

另外 `simp [blev]` 在 `x ++ [i]` 的长度上会留下 `x.length ≤ x.length + 1 + 1`，
换成 `simp only [blev, List.length_append, List.length_singleton]; omega` 才干净。
### Round 11：整体完整性核对 + d 维 Moore 的设计定稿（未实施）

完整性核对（本轮实测）：

    Shells.lean    : errors=0 sorry=0
    Instances.lean : errors=0 sorry=0

把 d 维 Moore 的实现方案定下来（下一轮直接写）：

* 空间 `X = Fin D → Nat`，层 `dlev x := Finset.univ.sup x`；
* 邻域**不要**用 `Finset.pi`（`Finset.mem_pi` 在这个 Mathlib 里没找到），改用偏移像：

      def dnb (x : Fin D → Nat) : Finset (Fin D → Nat) :=
        (Finset.univ : Finset (Fin D → Fin 3)).image (fun σ i => x i + (σ i).val - 1)

  这样成员提取只需要 `Finset.mem_image`，完全避开 `pi` 与 `Finset.Icc`；
  并且 `σ ≡ 1` 给出 `x`（H2）、`σ ≡ 0` 给出 `x - 1`（H3）、`σ ≡ 2` 给出 `x + 1`（H4）。
* sup 的三条引理已确认存在：
  `Finset.sup_le_iff : s.sup f ≤ a ↔ ∀ b ∈ s, f b ≤ a`、
  `Finset.le_sup (hb : b ∈ s) : f b ≤ s.sup f`、
  `Finset.exists_mem_eq_sup' (s.Nonempty) f`（取值点，H3/H4 的 `sup` 下降/上升需要）。
* 需要 `hD : 0 < D`（D = 0 时 (H4) 不可能成立），并用
  `haveI : Nonempty (Fin D) := ⟨⟨0, hD⟩⟩` 打开 `Finset.univ_nonempty`。
### Round 12：d 维 Moore 完成 ✅（`Instances.lean`）

```lean
variable {D : Nat}
def dlev (x : Fin D → Nat) : Nat := Finset.univ.sup x
def dnb (x : Fin D → Nat) : Finset (Fin D → Nat) :=
  (Finset.univ : Finset (Fin D → Fin 3)).image (fun σ i => x i + (σ i).val - 1)

theorem dnb_mem   : x ∈ dnb x
theorem dnb_bound : y ∈ dnb x → dlev y + 1 ≥ dlev x ∧ dlev y ≤ dlev x + 1
theorem dnb_prev  : 0 < D → 1 ≤ dlev x → ∃ y ∈ dnb x, dlev y = dlev x - 1
theorem dnb_next  : 0 < D → ∃ y ∈ dnb x, dlev y = dlev x + 1

/-- 任意维数 D ≥ 1 的 3^D Moore 箱，原点处中列都是 2^k − 1。 -/
theorem mooreD_middle (hD : 0 < D) (t : Nat) (ht : 1 ≤ t) :
    ustate dlev (dnb (D := D)) t (fun _ => 0) = 0 ↔ ∃ k : Nat, 1 ≤ k ∧ t = 2 ^ k - 1
```

要点：
* 邻域用**偏移向量的像**（`Fin 3` 的 D 次积），成员提取只需 `Finset.mem_image`，
  完全避开 `Finset.pi` / `Finset.Icc` 这两个 API；
* `(H1)` 用 `Finset.sup_le_iff.mpr` + `Finset.le_sup`；
* `(H3)/(H4)` 需要 `sup` 的**取值点**，用 `Finset.exists_mem_eq_sup`
  （**不是** `exists_mem_eq_sup'`：后者给出的是 `sup'` 的等式，无法重写 `sup`）；
* `(H3)/(H4)` 的最后两步不要用 omega，改用精确引理：
  `Nat.sub_le_sub_right`、`Nat.add_le_add_right`，再 `rw [hi₀]` 收尾。

至此目标里的"推广到 d 维 Moore 与任意分支数树"**两项都完成**。
### Round 13：一维非负半轴的零点计数

```lean
/-- 非负半轴上的零格恰好由壳层标号：c_d = 2 的那一半。 -/
theorem row_zero_pos_eq_shell (t : Nat) (ht : 1 ≤ t) :
    (Finset.range (t + 1)).filter (fun d => row t ((d : Nat) : Int) = 0) = shell t

theorem row_zero_pos_card (t : Nat) (ht : 1 ≤ t) :
    (…同上…).card = (shell t).card
```

证明只需 `ext d` + 一次 `simp [Finset.mem_filter, Finset.mem_range, mem_shell,
row_zero_iff_shell t ht]`（`Int.natAbs_natCast` 与 `Nat.lt_succ_iff` 自动生效）。
注意**不要**先 `rw [mem_shell]`：那会把 `shell` 展开成 `List.filter` 形式，
后续 `constructor`/`rintro` 全部失效。

配合 `row_symm`（`row t (-j) = row t j`），整条窗口的计数是
`2·#shell t − [0 ∈ shell t]`，即 `2^{1+wt(r)} − [t = 2^k − 1]`（A071051 的公式）。
对称化那一步需要 Int 区间上的双射（`j ↦ -j`），尚未形式化；数值核对见脚本 272。

## 目标总览（第 13 轮结束）

| 目标项 | Lean | 数值 |
|---|---|---|
| 零集恒等式 | `shell_iff`, `shell_eq_image` | 268/271 |
| σ = 2^wt(r)(2t−1−2r) | `sigma_shell`（N = #subm 形式） | 268 |
| 零集 = 壳层并（任意几何） | `universal_zero_iff`, `row_zero_iff_shell` | 266/265 |
| 1D 计数（非负半轴） | `row_zero_pos_card` | 272 |
| 1D 计数（整条） | 待做（Int 对称化） | 272 |
| 任意分支数树 | `btree_middle` | 274 |
| d 维 Moore | `mooreD_middle` | 已有 2D 验证 |
| OEIS 核对/勘误 | 脚本 273 | A169699 9 处错 |

### Round 14：两件遗留工作全部收口 ✅（`Final.lean`，见 `docs/46`）

第 13 轮末尾列的"非负半轴已好、整条窗口待做"和"各几何 Σ c_d 显式实例化"都已完成，
并在做的过程中长出了三件新东西：

1. **抽象层**：`zero_card_eq_sum_levels` —— 任意 (H1)-(H4) 几何上
   `#零 = Σ_{d∈S(t)} #{x | lev x = d}`（用 `Finset.card_eq_sum_card_fiberwise`
   绕开 `card_biUnion` 的 `Set.PairwiseDisjoint` 坑）。
2. **一维整窗**：`row_zero_win_card` 给出 `2·#shell − [0∈shell]`，
   闭式 `2^{1+wt t} − [t = 2^i−1]`，命中 A267447 全部 71 项，
   并给出 Mathar(2016) 猜想的闭式依据。
3. **二次 Moore**：`level_card`（`c_d = 2d+1`）+ `moore_zero_card_closed`
   （`4·#subm(r t)·(t − r t) = 2^{1+wt t+⌊log₂t⌋}`），命中 A189007 的 68 项。
4. **幂次层**：`exists_pow_card_subm/shell`、`moore_zero_card_pow`、
   `row_zero_win_card_pow` —— 这些计数全是 2 的幂。

修正第 13 轮末尾的"目标总览"表：

| 目标项 | Lean | 数值 |
|---|---|---|
| 零点数 = Σ c_d（任意几何） | **`zero_card_eq_sum_levels`** | — |
| 1D 计数（整条） | **`row_zero_win_card`**, `row_zero_win_eq`, `posImg_inter_negImg` | 272/276 |
| 二次 Moore 的 Σ c_d | **`level_card`, `moore_zero_card_closed`** | 275 |
| 各计数的幂形式 | **`exists_pow_card_*`, `moore_zero_card_pow`, `row_zero_win_card_pow`** | 276 |
| OEIS 身份 | A267447（71 项）、A189007（68 项）、A071051（74 项）、A056791（87 项） | 276 |

仍未形式化：b 叉树的 `Σ b^d`、d 维 Moore 的 `(d+1)^D − d^D`、
整平面的 `4σ+ε`、以及 Lean 里没有 `popcount`（`#subm = 2^wt` 只在数值层）。

