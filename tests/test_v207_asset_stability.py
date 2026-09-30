#!/usr/bin/env python3
import re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import upgrade_v207 as U
if len(sys.argv)!=3: raise SystemExit('usage: V206 V207')
oldp,newp=map(Path,sys.argv[1:]);oldb=oldp.read_bytes();newb=newp.read_bytes()
assert U.blob(oldb)==U.BASE and U.blob(newb)==U.TARGET
assert U.upgrade(oldb)==newb
old=oldb.decode();new=newb.decode()
rev=new.replace(U.NEW1,U.OLD1).replace(U.NEW2,U.OLD2).replace(U.NEW3,U.OLD3)
# OLD4 was deleted in V207; restore it immediately before route calculation.
rev=rev.replace("    let p=route(u,v.x,v.y,v.z);if(p)return p;", "    "+U.OLD4+"\n    let p=route(u,v.x,v.y,v.z);if(p)return p;",1)
rev=rev.replace('Original Restoration V207','Original Restoration V206').replace('ORIGINAL RULE RESTORATION · V207','ORIGINAL RULE RESTORATION · V206').replace('モナークモナーク · v207','モナークモナーク · v206')
assert rev==old
for name in ('STAGES','SOUND_DATA'):
    a=re.search(r'^const '+name+r'=(.*);$',old,re.M);b=re.search(r'^const '+name+r'=(.*);$',new,re.M);assert a and b and a.group(1)==b.group(1),name
pat=re.compile(r'base64,([A-Za-z0-9+/=]+)');a=pat.findall(old);b=pat.findall(new);assert a==b
print(f'PASS V207 exact reverse-patch; STAGES/SOUND_DATA; {len(a)} Base64 payloads unchanged; blob {U.blob(newb)}')
