#!/usr/bin/env python3
"""Build oeis.db: one SQLite file holding every OEIS entry of the snapshot.

    python scripts/02_build_db.py                 # full build, 8 shards
    python scripts/02_build_db.py --jobs 8 --limit-dirs 40
    python scripts/02_build_db.py --shard 3 --of 8   # internal: one shard

The sandbox blocks named pipes, so the shards are started with subprocess
(stdout redirected to a log file) instead of multiprocessing.  Each shard
writes build/part_NN.sqlite; the launcher merges them (disjoint A-numbers)
and creates the indexes once, on the merged table.
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
SEQ = DATA / "seq"
BUILD = ROOT / "build"
DB_PATH = ROOT / "oeis.db"

sys.path.insert(0, str(ROOT))

from oeisdb import db as dbmod  # noqa: E402


def term_stats(terms: str) -> tuple[int, int, str]:
    """(all_int64, max_abs_digits, sign_class) for a comma separated term list."""
    if not terms:
        return 1, 0, "nonneg"
    all64 = 1
    max_d = 0
    has_pos = has_neg = False
    for t in terms.split(","):
        if t[0] == "-":
            has_neg = True
            s = t[1:]
        elif t[0] == "+":
            s = t[1:]
        else:
            has_pos = True
            s = t
        d = len(s)
        if d > max_d:
            max_d = d
        if all64:
            if d > 19:
                all64 = 0
            elif d == 19 and not (-2**63 <= int(t) < 2**63):
                all64 = 0
    if has_neg and has_pos:
        sign = "mixed"
    elif has_neg:
        sign = "nonpos"
    else:
        sign = "nonneg"
    return all64, max_d, sign


def build_shard(k: int, of: int, limit_dirs: int | None = None) -> dict:
    from oeisdb import parse_text

    t0 = time.time()
    dirs = sorted(str(p) for p in SEQ.iterdir() if p.is_dir())
    if limit_dirs:
        dirs = dirs[:limit_dirs]
    dirs = dirs[k::of]
    out_path = str(BUILD / f"part_{k:02d}.sqlite")
    if Path(out_path).exists():
        Path(out_path).unlink()

    conn = sqlite3.connect(out_path)
    conn.execute("PRAGMA journal_mode=OFF")
    conn.execute("PRAGMA synchronous=OFF")
    conn.executescript(dbmod.SCHEMA)

    seq_rows: list[tuple] = []
    kw_rows: list[tuple] = []
    f_rows: list[tuple] = []
    x_rows: list[tuple] = []
    l_rows: list[tuple] = []
    p_rows: list[tuple] = []
    n_files = n_bad = 0

    def flush() -> None:
        nonlocal seq_rows, kw_rows, f_rows, x_rows, l_rows, p_rows
        if not seq_rows:
            return
        conn.executemany(
            "INSERT INTO seq VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", seq_rows)
        conn.executemany("INSERT INTO keyword VALUES (?,?)", kw_rows)
        conn.executemany("INSERT INTO formula VALUES (?,?,?,?,?)", f_rows)
        conn.executemany("INSERT INTO xref VALUES (?,?)", x_rows)
        conn.executemany("INSERT INTO link VALUES (?,?,?,?)", l_rows)
        conn.executemany("INSERT INTO program VALUES (?,?,?)", p_rows)
        seq_rows, kw_rows, f_rows, x_rows, l_rows, p_rows = [], [], [], [], [], []

    for d in dirs:
        for f in sorted(Path(d).glob("*.seq")):
            aid = f.stem
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                n_bad += 1
                continue
            e = parse_text(text, aid)
            n_files += 1
            all64, max_d, sign = term_stats(e["terms"])
            seq_rows.append((
                aid, e["name"], e["offset1"], e["offset2"], ",".join(e["keywords"]),
                e["n_terms"], e["terms"],
                e["n_comments"], e["n_formulas"], e["n_links"], e["n_refs"],
                e["n_examples"], e["n_programs"], e["n_xrefs"],
                e["author"], e["version"], e["last_edit"],
                all64, max_d, sign,
            ))
            for kw in e["keywords"]:
                kw_rows.append((aid, kw))
            for fm in e["formulas"]:
                f_rows.append((aid, fm["idx"], fm["kind"], fm["conjectural"], fm["text"]))
            for x in e["xrefs"]:
                x_rows.append((aid, x))
            for ln in e["links"]:
                l_rows.append((aid, ln["idx"], ln["href"], ln["kind"]))
            for pr in e["programs"]:
                p_rows.append((aid, pr["lang"], pr["text"]))
            if len(seq_rows) >= 2000:
                flush()
    flush()
    conn.commit()
    conn.close()
    return {"part": k, "files": n_files, "bad": n_bad,
            "seconds": round(time.time() - t0, 1), "path": out_path}


def merge(jobs: int, t0: float) -> dict:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=OFF")
    conn.execute("PRAGMA synchronous=OFF")
    conn.execute("PRAGMA cache_size=-400000")
    conn.executescript(dbmod.SCHEMA)

    tables = ["seq", "keyword", "formula", "xref", "link", "program"]
    for k in range(jobs):
        part = BUILD / f"part_{k:02d}.sqlite"
        if not part.exists():
            continue
        conn.execute(f"ATTACH DATABASE '{part.as_posix()}' AS p{k}")
        for t in tables:
            conn.execute(f"INSERT INTO main.{t} SELECT * FROM p{k}.{t}")
        conn.commit()
        conn.execute(f"DETACH DATABASE p{k}")
    print(f"merged in {time.time()-t0:.0f}s; creating indexes", flush=True)
    conn.executescript(dbmod.INDEXES)
    conn.commit()

    manifest = DATA / "MANIFEST.tsv"
    att: list[tuple] = []
    if manifest.exists():
        with open(manifest, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line.startswith("#") or line.startswith("path\t"):
                    continue
                parts = line.rstrip("\r\n").split("\t")
                if len(parts) != 4 or not parts[0].startswith("files/"):
                    continue
                path, _sha, size, source = parts
                name = path.rsplit("/", 1)[-1]
                stem, dot, ext = name.partition(".")
                aid = ("A" + stem[1:]) if stem[:1] in "ab" and stem[1:].isdigit() else None
                att.append((aid, name, ext, int(size), source))
                if len(att) >= 20000:
                    conn.executemany("INSERT INTO attachment VALUES (?,?,?,?,?)", att)
                    att = []
        if att:
            conn.executemany("INSERT INTO attachment VALUES (?,?,?,?,?)", att)
    conn.commit()

    counts = {t: conn.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
              for t in ("seq", "keyword", "formula", "xref", "link", "program", "attachment")}
    meta = {
        "source": str(DATA),
        "snapshot_time": (DATA / "time.txt").read_text().strip() if (DATA / "time.txt").exists() else "",
        "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "n_seqs": counts["seq"],
        "counts": counts,
    }
    conn.executemany("INSERT INTO meta VALUES (?,?)",
                     [(k, json.dumps(v) if isinstance(v, dict) else str(v)) for k, v in meta.items()])
    conn.commit()
    conn.execute("ANALYZE")
    conn.commit()
    conn.close()
    return counts


def main(argv: list[str]) -> int:
    if "--shard" in argv:
        k = int(argv[argv.index("--shard") + 1])
        of = int(argv[argv.index("--of") + 1])
        limit = int(argv[argv.index("--limit-dirs") + 1]) if "--limit-dirs" in argv else None
        r = build_shard(k, of, limit)
        print(json.dumps(r))
        return 0

    jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 8
    limit = int(argv[argv.index("--limit-dirs") + 1]) if "--limit-dirs" in argv else None

    t0 = time.time()
    BUILD.mkdir(exist_ok=True)
    n_dirs = len([p for p in SEQ.iterdir() if p.is_dir()])
    if limit:
        n_dirs = min(n_dirs, limit)
    jobs = max(1, min(jobs, n_dirs))
    print(f"{n_dirs} directories, {jobs} shards", flush=True)

    procs = []
    extra = ["--limit-dirs", str(limit)] if limit else []
    for k in range(jobs):
        log = open(BUILD / f"part_{k:02d}.log", "w", encoding="utf-8")
        p = subprocess.Popen([sys.executable, str(Path(__file__).resolve()),
                              "--shard", str(k), "--of", str(jobs)] + extra,
                             stdout=log, stderr=subprocess.STDOUT)
        procs.append((k, p, log))

    failed = False
    for k, p, log in procs:
        rc = p.wait()
        log.close()
        tail = (BUILD / f"part_{k:02d}.log").read_text(encoding="utf-8", errors="replace").strip().splitlines()
        last = tail[-1] if tail else ""
        print(f"  shard {k}: rc={rc} {last}", flush=True)
        if rc != 0:
            failed = True
            print("\n".join(tail[-20:]))
    if failed:
        print("shard failed, aborting")
        return 1

    print(f"shards done in {time.time()-t0:.0f}s; merging", flush=True)
    counts = merge(jobs, t0)
    size = DB_PATH.stat().st_size
    print(f"done: {DB_PATH}  {size/1e6:.0f} MB  in {time.time()-t0:.0f}s")
    print(json.dumps(counts, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
