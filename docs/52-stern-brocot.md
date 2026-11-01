# 52 从顶部看：对偶闭式与 Stern–Brocot 连接

> 本轮（第 29 轮）发现：**"全体邻居相等" 规则生成的 CA 时空图，按列（固定距离）读取时，
> 死寂时刻的个数由 Stern 二分序列（Stern's diatomic sequence, A002487）给出。**
> 这是本项目中第一个真正的跨领域结构连接：元胞自动机 ↔ Stern–Brocot 树 / Farey 分数 /
> Calkin–Wilf 枚举 / 超二进制表示。

---

## 0. 三个新定理（全部已证，数值独立验证）

设 `S(t) = {d ≤ t : ⌊(t−d)/2⌋ ⊆ r(t)}` 是时刻 t 的"全死层集合"（shell），
`r(t) = t − 2^⌊log₂ t⌋`。

### 定理 A（对偶闭式，"从顶部看"）

设 `t ≥ 1`，`k = ⌊log₂ t⌋`，`s = 2^{k+1} − t`（t 到下一个 2 的幂的距离，`1 ≤ s ≤ 2^k`），
`u = s − 1`。则对 `0 ≤ d ≤ t`：

```
d ∈ S(t)   ⟺   u ⊆ ⌊(u + d)/2⌋
```

即 **状态只通过 `s` 依赖 t，与块号 k 无关**。对比原来的"从底部看"形式
`⌊(t−d)/2⌋ ⊆ r(t)`：两者是同一条规则在布尔格上的补集对偶。

> 验证：`scripts/307_dual_form.py`，对全部 `t ≤ 2^14`、全部 `0 ≤ d ≤ t`（1.34 亿个案例），
> 反例 **0**。

### 定理 B（无进位化简）

```
u ⊆ ⌊(u+d)/2⌋   ⟺   u &&& h = 0，其中 h = ⌊(d−u)/2⌋
```

于是

```
Σ_d  :=  {u : u ⊆ ⌊(u+d)/2⌋}  =  {u ≤ d : u &&& ⌊(d−u)/2⌋ = 0}
```

> 用到的核心引理（`scripts/313`，u,h < 300 全验证）：
> ```
> u ⊆ u + h   ⟺   u &&& h = 0
> ```
> 即"加上 h 不会破坏 u 的任何一个 1 位"等价于"u 与 h 的二进制支集不交"。

### 定理 C（Stern 定理）

设 `fusc` 是 Stern 二分序列（`fusc(0)=0, fusc(1)=1, fusc(2n)=fusc(n), fusc(2n+1)=fusc(n)+fusc(n+1)`）。
则

```
A(d) := |Σ_d|  =  fusc(d) + fusc(d+1)  =  fusc(2d+1)
```

也就是说：**每个二进块内、距离 d 这一层"死掉"的时刻个数，等于 Stern 序列相邻两项之和** ——
按 Calkin–Wilf/Stern–Brocot 对应，这正是第 d 个 Stern–Brocot 有理数 `p/q` 的 `p + q`。

> 验证：`scripts/308_stern.py`（d ≤ 4000）、`scripts/311_stern_proof.py`（全部递归片段，d ≤ 400）。

等价形式（`scripts/313`，n < 800 验证）：

```
c(n) := #{(u,h) : u &&& h = 0,  u + 2h = n}  =  fusc(n+1) = HB(n)
A(d) = c(d) + c(d−1)
```

其中 `HB(n)` = n 的**超二进制表示数**（每幂 2^i 最多用两次的表示）。
所以：**距离 d 处的死寂时刻，枚举了 d 与 d−1 的所有"带进位的二进制写法"。**

---

## 1. 定理 A 的证明

设 `t = 2^k + r`（`0 ≤ r < 2^k`），则 `s = 2^k − r`，`r(t) = r`。

```
d ∈ S(t) ⟺ m := ⌊(t−d)/2⌋ ⊆ r.
t − d = 2^{k+1} − s − d，故
m = ⌊(2^{k+1} − (s+d))/2⌋ = 2^k − ⌈(s+d)/2⌉        (2^{k+1} 是偶数)
```

