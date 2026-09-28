#!/usr/bin/env python3
import re,sys
from pathlib import Path

if len(sys.argv)!=3:
    raise SystemExit('Usage: test_v185_asset_stability.py V184 V185')
old_path,new_path=map(Path,sys.argv[1:])
old=old_path.read_text(encoding='utf-8')
new=new_path.read_text(encoding='utf-8')
OLD="if(family==='base'){if((factionResource[u.f]||0)<100||u.strength<=1)return null;"
NEW="if(family==='base'){if((factionResource[u.f]||0)<100||u.strength<=0)return null;"
assert old.count(OLD)==1,'V184 repeatCandidate baseline missing/duplicated'
assert new.count(NEW)==1,'V185 patch missing/duplicated'
reverted=new.replace(NEW,OLD)
reverted=reverted.replace('Original Restoration V185','Original Restoration V184')
reverted=reverted.replace('ORIGINAL RULE RESTORATION · V185','ORIGINAL RULE RESTORATION · V184')
reverted=reverted.replace('モナークモナーク · v185','モナークモナーク · v184')
assert reverted==old,'V185 contains unrelated changes beyond final-strength gate + version labels'
for name in ('STAGES','SOUND_DATA'):
    a=re.search(r'^const '+name+r'=(.*);$',old,re.M)
    b=re.search(r'^const '+name+r'=(.*);$',new,re.M)
    assert a and b and a.group(1)==b.group(1),f'{name} changed'
pat=re.compile(r'base64,([A-Za-z0-9+/=]+)')
a=pat.findall(old);b=pat.findall(new)
assert a==b,f'embedded base64 payloads changed: {len(a)} -> {len(b)}'
print(f'PASS V185 asset stability: exact reverse-patch equality; STAGES/SOUND_DATA; {len(a)} base64 payloads')
