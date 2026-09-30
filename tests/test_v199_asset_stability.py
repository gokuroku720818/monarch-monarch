#!/usr/bin/env python3
import re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import upgrade_v199 as U
if len(sys.argv)!=3: raise SystemExit('usage: V198 V199')
oldp,newp=map(Path,sys.argv[1:]);oldb=oldp.read_bytes();newb=newp.read_bytes();kind='full' if len(oldb)>10_000_000 else 'lite'
assert U.blob(oldb)==U.BASE[kind] and U.blob(newb)==U.TARGET[kind]
assert U.upgrade(oldb,kind)==newb
old=oldb.decode();new=newb.decode()
rev=new.replace(U.NEW1,U.OLD1).replace(U.NEW2,U.OLD2).replace('Original Restoration V199','Original Restoration V198').replace('ORIGINAL RULE RESTORATION · V199','ORIGINAL RULE RESTORATION · V198').replace('モナークモナーク · v199','モナークモナーク · v198')
assert rev==old
for name in ('STAGES','SOUND_DATA'):
 a=re.search(r'^const '+name+r'=(.*);$',old,re.M);b=re.search(r'^const '+name+r'=(.*);$',new,re.M);assert a and b and a.group(1)==b.group(1),name
pat=re.compile(r'base64,([A-Za-z0-9+/=]+)');a=pat.findall(old);b=pat.findall(new);assert a==b
print(f'PASS V199 {kind} exact reverse-patch; STAGES/SOUND_DATA; {len(a)} Base64 payloads unchanged; blob {U.blob(newb)}')
