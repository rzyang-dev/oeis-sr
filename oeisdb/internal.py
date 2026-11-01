"""Parser for the OEIS "internal format" (*.seq) files.

An entry is a sequence of lines of the form

    %<code> <A-number> <payload>

where <code> is a single letter identifying the kind of information.  The
codes seen in the current database are::

    I  identification (version number, last edit date, old M/N numbers)
    S T U  the terms, split over up to three lines
    N  name (the canonical one-line description)
    C  comments
    D  references
    H  links (HTML anchors + free text)
    F  formulas
    e  examples
    p  Maple program
    t  Mathematica program
    o  other programs (PARI, Python, Magma, GAP, ...)
    Y  cross references to other A-numbers
    K  keywords
    O  offset: (index of first term, position of first |a(n)|>1)
    A  author
    E  extensions / edits
"""

from __future__ import annotations

import re
from pathlib import Path

ID_RE = re.compile(r"^A\d{6}$")
HREF_RE = re.compile(r'<a href="([^"]+)"')
ANUM_RE = re.compile(r"A\d{6}")
VERSION_RE = re.compile(r"#(\d+)")
DATE_RE = re.compile(r"([A-Z][a-z]{2}) (\d{1,2}) (\d{4}) (\d{2}):(\d{2}):(\d{2})")
PROG_TAG_RE = re.compile(r"^\s*\(([A-Za-z0-9+# ]{2,30})\)")
BFILE_HREF_RE = re.compile(r"^/A\d{6}/b\d{6}\.txt$")
SIMPLE_CLOSED_RE = re.compile(r"^a\(\s*n\s*\)\s*=\s*[-+0-9n()*/^ .]+$")
RECURRENCE_RE = re.compile(r"a\(\s*n\s*\)\s*=\s*[^=]*a\(\s*n\s*-\s*\d+\s*\)")
CONJECTURE_RE = re.compile(r"conjectur|empirical", re.I)

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


def _split_terms(payloads: list[str]) -> tuple[list[str], str]:
    """Join the %S/%T/%U payloads into one comma separated list of tokens."""
    parts = []
    for p in payloads:
        p = p.strip()
        if not p:
            continue
        parts.append(p[:-1] if p.endswith(",") else p)
    if not parts:
        return [], ""
    tokens = [t.strip() for t in ",".join(parts).split(",") if t.strip()]
    return tokens, ",".join(tokens)


def classify_formula(text: str) -> str:
    t = text.strip()
    if SIMPLE_CLOSED_RE.match(t):
        return "closed_form"
    if "G.f." in t:
        return "gf"
    if "E.g.f." in t:
        return "egf"
    if RECURRENCE_RE.search(t):
        return "recurrence"
    if "Sum_{" in t:
        return "sum"
    if "binomial(" in t:
        return "binomial"
    if "Integral" in t:
        return "integral"
    return "other"


def classify_link(href: str) -> str:
    if BFILE_HREF_RE.match(href):
        return "bfile"
    if href.startswith("/"):
        return "internal"
    return "external"


def parse_programs(fields: dict[str, list[str]]) -> list[tuple[str, str]]:
    """Return [(language, code)] for the %p / %t / %o lines.

    A %o block normally starts with a line such as "(PARI)" followed by the
    code lines; continuation lines are appended to the current program.
    """
    out: list[tuple[str, str]] = []
    for code, default_lang in (("p", "Maple"), ("t", "Mathematica"), ("o", "")):
        lang = default_lang
        buf: list[str] = []
        for payload in fields.get(code, []):
            m = PROG_TAG_RE.match(payload)
            if m:
                if buf and (lang or not default_lang):
                    out.append((lang or "unknown", "\n".join(buf).strip()))
                buf = []
                lang = m.group(1).strip()
                rest = payload[m.end():].strip()
                if rest:
                    buf.append(rest)
            else:
                if not buf and not lang:
                    lang = "unknown"
                buf.append(payload.strip())
        if buf:
            out.append((lang or "unknown", "\n".join(buf).strip()))
    return [(l, t) for l, t in out if t]


