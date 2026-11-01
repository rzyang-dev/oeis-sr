# 49 计数总表：每种几何一行闭式

第 15 轮起我们反复用"零点数 = Σ_{d∈S(t)} c_d"算各种几何。这一轮把它固化成
**一张可机器核对的表**：每行的闭式都由 `scripts/282_counting_table.py` 与
"按定义逐个壳层求和"逐项对比（t = 1..60）。

```
| geometry | c_d | closed form | checked | Lean | OEIS |
|---|---|---|---|---|---|
| 1-D line | [1,2,2,2,2,2] | 2^(1+wt t) - [t=2^i-1] | t <= 60 OK | Final: row_zero_win_card | A267447 |
| 1-D ray (orthant) | [1,1,1,1,1,1] | #shell t = 2^wt t | t <= 60 OK | Final: row_zero_pos_card | -- |
| Z^2 von Neumann (5-nbhd) | [1,4,8,12,16,20] | 4 sigma + eps | t <= 60 OK | Census: shell_sum_linear_form | A169699 (formula wrong) |
| Z^2 Moore (9-nbhd) | [1,8,16,24,32,40] | 8 sigma + eps | t <= 60 OK | Census: shell_sum_linear_form | not in OEIS |
| triangular lattice | [1,6,12,18,24,30] | 6 sigma + eps | t <= 60 OK | Census: shell_sum_linear_form | not in OEIS |
| Z^2 orthant, von Neumann | [1,2,3,4,5,6] | sigma + #shell = #subm(2t+1-2r) | t <= 60 OK | (analogue) | -- |
| Z^2 orthant, Moore | [1,3,5,7,9,11] | 2^(1+wt t+floor(log2 t)) | t <= 60 OK | Final: moore_zero_card_closed | A189007 (shifted) |
| Z^3 von Neumann | [1,6,18,38,66,102] | 4 M2 + 2(#shell - eps) + eps | t <= 60 OK | (M2 verified numerically) | not in OEIS |
| Z^3 Moore | [1,26,98,218,386,602] | 24 M2 + 2(#shell - eps) + eps | t <= 60 OK | (M2 verified numerically) | not in OEIS |
| binary tree | [1,2,4,8,16,32] | (b+1) b^(t-1-2r) prod(1+b^(2^(i+1))) | t <= 60 OK | Tree: shell_sum_pow_factored | not in OEIS |
| ternary tree | [1,3,9,27,81,243] | same, b = 3 | t <= 60 OK | Tree: shell_sum_pow_factored | not in OEIS |
```

其中：
* `N = #subm(r t) = 2^wt(t)`，`sigma = N(2t-1-2r)`，`#shell = 2N`，`eps = [0 in shell]`；
* `K = t - r t`（= 不超过 t 的最大 2 的幂），`Q = sum_{i in bits r} 4^i`；
* `M2 = N(2K(K-1) + 2Q + 1)` = 壳层上 d² 的和。

## 每一行的 Lean 支撑

| 行 | 用到的定理 |
|---|---|
| 1-D line | `row_zero_win_card`（`2 #shell − eps`）+ `card_shell` + `zero_mem_shell` |
| Z^2 5/9 邻、三角格 | `shell_sum_linear` + `shell_sum_linear_form`（k = 4, 8, 6） |
| Z^2 四分之一平面 Moore | `moore_zero_card_closed` |
| 树 | `shell_sum_pow_factored`（`sum_subm_pow_eq_prod` 的推论） |
| Z^3 两族 | `shell_sum_linear` 的二次类比 + `M2`（见下） |

`c_d = 4d²+2` 与 `24d²+2` 的"二次档"还没有专门的 Lean 定理，
但 `c_d = 0`/常数/线性/指数四档都有；二次档的缺口正是 `M2` 的最终装配。

## 本轮新增：三条矩关系（`lean/ShellSq.lean`，3 条定理）

壳体是"成对"的：`S(t) = ⊎_m {u, u−1}`，`u = t − 2m`，`m ⊆ r t`。记

