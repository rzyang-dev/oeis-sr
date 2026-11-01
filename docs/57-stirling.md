# 57 Stirling 数 mod 2：这条桥不是巧合，是同一串符号

> 承接 docs/52（Stern 定理）、docs/53 §1（Stirling 桥，那里写"尚未做"）、
> docs/58 诚实清单（那里把这条桥标成"**只是数值**（d ≤ 199）"）。
> 本轮把它从数值巧合升级为**定理**，而且升级的方式比预期强：
> 两侧不是"计数相等"，而是**逐元素、逐比特的同一条判据**。
>
> 一句话：
> **令 u = n − k。第二类 Stirling 数奇偶性的位与判据 (n−k) & ⌊(k−1)/2⌋ = 0，
> 换元后与死寂偏移判据 u & ⌊(d−u)/2⌋ = 0 是同一串符号。**
> 于是 {k : S(d+1,k) 奇} = {d+1−u : u ∈ Σ_d} 是**集合相等**（显式双射 k ↦ d+1−k），
> A007306 的 Cloitre 注释（2004）成为定理，而 Stern 序列在这条证明里完全不需要出场。

---

## 0. 结果一览

| # | 陈述 | 强度 |
|---|---|---|
| T1 | S(n,k) ≡ C(n−⌈(k+1)/2⌉, ⌊(k−1)/2⌋) (mod 2) | **【已证】**（本文 §4，生成函数 + Lucas） |
| T2 | S(n,k) 奇 ⟺ (n−k) & ⌊(k−1)/2⌋ = 0 | **【已证】**（本文 §4；与 Wikipedia 一致，见 §3） |
| T3 | {k ∈ [1,d+1] : S(d+1,k) 奇} = {d+1−u : u ∈ Σ_d}（集合相等） | **【已证】**（本文 §5，换元即得） |
| T4 | A(d) = \|Σ_d\| = #{k : S(d+1,k) 奇} = fusc(d)+fusc(d+1) = A007306(d) | **【已证】**（T3 + docs/52 定理 C） |
| T5 | #{k 偶 : S(n,k) 奇} = fusc(n−1)，#{k 奇 : S(n,k) 奇} = fusc(n) | **【已证】**（T3 + docs/52 §3 的 p/q） |
| T6 | S(2n,n) 奇 ⟺ n 是 fibbinary（n & (n≫1) = 0） | **【已证】**（T2 + §5.5 引理；Wikipedia 亦载） |
| T7 | 局部 2 状态数位判据在 Stirling 侧成立（Gray 码形式） | **【数值验证】**（d ≤ 1999，脚本 C12） |
| T8 | 以上一切在 n ≤ 2000 上零反例 | **【数值验证】**（脚本 323，2.9 s） |

本轮**没有**做的事：【未做】Lean 形式化；【未做】拿到同行评议的一级文献出处（见 §3.3）。

---

## 1. 三个层次的说法，强度递增

设 n = d + 1，u := n − k ∈ [0, d]。三条判据写在一起：

```
(CA 侧, docs/52 定理 B, Lean: mem_sig_iff)
    u ∈ Σ_d   ⟺   u & ⌊(d−u)/2⌋ = 0

(Stirling 侧, Wikipedia / 本文 T2)
    S(n,k) 奇  ⟺   (n−k) & ⌊(k−1)/2⌋ = 0

(换元 u = n−k, d = n−1)
    ⌊(k−1)/2⌋ = ⌊(n−1−u)/2⌋ = ⌊(d−u)/2⌋ ,   n−k = u
```

第二行与第一行在换元后**逐字符相同**。所以：

* **弱说法（原来只有这个）**：两边计数相等，d ≤ 199 数值验证 —— 巧合。
* **中说法**：两侧各有一个"数位/子掩码"刻画，两刻画等价 —— 需要证两个刻画。
* **强说法（本文）**：两个刻画是**同一个谓词**，中间只差一次改名。
  于是不需要"证明两个条件等价"，只需要**把 k 换成 n−k**；计数相等是集合相等的推论。

这也是本轮最有价值的产出：**桥是恒等式，不是定理**（一旦两侧判据都已知）。

---

## 2. (a) 大范围验证

