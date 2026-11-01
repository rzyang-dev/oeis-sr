#!/usr/bin/env python3
"""Definition graph and atomicity analysis.

Two graphs are derived from the %N / %F / %C statements in oeis.db:

D  (definition)  A -> B if A's *name* (%N) is stated in terms of B.
                 This is the graph in which A is "introduced through" B.
I  (identity)    A -> B if any formula/comment of A expresses A via B.
                 Denser; useful for "related sequence" retrieval, not for
                 atomicity.

A sequence is an ATOM when its name does not invoke any other sequence.
Atoms that many sequences (transitively) rest on are the "foundational" ones.

    python scripts/07_atoms.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "oeis.db"
OUT = ROOT / "reports" / "relations.json"

EQUIV = ("duplicate of", "erroneous version of", "same as a", "identical to a",
         "version of a", "is a duplicate")


def is_equiv(text: str) -> bool:
    low = text.lower()
    return any(m in low for m in EQUIV)


def tarjan(adj: dict[str, list[str]]) -> tuple[dict[str, int], int]:
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on: set[str] = set()
    stack: list[str] = []
    comp: dict[str, int] = {}
    counter = 0
    n_comp = 0

    for root in list(adj):
        if root in index:
            continue
        work = [(root, 0)]
        while work:
            v, i = work.pop()
            if i == 0:
                index[v] = low[v] = counter
                counter += 1
                stack.append(v)
                on.add(v)
            recurse = False
            nbrs = adj.get(v, ())
            while i < len(nbrs):
                w = nbrs[i]
                i += 1
                if w not in index:
                    work.append((v, i))
                    work.append((w, 0))
                    recurse = True
                    break
                if w in on:
                    low[v] = min(low[v], index[w])
            if recurse:
                continue
            if low[v] == index[v]:
                while True:
                    w = stack.pop()
                    on.discard(w)
                    comp[w] = n_comp
                    if w == v:
                        break
                n_comp += 1
            if work:
                parent = work[-1][0]
                lv = low[v]
                if lv < low[parent]:
                    low[parent] = lv
    return comp, n_comp


def main() -> int:
    import sqlite3

    t0 = time.time()
    con = sqlite3.connect(str(DB))
    n_seq = con.execute("select count(*) from seq").fetchone()[0]

    # ---------- edge extraction ----------
    def_edges: dict[tuple[str, str], str] = {}
    id_edges: set[tuple[str, str]] = set()
    for aid, dst, field, kind, text in con.execute(
            "SELECT r.aid, r.dst, s.field, s.kind, s.text FROM stmt_ref r "
            "JOIN stmt s ON s.aid=r.aid AND s.field=r.field AND s.idx=r.idx"):
        if field == "N":
            if not is_equiv(text):
                def_edges.setdefault((aid, dst), text)
        elif kind in ("def", "alias") and not is_equiv(text):
            id_edges.add((aid, dst))

    # ---------- persist the two graphs ----------
    con.execute("DROP TABLE IF EXISTS relation")
    con.execute("DROP TABLE IF EXISTS definition")
    con.execute("DROP TABLE IF EXISTS identity")
    con.execute("CREATE TABLE definition (aid TEXT, dst TEXT, text TEXT)")
    con.execute("CREATE TABLE identity (aid TEXT, dst TEXT)")
    con.executemany("INSERT INTO definition VALUES (?,?,?)",
                    [(a, d, t) for (a, d), t in def_edges.items()])
    con.executemany("INSERT INTO identity VALUES (?,?)", sorted(id_edges))
    con.execute("CREATE INDEX idx_definition_aid ON definition(aid)")
    con.execute("CREATE INDEX idx_definition_dst ON definition(dst)")
    con.execute("CREATE INDEX idx_identity_aid ON identity(aid)")
    con.commit()

    # ---------- definition graph D ----------
    adj: dict[str, list[str]] = defaultdict(list)
    for (a, d) in def_edges:
        adj[a].append(d)
    for a in adj:
        adj[a] = sorted(set(adj[a]))
    derived = set(adj)                      # sequences whose name uses others
    atoms = {r[0] for r in con.execute("select aid from seq")} - derived

    comp, n_comp = tarjan(adj)
    members: dict[int, list[str]] = defaultdict(list)
    for v, c in comp.items():
        members[c].append(v)

    cadj: dict[int, set[int]] = defaultdict(set)
    for a, ds in adj.items():
        for d in ds:
            if comp[a] != comp[d]:
                cadj[comp[a]].add(comp[d])

    # depth = longest definition chain to an atom, on the condensation
    depth: dict[int, int] = {}

    def comp_depth(c: int) -> int:
        stack = [(c, False)]
        while stack:
            node, done = stack.pop()
            if node in depth:
                continue
            if done:
                depth[node] = 1 + max((depth.get(nb, 0) for nb in cadj.get(node, ())), default=-1) \
                    if cadj.get(node) else 0
                continue
            stack.append((node, True))
            for nb in cadj.get(node, ()):
                if nb not in depth:
                    stack.append((nb, False))
        return depth.get(c, 0)

    for c in members:
        comp_depth(c)
    node_depth = {v: depth.get(comp[v], 0) for v in comp}

    # transitive atom dependencies (per component)
    deps: dict[int, set[str]] = {}

    def comp_deps(c: int) -> set[str]:
        stack = [(c, False)]
        while stack:
            node, done = stack.pop()
            if node in deps:
                continue
            if done:
                s: set[str] = set(members[node]) - derived
                for nb in cadj.get(node, ()):
                    s |= deps.get(nb, set())
                deps[node] = s
                continue
            stack.append((node, True))
            for nb in cadj.get(node, ()):
                if nb not in deps:
                    stack.append((nb, False))
        return deps.get(c, set())

    for c in members:
        comp_deps(c)

    direct = Counter(d for (_a, d) in def_edges)
    trans: Counter[str] = Counter()
    for c, s in deps.items():
        k = sum(1 for v in members[c] if v in derived)
        if k:
            for a in s:
                trans[a] += k

    # ---------- identity graph I ----------
    i_src = len({a for a, _ in id_edges})

    # ---------- reporting ----------
    cycles = [c for c, vs in members.items() if len(vs) > 1]
    cyc_nodes = sum(len(members[c]) for c in cycles)
    max_depth = max(node_depth.values()) if node_depth else 0
    deepest = sorted(node_depth.items(), key=lambda kv: -kv[1])[:3]
    chains = []
    for aid, _ in deepest:
        path, cur, seen = [aid], aid, {aid}
        while adj.get(cur):
            nxt = max((x for x in adj[cur] if x not in seen),
                      key=lambda x: node_depth.get(x, 0), default=None)
            if nxt is None:
                break
            path.append(nxt)
            seen.add(nxt)
            cur = nxt
            if len(path) >= 10:
                break
        chains.append(path)

    name = dict(con.execute("select aid, name from seq"))
    kw = dict(con.execute("select aid, keywords from seq"))

    def top_atoms(counter: Counter[str], n: int = 30):
        rows = []
        for aid, cnt in counter.most_common(n * 3):
            if aid in derived or aid not in name:
                continue
            rows.append({"aid": aid, "count": cnt, "name": name[aid],
                         "keywords": kw.get(aid, "")})
            if len(rows) >= n:
                break
        return rows

    cov = sorted(trans.values(), reverse=True)
    total_pairs = sum(cov)

    def coverage(frac: float) -> int:
        acc = 0
        for i, v in enumerate(cov, 1):
            acc += v
            if acc >= frac * total_pairs:
                return i
        return len(cov)

    # core atom catalogue (top 2000 by transitive dependents)
    cat = ROOT / "data" / "atom_core.csv"
    cat.parent.mkdir(exist_ok=True)
    with open(cat, "w", encoding="utf-8", newline="") as fh:
        fh.write("aid,direct_dependents,transitive_dependents,name,keywords\n")
        for aid, cnt in trans.most_common():
            if aid in derived or aid not in name:
                continue
            nm = name[aid].replace('"', "'")
            fh.write(f'{aid},{direct.get(aid, 0)},{cnt},"{nm}","{kw.get(aid, "")}"\n')
            if fh.tell() > 2_000_000:
                break

    out = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "n_sequences": n_seq,
        "definition_edges": len(def_edges),
        "identity_edges": len(id_edges),
        "identity_sources": i_src,
        "derived": len(derived),
        "atoms": len(atoms),
        "atoms_referenced": len(set(direct) & atoms),
        "cycles": {"nontrivial_sccs": len(cycles), "nodes": cyc_nodes},
        "depth": {"max": max_depth,
                  "hist": sorted(Counter(node_depth.values()).items())[:15]},
        "top_atoms_direct": top_atoms(direct),
        "top_atoms_transitive": top_atoms(trans),
        "coverage": {"total_dependency_pairs": total_pairs,
                     "atoms_for_50pct": coverage(0.5),
                     "atoms_for_80pct": coverage(0.8),
                     "atoms_for_90pct": coverage(0.9)},
        "chains": chains,
        "top_direct_raw": direct.most_common(10),
    }
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"sequences {n_seq:,}   definition edges {len(def_edges):,}   identity edges {len(id_edges):,} ({i_src:,} sources)")
    print(f"derived (name uses another sequence): {len(derived):,}   atoms: {len(atoms):,}   atoms referenced: {len(set(direct) & atoms):,}")
    print(f"cycles: {len(cycles):,} sccs / {cyc_nodes:,} nodes   max depth {max_depth}")
    print("depth hist:", out["depth"]["hist"])
    print(f"dependency pairs (derived seq -> atom, transitive): {total_pairs:,}")
    print("atoms needed for 50/80/90% coverage:", out["coverage"]["atoms_for_50pct"],
          out["coverage"]["atoms_for_80pct"], out["coverage"]["atoms_for_90pct"])
    print("\ntop atoms by DIRECT dependents:")
    for r in out["top_atoms_direct"][:15]:
        print(f"  {r['aid']}  {r['count']:>5}  {r['name'][:78]}")
    print("\ntop atoms by TRANSITIVE dependents:")
    for r in out["top_atoms_transitive"][:15]:
        print(f"  {r['aid']}  {r['count']:>5}  {r['name'][:78]}")
    print("\nchains:")
    for ch in chains:
        print("  " + " -> ".join(ch))
    print(f"\nwrote {OUT}  ({time.time()-t0:.1f}s)")
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
