#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys

BASE='8d678a731679a8be1043ee1aabf6a889cf0b0974'
TARGET='99bf93612175400b45feaf73d2a7b52292d7b381'
OLD1="if(!u||!v||!u.alive||!v.alive)return null;"
NEW1="if(!u||!v||!u.alive||(!v.alive&&!(u.f===4&&v.dying)))return null;"
OLD2="if((u.neutralCounter&1)===0){for(const v of units){if(!v||!v.alive||v===u||v.f===u.f)continue;const p=trackedUnitRoute(u,v,3);"
NEW2="if((u.neutralCounter&1)===0){for(const v of units){if(!v||!(v.alive||v.dying)||v===u||v.f===u.f)continue;const p=trackedUnitRoute(u,v,3);"

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def upgrade(raw):
    got=blob(raw)
    if got!=BASE:
        raise ValueError(f'Unknown V202 lite blob expected {BASE} got {got}')
    text=raw.decode('utf8')
    if text.count(OLD1)<1:
        raise ValueError('V202 tracked-unit alive gate missing')
    first=text.index(OLD1)
    text=text[:first]+NEW1+text[first+len(OLD1):]
    if text.count(OLD2)!=1:
        raise ValueError(f'Expected V202 neutral alive scan once, got {text.count(OLD2)}')
    text=text.replace(OLD2,NEW2)
    text=text.replace('Original Restoration V202','Original Restoration V203')
    text=text.replace('ORIGINAL RULE RESTORATION · V202','ORIGINAL RULE RESTORATION · V203')
    text=text.replace('モナークモナーク · v202','モナークモナーク · v203')
    out=text.encode('utf8')
    if blob(out)!=TARGET:
        raise ValueError(f'generated blob mismatch {blob(out)} != {TARGET}')
    return out

def main():
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]);out=upgrade(src.read_bytes());dst.write_bytes(out);print('V203 lite Git blob:',blob(out));return
    if len(sys.argv)==1:
        index=Path('index.html');archive=Path('monarch_v203_lite.html');raw=index.read_bytes();got=blob(raw)
        if got==BASE:
            out=upgrade(raw);index.write_bytes(out);archive.write_bytes(out)
        elif got==TARGET and b'Original Restoration V203 LITE' in raw and NEW1.encode() in raw and NEW2.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw: raise ValueError('Refuse mismatched V203 archive')
            archive.write_bytes(raw)
        else:
            raise ValueError(f'Unknown index version; refusing overwrite: {got}')
        assert index.read_bytes()==archive.read_bytes() and blob(index.read_bytes())==TARGET
        print('PASS V203 index/archive blob',blob(index.read_bytes()));return
    raise SystemExit('Usage: upgrade_v203.py [V202lite V203lite]')

if __name__=='__main__':
    main()
