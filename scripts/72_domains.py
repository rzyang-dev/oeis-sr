#!/usr/bin/env python3
"""Domain clustering of the whole OEIS by name (TF-IDF + k-means).

    python scripts/72_domains.py
"""
from __future__ import annotations

import json
import math
import random
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "domains.json"
K = 40
VOCAB = 3000
SAMPLE = 30000

STOP = set("""a an the of in on for to and or with by is are as at from that this which
numbers number sequence n k m p q x y s t values terms integers positive nonnegative given
where such every all any first second one two three zero also equals equal defined let
if then else not its his her their there here we you they it be been being was were has have
had do does did can could may might must shall should will would""".split())


def tokens(name):
    w = re.findall(r"[a-z][a-z']+", name.lower())
    return [x for x in w if len(x) > 2 and x not in STOP]


def main() -> int:
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    rows = con.execute("select aid, name from seq").fetchall()
    print("sequences:", len(rows))
    docs = [(aid, tokens(name)) for aid, name in rows]
    df = Counter()
    for _, toks in docs:
        df.update(set(toks))
    vocab = [w for w, _ in df.most_common(VOCAB)]
    vid = {w: i for i, w in enumerate(vocab)}
    idf = np.array([math.log(len(docs) / (1 + df[w])) for w in vocab], dtype=np.float32)
    sparse = []
    for _, toks in docs:
        c = Counter(t for t in toks if t in vid)
        if not c:
            sparse.append({})
            continue
        v = {vid[t]: n for t, n in c.items()}
        nrm = math.sqrt(sum((n * idf[i]) ** 2 for i, n in v.items())) or 1.0
        sparse.append({i: n * idf[i] / nrm for i, n in v.items()})
    print("vocab:", len(vocab), "docs with tokens:", sum(1 for s in sparse if s))

    rng = random.Random(1)
    idx = rng.sample(range(len(sparse)), min(SAMPLE, len(sparse)))
    X = [sparse[i] for i in idx]

    C = np.zeros((K, len(vocab)), dtype=np.float32)
    for j in range(K):
        C[j] = np.random.default_rng(j).random(len(vocab)).astype(np.float32)
        C[j] /= np.linalg.norm(C[j]) + 1e-9

    for it in range(15):
        assign = []
        for x in X:
            scores = np.array([sum(v * C[j][i] for i, v in x.items()) for j in range(K)])
            assign.append(int(scores.argmax()))
        newC = np.zeros_like(C)
        for x, a in zip(X, assign):
            for i, v in x.items():
                newC[a][i] += v
        for j in range(K):
            nrm = np.linalg.norm(newC[j])
            if nrm > 0:
                newC[j] /= nrm
        shift = np.abs(newC - C).sum()
        C = newC
        print("iter", it, "shift", round(float(shift), 2), flush=True)

    for j in range(K):
        top = np.argsort(-C[j])[:12]
        print(f"cluster {j}: " + ", ".join(vocab[i] for i in top))

    # assign all
    out = []
    for aid, x in zip([d[0] for d in docs], sparse):
        if not x:
            out.append((aid, -1))
            continue
        scores = np.array([sum(v * C[j][i] for i, v in x.items()) for j in range(K)])
        out.append((aid, int(scores.argmax())))
    con2 = sqlite3.connect(str(ROOT / "oeis.db"))
    con2.execute("DROP TABLE IF EXISTS domain")
    con2.execute("CREATE TABLE domain (aid TEXT PRIMARY KEY, cluster INTEGER)")
    con2.executemany("INSERT INTO domain VALUES (?,?)", out)
    con2.commit()
    print("assigned:", Counter(c for _, c in out).most_common(5))
    json.dump({"vocab": vocab[:200],
               "centroids_top": {j: [vocab[i] for i in np.argsort(-C[j])[:15]] for j in range(K)}},
              open(OUT, "w"), indent=1)
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