def parse_text(text: str, aid: str) -> dict:
    """Parse one .seq file into a plain dict (no validation, fast path)."""
    fields: dict[str, list[str]] = {}
    malformed = 0
    for ln in text.splitlines():
        if not ln:
            continue
        if len(ln) >= 11 and ln[0] == "%" and ln[2] == " ":
            f = ln[1]
            lst = fields.get(f)
            if lst is None:
                fields[f] = [ln[11:]]
            else:
                lst.append(ln[11:])
        else:
            malformed += 1

    tokens, term_text = _split_terms(fields.get("S", []) + fields.get("T", []) + fields.get("U", []))

    name = " ".join(p.strip() for p in fields.get("N", []))
    keywords = []
    if fields.get("K"):
        keywords = [k.strip() for k in fields["K"][0].split(",") if k.strip()]

    off1 = off2 = None
    if fields.get("O"):
        try:
            parts = [int(x) for x in fields["O"][0].split(",")]
            off1 = parts[0]
            if len(parts) > 1:
                off2 = parts[1]
        except ValueError:
            pass

    version = None
    last_edit = ""
    if fields.get("I"):
        ident = fields["I"][0]
        m = VERSION_RE.search(ident)
        if m:
            version = int(m.group(1))
        m = DATE_RE.search(ident)
        if m:
            mon = MONTHS.get(m.group(1))
            if mon:
                last_edit = f"{int(m.group(3)):04d}-{mon:02d}-{int(m.group(2)):02d}"

    formulas = []
    for idx, payload in enumerate(fields.get("F", [])):
        txt = payload.strip()
        if not txt:
            continue
        formulas.append({
            "idx": idx,
            "kind": classify_formula(txt),
            "conjectural": 1 if CONJECTURE_RE.search(txt) else 0,
            "text": txt,
        })

    links = []
    for idx, payload in enumerate(fields.get("H", [])):
        for href in HREF_RE.findall(payload):
            links.append({"idx": idx, "href": href, "kind": classify_link(href)})

    xrefs: list[str] = []
    seen: set[str] = set()
    for payload in fields.get("Y", []):
        for ref in ANUM_RE.findall(payload):
            if ref != aid and ref not in seen:
                seen.add(ref)
                xrefs.append(ref)

    programs = [{"lang": lang, "text": txt} for lang, txt in parse_programs(fields)]

    return {
        "aid": aid,
        "name": name,
        "offset1": off1,
        "offset2": off2,
        "keywords": keywords,
        "n_terms": len(tokens),
        "terms": term_text,
        "n_comments": len(fields.get("C", [])),
        "n_formulas": len(fields.get("F", [])),
        "n_links": len(fields.get("H", [])),
        "n_refs": len(fields.get("D", [])),
        "n_examples": len(fields.get("e", [])),
        "n_programs": len(programs),
        "n_xrefs": len(xrefs),
        "author": "; ".join(p.strip() for p in fields.get("A", [])),
        "version": version,
        "last_edit": last_edit,
        "malformed": malformed,
        "formulas": formulas,
        "links": links,
        "xrefs": xrefs,
        "programs": programs,
    }


def parse_file(path: str | Path, aid: str | None = None) -> dict:
    p = Path(path)
    if aid is None:
        aid = p.stem
    return parse_text(p.read_text(encoding="utf-8", errors="replace"), aid)


def iter_seq_files(root: str | Path):
    """Yield (aid, Path) for every .seq file below *root*."""
    for d in sorted(p for p in Path(root).iterdir() if p.is_dir()):
        for f in sorted(d.glob("*.seq")):
            yield f.stem, f


def term_values(entry: dict) -> list[int]:
    """Terms as Python ints (raises ValueError on a malformed token)."""
    if not entry["terms"]:
        return []
    return [int(t) for t in entry["terms"].split(",")]


if __name__ == "__main__":
    import json
    import sys

    e = dict(parse_file(sys.argv[1]))
    e["terms"] = (e["terms"][:120] + "...") if len(e["terms"]) > 120 else e["terms"]
    e["formulas"] = e["formulas"][:5]
    e["links"] = e["links"][:5]
    e["xrefs"] = e["xrefs"][:10]
    e["programs"] = e["programs"][:3]
    print(json.dumps(e, indent=1, ensure_ascii=False))
