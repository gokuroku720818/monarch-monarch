#!/usr/bin/env python3
import re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import upgrade_v198 as U
if len(sys.argv)!=3: raise SystemExit('usage: V197 V198')
oldp,newp=map(Path,sys.argv[1:]);oldb=oldp.read_bytes();newb=newp.read_bytes();kind='full' if len(oldb)>10_000_000 else 'lite'
assert U.blob(oldb)==U.BASE[kind] and U.blob(newb)==U.TARGET[kind]
assert U.upgrade(oldb,kind)==newb
old=oldb.decode();new=newb.decode()
rev=new.replace(U.NEW,U.OLD).replace('Original Restoration V198','Original Restoration V197').replace('ORIGINAL RULE RESTORATION · V198','ORIGINAL RULE RESTORATION · V197').replace('モナークモナーク · v198','モナークモナーク · v197')
assert rev==old
for name in ('STAGES','SOUND_DATA'):
    a=re.search(r'^const '+name+r'=(.*);$',old,re.M);b=re.search(r'^const '+name+r'=(.*);$',new,re.M);assert a and b and a.group(1)==b.group(1),name
pat=re.compile(r'base64,([A-Za-z0-9+/=]+)');a=pat.findall(old);b=pat.findall(new);assert a==b
print(f'PASS V198 {kind} exact reverse-patch; STAGES/SOUND_DATA; {len(a)} Base64 payloads unchanged; blob {U.blob(newb)}')