脚本：`scripts/323_stirling_proof.py`（唯一新增 .py）。
方法：直接对 S(n,k) mod 2 做 DP —— 递推 `S(n,k) = S(n-1,k-1) + k*S(n-1,k)`，
mod 2 后 `k*S` 这一项只在 k 为奇数时留下。两套**独立实现**：

1. 逐行整数数组 DP（字面递推，O(n²) 个 bit）；
2. 整行打包成一个 Python 大整数：`R_n = (R_{n-1} << 1) XOR (R_{n-1} & ODD)`。

两者逐行逐位比对（C10），n ≤ 2000 完全一致。

### 2.1 关键输出（`py -3 scripts/323_stirling_proof.py`，n = 2000，2.9 s）

```
[lucas] parity of C(z,w) via (w & z)==w vs math.comb, 0<=w<=z<=60 : violations = 0
[sigma] definition  u subset floor((u+d)/2)  vs  u & floor((d-u)/2)==0, d < 2000 : violations = 0

--- small table (d, SIGMA_d, odd k in row d+1) ------------------------
  d | |SIGMA_d| | SIGMA_d                    | {k : S(d+1,k) odd}
   0 |     1    | [0]                        | [1]
   1 |     2    | [0, 1]                     | [1, 2]
   2 |     3    | [0, 1, 2]                  | [1, 2, 3]
   3 |     3    | [0, 2, 3]                  | [1, 2, 4]
   4 |     4    | [0, 2, 3, 4]               | [1, 2, 3, 5]
   5 |     5    | [0, 1, 2, 4, 5]            | [1, 2, 4, 5, 6]
   6 |     5    | [0, 1, 4, 5, 6]            | [1, 2, 3, 6, 7]
   7 |     4    | [0, 4, 6, 7]               | [1, 2, 4, 8]
   8 |     5    | [0, 4, 6, 7, 8]            | [1, 2, 3, 5, 9]
   9 |     7    | [0, 1, 4, 5, 6, 8, 9]      | [1, 2, 4, 5, 6, 9, 10]
  10 |     8    | [0, 1, 2, 4, 5, 8, 9, 10]  | [1, 2, 3, 6, 7, 9, 10, 11]
  11 |     7    | [0, 2, 3, 4, 8, 10, 11]    | [1, 2, 4, 8, 9, 10, 12]
  12 |     7    | [0, 2, 3, 8, 10, 11, 12]   | [1, 2, 3, 5, 10, 11, 13]
  13 |     8    | [0, 1, 2, 8, 9, 10, 12, 13] | [1, 2, 4, 5, 6, 12, 13, 14]
  14 |     7    | [0, 1, 8, 9, 12, 13, 14]   | [1, 2, 3, 6, 7, 14, 15]
  15 |     5    | [0, 8, 12, 14, 15]         | [1, 2, 4, 8, 16]

--- checks --------------------------------------------------------------
  C1  #{k : S(n,k) odd} == |SIGMA_{n-1}|            (n <= 2000) : 0 violations
  C2  |SIGMA_d| == fusc(d)+fusc(d+1) == fusc(2d+1)  (d <= 1999) : 0 violations
  C3  {k : odd} == {n-u : u in SIGMA_{n-1}}  (as sets) (n <= 2000) : 0 violations
  C4  S(n,k) odd <=> (n-k)&((k-1)//2) == 0  (2001000 pairs)      : 0 violations
  C5  S(n,k) == C(n-ceil((k+1)/2),(k-1)//2) mod 2 (Lucas)   : 0 violations
  C6  #{k even: odd} == fusc(n-1), #{k odd: odd} == fusc(n) : 0 violations
  C7  S(2h,h) odd <=> h fibbinary           (h <= 1000)      : 0 violations
  C8  sum_{d<2^m} |SIGMA_d| == 3^m                 (m <= 10) : 0 violations
  C9  (m&a)==0 <=> m submask of m+a         (a,m <= 1200)     : 0 violations
  C10 two independent DP implementations agree  (n <= 2000)   : 0 violations
  C11 p(2e)=p(e), q(2e)=A(e), p(2e+1)=A(e), q(2e+1)=q(e)  : 0 violations
  C12 local digit rule  u & (gray(d)^(u>>1)) == u, u=n-k, d=n-1 : 0 violations
  C12b bit-by-bit local rule == closed Gray-code form (d<=599)  : 0 violations
  C13 GF identity x^k/prod(1-ix) reproduces S(n,k) (k<=8, n<=40) : 0 violations
  aux Lucas parity helper vs math.comb                        : 0 violations
  aux two SIGMA_d forms                                       : 0 violations

  max row n = 2000, (n,k) pairs checked = 2001000, A(d) computed for d <= 1999
  A(0..20)   = [1, 2, 3, 3, 4, 5, 5, 4, 5, 7, 8, 7, 7, 8, 7, 5, 6, 9, 11, 10, 11]
  #odd in rows 1..20 = [1, 2, 3, 3, 4, 5, 5, 4, 5, 7, 8, 7, 7, 8, 7, 5, 6, 9, 11, 10]
  fusc(0..20)        = [0, 1, 1, 2, 1, 3, 2, 3, 1, 4, 3, 5, 2, 5, 3, 4, 1, 5, 4, 7, 3]

  RESULT: ALL CHECKS PASSED   (total violations = 0, 2.9 s)
```

