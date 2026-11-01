import json, sys, urllib.request
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
KEY = (ROOT / "APIkey").read_text(encoding="utf-8").strip()
def search(query, count=5):
    body = json.dumps({"query": query[:128], "count": count, "need_content": True}).encode()
    req = urllib.request.Request("https://api.deepseek.com/v1/tools/search", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())
qs = ["A267442 A043545 Rule 129 cellular automaton",
      "A284948 A096268 period doubling",
      "A285383 A035263 OEIS",
      "A270803 A151666"]
for q in qs:
    print("="*70); print("Q:", q)
    try: res = search(q)
    except Exception as e:
        print("ERR", e); continue
    for x in res.get("results", [])[:3]:
        print("-", (x.get("title") or "")[:90])
        print("  ", (x.get("url") or "")[:100])
        print("  ", ((x.get("content") or x.get("summary") or "").replace("\n"," "))[:200])
