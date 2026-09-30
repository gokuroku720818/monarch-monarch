#!/usr/bin/env python3
import re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import upgrade_v204 as U
if len(sys.argv)!=3: raise SystemExit('usage: V203 V204')
oldp,newp=map(Path,sys.argv[1:]);oldb=oldp.read_bytes();newb=newp.read_bytes()
assert U.blob(oldb)==U.BASE and U.blob(newb)==U.TARGET
assert U.upgrade(oldb)==newb
old=oldb.decode();new=newb.decode()
rev=new.replace(U.NEW,U.OLD).replace('Original Restoration V204','Original Restoration V203').replace('ORIGINAL RULE RESTORATION · V204','ORIGINAL RULE RESTORATION · V203').replace('モナークモナーク · v204','モナークモナーク · v203')
assert rev==old
for name in ('STAGES','SOUND_DATA'):
    a=re.search(r'^const '+name+r'=(.*);$',old,re.M);b=re.search(r'^const '+name+r'=(.*);$',new,re.M);assert a and b and a.group(1)==b.group(1),name
pat=re.compile(r'base64,([A-Za-z0-9+/=]+)');a=pat.findall(old);b=pat.findall(new);assert a==b
print(f'PASS V204 exact reverse-patch; STAGES/SOUND_DATA; {len(a)} Base64 payloads unchanged; blob {U.blob(newb)}')
