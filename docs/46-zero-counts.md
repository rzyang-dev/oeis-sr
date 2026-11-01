# 46 零点计数：Σ c_d、整条窗口与幂次形式

第 13 轮结束时留下了两件"仓库整理"性质的工作：

1. 一维**整条窗口**的零点数（非负半轴已形式化，差一步 Int 对称化）；
2. 各几何的 **Σ_{d∈S(t)} c_d** 显式实例化。

本轮把两件都做完了，并顺带发现三件新东西：计数层的**抽象形式**（任意几何成立）、
两个计数序列在 OEIS 中的**确切身份**，以及所有计数都**是 2 的幂**。

新文件：`lean/Final.lean`（16 条定理，errors = 0，sorry = 0，公理只有
`propext, Classical.choice, Quot.sound`）。新脚本：`scripts/275`、`scripts/276`。

---

## 0 摘要

设 `S(t) = shell t`（承载零点的层集），`c_d` = 第 d 层上的点数。

| 结论 | Lean 定理 | 数值 |
|---|---|---|
| **零点数 = Σ_{d∈S(t)} c_d**（任意 (H1)-(H4) 几何） | `zero_card_eq_sum_levels` | — |
| 零集 = 壳层的**无交并** | `zero_set_eq_biUnion` | — |
| 一维整窗：`#Z = 2·#shell t − [0 ∈ shell t]` | `row_zero_win_card` | 272（t ≤ 30） |
| 一维整窗闭式：`2^(1+wt t) − [t = 2^i−1]` | 由 `row_zero_win_card` + 数值 | 276（t ≤ 1200） |
| 二次 Moore 每层 `c_d = 2d+1` | `level_card` | 275 |
| **Moore 四分之一平面：`#Z = 4·#subm(r t)·(t − r t)`** | `moore_zero_card_closed` | 275（t ≤ 29） |
| 同一式的幂形式：`2^(1+wt t+⌊log₂t⌋)` | 由上式 + `t_sub_r_eq_pow` | 276（t ≤ 1200） |
| `#subm r`、`#shell t`、两个零点数**全是 2 的幂** | `exists_pow_card_*`, `moore_zero_card_pow`, `row_zero_win_card_pow` | 276 |

---

## 1 抽象层：零点数 = Σ c_d

```lean
variable {X : Type} [DecidableEq X] [Fintype X]

theorem zero_set_eq_biUnion (lev : X → Nat) (nbhd : X → Finset X)
    (hm : UMem nbhd) (hb : UBound lev nbhd) (hp : UPrev lev nbhd) (hn : UNext lev nbhd)
    (t : Nat) (ht : 1 ≤ t) :
    (Finset.univ.filter (fun x => ustate lev nbhd t x = 0))
      = (shell t).biUnion (fun d => Finset.univ.filter (fun x => lev x = d))

theorem zero_card_eq_sum_levels … :
    (Finset.univ.filter (fun x => ustate lev nbhd t x = 0)).card
      = (shell t).sum (fun d => (Finset.univ.filter (fun x => lev x = d)).card)
```

这就是"零点数 = Σ c_d"的字面形式，也是壳层标度律的**最后一块逻辑拼图**：
几何只通过每层的点数 `c_d` 进入计数，层集 `S(t)` 本身与几何无关
（`universal_zero_iff`）。此后每个几何的工作都退化成"数一层有多少点"。

**工程要点（踩过的坑）**

* 不要用 `Finset.card_biUnion`：它的假设是 `Set.PairwiseDisjoint`，其中 `Disjoint`
  在**格**意义下求值，Lean 会把 `Finset X` 的码域显示成 `Set X`，
  `rw [Finset.disjoint_left]` 匹配不上（`Function.onFun Disjoint …`）。
