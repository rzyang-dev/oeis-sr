# OEIS × 符号回归：探索工作区

把 OEIS 全库（40 万条整数序列）解析成一个可查询的 SQLite 数据库，并盘点其中
**哪些数据可以被机器直接处理**，为后续的符号回归（symbolic regression）实验打底。

- 数据源：`C:\Users\ginger\oeisdata`（2026-10-27 快照，CC BY-SA 4.0）
- 核心产物：`oeis.db`（563 MB，40 万条序列 / 1783 万个整数项）
- 主报告：[docs/01-oeis-data-inventory.md](docs/01-oeis-data-inventory.md)（数据盘点）、
  [docs/02-relations-and-atoms.md](docs/02-relations-and-atoms.md)（序列关系与原子性）

## 快速开始

```python
import sqlite3

con = sqlite3.connect("oeis.db")

# 一条序列的项与偏移
aid, name, n0, terms = con.execute(
    "SELECT aid, name, offset1, terms FROM seq WHERE aid = 'A000045'"
).fetchone()
ys = [int(t) for t in terms.split(",")]
pairs = list(zip(range(n0, n0 + len(ys)), ys))   # [(0,0), (1,1), (2,1), (3,2), ...]

# 它记录的所有公式
for kind, text in con.execute(
        "SELECT kind, text FROM formula WHERE aid = ? ORDER BY idx", (aid,)):
    print(kind, "|", text)
```

## 目录结构

