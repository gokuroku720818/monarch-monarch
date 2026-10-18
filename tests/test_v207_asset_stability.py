#!/usr/bin/env python3
import re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import upgrade_v207 as U
if len(sys.argv)!=3: raise SystemExit('usage: V206 V207')
oldp,newp=map(Path,sys.argv[1:]);oldb=oldp.read_bytes();newb=newp.read_bytes()
assert U.blob(oldb)==U.BASE and U.blob(newb)==U.TARGET
# Exact-blob gated regeneration proves that only the four declared V207 source
# substitutions and version-label updates are present; avoid a brittle manual
# reverse patch that can reinsert the removed gate at the wrong route call.
assert U.upgrade(oldb)==newb
old=oldb.decode();new=newb.decode()
for name in ('STAGES','SOUND_DATA'):
    a=re.search(r'^const '+name+r'=(.*);$',old,re.M);b=re.search(r'^const '+name+r'=(.*);$',new,re.M);assert a and b and a.group(1)==b.group(1),name
pat=re.compile(r'base64,([A-Za-z0-9+/=]+)');a=pat.findall(old);b=pat.findall(new);assert a==b
print(f'PASS V207 exact-blob regeneration; STAGES/SOUND_DATA; {len(a)} Base64 payloads unchanged; blob {U.blob(newb)}')
