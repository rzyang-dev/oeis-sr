import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
atlas = json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))
per = json.load(open(ROOT/"reports"/"periodicity930.json", encoding="utf-8"))
print("periodicity keys sample:", list(per)[:3] if isinstance(per, dict) else type(per))
# figure out structure
if isinstance(per, dict):
    sample = list(per.items())[:3]
    print(sample)