```
oeis.db                 # 解析后的 SQLite 数据库（主要产物）
oeisdb/
  internal.py           # .seq 内部格式解析器（也可单独 import 使用）
  db.py                 # 表结构与索引定义
scripts/
  01_survey_format.py   # 全库格式普查 -> reports/format_survey.*
  02_build_db.py        # 8 分片并行构建 oeis.db
  03_inventory.py       # 数据盘点统计 -> reports/inventory.json
  04_export_targets.py  # 按条件导出符号回归数据集（JSONL）
  05_verify_sample.py   # 用独立解析器抽查数据库与原文是否一致
  06_extract_statements.py  # 抽取 %N/%F/%C 中指向其他序列的陈述
  07_atoms.py           # 建定义图/恒等式图，计算原子性 -> reports/relations.json
  08_pdf_to_text.py     # 无依赖 PDF 取文本（用于读 arXiv 论文）
  09_relation_types.py  # 定义边按关系类型分类
  10_numeric_relations.py  # 用项值挖精确关系（相等/仿射/前缀和）
  11_verify_numeric.py  # 用 b-file 复核挖出的关系
  12_long_identities.py    # “前 14 项相同”的对在 b-file 上能一致多远
  13_pointwise_decompositions.py  # 搜索 a = b ± c / b·c 的精确分解
  14_equivalence.py     # 由数值关系建等价类 / 泄漏组
  15_benchmark_set.py   # 选取闭式基准集并打难度标签
  16_splits.py          # 按泄漏组切分 train/val/test
  17_baseline.py        # 有限差分 + Berlekamp–Massey 基线
  18_benchmark_report.py # 标记 C-finite / residual 并汇总
  19_export_benchmark.py # 导出 data/benchmark.jsonl
  20_eml_baseline.py    # EML level-2 对照基线（初步，负结果）
  21_hard_track.py      # hard track：binomial/factorial/sum 目标的基线失败率
  22_precursive.py      # P-recursive（holonomic）猜想器，第二层基线
  23_cascade.py         # 序列算子级联（前缀/差分/仿射），带留出验证
  24_pointwise_cascade.py  # 逐点组合级联（a = b ± c / b·c）
  25_templates.py       # 组合模板库（Bell / Catalan / Motzkin）
  26_precursive_high.py # 高阶 P-recursive 扫描，逐条落库
  27_formula_shapes.py  # 公式形状清单与集中度
  28_shape_difficulty.py # 形状 × 可解性映射
  29_long_window.py      # 长窗口（200 项）求解对照
  30_fingerprints.py     # 从 b-file 计算结构指纹（增长类/周期/位数）
  31_exact_census.py     # 全库精确结构普查（多项式 / 线性递推 / 非递推）
  32_construction.py     # 非 C-finite 序列的构造类型分类
  33_conditional_routing.py  # 条件频率的方法路由（样本外评估）
  34_failure_prediction.py   # 预测哪些目标值得尝试（AUC 0.847）
  35_routed_eval.py          # 端到端：固定顺序 vs 预测+路由（真实耗时）
  36_predict_construction.py # 只用项值预测构造类型
  37_routed_full.py          # 全量 hard 集上的路由实跑（8 分片）
  38_algebraic_gf.py         # 代数生成函数猜测（5/121，负结果为主）
  39_long_pass.py            # 高置信目标的 60 项窗口二遍扫描
  40_census_recheck.py       # 抽样复核普查的"非 C-finite"（长窗口 + 高阶）
  41_bench_routed.py         # routed 流程在 v0 基准上的对照（含 cheap-first）
  43_congruence_mining.py    # 全库同余挖掘（拉马努金式）
  44_congruence_depth.py     # p-adic 深度（重现拉马努金–Watson 到第 4 层）
  45_kernel.py               # p-核判据：区分自动/非自动同余
  46_kernel_growth.py        # p-核随层数是否饱和
  47_factor_explain.py       # 线性因子解释同余（636/4,560）
  48_divisor_mechanisms.py   # 除数机制（(n+c)/d）解释同余
  49_depth_transforms.py     # 关系边上的深度传播
  50_transform_depth.py      # 受控实验：哪些变换保持深度
  51_freshman_survey.py      # freshman's dream 预测器的批量验证（8/8）
  53_literature_search.py    # 用搜索 API 做文献核查
  54_closed_loop.py          # 候选构建 + 逐条文献检索
  55_verify_candidates.py    # 候选的 b-file 重算验证
  56_statement_lit.py        # 深度候选的陈述级文献检索
  57_statement_lit_z1.py     # Z={1} 候选的陈述级文献检索
  58_z1_periodic.py          # Z={1} 候选的 mod-5 周期性检查
  66_formula_validate.py     # 公式解析器的全库验证
data/
  sr_pool_sample.jsonl  # 500 条候选序列的示例导出
  benchmark.jsonl       # 2,891 条公式基准（含切分与难度标签）
  atom_core.csv         # 16,827 条被引用的原子序列（含直接/传递被引用数）
docs/
  01-oeis-data-inventory.md
  02-relations-and-atoms.md
  03-eml-paper-notes.md      # EML 算子论文的笔记与评估
  04-numeric-relations.md    # 数值关系挖掘：OEIS 的隐蔽派生层
  05-hidden-identities.md    # 隐藏恒等式与近重复：案例与证据
  06-formula-benchmark.md    # 无泄漏、按难度分层的公式基准（v0）
  07-hard-track.md           # hard track：真正的难度在组合结构里
  08-formula-shapes.md       # 公式空间的形状结构（形状优先的 SR）
  09-bfile-fingerprints.md   # 11 亿项的结构指纹：增长类预测可解性
  10-exact-census.md         # 全库精确结构普查：82% 不是线性递推
  11-constructions.md        # 15.5 万条非 C-finite 的构造分类与路由表
  12-where-to-invest.md      # 用预测缺口决定下一个方法投在哪里
  13-synthesis.md            # 项目总结与关键数字
  14-congruences.md          # 全库同余挖掘：4,560 条未记录候选
  15-mechanisms.md           # p-核机制分类：188 自动 vs 133 非自动
  16-freshman-dream.md       # 从 A338464 挖出的 freshman's dream 同余定理
  17-congruence-program.md   # 同余发现流水线总报告
  18-closed-loop.md          # 闭环验证：170 条三腿通过的候选
  19-a156886-proof.md        # A156886 同余的完整证明
  20-formula-parser.md       # 公式解析器：文法、求值、覆盖率
  21-automatic-census.md     # 全库自动序列普查（930 条严格 2-自动）
  22-automata-atlas.md       # 159 条自动序列的显式 DFA 图鉴
  23-automatic-sequences-note.md  # 自动序列普查：自包含笔记
  24-conjectures-decided.md  # 用自动机判定 OEIS 猜想（6 条）
  25-findings-summary.md     # 可发布成果摘要（给整理者）
  26-publication-draft.md    # 投稿材料完整稿
  27-oeis-submissions.md     # OEIS 评论投稿草案（六条）
  28-verification-manifest.md # Lean 验证清单（全部 EXIT:0，无 sorry）
  29-rule129-attempt.md      # Rule 129 中列：形式化尝试记录
reports/
  format_survey.txt/json
  inventory.json
  relations.json
  relation_types.json
  numeric_relations.json
  long_equal.json        # 981 对“前缀相同”序列的长期一致长度
  pointwise_hits.json    # 18,867 条逐点分解
  hard_track.json        # hard track 汇总
  precursive.json        # P-recursive 层结果
  cascade.json           # 序列算子级联结果
  pointwise_cascade.json # 逐点组合级联结果
  templates.json         # 组合模板命中
  routing.json           # 路由实验结果
  failure_prediction.json # 失败预测结果
  routed_eval.json       # 端到端路由实测
  routed_thresholds.json # 阈值-召回-算力曲线
  algebraic_gf.json      # 代数生成函数命中的目标
  paper.txt              # 论文 PDF 抽取的纯文本
build/                  # 构建时的分片数据库与日志（可删）
```

