# 61 新颖性档案：Rule 129 / shell / SIGMA / Hyp 逐条对 OEIS

> 目的：给投稿用。判断这批结果里哪些是**新的**，哪些只是**已知对象的重新解释**。
> 方法：本机 OEIS 原始快照（400,725 条 `.seq`，快照时间 2026-10-27T03:00:20-04:00）
> ＋ 全库字面扫描 ＋ 现场 API 抽查（`https://oeis.org/search?q=id:...&fmt=json`）。
> 脚本：`scripts/332_novelty.py`（离线可跑；`--scan` 追加全库扫描；`--net` 走网络）。
>
> 结论分级：【已证】/【数值验证】/【猜想】/【未做】，与仓库其它文档一致。

---

## 0 一句话结论

**我们的"对象"几乎全在 OEIS 里，"定理"不在。** 具体地：

* 中列 A267442、层大小 A001316、SIGMA 计数 A007306、一维零计数 A071051/A267447
  —— 这四条**都是已有条目**，其中两条（一维零计数的 2^{1+wt}−1 形式、SIGMA 计数 = Stirling 奇数项数）
  连**闭式**都已经被别人写进 OEIS（Sloane 2014、Cloitre 2004）。
* 真正的新意在**结构层**：几何无关闭式、shell 与几何无关、零点数 = Σ_{d∈shell(t)} c_d、
  SIGMA_d ≅ Hyp(d) ⊎ Hyp(d−1) 的**集合双射**，以及在 OEIS 中**完全没有对应条目**的二维计数。
* 最危险的一条：**"中列 = 2^k−1 指示"这件事，OEIS 在 2002 年就用交叉引用记录过**
  （A071035 的 `%Y Cf. A036987 (central column)`），只是 2016 年的 A267442 没有链接过去，
  于是又被当成猜想重提。**不能**把这当成我们的发现。

---

## 1 数据与方法

| 项 | 内容 |
|---|---|
| 本地快照 | `C:\Users\ginger\oeisdata\seq\A???\A??????.seq`，400,725 条，快照 2026-10-27 |
| 结构化库 | `oeis.db`（同源；`seq` / `keyword` / `stmt` 等表） |
| 现场核对 | `oeis.org/search?q=id:A267442&fmt=json` 等 9 条，逐字与快照一致 |
| 网络 | 直连 `oeis.org` 的 urllib / Invoke-WebRequest 失败（`基础连接已经关闭: 接收时发生错误`）；改走工作区 API 端点（`api-docs/`，`api.deepseek.com/v1/tools/{search,fetch}`）成功 |
| 全库扫描 | 对 400,725 个 `.seq` 文件做**字面**串匹配（非语义检索） |

注意：`oeis.db` 的 `stmt` 表**不全**（例如 A002487 记 `n_comments=62`，表里只有 15 条 `%C`）。
凡涉及"注释里有没有 X"的判断，一律以 `.seq` 原始快照为准，不用 `stmt` 表。

---

## 2 逐条结论表

