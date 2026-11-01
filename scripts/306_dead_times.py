
import math
def r(t):
    return 0 if t == 0 else t - (1 << (t.bit_length() - 1))

KMAX = 18
DMAX = 24
N = 1 << KMAX
cnt = [[0]*(KMAX+1) for _ in range(DMAX+1)]
for t in range(N):
    rt = r(t)
    lim = min(t, DMAX)
    for d in range(lim+1):
        m = (t - d) >> 1
        if rt & m == m:
            cnt[d][t.bit_length()] += 1
# cumulative
for d in range(DMAX+1):
    for k in range(1, KMAX+1):
        cnt[d][k] += cnt[d][k-1]

print("N_d(2^K) for d=0..12")
print("d | " + " | ".join(str(k) for k in range(6, KMAX+1)))
for d in range(13):
    print(f"{d} | " + " | ".join(str(cnt[d][k]) for k in range(6, KMAX+1)))

print()
print("exponent estimate log2(N_d(2^K))/K")
print("d | " + " | ".join(str(k) for k in range(8, KMAX+1)))
for d in range(13):
    print(f"{d} | " + " | ".join(f"{math.log2(max(cnt[d][k],1))/k:.3f}" for k in range(8, KMAX+1)))
