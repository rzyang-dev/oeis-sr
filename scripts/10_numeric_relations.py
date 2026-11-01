#!/usr/bin/env python3
"""Mine exact numeric relations between sequences and compare with the docs.

Three O(N) detectors over sequences with >=14 int64 terms and offset 0/1:

    equal    same first 14 terms, verified on all available terms
    affine   a = alpha*b + beta  (rational alpha != 0), verified exactly
    prefix   a(n) - a(n-1) = b(n)  (a is the prefix sum of b, up to constant)

Candidates come from hashing a 14-term prefix (or 13-term window for prefix);
each candidate is then checked with exact integer arithmetic on the full term
list.  Relations are compared against definition / identity / xref.

    python scripts/10_numeric_relations.py
"""
from __future__ import annotations

import json
import random
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "numeric_relations.json"
L = 14


def affine_key(v: np.ndarray):
    d = v - v[0]
    nz = d[d != 0]
    if nz.size == 0:
        return None
    g = int(np.gcd.reduce(np.abs(nz)))
    dn = d // g
    if dn[dn != 0][0] < 0:
        dn = -dn
    return dn.tobytes()


def main() -> int:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = con.execute(
        "select aid, offset1, terms from seq where all_int64=1 and n_terms>=14 "
        "and offset1 in (0,1)").fetchall()
    full, off, vec = {}, {}, {}
    for aid, o, t in rows:
        parts = [int(x) for x in t.split(",")]
        if len(parts) < L:
            continue
        full[aid] = parts
        off[aid] = o
        vec[aid] = np.array(parts[:L], dtype=np.int64)
    print("sequences:", len(full))

    idx_eq = defaultdict(list)
    idx_aff = defaultdict(list)
    idx_win = defaultdict(list)
    for aid, v in vec.items():
        o = off[aid]
        idx_eq[(o, v.tobytes())].append(aid)
        k = affine_key(v)
        if k is not None:
            idx_aff[(o, k)].append(aid)
        w = full[aid]
        for start in (0, 1):
            if len(w) >= start + L - 1:
                idx_win[(o + start, tuple(w[start:start + L - 1]))].append(aid)

    def bucket_pairs(idx, cap=25):
        out = []
        for vs in idx.values():
            if len(vs) < 2:
                continue
            take = vs[:cap]
            for i in range(len(take)):
                for j in range(i + 1, len(take)):
                    out.append((take[i], take[j]))
        return out

    cand = [("equal", a, b) for a, b in bucket_pairs(idx_eq)]
    cand += [("affine", a, b) for a, b in bucket_pairs(idx_aff)]
    for aid, w in full.items():
        d = [w[i] - w[i-1] for i in range(1, min(len(w), L))]
        if len(d) < L - 1:
            continue
        key = (off[aid] + 1, tuple(d))
        for b in idx_win.get(key, ())[:25]:
            if b != aid:
                cand.append(("prefix", aid, b))
    print("candidate pairs:", len(cand))

    def align(a, b):
        oa, va = off[a], full[a]
        ob, vb = off[b], full[b]
        lo = max(oa, ob)
        hi = min(oa + len(va), ob + len(vb))
        if hi - lo < 10:
            return None
        return [va[i-oa] for i in range(lo, hi)], [vb[i-ob] for i in range(lo, hi)]

    def check(kind, a, b):
        ab = align(a, b)
        if ab is None:
            return False
        x, y = ab
        if len(set(x)) == 1 or len(set(y)) == 1:
            return False                       # trivial constant relation
        if kind == "equal":
            return x == y
        if kind == "prefix":
            return all(x[k] == x[k-1] + y[k] for k in range(1, len(x)))
        # affine
        i = j = None
        for k in range(len(y) - 1):
            if y[k] != y[k+1]:
                i, j = k, k + 1
                break
        if i is None:
            return False
        an, ad = x[i] - x[j], y[i] - y[j]
        bn = x[i] * ad - an * y[i]
        return all(x[k] * ad == an * y[k] + bn for k in range(len(x)))

    kept = [c for c in cand if check(*c)]
    print("verified pairs:", len(kept), Counter(k for k, _, _ in kept))

    doc = set()
    for q in ("select aid, dst from definition", "select aid, dst from identity",
              "select src, dst from xref"):
        for a, b in con.execute(q):
            doc.add((a, b) if a < b else (b, a))
    print("documented pairs:", len(doc))

    derived = {r[0] for r in con.execute("select distinct aid from definition")}
    stats = Counter()
    undoc = []
    for kind, a, b in kept:
        key = (a, b) if a < b else (b, a)
        ok = key in doc
        stats[(kind, ok)] += 1
        if not ok:
            undoc.append((kind, a, b))

    seqs_undoc = {x for _, a, b in undoc for x in (a, b)}
    both_atoms = sum(1 for _, a, b in undoc if a not in derived and b not in derived)
    name = dict(con.execute("select aid, name from seq"))

    print()
    for kind in ("equal", "affine", "prefix"):
        d, u = stats[(kind, True)], stats[(kind, False)]
        print(f"{kind:7} documented {d:>6}   undocumented {u:>6}   total {d+u:>6}")
    print(f"\nundocumented pairs: {len(undoc)}   distinct sequences involved: {len(seqs_undoc):,}")
    print(f"undocumented pairs with both sides atomic: {both_atoms:,}")

    random.seed(2)
    examples = {}
    for kind in ("equal", "affine", "prefix"):
        ex = [x for x in undoc if x[0] == kind]
        random.shuffle(ex)
        examples[kind] = [
            {"a": a, "b": b, "a_name": name.get(a, "")[:100], "b_name": name.get(b, "")[:100]}
            for _, a, b in ex[:5]]

    # persist the verified pairs (canonical order) for downstream use
    con2 = sqlite3.connect(str(DB))
    con2.execute("DROP TABLE IF EXISTS numeric_relation")
    con2.execute("CREATE TABLE numeric_relation (aid TEXT, dst TEXT, kind TEXT)")
    n_inserted = 0
    seen = set()
    for kind, a, b in kept:
        if a == b:
            continue
        if kind == "prefix":
            rec = (a, b, "prefix")          # directional: a(n)-a(n-1) = b(n)
        else:
            lo, hi = (a, b) if a < b else (b, a)
            rec = (lo, hi, kind)
        if rec in seen:
            continue
        seen.add(rec)
        con2.execute("INSERT INTO numeric_relation VALUES (?,?,?)", rec)
        n_inserted += 1
    con2.execute("CREATE INDEX idx_numrel_aid ON numeric_relation(aid)")
    con2.execute("CREATE INDEX idx_numrel_dst ON numeric_relation(dst)")
    con2.commit()
    con2.close()
    print(f"numeric_relation table: {n_inserted} rows")

    out = {
        "eligible_sequences": len(full),
        "candidates": len(cand),
        "verified": len(kept),
        "by_kind": {k: {"documented": stats[(k, True)], "undocumented": stats[(k, False)]}
                    for k in ("equal", "affine", "prefix")},
        "undocumented": len(undoc),
        "sequences_in_undocumented": len(seqs_undoc),
        "both_atomic_undocumented": both_atoms,
        "examples": examples,
    }
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
