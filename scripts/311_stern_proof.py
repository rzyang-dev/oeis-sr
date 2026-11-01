
def fusc(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        if bit=='0': b=a+b
        else: a=a+b
    return a
def insig(u,d):
    return (u & ((u+d)//2)) == u
def sig(d):
    return [u for u in range(d+1) if insig(u,d)]

N=400
# KEY LEMMA:  v in Sigma_e  <=>  2v subset v+e
bad=0
for e in range(N+1):
    for v in range(e+1):
        if insig(v,e) != ((2*v & (v+e)) == 2*v): bad+=1
print("KEY LEMMA  v in Sigma_e  <=>  2v subseteq v+e :  violations =",bad)

# (S1)/(S3)  even part
b1=b3=0
for e in range(N+1):
    S2=set(sig(2*e)); S3=set(sig(2*e+1))
    doubles=set(2*v for v in sig(e))
    if doubles != {u for u in S2 if u%2==0}: b1+=1
    if doubles != {u for u in S3 if u%2==0}: b3+=1
print("(S1) Sigma_2e  even part = 2*Sigma_e :  violations =",b1)
print("(S3) Sigma_2e+1 even part = 2*Sigma_e :  violations =",b3)

# (S2)/(S4)  odd part
b2=b4=0
for e in range(N+1):
    S2=set(sig(2*e)); S4=set(sig(2*e+1)); Se=sig(e)
    odd_from_P=set(2*v+1 for v in Se if (v+e)%2==1)
    odd_from_Q=set(2*v+1 for v in Se if (v+e)%2==0)
    if odd_from_P != {u for u in S2 if u%2==1}: b2+=1
    if odd_from_Q != {u for u in S4 if u%2==1}: b4+=1
print("(S2) Sigma_2e   odd part = {2v+1 : v in Sigma_e, v+e odd}  : violations =",b2)
print("(S4) Sigma_2e+1 odd part = {2v+1 : v in Sigma_e, v+e even} : violations =",b4)

# the Stern induction: p(e)=f(e), q(e)=f(e+1), A(e)=p+q
bp=bq=bA=0
for e in range(N+1):
    Se=sig(e); p=sum(1 for v in Se if (v+e)%2==1); q=len(Se)-p
    if p!=fusc(e): bp+=1
    if q!=fusc(e+1): bq+=1
    if len(Se)!=fusc(e)+fusc(e+1): bA+=1
print("p(e)=fusc(e):",bp," q(e)=fusc(e+1):",bq," A(e)=fusc(e)+fusc(e+1):",bA,"  (all counted as violations over e<=%d)"%N)
