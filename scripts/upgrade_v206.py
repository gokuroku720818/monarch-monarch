#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys

BASE='c9ac6ee11b641e536b845c6843ab3e3d1faf57c1'
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
    return text.encode('utf8')

def main():
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]);out=upgrade(src.read_bytes());dst.write_bytes(out)
        print('V206 candidate Git blob:',blob(out));return
    raise SystemExit('Usage: upgrade_v206.py V205lite V206lite')

if __name__=='__main__':
    main()
