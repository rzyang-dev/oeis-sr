# 63 文献检索：我们的定理有没有人做过

> 方法：arXiv API（元数据：标题/摘要/comment）、web_search、OEIS（已由 docs/61 完成）。
> 没有检索：MathSciNet / zbMATH（无订阅）、Google Scholar（限流）、Wolfram NKS（书，无检索接口）。

---

## 0. 结论先行

**在 arXiv 的元数据检索下，我们没有找到任何与我们核心定理竞争的论文。**
最接近的是"线性 CA 的对称图案 → 奇异函数"这条线（arXiv:2203.05236、Martin–Odlyzko–Wolfram 1984），
它们处理线性规则（Rule 90 等），用代数/分形方法；我们的规则（Rule 129）是非线性的，
而且我们的结论是**几何无关的闭式**，不是渐近/极限函数。

**注意这个结论的强度**：arXiv 元数据检索的"0 命中"意味着"没有论文在标题/摘要里提过"，
不等于"没有人做过"。图元胞自动机（graph CA）与共识动力学（consensus dynamics）的文献
很多不在 arXiv，或不用这些词。所以下面逐条给的是【未找到】，不是【新】。

---

## 1. 检索记录

### 1.1 arXiv API（`https://export.arxiv.org/api/query`）

| 查询 | 命中数 | 相关条目 |
|---|---|---|
| `all:"rule 129"` | **0** | — |
| `all:"rule 126"` | 2 | "How to make dull cellular automata complex by adding memory: Rule 126 case study"；**"Cellular automata that generate symmetrical patterns give singular functions"** |
| `all:"unanimity" AND all:"cellular automaton"` | **0** | — |
| `all:"2-regular" AND all:"cellular automaton"` | **0** | — |
| `all:"Stern" AND all:"cellular automaton"` | **0** | — |
| `all:"submask"` | 1 | 无关（图像处理） |
| `all:"cellular automaton" AND all:"submask"` | **0** | — |
| `all:"elementary cellular automaton" AND all:"number of ones"` | **0** | — |
| `all:"elementary cellular automaton" AND all:"closed form"` | 1 | "Symmetric Nonlinear Cellular Automata as Algebraic References for Rule 30" |
| `all:"elementary cellular automata" AND all:"self-similar"` | 2 | "Renormalization of cellular automata and self-similarity"；"Discontinuous Riemann integrable functions emerging from cellular automata" |
| `all:"graph cellular automata" AND all:"consensus"` | 1 | "Dynamical Phase Transitions in Graph Cellular Automata" |

### 1.2 web_search

质量差（返回大量无关的 CA 教材/论文 PDF）。唯一有用的信号：
"Martin Odlyzko Wolfram, Algebraic properties of cellular automata (1984)" 反复出现 —— 那是线性 CA 的经典。

### 1.3 已知的（docs/31 早就查过）

- Wolfram Atlas 的 rule 129 页只有 GIF；
- StackExchange（math / mathoverflow / cs / mathematica）零命中；
- OEIS 的 rule 129 系列所有公式都还是猜想（A267442 的 Mathar 2016）。

---

## 2. 最接近的相关工作

| 文献 | 做什么 | 与我们的差别 |
|---|---|---|
| **Martin, Odlyzko, Wolfram (1984)**, *Algebraic properties of cellular automata* | 线性 CA 的极限集维数、代数性质 | **只处理线性（GF(2) 可加）规则**。Rule 129 非线性，其零集不是线性子空间；我们的方法（壳层/子掩码）与他们的代数方法无关。 |
| **arXiv:2203.05236**, *Cellular automata that generate symmetrical patterns give singular functions* | 线性 1D/2D ECA 从单点出发，归一化非零格数取极限，得奇异函数（处处连续、几乎处处导数为 0） | 他们做**极限函数**、线性规则；我们做**精确闭式 + 几何无关性 + 秩**。我们的 `S(N)=N^{log₂3}F(log₂N)` 与他们的"奇异函数"是同一种精神（自相似），但我们的自相似是**精确**的（`S(2N)=3S(N)`，Lean 已验证）。 |
| **Allouche & Shallit**, *Automatic Sequences* / k-regular 序列 | k-正则序列理论、核的有限生成 | 他们建**理论框架**；我们给出的是"CA 的零计数序列，其 2-kernel 秩 = 层函数的几何复杂度"这样一条**具体等式**。检索显示没人把 CA 与 kernel 秩这样连过。 |
| **Renormalization of cellular automata and self-similarity** | CA 的重整化/自相似 | 方法上是重整化群；我们是数位 DP。 |
| **Dynamical Phase Transitions in Graph Cellular Automata** | 图 CA 的相变 | 统计物理视角，不涉及闭式。 |

---

## 3. 逐条判定

