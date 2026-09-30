#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys

BASE='4444c1f2791070a791e4255677794caaac858f17'
TARGET='8d678a731679a8be1043ee1aabf6a889cf0b0974'
OLD1="if(v.type==='king'&&actionCode===3&&(factionCastleHP[v.f]||0)>0)return null;"
NEW1="if(u.f!==4&&v.type==='king'&&actionCode===3&&(factionCastleHP[v.f]||0)>0)return null;"
OLD2="if((u.neutralCounter&1)===0){for(const v of units){if(!v||!v.alive||v===u||v.f===u.f||(v.type==='king'&&(factionCastleHP[v.f]||0)>0))continue;const p=trackedUnitRoute(u,v,3);"
NEW2="if((u.neutralCounter&1)===0){for(const v of units){if(!v||!v.alive||v===u||v.f===u.f)continue;const p=trackedUnitRoute(u,v,3);"

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def upgrade(raw):
    got=blob(raw)
    if got!=BASE:
        raise ValueError(f'Unknown V201 lite blob expected {BASE} got {got}')
    text=raw.decode('utf8')
    if text.count(OLD1)!=2:
        raise ValueError(f'Expected two V201 chase castle gates, got {text.count(OLD1)}')
    first=text.index(OLD1)
    text=text[:first]+NEW1+text[first+len(OLD1):]
    if text.count(OLD2)!=1:
        raise ValueError(f'Expected exact V201 neutral hunt scan once, got {text.count(OLD2)}')
    text=text.replace(OLD2,NEW2)
    text=text.replace('Original Restoration V201','Original Restoration V202')
    text=text.replace('ORIGINAL RULE RESTORATION · V201','ORIGINAL RULE RESTORATION · V202')
    text=text.replace('モナークモナーク · v201','モナークモナーク · v202')
    out=text.encode('utf8')
    if blob(out)!=TARGET:
        raise ValueError(f'generated blob mismatch {blob(out)} != {TARGET}')
    return out

def main():
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]);out=upgrade(src.read_bytes());dst.write_bytes(out);print('V202 lite Git blob:',blob(out));return
    if len(sys.argv)==1:
        index=Path('index.html');archive=Path('monarch_v202_lite.html');raw=index.read_bytes();got=blob(raw)
        if got==BASE:
            out=upgrade(raw);index.write_bytes(out);archive.write_bytes(out)
        elif got==TARGET and b'Original Restoration V202 LITE' in raw and NEW1.encode() in raw and NEW2.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw: raise ValueError('Refuse mismatched V202 archive')
            archive.write_bytes(raw)
        else:
            raise ValueError(f'Unknown index version; refusing overwrite: {got}')
        assert index.read_bytes()==archive.read_bytes() and blob(index.read_bytes())==TARGET
        print('PASS V202 index/archive blob',blob(index.read_bytes()));return
    raise SystemExit('Usage: upgrade_v202.py [V201lite V202lite]')

if __name__=='__main__':
    main()
