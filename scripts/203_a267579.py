import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
for aid in ("A267579", "A267442", "A285384", "A347523"):
    r = con.execute("select name, terms, offset1 from seq where aid=?", (aid,)).fetchone()
    if r:
        print(f"{aid} (offset {r[2]}): {r[0][:150]}")
        print(f"   terms: {r[1][:70]}")
    else:
        print(aid, "NOT IN DB")