（表里能直接看出双射的形状：d = 7 时 Σ_7 = {0,4,6,7}，行 8 的奇 k = {1,2,4,8}，
正是 8 − {0,4,6,7}。）

### 2.2 加跑：n = 4000

`py -3 scripts/323_stirling_proof.py 4000` 同样全绿（10.8 s）：

```
  C1  #{k : S(n,k) odd} == |SIGMA_{n-1}|            (n <= 4000) : 0 violations
  C2  |SIGMA_d| == fusc(d)+fusc(d+1) == fusc(2d+1)  (d <= 3999) : 0 violations
  C3  {k : odd} == {n-u : u in SIGMA_{n-1}}  (as sets) (n <= 4000) : 0 violations
  C4  S(n,k) odd <=> (n-k)&((k-1)//2) == 0  (8002000 pairs)      : 0 violations
  C7  S(2h,h) odd <=> h fibbinary           (h <= 2000)      : 0 violations
  max row n = 4000, (n,k) pairs checked = 8002000, A(d) computed for d <= 3999
  RESULT: ALL CHECKS PASSED   (total violations = 0, 10.8 s)
```

### 2.3 各项检查在查什么

| 编号 | 内容 | 覆盖范围 |
|---|---|---|
| C1 | 计数：奇数个数 = \|Σ_{n−1}\| | n ≤ 2000 |
| C2 | Stern 闭式 \|Σ_d\| = fusc(d)+fusc(d+1) = fusc(2d+1) | d ≤ 1999 |
| C3 | **集合相等** {k : 奇} = {n−u : u ∈ Σ_{n−1}}（比计数强） | n ≤ 2000 |
| C4 | 判据 T2 逐点成立 | 2 001 000 个 (n,k) |
| C5 | Lucas 型二项式形式 T1 逐点成立 | 同上 |
| C6 | k 的奇偶把奇数个数切成 fusc(n−1) / fusc(n) | n ≤ 2000 |
| C7 | 中心 Stirling 数 T6 | h ≤ 1000 |
| C8 | 块质量 Σ_{d<2^m} A(d) = 3^m（S(2N)=3S(N) 的等价形式） | m ≤ 10 |
| C9 | 无进位引理 u & h = 0 ⟺ u ⊆ u+h（本项目 Lean `land_add_iff`） | a,m ≤ 1200 |
| C10 | 两套 DP 实现逐位一致 | n ≤ 2000 |
| C11 | Stern 递归在 Stirling 行上的四个等式 | n ≤ 2000 |
| C12/C12b | 局部 2 状态数位判据（Gray 码形式）与逐位规则 | d ≤ 1999 / 599 |
| C13 | 证明用的生成函数恒等式（精确整数幂级数求逆） | k ≤ 8, n ≤ 40 |

---

## 3. (b) 文献里的确切判据

### 3.1 Wikipedia 的 "Parity" 一节（两条陈述）

URL：<https://en.wikipedia.org/wiki/Stirling_numbers_of_the_second_kind>，小节 **Parity**。
（本机直连 en.wikipedia.org 被网络策略拒绝，本文读到的是同一篇文章的镜像
<https://handwiki.org/wiki/Stirling_numbers_of_the_second_kind>，正文一致。）

原文（英文照录）：