于是条件变成 `2^k − ⌈(s+d)/2⌉ ⊆ 2^k − s`。

用补集引理：对 `1 ≤ a, b ≤ 2^k`，

```
2^k − a ⊆ 2^k − b   ⟺   (b−1) ⊆ (a−1)
```

（因为 `2^k − x = ¬(x−1)` 在低 k 位内，而 `¬A ⊆ ¬B ⟺ B ⊆ A`。）
取 `a = ⌈(s+d)/2⌉`，`b = s`，条件化为

```
(s−1) ⊆ (⌈(s+d)/2⌉ − 1) = ⌊(s+d−1)/2⌋ = ⌊(u+d)/2⌋.   ∎
```

（需要 `a ≤ 2^k` 即 `s+d ≤ 2^{k+1}`，正好是 `d ≤ t`。）

## 2. 无进位引理的证明

**引理.** `u ⊆ u+h ⟺ u &&& h = 0`（`u,h ∈ ℕ`）。

*证明.* 经典判据：`x ⊆ y ⟺ x ≤ y ∧ (y−x) &&& x = 0`
（因为 `y = x + (y−x)`，`x ⊆ y` 等价于这个加法无进位）。
取 `y = u+h`，`y−x = h`，即得。∎

定理 B 的推论：`u ⊆ B` 时 `B − u = ⌊(u+d)/2⌋ − u = ⌊(d−u)/2⌋`，故条件即 `u &&& ⌊(d−u)/2⌋ = 0`。

## 3. 递归结构（定理 C 的核心）

记 `p(d) = #{u ∈ Σ_d : u + d 奇}`，`q(d) = #{u ∈ Σ_d : u + d 偶}`（`A = p + q`）。则

```
Σ_{2e}   =  2·Σ_e  ⊎  {2v+1 : v ∈ Σ_e, v+e 奇}
Σ_{2e+1} =  2·Σ_e  ⊎  {2v+1 : v ∈ Σ_e, v+e 偶}
```

（`2·Σ_e` 表示 `{2v : v ∈ Σ_e}`，两部分按奇偶性不交。）

*证明.* 用定理 B 的 `u &&& ⌊(d−u)/2⌋ = 0` 形式，逐奇偶拆解：

* `d = 2e, u = 2v`：`⌊(2e−2v)/2⌋ = e−v`，条件 `2v &&& (e−v) = 0`
  `⟺ v &&& ⌊(e−v)/2⌋ = 0`（两边同除 2，因为 `2v` 的最低位是 0）
  `⟺ v ∈ Σ_e`。
* `d = 2e+1, u = 2v`：`⌊(2e+1−2v)/2⌋ = e−v`，同一条件 `⟺ v ∈ Σ_e`。
* `d = 2e, u = 2v+1`：`⌊(2e−2v−1)/2⌋ = e−v−1`，要求最低位为 0
  （即 `e−v−1` 偶，`v+e` 奇），其余位条件 `⟺ v ∈ Σ_e`。
* `d = 2e+1, u = 2v+1`：`⌊(2e−2v)/2⌋ = e−v`，要求最低位为 0
  （即 `e−v` 偶，`v+e` 偶），其余位 `⟺ v ∈ Σ_e`。∎

由此立刻读出

```
A(2e)   = A(e) + p(e)        p(2e)   = p(e)        q(2e)   = A(e)
A(2e+1) = A(e) + q(e)        p(2e+1) = A(e)        q(2e+1) = q(e)
```

而 Stern 序列满足 `f(2e) = f(e)`，`f(2e+1) = f(e) + f(e+1)`。
对 `d` 做强归纳，假设 `(A, p, q)(e) = (f(e)+f(e+1), f(e), f(e+1))`：

* `p(2e) = p(e) = f(e) = f(2e)` ✓
* `q(2e) = A(e) = f(e)+f(e+1) = f(2e+1)` ✓
* `A(2e) = A(e)+p(e) = f(e)+f(e+1)+f(e) = f(2e)+f(2e+1)` ✓
* `p(2e+1) = A(e) = f(2e+1)` ✓
* `q(2e+1) = q(e) = f(e+1) = f(2e+2)` ✓
* `A(2e+1) = A(e)+q(e) = f(e)+2f(e+1) = f(2e+1)+f(2e+2)` ✓