* 改用**纤维计数** `Finset.card_eq_sum_card_fiberwise`
  （`Algebra/BigOperators/Group/Finset/Basic.lean:993`）：

  ```
  (H : (s : Set ι).MapsTo f t) : #s = ∑ b ∈ t, #{a ∈ s | f a = b}
  ```

  取 `s = {x | ustate … = 0}`、`f = lev`、`t = shell t`，假设就是
  `universal_zero_iff`；再把每个纤维 `#{x ∈ s | lev x = d}` 换成整层
  `#{x | lev x = d}`（用 `universal_zero_iff` 反方向），一行 `sum_congr` 收尾。

---

## 2 一维整条窗口

零集在 `j ↦ −j` 下不变（`row_symm`，或直接用 `j.natAbs`），
所以整条窗口 `[−t, t]` 是"非负半轴 + 镜像"，唯一在镜像下重合的层是 `d = 0`。

```lean
def posImg (s : Finset Nat) : Finset Int := s.image (fun d : Nat => (d : Int))
def negImg (s : Finset Nat) : Finset Int := s.image (fun d : Nat => -((d : Int)))
def win (t : Nat) : Finset Int := posImg (Finset.range (t + 1)) ∪ negImg (Finset.range (t + 1))

theorem mem_win : j ∈ win t ↔ ∃ d, d ≤ t ∧ (j = ↑d ∨ j = -↑d)
theorem row_zero_win_eq  : (win t).filter (fun j => row t j = 0) = posImg (shell t) ∪ negImg (shell t)
theorem posImg_inter_negImg (s) : posImg s ∩ negImg s = if 0 ∈ s then {(0 : Int)} else ∅
theorem row_zero_win_card (t) (ht : 1 ≤ t) :
    ((win t).filter (fun j => row t j = 0)).card
      = 2 * (shell t).card - (if 0 ∈ shell t then 1 else 0)
```

`posImg_inter_negImg` 是唯一需要一点算术的地方：`j ∈ posImg s ∩ negImg s`
给出 `(↑d : ℤ) = -↑e`（d, e ∈ s），两边取 `Int.natAbs` 后剩 `d = e = 0`
（`omega` 在给了 `(0:ℤ) ≤ ↑e` 之后可以收尾）。

**闭式**。用 `card_shell` 与 `#subm r = 2^{wt r}`（第 5 节）：

```
#Z(t) = 2·#shell t − [0 ∈ shell t]
      = 4·2^{wt(r t)} − [t = 2^i − 1]
      = 2^{1 + wt(t)} − [t = 2^i − 1]          (t ≥ 1，因为 wt(t) = 1 + wt(r t))
```

数值：`scripts/272`（t ≤ 30 直接模拟）、`scripts/276`（t ≤ 1200）。

---

## 3 二次 Moore 四分之一平面

水平的层是正方形的 L 形四分之一壳（`qlev p = max p.1 p.2`）：

```lean
def mbox (t : Nat) : Finset (Nat × Nat) := (Finset.range (t+1)) ×ˢ (Finset.range (t+1))
def armA (d) := (Finset.range (d+1)).image (fun a => (a, d))
def armB (d) := (Finset.range (d+1)).image (fun b => (d, b))

theorem level_eq : (mbox t).filter (fun p => qlev p = d) = armA d ∪ armB d      -- d ≤ t
theorem arm_inter : armA d ∩ armB d = {(d, d)}
theorem level_card : ((mbox t).filter (fun p => qlev p = d)).card = 2*d + 1      -- d ≤ t
```

两条臂各有 `d+1` 个点、只在角上重合，所以 `c_d = 2(d+1) − 1 = 2d+1`。
再套第 1 节的抽象式（这里空间无限，直接对盒子用一次纤维计数）：

```lean
theorem moore_zero_card_sum : #(盒子里的零点) = (shell t).sum (fun d => 2*d + 1)
theorem moore_zero_card_closed :
    #(盒子里的零点) = 4 * (subm (r t)).card * (t - r t)
```

