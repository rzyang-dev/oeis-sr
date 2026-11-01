
import re, zlib, sys, os
def extract(path):
    data = open(path,'rb').read()
    out=[]
    for m in re.finditer(rb'stream\r?\n', data):
        start=m.end(); end=data.find(b'endstream', start)
        if end<0: continue
        raw=data[start:end]
        dec=None
        try: dec=zlib.decompress(raw)
        except Exception:
            try: dec=zlib.decompressobj().decompress(raw)
            except Exception: dec=None
        if dec is None: continue
        if b'Tj' not in dec and b'TJ' not in dec: continue
        for s in re.finditer(rb'\((?:\\.|[^\\()])*\)', dec):
            t=s.group()[1:-1]
            t=re.sub(rb'\\([nrtbf()\\])', lambda m: {b'n':b'\n',b'r':b'\r',b't':b'\t',b'b':b'',b'f':b'',b'(':b'(',b')':b')',b'\\':b'\\'}[m.group(1)], t)
            t=re.sub(rb'\\[0-7]{1,3}', lambda m: bytes([int(m.group()[1:],8)&0xFF]), t)
            out.append(t)
        out.append(b' ')
    return b''.join(out).decode('latin-1')

p=sys.argv[1]
t=extract(p)
print("chars:", len(t))
sample=t[:1200].replace("\n"," ")
print("sample:", sample[:900])
for kw in ["129","neighbour","neighbor","unanim","submask","closed form","zero"]:
    print(kw, t.count(kw))