基例 `d = 0`：`Σ_0 = {0}`，`A = 1 = f(0)+f(1)`，`p = 0 = f(0)`，`q = 1 = f(1)`。∎

**注意递归的"形状"**：`(p,q)(2e) = (p(e), A(e))`，`(p,q)(2e+1) = (A(e), q(e))` ——
这正是 Stern 的 2×2 矩阵（行列式 1 的幺模矩阵，`A = p+q`），
也就是 Stern–Brocot 树"左右子树"的转移矩阵。**CA 的死寂集合递归 = Stern–Brocot 树的遍历。**

---

## 4. 局部的数位刻画（另一个等价形式）

`scripts/312` 验证：``u ∈ Σ_d ⟺ ∀i: 若 bit_i(u)=1 则 bit_{i+1}(u) ⊕ bit_{i+1}(d) ⊕ bit_i(d) = 1``。

即：把 u 的二进制位从低位往高位读，需要一个 **2 状态自动机**，
其转移只依赖 d 的相邻两位。Stern 序列正是"2 状态转移矩阵乘积"的经典产物，
这解释了为什么这里必然出现 Stern 而不是别的序列。

---

## 5. 数值表

`A(d) = fusc(d)+fusc(d+1)`，d = 0..20：

```
1, 2, 3, 3, 4, 5, 5, 4, 5, 7, 8, 7, 7, 8, 7, 5, 6, 9, 11, 10, 11
```

每块（`2^k ≤ t < 2^{k+1}`）内死寂 (t,d) 对总数：`Σ_t 2^{wt t} = 2·3^k`；
其中 `d < 2^k` 的恰好一半，且

```
Σ_{d < 2^k} A(d) = 3^k        （k = 0..11 验证，scripts/308）
```

这是 Stern 的经典恒等式 `Σ_{d<2^k} fusc(2d+1) = 3^k` 的 CA 解释：
**"每块死寂对的一半 = 3^k" 与 "Stern 奇数位求和 = 3^k" 是同一件事。**

---

## 6. 跨领域地图（为什么这算"啊哈"）

| 领域 | 对象 | 与本结果的关系 |
|---|---|---|
| **Stern 二分序列** A002487 | `fusc` | `A(d) = fusc(d)+fusc(d+1)` |
| **Stern–Brocot / Farey 树** | 有理数枚举 | `A(d)` = 第 d 个分数的 `p+q`（"高度"） |
| **Calkin–Wilf 树** | `n ↦ (fusc(n), fusc(n+1))` | 同一个双射 |
| **超二进制表示** | 每幂 ≤ 2 次的二进制展开 | `c(n) = HB(n)`，`A(d) = HB(d)+HB(d−1)` |
| **连分数** | Stern 序列编码连分数 | `Σ_d` 的递归 = 连分数的"跑长"分解 |
| **2-正则序列** | `fusc` 是秩 2 的原型 | 列方向秩 2，行方向秩 `deg+1` |
| **Gould 序列** A001316 | `2^{wt t} = |S(t)|` | 行方向的"长度" |
| **Delange/数字和** | `Σ_{t<N} 2^{wt t}` | 行方向求和的渐近 |
| **Christol 定理** | mod p 代数性 | `A(d) mod p` 仍 2-automatic |

**"啊哈"点**：一个由"(全体邻居相等)"定义的、看起来纯几何的元胞自动机，
其时空图按列统计后 **正好是数学中最古老的二分递归结构**（Stern 1858）。
这不是巧合——第 4 节的自动机刻画说明了机制：2 状态的数位转移必然产生 Stern。

---

## 7. 对本项目其余部分的意义

