
import json, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
KEY = open('APIkey', encoding='utf-8').read().strip()
def search(q, count=8, need_content=False):
    body = json.dumps({"query": q, "count": count, "need_content": need_content}).encode('utf-8')
    req = urllib.request.Request("https://api.deepseek.com/v1/tools/search", data=body,
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)
try:
    j = search("Rule 129 elementary cellular automaton closed form", count=6)
    res = j.get("results", [])
    print("OK, results:", len(res))
    for x in res:
        print("-", x.get("title"))
        print("  ", x.get("url"))
        print("  ", (x.get("summary") or "")[:220].replace("\n"," "))
except Exception as e:
    print("ERR:", type(e).__name__, str(e)[:400])
