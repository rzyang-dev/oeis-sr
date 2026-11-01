import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = r"C:\Users\ginger\Documents\oeis"
con = sqlite3.connect("file:" + ROOT.replace("\\","/") + "/oeis.db?mode=ro", uri=True)
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
atlas = {r["aid"] for r in rows if r["val_ok"] == r["val_total"] and r["val_total"] >= 1000}
print("atlas:", len(atlas))
pat = re.compile(r"a\(n\)\s*=\s*A(\d{6})\(n\s*([+-]\s*\d+)?\)")
cands = []
for aid, t in con.execute("select aid, text from stmt where lower(text) like '%conjecture%'"):
    if aid not in atlas:
        continue
    for m in pat.finditer(t):
        other = "A" + m.group(1)
        if other in atlas:
            off = (m.group(2) or "0").replace(" ", "")
            cands.append((aid, other, off, t[:150]))
print("candidates (simple equality, both automatic):", len(cands))
seen = set()
for aid, other, off, t in cands:
    key = (aid, other, off)
    if key in seen: continue
    seen.add(key)
    print(f"  {aid} = {other}(n{off})  | {t[:110]}")
