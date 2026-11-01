import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
f = Path(r"C:\Users\ginger\oeisdata\files\A338\b338464.txt")
v = {}
for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
    line=line.strip()
    if not line or line.startswith("#"): continue
    q=line.split()
    if len(q)>=2:
        try: v[int(q[0])]=int(q[1])
        except ValueError: pass

def is_qr(a, p):
    return any((x*x) % p == a % p for x in range(p))

print("prediction: a(n)=0 mod p for all n=1 mod p  <=>  2 is a NON-residue mod p")
print(f"{'p':>4} {'2 QR?':>6} {'n=1 mod p zeros':>16} {'all zero?':>10}")
for p in (3, 5, 7, 11, 13, 17, 19, 23, 29, 31):
    ns = [n for n in v if n % p == 1]
    z = sum(1 for n in ns if v[n] % p == 0)
    print(f"{p:>4} {str(is_qr(2,p)):>6} {z:>7}/{len(ns):<8} {str(z==len(ns)):>10}")
