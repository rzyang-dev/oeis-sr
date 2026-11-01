"""SQLite schema for the parsed OEIS snapshot."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE seq (
    aid            TEXT PRIMARY KEY,   -- A000045
    name           TEXT NOT NULL,      -- %N line
    offset1        INTEGER,            -- index of the first term
    offset2        INTEGER,            -- 1-based position of first |a(n)| > 1
    keywords       TEXT,               -- comma separated %K list
    n_terms        INTEGER NOT NULL,
    terms          TEXT NOT NULL,      -- comma separated decimal integers
    n_comments     INTEGER,
    n_formulas     INTEGER,
    n_links        INTEGER,
    n_refs         INTEGER,
    n_examples     INTEGER,
    n_programs     INTEGER,
    n_xrefs        INTEGER,
    author         TEXT,
    version        INTEGER,            -- %I revision counter
    last_edit      TEXT,               -- %I date, ISO
    all_int64      INTEGER,            -- 1 if every term fits int64
    max_abs_digits INTEGER,            -- digits of the largest |term|
    sign_class     TEXT                -- nonneg | pos | mixed | zero
);

CREATE TABLE keyword (
    aid TEXT NOT NULL,
    kw  TEXT NOT NULL
);

CREATE TABLE formula (
    aid         TEXT NOT NULL,
    idx         INTEGER NOT NULL,
    kind        TEXT NOT NULL,         -- gf | egf | closed_form | recurrence | sum | binomial | integral | other
    conjectural INTEGER NOT NULL,
    text        TEXT NOT NULL
);

CREATE TABLE xref (
    src TEXT NOT NULL,
    dst TEXT NOT NULL
);

CREATE TABLE link (
    aid  TEXT NOT NULL,
    idx  INTEGER NOT NULL,
    href TEXT NOT NULL,
    kind TEXT NOT NULL                 -- bfile | internal | external
);

CREATE TABLE program (
    aid  TEXT NOT NULL,
    lang TEXT NOT NULL,
    text TEXT NOT NULL
);

CREATE TABLE attachment (
    aid    TEXT,
    name   TEXT,                       -- b000045.txt
    ext    TEXT,
    size   INTEGER,
    source TEXT                        -- lfs | git
);
"""

INDEXES = """
CREATE INDEX idx_keyword_kw  ON keyword(kw);
CREATE INDEX idx_keyword_aid ON keyword(aid);
CREATE INDEX idx_formula_aid ON formula(aid);
CREATE INDEX idx_formula_kind ON formula(kind);
CREATE INDEX idx_xref_src    ON xref(src);
CREATE INDEX idx_xref_dst    ON xref(dst);
CREATE INDEX idx_link_aid    ON link(aid);
CREATE INDEX idx_link_kind   ON link(kind);
CREATE INDEX idx_program_aid ON program(aid);
CREATE INDEX idx_program_lang ON program(lang);
CREATE INDEX idx_attachment_aid ON attachment(aid);
CREATE INDEX idx_seq_nt      ON seq(n_terms);
CREATE INDEX idx_seq_offset  ON seq(offset1);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=OFF")
    conn.execute("PRAGMA synchronous=OFF")
    conn.execute("PRAGMA cache_size=-200000")
    return conn


def init(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)


def create_indexes(conn: sqlite3.Connection) -> None:
    conn.executescript(INDEXES)
