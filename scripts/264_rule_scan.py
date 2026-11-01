import sys
sys.stdout.reconfigure(encoding="utf-8")
N = 200
T = 70
def middle(rule, T=T):
    s = [0]*(2*N+1); s[N] = 1
    out = []
    for t in range(T):
        out.append(s[N])
        ns = [0]*(2*N+1)
        for i in range(2*N+1):
            l = s[i-1] if i-1 >= 0 else 0
            c = s[i]
            r = s[i+1] if i+1 < 2*N+1 else 0
            ns[i] = (rule >> (4*l+2*c+r)) & 1
        s = ns
    return out
mersenne = [2**k-1 for k in range(1, 7)]
pow3 = [3**k-1 for k in range(1, 5)]
from collections import Counter
classes = Counter()
examples = {}
for rule in range(256):
    m = middle(rule)
    zeros = [t for t in range(1, T) if m[t] == 0]
    ones = sum(m[1:])
    if not zeros:
        cls = "no zeros"
    elif len(zeros) == T-1:
        cls = "all zeros"
    elif zeros == [t for t in mersenne if t < T]:
        cls = "2^k-1"
    elif zeros == [t for t in pow3 if t < T]:
        cls = "3^k-1"
    else:
        cls = "other"
    classes[cls] += 1
    examples.setdefault(cls, []).append((rule, zeros[:8]))
for cls, cnt in classes.most_common():
    print(f"{cls}: {cnt}  e.g. {examples[cls][:3]}")
