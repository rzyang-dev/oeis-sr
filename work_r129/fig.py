
import numpy as np, sys, zlib, struct
sys.stdout.reconfigure(encoding="utf-8")
N, T = 700, 340
def simulate(N,T):
    s=np.ones(2*N+1,dtype=np.uint8); s[N-1:N+2]=0
    rows=np.empty((T+1,2*N+1),dtype=np.uint8); rows[1]=s
    r0=np.zeros(2*N+1,dtype=np.uint8); r0[N]=1; rows[0]=r0
    for t in range(1,T):
        a=s[:-2]; b=s[1:-1]; c=s[2:]
        s[1:-1]=((a==b)&(b==c)).astype(np.uint8)
        rows[t+1]=s
    return rows
rows=simulate(N,T)
img=(rows[:T+1, N-310:N+311]*255).astype(np.uint8)   # 0(black)=state 0, 255=state 1
img=np.kron(img, np.ones((2,2),dtype=np.uint8))
h,w=img.shape
raw=b"".join(b"\x00"+img[i].tobytes() for i in range(h))
comp=zlib.compress(raw,9)
def chunk(t,d):
    return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
png=b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,0,0,0,0))+chunk(b"IDAT",comp)+chunk(b"IEND",b"")
open("rule129_zerosef.png","wb").write(png)
print("wrote", w, h)