```
B = Σ_m (t−2m)          A = Σ_m (t−2m)²
S1 = Σ_m m              S2 = Σ_m m²
N = #subm(r t)          Zsq = Σ_{d∈S} d²
```

则三条**无减法**的恒等式成立（全部 Lean 已证）：

```lean
theorem subm_sum_shift      : B + 2*S1       = N * t
theorem subm_sum_shift_sq   : A + 4*(t*S1)   = N*(t*t) + 4*S2
theorem shell_sum_sq_split  : Zsq + 2*B      = 2*A + N
```

配合 `two_mul_sum_subm`（`2 S1 = N r`）与 `four_mul_card_sq`（`4 S2 = N(r²+Q)`），
这四条足以把 `Zsq` 完全确定下来；只剩最后一步"把减法消掉、组装成闭式"。

## 工程坑（这一轮）

1. **Nat 的截断减法会污染 `ring`**。想用 `rw [show t = (t - 2*m) + 2*m]; ring`
   消去减号，`ring` 会把 `m*2 + (t - m*2) - m*2` 当成原子，留下无法闭合的平方项。
   正确做法是先 `set u := t - 2*m`（让减法项变成原子变量），再 `rw [ht']` 把
   **t** 换成 `u + 2*m`，这样式子里完全没有减号，`ring` 一次过。
2. **`← Finset.sum_add_distrib` 与 `Finset.sum_add_distrib` 方向不同，
   括号结构也不同**。`Σf + Σg → Σ(f+g)` 用反向；把 `Σ(f+g)` 拆开用正向。
   方向搞错时目标会变成括号不同的形式（`(a+b)+c` vs `a+(b+c)`），`rw` 找不到匹配。
3. **`sum_const` 之后是 `card • x` 而不是 `card * x`**，`Nat.smul_eq_mul` 不存在，
   直接 `simp` 即可。
4. 以上三条乘以"每个几何一次"，就是为什么这一轮的表比定理多。

## 验证

```
Shells 24 · Instances 8 · Final 16 · Census 6 · Tree 20 · Parity 4 · Moments 3 · ShellSq 3
errors = 0, sorryAx = 0, 公理只有 propext / Classical.choice / Quot.sound
```

表本身：`scripts/282_counting_table.py`，11 种几何 × t ≤ 60，0 处不符。

---

## 本轮补完：M2 装配 + 二次档定理（第 19 轮）

上表里 ℤ³ 两行之前只有"数值验证"，现在已经是 Lean 定理了。

### 1. 壳体二阶矩的闭式（`ShellSq.lean`）

```lean
theorem shell_sum_sq (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => d * d)
      = (subm (r t)).card * (2 * (t - r t) * (t - r t - 1) + 2 * Q (r t) + 1)
```

证明分两段，中间用了一个**原子化 + ℤ 里 nlinarith** 的技巧，值得记下来：

**第一步（纯 Nat）**：把四条关系里的每个"大的和"都 `set` 成不透明变量

```lean
set N := (subm (r t)).card
set S1 := (subm (r t)).sum (fun m => m)
set S2 := (subm (r t)).sum (fun m => m * m)
set B  := (subm (r t)).sum (fun m => t - 2 * m)
set A  := (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m))
set Zsq := (shell t).sum (fun d => d * d)
```

于是五条关系变成**关于原子**的等式：

```
B + 2·S1 = N·t
A + 4·(t·S1) = N·t² + 4·S2
Zsq + 2·B = 2·A + N
2·S1 = N·r t
4·S2 = N·(r t² + Q(r t))
```

**第二步（转到 ℤ）**：原子化之后 `exact_mod_cast` 就能干净地把它们搬到 ℤ
（之前失败的根因是 `Σ (t − 2m)` 直接 `cast` 会变成 `Int.subNatNat`，
而原子化后每个变量都是纯 Nat 项）。

**第三步**：`nlinarith` 一次收掉 —— 目标是从五条关系推出

```
Zsq = N · (2·(T−R)·(T−R−1) + 2Q + 1)
```