> The parity of a Stirling number of the second kind is same as the parity of a related
> binomial coefficient:
> `{n \brace k} ≡ C(z, w) (mod 2)`, where `z = n − ⌈(k+1)/2⌉`, `w = ⌊(k−1)/2⌋`.
> This relation is specified by mapping n and k coordinates onto the Sierpiński triangle.
>
> More directly, let two sets contain positions of 1's in binary representations of results
> of respective expressions:
> `A: Σ_{i∈A} 2^i = n − k`, `B: Σ_{j∈B} 2^j = ⌊(k−1)/2⌋`.
> One can mimic a bitwise AND operation by intersecting these two sets:
> `{n \brace k} mod 2 = 0` if `A ∩ B ≠ ∅`, `1` if `A ∩ B = ∅`,
> to obtain the parity of a Stirling number of the second kind in O(1) time.
> In pseudocode: `{n k} mod 2 := [((n − k) & ((k − 1) div 2)) = 0]`;
> where `[b]` is the Iverson bracket.

中文转述（两条，互为等价）：

* **(W1) 二项式形式**：`S(n,k) ≡ C(n − ⌈(k+1)/2⌉, ⌊(k−1)/2⌋) (mod 2)`。
* **(W2) 位与形式**：`S(n,k)` 奇 `⟺ (n−k) & ⌊(k−1)/2⌋ = 0`。
  （"A、B 分别是 n−k 与 ⌊(k−1)/2⌋ 的 1 位位置集，A ∩ B = ∅"，即位与为 0。）

同一节还给出一条推论：中心 Stirling 数 `S(2n,n)` 奇 ⟺ n 是 fibbinary
（二进制无相邻 1），该句带脚注 [13]。

**诚实说明**：这一节的前两段（W1、W2）在 Wikipedia 正文里**没有脚注/引用**
（脚注 [13] 只挂在后面关于中心 Stirling 的那句上）。因此 §4 给出自足证明，
不依赖任何未核实的文献。

### 3.2 OEIS

* **A007306**（name："Denominators of Farey tree fractions (i.e., the Stern-Brocot subtree in
  the range [0,1])"，等价于 `a(n) = fusc(2n+1)`）：注释原文（<https://oeis.org/A007306>）：

  > Also number of odd entries in n-th row of triangle of Stirling numbers of the second
  > kind (A008277). — Benoit Cloitre, Feb 28 2004

  这正是本任务要证的等式：`A007306(n) = #{k : S(n+1,k) 奇}`，而
  `A007306(n) = fusc(2n+1) = fusc(n)+fusc(n+1) = A(n)`。
  Cloitre 只给了观察，没有解释，也没有 CA 侧含义。

* **A008277**（第二类 Stirling 三角形，<https://oeis.org/A008277>）：条目里没有奇偶性公式，
  链接区有 Gosper 的 "Colored illustrations ... read mod 2" —— mod 2 图案是已知研究对象，
  但**没有**与本 CA 的联系。

### 3.3 没拿到的

【未做】本轮没有拿到同行评议的一级文献出处。检索中出现的可疑线索
（Lengyel 的 2-adic 系列、Adelberg 的 p-adic 论文、zbMATH 上 Lundell 的条目）
在本机网络下都打不开正文（见 §7 的抓取限制），所以只标注 Wikipedia + OEIS 两个
可核对 URL，并且**不依赖**它们（§4 是自足证明）。

---

## 4. (c) 判据的证明（自足，两步）

### 4.1 第一步：Lucas 型二项式形式（T1）

**命题.** 对 1 ≤ k ≤ n：`S(n,k) ≡ C(n − ⌈(k+1)/2⌉, ⌊(k−1)/2⌋) (mod 2)`。

**证明.**
(i) 标准生成函数（固定 k；由递推归纳，或由 "把 n 个球放进 k 个非空盒" 的指数公式）：

```
Σ_{n≥k} S(n,k) x^n  =  x^k / Π_{i=1}^{k} (1 − i·x)        (Z[[x]] 中的恒等式)
```

(ii) 模 2 化：i 偶时 `1 − ix ≡ 1`，i 奇时 `1 − ix ≡ 1 + x`；
`[1,k]` 中奇数有 `⌈k/2⌉` 个，故在 `F₂[[x]]` 中

```
Π_{i=1}^{k} (1 − i·x)  ≡  (1 + x)^{⌈k/2⌉} .
```

右式常数项为 1，在 `F₂[[x]]` 中可逆，故"取倒数 + 取系数"合法。

