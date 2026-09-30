#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys

BASE={
    'lite':'ec7dc0a2cef14fa575ccfc4207cbd2431c372387',
    'full':'9240650d698c942dee000322f1e468df869159d5',
}
TARGET={
    'lite':'3484b9bc2f562864f4b9efde6f452b5a479d2b0d',
    'full':'5487f119ebefbc918b5151c29aaf046f7b291e1d',
}
OLD1="if(b.strength<=0){beginDeathVisual(b,a.f,b0);b.alive=false;originalSfx(30+Math.max(0,Math.min(4,b.f|0)),.24)}"
NEW1="if(b.strength<=0){beginDeathVisual(b,a.f,b0);b.alive=false;originalSfx(30+Math.max(0,Math.min(4,a.f|0)),.24)}"
OLD2="if(a.strength<=0){beginDeathVisual(a,b.f,a0);a.alive=false;originalSfx(30+Math.max(0,Math.min(4,a.f|0)),.24);return 6}"
NEW2="if(a.strength<=0){beginDeathVisual(a,b.f,a0);a.alive=false;originalSfx(30+Math.max(0,Math.min(4,b.f|0)),.24);return 6}"

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def upgrade(raw,kind):
    got=blob(raw)
    if got!=BASE[kind]:
        raise ValueError(f'Unknown V193 {kind} blob expected {BASE[kind]} got {got}')
    text=raw.decode('utf8')
    if text.count(OLD1)!=1 or text.count(OLD2)!=1:
        raise ValueError(f'Expected exact V193 death SFX blocks once, got defender={text.count(OLD1)} actor={text.count(OLD2)}')
    text=text.replace(OLD1,NEW1).replace(OLD2,NEW2)
    text=text.replace('Original Restoration V193','Original Restoration V194')
    text=text.replace('ORIGINAL RULE RESTORATION · V193','ORIGINAL RULE RESTORATION · V194')
    text=text.replace('モナークモナーク · v193','モナークモナーク · v194')
    out=text.encode('utf8')
    if blob(out)!=TARGET[kind]:
        raise ValueError(f'generated blob mismatch {blob(out)} != {TARGET[kind]}')
    return out

def main():
    if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
        src,dst=map(Path,sys.argv[2:])
        out=upgrade(src.read_bytes(),'full'); dst.write_bytes(out)
        print('V194 full Git blob:',blob(out)); return
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:])
        out=upgrade(src.read_bytes(),'lite'); dst.write_bytes(out)
        print('V194 lite Git blob:',blob(out)); return
    if len(sys.argv)==1:
        index=Path('index.html'); archive=Path('monarch_v194_lite.html')
        raw=index.read_bytes(); got=blob(raw)
        if got==BASE['lite']:
            out=upgrade(raw,'lite'); index.write_bytes(out); archive.write_bytes(out)
        elif got==TARGET['lite'] and b'Original Restoration V194 LITE' in raw and NEW1.encode() in raw and NEW2.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw:
                raise ValueError('Refuse mismatched V194 archive')
            archive.write_bytes(raw)
        else:
            raise ValueError(f'Unknown index version; refusing overwrite: {got}')
        assert index.read_bytes()==archive.read_bytes()
        assert blob(index.read_bytes())==TARGET['lite']
        print('PASS V194 index/archive blob',blob(index.read_bytes())); return
    raise SystemExit('Usage: upgrade_v194.py [V193lite V194lite] | [--full V193full V194full]')

if __name__=='__main__': main()
