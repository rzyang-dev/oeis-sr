# 59 秩缺口填补：`dim span{A(k,j)ᵀp} = #DClose(supp p)` 【已证】

> 第 34 轮。承接 [docs/55-rank-law.md](docs/55-rank-law.md) 第 2 节的归约与两侧界，
> 把中间那一步 **`dim span{A(k,j)ᵀp} = #DClose(supp p)`** 证掉。
> 脚本 [scripts/330_rank_closure.py](scripts/330_rank_closure.py)（精确有理/整数运算，**9 秒**，退出码 0）。
>
> **一句话**：把转移矩阵算成闭式 `A(k,j)[i][l] = 2^{kl} C(i,l) S_j(i-l)` 之后，
> 一切都塌缩成两件事——**`k` 只是逐坐标伸缩 `2^{kl}`，`j` 只决定一个"权重模式" `w(j)`**。
> 于是一个 `j` 加 `#DClose` 个连续的 `k` 就够：Vandermonde 管独立，`j` 只负责"每个坐标的权重非零"。
> 缺口的真正内容不是"需要很多不同的 (k,j) 组合"，而是"**要选对 `j` 使权重模式全非零**"。

---

## 0. 结论速览（含标注）

| # | 结论 | 标注 |
|---|---|---|
| 1 | **显式元素公式**：`A(k,j)[i][l] = 2^{kl} C(i,l) S_j(i-l)`，`S_j(d) = Σ_{m⊆j}(j-2m)^d`（`j < 2^k`） | 【已证】(EGF + arm 递归)，数值 381 例 0 不符 |
| 2 | `S_j(d) = 0`（`d` 奇）、`S_j(0) = 2^{wt j}`：**奇偶解耦** | 【已证】(E_j 对 `e↦−e` 封闭)，数值 4096×8 例 0 反例 |
| 3 | **列公式**：`(Aᵀp)_l = 2^{kl} Σ_r C(l+2r,l) S_j(2r) p_{l+2r}`，只吃**同奇偶、指标 ≥ l** 的系数（重得上界 `supp ⊆ DClose`） | 【已证】，数值 15240 个向量 0 反例 |
| 4 | **单点**：`p = e_i` ⟹ `dim = ⌊i/2⌋+1 = #DClose({i})`，且 `j = 1`、`k = 1..⌊i/2⌋+1` 已够 | 【已证】，数值 `i ≤ 12` 全中 |
| 5 | **单 j 判据**：固定 `j` 时 `dim span_k{A(k,j)ᵀp} = #DClose` ⟺ **`w^{(ε)}_a(j) ≠ 0` 对所有 `ε, a`** | 【已证】(根计数)，数值 2400 例 0 反例 |
| 6 | **存在性（一致界）**：`m ≤ A_0(A_0+1)/2 + A_1(A_1+1)/2 (≤ A(A+1))` 内必有 `j = 2^m` 使 `w(2^m)` 全非零（`A_ε = ⌊max(S_ε)/2⌋`），**与系数大小无关** | 【已证】，数值 300/300 + 对抗例 |
| 7 | **存在性（2-adic 界）**：整数 `p`、`B = max|p_i|` 时 `m ≥ A+1+⌈log₂B⌉` 也行（显式、可算） | 【已证】，数值 250/250 |
| 8 | **主定理**：`dim_Q span{A(k,j)ᵀp : k ≥ 0, 0 ≤ j < 2^k} = #DClose(supp p)`；**单个 `j = 2^m` 加 `#DClose` 个连续 `k` 就达到**，且这组向量线性无关（不能再少一个 `k`） | 【已证】，数值 400/400 + 120/120 紧 |
| 9 | **猜想 A 成立**：`rank₂(Z_c) = #DClose(supp p) + [δ≠0]` | 【已证】(= 第 8 条 + docs/55 定理 1)，端到端数值 825/825 |
| 10 | 把 1–9 形式化进 Lean | 【未做】 |
| 11 | 非多项式情形（docs/55 猜想 B、C′）：本轮未触及 | 【未做】 |