(iii) 负二项式级数（整数恒等式，模 2 后仍成立）：对 c ≥ 1，

```
(1+x)^{−c} = Σ_{j≥0} C(j + c − 1, c − 1) x^j .
```

取 `c = ⌈k/2⌉`、`j = n − k`：

```
S(n,k) ≡ C(n − k + ⌈k/2⌉ − 1, ⌈k/2⌉ − 1)  (mod 2),
```

而 `⌈k/2⌉ − 1 = ⌊(k−1)/2⌋`，且 `n − k + ⌈k/2⌉ − 1 = n − ⌈(k+1)/2⌉`
（因为 `k − ⌊(k−1)/2⌋ = ⌈(k+1)/2⌉`）。∎

> 数值核对：脚本 C13 用**精确整数**幂级数求逆重算 `x^k/Π(1−ix)`，
> 与真实 S(n,k) 在 k ≤ 8、n ≤ 40 上逐项相等（0 处不符）；C5 再把 (W1) 在
> n ≤ 2000 的全部 2 001 000 个 (n,k) 上模 2 核对通过。

### 4.2 第二步：位与形式（T2）

**定理.** 对 1 ≤ k ≤ n：`S(n,k)` 奇 `⟺ (n−k) & ⌊(k−1)/2⌋ = 0`。

**证明.** 记 `a = n−k`，`m = ⌊(k−1)/2⌋`。由 T1，`S(n,k) ≡ C(a+m, m)`。

* **Lucas 定理**：`C(z,w)` 奇 `⟺ w ⊆ z`（按位包含）。取 `z = a+m`、`w = m`。
* **无进位引理**（本项目 Lean 已证，`lean/Brocot.lean` 的 `land_add_iff`）：

```
m ⊆ m + a   ⟺   m & a = 0 .
```

两者相接即得。∎

> 这就是全部。两个输入都是标准工具：Lucas 定理（脚本把它的实现与 `math.comb`
> 在 `0 ≤ w ≤ z ≤ 60` 上对齐，0 处不符），以及无进位引理（脚本 C9 在
> `a, m ≤ 1200` 上重验，0 处不符；它在本项目里是 Lean 定理）。
> 注意这里**没有**出现 Stern 序列，也没有出现本 CA —— 判据是纯 Stirling 侧的。

---

## 5. (d) 与 SIGMA_d 的对照：同一条判据，一个双射

### 5.1 换元

d ≥ 0，n = d+1，k ∈ [1, n]，`u := n − k ∈ [0, d]`。则

```
(n − k) & ⌊(k−1)/2⌋
   =  u & ⌊(n − 1 − u)/2⌋
   =  u & ⌊(d − u)/2⌋ .
```

右端正是 docs/52 **定理 B**（Lean：`mem_sig_iff`）里 Σ_d 的刻画：

```
Σ_d = { u : u ≤ d,  u & ⌊(d−u)/2⌋ = 0 } .
```

### 5.2 桥定理（T3）

```
对每个 d ≥ 0：     { k ∈ [1, d+1] : S(d+1,k) 为奇数 }
                 = { d+1−u : u ∈ Σ_d }                        (集合相等)
```

映射 `k ↦ u = d+1−k` 是 `[1,d+1] → [0,d]` 的双射，且两侧谓词**逐字符相同**，
所以这不是"计数巧合"，是同一批数的两种叫法。取基数立刻得到

```
A(d) := |Σ_d| = #{ k : S(d+1,k) 为奇数 } .
```

再由 docs/52 定理 C（Lean：`card_sig_stern`）`|Σ_d| = fusc(d)+fusc(d+1)`：

```
#{ k : S(n,k) 为奇数 } = fusc(n−1) + fusc(n) = fusc(2n−1) = A007306(n−1) .
```

**Cloitre 2004 的注释由此成为定理**，并且第一次有了 CA 侧解释：

> "全体邻居相等" 元胞自动机在同一个 2-块内、距离 d 上死掉的时刻数，
> 等于第二类 Stirling 数第 d+1 行里奇数的个数 —— 因为两件事在数位上问的是同一个问题。

### 5.3 顺带：Stern 递归在 Stirling 行上的样子（T5）

docs/52 §3 把 Σ_d 按 `u + d` 的奇偶切成 `p(d), q(d)`。换元 `u = n−k`、
`d = n−1` 后：