| # | 我们的主张 | 判定 | 依据 |
|---|---|---|---|
| 1 | **几何无关闭式**：对任意满足 (H1)–(H4) 的层结构空间，`x_t(v) = 1 − [⌊(t−‖v‖)/2⌋ ⊆ r(t)]` | **未找到** | arXiv "rule 129" / "unanimity + CA" / "CA + radial" 全 0；OEIS 只有一维序列 A071051（2014） |
| 2 | **主定律** `#Z(t) = Σ_{d∈shell(t)} c_d`（零计数是层大小向量的线性泛函） | **未找到** | 无对应检索命中 |
| 3 | **对偶闭式** `d ∈ shell(t) ⟺ (s−1) ⊆ ⌊(s−1+d)/2⌋` | **未找到** | 这是我们自己的形式，未见任何文献 |
| 4 | 列分布 = `fusc(d)+fusc(d+1)` | **计数已知**（A007306 Cloitre 2004；A002487 Carlitz/Stirling）；**CA 解释未见** | docs/61 |
| 5 | **秩定理** `rank₂(Z_c) = #DClose(supp p) + [δ≠0]` | **未找到** | "2-regular + CA" 命中 0 |
| 6 | **分类**：256/256 几何无关、8 条非平凡 2-收缩、c=3 无解 | **未找到** | 无对应检索命中 |

---

## 4. 可安全声称的措辞（novelty statement 草稿）

> We give a closed form for the zero set of the "all neighbours equal" elementary cellular automaton
> (Rule 129) which is **independent of the underlying geometry**: it depends only on four abstract
> layer hypotheses, and consequently holds simultaneously for the line, for ℤ² with the von Neumann
> or Moore neighbourhood, and for the infinite binary tree. The proof yields a *master law*:
> the number of zeros at time `t` is a **linear functional of the layer-size sequence**, evaluated on
> a digit-defined set `shell(t)`. For linear rules the corresponding theory is algebraic
> (Martin–Odlyzko–Wolfram); Rule 129 is nonlinear and our method is combinatorial (submask/digit DP).
> As consequences we obtain an exact `2`-kernel rank formula for the zero-count sequences
> (`rank₂ = #DClose(supp(c(x)+c(x−1))) + [δ≠0]`), a census of all `256` layer-reducible rules
> (exactly eight non-trivial dyadic contractions, and no `c=3` analogue), and an exact
> self-similarity `S(2N)=3S(N)` for the cumulative level counts. Everything is formalised in Lean 4.

**不要写**：不能说"发现了 Rule 129 的中心列结构"（A071035 2002 已有）、
不能说"一维零计数闭式是首创"（A071051 Sloane 2014）、
不能说"Stern ↔ hyperbinary / Stern ↔ Stirling 奇偶是新桥"（A002487 注释里都有）。

---

## 5. 局限（必须随结论一起报）

1. **arXiv 元数据 ≠ 全文**。`all:` 只搜标题/摘要/comment。正文里提过 Rule 129 的论文不会被命中。
2. **没有 MathSciNet / zbMATH**（订阅墙）。这是最大的盲区 —— 组合/CA 的老论文很多只在那里。
3. **图 CA / 共识动力学** 的文献常用 "consensus", "voter model", "majority dynamics" 等词，
   我们只试了 consensus + graph CA 一条，命中 1 篇且不相关；这个方向值得再查。
4. **Wolfram NKS** 是书，没有可检索的 API；它可能讨论过"径向解"，需要人工翻。
5. Semantic Scholar API 被限流（"Too Many Requests"），只跑了 0 次成功查询。
---

## 6. NKS 本地全文检索（工作区有全书 PDF，我自己做的）

方法：工作区 `nks/` 下有 12 个正文章节 + 12 个 notes 章节的 PDF。没有 PDF 库可用
（`pypdf`/`fitz`/`pdfminer` 都没装），我写了一个基于 `zlib` 的最小提取器
（[scripts/336b_pdftext_all.py](scripts/336b_pdftext_all.py)）：解压 content stream → 抽 `(...)`
字符串 → 清洗。**共提取 9,834,471 字符**，存到 `nks/txt/`。
质量一般（图形流混进大量垃圾字节），但正文可检索。

### 6.1 关键命中：NKS 早就说过中列 = 2 的幂

第 11 章（两处，同一段落前后）：

> "…while rule 190 enumerates numbers that are multiples of 4.
> **And if one looks down the center column of the pattern it produces,
> rule 129 can be thought of as enumerating numbers that are powers of 2.**"

以及

> "…in the center column of rule 129 to powers of 2."

**所以"Rule 129 的中心列编码 2 的幂"这件事，Wolfram 2002 年就在书里写下了**（作为观察，不是证明）。
加上 A071035 在 2002 年的 `%Y` 交叉引用，这条事实在 2002 年被两个独立来源记录过，2016 年又被当猜想重提。

