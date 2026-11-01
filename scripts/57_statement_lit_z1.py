import json, sys, re, time, urllib.request
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
KEY = (ROOT / "APIkey").read_text(encoding="utf-8").strip()
con = sqlite3.connect("file:" + (ROOT / "oeis.db").as_posix() + "?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
fame = dict(con.execute("select aid, count(*) from formula group by 1"))
ver = json.load(open(ROOT / "reports" / "closed_loop_verified.json", encoding="utf-8"))
z1 = [x for x in ver if x["kind"] == "z1"]
top = sorted(z1, key=lambda y: -fame.get(y["aid"], 0))[:15]

def search(query, count=4):
    body = json.dumps({"query": query[:128], "count": count, "need_content": True}).encode()
    req = urllib.request.Request("https://api.deepseek.com/v1/tools/search", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

out = []
for x in top:
    aid = x["aid"]
    nm = re.sub(r"^(Number of|Expansion of|E\.g\.f\.:|G\.f\.:)\s*", "", names.get(aid, ""))
    nm = nm[:70].strip(" .")
    q = f"{nm} congruence modulo 5"
    try:
        res = search(q)
    except Exception as e:
        print("ERR", aid, e, flush=True); continue
    hits = []
    for y in res.get("results", []):
        blob = ((y.get("title") or "") + " " + (y.get("summary") or "") + " " + (y.get("content") or ""))
        if re.search(r"mod(?:ulo)?\s*5\b", blob, re.I) and "congruen" in blob.lower():
            hits.append({"title": (y.get("title") or "")[:110], "url": (y.get("url") or "")[:120]})
    out.append({"aid": aid, "query": q, "hits": hits})
    print(f"{aid}: {len(hits)} hits | {nm[:50]}", flush=True)
    for h in hits[:2]:
        print("    ", h["title"][:88])
    time.sleep(0.4)
json.dump(out, open(ROOT / "reports" / "statement_lit_z1.json", "w"), indent=1)
print("saved")
