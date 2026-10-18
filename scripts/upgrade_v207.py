#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys

BASE='227b44d081e59b667e42efc6dfe024e9e6a3b997'
TARGET='a3b037ef3f17bf75fea23e160be2f76a4b3dd9eb'
OLD1="const v=units.find(q=>q?.alive&&q.slot===u.actionTarget.slot);"
NEW1="const v=units.find(q=>q&&(q.alive||q.dying)&&q.slot===u.actionTarget.slot);"
OLD2="if(!v||v===u||(u.actionCode===2?(v.f!==u.f||v.type==='king'):(v.f===u.f||(v.type==='king'&&(factionCastleHP[v.f]||0)>0)))){resetAiAction(u)}"
NEW2="if(!v||v===u){resetAiAction(u)}"
OLD3="if(!u||!v||!u.alive||(!v.alive&&!(u.f===4&&v.dying)))return null;"
NEW3="if(!u||!v||!u.alive||!(v.alive||v.dying))return null;"
OLD4="if(u.f!==4&&v.type==='king'&&actionCode===3&&(factionCastleHP[v.f]||0)>0)return null;"
NEW4=""

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def upgrade(raw):
    got=blob(raw)
    if got!=BASE: raise ValueError(f'Unknown V206 lite blob expected {BASE} got {got}')
    text=raw.decode('utf8')
    for old,name in [(OLD1,'slot live lookup'),(OLD2,'follow revalidation'),(OLD3,'tracked route live gate'),(OLD4,'tracked route castle gate')]:
        if text.count(old)!=1: raise ValueError(f'Expected exact V206 {name} once, got {text.count(old)}')
    text=text.replace(OLD1,NEW1).replace(OLD2,NEW2).replace(OLD3,NEW3).replace(OLD4,NEW4)
    text=text.replace('Original Restoration V206','Original Restoration V207')
    text=text.replace('ORIGINAL RULE RESTORATION · V206','ORIGINAL RULE RESTORATION · V207')
    text=text.replace('モナークモナーク · v206','モナークモナーク · v207')
    out=text.encode('utf8')
    if blob(out)!=TARGET: raise ValueError(f'generated blob mismatch {blob(out)} != {TARGET}')
    return out

def main():
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]);out=upgrade(src.read_bytes());dst.write_bytes(out)
        print('V207 lite Git blob:',blob(out));return
    if len(sys.argv)==1:
        index=Path('index.html');archive=Path('monarch_v207_lite.html');raw=index.read_bytes();got=blob(raw)
        if got==BASE:
            out=upgrade(raw);index.write_bytes(out);archive.write_bytes(out)
        elif got==TARGET and b'Original Restoration V207 LITE' in raw and NEW1.encode() in raw and NEW2.encode() in raw and NEW3.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw: raise ValueError('Refuse mismatched V207 archive')
            archive.write_bytes(raw)
        else: raise ValueError(f'Unknown index version; refusing overwrite: {got}')
        assert index.read_bytes()==archive.read_bytes() and blob(index.read_bytes())==TARGET
        print('PASS V207 index/archive blob',blob(index.read_bytes()));return
    raise SystemExit('Usage: upgrade_v207.py [V206lite V207lite]')

if __name__=='__main__':
    main()
