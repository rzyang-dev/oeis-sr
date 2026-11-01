import zlib, struct, sys
sys.stdout.reconfigure(encoding="utf-8")
data = open(r"C:\Users\ginger\Documents\oeis\work_r129\rule129.png","rb").read()
assert data[:8] == b"\x89PNG\r\n\x1a\n"
pos = 8; idat = b""; w=h=0
while pos < len(data):
    ln = struct.unpack(">I", data[pos:pos+4])[0]; tag = data[pos+4:pos+8]
    payload = data[pos+8:pos+8+ln]
    if tag == b"IHDR":
        w,h,bd,ct,cm,fm,im = struct.unpack(">IIBBBBB", payload)
        print("IHDR", w, h, "bitdepth", bd, "colortype", ct)
    elif tag == b"IDAT":
        idat += payload
    pos += 12 + ln
raw = zlib.decompress(idat)
stride = w + 1
def rowvals(r):
    off = r*stride
    assert raw[off] == 0, ("filter", raw[off])
    return raw[off+1:off+1+w]
for r in [0, 1, 2, 3, h-3, h-2, h-1]:
    v = rowvals(r)
    print("row", r, "black px:", sum(1 for x in v if x == 0), "white px:", sum(1 for x in v if x == 255),
          "center vals:", [v[w//2-2+k] for k in range(5)])
