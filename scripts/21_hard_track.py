#!/usr/bin/env python3
"""Hard track: non-C-finite targets built from binomial / factorial / sum formulas.

Selection: sequences that have an 'a(n) = ...' formula containing binomial(),
factorial or a sum, at least 20 terms and a b-file.  Each is then probed with
the exact baselines; those that neither a degree-12 polynomial nor an order-12
linear recurrence can extrapolate form the hard subset.

    python scripts/21_hard_track.py
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "hard_track.json"
T, K = 20, 30
ATTR = re.compile(r"\s*-\s*_[^_]+_,.*$")


def clean(t: str) -> str:
    t = ATTR.sub("", t).strip().rstrip(".")
    t = re.sub(r"^a\(n\)\s*=\s*", "", t)
    return t.strip()


def poly_predict(vals, k, maxdeg=12):
    cols = [list(vals)]
    for deg in range(1, maxdeg + 1):
        prev = cols[-1]
        if len(prev) < 2:
            return None
        cols.append([prev[i+1]-prev[i] for i in range(len(prev)-1)])
        row = cols[-1]
        if len(row) >= 2 and len(set(row)) == 1:
            out = []
            for _ in range(k):
                cols[-1].append(cols[-1][-1])
                for j in range(len(cols)-2, -1, -1):
                    cols[j].append(cols[j][-1] + cols[j+1][-1])
                out.append(cols[0][-1])
            return out
    return None


def berlekamp_massey(s):
    C = [Fraction(1)]; B = [Fraction(1)]
    L = 0; m = 1; b = Fraction(1)
    for n in range(len(s)):
        d = sum(C[i]*s[n-i] for i in range(min(L, n)+1))
        if d == 0:
            m += 1; continue
        T = C[:]
        coef = d / b
        if len(C) < len(B) + m:
            C += [Fraction(0)] * (len(B) + m - len(C))
        for j, bj in enumerate(B):
            C[j+m] -= coef * bj
        if 2*L <= n:
            L = n + 1 - L; B = T; b = d; m = 1
        else:
            m += 1
    return C, L


def bm_predict(vals, k, maxorder=12):
    C, L = berlekamp_massey([Fraction(x) for x in vals])
    if L == 0 or L > maxorder or len(C) < L+1:
        return None
    out = [Fraction(x) for x in vals]
    for _ in range(k):
        n = len(out)
        out.append(-sum(C[i]*out[n-i] for i in range(1, L+1)) / C[0])
    return out[-k:]


_c = {}
def bfile(aid, limit=4000):
    if aid in _c: return _c[aid]
    p = DATA / "files" / ("A"+aid[1:4]) / f"b{aid[1:]}.txt"
    d = None
    if p.exists():
        d = {}
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#"): continue
                    q = line.split()
                    if len(q) >= 2:
                        try: d[int(q[0])] = int(q[1])
                        except ValueError: pass
                    if len(d) >= limit: break
        except OSError: d = None
    _c[aid] = d
    return d


def main() -> int:
    con = sqlite3.connect(str(DB))
    rows = con.execute("""
        SELECT f.aid, f.text FROM formula f JOIN seq s ON s.aid = f.aid
        WHERE f.text LIKE 'a(n) =%'
          AND (f.text LIKE '%binomial(%' OR f.text LIKE '%!%' OR f.text GLOB '*Sum_{*')
          AND s.n_terms >= 20
          AND s.aid IN (SELECT aid FROM attachment WHERE name LIKE 'b%.txt')
    """).fetchall()
    print("raw formula lines:", len(rows))

    best = {}
    for aid, text in rows:
        if aid in best and len(best[aid]) <= len(text):
            continue
        best[aid] = text
    print("candidate sequences:", len(best))

    out = []
    for aid, text in best.items():
        d = bfile(aid)
        if not d: continue
        ns = sorted(d)
        run, prev, longest = [], None, []
        for n in ns:
            if prev is not None and n != prev + 1:
                if len(run) > len(longest):
                    longest = run
                run = []
            run.append(n); prev = n
        if len(run) > len(longest):
            longest = run
        if len(longest) < T + K: continue
        vals = [d[n] for n in longest[:T]]
        truth = [d[n] for n in longest[T:T+K]]
        pp = poly_predict(vals, K)
        bp = bm_predict(vals, K)
        poly_ok = int(pp == truth) if pp is not None else 0
        if bp is not None:
            bm_ok = int(bp == truth)
        else:
            bm_ok = 0
        fam = "binomial" if "binomial(" in text else ("factorial" if "!" in text else "sum")
        out.append({"aid": aid, "family": fam, "expr": clean(text)[:300],
                    "poly_ok": poly_ok, "bm_ok": bm_ok})
    print("evaluated:", len(out))

    con.execute("DROP TABLE IF EXISTS hard_bench")
    con.execute("""CREATE TABLE hard_bench (
        aid TEXT PRIMARY KEY, family TEXT, expr TEXT,
        poly_ok INTEGER, bm_ok INTEGER, hard INTEGER)""")
    con.executemany("INSERT INTO hard_bench VALUES (?,?,?,?,?,?)",
                    [(r["aid"], r["family"], r["expr"], r["poly_ok"], r["bm_ok"],
                      int(not (r["poly_ok"] or r["bm_ok"]))) for r in out])
    con.execute("CREATE INDEX idx_hard ON hard_bench(hard)")
    con.commit()

    by_fam = Counter(r["family"] for r in out)
    hard = [r for r in out if not (r["poly_ok"] or r["bm_ok"])]
    hard_fam = Counter(r["family"] for r in hard)
    print("by family:", dict(by_fam))
    print("hard (neither baseline):", len(hard), f"({100*len(hard)/len(out):.1f}%)", dict(hard_fam))
    print("\nhard examples:")
    for r in hard[:15]:
        print(f"  {r['aid']} [{r['family']}] {r['expr'][:85]}")
    json.dump({"evaluated": len(out), "by_family": dict(by_fam),
               "hard": len(hard), "hard_by_family": dict(hard_fam)},
              open(OUT, "w"), indent=1)
    print("wrote", OUT)
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())