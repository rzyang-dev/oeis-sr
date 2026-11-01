import re, sys, zlib
sys.stdout.reconfigure(encoding="utf-8")
PDF = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\ginger\Documents\oeis\2603.21852v2.pdf"
OUT = sys.argv[2] if len(sys.argv) > 2 else "reports/paper.txt"
data = open(PDF, "rb").read()

objs = {}
for m in re.finditer(rb"(\d+)\s+0\s+obj(.*?)endobj", data, re.S):
    objs[int(m.group(1))] = m.group(2)

def raw_stream(body):
    i = body.find(b"stream")
    if i < 0: return None
    j = body.find(b"endstream", i)
    raw = body[i+6:j].lstrip(b"\r\n").rstrip(b"\r\n")
    if b"/FlateDecode" in body[:i]:
        try: return zlib.decompress(raw)
        except Exception: return None
    return raw

# ---- font name -> object number (resource dicts) ----
fontmap = {}
for num, body in objs.items():
    for fm in re.finditer(rb"/Font\s*<<(.*?)>>", body, re.S):
        for mm in re.finditer(rb"/([A-Za-z0-9]+)\s+(\d+)\s+0\s+R", fm.group(1)):
            fontmap[mm.group(1).decode()] = int(mm.group(2))
print("fonts:", len(fontmap))

# ---- ToUnicode CMaps ----
def _dst(b):
    if len(b) == 1:
        return b.decode("latin-1")
    return b.decode("utf-16-be", "replace")

def parse_cmap(s):
    cmap = {}
    for m in re.finditer(rb"beginbfchar(.*?)endbfchar", s, re.S):
        for a, b in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", m.group(1)):
            cmap[int(a, 16)] = _dst(bytes.fromhex(b.decode()))
    for m in re.finditer(rb"beginbfrange(.*?)endbfrange", s, re.S):
        for lo, hi, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", m.group(1)):
            lo, hi = int(lo, 16), int(hi, 16)
            db = bytes.fromhex(dst.decode())
            base = int.from_bytes(db, "big")
            for k in range(lo, hi + 1):
                v = base + (k - lo)
                try:
                    cmap[k] = v.to_bytes(len(db), "big").decode("utf-16-be", "replace")
                except (OverflowError, UnicodeDecodeError):
                    pass
    return cmap

font_cmap = {}
for name, num in fontmap.items():
    body = objs.get(num, b"")
    m = re.search(rb"/ToUnicode\s+(\d+)\s+0\s+R", body)
    if m:
        s = raw_stream(objs.get(int(m.group(1)), b""))
        if s:
            font_cmap[name] = parse_cmap(s)
print("fonts with ToUnicode:", len(font_cmap))

TOKEN = re.compile(rb"\((?:[^()\\]|\\.)*\)|<[0-9A-Fa-f\s]+>|\[|\]|/[A-Za-z0-9]+|-?\d*\.?\d+|[A-Za-z*'\"]{1,3}")

def unescape(b):
    out = bytearray(); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5c and i + 1 < len(b):
            n = b[i+1]
            if n in b"nrtbf":
                out.append({110:10,114:13,116:9,98:8,102:12}[n]); i += 2; continue
            if 48 <= n <= 55:
                j = i+1; v = 0; k = 0
                while j < len(b) and 48 <= b[j] <= 55 and k < 3:
                    v = v*8 + (b[j]-48); j += 1; k += 1
                out.append(v & 0xFF); i = j; continue
            if n in b"\r\n":
                i += 2
                if n == 13 and i < len(b) and b[i] == 10: i += 1
                continue
            out.append(n); i += 2; continue
        out.append(c); i += 1
    return bytes(out)

def decode(b, font):
    cm = font_cmap.get(font)
    if not cm:
        return b.decode("latin-1")
    return "".join(cm.get(c, "") for c in b)

def is_content(s):
    return s is not None and b"BT" in s and (b"Tj" in s or b"TJ" in s)

pages = [(n, raw_stream(b)) for n, b in objs.items()]
pages = [(n, s) for n, s in pages if is_content(s)]
pages.sort()

lines_out = []
for num, s in pages:
    font = ""
    y_last = None
    line = []
    def flush():
        global line
        if line:
            t = "".join(line).strip()
            if t: lines_out.append(t)
            line = []
    stack = []
    toks = TOKEN.findall(s)
    i = 0
    pending_name = None
    while i < len(toks):
        t = toks[i]
        if t.startswith(b"/"):
            pending_name = t[1:].decode()
        elif t == b"Tf" and pending_name in fontmap:
            font = pending_name
        elif t == b"[":
            j = i + 1; nums = []; strs = []
            while j < len(toks) and toks[j] != b"]":
                if toks[j].startswith(b"(") or toks[j].startswith(b"<"):
                    strs.append(toks[j])
                else:
                    try: nums.append(float(toks[j]))
                    except ValueError: pass
                j += 1
            # interleave: rebuild with gaps
            k = i + 1; txt = []
            for tok in toks[i+1:j]:
                if tok.startswith(b"("):
                    txt.append(decode(unescape(tok[1:-1]), font))
                elif tok.startswith(b"<"):
                    h = re.sub(rb"\s+", b"", tok[1:-1])
                    if len(h) % 2: h += b"0"
                    txt.append(decode(bytes.fromhex(h.decode()), font))
                else:
                    try:
                        v = float(tok)
                        if v <= -120: txt.append(" ")
                    except ValueError:
                        pass
            line.append("".join(txt))
            i = j
        elif t.startswith(b"(") or t.startswith(b"<"):
            if t.startswith(b"("):
                line.append(decode(unescape(t[1:-1]), font))
            else:
                h = re.sub(rb"\s+", b"", t[1:-1])
                if len(h) % 2: h += b"0"
                line.append(decode(bytes.fromhex(h.decode()), font))
        elif t in (b"Td", b"TD"):
            dx, dy = (float(toks[i-2]), float(toks[i-1]))
            if abs(dy) > 0.5:
                flush()
            elif dx > 1.5:
                line.append(" ")
        elif t == b"Tm":
            flush()
        elif t == b"T*":
            flush()
        elif t == b"ET":
            flush()
        i += 1
    flush()

text = "\n".join(lines_out)
open(OUT, "w", encoding="utf-8").write(text)
print("lines:", len(lines_out), "chars:", len(text))
print(text[:3000])