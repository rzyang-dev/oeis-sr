import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\holdout.json", encoding="utf-8"))
print("entries:", len(rows))
for thr in (0, 100, 1000, 5000):
    sub = [r for r in rows if r["defined"] >= thr]
    tot = sum(r["defined"] for r in sub)
    ok = sum(r["correct"] for r in sub)
    perf = sum(1 for r in sub if r["defined"] > 0 and r["correct"] == r["defined"])
    print(f"defined>={thr}: entries={len(sub)} predictions={tot} accuracy={ok/max(tot,1):.2%} perfect={perf}")
big = sorted([r for r in rows if r["defined"] >= 1000], key=lambda x: -(x["defined"]-x["correct"]))
print("\nworst accuracy (defined>=1000):")
for r in big[:8]:
    print(f"  {r['aid']} defined={r['defined']} correct={r['correct']} acc={r['correct']/r['defined']:.3f} states={r['states']}")