**地位变化**：docs/55 里 `rank = #DClose + [δ≠0]` 是【猜想 A】，1016 例 0 反例；
本轮之后它是**定理**（唯一"外来"输入是 docs/55 第 2 节的归约定理，那句是纸面 3 行 + Lean 引理）。
数值部分现在只是"核对证明没写错"，不再是"支持猜想的证据"。

---

## 1. 记号与出发点

沿用 docs/55：

    M0[i][l] = 2^i·[i=l],      M1[i][l] = C(i,l)·2^{l+1}·[l ≤ i, l ≡ i (mod 2)]
    A(k,j)   = M_{b_0} M_{b_1} ⋯ M_{b_{k−1}},     b_t = (j >> t) & 1        (0 ≤ j < 2^k)
    X(2^k n + j) = A(k,j)·X(n),   X = (Φ_0, Φ_1, …)
    p = c(x) + c(x−1),  S = supp(p),  δ = c(0) + c(1) − p(1) = c_0 − P(0)

    DClose(S) = ⋃_{i∈S} { l : l ≤ i, l ≡ i (mod 2) } = ⋃_{ε} {ε, ε+2, …, 2A_ε+ε}

其中（`S_ε = S ∩ {l ≡ ε}`，空类记 `A_ε = −1`）

    A_ε := ⌊max(S_ε)/2⌋ ,      #DClose(S) = (A_0+1) + (A_1+1)   （空类贡献 0）

docs/55 已证的两条（本轮只用到第 (i) 条作为黑箱，其余自证）：

* (i) **归约**：`rank₂(Z_c) = dim span{A(k,j)ᵀp} + [δ≠0]`；
* (ii) 上界 `≤ #DClose + [δ≠0]`（本轮第 3 条把它的证明独立重做了一遍）；
* (iii) 下界 `≥ #supp p + [δ≠0]`（本轮被第 8 条完全吸收）。

**本轮只研究一个纯线性代数命题**（`p` 可以是 `Q^{D+1}` 里任意向量，不要求来自某个 `c`）：

    P(D, p):   dim_Q span{ A(k,j)ᵀ p : k ≥ 0, 0 ≤ j < 2^k } = #DClose(supp p).

> 为什么可以放开成"任意 `p`"：`c ↦ c(x)+c(x−1)` 在次数 ≤ D 的多项式空间上是**双射**
> （三角、对角元恒为 2），所以每个 `p` 都唯一来自某个 `c`。脚本 (5a) 用 Fractions 反解
> `c` 并回代，60/60 吻合。因此"对任意 `p` 证 `P(D,p)`"与"对任意多项式 `c` 证猜想 A 的中间步"等价，
> 而且 `p` 的取法可以完全脱离几何/组合背景。

---

## 2. 引理 1：转移矩阵的显式元素 【已证】

**引理 1**  设 `k ≥ 0`，`0 ≤ j < 2^k`。则对一切 `0 ≤ l ≤ i`：

    A(k,j)[i][l] = 2^{k l} · C(i,l) · S_j(i−l),      S_j(d) := Σ_{m ⊆ j} (j − 2m)^d ,   S_j(0) := 2^{wt j}

（约定 `0^0 = 1`；`l > i` 时右端为 0。）

*证明.* 关键恒等式是**臂的递归**：

    r(2^k n + j) = 2^k r(n) + j            （0 ≤ j < 2^k，n ≥ 1）
    arm(2^k n + j) = { 2^k x + (j − 2m) : x ∈ arm(n), m ⊆ j }

（第二式：`2^k r(n) + j` 的低 `k` 位恰是 `j`、高位恰是 `r(n)`，于是子掩码按位拆开。）取指数生成函数

    φ(t;y) := Σ_{x ∈ arm(t)} e^{xy} = Σ_i Φ_i(t) y^i / i!

