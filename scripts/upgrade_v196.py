#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys

BASE={'lite':'6877f4648bb1958309f808ed9de3dc48d1c8b969','full':'aa6519e0dc8157b75f62496e4bd7a76f73522358'}
TARGET={'lite':'df4f5dad7a261959b6b5902dc8ffafa5f6aa53ae','full':'81bf9090ce6516ae56b9f7ae5068ac513259a3d3'}
OLD="if(!a?.alive||!b?.alive||a===b)return 0;"
NEW="if(!a?.alive||a===b)return 0;"

def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def upgrade(raw,kind):
    got=blob(raw)
    if got!=BASE[kind]: raise ValueError(f'Unknown V195 {kind} blob expected {BASE[kind]} got {got}')
    text=raw.decode('utf8')
    if text.count(OLD)!=1: raise ValueError(f'Expected exact V195 exchange alive gate once, got {text.count(OLD)}')
    text=text.replace(OLD,NEW)
    text=text.replace('Original Restoration V195','Original Restoration V196')
    text=text.replace('ORIGINAL RULE RESTORATION · V195','ORIGINAL RULE RESTORATION · V196')
    text=text.replace('モナークモナーク · v195','モナークモナーク · v196')
    out=text.encode('utf8')
    if blob(out)!=TARGET[kind]: raise ValueError(f'generated blob mismatch {blob(out)} != {TARGET[kind]}')
    return out
def main():
    if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
        src,dst=map(Path,sys.argv[2:]);out=upgrade(src.read_bytes(),'full');dst.write_bytes(out);print('V196 full Git blob:',blob(out));return
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]);out=upgrade(src.read_bytes(),'lite');dst.write_bytes(out);print('V196 lite Git blob:',blob(out));return
    if len(sys.argv)==1:
        index=Path('index.html');archive=Path('monarch_v196_lite.html');raw=index.read_bytes();got=blob(raw)
        if got==BASE['lite']:
            out=upgrade(raw,'lite');index.write_bytes(out);archive.write_bytes(out)
        elif got==TARGET['lite'] and b'Original Restoration V196 LITE' in raw and NEW.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw: raise ValueError('Refuse mismatched V196 archive')
            archive.write_bytes(raw)
        else: raise ValueError(f'Unknown index version; refusing overwrite: {got}')
        assert index.read_bytes()==archive.read_bytes() and blob(index.read_bytes())==TARGET['lite']
        print('PASS V196 index/archive blob',blob(index.read_bytes()));return
    raise SystemExit('Usage: upgrade_v196.py [V195lite V196lite] | [--full V195full V196full]')
if __name__=='__main__': main()
