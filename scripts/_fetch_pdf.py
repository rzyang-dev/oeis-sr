import sys, urllib.request
from pathlib import Path
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
url = "https://openreview.net/pdf?id=QSIkBpEbPt"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    print("bytes:", len(data))
    Path("reports/oeis_discovery_paper.pdf").write_bytes(data)
    print("saved")
except Exception as e:
    print("ERR", type(e).__name__, e)
