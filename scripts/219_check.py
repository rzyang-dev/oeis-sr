import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
for aid in ("A209229", "A255738", "A268411", "A295890", "A392736"):
    r = con.execute("select name, terms from seq where aid=?", (aid,)).fetchone()
    if r:
        print(f"{aid}: {r[0][:80]}")
        print(f"   {r[1][:70]}")
    else:
        print(aid, "NOT IN DB")
