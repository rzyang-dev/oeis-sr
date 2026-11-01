import json, sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
print("NAME:", con.execute("select name from seq where aid='A216059'").fetchone()[0])
for (f, t) in con.execute("select field, text from stmt where aid='A216059' order by rowid"):
    print(f"  [{f}] {t[:200]}")
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
for r in rows:
    if r["aid"] == "A216059":
        print("\nstates:", r["states"], "out:", r["out"])
        print("trans:", r["trans"])
        print("val:", r["val_ok"], "/", r["val_total"])
