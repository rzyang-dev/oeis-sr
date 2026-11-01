#!/usr/bin/env python3
"""Structural fingerprints from b-files: growth class, degree, periodicity.

For every sequence with a b-file, read up to 2000 terms and summarise:
  growth       zero | polynomial | exponential | factorial | super | other
  degree       log-log slope of |a(n)| vs n (polynomial degree estimate)
  log2_base    tail log2 ratio a(n+1)/a(n) (exponential base)
  periodic     smallest period p <= 12 seen in the last 120 terms, else 0
  max_digits   digits of the largest |a(n)|
  zeros        number of zero terms
  sign_changes number of sign changes

    python scripts/30_fingerprints.py --shard k --of n
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
DB = ROOT / "oeis.db"


def read_bfile(aid, limit=600):
    p = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not p.exists():
        return None
    vals = []
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                q = line.split()
                if len(q) >= 2:
                    try:
                        vals.append(int(q[1]))
                    except ValueError:
                        pass
                if len(vals) >= limit:
                    break
    except OSError:
        return None
    return vals or None


def fingerprint(v):
    n = len(v)
    if n < 10:
        return None
    max_digits = max(len(str(abs(x))) for x in v)
    zeros = sum(1 for x in v if x == 0)
    signs = sum(1 for i in range(1, n) if (v[i] > 0) != (v[i-1] > 0) and v[i] != 0 and v[i-1] != 0)
    nz = [(i, abs(x)) for i, x in enumerate(v) if x != 0]
    if len(nz) < 8:
        return {"growth": "zero", "degree": 0.0, "log2_base": 0.0,
                "periodic": 0, "max_digits": max_digits, "zeros": zeros,
                "sign_changes": signs}
    tail = nz[-60:]
    # log-log slope
    xs = [math.log(i + 2) for i, _ in tail]
    ys = [math.log(a) for _, a in tail]
    mx = sum(xs) / len(xs); my = sum(ys) / len(ys)
    den = sum((x - mx) ** 2 for x in xs) or 1.0
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    # tail log2 ratios
    lr = []
    for k in range(len(tail) - 20, len(tail) - 1):
        if k < 0 or tail[k][1] == 0:
            continue
        lr.append(math.log2(tail[k+1][1]) - math.log2(tail[k][1]))
    lr_mean = sum(lr) / len(lr) if lr else 0.0
    lr_last = lr[-1] if lr else 0.0
    growth = "other"
    if lr and abs(lr_last) < 0.05 and abs(slope) < 20:
        growth = "polynomial"
    elif lr and 0.05 <= lr_mean < 20 and abs(lr_last - lr_mean) < 0.5:
        growth = "exponential"
    elif lr and lr_last > math.log2(max(2, n)) * 0.5:
        growth = "factorial"
    elif lr and lr_mean >= 20:
        growth = "super"
    # periodicity over last 120 terms
    per = 0
    m = min(120, n)
    seg = v[-m:]
    for p in range(1, 13):
        if all(seg[i] == seg[i - p] for i in range(p, len(seg))):
            per = p
            break
    return {"growth": growth, "degree": round(slope, 2), "log2_base": round(lr_mean, 3),
            "periodic": per, "max_digits": max_digits, "zeros": zeros,
            "sign_changes": signs}


def main(argv: list[str]) -> int:
    shard = int(argv[argv.index("--shard") + 1]) if "--shard" in argv else 0
    of = int(argv[argv.index("--of") + 1]) if "--of" in argv else 1
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    aids = [r[0] for r in con.execute(
        "select distinct aid from attachment where name like 'b%.txt' and aid in (select aid from seq)")]
    aids.sort()
    if of > 1:
        aids = aids[shard::of]
    print("shard", shard, "sequences:", len(aids), flush=True)
    out = ROOT / "reports" / f"fingerprint_{shard:02d}.jsonl"
    n = 0
    with open(out, "w", encoding="utf-8") as fh:
        for i, aid in enumerate(aids):
            v = read_bfile(aid)
            if not v:
                continue
            fp = fingerprint(v)
            if not fp:
                continue
            fp["aid"] = aid
            fp["n_terms"] = len(v)
            fh.write(json.dumps(fp) + "\n")
            n += 1
            if (i + 1) % 5000 == 0:
                print(f"  {i+1}/{len(aids)}", flush=True)
    print("wrote", out, n, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