**第四步**：`push_cast [h1, h2]` + `ring` 把 ℤ 里的式子搬回 Nat
（需要 `1 ≤ t − r t` 与 `r t ≤ t` 才能把 `t − r t − 1` 的 cast 拆开），
最后 `Nat.cast_injective` 收尾。

**核心经验**：遇到"Nat 里减法不可交换"的代数题，不要在 Nat 里硬推——
把大表达式 `set` 成原子，然后去 ℤ（或 ℚ）里用 `nlinarith`/`ring`，
最后 `push_cast` + `Nat.cast_injective` 搬回来。

### 2. 二次档定理（`Dim3.lean`，3 条）

```lean
/-- 层大小 1, 4k·d²+2 (d ≥ 1) 的零点数。 -/
theorem shell_sum_quadratic (k : Nat) (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => if d = 0 then 1 else 4 * k * (d * d) + 2)
      = 4 * k * (shell t).sum (fun d => d * d) + 2 * (shell t).card
        - (if 0 ∈ shell t then 1 else 0)

theorem zero_count_Z3_vonNeumann (t) (ht) :
    (shell t).sum (fun d => if d = 0 then 1 else 4 * (d * d) + 2)
      = 4 * (N * (2K(K−1) + 2Q + 1)) + 2·#shell − eps

theorem zero_count_Z3_moore (t) (ht) :
    (shell t).sum (fun d => if d = 0 then 1 else 24 * (d * d) + 2)
      = 24 * (N * (2K(K−1) + 2Q + 1)) + 2·#shell − eps
```

（k = 1 是 ℤ³ 冯诺依曼的 `4d²+2`，k = 6 是 ℤ³ Moore 的 `24d²+2`。）

于是表中 ℤ³ 两行的"Lean"列可以写成 `Dim3: zero_count_Z3_vonNeumann` /
`zero_count_Z3_moore` —— **四档增长（常数/线性/二次/指数）全部形式化**。

### 3. `Σ_{d∈S} d^j` 的现状

| j | 闭式 | Lean |
|---|---|---|
| 0 | `#shell = 2N` | `card_shell` |
| 1 | `N(2t−1−2r)` | `sigma_shell` |
| 2 | `N(2K(K−1) + 2Q + 1)` | **`shell_sum_sq`（本轮）** |
| 3 | `N(2k³+3k²+3k+1+3Q(2k+1))` | **`shell_sum_cube`（第 22 轮补上）** |
| ≥ 4 | 需要子掩码的四阶以上矩 | 未做 |

---

## 第 20 轮：三阶矩与 ℤ⁴

### 1. 已形式化（`lean/Cubic.lean`，3 条定理）

```lean
/-- 子掩码三阶矩。 -/
theorem eight_mul_card_cube (r : Nat) :
    8 * (subm r).sum (fun m => m * m * m) = (subm r).card * (r*r*r + 3 * Q r * r)

/-- 壳体的三阶拆分关系。 -/
theorem subm_sum_shift_cube (t) (ht) :
    Σ_m (t−2m)³ + 6·(t²·Σ_m m) + 8·Σ_m m³ = N·t³ + 12·(t·Σ_m m²)

theorem shell_sum_cube_split (t) (ht) :
    Σ_{d∈S} d³ + 3·Σ_m (t−2m)² + N = 2·Σ_m (t−2m)³ + 3·Σ_m (t−2m)
```

第一条的证明和 `four_mul_card_sq` 同构（对 r 强归纳 + 二进制两支），
新增的只有奇支里 `(2m)³ + (2m+1)³ = 16m³ + 12m² + 6m + 1`。

**这一轮又踩了同一个坑**：`hshape` 的重排里，左边写 `Σ m`、右边写 `Σ id`，
`ring` 把两者当成**不同的原子**，于是恒等式证不出来。教训：
在 `ring` 之前确保同一个和式在两边的语法形式完全一致。

### 2. 数值验证但未形式化（`scripts/283`，r ≤ 300 / t ≤ 300）