则 `φ(2^k n + j; y) = Σ_{m⊆j} e^{(j−2m)y} · φ(n; 2^k y)`。把 `φ(n;2^k y) = Σ_l Φ_l(n) 2^{kl} y^l/l!`
与 `e^{ay} = Σ_{n≥0} a^n y^n/n!` 相乘，比较 `y^i/i!` 的系数即得

    Φ_i(2^k n + j) = Σ_l Φ_l(n) · 2^{kl} C(i,l) S_j(i−l).   ∎

**数值复核**（脚本 [1]）：与 `M_{b_0}⋯M_{b_{k−1}}` 的矩阵乘积逐元素比对 `D ≤ 9, k ≤ 6` 全部 `j`：

    (a) formula vs the M0/M1 product:  381 cases (D<=9, k<=6, all j<2^k), 0 mismatches
    (b) arm recursion arm(2^k n+j) = 2^k arm(n) + (j-2m):  713 cases, 0 mismatches
    (c) cocycle A(k1+k2, j1+2^k1 j2) = A(k1,j1)A(k2,j2):  225 cases, 0 mismatches

（(b) 是组合核心，(c) 是"公式与递推兼容"的独立旁证。）

**两个直接推论**（也是后面全部论证的支点）：

> **(C1) `j` 与 `k` 分工。** `k` 只以 `2^{kl}` 逐坐标伸缩出现；`j` 只通过 `S_j(2r)` 进入。
> 因此对**固定**的 `j`：`A(k,j)ᵀp = diag(2^{kl})_l · v(j)`，其中 `v(j) := (Σ_r C(l+2r,l)S_j(2r)p_{l+2r})_l`
> 与 `k` 无关。于是 `k` 一族正好是一个"带权 Vandermonde"。
>
> **(C2) 列公式 / 上界。** `S_j` 的奇次项为 0（引理 2），故 `(Aᵀp)_l` 只依赖 `p` 在 `{l, l+2, l+4, …}` 上的值；
> 特别地 `supp(A(k,j)ᵀp) ⊆ DClose(S)`，故 `dim ≤ #DClose(S)`——**上界是引理 1 的一行推论**。

---

## 3. 引理 2：奇偶解耦 【已证】

**引理 2**  `E_j := {j − 2m : m ⊆ j}` 对 `e ↦ −e` 封闭（`m ↦ j−m` 保持"是子掩码"），故

    S_j(d) = Σ_{e ∈ E_j} e^d = 0   (d 奇),        S_j(0) = #E_j = 2^{wt(j)},
    S_j(2r) = 2·Σ_{e ∈ E_j, e>0} e^{2r}   (j ≥ 1 时 > 0 ; j = 0 时 S_0(0)=1, S_0(2r)=0 (r>0)).

脚本 [2] 的表（`j = 0..15`，含 `S_j(0) = 2^{wt j}`、`S_j(1) = S_j(3) = 0`）：

      j  wt(j)   S_j(0)  2^wt   S_j(1)  S_j(2)  S_j(3)  S_j(4)  S_j(6)   #E_j
      0     0        1     1       0       0       0       0        0      1
      1     1        2     2       0       2       0       2        2      2
      2     1        2     2       0       8       0      32      128      2
      3     2        4     4       0      20       0     164     1460      4
      4     1        2     2       0      32       0     512     8192      2
      5     2        4     4       0      68       0    1412    32708      4
      7     3        8     8       0     168       0    6216   268008      8
     15     4       16    16       0    1360       0  206992 37308880     16
    j < 4096, d <= 8: odd-d vanishing and S_j(0)=2^wt(j): 0 violations

**推论（奇偶解耦）**：把坐标按奇偶分成两类，写 `l = 2a+ε`，则

    (A(k,j)ᵀp)_{2a+ε} = 2^{(2a+ε)k} · w^{(ε)}_a(j),
    w^{(ε)}_a(j)   := Σ_{b=a}^{A_ε} C(2b+ε, 2a+ε) · S_j(2(b−a)) · p_{2b+ε}          (0 ≤ a ≤ A_ε)

