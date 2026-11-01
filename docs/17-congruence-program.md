# 同余挖掘程序：从 64 万条命中到一个定理

> 这是"同余发现流水线"的总报告。分阶段细节见 [14-congruences.md](14-congruences.md)、
> [15-mechanisms.md](15-mechanisms.md)、[16-freshman-dream.md](16-freshman-dream.md)。

## 1. 流水线

```
b-files (24.5 万个)
  → 全库扫描：a(n) ≡ 0 (mod p) 的剩余类        646,143 条命中
  → 密度过滤（排除稀疏序列）                    79,934
  → 非 C-finite + 指数/阶乘增长                  6,712
  → 去掉 r=0（平凡因子）                         4,734
  → 条目原文未提及                               4,560 条 / 2,470 个序列
  → p-adic 深度 ≥ 3                              274 条 / 217 个序列
  → 非自动（p-核 ≥ 50）                           56 条 / 48 个序列
  → 逐条机制判定                                  1 条剩余
  → freshman's dream 定理                         0 条剩余
```

## 2. 机制清单

| 机制 | 判定方式 | 覆盖 |
|---|---|---|
| 线性因子 (a·n+b) | 整除检验 | 636 条 |
| 奇因子 / 除子 | (n+c)/d 整除 | 部分 |
| p-自动（Lucas 型） | p-核 ≤ 20 | 188 条 |
| 模形式 / eta / McKay | 名称与公式 | 17 条 |
| 代数生成函数 | 公式形式 | 12 条 |
| **freshman's dream** | 和集判据 | A338464 及同型 |

## 3. 定理

对 `a(n) = [x^n] S(x)^n`，设 `R_p` 是 S 的指数集模 p，则
`a(pm+r) ≡ 0 (mod p)` 当 r 不在 R_p 的 r 重和集里。

推论：A338464 的 `a(pm+1) ≡ 0` 当且仅当 2 是模 p 的二次非剩余（p ≡ ±3 mod 8）。
在 p = 3,5,7,11,13,17,19,23,29,31 上全部验证通过。

## 4. 反演

p=5 时 31 种可能的 R 只产生 5 种零点模式。对照 14,646 条有 mod-5 零点类的序列，
2,100 条与某种 R 的模式吻合；其中 **829 条与 A338464 的 {1} 模式相同**。

## 5. 深度与变换

- A000041 上逐层重现拉马努金–Watson 到第 4 层（599 mod 625）；
- 深度 4 只在 p=5 上出现（数据长度限制：p=7 的第 4 层需要约 12,000 项）；
- 逐点代数（乘、平方、2^n）保持深度；求和/差分/二项式变换破坏深度。

## 6. 局限

- 公式解析是瓶颈：能干净解析成 `[x^n]P(x)^n` 的只有个位数序列；
- 深度受 b-file 长度限制，p=7/11 的高层深度大多不可判；
- p-核判据只能"证明自动"，不能"证明非自动"（大核可能是大自动机）；
- 定理的框架已确认属于已知理论（Rowland–Yassawi 的对角线自动同余、Cartier 算子）；
  具体判据未检索到，但不能据此声称新颖。详见 [16-freshman-dream.md](16-freshman-dream.md) 第 8 节。

## 7. 文件

```
scripts/43_congruence_mining.py   全库扫描
scripts/44_congruence_depth.py    p-adic 深度
scripts/45_kernel.py              p-核
scripts/46_kernel_growth.py       核的饱和性
scripts/47_factor_explain.py      线性因子
scripts/48_divisor_mechanisms.py  除子机制
scripts/49_depth_transforms.py    关系边上的传播
scripts/50_transform_depth.py     变换保持深度
scripts/51_freshman_survey.py     定理的批量验证
scripts/52_invert_R.py            零点模式反演
```
