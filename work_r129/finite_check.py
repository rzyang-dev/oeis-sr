
import numpy as np, sys, zlib, struct
sys.stdout.reconfigure(encoding="utf-8")

# ---------- universal finite check of block substitution ----------
# rows as dicts over range; 1 outside
R = 26
def F(v):
    # v: dict j->0/1 with 1 outside range; returns dict over same range shifted
    lo = min(v); hi = max(v)
    return {j: (1 if (v.get(j-1,1)==v.get(j,1)==v.get(j+1,1)) else 0) for j in range(lo+1, hi)}

def sigma0(A, B, p, lo, hi):
    # A = row t-1, B = row t, phase p = t mod 2 ; returns dict over [lo,hi]
    out = {}
    for j in range(lo, hi+1):
        if j % 2 == 0:
            i = j//2
            out[j] = 0 if (B.get(i,1)==0 and (i - p) % 2 == 0) else 1
        else:
            i = (j-1)//2
            out[j] = 0 if (A.get(i,1) != A.get(i+1,1)) else 1
    return out

bad2 = 0; bad1 = 0; ex2 = None; ex1 = None
count = 0
A0 = {}
for bits in range(1<<17):
    A = {i: (bits>>(i+8))&1 for i in range(-8,9)}
    B = F(A)
    C = F(B)
    for p in (0,1):
        s0 = sigma0(A,B,p,-13,13)
        s1 = F(s0)
        lhs = F(s1)
        rhs = sigma0(B,C,1-p,-11,11)
        for j in range(-9,10):
            if lhs[j] != rhs[j]:
                bad2 += 1
                if ex2 is None: ex2 = (A,B,p,j,lhs[j],rhs[j])
                break
        for j in range(-7,8):
            i = 2*j
            if s1[i] != B.get(j,1):
                bad1 += 1
                if ex1 is None: ex1 = (A,B,p,j,s1[i],B.get(j,1))
                break
    count += 1
print("patterns:", count, "Check2(F^2 sigma0 = sigma0(B,F B)) failures:", bad2, "Check1(sigma1 even = B) failures:", bad1)
if ex2: print("ex2:", ex2[2:])
if ex1: print("ex1:", ex1[2:])