## 数据库速览

| 表 | 行数 | 内容 |
|---|---|---|
| `seq` | 400,725 | 每条序列一行：名称、项值、偏移、关键词、各类字段计数 |
| `keyword` | 684,412 | (序列, 关键词) 多对多 |
| `formula` | 543,748 | %F 公式行，带 8 类粗分类 + 猜想标记 |
| `xref` | 1,487,362 | %Y 交叉引用有向边 |
| `link` | 601,746 | %H 链接（b-file / OEIS 内部 / 外部 URL） |
| `program` | 549,006 | 计算该序列的程序块（Mathematica/PARI/Maple/...） |
| `attachment` | 279,970 | files/ 目录里的附件清单（含 24.5 万个 b-file） |
| `definition` | 87,078 | 定义边：A 的名称以定义方式引用了 B |
| `identity` | 195,088 | 恒等式边：A 的公式/评论把 A 表示为 B 的函数 |
| `numeric_relation` | 44,821 | 项值上的精确关系：equal / affine / prefix |
| `pointwise_decomposition` | 18,867 | a = b ± c / b·c 的精确分解（核心原子两两组合） |
| `seq_class` | 400,725 | 等价类与泄漏组（去重 / 分组切分用） |
| `bench` | 2,891 | 公式基准集（含公式、难度、切分、C-finite 标记） |
| `bench_result` | 2,888 | 基线的逐条结果 |
| `hard_bench` | 14,019 | binomial/factorial/sum 目标及基线失败标记 |
| `hard_solved` | 11,043 | 每条 hard 目标被哪个精确方法解出 |
| `seq_fingerprint` | 217,960 | 从 b-file 算出的增长类/周期/位数等指纹 |
| `seq_exact` | 189,847 | 全库精确结构普查：poly / cf / none |
| `construction` | 155,661 | 非 C-finite 序列的构造类型 |
| `routed_run` | 11,043 | 全量路由实跑：预测分、跳过、尝试次数、命中方法 |
| `hard_long` | 695 | 高置信目标的 60 项窗口二遍扫描结果 |

## 重建

```powershell
python scripts\02_build_db.py --jobs 8     # 约 4 分钟（8 分片）
python scripts\03_inventory.py             # 约 2 分钟（含 b-file 抽样校验）
python scripts\06_extract_statements.py    # 约 3 分钟（8 分片）
python scripts\07_atoms.py                 # 约 10 秒
```

需要 Python 3.11+，只用标准库。


## 本仓库说明

GitHub 仓库 [oeis-sr](https://github.com/rzyang-dev/oeis-sr)（私有）保存本工作区的
**代码、文档、数据派生结果与论文草稿**。以下内容因体积或授权原因不入库：

| 排除项 | 原因 | 重建方式 |
|---|---|---|
| `oeis.db`（826 MB） | 超出 GitHub 单文件 100 MB 限制 | `python scripts\02_build_db.py --jobs 8` |
| `nks/*.pdf`（187 MB） | Wolfram《NKS》原书 PDF，受版权保护 | 从 wolframscience.com 自取 |
| `reports/*.jsonl`（94 MB） | 8 分片扫描的中间产物 | 重跑对应 `scripts/*.py` |
| `lean/*.olean`（19 MB） | Lean 构建产物 | `cd lean; lake build` |
| `APIkey` | 个人 API 凭据 | 不入库，本地自备 |
| 各 `*.pdf` | 第三方论文 / 书籍 | 从 arXiv 等原站获取 |

数据源 `oeisdata`（2026-10-27 快照）与全部序列内容版权归 OEIS 基金会，
采用 CC BY-SA 4.0 授权；本仓库中的派生数据沿用同一授权。
