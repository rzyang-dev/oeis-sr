# 48 树：零点计数的乘积型闭式

第 15 轮把"零点数 = Σ c_d"用成了测量仪器，并指出增长类型决定闭式形态
（多项式 → 加性；指数 → 乘性）。这一轮把指数那一档**形式化**了。

新文件：`lean/Tree.lean`（19 条定理 + 1 个定义 `bits`，0 error / 0 sorry）。
新脚本：`280`。

---

## 0 结果

```
#Z_tree(t) = Σ_{d∈S(t)} b^d
           = (b+1) · b^{t−1−2r(t)} · ∏_{i ∈ bits(r(t))} (1 + b^{2^{i+1}})
```

其中 `bits(r) = {i < r : r 的第 i 位是 1}`。

| Lean 定理 | 内容 |
|---|---|
| **`shell_sum_pow`** | `Σ_{d∈S} b^d = (b+1)·b^{t−1−2r}·Σ_{m⊆r}(b*b)^m` |
| **`sum_subm_pow_eq_prod`** | `Σ_{m⊆r} y^m = ∏_{i∈bits r}(1 + y^{2^i})` |
| **`shell_sum_pow_factored`** | 上面两式合起来（`(b*b)^{2^i}` 形式） |
| **`shell_sum_pow_factored'`** | 每个因子写成 `1 + b^{2^{i+1}}` |

数值核对（脚本 280）：b = 2..8、t ≤ 300，**0 处不符**。

---

## 1 为什么是乘性

`Σ_{m⊆r} y^m` 这个"子掩码和"在二进制下分裂：

```lean
theorem sum_subm_pow_two_mul (u y) :
    (subm (2*u)).sum (fun m => y^m) = (subm u).sum (fun m => (y*y)^m)

theorem sum_subm_pow_two_mul_add_one (u y) :
    (subm (2*u+1)).sum (fun m => y^m) = (1+y) * (subm u).sum (fun m => (y*y)^m)
```

**参数翻倍 → 底数平方；参数为奇数 → 多一个因子 (1+y)。** 这就是因式分解的全部内容：
把 r 的二进制位从低到高读一遍，每一位贡献一个 `(1 + y^{2^i})`。

数值直觉（b = 2，y = 4）：

| t | bits(r(t)) | #Z(t) | 因子 |
|---|---|---|---|
| 3 | {0} | 15 | 3·2⁰·5 |
| 6 | {1} | 102 | 3·2¹·17 |
| 7 | {0,1} | 255 | 3·2⁰·5·17 |
| 12 | {2} | 6168 | 3·2³·257 |

（`3 = b+1`，`5 = 1+2²`，`17 = 1+2⁴`，`257 = 1+2⁸`。）

---

## 2 工程要点

### 2.1 `bits` 与 `testBit`

Mathlib 里**没有** `Nat.popcount`，`Nat.testBit` 的 API 也很薄。可行的定义是

```lean
def bits (r : Nat) : Finset Nat := (Finset.range r).filter (fun i => r.testBit i)
```

（用 `range r` 而不是 `range (r+1)`：位位置严格小于 r 对 r ≥ 1 成立，r = 0 时两边都是空集。）

递归律 `bits (2u) = (bits u).image (·+1)` 的**唯一难点**是区间条件：
从 `(2u).testBit (j+1) = u.testBit j` 得到 `j+1 < 2u ⟺ j < u`。
"⟸"用 `j < u → j+1 ≤ u ≤ 2u`；"⟹"需要 **`u.testBit j = true → j < u`**，即

```lean
theorem testBit_lt {u j : Nat} (h : u.testBit j = true) : j < u
```

证法：`Nat.testBit_eq_false_of_lt` 的逆否给出 `2^j ≤ u`，再用 **`j < 2^j`**（`lt_two_pow_self`，
对 j 归纳）即可。

⚠️ 注意必须是**严格**不等式：只有 `j ≤ 2^j` 时 `j ≤ 2^j ≤ u` 推不出 `j < u`，
`omega` 会直接给出反例模型。