1. **行 vs 列的双重 2-正则性**：
   - 行方向（时刻 t → 死层集合 S(t)）：秩 = `deg(c)+1+[中心修正]`，即"几何维度 + 1"（docs/51）；
   - 列方向（层 d → 死寂时刻集合 Σ_d）：秩 = 2，由 Stern 支配。
   时空矩阵 M（`M[t][d] = [d ∈ S(t)]`）在两个方向都是 2-正则的，且两个方向的秩差别巨大。

2. **新的精确公式**（对所有几何 c 成立，不只多项式）：
   ```
   设 t = 2^{k+1} − 1 − u（即 u = s(t) − 1），则
   Z_c(t) = Σ_{d : u ≤ d ≤ t, u ⊆ ⌊(u+d)/2⌋} c_d
   ```
   条件 `u ⊆ ⌊(u+d)/2⌋` 自动给出 `u ≤ d`，所以上界 d ≤ t 是唯一的截断。
这把"每个块顶部附近"的零计数写成了一个**只依赖 u 的求和**，与 k 无关（只在 d ≤ t 处截断）。
   对树这类指数层函数（没有有限矩展开）也有效——这是旧框架做不到的。

3. **为什么树不行**：树的行方向秩无界（docs/51）；但列方向是纯组合的，与 c 无关，
   所以"列方向"总能用 Stern 描述。两个方向的差别正是"几何 vs 规则"的差别。

---

## 8. 状态

| 项 | 状态 |
|---|---|
| 定理 A 对偶闭式 | **已证**（本文第 1 节）+ 1.34 亿案例数值验证 |
| 定理 B 无进位化简 | **已证**（第 2 节） |
| 定理 C Stern 定理 | **已证**（第 3 节）+ d ≤ 4000 数值验证 |
| 局部自动机刻画 | 数值验证（d ≤ 500），机制解释 |
| `Σ_{d<2^k}A(d) = 3^k` | 数值验证（k ≤ 11） |
| Lean 形式化 | 待做（下一轮） |
| 与 OEIS 的关系 | `A(d)` 本身 = A002487 的相邻和；CA 侧解读是新的 |

### 未解 / 值得继续

* ~~`Σ_d` 与 Stern–Brocot 树节点之间是否存在显式双射？~~ **已回答**（见 docs/56）：
  规范形式是 `Σ_d ≅ Hyp(d) ⊎ Hyp(d−1)`（`Hyp` = 超二进制表示集，映射 `u ↦ (u, ⌊(d−u)/2⌋, (d−u) mod 2)`，
  逆映射是投影到 `u`）；"加倍 = Calkin–Wilf 左子"那条路被计数障碍排除
  （`|Σ_{2e}| = |Σ_e| + fusc(e) ≠ 2|Σ_e|`）。
  另有元素级刻画：`u ∈ Σ_d` ⟺ `u` 的每个极大 1-段 `[a,b]` 满足 `b ∈ T(d)` 且 `d` 在段上常值
  （`T(d)` = `d` 的相邻位变化位置）。
* 列方向的"2-正则秩 = 2"能否直接由行方向的传输矩阵推出？
* 这个"顶部坐标 s"的技巧能否用到别的规则族（Rule 126、二维 vN 等）？
  理论上可以：本项目的万能闭式只依赖"层结构"，所以**任何**满足 (H1)–(H4) 的几何都适用。
---

## 9. Lean 形式化（`lean/Brocot.lean`，48 条声明）

**Stern 递归已完整形式化**，公理仅 `[propext, Classical.choice, Quot.sound]`，无 `sorry`。

