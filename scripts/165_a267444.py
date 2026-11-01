import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
for aid in ("A267444", "A267417"):
    r = con.execute("select aid, name from seq where aid=?", (aid,)).fetchone()
    print(r)
    for (t,) in con.execute("select text from stmt where aid=? order by rowid limit 4", (aid,)):
        print("   ", t[:200])
