#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys

BASE='c9ac6ee11b641e536b845c6843ab3e3d1faf57c1'
TARGET='227b44d081e59b667e42efc6dfe024e9e6a3b997'
OLD="if(!v.alive||v===u||v.f!==u.f||((v.unitWord||0)&0x800)!==0||((v.unitWord||0)&0xff)===2)continue;"
NEW="if(!(v.alive||v.dying)||v===u||v.f!==u.f||((v.unitWord||0)&0x800)!==0||((v.unitWord||0)&0xff)===2)continue;"

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def upgrade(raw):
    got=blob(raw)
    if got!=BASE:
        raise ValueError(f'Unknown V205 lite blob expected {BASE} got {got}')
    text=raw.decode('utf8')
    if text.count(OLD)!=1:
        raise ValueError(f'Expected exact V205 friendly CPU live-only scan once, got {text.count(OLD)}')
    text=text.replace(OLD,NEW)
    text=text.replace('Original Restoration V205','Original Restoration V206')
    text=text.replace('ORIGINAL RULE RESTORATION · V205','ORIGINAL RULE RESTORATION · V206')
    text=text.replace('モナークモナーク · v205','モナークモナーク · v206')
    out=text.encode('utf8')
    if blob(out)!=TARGET:
        raise ValueError(f'generated blob mismatch {blob(out)} != {TARGET}')
    return out

def main():
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]);out=upgrade(src.read_bytes());dst.write_bytes(out)
        print('V206 lite Git blob:',blob(out));return
    if len(sys.argv)==1:
        index=Path('index.html');archive=Path('monarch_v206_lite.html');raw=index.read_bytes();got=blob(raw)
        if got==BASE:
            out=upgrade(raw);index.write_bytes(out);archive.write_bytes(out)
        elif got==TARGET and b'Original Restoration V206 LITE' in raw and NEW.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw: raise ValueError('Refuse mismatched V206 archive')
            archive.write_bytes(raw)
        else:
            raise ValueError(f'Unknown index version; refusing overwrite: {got}')
        assert index.read_bytes()==archive.read_bytes() and blob(index.read_bytes())==TARGET
        print('PASS V206 index/archive blob',blob(index.read_bytes()));return
    raise SystemExit('Usage: upgrade_v206.py [V205lite V206lite]')

if __name__=='__main__':
    main()
