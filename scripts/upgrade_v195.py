#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys

BASE={'lite':'3484b9bc2f562864f4b9efde6f452b5a479d2b0d','full':'5487f119ebefbc918b5151c29aaf046f7b291e1d'}
TARGET={'lite':'6877f4648bb1958309f808ed9de3dc48d1c8b969','full':'aa6519e0dc8157b75f62496e4bd7a76f73522358'}
OLD="if(firstStrike&&attacker.f!==4&&((target.unitWord&0x0800)!==0||target.type==='king'))return 100;"
NEW="if(firstStrike&&attacker.f!==4&&((target.unitWord&0x0800)!==0))return 100;"

def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def upgrade(raw,kind):
    got=blob(raw)
    if got!=BASE[kind]: raise ValueError(f'Unknown V194 {kind} blob expected {BASE[kind]} got {got}')
    text=raw.decode('utf8')
    if text.count(OLD)!=1: raise ValueError(f'Expected exact V194 commander override once, got {text.count(OLD)}')
    text=text.replace(OLD,NEW)
    text=text.replace('Original Restoration V194','Original Restoration V195')
    text=text.replace('ORIGINAL RULE RESTORATION · V194','ORIGINAL RULE RESTORATION · V195')
    text=text.replace('モナークモナーク · v194','モナークモナーク · v195')
    out=text.encode('utf8')
    if blob(out)!=TARGET[kind]: raise ValueError(f'generated blob mismatch {blob(out)} != {TARGET[kind]}')
    return out
def main():
    if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
        src,dst=map(Path,sys.argv[2:]); out=upgrade(src.read_bytes(),'full'); dst.write_bytes(out); print('V195 full Git blob:',blob(out)); return
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]); out=upgrade(src.read_bytes(),'lite'); dst.write_bytes(out); print('V195 lite Git blob:',blob(out)); return
    if len(sys.argv)==1:
        index=Path('index.html'); archive=Path('monarch_v195_lite.html'); raw=index.read_bytes(); got=blob(raw)
        if got==BASE['lite']:
            out=upgrade(raw,'lite'); index.write_bytes(out); archive.write_bytes(out)
        elif got==TARGET['lite'] and b'Original Restoration V195 LITE' in raw and NEW.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw: raise ValueError('Refuse mismatched V195 archive')
            archive.write_bytes(raw)
        else: raise ValueError(f'Unknown index version; refusing overwrite: {got}')
        assert index.read_bytes()==archive.read_bytes() and blob(index.read_bytes())==TARGET['lite']
        print('PASS V195 index/archive blob',blob(index.read_bytes())); return
    raise SystemExit('Usage: upgrade_v195.py [V194lite V195lite] | [--full V194full V195full]')
if __name__=='__main__': main()
