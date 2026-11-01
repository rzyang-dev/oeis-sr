import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from collections import Counter
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
per = json.load(open(ROOT/"reports"/"periodicity930.json", encoding="utf-8"))
print(Counter(r["period"] for r in per).most_common(20))
print(per[:5])
