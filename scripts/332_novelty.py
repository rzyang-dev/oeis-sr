#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""332_novelty.py -- 新颖性档案：把本仓库的 Rule 129 / shell / SIGMA / Hyp 结果逐条对照 OEIS.

用法
----
  py -3 scripts/332_novelty.py              # 默认：离线核对（本地 OEIS 快照 + oeis.db + 仓库内 HTML）
  py -3 scripts/332_novelty.py --scan       # 追加「全库字面扫描」（约 10-15 分钟，400k 条）
  py -3 scripts/332_novelty.py --net        # 优先走 https://oeis.org 的 JSON 接口（无网络时自动回退）

设计约束
--------
* 只读：不写任何文件。
* 无网络、无快照时也能跑完，并干净地报告「无数据」，绝不编造条目内容。
* 所有 OEIS 引文都从数据里现取（不硬编码 comment 文本），取不到就打印「未能核对」。

输出分四块
----------
  [0] 数据源探测
  [1] 恒等式数值验证（我们自己的数学）
  [2] 逐条 OEIS 核对（任务清单 1-6）
  [3] 结论表（可安全声称 / 不能声称）
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from urllib.request import urlopen

try:                                    # Windows 控制台默认 cp936，避免中文/特殊字符崩
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = Path(__file__).resolve().parent.parent
SEQ_ROOTS = [
    Path(os.environ.get("OEIS_SEQ_ROOT", "")),
    Path(r"C:\Users\ginger\oeisdata\seq"),
    REPO / "oeisdata" / "seq",
    REPO.parent / "oeisdata" / "seq",
]
DB_CANDIDATES = [REPO / "oeis.db", Path("oeis.db")]
HTML_CANDIDATES = ["A267442.html", "A267417.html", "A267444.html", "A036987.html"]

KEYWORDS = [
    ("cellular/automaton", r"cellular|\bautomat"),
    ("Rule 129",           r"rule\s*129"),
    ("shell",              r"\bshell"),
    ("submask",            r"sub-?\s*mask"),
    ("hyperbinary",        r"hyper-?\s?binary"),
    ("Stirling",           r"stirling"),
    ("parity/mod 2",       r"parity|mod\s*2|odd entr|is odd|are odd"),
    ("neighbours equal",   r"neighbou?rs?\s+(?:are\s+)?equal"),
]


# --------------------------------------------------------------------------
# 0. 数据源
# --------------------------------------------------------------------------
class Source:
    def __init__(self) -> None:
        self.seq_root: Path | None = None
        self.db: Path | None = None
        self.conn = None
        self.html: dict[str, Path] = {}
        self.notes: list[str] = []

    def probe(self) -> None:
        for p in SEQ_ROOTS:
            if p and (p / "A000" / "A000001.seq").exists():
                self.seq_root = p
                break
        for p in DB_CANDIDATES:
            if Path(p).exists():
                self.db = Path(p)
                break
        for h in HTML_CANDIDATES:
            if (REPO / h).exists():
                self.html[h] = REPO / h
        if self.db is not None:
            try:
                self.conn = sqlite3.connect(str(self.db))
            except Exception as e:                       # pragma: no cover
                self.notes.append(f"oeis.db 打不开：{e}")
        if self.seq_root:
            n = sum(1 for _ in (self.seq_root / "A267").glob("A2674*.seq"))
            self.notes.append(f"原始快照 {self.seq_root}（A2674* 有 {n} 个 .seq 文件）")
        if self.db:
            self.notes.append(f"结构化快照 {self.db}")
        if self.html:
            self.notes.append("仓库内 HTML 快照：" + ", ".join(sorted(self.html)))
        if not (self.seq_root or self.db or self.html):
            self.notes.append("未发现任何本地 OEIS 数据（无 .seq 快照、无 oeis.db、无 HTML）")

    @property
    def has_data(self) -> bool:
        return bool(self.seq_root or self.db or self.html)

    # ---- 单条读取 ------------------------------------------------------
    def raw_lines(self, aid: str) -> list[str] | None:
        if not self.seq_root:
            return None
        p = self.seq_root / aid[:4] / f"{aid}.seq"
        if not p.exists():
            return None
        return p.read_text(encoding="utf-8", errors="replace").splitlines()

    def entry(self, aid: str) -> dict | None:
        """返回 {name, terms, offset, comments[], formulas[], src} 或 None。"""
        lines = self.raw_lines(aid)
        if lines:
            name, terms, off = "", [], None
            cs, fs = [], []
            for ln in lines:
                tag = ln[:2]
                body = ln[11:] if len(ln) > 11 else ""
                if tag == "%N":
                    name = body
                elif tag in ("%S", "%T", "%U"):
                    terms += [int(z) for z in body.split(",") if re.fullmatch(r"-?\d+", z.strip())]
                elif tag == "%C":
                    cs.append(body)
                elif tag == "%F":
                    fs.append(body)
                elif tag == "%O" and off is None:
                    try:
                        off = int(body.split(",")[0])
                    except ValueError:
                        pass
            return {"aid": aid, "name": name, "terms": terms, "offset": off,
                    "comments": cs, "formulas": fs, "src": "seq-snapshot"}
        if self.conn is not None:
            row = self.conn.execute(
                "select name, terms, offset1 from seq where aid=?", (aid,)).fetchone()
            if row:
                terms = []
                try:
                    terms = [int(x) for x in row[1].split(",")]
                except Exception:
                    pass
                cs = [t for t in self.conn.execute(
                    "select text from stmt where aid=? and field='C' order by idx", (aid,))]
                fs = [t for t in self.conn.execute(
                    "select text from stmt where aid=? and field='F' order by idx", (aid,))]
                return {"aid": aid, "name": row[0], "terms": terms, "offset": row[2],
                        "comments": [c[0] for c in cs], "formulas": [f[0] for f in fs],
                        "src": "oeis.db（stmt 表不全，仅部分 comment）"}
        h = self.html.get(f"{aid}.html")
        if h is not None:
            txt = re.sub(r"<[^>]+>", " ", h.read_text(encoding="utf-8", errors="replace"))
            txt = re.sub(r"\s+", " ", txt)
            return {"aid": aid, "name": "", "terms": [], "offset": None,
                    "comments": [txt], "formulas": [], "src": f"{h.name}（HTML 文本）"}
        return None

    def terms(self, aid: str) -> list[int] | None:
        e = self.entry(aid)
        return e["terms"] if e else None


