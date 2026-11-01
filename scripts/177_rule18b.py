import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
for pat in ("%rule 18%", "%Rule 018%", "%rule18%"):
    rows = con.execute("select aid, name from seq where name like ? limit 20", (pat,)).fetchall()
    if rows:
        print("PATTERN", pat)
        for r in rows: print(" ", r[0], "|", r[1][:120])
