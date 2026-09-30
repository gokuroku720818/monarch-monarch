#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys

BASE={
    'lite':'8388cb9d5578c9f039d2050264ba3e00033c2f35',
    'full':'3037c73761902aad41fde8d9c3555d6ba2b6bd9c',
}
TARGET={
    'lite':'55bba7d749d0d88fa29e6cfb091dc3357393e8e7',
    'full':'59050bc2031a212293489523f8cf3c7d8e82580d',
}
OLD1="if(b.strength<=0){beginDeathVisual(b,a.f,b0);b.alive=false;originalSfx(30+Math.max(0,Math.min(4,b.f|0)),.24);return 6}"
NEW1="if(b.strength<=0){beginDeathVisual(b,a.f,b0);b.alive=false;originalSfx(30+Math.max(0,Math.min(4,b.f|0)),.24)}"
OLD2="if(a.strength<=0){beginDeathVisual(a,b.f,a0);a.alive=false;originalSfx(30+Math.max(0,Math.min(4,a.f|0)),.24)}\n   return 4;"
NEW2="if(a.strength<=0){beginDeathVisual(a,b.f,a0);a.alive=false;originalSfx(30+Math.max(0,Math.min(4,a.f|0)),.24);return 6}\n   return 4;"

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def upgrade(raw,kind):
    got=blob(raw)
    if got!=BASE[kind]:
        raise ValueError(f'Unknown V191 {kind} blob expected {BASE[kind]} got {got}')
    text=raw.decode('utf8')
    if text.count(OLD1)!=1 or text.count(OLD2)!=1:
        raise ValueError(f'Expected exact V191 combat blocks once, got defender={text.count(OLD1)} actor={text.count(OLD2)}')
    text=text.replace(OLD1,NEW1).replace(OLD2,NEW2)
    text=text.replace('Original Restoration V191','Original Restoration V192')
    text=text.replace('ORIGINAL RULE RESTORATION · V191','ORIGINAL RULE RESTORATION · V192')
    text=text.replace('モナークモナーク · v191','モナークモナーク · v192')
    out=text.encode('utf8')
    if blob(out)!=TARGET[kind]:
        raise ValueError(f'generated blob mismatch {blob(out)} != {TARGET[kind]}')
    return out

def main():
    if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
        src,dst=map(Path,sys.argv[2:])
        out=upgrade(src.read_bytes(),'full'); dst.write_bytes(out)
        print('V192 full Git blob:',blob(out)); return
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:])
        out=upgrade(src.read_bytes(),'lite'); dst.write_bytes(out)
        print('V192 lite Git blob:',blob(out)); return
    if len(sys.argv)==1:
        index=Path('index.html'); archive=Path('monarch_v192_lite.html')
        raw=index.read_bytes(); got=blob(raw)
        if got==BASE['lite']:
            out=upgrade(raw,'lite'); index.write_bytes(out); archive.write_bytes(out)
        elif got==TARGET['lite'] and b'Original Restoration V192 LITE' in raw and NEW1.encode() in raw and NEW2.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw:
                raise ValueError('Refuse mismatched V192 archive')
            archive.write_bytes(raw)
        else:
            raise ValueError(f'Unknown index version; refusing overwrite: {got}')
        assert index.read_bytes()==archive.read_bytes()
        assert blob(index.read_bytes())==TARGET['lite']
        print('PASS V192 index/archive blob',blob(index.read_bytes())); return
    raise SystemExit('Usage: upgrade_v192.py [V191lite V192lite] | [--full V191full V192full]')

if __name__=='__main__': main()