### 6.2 NKS 还有：Rule 129 的代数形式与"嵌套/分形"归类

- **代数形式**（p.884 的表，与 rules 0–255 并列）：
  抽取文本给出 `rule129:((pÒq)(pÒr))`（`Ò` = XOR；提取丢掉了上横线），
  即 `¬[(p⊕q) ∨ (p⊕r)]` = "三者全等"，与我们的规则一致。
- **归类**（第 3 章）：Rule 129 与 22、60、105、150、225 并列为
  "cellular automata that produce nested or fractal patterns"。

### 6.3 NKS 没有的

| 关键词 | 命中数 |
|---|---|
| `unanim` | **0** |
| `submask` | **0** |
| `closed form` | **0** |
| `radial` | **0** |
| `neighbour`（英式） | 0（全书用美式 `neighbor`，530 次） |
| `Stern` | 25 —— **全是假阳性**（"Western"、"Eastern"），**NKS 从未提到 Stern 序列** |

也就是说：NKS 有"这条规则的图案是嵌套/分形的""中列枚举 2 的幂"这些**定性观察**，
但**没有**：整条时空图的闭式、几何无关性、壳层/主定律、Stern 连接、2-kernel 秩、规则普查。

### 6.4 对新颖性台账的修正

| 主张 | 原判定 | 修正后 |
|---|---|---|
| 中心列零点 = `2^k−1` | "OEIS 2002 已记录" | **NKS 2002 也写了**（两个独立来源）→ 我们只有"第一个证明"，没有"发现" |
| 一维零计数闭式 | "A071051 2014" | 不变 |
| 几何无关闭式 / 主定律 / 秩定理 / 分类 | 未找到 | **不变**（NKS 完全没有这些） |
| Stern 连接 | "OEIS 注释里有" | 不变；额外确认 **NKS 没提过 Stern** |

---

## 7. 关于"DeepSeek 搜索端口"的说明

本机能拿到的两个通道：
- `web_search`（harness 提供）：可用，但**只返回 URL 列表，不返回综合正文**；对冷门数学话题噪声很大。
- `api.deepseek.com/v1/tools/search` 与 `/v1/tools/fetch`：端点存在，但**需要 API key**，
  在当前环境里直接调返回 `401 Authentication Fails (missing key)`。`$env:DSH_*` 里没有 key。
  如果要用，需要把 key 注入环境或提供一个本地代理。

本次检索实际走的路径是：`web_search` 找 URL → `web_fetch` 取（arXiv API、OEIS JSON、
arxiv abs 页都通）+ **本地 NKS 全文**。
### 7.1 搜索 API 的正确用法（已跑通）

工作区里有 `APIkey` 与 `api-docs/`。接口是 **POST + Bearer**：

```
POST https://api.deepseek.com/v1/tools/search
Headers: Authorization: Bearer <APIkey>, Content-Type: application/json
Body:    {"query": "...", "count": 6, "need_content": false}
```

`web_fetch` 只能 GET，所以必须用本机 POST（`py -3` + `urllib`，见
[scripts/340_dssearch.py](340_dssearch.py)、[scripts/341_ds_lit.py](341_ds_lit.py)）。
**质量明显好于 harness 的 `web_search`**：直接返回 title/url/summary，且能命中 OEIS 内部页与 NKS 页面。

### 7.2 用它跑出的新命中

- **A267444** "Decimal representation of the middle column of the Rule 129 ECA"；
- **A267445** "Number of ON (black) cells in the n-th iteration of Rule 129"，
  data `1,0,1,0,5,3,5,0,13,...` —— 我核对过：它就是 `2t+1 − Z(t)`（光锥内 ON 数），
  所以它也是我们闭式的推论，不是独立发现；
- **NKS 原文（带 URL）**：`wolframscience.com/nks/search/?q=...&p=55` 命中那句
  "rule 129 can be thought of as enumerating numbers that are powers of 2"。

### 7.3 12 条查询的结论

`unanimity rule CA` / `k-regular + CA` / `CA closed form submask` / `Rule 129 中列 2 的幂 证明` /
`A071051` / `graph CA consensus` / `CA radial tree` / `Stern + CA` / `"all neighbours equal"` /
`CA tree lattice same pattern` / `zero set ECA digit condition` / `A267444`

→ **没有任何一条命中与我们核心定理竞争的论文**。
命中最多的是 Allouche–Shallit 的 k-正则理论（框架，不含 CA 计数），
以及共识/多数票动力学的教材材料（无闭式）。
（Rule 30 方向有几篇 Zenodo 预印本自称"closed form"；与我们的规则无关。）
