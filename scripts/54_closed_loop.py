#!/usr/bin/env python3
"""Closed-loop candidate verification.

    python scripts/54_closed_loop.py --build
    python scripts/54_closed_loop.py --lit
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "closed_loop_candidates.json"
LIT = ROOT / "reports" / "closed_loop_lit.jsonl"


def search(query, count=5):
    key = (ROOT / "APIkey").read_text(encoding="utf-8").strip()
    body = json.dumps({"query": query, "count": count, "need_content": False}).encode()
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/tools/search", data=body,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def build() -> int:
    con = sqlite3.connect("file:" + ROOT.joinpath("oeis.db").as_posix() + "?mode=ro", uri=True)
    hits = defaultdict(set)
    for aid, r in con.execute("select aid, r from congruence2 where p=5 and m=5"):
        hits[aid].add(r)
    z1 = {a for a, z in hits.items() if z == {1}}
    fe = json.load(open(ROOT / "reports" / "factor_explain.json", encoding="utf-8"))
    unexplained = {a for a, p, r in fe["unexplained"]}
    dep = {}
    for x in json.load(open(ROOT / "reports" / "congruence_depth.json", encoding="utf-8")):
        k = (x["aid"], x["p"])
        if k not in dep or x["depth"] > dep[k]["depth"]:
            dep[k] = x
    kern = {x["aid"]: x["kernel"] for x in json.load(open(ROOT / "reports" / "kernel.json", encoding="utf-8"))}
    deep = []
    for (a, p, r) in fe["unexplained"]:
        x = dep.get((a, p))
        if x and x["depth"] >= 3 and kern.get(a, 999) >= 50:
            deep.append({"aid": a, "p": p, "r": r, "depth": x["depth"]})
    cand = {"z1": sorted(z1 & unexplained), "deep": deep}
    print("Z={1} unexplained:", len(cand["z1"]))
    print("deep:", len(deep), "seqs:", len({d['aid'] for d in deep}))
    OUT.write_text(json.dumps(cand, indent=1), encoding="utf-8")
    print("wrote", OUT)
    return 0


def literature() -> int:
    cand = json.load(open(OUT, encoding="utf-8"))
    aids = sorted({d["aid"] for d in cand["deep"]} | set(cand["z1"]))
    print("unique candidates:", len(aids), flush=True)
    done = set()
    if LIT.exists():
        for line in open(LIT, encoding="utf-8"):
            done.add(json.loads(line)["aid"])
    with open(LIT, "a", encoding="utf-8") as fh:
        for i, aid in enumerate(aids):
            if aid in done:
                continue
            try:
                res = search(aid + " congruence", 5)
            except Exception as e:
                print("ERR", aid, type(e).__name__, flush=True)
                time.sleep(3)
                continue
            hits = []
            for x in res.get("results", []):
                url = x.get("url") or ""
                if "oeis.org" in url:
                    continue
                blob = ((x.get("title") or "") + " " + (x.get("summary") or "")).lower()
                if "congruen" in blob or "modulo" in blob or " mod " in blob:
                    hits.append({"title": (x.get("title") or "")[:120], "url": url[:150]})
            fh.write(json.dumps({"aid": aid, "hits": hits}) + chr(10))
            fh.flush()
            if (i + 1) % 20 == 0:
                print("  done", i + 1, "/", len(aids), flush=True)
            time.sleep(0.3)
    print("wrote", LIT)
    return 0


def main(argv) -> int:
    if "--lit" in argv:
        return literature()
    return build()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
