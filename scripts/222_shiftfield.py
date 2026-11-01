import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
rows = json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))
atlas = {r["aid"]: r for r in rows}
r = atlas["A268411"]
print("shift:", r["shift"], "type of trans:", type(r["trans"]).__name__, "type out:", type(r["out"]).__name__)
print("out:", r["out"])
from collections import Counter
print("shift distribution:", Counter(x["shift"] for x in rows).most_common(8))