于是 `V := span{A(k,j)ᵀp} = V_0 ⊕ V_1`，`V_ε ⊆ span{e_l : l ≡ ε, l ≤ 2A_ε+ε}`，
两个奇偶类**完全独立**，各自是一个上三角系统（`b ≥ a`，且 `w^{(ε)}_{A_ε} = S_j(0)p_{2A_ε+ε} = 2^{wt j}p_{2A_ε+ε} ≠ 0`）。

---

## 4. 单点情形：任务建议路线 1 的完整回答 【已证】

`p = e_i`（`S = {i}`，只有一个奇偶类，`A_ε = ⌊i/2⌋`）：

* `M1ᵀe_i` 就是 `M1` 的第 `i` 行，`(M1ᵀe_i)_l = C(i,l)2^{l+1}`（`l ≤ i, l ≡ i`）。
  因为 `0 ≤ l ≤ i` 时 `C(i,l) ≠ 0`，**这一个向量的支撑恰好就是整条 parity chain**
  `{i, i−2, …, i mod 2}`，其势为 `⌊i/2⌋+1 = #DClose({i})`。
* 但请注意：**"一个向量覆盖整条链"只给出 `dim ≥ 1`，不给出 `dim ≥ ⌊i/2⌋+1`**。
  补齐这一步的是 (C1)：`j = 1` 固定时 `S_1(2r) = 2`（全非零），于是
  `(A(k,1)ᵀe_i)_l = 2^{kl}·2C(i,l)`，取 `k = 1, …, ⌊i/2⌋+1` 得"权 `2C(i,l)`、节点 `2^l`"的 Vandermonde：
  `det = (Π_l 2C(i,l))·Π_{l<l'}(2^{l'}−2^l) ≠ 0`。
* 上界 `≤ ⌊i/2⌋+1` 由 (C2)。两者夹死：`dim = ⌊i/2⌋+1`。

脚本 [3]（`i = 0..12`，精确消元；下表只列偶数行，奇数行同样全中）：

      i  floor(i/2)+1  rank{all k<=6,j}  rank{j=1,k=1..}  #supp(M1^T e_i)
      0           1                 1                1               1
      2           2                 2                2               2
      4           3                 3                3               3
      6           4                 4                4               4
      8           5                 5                5               5
     10           6                 6                6               6
     12           7                 7                7               7
    violations: 0

所以路线 1 **成立**，但正确的因果链是"**一个 `j` 的整族 `k`**"，不是"单个向量"。
这一步恰好就是一般情形的缩影。

---

## 5. 一般情形：主定理 【已证】

### 5.1 单 `j` 判据（权重非零 ⟺ 张满）

**引理 3**  固定 `j`，记 `n = #DClose(S)`，取 `k_0 = max(1, bit_length(j))` 与连续 `n` 个 `k`：
`K = {k_0, …, k_0+n−1}`（这些 `k` 满足 `j < 2^k`，合法）。则

    dim span{ A(k,j)ᵀp : k ∈ K } = n   ⟺   w^{(ε)}_a(j) ≠ 0  对所有 ε ∈ {0,1}, 0 ≤ a ≤ A_ε.

*证明.* (⇒) 若某 `w^{(ε)}_a(j) = 0`，则该坐标在**所有** `k` 上都是 0（(C1)），维数必然 `< n`。

(⇐) 设 `Σ_{k∈K} c_k A(k,j)ᵀp = 0`。对每个 `(ε,a)`，由 (C1) 与 `w^{(ε)}_a ≠ 0` 得

    C(2^{2a+ε}) = 0,      其中 C(t) := Σ_{k∈K} c_k t^k ∈ Q[t].

两类节点 `{2^{2a+ε} : 0 ≤ a ≤ A_ε, ε = 0,1}` 是 `n` 个**互异非零**实数（指数 `0..2A_0` 与 `1,3,…,2A_1+1` 不相交），
故 `C` 有 `n` 个互异非零根；又 `min K = k_0 ≥ 1`，故 `0` 是 `C` 的根且重数 `≥ k_0`。
于是根的重数总和 `≥ k_0 + n > k_0+n−1 = max K ≥ deg C`，所以 `C ≡ 0`，即各 `c_k = 0`。∎

