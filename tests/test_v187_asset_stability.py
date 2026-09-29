#!/usr/bin/env python3
import re,sys
from pathlib import Path

if len(sys.argv)!=3:
    raise SystemExit('Usage: test_v187_asset_stability.py V186 V187')

old_path,new_path=map(Path,sys.argv[1:])
old=old_path.read_text(encoding='utf-8')
new=new_path.read_text(encoding='utf-8')
OLD="else if(family==='destroyBase'){const t=surfaceChip[y*32+x];if(t>=29&&t<=32)return{action:8,x,y,z,standX:cur.x,standY:cur.y,standZ:cur.z}}"
NEW="else if(family==='destroyBase'){const t=surfaceChip[y*32+x];if(t>=29&&t<=32&&t!==29+u.f)return{action:8,x,y,z,standX:cur.x,standY:cur.y,standZ:cur.z}}"

assert old.count(OLD)==1,'V186 baseline missing/duplicated'
assert new.count(NEW)==1,'V187 patch missing/duplicated'

reverted=new.replace(NEW,OLD)
reverted=reverted.replace('Original Restoration V187','Original Restoration V186')
reverted=reverted.replace('ORIGINAL RULE RESTORATION · V187','ORIGINAL RULE RESTORATION · V186')
reverted=reverted.replace('モナークモナーク · v187','モナークモナーク · v186')
assert reverted==old,'V187 contains unrelated changes beyond own-base exclusion + version labels'

for name in ('STAGES','SOUND_DATA'):
    a=re.search(r'^const '+name+r'=(.*);$',old,re.M)
    b=re.search(r'^const '+name+r'=(.*);$',new,re.M)
    assert a and b and a.group(1)==b.group(1),f'{name} changed'

pat=re.compile(r'base64,([A-Za-z0-9+/=]+)')
a=pat.findall(old);b=pat.findall(new)
assert a==b,f'embedded Base64 changed: {len(a)} -> {len(b)}'
print(f'PASS V187 asset stability: exact reverse-patch equality; STAGES/SOUND_DATA; {len(a)} Base64 payloads')
