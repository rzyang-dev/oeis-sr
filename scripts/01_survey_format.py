#!/usr/bin/env python3
r"""Census of the OEIS .seq "internal format" files.

Single streaming pass over C:\Users\ginger\oeisdata\seq\*.seq that answers:
which field codes exist, how clean the file format is, how many terms each
entry carries, which keywords occur, how references/links behave, etc.

Writes  reports/format_survey.json  (machine readable, all numbers)
and     reports/format_survey.txt   (human readable summary).

Usage:  python scripts/01_survey_format.py [--limit N]
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Users\ginger\oeisdata\seq")
PROJ = Path(__file__).resolve().parent.parent
OUT_JSON = PROJ / "reports" / "format_survey.json"
OUT_TXT = PROJ / "reports" / "format_survey.txt"

ID_RE = re.compile(r"^A\d{6}$")
HREF_RE = re.compile(r'<a href="([^"]+)"')
ANUM_RE = re.compile(r"A\d{6}")
VERSION_RE = re.compile(r"#(\d+)")
DATE_RE = re.compile(r"([A-Z][a-z]{2}) (\d{2}) (\d{4})")

# syntactic markers inside %F formula lines (case sensitive where useful)
FORMULA_MARKERS = {
    "a(n) =": "a(n) =",
    "G.f.": "G.f.",
    "E.g.f.": "E.g.f.",
    "Sum_": "Sum_{",
    "Product_": "Product_{",
    "binomial(": "binomial(",
    "sqrt(": "sqrt(",
    "floor(": "floor(",
    "ceiling(": "ceiling(",
    "Integral": "Integral",
    "n!": "n!",
    "Mod": " mod ",
}
CLOSED_FORM_RE = re.compile(r"^a\(\s*n\s*\)\s*=\s*[-+0-9n()*/^ .]+$")
LINEAR_REC_RE = re.compile(r"a\(\s*n\s*\)\s*=\s*[^=]*a\(\s*n\s*-\s*1\s*\)")
CONJECTURE_RE = re.compile(r"conjectur|empirical", re.I)


def is_seq_id(s: str) -> bool:
    return len(s) == 7 and s[0] == "A" and s[1:].isdigit()


class DSU:
    __slots__ = ("parent",)

    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def add(self, x: str) -> None:
        if x not in self.parent:
            self.parent[x] = x

    def find(self, x: str) -> str:
        p = self.parent
        root = x
        while p[root] != root:
            root = p[root]
        while p[x] != root:
            p[x], x = root, p[x]
        return root

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def pct(n: int, d: int) -> float:
    return round(100.0 * n / d, 2) if d else 0.0


def main(argv: list[str]) -> int:
    limit = None
    if "--limit" in argv:
        limit = int(argv[argv.index("--limit") + 1])

    t0 = time.time()
    field_files: Counter[str] = Counter()
    field_lines: Counter[str] = Counter()
    unknown_field: Counter[str] = Counter()
    malformed: list[str] = []
    bad_encoding: list[str] = []
    cr_files = 0
    bom_files = 0
    trailing_ws_lines = 0

    n_files = 0
    total_bytes = 0
    sizes: list[int] = []
    ids: list[str] = []
    dir_mismatch = 0

    n_terms_hist: Counter[int] = Counter()
    n_terms_total = 0
    max_terms: list[tuple[int, str]] = []
    max_digits: list[tuple[int, str]] = []
    bad_term_token: list[str] = []
    int64_ok = 0
    empty_terms_list: list[str] = []

    kw_counts: Counter[str] = Counter()
    kw_combo: Counter[tuple[str, ...]] = Counter()
    offset_first: Counter[int] = Counter()
    offset_second: Counter[int] = Counter()
    bad_offset: list[str] = []

    formula_seq = 0
    formula_lines = 0
    formula_hist: Counter[int] = Counter()
    marker_counts: Counter[str] = Counter()
    closed_seqs = 0
    linear_rec_seqs = 0
    conjecture_formula_seqs = 0
    long_formula_seqs = 0  # >= 20 formula lines

    comment_lines = 0
    comment_seq = 0
    comment_hist: Counter[int] = Counter()
    ref_lines = 0
    example_lines = 0
    program_lines = 0
    program_seq = 0
    prog_lang: Counter[str] = Counter()

    link_lines = 0
    link_seq = 0
    link_total = 0
    link_internal = 0
    link_external = 0
    link_bfile = 0
    domains: Counter[str] = Counter()
    link_hist: Counter[int] = Counter()

    xref_lines = 0
    xref_seq = 0
    xref_edges = 0
    xref_targets: Counter[str] = Counter()
    xref_hist: Counter[int] = Counter()
    dsu = DSU()

    years = Counter()
    versions: list[int] = []
    dates: list[str] = []
    name_missing = 0
    author_missing = 0

    has_formula = 0
    has_program = 0
    has_link = 0
    has_xref = 0

    def walk():
        for d in sorted(p for p in ROOT.iterdir() if p.is_dir()):
            for f in sorted(d.glob("*.seq")):
                yield d.name, f

    for dirname, path in walk():
        if limit and n_files >= limit:
            break
        n_files += 1
        raw = path.read_bytes()
        total_bytes += len(raw)
        sizes.append(len(raw))
        aid = path.stem
        ids.append(aid)
        if dirname != "A" + aid[1:4]:
            dir_mismatch += 1
        if raw.startswith(b"\xef\xbb\xbf"):
            bom_files += 1
        if b"\r" in raw:
            cr_files += 1
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            bad_encoding.append(aid)
            text = raw.decode("utf-8", errors="replace")

        seen_fields: set[str] = set()
        terms_parts: list[str] = []
        nf = 0
        nc = 0
        nl = 0
        nx = 0
        name = ""
        kw: list[str] = []
        off: list[int] = []
        n_prog = 0
        max_v = 0
        max_dig = 0

        for line in text.split("\n"):
            if not line:
                continue
            if not line.startswith("%"):
                if len(malformed) < 30:
                    malformed.append(f"{aid}: {line[:120]!r}")
                continue
            if len(line) < 11 or line[2] != " " or not line[1].isalpha():
                if len(malformed) < 30:
                    malformed.append(f"{aid}: {line[:120]!r}")
                continue
            field = line[1]
            file_id = line[3:10]
            payload = line[11:]
            if not ID_RE.match(file_id) or file_id != aid:
                if len(malformed) < 30:
                    malformed.append(f"{aid}: bad id prefix {line[:40]!r}")
            seen_fields.add(field)
            field_lines[field] += 1
            if payload != payload.rstrip():
                trailing_ws_lines += 1

            if field in ("S", "T", "U"):
                terms_parts.append(payload.strip())
            elif field == "N":
                name = payload
            elif field == "K":
                kw = [k.strip() for k in payload.split(",") if k.strip()]
            elif field == "O":
                try:
                    off = [int(x) for x in payload.split(",")]
                except ValueError:
                    if len(bad_offset) < 30:
                        bad_offset.append(f"{aid}: {payload!r}")
            elif field == "C":
                nc += 1
            elif field == "D":
                ref_lines += 1
            elif field == "H":
                nl += 1
                link_lines += 1
                hrefs = HREF_RE.findall(payload)
                link_total += len(hrefs)
                for h in hrefs:
                    if h.startswith("/"):
                        link_internal += 1
                        if re.match(r"^/A\d{6}/b\d{6}\.txt$", h):
                            link_bfile += 1
                    elif "://" in h:
                        link_external += 1
                        domains[h.split("://", 1)[1].split("/", 1)[0].lower()] += 1
            elif field == "F":
                nf += 1
                formula_lines += 1
                for key, sub in FORMULA_MARKERS.items():
                    if sub in payload:
                        marker_counts[key] += 1
                stripped = payload.strip()
                if CLOSED_FORM_RE.match(stripped):
                    marker_counts["closed_form_match"] += 1
                if CONJECTURE_RE.search(payload):
                    marker_counts["conjecture_word"] += 1
            elif field == "e":
                example_lines += 1
            elif field in ("p", "t", "o"):
                n_prog += 1
                program_lines += 1
                m = re.match(r"^\s*\(([A-Za-z0-9+# ]{2,30})\)", payload)
                if m:
                    prog_lang[m.group(1).strip()] += 1
                elif field == "t":
                    prog_lang["Mathematica"] += 1
                elif field == "p":
                    prog_lang["Maple"] += 1
                else:
                    prog_lang["(unlabelled)"] += 1
            elif field == "Y":
                nx += 1
                xref_lines += 1
                refs = {r for r in ANUM_RE.findall(payload) if r != aid}
                for r in refs:
                    dsu.add(aid)
                    dsu.add(r)
                    dsu.union(aid, r)
                    xref_targets[r] += 1
                    xref_edges += 1
            elif field == "A":
                if not payload.strip():
                    author_missing += 1
            elif field == "I":
                m = VERSION_RE.search(payload)
                if m:
                    versions.append(int(m.group(1)))
                m = DATE_RE.search(payload)
                if m:
                    years[m.group(3)] += 1
                    dates.append(payload)

        for f in seen_fields:
            field_files[f] += 1
        if not name.strip():
            name_missing += 1

        # ---- terms ----
        parts = [p for p in terms_parts if p]
        joined = ",".join(p.rstrip(",").rstrip() for p in parts)
        tokens = [t.strip() for t in joined.split(",")] if joined else []
        tokens = [t for t in tokens if t]
        n_terms = len(tokens)
        n_terms_total += n_terms
        n_terms_hist[n_terms] += 1
        if n_terms == 0:
            empty_terms_list.append(aid)
        if len(max_terms) < 5 or n_terms > max_terms[0][0]:
            max_terms.append((n_terms, aid))
            max_terms.sort(reverse=True)
            max_terms = max_terms[:5]
        all_i64 = True
        for t in tokens:
            tt = t.lstrip("+")
            try:
                v = int(tt)
            except ValueError:
                if len(bad_term_token) < 30:
                    bad_term_token.append(f"{aid}: {t!r}")
                all_i64 = False
                continue
            d = len(t.lstrip("+-"))
            if d > max_dig:
                max_dig = d
            if abs(v) > max_v:
                max_v = abs(v)
            if not (-2**63 <= v < 2**63):
                all_i64 = False
        if all_i64:
            int64_ok += 1
        if len(max_digits) < 5 or max_dig > max_digits[0][0]:
            max_digits.append((max_dig, aid))
            max_digits.sort(reverse=True)
            max_digits = max_digits[:5]

        # ---- keywords ----
        for k in kw:
            kw_counts[k] += 1
        if kw:
            kw_combo[tuple(kw)] += 1
        if off:
            offset_first[off[0]] += 1
            if len(off) > 1:
                offset_second[off[1]] += 1
        else:
            if len(bad_offset) < 30:
                bad_offset.append(f"{aid}: <missing>")

        if nf:
            has_formula += 1
            formula_seq += 1
            formula_hist[min(nf, 50)] += 1
            if nf >= 20:
                long_formula_seqs += 1
        if n_prog:
            has_program += 1
            program_seq += 1
        if nl:
            has_link += 1
            link_seq += 1
            link_hist[min(nl, 200)] += 1
        if nx:
            has_xref += 1
            xref_seq += 1
            xref_hist[min(nx, 100)] += 1
        if nc:
            comment_seq += 1
            comment_hist[min(nc, 100)] += 1
            comment_lines += nc

        if n_files % 25000 == 0:
            print(f"  {n_files} files  {time.time()-t0:.1f}s", flush=True)

    # ---- post pass ----
    components = 0
    seen_roots: set[str] = set()
    for x in dsu.parent:
        r = dsu.find(x)
        if r not in seen_roots:
            seen_roots.add(r)
            components += 1

    ids_sorted = sorted(ids)
    missing_ids = 0
    if ids_sorted:
        lo, hi = int(ids_sorted[0][1:]), int(ids_sorted[-1][1:])
        missing_ids = (hi - lo + 1) - len(ids_sorted)

    # pool: how many entries look usable as regression targets
    pool = {
        "ge_5_terms": sum(v for k, v in n_terms_hist.items() if k >= 5),
        "ge_8_terms": sum(v for k, v in n_terms_hist.items() if k >= 8),
        "ge_10_terms": sum(v for k, v in n_terms_hist.items() if k >= 10),
        "ge_15_terms": sum(v for k, v in n_terms_hist.items() if k >= 15),
        "ge_20_terms": sum(v for k, v in n_terms_hist.items() if k >= 20),
        "int64_safe": int64_ok,
    }

    out = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "root": str(ROOT),
        "n_files": n_files,
        "total_bytes": total_bytes,
        "size": {
            "min": min(sizes) if sizes else 0,
            "max": max(sizes) if sizes else 0,
            "mean": round(sum(sizes) / len(sizes), 1) if sizes else 0,
        },
        "ids": {
            "n": len(ids_sorted),
            "first": ids_sorted[0] if ids_sorted else None,
            "last": ids_sorted[-1] if ids_sorted else None,
            "span_missing": missing_ids,
            "dir_mismatch": dir_mismatch,
        },
        "encoding": {
            "non_utf8_files": len(bad_encoding),
            "non_utf8_examples": bad_encoding[:10],
            "cr_files": cr_files,
            "bom_files": bom_files,
            "trailing_ws_lines": trailing_ws_lines,
        },
        "fields": {
            "files_with": dict(field_files.most_common()),
            "lines_total": dict(field_lines.most_common()),
            "unknown": dict(unknown_field),
        },
        "anomalies": {
            "malformed_examples": malformed,
            "bad_offsets": bad_offset,
            "bad_term_tokens": bad_term_token,
            "name_missing": name_missing,
            "author_missing": author_missing,
            "zero_terms": len(empty_terms_list),
            "zero_terms_examples": empty_terms_list[:10],
        },
        "terms": {
            "total": n_terms_total,
            "mean": round(n_terms_total / n_files, 2) if n_files else 0,
            "hist": sorted(n_terms_hist.items()),
            "max": max_terms,
            "max_digits": max_digits,
            "pool": pool,
        },
        "keywords": {
            "n_with_keywords": sum(kw_counts.values()) and n_files,
            "counts": kw_counts.most_common(),
            "n_distinct_combos": len(kw_combo),
            "top_combos": [("|".join(c), v) for c, v in kw_combo.most_common(15)],
        },
        "offset": {
            "first": offset_first.most_common(20),
            "second": offset_second.most_common(20),
            "n_negative_first": sum(v for k, v in offset_first.items() if k < 0),
        },
        "formulas": {
            "sequences_with": formula_seq,
            "lines": formula_lines,
            "pct_sequences": pct(formula_seq, n_files),
            "n_formulas_hist": sorted(formula_hist.items()),
            "seqs_ge_20": long_formula_seqs,
            "markers": marker_counts.most_common(),
        },
        "comments": {"sequences_with": comment_seq, "lines": comment_lines, "pct": pct(comment_seq, n_files)},
        "refs": {"lines": ref_lines},
        "examples": {"lines": example_lines},
        "programs": {
            "sequences_with": program_seq,
            "lines": program_lines,
            "pct_sequences": pct(program_seq, n_files),
            "languages": prog_lang.most_common(40),
        },
        "links": {
            "sequences_with": link_seq,
            "lines": link_lines,
            "hrefs_total": link_total,
            "hrefs_internal": link_internal,
            "hrefs_external": link_external,
            "hrefs_bfile": link_bfile,
            "pct_sequences": pct(link_seq, n_files),
            "n_links_hist": sorted(link_hist.items())[:60],
            "top_domains": domains.most_common(40),
            "n_distinct_domains": len(domains),
        },
        "xrefs": {
            "sequences_with": xref_seq,
            "lines": xref_lines,
            "edges": xref_edges,
            "pct_sequences": pct(xref_seq, n_files),
            "n_refs_hist": sorted(xref_hist.items()),
            "graph": {
                "nodes_touched": len(dsu.parent),
                "components": components,
            },
            "top_targets": xref_targets.most_common(25),
        },
        "dates": {
            "years": years.most_common(),
            "version_max": max(versions) if versions else None,
            "version_mean": round(sum(versions) / len(versions), 1) if versions else None,
        },
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

    L = []
    A = L.append
    A(f"OEIS .seq format survey  ({out['generated_at']})")
    A(f"root: {ROOT}")
    A(f"files: {n_files:,}   bytes: {total_bytes/1e6:.1f} MB   mean size {out['size']['mean']} B")
    A(f"A-numbers: {ids_sorted[0]} .. {ids_sorted[-1]}   missing in span: {missing_ids}")
    A(f"non-UTF8 files: {len(bad_encoding)}   CR files: {cr_files}   BOM files: {bom_files}")
    A("")
    A("FIELD CODES (files containing at least one such line / total lines):")
    for f, n in field_files.most_common():
        A(f"  %{f}  {n:>7,} files  {field_lines[f]:>9,} lines")
    A("")
    A(f"TERMS: total {n_terms_total:,}  mean/entry {out['terms']['mean']}")
    A("  pooled usable target sizes: " + ", ".join(f"{k}={v:,}" for k, v in pool.items()))
    A("  entries with most terms: " + ", ".join(f"{a}({n})" for n, a in max_terms))
    A("  largest term digit counts: " + ", ".join(f"{a}({n}d)" for n, a in max_digits))
    A("")
    A("KEYWORDS (top 40):")
    for k, n in kw_counts.most_common(40):
        A(f"  {k:<12} {n:>7,}  ({pct(n, n_files)}%)")
    A("")
    A(f"OFFSET first: " + ", ".join(f"{k}:{v:,}" for k, v in offset_first.most_common(12)))
    A("")
    A(f"FORMULAS: {formula_seq:,} seqs ({pct(formula_seq,n_files)}%), {formula_lines:,} lines, "
      f"{long_formula_seqs:,} seqs with >=20")
    for k, n in marker_counts.most_common():
        A(f"  {k:<22} {n:,}")
    A("")
    A(f"COMMENTS: {comment_seq:,} seqs, {comment_lines:,} lines")
    A(f"REFS: {ref_lines:,} lines    EXAMPLES: {example_lines:,} lines")
    A(f"PROGRAMS: {program_seq:,} seqs ({pct(program_seq,n_files)}%), {program_lines:,} lines")
    A("  " + ", ".join(f"{k}:{v:,}" for k, v in prog_lang.most_common(15)))
    A("")
    A(f"LINKS: {link_seq:,} seqs, {link_lines:,} lines, {link_total:,} hrefs "
      f"(internal {link_internal:,}, external {link_external:,}, b-file {link_bfile:,})")
    A("  top domains: " + ", ".join(f"{d}:{n:,}" for d, n in domains.most_common(12)))
    A("")
    A(f"XREFS: {xref_seq:,} seqs, {xref_edges:,} edges, "
      f"graph nodes {len(dsu.parent):,} in {components:,} components")
    A("  top targets: " + ", ".join(f"{t}:{n:,}" for t, n in xref_targets.most_common(10)))
    A("")
    A(f"VERSIONS: mean {out['dates']['version_mean']}   years: " +
      ", ".join(f"{y}:{n:,}" for y, n in years.most_common(8)))
    A("")
    A(f"ANOMALIES: malformed={len(malformed)} bad_offsets={len(bad_offset)} "
      f"bad_terms={len(bad_term_token)} zero_terms={len(empty_terms_list)} "
      f"name_missing={name_missing} author_missing={author_missing}")

    OUT_TXT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"\nWrote {OUT_JSON} and {OUT_TXT}  in {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