| # | 条目 | OEIS 编号 | 现有内容摘要 | 我们是否新增 | 来源 |
|---|---|---|---|---|---|
| 1 | A267442 = Rule 129 中列？零点 = {2^k−1}？ | **A267442**（offset 0） | `Middle column of the "Rule 129" elementary cellular automaton...`；1,0,1,0,1,1,1,0,…；**0 条 comment**；唯一公式是 Mathar(2016) 的**猜想** `a(n)=A043545(n), n>0` | 对象：**否**（2016 年已有）。零点位置 = {1,3,7,15,31,…}（**不含 0**），不是"数列 {0,1,3,7,…}"本身 | [A267442](https://oeis.org/A267442) |
| 2 | A001316 = \|shell(t)\|？ | **A001316**（offset 0） | `Gould's sequence … a(n)=2^A000120(n)`；前 20 项 1,2,2,4,2,4,4,8,… 与 \|shell(t)\| **完全一致** | 数值：**否**（就是 A001316）。“层大小”这个**解释**是新的 | [A001316](https://oeis.org/A001316) |
| 3a | A002487（Stern）注释 | **A002487** | **已有 hyperbinary**：`a(n+1) is the number of … hyperbinary representations of n [Carlitz; Lind]`；**已有 Stirling 奇偶**：`a(n) is the number of odd Stirling numbers S_2(n+1, 2r+1) [Carlitz]`；**无** CA / Rule 129 / shell / submask | 计数：**否** | [A002487](https://oeis.org/A002487) |
| 3b | A007306 注释 | **A007306**（offset 0） | **已有 Cloitre 2004-02-28**：`Also number of odd entries in n-th row of triangle of Stirling numbers of the second kind (A008277)`；**无** hyperbinary / CA / shell / Rule 129 | 计数：**否** | [A007306](https://oeis.org/A007306) |
| 4 | A008277 的 parity 记录 | **A008277** | 28 条 comment + 52 条 formula，**没有任何 parity / mod 2 / odd 陈述**（脚本断言通过） | 位置：**否**——奇偶性记录在 A007306 / A002487，不在三角本身 | [A008277](https://oeis.org/A008277) |
| 5 | A(d)=fusc(d)+fusc(d+1) 的编号 | **A007306** | 见 3b。**A(d) = A007306(d+1)**（整体前移 1），也 = A002487(2d+1)（Stern 奇数位） | 编号：**否**（是 A007306 的平移） | [A007306](https://oeis.org/A007306) |
| 6 | "全体邻居相等" CA / Rule 129 零计数 | **A267417, A267440–A267448**（1D）；A270217–A270220, A279028/30（2D，**数值不符**） | 1D 零计数 = **A267447**（n≥1），其闭式早在 **A071051**（Sloane 2014-08-09）：`a(n)=2^(1+wt(n)) unless n is of the form 2^i-1 in which case we must subtract 1` | 1D 零计数：**否**。2D / 任意几何：**是**（OEIS 无对应） | [A071051](https://oeis.org/A071051) / [A267447](https://oeis.org/A267447) |

**"全体邻居相等"这个短语本身**：全库 400,725 条中，字面串 `all (the) neighbour(s) equal`
**零命中**（见附录扫描输出）；OEIS 一律叫 `Rule 129` / `Rule 126`。
`shell` 一词共 257 条命中，抽查均为物理/几何壳层（核壳层、晶格壳层、Shell sort 等），
未见我们的"层集"含义；`submask` 8 条命中抽查亦与"二进制子掩码"无关
（这些是**抽查**结论，不是逐条核对）。

---

## 3 逐条细节

### 3.1 条目 1：A267442 到底是什么

原始条目（`.seq`，与 live JSON 一致，rev 13，2025-02-16，作者 Robert Price, 2016-01-15）：

```
%N A267442 Middle column of the "Rule 129" elementary cellular automaton starting with a single ON (black) cell.
%S A267442 1,0,1,0,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,...
%F A267442 Conjecture: a(n) = A043545(n), n>0. - _R. J. Mathar_, Jan 17 2016
%Y A267442 Cf. A267417.
```

* **它不是** `{0,1,3,7,15,31,...}` 这个数列，也不是它的某个平移。
  它是"中心是否**活着**"的指示：`a(t) = x_t(0)`。
* 真正的对应关系是**零点位置**：`a(t) = 0 ⟺ t ∈ {1,3,7,15,31,63,…} = {2^k−1 : k ≥ 1}`。
  **t = 0 不在内**（`a(0)=1` 是初值，而我们的闭式在 t=0 会给出 0，这正是"公式对 t≥1 成立"的那一条边界）。
* 脚本给出：`A267442 的零点位置 = [1, 3, 7, 15, 31, 63]`，并且 `A267442(n) = A043545(n) (n ≥ 1)` 逐项成立。
* 上一轮的措辞"零点集合是 t = 2^k−1"方向正确，但**要说清是"零点位置"而不是"项值"**，并且**不含 0**。

**一个必须先讲清楚的历史**（对投稿至关重要）：

* **A071035**（2002，Hans Havermann，Rule 126 三角）的交叉引用里已经写着
  `Cf. A036987 (central column)`；
* **A036987** 的定义就是 `Characteristic function of A000225`（Zumkeller 2012），即 **1 ⟺ n = 2^k−1**；
* Rule 126 = 255 − 129，两者逐格互补，所以 `A267442 = 1 − A036987(n)`（n ≥ 1）。

也就是说，**这条事实 OEIS 在 2002 年就以"交叉引用"的形式记录过**，2016 年的 A267442 没有链接过去，
于是又被当成"猜想"重提。所以：

> 【已证】我们给出的是**第一个显式证明**（两条独立路线，且有 Lean 形式化），
> 但**不能**声称"发现了中列 = 2^k−1"。这句话的功劳属于 2002 年的 A071035 交叉引用。

### 3.2 条目 2：A001316 就是 |shell(t)|

* `%N A001316 Gould's sequence: … a(n) = 2^A000120(n)`，offset 0。
* 前 20 项：`1,2,2,4,2,4,4,8,2,4,4,8,4,8,8,16,2,4,4,8` —— 与 `|shell(t)|` **逐项相同**。
* 条目里已有的 CA 注释是 **Rule 90 / Rule 18** 的活细胞数（Branman 2009、Sloane 2009），**没有** Rule 129、没有 shell、没有 submask。

> 判定：`|shell(t)| = 2^{wt(t)}` 的**数学内容是 A001316 的标题**，不是新序列。
> 新的只是"它是 Rule 129 的**死层数**"这个解释——而这个解释在 A267447 / A071051 里已经以"OFF 格数"的形式出现了。

### 3.3 条目 3：Stern 与 Stirling —— 两座桥都已经在 OEIS 里

A002487 的原始注释（`.seq`）：

```
%C a(n+1) is the number of ways of writing n as a sum of powers of 2, each power being used
   at most twice (the number of hyperbinary representations of n) [Carlitz; Lind].
%C a(n) is the number of odd Stirling numbers S_2(n+1, 2r+1) [Carlitz].
```

A007306 的原始注释：

```
%C Also number of odd entries in n-th row of triangle of Stirling numbers of the second kind
   (A008277). - _Benoit Cloitre_, Feb 28 2004
```

**这就是任务里点名的 Cloitre 2004 那条**：它确实存在，而且正是"整行奇数项个数"。

数值复算（`scripts/332_novelty.py`）：

```
fusc(n)              : 0  1  1  2  1  3  2  3  1  4  3  5
#{k even: S2(n+1,k) odd} : 0  1  1  2  1  3  2  3  1  4  3  5
#{k odd  : S2(n+1,k) odd} : 1  1  2  1  3  2  3  1  4  3  5  2
fusc(n+1)            : 1  1  2  1  3  2  3  1  4  3  5  2
整行奇数项数 = fusc(n)+fusc(n+1) = A007306(n+1)   （n ≤ 30 验证）
```

（哪一半对应 fusc(n)、哪一半对应 fusc(n+1) 取决于 k 从 0 还是从 1 起编号；A008277 用 1-based，
所以"偶 k ↔ fusc(n)"。Carlitz 的注释只说了"一半"，总数由 Cloitre 补齐。）

全库字面扫描的一个副产品：**同时含 `hyperbinary` 与 `Stirling` 的条目只有 A002487 一条**
（400,725 条中的唯一一条）。也就是说，Stirling 奇偶与超二进制的桥在 OEIS 里**恰好**由这一条记录承载。

> 判定：**SIGMA_d 的计数不是新的**。`|SIGMA_d| = fusc(d)+fusc(d+1) = A007306(d+1) = 第 d+1 行
> Stirling 三角的奇数项个数`——这在 OEIS 里以两条相邻注释的形式存在了 20 年。
> 新的只能是**集合级**的双射 `SIGMA_d ≅ Hyp(d) ⊎ Hyp(d−1)`（计数层面是 Carlitz + Cloitre 的推论）。

### 3.4 条目 4：A008277 里**没有** parity 记录

* A008277（`Triangle of Stirling numbers of the second kind`，offset 1,5）：28 条 comment、52 条 formula；
* 其中**没有任何** parity / mod 2 / odd 陈述（脚本对全条目做了 `parity|mod\s*2|\bodd\b` 断言，通过）；
* 唯一的"奇偶邻居"是 `Also known as Stirling set numbers` 这类无关文字。

> 判定：**奇偶性的记录位置是 A007306（计数）与 A002487（半区计数），不是三角本身**。
> 如果我们要给 A008277 加一条 parity 评论，那是**补链**，不是发现。

### 3.5 条目 5：A(d) 落在哪里、偏移是多少

* `A(d) = fusc(d)+fusc(d+1)`，d = 0,1,2,…：`1,2,3,3,4,5,5,4,5,7,8,7,…`
* `A007306`（offset 0）：`1,1,2,3,3,4,5,5,4,5,7,8,7,…`
* 逐项对齐（脚本 `match_sequence` 给 `shift = −1`）：

  ```
  A(d) = A007306(d+1)      （整体前移一位）
  A(d) = A002487(2d+1)     （Stern 的奇数位；因 Stern 递归 a(2n+1)=a(n)+a(n+1)）
  ```

* **陷阱**：`A007306(0) = 1 = A(0)`，只看第 1 项会误判成"offset 0 完全一致"；
  从第 2 项起就错开（`A007306(1)=1`，而 `A(1)=2`）。**偏移是 1，不是 0**。
* 这条也解释了为什么 A007306 的 Cloitre 注释"偏移一位"地等于我们的 `|SIGMA_d|`。

> 判定：**不是新序列**，是 A007306 的平移（其本身又是 A002487 的奇数位）。

### 3.6 条目 6：Rule 129 与"全体邻居相等"

名称里含 `Rule 129` 的条目共 **16 条**（`oeis.db` 的 `seq.name` 匹配，与全库字面扫描一致）：

| 类别 | 条目 |
|---|---|
| 1D 三角 | A267417（`Triangle read by rows giving successive states … "Rule 129" …`，注释还写了 `also generated by Rule 161`） |
| 1D 整行 | A267440（二进制）、A267441（十进制） |
| 1D 中列 | **A267442**（0/1）、A267443（二进制）、A267444（十进制） |
| 1D ON 计数 | A267445（每轮）、A267446（累计） |
| 1D OFF 计数 | **A267447**（每轮）、A267448（累计） |
| 2D | A270217–A270220、A279028/A279030 |

**一维零计数早已有闭式**：

* A071051（2002 Havermann；2014 Sloane 加注）：`Number of ON cells at generation n of 1-D CA defined by Rule 126`
  且已有公式 `a(n) = 2^(1+wt(n)) unless n is of the form 2^i-1 in which case we must subtract 1`。
* 这正是我们的 `Z_{1D}(t) = 2^{1+wt(t)} − [t = 2^i−1]`，**逐字相同**。
* A267447 的 2016 年"猜想" `a(n) = A071051(n), n>0` 只是把这条闭式搬到 Rule 129 的语言里。

**二维**：A270217（2D Rule 129 的 ON 数）前 12 项是
`1,4,5,28,9,84,21,140,25,260,37,380`；
我们的 von Neumann "全同" ON 数是 `1,0,0,1,0,13,5,29,0,85,61,101` —— **完全不一致**。
二维的"Rule 129"用的是另一套（2D 规则编码）约定，**不是**我们的"全体邻居相等"规则。

> 判定：**一维零计数：已知**（A071051 / A267447）。**二维与任意几何的 `Σ_{d∈shell(t)} c_d`：OEIS 无对应**。

---

## 4 可以安全声称的新意

按"投出去最安全 → 最危险"排序：

1. **【已证】几何无关的闭式与计数归约。**
   对任意满足 (H1)–(H4) 的几何，
   `x_t(v) = 1 − [⌊(t−‖v‖)/2⌋ ⊆ r(t)]`，且 `#Z(t) = Σ_{d∈shell(t)} c_d`。
   OEIS 只有逐条几何的**数据**（且只覆盖一维与少数二维），**没有任何条目陈述这条定理**。
   ⚠️ 但必须在正文里写明：**一维特例的闭式 = A071051 的 Sloane 2014 公式**，我们不是第一个写下来的。

2. **【已证】shell 的结构性陈述**：`shell(t)` 与几何无关、`|shell(t)| = 2^{wt(t)}`、
   零集 = 各壳层之**无交并**。数值上 `|shell(t)|` 就是 A001316，所以只能声称"解释/结构"，
   不能声称新序列。

3. **【已证】集合级双射 `SIGMA_d ≅ Hyp(d) ⊎ Hyp(d−1)`。**
   计数层面（`= fusc(d)+fusc(d+1) = A007306(d+1)`）是 **Cloitre 2004 + Carlitz** 的推论，
   但"两个集合同构"不是 OEIS 的内容，也不是那两条注释的内容。**这是最结实的一条**。

4. **【已证】二维/高维的具体闭式**，例如 Moore 四分之一平面
   `#Z = 4·|subm(r(t))|·(t − r(t)) = 2^{1+wt(t)+⌊log2 t⌋}`。
   OEIS 的二维 "Rule 129"（A270217 等）**数值不符**，说明它不是我们的规则。**OEIS 中无对应**。

5. **【已证】A267442 的 Mathar (2016) 猜想成立**，可作为 OEIS 评论提交；
   但必须同时指出**A071035 (2002) 的 `%Y Cf. A036987 (central column)` 已经记录过同一事实**，
   我们的贡献是"证明 + 把断掉的链接接上"，不是"发现"。

6. **【术语】`shell` / `SIGMA` / `Hyp` 这套语言在 OEIS 中不存在**（`shell` 257 次命中抽查均为物理壳层，
   `submask` 8 次命中抽查无关）。术语是新的，但没有数学内容，不构成新颖性主张。

---

## 5 不能声称的（逐条，附证据）

1. **不能**说 A267442 是新对象 —— Robert Price, 2016-01-15 已收录。
2. **不能**说"中列零点 = 2^k−1"是发现 —— A043545 的 `%F` 明写 `a(n)=0 iff n = 2^m - 1`；
   A036987 的注释是 `Characteristic function of A000225`；A071035 (2002) 的 `%Y` 已把中列指向 A036987。
3. **不能**说一维零计数闭式是新结果 —— A071051, Sloane 2014-08-09：`a(n) = 2^(1+wt(n)) unless n is of
   the form 2^i-1 in which case we must subtract 1`，与我们的公式**逐字相同**。
4. **不能**说 `|shell(t)| = 2^{wt(t)}` 是新的 —— 那是 A001316 的标题（1899 Glaisher / Gould）。
5. **不能**说 Stern ↔ hyperbinary 的桥是新的 —— A002487 注释（Carlitz; Lind）。
6. **不能**说"SIGMA_d 计数 = Stirling 行奇数项数"是新的 —— A007306 注释（Cloitre 2004-02-28），
   半区版本在 A002487（Carlitz）。
7. **不能**说 A008277 里已有 parity 记录 —— 它**没有**；要加是"补链"，不是"发现"。
8. **不能**说"全体邻居相等"是 OEIS 的既有说法 —— OEIS 一律叫 `Rule 129`/`Rule 126`；
   这个短语在全库 400,725 条中**零命中**。反过来看，这既是术语空间，也提醒我们：**文献里可能也不这么叫**。
9. **不能**把"数值一致"写成"定理" —— 本档案里所有 `[OK]` 都是数值/对齐检查。

---

## 6 未能核对 / 局限

* **文献（非 OEIS）未检索**：arXiv / 期刊里 Rule 129 的闭式是否已发表，本次**未做**。
  `docs/31-rule129-literature.md` 记录过一次（arXiv `all:"rule 129"` 零结果），但那是别的轮次、别的时点，
  不能替代投稿前的正式检索。**这是本档案最大的缺口。**
* **网络**：直连 oeis.org 失败，全部 live 数据走工作区 API 端点取得；若端点策略变化，现场核对需重跑。
* **全库扫描是字面匹配**：把 "all neighbours equal" 写成 "unanimity rule"、"consensus rule" 的条目不会命中。
* **快照时点**：2026-10-27；此后新增的条目不在覆盖范围内。
* **二维结论**只做了"与 A270217 数值不符"这一条反面证据，没有穷举 OEIS 中所有二维 CA 条目。

---

## 7 建议的 OEIS 投稿（都可安全声称，且是"补链"而非"发现"）

| 目标条目 | 建议评论 | 依据 |
|---|---|---|
| A267442 | `a(n) = A043545(n) for n > 0.`（把 2016 的猜想标为已证）＋ `Equals 1 - A036987(n) for n >= 1; see the cross-reference in A071035.` | 本仓库 Lean `A267442_eq_A043545`；A071035 `%Y` |
| A267447 | `a(n) = A071051(n) for n > 0` 由 A071051 的闭式立得（该闭式见 A071051, Sloane 2014） | A071051 公式 |
| A001316 | （可选）`a(n) is the number of "dead levels" (shell size) of the "all neighbors equal" cellular automaton at time n.` | 本档案 3.2 |
| A007306 | （可选）`a(n+1) is the number of admissible offsets (SIGMA_n) in the "all neighbors equal" cellular automaton.` | 本档案 3.3 |

**不建议**给 A267442 提"我们发现中列 = 2^k−1"——会被编辑直接以 A071035 的交叉引用挡回来。

---

## 附录 脚本关键输出

`py -3 scripts/332_novelty.py`（离线，19/19 检查通过）：

```
[1] 恒等式数值验证（与 OEIS 无关，纯自算）
  [OK ] |shell(t)| = 2^popcount(t)  (t <= 60)   |shell(0..11)| = [1, 2, 2, 4, 2, 4, 4, 8, 2, 4, 4, 8]
  [OK ] fusc(d)+fusc(d+1) = fusc(2d+1)  (Stern 递归, d <= 60)
  [OK ] |SIGMA_d| = fusc(d)+fusc(d+1)  (d <= 60)   d=0..11 -> [1, 2, 3, 3, 4, 5, 5, 4, 5, 7, 8, 7]
  [OK ] |Hyp(n)| = fusc(n+1)  (n <= 60)   n=0..11 -> [1, 1, 2, 1, 3, 2, 3, 1, 4, 3, 5, 2]
  [OK ] |SIGMA_d| = |Hyp(d)| + |Hyp(d-1)|  (d <= 50)
  [OK ] #{k: S2(n,k) odd} = fusc(n-1)+fusc(n)  (n <= 40)   n=1..12 -> [1, 2, 3, 3, 4, 5, 5, 4, 5, 7, 8, 7]
  [OK ] 一维零点数 = 2^(1+wt t) - [t = 2^i-1]  (t <= 2000)   Z(0..11) = [1, 3, 4, 7, 4, 8, 8, 15, 4, 8, 8, 16]

[2] 逐条核对（节选）
  [OK ] A267442 前 12 项 = 1,0,1,0,1,1,1,0,...   [1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1]
  [OK ] A267442 与我们的中列 x_t(0) 逐项一致 (前 40 项)
    A267442 的零点位置：[1, 3, 7, 15, 31, 63]
  [OK ] 零点位置 = {2^k - 1 : k >= 1} = {1,3,7,15,31,...}
  [OK ] A267442(n) = A043545(n) 对 n >= 1（OEIS 2016 年的『猜想』）
  [OK ] A001316 前 20 项 = 2^popcount(n)
  [OK ] 我们的 |shell(t)| 与 A001316 在 offset 0 完全对齐   match=(True, 0)
  [OK ] A008277 条目内没有 parity/mod 2/odd 陈述
  [OK ] A(d) = A007306(d+1)（即 A007306 前移一位；offset 0 的条目）   match=(True, -1)
  [OK ] A(d) = A002487(2d+1)（A002487 的奇数位）
  [OK ] 我们的 Z_1D(t) 与 A071051 完全一致（offset 0）
  [OK ] Z_1D(t) = A267447(t) 对 t >= 1（t=0 差一次初值约定）
  [OK ] ON_1D(t) = A267445(t) 对 t >= 1
```

全库扫描（`--scan`，400,725 条 `.seq`）结果见下表（`py -3 scripts/332_novelty.py --scan`）：

```
    扫描 400725 条 .seq
    Rule 129                        16 条 :: A267417 A267440 A267441 A267442 A267443 A267444
                                              A267445 A267446 A267447 A267448 A270217 A270218
                                              A270219 A270220 A279028 A279030
    hyperbinary                     11 条 :: A000120 A000695 A002487 A005836 A033042 A125184
                                              A125186 A262097 A273513 A274515 A331128
    submask                          8 条 :: A225546 A303763 A303765 A303775 A304083 A396114
                                              A396728 A397434
    all ... neighbours equal         0 条 ::
    both hyperbinary+Stirling        1 条 :: A002487
```
