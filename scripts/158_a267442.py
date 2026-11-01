import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
con = sqlite3.connect("file:oeis.db?mode=ro", uri=True)
print("NAME:", con.execute("select name from seq where aid='A267442'").fetchone()[0])
for (f, t) in con.execute("select field, text from stmt where aid='A267442' order by rowid"):
    print(f"[{f}] {t[:300]}")
