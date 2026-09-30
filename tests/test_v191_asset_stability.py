#!/usr/bin/env python3
import re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts import upgrade_v191 as U

if len(sys.argv)!=3:
    raise SystemExit('usage: V190 V191')
oldp,newp=map(Path,sys.argv[1:])
oldb=oldp.read_bytes()
newb=newp.read_bytes()
kind='full' if len(oldb)>10_000_000 else 'lite'
assert U.blob(oldb)==U.BASE[kind],(kind,U.blob(oldb))
assert U.blob(newb)==U.TARGET[kind],(kind,U.blob(newb))
assert U.upgrade(oldb,kind)==newb,'V191 must be exactly reproducible from exact V190 blob'

old=oldb.decode('utf8')
new=newb.decode('utf8')
rev=new.replace(U.NEW,U.OLD)
rev=rev.replace('Original Restoration V191','Original Restoration V190')
rev=rev.replace('ORIGINAL RULE RESTORATION · V191','ORIGINAL RULE RESTORATION · V190')
rev=rev.replace('モナークモナーク · v191','モナークモナーク · v190')
assert rev==old,'V191 contains unrelated changes beyond strict radius gate + version labels'

for name in ('STAGES','SOUND_DATA'):
    a=re.search(r'^const '+name+r'=(.*);$',old,re.M)
    b=re.search(r'^const '+name+r'=(.*);$',new,re.M)
    assert a and b and a.group(1)==b.group(1),name

pat=re.compile(r'base64,([A-Za-z0-9+/=]+)')
a=pat.findall(old)
b=pat.findall(new)
assert a==b,(len(a),len(b))
print(f'PASS V191 {kind} exact reverse-patch; STAGES/SOUND_DATA; {len(a)} Base64 payloads unchanged; blob {U.blob(newb)}')
