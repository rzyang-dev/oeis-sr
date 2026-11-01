
import re, zlib, sys, os, glob
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def extract(path):
    data=open(path,'rb').read(); out=[]
    for m in re.finditer(rb'stream\r?\n', data):
        start=m.end(); end=data.find(b'endstream', start)
        if end<0: continue
        raw=data[start:end]; dec=None
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

os.makedirs('nks/txt', exist_ok=True)
tot=0
for p in sorted(glob.glob('nks/*.pdf')):
    name=os.path.basename(p).replace('.pdf','')
    t=extract(p)
    open('nks/txt/'+name+'.txt','w',encoding='utf-8').write(t)
    tot+=len(t)
    print("%-18s %8d chars" % (name, len(t)))
print("total chars:", tot)