```
Σ_{m⊆r} m³        = N(r³ + 3Qr)/8
Σ_{d∈S(t)} d³     = N(2k³ + 3k² + 3k + 1 + 3Q(2k+1)),   k = t − r t − 1
```

推导用的是"每位独立取 0/1"的期望模型：
`Σ m³ = N·[P1/2 + (3/4)(Qr − P1) + (3/4)·e3]`，其中 `P1 = Σ 8^i` 会**精确抵消**，
剩下只有 `r` 和 `Q` —— 三阶矩依旧只用这两个不变量。

壳体闭式的最终组装（原子化 + ℤ 里 `nlinarith`）这一次**超时**了
（`maxHeartbeats` 200000 用尽，因为式子里有 7 个关系、次数到 3、变量到 10 个）。
下一步可以：调大 `maxHeartbeats`、或先化简成两个中间量、或改用 `linear_combination`。

### 3. ℤ⁴ 两族（数值验证）

| 几何 | `c_d` (d ≥ 1) | 零点数 | 验证 |
|---|---|---|---|
| ℤ⁴ 冯诺依曼 | `8d(d²+2)/3` | `3·Z = 8(M3 + 2σ) + 3ε` | t ≤ 200 ✓ |
| ℤ⁴ Moore | `64d³ + 16d` | `Z = 64 M3 + 16σ + ε` | t ≤ 200 ✓ |

序列本身与第 15 轮普查（`scripts/277`）逐项吻合：
ℤ⁴ vN 是 `9, 40, 129, 280, 672, 1008, 2241, 2360, …`，
ℤ⁴ Moore 是 `81, 624, 2401, 5936, 14560, 22624, 50625, …`。

### 4. `Σ_{d∈S} d^j` 总表（更新）

| j | 闭式 | Lean | 验证 |
|---|---|---|---|
| 0 | `2N` | `card_shell` | ✓ |
| 1 | `N(2t−1−2r)` | `sigma_shell` | ✓ |
| 2 | `N(2K(K−1) + 2Q + 1)` | `shell_sum_sq` | ✓ |
| 3 | `N(2k³+3k²+3k+1+3Q(2k+1))` | **`shell_sum_cube`（第 22 轮补上）** | t ≤ 300 ✓ |
| ≥4 | 需要四阶以上矩 | 未做 | — |

子掩码矩的模式很清楚：`Σ m^j = N·P_j(r,Q)/2^j`，`P_1 = r, P_2 = r²+Q, P_3 = r³+3Qr`。

---

## 第 21 轮：ℤ⁴ 进表 + OEIS 收尾

计数表又加了两行（`scripts/282`，13 行 × t ≤ 60 全部通过）：

| 几何 | c_d (d ≥ 1) | 闭式 | 检查 |
|---|---|---|---|
| ℤ⁴ Moore | `64d³ + 16d` | `64·M3 + 16σ + ε` | t ≤ 60 ✓ |
| ℤ⁴ 冯诺依曼 | `8d(d²+2)/3` | `3Z = 8(M3 + 2σ) + 3ε` | t ≤ 60 ✓ |

其中 `M3 = N(2k³+3k²+3k+1+3Q(2k+1))`，`k = t−r t−1`。

OEIS 检索（本轮补做）：
* ℤ⁴ Moore 零点数 `81, 624, 2401, 5936, 14560, 22624, 50625, …` → **不在 OEIS**
* ℤ⁴ 冯诺依曼零点数 `9, 40, 129, 280, 672, 1008, 2241, …` → **不在 OEIS**

至此 OEIS 的图景完全确定：

| 几何 | OEIS |
|---|---|
| 一维直线 | A267447（其唯一公式是一条 2016 年的猜想，我们的闭式解释了它） |
| ℤ² 5 邻 | A169699（**公式错 9/52 项**，正确条件是 `n = 2^i−1`） |
| ℤ² 四分之一平面 Moore | A189007（移位，68 项） |
| ℤ² 9 邻 / 三角格 / ℤ³ 两族 / ℤ⁴ 两族 / 树 | **全部不在 OEIS** |

