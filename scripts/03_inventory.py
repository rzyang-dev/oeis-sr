#!/usr/bin/env python3
"""Inventory queries over oeis.db -> reports/inventory.json (+ console summary).

Every number quoted in docs/01-oeis-data-inventory.md comes from here.

    python scripts/03_inventory.py [--bfile-sample 200]
"""
from __future__ import annotations

import json
import random
import sqlite3
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "oeis.db"
DATA = Path(r"C:\Users\ginger\oeisdata")
OUT = ROOT / "reports" / "inventory.json"

CLEAN_KW = ("cons", "base", "frac", "dead", "dupe", "recycled")


def main(argv: list[str]) -> int:
    n_sample = 200
    if "--bfile-sample" in argv:
        n_sample = int(argv[argv.index("--bfile-sample") + 1])
    t0 = time.time()
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    one = lambda sql, *a: con.execute(sql, a).fetchone()[0]
    rows = lambda sql, *a: con.execute(sql, a).fetchall()

    out: dict = {}
    out["db"] = {
        "path": str(DB),
        "size_mb": round(DB.stat().st_size / 1e6, 1),
        "meta": dict(rows("select key, value from meta")),
    }
    out["n_seqs"] = one("select count(*) from seq")
    out["terms_total"] = one("select sum(n_terms) from seq")
    out["terms_mean"] = round(out["terms_total"] / out["n_seqs"], 2)
    n = out["n_seqs"]
    out["terms_median"] = one(
        f"select n_terms from seq order by n_terms limit 1 offset {n // 2}")
    out["terms_hist"] = rows("select n_terms, count(*) from seq group by 1 order by 1")
    out["pool_by_terms"] = {
        str(thr): one(f"select count(*) from seq where n_terms >= {thr}")
        for thr in (5, 8, 10, 15, 20, 30, 50, 100)
    }
    out["int64"] = one("select count(*) from seq where all_int64=1")
    out["max_digits"] = rows("select aid, max_abs_digits from seq order by max_abs_digits desc limit 5")
    out["sign_class"] = dict(rows("select sign_class, count(*) from seq group by 1"))
    out["offset"] = dict(rows("select offset1, count(*) from seq group by 1"))
    out["offset_negative"] = one("select count(*) from seq where offset1 < 0")
    out["offset_missing"] = one("select count(*) from seq where offset1 is null")
    out["keyword_counts"] = dict(rows("select kw, count(*) from keyword group by 1 order by 2 desc"))
    out["n_distinct_keywords"] = len(out["keyword_counts"])
    out["n_keyword_pairs"] = one("select count(*) from keyword")

    out["formulas"] = {
        "lines": one("select count(*) from formula"),
        "seqs": one("select count(distinct aid) from formula"),
        "by_kind": dict(rows("select kind, count(*) from formula group by 1 order by 2 desc")),
        "seqs_by_kind": dict(rows("select kind, count(distinct aid) from formula group by 1 order by 2 desc")),
        "conjectural_lines": one("select count(*) from formula where conjectural=1"),
        "seqs_with_conjecture": one("select count(distinct aid) from formula where conjectural=1"),
    }
    out["comments"] = {
        "lines": one("select sum(n_comments) from seq"),
        "seqs": one("select count(*) from seq where n_comments > 0"),
    }
    out["refs"] = one("select sum(n_refs) from seq")
    out["examples"] = one("select sum(n_examples) from seq")

    out["links"] = {
        "hrefs": one("select count(*) from link"),
        "seqs": one("select count(distinct aid) from link"),
        "by_kind": dict(rows("select kind, count(*) from link group by 1")),
        "distinct_hrefs": one("select count(distinct href) from link"),
        "top_domains": rows(
            "select case when href like '/%' then 'oeis.org (internal)' "
            "else substr(rest, 1, coalesce(nullif(instr(rest,'/'),0), length(rest)+1)-1) end dom, "
            "count(*) n from (select href, substr(href, instr(href,'://')+3) rest from link) "
            "group by dom order by n desc limit 20"),
    }
    out["programs"] = {
        "lines": one("select count(*) from program"),
        "seqs": one("select count(distinct aid) from program"),
        "by_lang": rows("select lang, count(*) n from program group by 1 order by n desc limit 30"),
    }
    out["attachments"] = {
        "files": one("select count(*) from attachment"),
        "seqs": one("select count(distinct aid) from attachment"),
        "by_ext": rows("select ext, count(*) n, sum(size) bytes from attachment group by 1 order by n desc limit 15"),
        "total_bytes": one("select sum(size) from attachment"),
    }
    out["bfiles"] = {
        "files": one("select count(*) from attachment where ext='txt' and name like 'b%.txt'"),
        "bytes": one("select sum(size) from attachment where ext='txt' and name like 'b%.txt'"),
        "seqs_with_bfile": one(
            "select count(distinct a.aid) from attachment a join seq s on s.aid=a.aid "
            "where a.ext='txt' and a.name like 'b%.txt'"),
        "seqs_total": n,
    }
    out["xrefs"] = {
        "edges": one("select count(*) from xref"),
        "sources": one("select count(distinct src) from xref"),
        "targets": one("select count(distinct dst) from xref"),
        "targets_in_db": one("select count(distinct x.dst) from xref x join seq s on s.aid=x.dst"),
        "top_targets": rows("select dst, count(*) n from xref group by 1 order by n desc limit 15"),
        "self_loops": one("select count(*) from xref where src=dst"),
    }
    out["last_edit_years"] = rows(
        "select substr(last_edit,1,4) y, count(*) n from seq "
        "where last_edit<>'' group by 1 order by 1")
    out["names"] = {
        "empty": one("select count(*) from seq where trim(name)=''"),
        "mean_len": round(one("select avg(length(name)) from seq"), 1),
    }

    # ---- derived "symbolic-regression ready" slices ----
    not_clean = " and ".join(
        f"not exists (select 1 from keyword k where k.aid=s.aid and k.kw='{kw}')" for kw in CLEAN_KW)
    has_formula = ("exists (select 1 from formula f where f.aid=s.aid "
                   "and f.kind in ('closed_form','gf','egf','recurrence') and f.conjectural=0)")
    has_bfile = "exists (select 1 from attachment a where a.aid=s.aid and a.name like 'b%.txt')"

    def count_clean(min_terms: int, extra: str = "") -> int:
        sql = (f"select count(*) from seq s where s.n_terms >= {min_terms} "
               f"and s.all_int64 = 1 and {not_clean}")
        if extra:
            sql += f" and {extra}"
        return one(sql)

    out["sr_pool"] = {
        "ge10_int64_clean": count_clean(10),
        "ge20_int64_clean": count_clean(20),
        "ge10_int64_clean_with_formula": count_clean(10, has_formula),
        "ge10_int64_clean_with_bfile": count_clean(10, has_bfile),
        "ge10_int64_clean_formula_and_bfile": count_clean(10, has_formula + " and " + has_bfile),
    }
    out["seqs_with_any_formula"] = one("select count(distinct aid) from seq where n_formulas>0")
    out["seqs_with_program"] = one("select count(*) from seq where n_programs>0")
    out["seqs_with_link"] = one("select count(*) from seq where n_links>0")

    # ---- b-file sample: size, and agreement with the %S terms ----
    sample = rows(
        "select a.aid, a.size from attachment a join seq s on s.aid=a.aid "
        "where a.ext='txt' and a.name like 'b%.txt' order by random() limit ?", n_sample)
    per_file = []
    agree = checked = 0
    bad = []
    for aid, size in sample:
        p = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
        if not p.exists():
            continue
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        vals = {}
        for ln in lines:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            parts = ln.split()
            if len(parts) >= 2:
                try:
                    vals[int(parts[0])] = parts[1]
                except ValueError:
                    pass
        per_file.append((len(vals), size, aid))
        if aid and vals:
            off1, terms = con.execute("select offset1, terms from seq where aid=?", (aid,)).fetchone()
            if off1 is not None and terms:
                t = terms.split(",")
                ok = all(vals.get(off1 + i) == v for i, v in enumerate(t))
                checked += 1
                agree += int(ok)
                if not ok and len(bad) < 5:
                    bad.append(aid)
    if per_file:
        out["bfile_sample"] = {
            "n": len(per_file),
            "terms_median": statistics.median(x[0] for x in per_file),
            "terms_mean": round(statistics.mean(x[0] for x in per_file), 1),
            "terms_min": min(x[0] for x in per_file),
            "terms_max": max(x[0] for x in per_file),
            "size_median_kb": round(statistics.median(x[1] for x in per_file) / 1024, 1),
            "checked_against_seq_terms": checked,
            "agree": agree,
            "mismatch_examples": bad,
        }

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---------------- console summary ----------------
    print(f"OEIS inventory  ({out['db']['size_mb']} MB, {time.time()-t0:.1f}s)")
    print(f"entries {n:,}   terms {out['terms_total']:,}   median/entry {out['terms_median']}   mean {out['terms_mean']}")
    print("pool by n_terms:", out["pool_by_terms"])
    print("int64-safe:", out["int64"], " sign:", out["sign_class"])
    print("keyword pairs:", out["n_keyword_pairs"], " distinct:", out["n_distinct_keywords"])
    print("formulas:", out["formulas"]["lines"], "lines on", out["formulas"]["seqs"], "seqs")
    print("  by kind:", out["formulas"]["by_kind"])
    print("  by seqs:", out["formulas"]["seqs_by_kind"])
    print("links:", out["links"]["by_kind"], " distinct hrefs:", out["links"]["distinct_hrefs"])
    print("programs:", out["programs"]["seqs"], "seqs;", out["programs"]["by_lang"][:6])
    print("attachments:", out["attachments"]["files"], "files,",
          round(out["attachments"]["total_bytes"] / 1e9, 2), "GB")
    print("bfiles:", out["bfiles"])
    print("xref edges:", out["xrefs"]["edges"], " targets in db:", out["xrefs"]["targets_in_db"])
    print("sr pool:", out["sr_pool"])
    if "bfile_sample" in out:
        print("bfile sample:", out["bfile_sample"])
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