```
u + d = (n−k) + (n−1) = 2n − 1 − k  ≡  k + 1  (mod 2),
```

所以 **p(d) = 第 d+1 行中 k 为偶数的奇数个数，q(d) = k 为奇数的奇数个数**：

```
P(n) := #{ k 偶 : S(n,k) 奇 } = fusc(n−1)
Q(n) := #{ k 奇 : S(n,k) 奇 } = fusc(n)
```

而 docs/52 §3 的四条递归在这一侧读作（脚本 C11 逐条核对，n ≤ 2000，0 处不符）：

```
p(2e) = p(e)      ⟺  P(2e+1) = P(e+1)
q(2e) = A(e)      ⟺  Q(2e+1) = P(e+1) + Q(e+1)
p(2e+1) = A(e)    ⟺  P(2e+2) = P(e+1) + Q(e+1)
q(2e+1) = q(e)    ⟺  Q(2e+2) = Q(e+1)
```

即 **Stirling 行的"奇数位置按 k 的奇偶分两半"直接复刻 Stern 的 2×2 幺模矩阵**。
这就是 docs/52 §4 那个"2 状态自动机 ⇒ 必然出现 Stern"在 Stirling 侧的对应物。

### 5.4 局部数位判据（T7，【数值验证】）

docs/52 §4 的局部判据（那里验证 d ≤ 500）：

```
u ∈ Σ_d  ⟺  ∀i: bit_i(u) = 1 ⟹ bit_{i+1}(u) ⊕ bit_{i+1}(d) ⊕ bit_i(d) = 1 .
```

搬到 Stirling 侧（u = n−k，d = n−1）并化简成闭式：令 `gray(d) = d ⊕ (d ≫ 1)`
（二进制反射 Gray 码），则逐位条件等价于

```
u  ⊆  gray(d) ⊕ (u ≫ 1)     即     u & (gray(d) ⊕ (u ≫ 1)) = u .
```

（两行证明：`bit_i(d) ⊕ bit_{i+1}(d) = bit_i(gray(d))`，
所以"在每个 u 的 1 位上，`u≫1` 与 gray(d) 的位相反"正是子掩码。）

脚本 C12 用它直接对 Stirling 奇偶性逐点核对（n ≤ 2000，0 处不符），
C12b 核对逐位形式与 Gray 形式一致（d ≤ 599，0 处不符）。
另外做了一次脚本外的一次性扫描：两种形式在 **d ≤ 20000** 上也完全一致（0 处不符）。
强度：**【数值验证】**（与 Σ_d 的等价性的纸面证明还没写）。

### 5.5 中心 Stirling 的 fibbinary 推论（T6）

由 T2 取 `k = n/2`（即 n = 2h）：`S(2h,h)` 奇 `⟺ h & ⌊(h−1)/2⌋ = 0`。而

**引理.** 对 h ≥ 1：`h & ⌊(h−1)/2⌋ = 0 ⟺ h & (h ≫ 1) = 0`（fibbinary）。

*证明.* 写 `h = 2^s·q`（q 奇）。
s = 0 时 `⌊(h−1)/2⌋ = (h−1)/2 = h ≫ 1`，同一条式子。
s ≥ 1 时 `⌊(h−1)/2⌋ = 2^{s−1}q − 1`：低 s−1 位全 1、第 s−1 位为 0、
s 位以上与 `2^{s−1}(q−1)` 相同；而 `h ≫ 1 = 2^{s−1}q = 2^{s−1}(q−1) + 2^{s−1}`
的第 s−1 位为 1、低 s−1 位全 0、s 位以上同 `2^{s−1}(q−1)`。h 的低 s 位全 0，
故两种取法交出的都只是 "h 与 `2^{s−1}(q−1)` 的交"。∎

这与 Wikipedia 所载（其脚注 [13]）一致；脚本 C7 在 h ≤ 1000 上核对，0 处不符。

---

## 6. 断在哪一步？—— 没有断

任务书里预备的"如果找不到联系"分支不需要用。但仍如实记录**尝试过并被否掉的候选判据**
（说明为什么必须走位与形式）：

