import sys, zlib, struct
sys.stdout.reconfigure(encoding="utf-8")
def simulate(W, T):
    mask = (1 << (2*W+1)) - 1
    a = 1 << W
    out = [a]
    for _ in range(T):
        L = (a << 1) & mask; R = a >> 1
        a = ((L & a & R) | (~(L | a | R) & mask)) & mask
        out.append(a)
    return out
T = 255; W = 2*T + 10           # dependency cone: |j|+t <= 2T < W
st = simulate(W, T)
SC = 2
cols = 2*T+1; rows = T+1
def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag+data) & 0xFFFFFFFF)
raw = bytearray()
for t in range(rows):
    line = bytearray()
    for j in range(-T, T+1):
        bit = (st[t] >> (j+W)) & 1
        line.extend(b"\x00"*SC if bit else b"\xff"*SC)
    raw.extend(b"\x00" + bytes(line))
    raw.extend((b"\x00" + bytes(line))*(SC-1))
ihdr = struct.pack(">IIBBBBB", cols*SC, rows*SC, 8, 0, 0, 0, 0)
png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
open(r"C:\Users\ginger\Documents\oeis\work_r129\rule129.png","wb").write(png)
print("wrote", len(png), "bytes", cols*SC, "x", rows*SC)
# decode check
data = open(r"C:\Users\ginger\Documents\oeis\work_r129\rule129.png","rb").read()
pos=8; idat=b""
while pos < len(data):
    ln = struct.unpack(">I", data[pos:pos+4])[0]; tag = data[pos+4:pos+8]
    if tag == b"IDAT": idat += data[pos+8:pos+8+ln]
    pos += 12+ln
raw2 = zlib.decompress(idat); stride = cols*SC+1
def rowblack(r):
    off=r*stride; return sum(1 for x in raw2[off+1:off+1+cols*SC] if x==0)
print("black px rows 0,2,510,511:", rowblack(0), rowblack(2), rowblack(510), rowblack(511), " (expect 2, 1016, 0, 0)")
