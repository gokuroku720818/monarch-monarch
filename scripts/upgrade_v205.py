#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys

BASE='db3b87755bc7c39faa6a90437d49290bfa79ae62'
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
    return text.encode('utf8')

def main():
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:])
        out=upgrade(src.read_bytes());dst.write_bytes(out)
        print('V205 candidate Git blob:',blob(out));return
    raise SystemExit('Usage: upgrade_v205.py V204lite V205lite')

if __name__=='__main__':
    main()
