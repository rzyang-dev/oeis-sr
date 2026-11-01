import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
for aid in ("A267442", "A284948", "A285383"):
    print("="*70)
    print(aid, con.execute("select name from seq where aid=?", (aid,)).fetchone()[0])
    for (t,) in con.execute("select text from stmt where aid=? order by rowid", (aid,)):
        if any(k in t.lower() for k in ("conjecture", "confirm", "correct", "proved", "proof")):
            print("  *", t[:300])
