#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys

BASE={'lite':'cec337794d03e50508a08cadb1938a646ac0c1ff','full':'a1d50d08ccefa18f3a547aef14fc5493d001d76d'}
TARGET={'lite':'fbd7d8b810184d15a067c9538293b168edc84a3e','full':'3893b00408ff582d94b043784e376c40547fac04'}
OLD="return Math.max(1,Math.trunc((attackerStrength+(attacker.z-target.z)*100)/80));"
NEW="const raw=Math.trunc((attackerStrength+(attacker.z-target.z)*100)/80);return firstStrike?Math.max(1,raw):(raw<0?1:raw);"

def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def upgrade(raw,kind):
    got=blob(raw)
    if got!=BASE[kind]: raise ValueError(f'Unknown V197 {kind} blob expected {BASE[kind]} got {got}')
    text=raw.decode('utf8')
    if text.count(OLD)!=1: raise ValueError(f'Expected exact V197 combat damage formula once, got {text.count(OLD)}')
    text=text.replace(OLD,NEW)
    text=text.replace('Original Restoration V197','Original Restoration V198')
    text=text.replace('ORIGINAL RULE RESTORATION · V197','ORIGINAL RULE RESTORATION · V198')
    text=text.replace('モナークモナーク · v197','モナークモナーク · v198')
    out=text.encode('utf8')
    if blob(out)!=TARGET[kind]: raise ValueError(f'generated blob mismatch {blob(out)} != {TARGET[kind]}')
    return out

def main():
    if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
        src,dst=map(Path,sys.argv[2:]);out=upgrade(src.read_bytes(),'full');dst.write_bytes(out);print('V198 full Git blob:',blob(out));return
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]);out=upgrade(src.read_bytes(),'lite');dst.write_bytes(out);print('V198 lite Git blob:',blob(out));return
    if len(sys.argv)==1:
        index=Path('index.html');archive=Path('monarch_v198_lite.html');raw=index.read_bytes();got=blob(raw)
        if got==BASE['lite']:
            out=upgrade(raw,'lite');index.write_bytes(out);archive.write_bytes(out)
        elif got==TARGET['lite'] and b'Original Restoration V198 LITE' in raw and NEW.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw: raise ValueError('Refuse mismatched V198 archive')
            archive.write_bytes(raw)
        else: raise ValueError(f'Unknown index version; refusing overwrite: {got}')
        assert index.read_bytes()==archive.read_bytes() and blob(index.read_bytes())==TARGET['lite']
        print('PASS V198 index/archive blob',blob(index.read_bytes()));return
    raise SystemExit('Usage: upgrade_v198.py [V197lite V198lite] | [--full V197full V198full]')
if __name__=='__main__': main()
