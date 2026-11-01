import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
for aid in ("A217586",):
    for (t,) in con.execute("select text from stmt where aid=? order by rowid", (aid,)):
        print("  *", t[:400])
