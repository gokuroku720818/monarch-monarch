#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys
BASE='99bf93612175400b45feaf73d2a7b52292d7b381'
OLD="if(!u||!u.alive||u.f!==4||u.type==='king')return false;u.neutralCounter=((u.neutralCounter||0)+1)&0xff;"
NEW="if(!u||!u.alive||u.f!==4||u.type==='king')return false;if(u.path||u.target)return true;u.neutralCounter=((u.neutralCounter||0)+1)&0xff;"
def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def upgrade(raw):
    got=blob(raw)
    if got!=BASE: raise ValueError(f'Unknown V203 lite blob expected {BASE} got {got}')
    s=raw.decode('utf8')
    if s.count(OLD)!=1: raise ValueError(f'Expected exact V203 neutral counter prefix once, got {s.count(OLD)}')
    s=s.replace(OLD,NEW)
    s=s.replace('Original Restoration V203','Original Restoration V204')
    s=s.replace('ORIGINAL RULE RESTORATION · V203','ORIGINAL RULE RESTORATION · V204')
    s=s.replace('モナークモナーク · v203','モナークモナーク · v204')
    return s.encode()
def main():
    if len(sys.argv)==3:
        a,b=map(Path,sys.argv[1:]);out=upgrade(a.read_bytes());b.write_bytes(out);print('V204 candidate Git blob:',blob(out));return
    if len(sys.argv)==1:
        p=Path('index.html');a=Path('monarch_v204_lite.html');out=upgrade(p.read_bytes());p.write_bytes(out);a.write_bytes(out);print('V204 candidate Git blob:',blob(out));return
    raise SystemExit('usage: upgrade_v204.py [V203 V204]')
if __name__=='__main__': main()
