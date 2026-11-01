# 44 几何无关性：三个机器验证的实例

## 一句话

"全体邻居相等" 这条规则在**中心**看到的东西，只取决于**层结构**，与几何完全无关。
现在有三种差别极大的几何被 Lean 验证：一维径向、二维 3×3 箱、**无限二叉树**，
中心处的取值在每一时刻都相同。

## 三个实例

| 实例 | 空间 X | 层函数 lev | 邻域 nbhd | 邻域大小 |
|---|---|---|---|---|
| Radial | `Nat` | `d` | `{d-1, d, d+1}`（0 处截断） | 2–3 |
| MooreNat | `Nat × Nat` | `max a b` | 3×3 箱（轴处截断） | 4–9 |
| Tree | `List Bool` | `length` | `{自身, 父, 两个子}` | 3–4 |

三个都满足抽象定理的四条假设 (H1)–(H4)：

* (H1) 邻域只落在 d−1, d, d+1 三层；
* (H2) 自身在邻域里；
* (H3) 层 d ≥ 1 的点有层 d−1 的邻居；
* (H4) 每个点都有层 d+1 的邻居。

## Lean 中的结果（Universal.lean，无 sorry）

```lean
theorem radial_middle (t : Nat) (ht : 1 ≤ t) :
    ustate rlev rnb t 0 = 0 ↔ ∃ k : Nat, 1 ≤ k ∧ t = 2 ^ k - 1

theorem moore_middle (t : Nat) (ht : 1 ≤ t) :
    ustate qlev qnb t (0, 0) = 0 ↔ ∃ k : Nat, 1 ≤ k ∧ t = 2 ^ k - 1

theorem tree_middle (t : Nat) (ht : 1 ≤ t) :
    ustate tlev tnb t [] = 0 ↔ ∃ k : Nat, 1 ≤ k ∧ t = 2 ^ k - 1

/-- 三者的中心值处处相同。 -/
theorem centres_agree (t : Nat) (ht : 1 ≤ t) :
    ustate rlev rnb t 0 = ustate qlev qnb t (0, 0) ∧
    ustate rlev rnb t 0 = ustate tlev tnb t [] := by ...
```

公理：`[propext, Classical.choice, Quot.sound]`，无 `sorry`。

## 为什么树这一条是"不寻常"的

在树上：

* **层集指数增长**（第 d 层有 2^d 个点），而一维径向的第 d 层只有 1 个点；
* **没有平移不变性**，没有格结构，没有几何；
* 根处的邻域只有 **3** 个格子（自身、两个子），不是 9，也不是 3；
* 每个内部点有 **两个** 层 d+1 的邻居，而径向上只有一个。

按任何"局部计数"直觉，这三者的演化都应该不同。但它们**完全相同**。

这说明：Rule 129 的中心列 2^k−1 不是"格上的现象"，而是"层结构上的现象"。
文献里关于 Rule 129 / 一维 CA 的闭式证明全都依赖平移不变性，因此都无法解释
二维 Moore 和二叉树；抽象定理把这一层剥掉了。

## 数值交叉验证（scripts/265_tree.py）

深度 16 的满二叉树（131 071 个顶点），时间 12 步：

* 比较 130 个 (t, d) 对：**0 处不符**；
* 每一时刻每一层内部完全一致（**0** 个非一致层）——这正好对应定理里最强的形态
  `ustate lev nbhd t x = H t (lev x)`（值是层的函数）；
* 根为 0 的时刻 = {1, 3, 7}，与 2^k−1 完全一致。

（此前二维 Moore 的数值验证规模是 121 484 个格子，von Neumann 85 319 个，
一维 r=1..4 共 4×1599 个，全部 0 处不符。）

## 证明是怎么落到树上的

抽象证明只用 (H1)–(H4)，从未用到"格"：

1. **层常值性**：`ustate_dep` 证明同层两点的值恒相等——归纳步只把"所有邻居与
   自身相等"化归成三层数值的三元合取式；
2. **单步匹配**：`step_preserved` 用 `H_step` 把该合取式识别为 `H (t+1) d = 1`；
3. **中列**：`H t 0 = 0 ↔ ∃ k ≥ 1, t = 2^k − 1`（R129.lean 的 `row_middle`）。

树的三条实例证明各只有几行：

* `tnb_bound`：邻域是 4 个候选的像，逐个 `interval_cases` 后 `omega`；
* `tnb_prev`：父 = `dropLast`，`List.length_dropLast`；
* `tnb_next`：子 = `x ++ [true]`。

## 工程记录（踩过的坑）

1. **`Nat.max_cases` 不存在**；且 `Nat.max_eq_left/right` 的签名方向容易搞错。
   最终用自定义 `nmax a b := if a ≤ b then b else a` 绕开整个 `max` API：
   所有算术都退化成 `by_cases` + `simp` + `omega`，一次通过。
2. **`Finset` 字面量的成员提取在 `simp only` 下不触发**（`Finset.mem_insert`
   形参不匹配），于是把邻域定义成 `(range n).image f` 或 `Icc ×ˢ Icc` 的形式，
   用 `Finset.mem_image` / `Finset.mem_product` 这种"直接应用"的引理，
   不用 simp 重写假设。
3. 复数条 `by_cases` 之后再 `simp` 往往一步清空目标，`<;> omega` 会空转——
   无害，但要注意 `<;>` 的属性：它只作用于剩余目标。

## 下一步

* **ℤ² 全 Moore 形式化**：唯一缺的是 `Int.natAbs` 的加减 1 估计
  （`Int.natAbs_add_le` / `Int.natAbs_sub_le` 已确认存在），以及 (H3) 在
  "两坐标同时到达最大层"时要把两个坐标一起内缩。数值已验 121 484 格。
* **b 叉树**：把 `List Bool` 换成 `List (Fin b)`，同一套证明应逐字通过，
  于是"任意分支数的树中列相同"。
* **哪些量是几何无关的？** 定理说整条"层剖面"不变；但 1 的总个数显然依赖几何。
  值得刻画：几何无关的线性泛函恰好是层剖面的那些。