| 组 | 声明 | 内容 |
|---|---|---|
| 无进位 | `land_add_iff` | `u &&& (u+h) = u ↔ u &&& h = 0` |
| | `land_of_le` | `u ≤ B → (u &&& B = u ↔ u &&& (B−u) = 0)` |
| 移位 | `land_two_mul`, `land_two_mul_iff` | `(2a) &&& b = 2(a &&& (b/2))` |
| 奇数移位 | `land_odd_left` | `(2v+1) &&& X = 0 ↔ X%2 = 0 ∧ v &&& (X/2) = 0` |
| 集合 | `sig`, `mem_sig`, `mem_sig_iff` | `Σ_d` 与 `u ⊆ ⌊(u+d)/2⌋` 的桥 |
| 成员递归 | `mem_sig_two_mul`, `mem_sig_two_mul_add_one`, `mem_sig_odd_two_mul`, `mem_sig_odd_two_mul_add_one` | 四个奇偶情形 |
| 集合分解 | `sig_even_two_mul`, `sig_odd_two_mul`, `sig_even_two_mul_add_one`, `sig_odd_two_mul_add_one` | `Σ_{2e}, Σ_{2e+1}` 的偶/奇部 |
| 基数递归 | `card_sig_two_mul`, `card_sig_two_mul_add_one`, `card_pp_two_mul`, `card_qq_two_mul`, `card_pp_two_mul_add_one`, `card_qq_two_mul_add_one` | 六个基数等式 |
| Stern | `fusc`, `fusc_zero`, `fusc_one`, `fusc_two_mul`, `fusc_two_mul_add_one` | 定义 + 两条递归 |
| **主定理** | `stern_triple`, **`card_sig_stern`**, `card_pp_stern`, `card_qq_stern` | `(Σ_d).card = fusc d + fusc (d+1)` |

```
'OEIS.Rule129.card_sig_stern' depends on axioms: [propext, Classical.choice, Quot.sound]
```

主定理的证法就是第 3 节的强归纳（同时在 `(A, p, q)` 三个量上归纳），
其中 `p`/`q` 是 `Σ_d` 按奇偶性的两半。

### 9b. 定理 A 的形式化（`lean/Dual.lean`，12 条声明）

**完成。** 主定理：

```lean
theorem mem_shell_dual {t d : Nat} (ht : 1 ≤ t) (hd : d ≤ t) :
    d ∈ shell t ↔ (2 ^ (Nat.log2 t + 1) - t - 1) ∈ sig d
```

公理 `[propext, Classical.choice, Quot.sound]`，无 `sorry`。

它需要的 `testBit` 补集 API（Mathlib 里没有，全部自建）：

| 声明 | 内容 |
|---|---|
| `land_eq_zero_iff` | `x &&& y = 0 ↔ ∀ i, x.testBit i → y.testBit i = false` |
| `land_eq_self_iff` | `x &&& y = x ↔ ∀ i, x.testBit i → y.testBit i` |
| `testBit_zero_eq` | `n.testBit 0 = decide (n % 2 = 1)` |
| `testBit_succ_div_two` | `n.testBit (j+1) = (n/2).testBit j` |
| `bit_two_mul_add_one_sub` | `2N+1−w = Nat.bit (w%2=0) (N − w/2)` |
| **`testBit_pow_sub_one_sub`** | `(2^k − 1 − w).testBit i = !(w.testBit i)`（i < k，归纳） |
| `testBit_eq_false_of_le` | `x ≤ 2^k−1 → k ≤ i → x.testBit i = false` |
| **`land_pow_sub_eq`** | **补集引理**：`x &&& (2^k−1−w) = 0 ↔ x &&& w = x` |
| `land_le_right` | `a &&& b ≤ b`（Mathlib 无此引理） |
| `div_two_pow_sub` | `(2^{k+1} − X)/2 = 2^k − (X+1)/2` |

主定理的证明就是 9b 之前写下的那条 `↔` 链：

```
m ⊆ r t  ⟺  m &&& (r t − m) = 0  ⟺  m &&& e = 0
        ⟺  e &&& (2^k − 1 − (e+u)) = 0  ⟺  e &&& (e+u) = e
        ⟺  e &&& u = 0  ⟺  u &&& e = 0  ⟺  u ∈ sig d
```

（`m = (t−d)/2`，`A = (s+d+1)/2`，`u = s−1`，`e = A−s = (d−u)/2`。）
退化情形（`s > d+1`）用 `land_le_right` 处理：此时 `m > r t` 且 `u > d`，两边都假。

```
'OEIS.Rule129.mem_shell_dual' depends on axioms: [propext, Classical.choice, Quot.sound]
'OEIS.Rule129.card_sig_stern' depends on axioms: [propext, Classical.choice, Quot.sound]
```

。