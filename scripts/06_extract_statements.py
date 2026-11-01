#!/usr/bin/env python3
"""Extract inter-sequence references from %N / %F / %C lines into oeis.db.

Every line that mentions another A-number becomes one row in

    stmt(aid, field, idx, kind, text)
    stmt_ref(aid, field, idx, dst)

kind is a rough statement about the *role* of the reference:

    def    the line is an equation/definition of this sequence that uses the
           other sequence (a(n) = ..., row sums of A..., ...)
    alias  a "where x = A000045" clause inside an %F line
    ref    the other sequence is only mentioned (cf., see also, ...)

Usage:
    python scripts/06_extract_statements.py            # full build, 8 shards
    python scripts/06_extract_statements.py --shard 3 --of 8
"""
from __future__ import annotations

import json
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(r"C:\Users\ginger\oeisdata")
SEQ = DATA / "seq"
BUILD = ROOT / "build"
DB = ROOT / "oeis.db"

ANUM = re.compile(r"A\d{6}")
ASSIGN = re.compile(r"^\s*a\([^)]{0,14}\)\s*=")
A_EQ = re.compile(r"a\(\s*n\s*\)\s*=")
DEF_PHRASES = (
    "equals a", "row sums of a", "row sum of a", "partial sums of a",
    "partial sum of a", "inverse binomial transform", "binomial transform",
    "euler transform", "inverse euler transform", "moebius transform",
    "difference between", "sum of the", "product of the", "n-th term of a",
    "a(n) = a", "is a(a", "is a(a",
)
REF_MARKERS = ("(see a", "[see a", "cf. a", "see also a", "see the comments in a")

SCHEMA = """
CREATE TABLE stmt (
    aid   TEXT NOT NULL,
    field TEXT NOT NULL,      -- N | F | C
    idx   INTEGER NOT NULL,
    kind  TEXT NOT NULL,      -- def | alias | ref
    text  TEXT NOT NULL
);
CREATE TABLE stmt_ref (
    aid   TEXT NOT NULL,
    field TEXT NOT NULL,
    idx   INTEGER NOT NULL,
    dst   TEXT NOT NULL
);
"""


def classify(field: str, s: str) -> str:
    low = s.lower()
    if field == "N":
        if "a(n) =" in s:
            return "def"
        if any(p in low for p in DEF_PHRASES):
            return "def"
        if any(m in low for m in REF_MARKERS):
            return "ref"
        return "def"
    if field == "F":
        if ASSIGN.match(s):
            return "def"
        if "where" in low and "=" in s:
            return "alias"
        if "=" in s and "a(" in s:
            return "def"
        return "ref"
    # C
    if A_EQ.search(s):
        return "def"
    if any(p in low for p in DEF_PHRASES):
        return "def"
    return "ref"


def scan_shard(k: int, of: int) -> dict:
    t0 = time.time()
    dirs = sorted(str(p) for p in SEQ.iterdir() if p.is_dir())[k::of]
    out = BUILD / f"stmt_{k:02d}.sqlite"
    if out.exists():
        out.unlink()
    conn = sqlite3.connect(str(out))
    conn.execute("PRAGMA journal_mode=OFF")
    conn.execute("PRAGMA synchronous=OFF")
    conn.executescript(SCHEMA)

    s_rows: list[tuple] = []
    r_rows: list[tuple] = []
    n_lines = 0
    n_files = 0

    def flush() -> None:
        nonlocal s_rows, r_rows
        if s_rows:
            conn.executemany("INSERT INTO stmt VALUES (?,?,?,?,?)", s_rows)
            conn.executemany("INSERT INTO stmt_ref VALUES (?,?,?,?)", r_rows)
        s_rows, r_rows = [], []

    for d in dirs:
        for f in sorted(Path(d).glob("*.seq")):
            aid = f.stem
            n_files += 1
            text = f.read_text(encoding="utf-8", errors="replace")
            counters = {"N": 0, "F": 0, "C": 0}
            for line in text.splitlines():
                if len(line) < 12 or line[0] != "%":
                    continue
                field = line[1]
                if field not in counters:
                    continue
                payload = line[11:]
                if "A" not in payload:
                    continue
                refs = [r for r in ANUM.findall(payload) if r != aid]
                if not refs:
                    continue
                idx = counters[field]
                counters[field] = idx + 1
                kind = classify(field, payload)
                s_rows.append((aid, field, idx, kind, payload[:600]))
                for r in dict.fromkeys(refs):
                    r_rows.append((aid, field, idx, r))
                n_lines += 1
                if len(s_rows) >= 5000:
                    flush()
    flush()
    conn.commit()
    conn.close()
    return {"shard": k, "files": n_files, "lines": n_lines,
            "seconds": round(time.time() - t0, 1)}


def merge(jobs: int, t0: float) -> None:
    conn = sqlite3.connect(str(DB))
    conn.execute("DROP TABLE IF EXISTS stmt")
    conn.execute("DROP TABLE IF EXISTS stmt_ref")
    conn.execute("DROP INDEX IF EXISTS idx_stmt_ref_dst")
    conn.execute("DROP INDEX IF EXISTS idx_stmt_aid")
    conn.executescript(SCHEMA)
    for k in range(jobs):
        part = BUILD / f"stmt_{k:02d}.sqlite"
        if not part.exists():
            continue
        conn.execute(f"ATTACH DATABASE '{part.as_posix()}' AS p{k}")
        conn.execute(f"INSERT INTO stmt SELECT * FROM p{k}.stmt")
        conn.execute(f"INSERT INTO stmt_ref SELECT * FROM p{k}.stmt_ref")
        conn.commit()
        conn.execute(f"DETACH DATABASE p{k}")
    print(f"merged in {time.time()-t0:.0f}s; indexing", flush=True)
    conn.execute("CREATE INDEX idx_stmt_aid ON stmt(aid)")
    conn.execute("CREATE INDEX idx_stmt_ref_dst ON stmt_ref(dst)")
    conn.execute("CREATE INDEX idx_stmt_ref_aid ON stmt_ref(aid)")
    conn.commit()
    n_stmt = conn.execute("select count(*) from stmt").fetchone()[0]
    n_ref = conn.execute("select count(*) from stmt_ref").fetchone()[0]
    by_kind = conn.execute("select kind, count(*) from stmt group by 1 order by 2 desc").fetchall()
    conn.close()
    print(f"stmt rows: {n_stmt:,}   stmt_ref rows: {n_ref:,}")
    print("by kind:", by_kind)


def main(argv: list[str]) -> int:
    if "--shard" in argv:
        k = int(argv[argv.index("--shard") + 1])
        of = int(argv[argv.index("--of") + 1])
        print(json.dumps(scan_shard(k, of)))
        return 0

    jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 8
    t0 = time.time()
    BUILD.mkdir(exist_ok=True)
    procs = []
    for k in range(jobs):
        log = open(BUILD / f"stmt_{k:02d}.log", "w", encoding="utf-8")
        p = subprocess.Popen([sys.executable, str(Path(__file__).resolve()),
                              "--shard", str(k), "--of", str(jobs)],
                             stdout=log, stderr=subprocess.STDOUT)
        procs.append((k, p, log))
    ok = True
    for k, p, log in procs:
        rc = p.wait()
        log.close()
        if rc != 0:
            ok = False
            print(f"shard {k} failed")
            print((BUILD / f"stmt_{k:02d}.log").read_text(errors="replace")[-2000:])
    if not ok:
        return 1
    print(f"scanned in {time.time()-t0:.0f}s", flush=True)
    merge(jobs, t0)
    print(f"done in {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
