#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys

BASE='db3b87755bc7c39faa6a90437d49290bfa79ae62'
TARGET='c9ac6ee11b641e536b845c6843ab3e3d1faf57c1'
OLD="for(const v of ordered){if(!v.alive||v===u||v.f===u.f)continue;"
NEW="for(const v of ordered){if(!(v.alive||v.dying)||v===u||v.f===u.f)continue;"

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def upgrade(raw):
    got=blob(raw)
    if got!=BASE:
        raise ValueError(f'Unknown V204 lite blob expected {BASE} got {got}')
    text=raw.decode('utf8')
    if text.count(OLD)!=1:
        raise ValueError(f'Expected exact V204 enemy CPU live-only scan once, got {text.count(OLD)}')
    text=text.replace(OLD,NEW)
    text=text.replace('Original Restoration V204','Original Restoration V205')
    text=text.replace('ORIGINAL RULE RESTORATION · V204','ORIGINAL RULE RESTORATION · V205')
    text=text.replace('モナークモナーク · v204','モナークモナーク · v205')
    out=text.encode('utf8')
    if blob(out)!=TARGET:
        raise ValueError(f'generated blob mismatch {blob(out)} != {TARGET}')
    return out

def main():
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:])
        out=upgrade(src.read_bytes());dst.write_bytes(out)
        print('V205 lite Git blob:',blob(out));return
    if len(sys.argv)==1:
        index=Path('index.html');archive=Path('monarch_v205_lite.html');raw=index.read_bytes();got=blob(raw)
        if got==BASE:
            out=upgrade(raw);index.write_bytes(out);archive.write_bytes(out)
        elif got==TARGET and b'Original Restoration V205 LITE' in raw and NEW.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw: raise ValueError('Refuse mismatched V205 archive')
            archive.write_bytes(raw)
        else:
            raise ValueError(f'Unknown index version; refusing overwrite: {got}')
        assert index.read_bytes()==archive.read_bytes() and blob(index.read_bytes())==TARGET
        print('PASS V205 index/archive blob',blob(index.read_bytes()));return
    raise SystemExit('Usage: upgrade_v205.py [V204lite V205lite]')

if __name__=='__main__':
    main()
