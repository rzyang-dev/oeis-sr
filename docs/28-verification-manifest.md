# Lean 验证清单（最终）

> 全部 10 个文件已从零顺序编译，EXIT:0，无 sorry。
> 编译方式：本地 Lean 4.34.1 + 已编译的 mathlib（LEAN_PATH 直接指向
> `.lake/packages/*/.lake/build/lib/lean`），不触发任何更新。

## 定理清单

| 文件 | 定理 | 陈述 | 公理 |
|---|---|---|---|
| OEIS.lean | `A267442_eq_A043545` | A267442 n = A043545 n, n ≥ 1 | propext, choice, Quot.sound |
| OEIS2.lean | `A217586_xor` | A217586 n = A096268(n-1) XOR A036987(n-1) | propext, Quot.sound |
| OEIS3.lean | `A285383_eq_A035263` | A285383 n = A035263(n-1) | propext, choice, Quot.sound |
| OEIS3.lean | `A284948_eq_A096268` | A284948 n = A096268(n-2) | propext, choice, Quot.sound |
| OEIS4.lean | `A306559_eq_A039982` | A306559(n+5) = A039982 n | propext, choice, Quot.sound |
| OEIS5.lean | `A270803_eq_A151666` | A270803 n = A151666(⌊(n+1)/2⌋), n ≥ 1 | propext, choice, Quot.sound |
| Conn.lean | `A043545_digits` | A043545 自动机 = 最大位 − 最小位 | propext, choice, Quot.sound |
| PdConn.lean | `A096268_pd` | A096268 自动机 = 周期倍增递推 | propext, choice, Quot.sound |
| FrConn.lean | `A036987_fr` | A036987 自动机 = 「2^k − 1 的指示」 | propext, choice, Quot.sound |
| Conn3.lean | `A035263_morphic` | A035263 自动机 = 形态词 0→11, 1→10 | propext, choice, Quot.sound |
| Conn4.lean | `A039982_morphic` | A039982 自动机 = 形态词极限 | propext, choice, Quot.sound |
| **R129.lean** | **`row_middle`** | **Rule 129 中列 = 2^k−1 指示（A267442 的定义）** | propext, choice, Quot.sound |
| R129.lean | `row_closed_form` | Rule 129 完整闭式 | propext, choice, Quot.sound |

## 编译验证记录

```
OEIS.lean EXIT:0
OEIS2.lean EXIT:0
OEIS3.lean EXIT:0
OEIS4.lean EXIT:0
OEIS5.lean EXIT:0
Conn.lean EXIT:0
PdConn.lean EXIT:0
FrConn.lean EXIT:0
Conn3.lean EXIT:0
Conn4.lean EXIT:0
VERIFY_DONE
```

命令（在 lean/ 目录）：

```powershell
$env:LEAN_PATH="C:\Users\ginger\my_math_project\.lake\build\lib\lean;
C:\Users\ginger\my_math_project\.lake\packages\mathlib\.lake\build\lib\lean;
... (其余依赖包) ..."
foreach ($f in $files) { lean.exe $f; echo $LASTEXITCODE }
```

## sorry 检查

`grep -r "sorry\|admit" lean/` 只命中 README 文字，**所有 .lean 文件中没有 sorry**。

## 辅助引理（未列在上表）

- `OEIS.lean`: `fold`, `fold_succ`, `fold_last`, `seq_eq_of_inv`（框架）
- `OEIS3.lean`: `shift_correct`, `enc2`, `shiftδ`, `shiftOut`（平移自动机）
- `OEIS5.lean`: `halveδ`, `halve_correct`, `halve_shift`（右移自动机）
- `Conn.lean`: `aut_spec`, `minDig_spec`, `maxDig_one`, `hasZero`, `hasOne`
- `PdConn.lean`: `fold_phi`, `fold_absorb`, `fold_two`（状态对称）
- `FrConn.lean`: `fold1`, `fold2`（吸收态分析）
- `Conn3.lean`: `w35_eq`（形态词与周期倍增的互补）
- `Conn4.lean`: `w39_odd/even/four/le`, `all_states`（七元联立归纳）

## 未完成项

- **无**。A267442 的定义连接已由 `R129.lean` 完成（Rule 129 中列 = 2^k−1 指示）。

## 新增（第 15 轮）

- `R129.lean`：777 行，EXIT:0，无 sorry，5 个定理，公理仅标准三条。