### 2.2 降序子掩码和的"回文性"

`Σ_{m⊆r} y^{r−m}`（降序）和 `Σ_{m⊆r} y^m`（升序）相等 —— 这是把
`b^{t−2m−1}` 里的指数拆成 `(t−1−2r) + 2(r−m)` 之后必需的一步。

两条路：
* 用补集双射 `m ↦ r−m`（需要 `m ⊆ r → r−m ⊆ r`，得碰位运算）；
* **本文件走的路**：证明两边服从**同一个递推**（`sum_subm_pow_shift_two_mul` /
  `_add_one`），再对 r 强归纳 —— 完全避开补集。

后者顺手给出了一个通用模式：**只要两个关于子掩码的量服从同一条二进制递推，
它们就相等**；这正是 `sum_subm_pow_eq_prod` 的证明骨架。

### 2.3 归纳要对底数泛化

`sum_subm_pow_shift` 的归纳里底数会变成 `y*y`，所以命题必须写成

```lean
theorem sum_subm_pow_shift (r : Nat) :
    ∀ y : Nat, (subm r).sum (fun m => y ^ (r - m)) = (subm r).sum (fun m => y ^ m)
```

（`∀ y` 在归纳**内部**，否则 `ih` 只对原始 y 成立）。

---

## 3 与线性档的对照

| 档 | `c_d` | 闭式形态 | Lean |
|---|---|---|---|
| 常数 | `k` | `k·#S − (k−1)[0∈S]` | Final/Shells |
| 线性 | `k·d` | `k·σ + [0∈S]`（加性） | `shell_sum_linear` |
| 指数 | `b^d` | `(b+1)b^{t−1−2r}·∏`（乘性） | **本轮** |
| 多项式 | `Σ a_j d^j` | `Σ_j a_j · Σ_{d∈S} d^j` | 待做 |

"加性 vs 乘性"不是风格差异：线性档里 `Σ_{m⊆r} m` 是**线性泛函**（`#subm·r`），
指数档里 `Σ_{m⊆r} y^m` 是**特征和**，而特征和按二进制位分解。
零点计数的形态是层大小序列的**代数性质**的直接反映。

---

## 4 验证

| 对象 | 手段 | 范围 | 结果 |
|---|---|---|---|
| `sum_subm_pow_two_mul` 等 4 条递推 | 数值比 `subm` 和 | 全部 r ≤ 300 | ✓ |
| `sum_subm_pow_eq_prod` | 同上 | r ≤ 300 | ✓ |
| `shell_sum_pow`（子掩码形式） | 直接求和 | b ≤ 7, t ≤ 200 | ✓（脚本 279） |
| `shell_sum_pow_factored'` | 直接求和 | b ≤ 8, t ≤ 300 | ✓（脚本 280） |
| 19 条定理 | `#print axioms` | — | propext/choice/Quot.sound |

---

## 5 遗留

1. **交替核**（`#偶数层 = #奇数层`）：需要两条奇偶引理
   （`(t−2m) % 2 = t % 2`、`(t−2m−1) % 2 = 1 − t % 2`）再加 `shell_eq_image` 的集合分析。
2. **`Σ_{d∈S} d^j`**：线性档是 j = 1；D 维格点需要到 j = D−1。
   一般的 `Σ_{d∈S} d^j` 可以走 `Σ_{m⊆r} [(t−2m)^j + (t−2m−1)^j]` 再用
   `Σ_{m⊆r} m^i`（i ≤ j）—— 同样是把问题推给"子掩码幂和"。
3. **`bits` 与 OEIS 的 A000120**：有了 `sum_subm_pow_eq_prod`，
   `#subm r = 2^{popcount r}` 现在是 `y = 1` 的特例（`∏(1+1) = 2^{#bits}`），
   可以顺手把"计数是 2 的幂"升级为"指数是 popcount"。
