import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
for aid in ("A306559", "A039982", "A285383", "A267442"):
    name = con.execute("select name from seq where aid=?", (aid,)).fetchone()
    print("="*70)
    print(aid, ":", name[0] if name else None)
    for (t,) in con.execute("select text from stmt where aid=? order by rowid limit 6", (aid,)):
        print("   ", t[:220])
