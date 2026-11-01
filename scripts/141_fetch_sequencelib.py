import urllib.request, sys
sys.stdout.reconfigure(encoding="utf-8")
urls = [
 "https://raw.githubusercontent.com/provables/sequencelib/main/Sequencelib/Synthetic/A267/A267442.lean",
 "https://raw.githubusercontent.com/provables/sequencelib/main/Sequencelib/Synthetic/A043/A043545.lean",
 "https://raw.githubusercontent.com/provables/sequencelib/main/Sequencelib/Synthetic/A285/A285383.lean",
]
for u in urls:
    print("="*70); print(u)
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            t = r.read().decode("utf-8", errors="replace")
        print(t[:2500])
    except Exception as e:
        print("ERR", type(e).__name__, e)
