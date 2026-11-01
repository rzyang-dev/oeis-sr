import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
per = json.load(open(ROOT/"reports"/"periodicity930.json", encoding="utf-8"))
print("len:", len(per))
print("first record:", per[0])