也就是说：**5 邻这一条例外地有人算过（还写错了），其余整片空白**。

### ℤ³ 三阶矩的组装为何仍未完成（**第 22 轮已解决，见文末**）

`shell_sum_cube` 的组装（把 7 条关系化成闭式）在 `nlinarith` 里反复超时：
* 一次性 7 条关系 + 10 个原子 + 3 次 → 200k heartbeats 不够；
* 提到 1M heartbeats 仍超时；
* 拆成三步（先证 `B = N·K`、`A2 = N(K²+Q)`、`A3 = N(K³+3QK)`，再合成）——
  前两步过了，最后一步仍超时。

这不是数学问题，是 tactic 的性能问题。可行的替代路线（留给下一轮或后续）：
1. 用 `linear_combination` 显式给系数（需要手算组合系数）；
2. 在 `ℚ` 里先做（`nlinarith` 在 ℚ 上更稳），再搬回；
3. 直接把 `Zc = 2A3 + 3B − 3A2 − N` 用 `Nat` 的 `omega`+`ring` 手推（把每个乘积当原子）。

---

## 第 22 轮：j = 3 闭环，ℤ⁴ 全部形式化

第 21 轮留下的唯一缺口是"三阶矩的组装"，当时的诊断是"tactic 性能问题"。这一轮证明了
这个诊断**是对的，但结论错了**：不是要等更好的 `nlinarith`，而是**根本不该用 `nlinarith`**。

### 1. 诊断：`nlinarith` 为什么必然炸

`nlinarith` 的工作方式是"把每个假设多项式化，然后对所有单项式做线性组合搜索"。
7 条假设 + 10 个原子 + 次数 3，单项式数量已经是数百个，而且它还要成对相乘生成二次单项式。
所以 200k / 1M heartbeats 都不够 —— 这不是"再等等就过了"，是指数级的搜索空间。

### 2. 修法：把代数从和式里搬出来

关键观察：**七个和式 `N S1 S2 S3 B A A3 ZC` 之间的关系，与"它们是和式"毫无关系。**
它们只是 12 个整数变量之间的多项式恒等式。于是拆成三步：

**第一步（纯 Nat，`set` 原子化）**

```lean
set N := (subm (r t)).card
set S1 := (subm (r t)).sum (fun m => m)
set S2 := (subm (r t)).sum (fun m => m * m)
set S3 := (subm (r t)).sum (fun m => m * m * m)
set B  := (subm (r t)).sum (fun m => t - 2 * m)
set A  := (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m))
set A3 := (subm (r t)).sum (fun m => (t - 2 * m) * (t - 2 * m) * (t - 2 * m))
set Zc := (shell t).sum (fun d => d * d * d)
```

七条关系（全部由已有定理直接 `exact`）：

```
(1) B + 2·S1                = N·t                     subm_sum_shift
(2) A + 4·(t·S1)            = N·t² + 4·S2             subm_sum_shift_sq
(3) A3 + 6·(t²·S1) + 8·S3   = N·t³ + 12·(t·S2)        subm_sum_shift_cube
(4) Zc + 3·A + N            = 2·A3 + 3·B              shell_sum_cube_split
(5) 2·S1                    = N·r t                   two_mul_sum_subm
(6) 4·S2                    = N·(r t² + Q(r t))       four_mul_card_sq
(7) 8·S3                    = N·(r t³ + 3Q r t)       eight_mul_card_cube
```

**第二步（纯代数，`cube_key`）**—— 这是整个问题的核心，而且它是一个
**不含 `Finset`、不含 Nat 减法、不含大表达式**的独立引理：

```lean
theorem cube_key (N S1 S2 S3 B A A3 ZC T R Q : Int)
    (h1 : B + 2 * S1 = N * T)
    (h2 : A + 4 * (T * S1) = N * (T * T) + 4 * S2)
    (h3 : A3 + 6 * ((T * T) * S1) + 8 * S3 = N * ((T * T) * T) + 12 * (T * S2))
    (h4 : ZC + 3 * A + N = 2 * A3 + 3 * B)
    (h5 : 2 * S1 = N * R)
    (h6 : 4 * S2 = N * (R * R + Q))
    (h7 : 8 * S3 = N * ((R * R) * R + 3 * Q * R)) :
    ZC = N * (2 * (T - R - 1) ^ 3 + 3 * (T - R - 1) ^ 2 + 3 * (T - R - 1) + 1
      + 3 * Q * (2 * (T - R - 1) + 1))
```

