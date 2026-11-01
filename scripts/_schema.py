import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
print(con.execute("select sql from sqlite_master where name='seq'").fetchone()[0][:800])