**这就是"加权组合 vs 并集"那个担心的答案**：权重 `w` 是**行伸缩**，`k` 一族在每一类里都是
"权 `w_a` × 节点 `2^{(2a+ε)k}`"的 Vandermonde 型矩阵；只要 `w` 全非零，权重完全不影响独立性。
**根本不需要换 `j` 来"改变组合系数"**——一个 `j` 就够，前提是它的权重模式不出现 0。

数值核对（脚本 4c）：`60` 个随机 `p`、`j = 0..39`，共 2400 例

    equivalence 'single-j rank = #DClose  <=>  w(j) has full support' : 2400 cases, 0 violations

### 5.2 存在性（一致界 `m ≤ A_0(A_0+1)/2 + A_1(A_1+1)/2`，不含系数大小）【已证】

**引理 4**  取 `j = 2^m`（则 `E_j = {2^m, −2^m}`，`S_{2^m}(2r) = 2·4^{mr}`）。令 `z = 4^m`，则

    w^{(ε)}_a(2^m) = W^{(ε)}_a(z),      W^{(ε)}_a(z) = 2·Σ_{b=a}^{A_ε} C(2b+ε,2a+ε) p_{2b+ε} z^{b−a}

是 `z` 的**次数恰为 `A_ε − a` 的多项式**（首项系数 `2C(2A_ε+ε,2a+ε)p_{2A_ε+ε} ≠ 0`）。
故 `w^{(ε)}_a(2^m) = 0` 至多对 `A_ε − a` 个 `m` 成立，从而

    #{ m ≥ 0 : 某个坐标的权重为 0 }  ≤  Σ_ε A_ε(A_ε+1)/2   ≤   A(A+1) ,   A := max_ε A_ε.

**推论**：把 `T := A_0(A_0+1)/2 + A_1(A_1+1)/2` 记作坏 `m` 的个数上界，则
`m ∈ {0,1, …, T}` 里一定有一个"好"的 `m`（否则就有 `T+1` 个坏 `m`，矛盾）；对它就可用引理 3。
两个奇偶类都满时 `T = A(A+1)`，只有一个类非空时 `T = A(A+1)/2`。
界与系数大小、与 `p` 的分子分母都无关，纯粹是"指数多项式根数 ≤ 次数"。

