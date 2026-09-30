#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys

BASE={
    'lite':'101c44bbd5ca45ea805bfb344c9aae03adba5401',
    'full':'2c97a97021f266d4f322bb71e1ac5c4ef2b767a6',
}
TARGET={
    'lite':'8388cb9d5578c9f039d2050264ba3e00033c2f35',
    'full':'3037c73761902aad41fde8d9c3555d6ba2b6bd9c',
}
OLD='if(d0>=radius)continue;'
NEW='if(d0+1>=radius)continue;'

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def upgrade(raw,kind):
    got=blob(raw)
    if got!=BASE[kind]:
        raise ValueError(f'Unknown V190 {kind} blob expected {BASE[kind]} got {got}')
    text=raw.decode('utf8')
    if text.count(OLD)!=1:
        raise ValueError(f'Expected exactly one V190 inclusive radius gate, got {text.count(OLD)}')
    text=text.replace(OLD,NEW)
    text=text.replace('Original Restoration V190','Original Restoration V191')
    text=text.replace('ORIGINAL RULE RESTORATION · V190','ORIGINAL RULE RESTORATION · V191')
    text=text.replace('モナークモナーク · v190','モナークモナーク · v191')
    out=text.encode('utf8')
    if blob(out)!=TARGET[kind]:
        raise ValueError(f'generated blob mismatch {blob(out)} != {TARGET[kind]}')
    return out

def main():
    if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
        src,dst=map(Path,sys.argv[2:])
        out=upgrade(src.read_bytes(),'full')
        dst.write_bytes(out)
        print('V191 full Git blob:',blob(out))
        return
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:])
        out=upgrade(src.read_bytes(),'lite')
        dst.write_bytes(out)
        print('V191 lite Git blob:',blob(out))
        return
    if len(sys.argv)==1:
        index=Path('index.html')
        archive=Path('monarch_v191_lite.html')
        raw=index.read_bytes()
        got=blob(raw)
        if got==BASE['lite']:
            out=upgrade(raw,'lite')
            index.write_bytes(out)
            archive.write_bytes(out)
        elif got==TARGET['lite'] and b'Original Restoration V191 LITE' in raw and NEW.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw:
                raise ValueError('Refuse mismatched V191 archive')
            archive.write_bytes(raw)
        else:
            raise ValueError(f'Unknown index version; refusing overwrite: {got}')
        assert index.read_bytes()==archive.read_bytes()
        assert blob(index.read_bytes())==TARGET['lite']
        print('PASS V191 index/archive blob',blob(index.read_bytes()))
        return
    raise SystemExit('Usage: upgrade_v191.py [V190lite V191lite] | [--full V190full V191full]')

if __name__=='__main__':
    main()