推导：`Σ_{d∈S}(2d+1) = 2σ(t) + #S = 2N(2t−1−2r) + 2N = 4N(t − r)`，`N = #subm(r t)`。

**幂形式**：`t − r t = 2^{⌊log₂ t⌋}`（`t_sub_r_eq_pow`），所以

```
#Z_Moore(t) = 2^{2 + wt(r t) + ⌊log₂ t⌋} = 2^{1 + wt(t) + ⌊log₂ t⌋}
```

即 Moore 四分之一平面的零点数**恒为 2 的幂**。数值：`scripts/275`（t ≤ 29，盒 90×90，
避免截断污染：盒子每步吃掉一层，读取范围要留足余量）。

⚠️ 这是个容易踩的坑：第一次用 `t ≤ 40` 的盒子读 `t ≤ 40`，从 t = 21 起全错——
不是公式错，而是**截断污染**（边界值每步向内传播一层）。

---

## 4 全是 2 的幂

```lean
theorem t_sub_r_eq_pow : t - r t = 2 ^ Nat.log2 t                       -- t ≥ 1
theorem exists_pow_card_subm (r) : ∃ k, (subm r).card = 2 ^ k
theorem exists_pow_card_shell (t) (ht) : ∃ k, (shell t).card = 2 ^ k
theorem moore_zero_card_pow (t) (ht) : ∃ k, Moore 零点数 = 2 ^ k
theorem row_zero_win_card_pow (t) (ht) :
    ∃ k, 一维零点数 = 2 ^ k ∨ 一维零点数 + 1 = 2 ^ k
```

`exists_pow_card_subm` 就是对 `subm` 的强归纳：偶数支 `#subm(2u) = #subm u`、
奇数支 `#subm(2u+1) = 2·#subm u`（`card_subm_two_mul` 等，第 1 轮已证）。

**工程要点**：`omega` 处理不了含 `2 ^ Nat.log2 t` 的 Nat 减法
（它把幂项当作 Int 变量，丢掉非负性）。`t_sub_r_eq_pow` 最终是用

```lean
rw [r_eq_t_sub_pow t ht, Nat.sub_sub_self hle]
```

一行收尾的（`Nat.sub_sub_self` 自带 `t − t` 归约，连 `rfl` 都不用加）。

---

## 5 OEIS 交叉识别

两个计数序列都能在 OEIS 里找到**确切身份**。

### 5.1 A267447（规则 129 的白格数）

* 条目定义：`Number of OFF (white) cells in the n-th iteration of the "Rule 129`
  `elementary cellular automaton starting with a single ON (black) cell.`
  ——**字面就是**我们的 `#Z(t)`。
* 我们的闭式 `2^{1+wt(t)} − [t = 2^i−1]` 命中它的 **71/71** 项（t = 0..70）。
* 条目里唯一的公式是一条**猜想**（R. J. Mathar, 2016-01-17）：
  `a(n) = A071051(n), n > 0`。
* 而 A071051 的条目自带 Sloane（2014-08-09）的公式
  `a(n) = 2^(1+wt(n))`，当 `n = 2^i−1` 时减 1 —— 与我们的闭式**逐字相同**。
* 所以：**Mathar 的猜想成立**，两边的闭式相同；我们这边是 Lean 定理
  （`row_zero_win_card`）加数值核对（`scripts/276`）。

  严格地说，把"规则 129 的白格数 = 我们的 `#Z`"接上" A071051 =
  `2^(1+wt) − [n=2^i−1]`"，缺的一环是 A071051 自身定义的化简
  （Sloane 给的是公式而非证明）。这一环我们没有形式化，只核对了它全部 74 项。

### 5.2 A189007（二维 CA 的黑格数）

* 条目定义的是**另一个** CA（"exactly one East/West neighbor was ON or exactly
  one North/South neighbor was ON"），不是我们的"九邻相等"。