数值（脚本 4d′，`m < 48` 内数"坏 `m`"）：

    #bad m <= A_0(A_0+1)/2 + A_1(A_1+1)/2 : 300/300   (largest bad count seen 1)
    adversarial p = -64 + 84x^2 - 21x^4 + x^6  (w_0 = 2(z-1)(z-4)(z-16)):
      bad m = [0, 1, 2]   smallest good m = 3   A_0(A_0+1)/2 = 6
      rank of the m-family: [3, 3, 3, 4, 4, 4]   (#DClose = 4)
    adversarial p = x^2 - 4 : bad m = [1] (w_0 = 2z - 8, root z = 4)

（对抗例 `p = −64+84x^2−21x^4+x^6` 是**构造**出来的：让 `W^{(0)}_0` 在 `z = 1,4,16`（即 `m = 0,1,2`）处为零，
所以 `m = 0,1,2` 的权重模式确实有 0，秩只有 3；`m = 3` 起才满 4。
这正是"必须选对 `j`"的实例，也说明**`j` 的选择不能只看 `wt(j)`**。）

### 5.3 存在性（2-adic 界 `m ≥ A+1+⌈log₂B⌉`）【已证】

把 `p` 乘上公分母（不改变"是否为零"），设 `p_i ∈ Z`、`B = max|p_i|`。取 `j = 2^m`：

    w^{(ε)}_a(2^m) = Σ_{b=a}^{A_ε} C(2b+ε,2a+ε)·2·4^{m(b−a)}·p_{2b+ε}

`b = A_ε` 项 `T` 满足 `|T| ≥ 2·4^{m(A_ε−a)}`；其余项之和 `R` 满足
`|R| ≤ 2B·4^{m(A_ε−1−a)}·2^{2A_ε+ε} ≤ 2B·4^{m(A_ε−1−a)}·2^{2A+1}`。
只要 `2^{2m} > B·2^{2A+1}`（即 `m ≥ A+1+⌈log₂B⌉`）就有 `|R| < |T|`，故 `w ≠ 0`。
（另一种等价的写法：`T` 的 2-adic 赋值固定，`R` 被更高的 2 幂整除。）

数值（脚本 4d，250 个随机 `p`，`|p_i| ≤ 20`）：

    at m = A+1+ceil(log2 B) the vector w(2^m) has full support : 250/250

### 5.4 主定理

**定理 5（秩缺口填补）**  对任意 `p ∈ Q^{D+1}`，

    dim_Q span{ A(k,j)ᵀ p : k ≥ 0, 0 ≤ j < 2^k }  =  #DClose(supp p).

更强地，**单个 `j` 就够**：取 `m` 使 `w(2^m)` 全非零（引理 4 给 `m ≤ T ≤ A(A+1)`；
整数 `p` 时引理 4′ 给 `m = A+1+⌈log₂B⌉` 也行），令

    j = 2^m ,      k = m+1, m+2, …, m + #DClose(S)

则这 `#DClose(S)` 个向量 `A(k,j)ᵀp` **线性无关**，张成 `span{e_l : l ∈ DClose(S)}`；少取一个 `k` 就掉一维。

*证明.* 上界 (C2)；下界 = 引理 3 + 引理 4（或 4′）。∎

**数值复核**（脚本 [4]，全部精确消元）：

    (4a) exhaustive p in {-1,0,1}^{D+1}:  D=4 243 例 0 不符, D=5 729 例 0 不符
    (4b) 300 random p (deg<=9, |coef|<=9, K=6): 0 不符; K=6 vs K=7 稳定 30/30
    (4c) single-j 判据: 2400 例 0 反例
    (4d) explicit family j=2^m, k=m+1..m+#DClose: 400/400 达到 #DClose
         min m over all cases = 1 ; bound A+1+ceil(log2 B) satisfied in 400/400
         at m = A+1+ceil(log2 B) full support: 250/250
         120/120 "紧": 去掉一个 k 就掉一维
    (4d') root-counting bound: 300/300 ; 对抗例 bad m = [0,1,2], 最小好 m = 3, A_0(A_0+1)/2 = 6
    (4e) supp(Aᵀp) ⊆ DClose(supp p): 15240 个向量 0 反例

一个完整的例子（`p = 1 − 3x^2 + x^4`，`S = {0,2,4}`，`#DClose = 3`）：

    m=0  j=1    k=[1, 2, 3]  rank=3
    m=1  j=2    k=[2, 3, 4]  rank=3
    m=2  j=4    k=[3, 4, 5]  rank=3
    m=3  j=8    k=[4, 5, 6]  rank=3

> **一个自然的坑（本轮真栽过）**：既然两个奇偶类都要各自 `A_ε+1` 个 `k` 的 Vandermonde，
> 而同一个 `j` 的同一族 `k` 要同时服务两类，那么取的 `k` 个数必须是 `(A_0+1)+(A_1+1) = #DClose`，
> **不是** `max(A_0,A_1)+1`。用 `A+1` 个 `k` 时矩阵只有 `A+1` 行，秩被行数卡死
> （例如 `A_0 = A_1 = 5` 时秩恒为 6，而正确值是 12）。这解释了为什么"单个 `j` 就够"必须配 `#DClose` 个 `k`。

---

## 6. 猜想 A 现在是定理

把定理 5 与 docs/55 定理 1（`rank₂(Z_c) = dim span{Aᵀp} + [δ≠0]`）拼起来：

**定理 6（精确秩公式）**  设 `c ∈ Q[x]`，`p = c(x)+c(x−1)`，`S = supp p`，`δ = c(0)+c(1)−p(1)`。则

    rank₂(Z_c) = #DClose(S) + [δ ≠ 0]
               = (A_0+1) + (A_1+1) + [δ≠0],      A_ε = ⌊max(S_ε)/2⌋.

【已证】（定理 5 + docs/55 定理 1；后者的三行证明用到 Lean 已证的分解/偶步/奇步/中心律）。

**端到端数值复核**（脚本 [5]，**完全独立的一条代码路径**：直接用 shell 定义
`Z_c(t) = Σ_{x ∈ arm(t)}(c(x)+c(x−1))` 求值，再做精确有理消元，K=6、M=20）：

    census: 825 layer functions (deg<=3 exhaustive |coef|<=2, plus random and
            centre-corrected),  K=6, M=20
      rank_2(Z_c) == #DClose+[delta!=0] : 825/825   (mismatches 0)
      examples with a parity gap (#supp < #DClose): 86, of which the naive
      #supp+[delta!=0] formula fails: 86

即：`#supp < #DClose` 的 86 个例子中，朴素公式 86 个全错，精确公式 825 个全对。
这与 docs/55 的 1016 例（K≤7、M=40）方向一致，规模小一些但代码路径更短。

---

## 7. 与任务建议路线的对照

| 任务建议 | 本轮结论 |
|---|---|
| 1. 单点 `p = e_i`：`{Aᵀe_i}` 张成维数应为 `⌊i/2⌋+1`；"单个 bit=1 时 `A = M1`，`M1ᵀe_i` 已经覆盖整条链" | **成立**，但要说清：覆盖整条链只给 `dim ≥ 1`；必须补上 `k`-伸缩的 Vandermonde（`j = 1` 固定，`k = 1..⌊i/2⌋+1`）才得到 `⌊i/2⌋+1`。上界由列公式，故等号成立。见第 4 节 |
| 2. 一般 `p`：为什么加权后仍张满（不是并集，加权组合会变）；给显式 `(k,j)` 集合并证线性无关 | **证掉了**，而且比预期强：`(k,j)` 只需**一个 `j = 2^m` 加 `#DClose` 个连续 `k`**。关键是引理 1 的因子化——`k` 只做行/列伸缩、`j` 只定权重模式；权重是行伸缩，Vandermonde 不受影响。唯一的真实内容是"选 `j` 使权重全非零"，用根计数（引理 4）或 2-adic 主导（引理 4′）保证存在。见第 5 节 |
| 3. 证不出来就给精确缺口描述 | 不需要了；无最小反例（定理）。**遗留**：Lean 形式化【未做】 |

**为什么"取不同的 `(k,j)` 让组合系数变化"这条直觉会误导**：
在 `A(k,j)ᵀp` 里，`j` 只改变 `(Aᵀp)` 各坐标的**相对权重**，`k` 只做**对角伸缩**。
两族参数都不改变"哪一类线性组合"的结构，所以独立的来源从来不是"`j` 很多"，
而是"`k` 上节点 `2^{(2a+ε)k}` 互异"。反过来，`j` 的唯一作用是**制造/破坏零坐标**（见 5.1、5.2 的对抗例）。

---

## 8. 强度标注、可形式化点、遗留

**标为【已证】的（纸面证明，本轮脚本逐条数值核对）**

1. 引理 1（显式元素公式，EGF + arm 递归）；
2. 引理 2（奇次消失、`S_j(0)=2^{wt j}`）；
3. 列公式与上界 `dim ≤ #DClose`；
4. 引理 3（单 `j` 判据，根计数）；
5. 引理 4 / 4′（好 `m` 的存在性，两种界）；
6. 定理 5（主定理）与定理 6（猜想 A）。

**唯一的外来输入**：docs/55 定理 1（秩 = 向量张成维数 + `[δ≠0]`）。
它本身是纸面 3 行 + 四条 Lean 引理，本轮没有重证，但其数值后果（825/825）本轮独立复核过。

**形式化路线（【未做】）**，按代价从低到高：

1. 引理 1 → 纯多项式/生成函数恒等式，`S_j` 用子掩码求和定义，Lean 里 `Finset` 上可做；
2. 引理 2 → `m ↦ j−m` 的双射，一行；
3. 引理 3 → 需要"次数 < 根数 ⇒ 零多项式"，Mathlib 有 `Polynomial.card_roots`；
4. 引理 4 → "`W_a` 次数 = `A_ε − a`" + 根数上界，一行组合计数；
5. 定理 5 → 上面 4 条 + 线性代数（`rank`/`span` 的基变换），Mathlib 的 `Matrix.rank` 够用；
6. 定理 6 → docs/55 定理 1 的形式化（那才是真正的工作量：`X_iterate`、`W_eq_A`、`Z_row_linear`、`zero_mem_digits`）。

**遗留**

* 非多项式层函数（docs/55 猜想 B `rank(Z_c) ≤ 2·rank(c)`、C′ 奇周期）本轮未触及；
* 本轮证明了"秩 = #DClose"，但没有解释"为什么几何上 `p` 总是稠密的"（docs/55 已指出 13 行真实几何都稠密）。

---

## 9. 复现

    py -3 scripts/330_rank_closure.py        # 约 9–11 秒，退出码 0

全部输出（节选，与上文表格一一对应）：

    [1] explicit-entry lemma   A(k,j)[i][l] = 2^{k l} C(i,l) S_j(i-l)
      (a) formula vs the M0/M1 product:  381 cases (D<=9, k<=6, all j<2^k), 0 mismatches
      (b) arm recursion arm(2^k n+j) = 2^k arm(n) + (j-2m):  713 cases, 0 mismatches
      (c) cocycle A(k1+k2, j1+2^k1 j2) = A(k1,j1)A(k2,j2):  225 cases, 0 mismatches

    [2] S_j(d) = sum_{m submask j} (j-2m)^d :  odd d vanish, S_j(0) = 2^{wt j}
      j < 4096, d <= 8: odd-d vanishing and S_j(0)=2^wt(j): 0 violations

    [3] single point p = e_i :  rank = floor(i/2)+1, one j is enough
      violations: 0

    [4] general p :   dim span{A(k,j)^T p} = #DClose(supp p)
      (4a) D=4: 243 vectors, 0 mismatches ; D=5: 729 vectors, 0 mismatches
      (4b) 300 random p, 0 mismatches;  K=6 vs K=7 stable on 30/30 spot checks
      (4c) equivalence 'single-j rank = #DClose  <=>  w(j) has full support' : 2400 cases, 0 violations
      (4d) explicit family reaches #DClose for every p : 400/400
           min m over all cases = 1 ; bound A+1+ceil(log2 B) satisfied in 400/400
           at m = A+1+ceil(log2 B) the vector w(2^m) has full support : 250/250
           #bad m <= A_0(A_0+1)/2 + A_1(A_1+1)/2 : 300/300
           120 vectors (maximal m-family) are tight: dropping one k drops the rank: 120/120
      (4e) 15240 vectors checked, 0 coordinates outside DClose

    [5] end to end from the raw shell definition:  rank_2(Z_c) = #DClose + [delta!=0]
      (5a) c(x)+c(x-1) = p is solvable for every p: 60/60 round trips
      rank_2(Z_c) == #DClose+[delta!=0] : 825/825   (mismatches 0)
      examples with a parity gap (#supp < #DClose): 86, of which the naive
      #supp+[delta!=0] formula fails: 86

    total time ~9-11 s

**本轮只新增两个文件**：[scripts/330_rank_closure.py](scripts/330_rank_closure.py)、
本报告 [docs/59-rank-closure.md](docs/59-rank-closure.md)。未改动任何已有文件。