证明只有四行，**全部是 `linear_combination` + 显式系数**（系数是手推的，不是搜索的）：

```lean
have eB  : B  = N * (T - R)                         := by linear_combination h1 - h5
have eA  : A  = N * ((T - R) * (T - R) + Q)         := by linear_combination h2 - (2*T)*h5 + h6
have eA3 : A3 = N * ((T-R)*(T-R)*(T-R) + 3*Q*(T-R)) := by linear_combination h3 - (3*(T*T))*h5 + (3*T)*h6 - h7
linear_combination h4 + 2 * eA3 + 3 * eB - 3 * eA
```

三个中间式化简后是 `A3 = N(K³ + 3QK)`、`A = N(K²+Q)`、`B = NK`，其中 `K = T − R`。于是

```
Zc = 2N(K³+3QK) + 3NK − 3N(K²+Q) − N
   = N(2K³ − 3K² + 3K − 1 + 3Q(2K−1))
   = N(2k³ + 3k² + 3k + 1 + 3Q(2k+1)),        k = K − 1
```

最后的换元恒等式 `2K³−3K²+3K−1 = 2k³+3k²+3k+1`（`k = K−1`）由 `ring` 一次收掉 ——
这正是为什么 `cube_key` 直接写成 k 的形式，而不必先写成 K 再换元。

**第三步（搬回 Nat）**

```lean
set K := t - r t - 1
set C := N * (2*K^3 + 3*K^2 + 3*K + 1 + 3*Q (r t) * (2*K + 1))
have hKi   : (K : Int) = (t:Int) - (r t:Int) - 1    -- push_cast [h1,h2]; ring
have hcast : (C : Int) = (N:Int) * (…)              -- rw [hC]; push_cast; rw [hKi]
exact Nat.cast_injective hgoalZ
```

`set K` 和 `set C` 的作用不只是让式子变短：**它们把 `↑(t − r t − 1)` 这种
"cast 里带截断减法"的怪物变成了 `↑K` 这样的原子**，于是 `push_cast` 不必再猜
哪个 `Nat.cast_sub` 该配哪个假设。第 21 轮在这一步卡住的表层原因，其实是括号里直接写
`((N * (… : Nat) : Int)` 导致 `: Nat` 归属错位、`push_cast` 无从下手。

### 3. 结果：`Cubic.lean` 5 条定理

| 定理 | 内容 |
|---|---|
| `eight_mul_card_cube` | `8 Σ_{m⊆r} m³ = N(r³ + 3Qr)` |
| `subm_sum_shift_cube` | `Σ(t−2m)³ + 6t²Σm + 8Σm³ = Nt³ + 12tΣm²` |
| `shell_sum_cube_split` | `Σ_S d³ + 3Σ(t−2m)² + N = 2Σ(t−2m)³ + 3Σ(t−2m)` |
| **`cube_key`** | **纯代数引理（新增）** |
| **`shell_sum_cube`** | **`Σ_{d∈S} d³ = N(2k³+3k²+3k+1+3Q(2k+1))`** |

### 4. `Dim4.lean`：ℤ⁴ 两族（5 条定理）

