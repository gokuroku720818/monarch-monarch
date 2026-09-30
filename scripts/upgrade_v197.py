#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys
BASE={'lite':'df4f5dad7a261959b6b5902dc8ffafa5f6aa53ae','full':'81bf9090ce6516ae56b9f7ae5068ac513259a3d3'}
TARGET={'lite':'cec337794d03e50508a08cadb1938a646ac0c1ff','full':'a1d50d08ccefa18f3a547aef14fc5493d001d76d'}
OLD="if(!a?.alive||!b?.alive||a===b||a.type==='king'||b.type==='king'||((a.unitWord||0)&0x0800)!==0||((b.unitWord||0)&0x0800)!==0||a.f!==b.f||(factionFreezeTimer[a.f]||0)>0)return false;"
NEW="if(!a?.alive||!b?.alive||a===b||((a.unitWord||0)&0x0800)!==0||((b.unitWord||0)&0x0800)!==0||a.f!==b.f||(factionFreezeTimer[a.f]||0)>0)return false;"
def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def upgrade(raw,kind):
    got=blob(raw)
    if got!=BASE[kind]: raise ValueError(f'Unknown V196 {kind} blob expected {BASE[kind]} got {got}')
    text=raw.decode('utf8')
    if text.count(OLD)!=1: raise ValueError(f'Expected exact V196 merge commander gate once, got {text.count(OLD)}')
    text=text.replace(OLD,NEW)
    text=text.replace('Original Restoration V196','Original Restoration V197')
    text=text.replace('ORIGINAL RULE RESTORATION · V196','ORIGINAL RULE RESTORATION · V197')
    text=text.replace('モナークモナーク · v196','モナークモナーク · v197')
    out=text.encode('utf8')
    if blob(out)!=TARGET[kind]: raise ValueError(f'generated blob mismatch {blob(out)} != {TARGET[kind]}')
    return out
def main():
    if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
        src,dst=map(Path,sys.argv[2:]);out=upgrade(src.read_bytes(),'full');dst.write_bytes(out);print('V197 full Git blob:',blob(out));return
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]);out=upgrade(src.read_bytes(),'lite');dst.write_bytes(out);print('V197 lite Git blob:',blob(out));return
    if len(sys.argv)==1:
        index=Path('index.html');archive=Path('monarch_v197_lite.html');raw=index.read_bytes();got=blob(raw)
        if got==BASE['lite']:
            out=upgrade(raw,'lite');index.write_bytes(out);archive.write_bytes(out)
        elif got==TARGET['lite'] and b'Original Restoration V197 LITE' in raw and NEW.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw: raise ValueError('Refuse mismatched V197 archive')
            archive.write_bytes(raw)
        else: raise ValueError(f'Unknown index version; refusing overwrite: {got}')
        assert index.read_bytes()==archive.read_bytes() and blob(index.read_bytes())==TARGET['lite']
        print('PASS V197 index/archive blob',blob(index.read_bytes()));return
    raise SystemExit('Usage: upgrade_v197.py [V196lite V197lite] | [--full V196full V197full]')
if __name__=='__main__': main()
