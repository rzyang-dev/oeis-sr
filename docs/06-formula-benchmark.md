# 一个无泄漏、按难度分层的 OEIS 公式基准（v0）

> 产物：`data/benchmark.jsonl`（2,891 条）、`bench` 表、`seq_class` 表、`reports/benchmark_summary.json`
> 复现：`02_build_db.py` → `10_numeric_relations.py` → `14_equivalence.py` → `15_benchmark_set.py` →
> `16_splits.py` → `17_baseline.py` → `18_benchmark_report.py` → `19_export_benchmark.py`

## 1. 基准是什么

2,891 条序列，每条满足：

- `%F` 里有一条**纯算术闭式**（只含数字、n、+ − × / ^），例如 `(10^n - 1)/9`；
- 至少 15 项，且带 b-file（用于外推验证）；
- 有专家写的公式作为 ground truth。

每条记录包含：`aid, name, expr, n0, terms, keywords, tier, ops, degree, split, class, leak_group`。

| 项目 | 数值 |
|---|---:|
| 条目数 | 2,891 |
| train / val / test | 2,024 / 434 / 433 |
| 泄漏组 | 2,501（同一组不跨集） |
| 难度 tier（按运算符数） | easy 175 / medium 973 / hard 1,743 |
| 代数类 | C_finite 2,772 / residual 116 |

## 2. 为什么要"泄漏组"

前一步发现 132 对序列在 b-file 上一致 ≥1000 项，还有 3 万对精确仿射/前缀关系。
如果按序列随机切分，测试集里会混进训练集的**仿射孪生**或**前缀和孪生**——
模型不需要理解任何东西就能"预测"。

因此切分单位不是序列，而是 `seq_class.leak_group`：把 exact-equal / affine / prefix
关系做并查集，得到 38.2 万个组。切分后检查：**跨组的条目数 = 0**。

## 3. 基线：纯线性代数能做到多少

给定前 20 项，预测后 30 项（来自 b-file），要求逐项精确相等：

| 方法 | 成功 | 说明 |
|---|---:|---|
| 有限差分（多项式，degree ≤12） | 1,056 | 精确整数运算 |
| Berlekamp–Massey（线性递推，order ≤12） | 2,694 成功 / 194 过拟合 | 有理数精确运算 |
| 二者合并（先多项式后递推） | **2,772 / 2,888 = 96.0%** | |

按切分：train 96.5% / val 95.2% / test 94.5% —— 三者一致，说明切分没有泄漏。
按 tier：easy 97.7% / medium 97.2% / hard 95.1%。

## 4. 关键发现：这是一个"地板"，不是"挑战"

**96% 的纯算术闭式序列是 C-finite**（常数系数线性递推），一个 60 行的
Berlekamp–Massey 就能精确外推。剩下的 116 条（4%）是：

- 高次多项式（degree 12–20，超出基线的阶数上限）；
- 含 `/n` 的有理函数（P-recursive，不是 C-finite）；
- `n^n`、嵌套指数这类非 C-finite 表达式。

结论：**以"纯算术闭式"为目标的项级公式发现，已经被经典线性代数解决**。
这也解释了为什么 EML 路线在这里前景有限：深度 ≤4 的 EML 树连乘法（K≈17）都装不下，
而 96% 的目标是 C-finite 序列，它们的 EML 表达只会更长。

真正有挑战的公式在 `closed_form` 之外：二项式、阶乘、分拆数、素数——
这些既不是 C-finite，也不是短 EML 表达式。

## 4.1 EML 对照（初步）

按论文第 4.3 节实现了 level-2 master formula（14 个实参数，`eml(x,y)=exp(x)-ln(y)`，
Adam + 有限差分梯度，1200 步，随机初始化），在 easy 档最简单的 5 条目标上试跑：

- 手工把参数设成已知解时，F ≡ 1 精确成立（说明表示没问题）；
- 从随机初始化出发，**0/5 恢复**，连常数序列 `a(n)=1` 都没收敛到；
- 作为对照，Berlekamp–Massey 在同一基准上 96%。

这与论文的结论一致：EML 的表达力不是瓶颈，"从随机初始化找到盆地"才是；
而 OEIS 的闭式目标绝大多数是 C-finite，EML 树的深度远超 4，梯度搜索更难。
结论：**EML 不适合作为这个基准的基线**，它适合的是"短初等函数"这个更小的子域。

## 5. 怎么用

```python
import json
for line in open("data/benchmark.jsonl", encoding="utf-8"):
    rec = json.loads(line)
    # rec["terms"] 是 a(n0), a(n0+1), ...
    # rec["expr"] 是 ground truth 公式
    # rec["split"] 和 rec["leak_group"] 用于无泄漏评估
```

评估协议（建议）：

1. 模型只看 `terms[:20]`，预测接下来 30 项；
2. 精确匹配计为成功；
3. 报告时**必须**说明基线（BM 96%），否则数字没有意义；
4. 按 `leak_group` 分组汇报，避免孪生泄漏。

## 6. 局限

- 只覆盖 `closed_form` 的 2,891/4,057 条；
- 评分是项级而非表达式级（模型可能用递推"作弊"，但这也是一种结构发现）；
- 三角形序列（tabl/tabf）与含函数的公式未纳入；
- 难度 tier 按运算符数划分，与实际难度相关性一般（C-finite 与否才是关键）。

## 7. 下一步

1. **加 hard track**：从 `binomial`/`sum`/`factorial` 公式里构造目标，那里才有非 C-finite 结构。
2. **表达式级评分**：解析 ground truth 的 AST，检查模型输出是否代数等价。
3. **EML 浅层拟合**作为对照基线（已做初步版，见 4.1）：需要更好的初始化/退火策略才公平。
