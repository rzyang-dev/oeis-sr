
import sys
sys.stdout.reconfigure(encoding="utf-8")
def g(W,k): return W.get(abs(k), 1)
def Phi_on(W, hi):
    return {j: (1 if (g(W,j-1)==g(W,j)==g(W,j+1)) else 0) for j in range(0, hi+1)}
def S_on(W, hi):
    return {j: W.get(abs(j)//2,1) for j in range(0, hi+1)}
def I1(W):
    SS=S_on(S_on(W, 60), 100); L=Phi_on(Phi_on(SS, 100), 98)
    R=S_on(Phi_on(S_on(W,60),98), 100)
    return all(L.get(p,1)==R.get(p,1) for p in range(0,40))
def I2(W):
    SFS=Phi_on(S_on(W,60),98); L=Phi_on(Phi_on(SFS,98),96)
    R=S_on(Phi_on(Phi_on(S_on(W,60),98),96),100)
    return all(L.get(p,1)==R.get(p,1) for p in range(0,40))
classO=[]; classE=[]
badI2_O=[]; badI1_O=[]; badI2_E=[]
# class O: W(2n)=W(2n+1) for n>=0 ; enumerate free values on pairs 0..3 (8 cells), tail 1
for free in range(1<<4):
    W={}
    for n in range(0,4):
        v=(free>>n)&1; W[2*n]=v; W[2*n+1]=v
    for j in range(8,12): W[j]=1
    if not I2(W): badI2_O.append(free)
    if not I1(W): badI1_O.append(free)
# class E: W(2n+1)=W(2n+2) for n>=0 ; free bits at even positions 0,2,4,6 and W(1)=W(2) etc.
for free in range(1<<4):
    W={}
    W[0]=(free>>0)&1
    for n in range(1,4):
        v=(free>>n)&1; W[2*n-1]=v; W[2*n]=v
    for j in range(7,12): W[j]=1
    if not I2(W): badI2_E.append(free)
print("I2 on class O failures:", len(badI2_O), "of 16", badI2_O)
print("I1 on class O failures:", len(badI1_O), "of 16", badI1_O)
print("I2 on class E failures:", len(badI2_E), "of 16", badI2_E)