```lean
theorem shell_sum_cubic (a b : Nat) (t : Nat) (ht : 1 ≤ t) :
    (shell t).sum (fun d => if d = 0 then 1 else a * (d*d*d) + b * d)
      = a * (shell t).sum (fun d => d*d*d) + b * (shell t).sum (fun d => d)
        + (if 0 ∈ shell t then 1 else 0)

theorem three_dvd (d : Nat) : 3 ∣ d * (d * d + 2)          -- 按 d % 3 三支
theorem three_mul_level (d : Nat) :
    3 * (8 * (d * (d * d + 2) / 3)) = 8 * (d*d*d) + 16 * d

theorem zero_count_Z4_moore (t) (ht) :
    Σ_{d∈S} (if d = 0 then 1 else 64d³ + 16d) = 64·M3 + 16σ + ε
theorem zero_count_Z4_vonNeumann (t) (ht) :
    3 · Σ_{d∈S} (if d = 0 then 1 else 8d(d²+2)/3) = 8·M3 + 16σ + 3ε
```

注意 ℤ⁴ 与 ℤ²/ℤ³ 的**结构性差别**：二次档的层大小是 `4k d² + 2`，在 `d = 0` 处给 2，
所以要 `−ε`；三次档的两族在 `d = 0` 处给 **0**（Moore 与 vN 的公式都没有常数项），
所以要 **`+ε`**。这个符号差别是本轮唯一"新"的组合事实，其余全是代数。

### 5. 数值验证（`scripts/285_four_dim.py`）

| 检查 | 范围 | 结果 |
|---|---|---|
| ℤ⁴ Moore 层大小 vs 暴力枚举 ℓ∞ 球 | d ≤ 10（17⁴ 个点） | OK |
| ℤ⁴ vN 层大小 vs 暴力枚举 ℓ¹ 球 | d ≤ 10 | OK |
| `Z = 64M3 + 16σ + ε` | t ≤ 200 | OK |
| `3Z = 8M3 + 16σ + 3ε` | t ≤ 200 | OK |
| `shell_sum_cube` 闭式 | t ≤ 2000 | OK |
| `three_mul_level` / `three_dvd` | d ≤ 500 | OK |

### 6. `Σ_{d∈S} d^j` 总表（终版）

| j | 闭式 | Lean | 验证 |
|---|---|---|---|
| 0 | `2N` | `card_shell` | ✓ |
| 1 | `N(2t−1−2r)` | `sigma_shell` | ✓ |
| 2 | `N(2K(K−1)+2Q+1)` | `shell_sum_sq` | ✓ |
| 3 | `N(2k³+3k²+3k+1+3Q(2k+1))` | **`shell_sum_cube`** | t ≤ 2000 ✓ |
| 4 | 需要 `r, Q, P16`（新不变量） | 未做 | t ≤ 500 ✓（`scripts/288`） |
| ≥ 4 | 不变量族 `P_j = Σ_{i∈bits r} 2^{ji}` 增长 | 未做 | 见 `docs/50` |

（**修正**，见 `docs/50`：`j ≥ 4` 其实有一个**结构性**障碍 —— 第 4 阶起
子掩码矩不再只用 `r` 和 `Q`，而是需要新不变量 `P16 = Σ_{i∈bits r} 16^i`。
见 `docs/50-invariant-tower.md`。）

### 7. 一句话教训

> **次数到 3 以后，不要再指望 `nlinarith`；换成 `linear_combination` + 手推系数，
> 并且先把代数从和式里剥出来。**
---

## 第 23 轮（另起一条线）：二正则性

计数表还有一个完全不同的读法：每一行都是 **2-regular** 序列，秩有干净规律
（ℤ^D 的行秩恰为 `D + 1`；纯 `c = d^j` 为 `j + 1`），而 **b 叉树不是 2-regular**。
详见 `docs/51-two-regularity.md`，Lean 侧是 `lean/Arm.lean` 的两步行递归（几何无关）：

```lean
theorem zero_count_two_mul (c) (u) (hu) :
    (shell (2*u)).sum c
      = (subm (r u)).sum (fun m => c (2*(u - 2*m)) + c (2*(u - 2*m) - 1))

theorem zero_count_two_mul_add_one (c) (u) (hu) :
    (shell (2*u+1)).sum c
      = (subm (r u)).sum (fun m => (c (2*(u-2*m)+1) + c (2*(u-2*m)))
                                  + (c (2*(u-2*m)-1) + c (2*(u-2*m)-2)))
```