| 候选判据 | 反例 | 结论 |
|---|---|---|
| `S(n,k)` 奇 ⟺ `(k−1) ⊆ (n−k)` | n=6,k=4：S=65 奇，但 3 ⊄ 2 | 否 |
| `S(n,k)` 奇 ⟺ `(k−1) & (n−k) = 0` | n=6,k=4：3 & 2 = 2，但 S 奇 | 否 |
| `S(n,k)` 奇 ⟺ `(n−k) ⊆ (n−1)` | n=16,k=3：13 ⊆ 15，但 S(16,3) 偶 | 否 |
| `S(n,k) ≡ C(n−1,k−1)` (mod 2) | n=7,k=6：S=21 奇，C(6,5)=6 偶 | 否 |
| `S(n,k)` 奇 ⟺ `k` 是 2 的幂 | 只在 n = 2^m 的行上成立 | 否（只是特例） |
| `(n−k) & ⌊(k−1)/2⌋ = 0` | —— n ≤ 4000 全验，0 反例 | **是**（T2，已证） |

"断点"只在一个工程位置：**没有拿到一级文献**（§3.3），以及 **Lean 未形式化**（§7）。
数学上没有断。

---

## 7. 结论强度与未做

| 项 | 强度 |
|---|---|
| T1 二项式形式（= Wikipedia W1） | **【已证】**（§4.1：生成函数 + 负二项式） |
| T2 位与判据（= Wikipedia W2） | **【已证】**（§4.2：Lucas + 无进位引理）；n ≤ 4000 数值 0 反例 |
| T3 桥：奇 k 位置 = {d+1−u : u ∈ Σ_d} | **【已证】**（换元，逐字符同一个谓词） |
| T4 A(d) = #{k : S(d+1,k) 奇} = fusc(d)+fusc(d+1)（Cloitre 注释） | **【已证】**（T3 + docs/52 定理 C，后者 Lean 已证） |
| T5 P(n)=fusc(n−1), Q(n)=fusc(n) | **【已证】**（T3 + docs/52 §3） |
| T6 中心 Stirling 的 fibbinary 判据 | **【已证】**（T2 + §5.5 引理） |
| T7 局部数位判据 / Gray 码形式 | **【数值验证】**：Stirling 侧 d ≤ 1999；与逐位规则一致 d ≤ 599；脚本外扫描 d ≤ 20000 一致 |
| T8 以上全部数值核对 | **【数值验证】**：n ≤ 2000（2 001 000 个 (n,k)）+ n ≤ 4000 加跑（8 002 000 个） |
| Lean 形式化 T1/T2/T3 | **【未做】**（路线见下） |
| 一级文献出处 | **【未做】**（本机网络限制） |
| OEIS 增补（给 Cloitre 注释补出处/证明） | **【未做】**（不在本轮交付范围） |

**建议的 Lean 路线**（若下一轮做）：

1. T1：先证有限版 `(Σ_{n≤N} S(n,k) x^n) · Π_{i≤k}(1−ix) ≡ x^k`（只需系数到次数 N，
   用 `Polynomial` 或自建系数列表即可），再模 2 化简 + 负二项式。
   这是**唯一**有技术风险的一步（形式幂级数在 Mathlib 里比较重）。
2. T2：需要 Lucas 定理。Mathlib 里若没有现成的 "C(n,k) 奇 ⟺ k ⊆ n"，
   走 `padicValNat` 或 `Nat.factorization` 路线自建；最后一步直接复用
   本项目 `land_add_iff`。
3. T3：几乎是一行 —— `Nat.sub_add_cancel` + `omega` 处理下标，
   谓词之间是定义相等。

---

## 8. 复现

```
py -3 scripts/323_stirling_proof.py          # n = 2000, 2.9 s, ALL CHECKS PASSED
py -3 scripts/323_stirling_proof.py 4000     # n = 4000, 10.8 s, ALL CHECKS PASSED
```

* 环境：Windows，`py -3`（本机 `python` 是坏的 Store 存根，不可用）。
* 依赖：只用标准库（`sys`, `time`, `math.comb`）。
* 脚本只读不写，不触碰 `lean/`，不改任何已有文件。
* 退出码 0 = 全部检查通过；非 0 = 有反例（会打印计数）。

---

## 9. 一句话总结

docs/58 的诚实清单把这条桥标成"只是数值"。现在它可以移到"定理"一栏，
而且理由比"证了一条计数等式"更强：

> **Stirling 数奇偶性的判据与 CA 死寂偏移的判据，是同一个位与条件换了变量名。**
> 桥不是被证明的，是被**认出来**的。