* 但它的计数序列 `1, 4, 8, 16, 16, 32, 32, 64, 32, …` 与我们的
  `#Z_Moore(t) = 2^{1+wt(t)+⌊log₂ t⌋}` 在 `n = t+1`、`n ≥ 2` 上**逐项相等**
  （68/68 项；`a(1) = 1` 是初始那个黑格，不是零计数）。
* 条目里 M. De Vlieger（2022-11-02）的猜想是
  `a(n) = 2^A056791(n−1), n > 1`；而 A056791 = `wt(n) + bitlength(n)`
  = `1 + wt(n) + ⌊log₂ n⌋`（n ≥ 1），正是我们的指数（核对全部 87 项）。
* 所以两个指数完全一致；这也是"两个不同 CA 的计数恰好相同"的一个实例，
  但我们**没有**证明这两个 CA 的计数恒等，只核对了 68 项。

### 5.3 结论口径

| 说法 | 状态 |
|---|---|
| 规则 129 的白格数 = `2^{1+wt t} − [t=2^i−1]` | **Lean 定理**（模 A267447 定义即规则 129） |
| Mathar 猜想 A267447 = A071051 | 由两边同一个闭式给出；A071051 一侧只到数值核对 |
| Moore 四分之一平面零点数 = `2^{1+wt t+⌊log₂ t⌋}` | **Lean 定理**（`moore_zero_card_closed` + `t_sub_r_eq_pow`） |
| 该式与 A189007 相同 | 数值核对 68 项，**未证明** |

---

## 6 验证清单

| 对象 | 手段 | 范围 | 结果 |
|---|---|---|---|
| `level_card = 2d+1` | 直接模拟（盒 90×90） | t ≤ 29 | 0 错 |
| `moore_zero_card_closed` | 同上 | t ≤ 29 | 0 错 |
| `#subm r = 2^{popcount}` | 暴力枚举子掩码 | t ≤ 1200 | 0 错 |
| `#shell t = 2^{wt t}` | 同上 | t ≤ 1200 | 0 错 |
| 一维整窗闭式 | 直接模拟规则 129 | t ≤ 30 | 0 错 |
| 一维整窗闭式 | 公式 vs 公式 | t ≤ 1200 | 0 错 |
| A267447 | 逐项比对 | 71 项 | 0 错 |
| A071051 | 逐项比对 | 74 项 | 0 错 |
| A189007 | 逐项比对（n ≥ 2） | 68 项 | 0 错 |
| A056791 | 逐项比对（n ≥ 1） | 87 项 | 0 错 |

`Final.lean` 的 16 条定理逐条 `#print axioms`，全部只有
`propext, Classical.choice, Quot.sound`，无 `sorryAx`。

---

## 7 遗留

1. **b 叉树的 Σ b^d**：需要 `List Bool` 的有限盒（`Finset` of lists
   在 Mathlib 里没有现成构造；可考虑用 `Fin d → Bool` + `List.ofFn` 的像）。
   `btree_middle`（任意分支数 b）已在第 12 轮完成，缺的只是这一层的求和。
2. **d 维 Moore 的 `c_d = (d+1)^D − d^D`**：2D 的 `2d+1` 已做；
   一般 D 需要数 `Fin D → Fin (d+1)` 的基数，可用
   `Fintype.card_fun` + `Fintype.card_fin` 的双射。
3. **整个平面**（不是四分之一）的 `4σ + ε` 形式：需要把层计数从
   `2d+1` 换成 `4d`（d ≥ 1）加原点，需要 ℤ² 上的四象限计数。
4. **Lean 里的 `popcount`**：Mathlib 没有 `Nat.popcount`，
   所以 `#subm r = 2^{popcount r}` 只在数值层（1200 项）。
   形式化的替代品是 `card_subm_two_mul` / `card_subm_two_mul_add_one`
   这两条递推 + `exists_pow_card_subm`（"是 2 的幂"）。

以上四条都不影响已经建立的数学结论：壳层恒等式、几何无关性、
以及"零点数 = Σ c_d"本身。