# --------------------------------------------------------------------------
# 1. 我们的数学（全部可独立复算）
# --------------------------------------------------------------------------
def popcount(n: int) -> int:
    return bin(n).count("1")


def fusc(n: int) -> int:
    """Stern 序列 A002487 的递归版。"""
    a, b = 0, 1
    for bit in bin(n)[2:]:
        if bit == "0":
            b = a + b
        else:
            a = a + b
    return a


def rt(t: int) -> int:
    """r(t) = t - 2^floor(log2 t)（t = 0 时取 0）。"""
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))


def is_sub(u: int, m: int) -> bool:
    """u 是 m 的二进制子掩码。"""
    return (u & ~m) == 0


def shell(t: int) -> list[int]:
    return [d for d in range(t + 1) if is_sub((t - d) // 2, rt(t))]


def x_tv(t: int, v: int) -> int:
    """Rule 129（全体邻居相等）的闭式状态。t = 0 取初始条件。"""
    d = abs(v)
    if d > t:
        return 0
    if t == 0:
        return 1 if d == 0 else 0
    return 0 if is_sub((t - d) // 2, rt(t)) else 1


def sigma_set(d: int) -> list[int]:
    return [u for u in range(d + 1) if (u & ((d - u) // 2)) == 0]


def hyp(n: int) -> list[tuple[int, int]]:
    return [(u, h) for u in range(n + 1) for h in range(n + 1)
            if (u & h) == 0 and u + 2 * h == n]


def stirl2_row(n: int) -> list[int]:
    row = [0] * (n + 2)
    row[0] = 1
    for nn in range(1, n + 1):
        new = [0] * (n + 2)
        for k in range(1, nn + 1):
            new[k] = row[k - 1] + k * row[k]
        row = new
    return row[1:n + 1]


def match_sequence(S: list[int], T: list[int], max_shift: int = 4) -> tuple[bool, int] | None:
    """检查 S[i] == T[i - shift] 是否在可比较区间上成立。返回 (True, shift)。"""
    n = len(S)
    best = None
    for sh in range(-max_shift, max_shift + 1):
        lo, hi = max(0, sh), min(len(T), n + sh)
        if hi - lo < n - 2 or hi - lo < 8:
            continue
        if all(T[j - sh] == S[j] for j in range(lo, hi)):
            best = (True, sh)
            if sh == 0:
                return best
    return best


# --------------------------------------------------------------------------
# 2. 核对工具
# --------------------------------------------------------------------------
CHECKS: list[tuple[str, bool, str]] = []


def chk(label: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((label, bool(ok), detail))
    print(f"  [{'OK ' if ok else 'FAIL'}] {label}" + (f"   {detail}" if detail else ""))


def statements(e: dict) -> list[tuple[str, str]]:
    out = [("NAME", e["name"] or "")]
    out += [("C", c) for c in e["comments"]]
    out += [("F", f) for f in e["formulas"]]
    return out


def keyword_report(e: dict) -> None:
    print(f"   条目 {e['aid']}（来源 {e['src']}）")
    print(f"   %N {e['name'][:200] if e['name'] else '（无）'}")
    if e["terms"]:
        print(f"   前 16 项（offset {e['offset']}）：" + ",".join(map(str, e["terms"][:16])))
    st = statements(e)
    for label, pat in KEYWORDS:
        rx = re.compile(pat, re.I)
        hit = [f"        [{tag}] {txt[:190]}" for tag, txt in st if txt and rx.search(txt)]
        if hit:
            print(f"   * 命中「{label}」{len(hit)} 条：")
            for h in hit[:6]:
                print(h)
        else:
            print(f"   - 未命中「{label}」")


# --------------------------------------------------------------------------
# 网络（可选）
# --------------------------------------------------------------------------
def net_entry(aid: str) -> dict | None:
    try:
        url = f"https://oeis.org/search?q=id:{aid}&fmt=json"
        with urlopen(url, timeout=25) as fh:
            j = json.loads(fh.read().decode("utf-8", "replace"))
        e = j[0] if isinstance(j, list) else j["results"][0]
        return {"aid": aid, "name": e.get("name", ""),
                "terms": [int(z) for z in (e.get("data") or "").split(",") if z.strip().isdigit()],
                "offset": int(str(e.get("offset", "0")).split(",")[0]),
                "comments": e.get("comment") or [], "formulas": e.get("formula") or [],
                "src": "oeis.org (live JSON)"}
    except Exception:
        return None


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true", help="对全部 .seq 做字面扫描（慢）")
    ap.add_argument("--net", action="store_true", help="优先用 oeis.org 的 JSON 接口")
    args = ap.parse_args()

    src = Source()
    src.probe()

    print("=" * 78)
    print("[0] 数据源")
    print("=" * 78)
    for n in src.notes:
        print("  -", n)
    if args.net:
        print("  - 网络模式：先试 oeis.org，失败则回退本地")

    def get(aid: str) -> dict | None:
        if args.net:
            e = net_entry(aid)
            if e:
                return e
        return src.entry(aid)

    # ---------------- [1] 我们自己的恒等式 ----------------
    print()
    print("=" * 78)
    print("[1] 恒等式数值验证（与 OEIS 无关，纯自算）")
    print("=" * 78)
    N = 40
    chk("|shell(t)| = 2^popcount(t)  (t <= 60)",
        all(len(shell(t)) == 2 ** popcount(t) for t in range(61)),
        f"|shell(0..11)| = {[len(shell(t)) for t in range(12)]}")
    chk("fusc(d)+fusc(d+1) = fusc(2d+1)  (Stern 递归, d <= 60)",
        all(fusc(d) + fusc(d + 1) == fusc(2 * d + 1) for d in range(61)))
    chk("|SIGMA_d| = fusc(d)+fusc(d+1)  (d <= 60)",
        all(len(sigma_set(d)) == fusc(d) + fusc(d + 1) for d in range(61)),
        f"d=0..11 -> {[len(sigma_set(d)) for d in range(12)]}")
    chk("|Hyp(n)| = fusc(n+1)  (n <= 60)",
        all(len(hyp(n)) == fusc(n + 1) for n in range(61)),
        f"n=0..11 -> {[len(hyp(n)) for n in range(12)]}")
    chk("|SIGMA_d| = |Hyp(d)| + |Hyp(d-1)|  (d <= 50)",
        all(len(sigma_set(d)) == len(hyp(d)) + (len(hyp(d - 1)) if d else 0)
            for d in range(51)))
    rows = {n: sum(1 for k in stirl2_row(n) if k % 2) for n in range(1, 41)}
    chk("#{k: S2(n,k) odd} = fusc(n-1)+fusc(n)  (n <= 40)",
        all(rows[n] == fusc(n - 1) + fusc(n) for n in range(1, 41)),
        f"n=1..12 -> {[rows[n] for n in range(1, 13)]}")

    # 一维几何：c_0 = 1, c_d = 2
    Z1 = [sum(1 if d == 0 else 2 for d in shell(t)) for t in range(N)]
    ON1 = [2 * t + 1 - Z1[t] for t in range(N)]
    MID = [x_tv(t, 0) for t in range(N)]
    SHL = [len(shell(t)) for t in range(N)]
    chk("一维零点数 = 2^(1+wt t) - [t = 2^i-1]  (t <= 2000)",
        all(Z1t == 2 ** (1 + popcount(t)) - (1 if popcount(t + 1) == 1 else 0)
            for t, Z1t in ((t, sum(1 if d == 0 else 2 for d in shell(t))) for t in range(2001))),
        f"Z(0..11) = {Z1[:12]}")
    AA = [fusc(d) + fusc(d + 1) for d in range(N)]

    # ---------------- [2] 逐条核对 ----------------
    print()
    print("=" * 78)
    print("[2] 逐条 OEIS 核对")
    print("=" * 78)

    # ---- 条目 1：A267442 ----
    print("\n--- 条目 1：A267442 是不是 Rule 129 中心列 / 是否等于 {0,1,3,7,15,...} ---")
    e442 = get("A267442")
    if not e442:
        print("  【未能核对】无 A267442 数据。")
    else:
        keyword_report(e442)
        T = e442["terms"]
        chk("A267442 前 12 项 = 1,0,1,0,1,1,1,0,...", T[:12] == MID[:12],
            str(T[:12]))
        chk("A267442 与我们的中列 x_t(0) 逐项一致 (前 %d 项)" % min(len(T), N),
            T[:min(len(T), N)] == MID[:min(len(T), N)])
        zeros = [i for i, v in enumerate(T) if v == 0]
        print(f"    A267442 的零点位置：{zeros[:10]}")
        chk("零点位置 = {2^k - 1 : k >= 1} = {1,3,7,15,31,...}",
            zeros == [2 ** k - 1 for k in range(1, len(zeros) + 1)] and zeros[0] == 1,
            "注意：不含 t=0（A267442(0)=1）")
        a435 = src.terms("A043545")
        if a435:
            chk("A267442(n) = A043545(n) 对 n >= 1（OEIS 2016 年的『猜想』）",
                all(T[n] == a435[n] for n in range(1, min(len(T), len(a435)))))
        else:
            print("    【未能核对】A043545 无数据。")

    # ---- 条目 2：A001316 ----
    print("\n--- 条目 2：A001316（Gould, 2^popcount）是不是 |shell(t)| ---")
    e316 = get("A001316")
    if not e316:
        print("  【未能核对】无 A001316 数据。")
    else:
        keyword_report(e316)
        T = e316["terms"]
        chk("A001316 前 20 项 = 2^popcount(n)",
            T[:20] == [2 ** popcount(n) for n in range(20)], str(T[:20]))
        m = match_sequence(SHL, T)
        chk("我们的 |shell(t)| 与 A001316 在 offset 0 完全对齐",
            bool(m) and m[1] == 0, f"match={m}")

    # ---- 条目 3：A002487 / A007306 ----
    print("\n--- 条目 3：A002487（Stern）/ A007306 —— 注释里有没有 CA / shell / Rule 129 /")
    print("            子掩码 / hyperbinary / Stirling 奇偶 ---")
    for aid in ("A002487", "A007306"):
        e = get(aid)
        if not e:
            print(f"  【未能核对】无 {aid} 数据。")
            continue
        keyword_report(e)

    # ---- 条目 4：A008277 ----
    print("\n--- 条目 4：A008277（第二类 Stirling 三角）有没有 parity / mod 2 的记录 ---")
    e8277 = get("A008277")
    if not e8277:
        print("  【未能核对】无 A008277 数据。")
    else:
        keyword_report(e8277)
        alltxt = " ".join(t for _, t in statements(e8277))
        chk("A008277 条目内没有 parity/mod 2/odd 陈述",
            not re.search(r"parity|mod\s*2|\bodd\b", alltxt, re.I))

    # ---- 条目 5：A(d) 的 A 编号 ----
    print("\n--- 条目 5：A(d) = fusc(d)+fusc(d+1) 的 OEIS 编号与偏移 ---")
    e306 = src.entry("A007306")
    if not e306:
        print("  【未能核对】无 A007306 数据。")
    else:
        T = e306["terms"]
        m = match_sequence(AA, T)
        print(f"    A007306 前 16 项（offset {e306['offset']}）：{T[:16]}")
        print(f"    我们的 A(d) 前 16 项：{AA[:16]}")
        chk("A(d) = A007306(d+1)（即 A007306 前移一位；offset 0 的条目）",
            bool(m) and m[1] == -1, f"match={m}")
        chk("A(d) = A002487(2d+1)（A002487 的奇数位）",
            all(fusc(2 * d + 1) == fusc(d) + fusc(d + 1) for d in range(60)))

    # ---- 条目 6：全体邻居相等 / Rule 129 零计数 ----
    print("\n--- 条目 6：OEIS 里有没有『全体邻居相等』CA 或 Rule 129 零计数 ---")
    rule129: list[str] = []
    if src.conn is not None:
        rule129 = [r[0] for r in src.conn.execute(
            "select aid from seq where name like '%Rule 129%' order by aid")]
        print(f"    名称含『Rule 129』的条目（oeis.db）：{len(rule129)} 条")
        for r in src.conn.execute("select aid,name from seq where name like '%Rule 129%' order by aid"):
            print(f"      {r[0]}  {r[1][:110]}")
    elif src.seq_root:
        for p in sorted(src.seq_root.glob("A*/A*.seq")):
            head = p.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"^%N \w+ (.*Rule 129.*)$", head, re.M)
            if m:
                rule129.append(p.stem)
                print(f"      {p.stem}  {m.group(1)[:110]}")
    if not rule129:
        print("    【未能核对】无名称索引可用。")

    # 一维零计数：A071051 / A267447
    for aid, lab in (("A071051", "一维 OFF 计数（Rule 126 的 ON 计数）"),
                     ("A267447", "Rule 129 第 n 轮 OFF 格数"),
                     ("A267445", "Rule 129 第 n 轮 ON 格数")):
        e = get(aid)
        if not e:
            print(f"    【未能核对】无 {aid} 数据。")
            continue
        print(f"    {aid}（{lab}）：{e['name'][:100]}")
        T = e["terms"]
        if aid == "A071051":
            chk("我们的 Z_1D(t) 与 A071051 完全一致（offset 0）",
                T[:N] == Z1[:N], f"前 12 项 {T[:12]}")
            hit = ([f for f in e["formulas"] if "wt(n)" in f]
                   or [f for f in e["formulas"] if "A000120" in f])
            if hit:
                print(f"      A071051 已有闭式：{hit[0][:180]}")
        elif aid == "A267447":
            chk("Z_1D(t) = A267447(t) 对 t >= 1（t=0 差一次初值约定）",
                all(T[t] == Z1[t] for t in range(1, min(len(T), N))),
                f"A267447 前 12 项 {T[:12]}")
        else:
            chk("ON_1D(t) = A267445(t) 对 t >= 1",
                all(T[t] == ON1[t] for t in range(1, min(len(T), N))),
                f"A267445 前 12 项 {T[:12]}")

    # ---- 可选的全文扫描 ----
    if args.scan:
        print("\n--- 全库字面扫描（只读，约 10-15 分钟）---")
        if not src.seq_root:
            print("  【未能核对】没有 .seq 快照，无法扫描。")
        else:
            pats = [("Rule 129", r"rule\s*129"),
                    ("hyperbinary", r"hyper-?\s?binary"),
                    ("submask", r"sub-?\s*mask"),
                    ("all ... neighbours equal", r"all\s+(?:the\s+)?neighbou?rs?\s+(?:are\s+)?equal"),
                    ("both hyperbinary+Stirling", None)]
            hits: dict[str, list[str]] = {k: [] for k, _ in pats}
            n = 0
            for dirpath, _dirs, files in os.walk(src.seq_root):
                for fn in files:
                    if not fn.endswith(".seq"):
                        continue
                    n += 1
                    try:
                        txt = Path(dirpath, fn).read_text(encoding="utf-8", errors="replace")
                    except Exception:
                        continue
                    low = txt.lower()
                    for k, pat in pats:
                        if pat is None:
                            if "hyperbinary" in low and "stirling" in low:
                                hits[k].append(fn[:-4])
                        elif re.search(pat, txt, re.I):
                            hits[k].append(fn[:-4])
                    if n % 50000 == 0:
                        print(f"    ... {n} 条")
            print(f"    扫描 {n} 条 .seq")
            for k, _ in pats:
                v = sorted(hits[k])
                print(f"    {k:28s} {len(v):5d} 条 :: {' '.join(v[:20])}")

    # ---------------- [3] 汇总 ----------------
    print()
    print("=" * 78)
    print("[3] 汇总")
    print("=" * 78)
    ok = sum(1 for _, o, _ in CHECKS if o)
    print(f"  数值/对齐检查：{ok}/{len(CHECKS)} 通过")
    for label, o, detail in CHECKS:
        if not o:
            print(f"    未通过：{label}  {detail}")
    print("  判定口径：数值一致只说明『是同一个已知对象』，不等于定理；")
    print("            OEIS 未收录只说明『在本快照中未出现』，需配合文献检索。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
