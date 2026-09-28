#!/usr/bin/env python3
import re,sys
from pathlib import Path

if len(sys.argv)!=3:
    raise SystemExit('Usage: test_v186_asset_stability.py V185 V186')
old_path,new_path=map(Path,sys.argv[1:])
old=old_path.read_text(encoding='utf8')
new=new_path.read_text(encoding='utf8')

OLD_REPEAT="if(family==='base'){if((factionResource[u.f]||0)<100||u.strength<=0)return null;"
NEW_REPEAT="if(family==='base'){if(u.strength<=0)return null;"
OLD_ACTION="if(u.actionCode===4&&u.actionTarget&&originalActionAdjacent(u,u.actionTarget)){const a=u.actionTarget;if(!prepareOriginalWorkFacing(u,a))continue;const built=tryBuildBase(u,a);if(built&&u.alive)finishWorkAction(u);else if(!built)finishWorkAction(u);continue}"
NEW_ACTION="if(u.actionCode===4&&u.actionTarget&&originalActionAdjacent(u,u.actionTarget)){const a=u.actionTarget;if(!prepareOriginalWorkFacing(u,a))continue;/* lm_win.exe 0x4332cb calls the treasury spender only at the work cell; insufficient funds return 1 and 0x43b8df keeps Action 4 active for a later retry. */if((factionResource[u.f]||0)<100)continue;const built=tryBuildBase(u,a);if(built&&u.alive)finishWorkAction(u);else if(!built)finishWorkAction(u);continue}"

assert new.count(NEW_REPEAT)==1 and new.count(NEW_ACTION)==1
reverted=new.replace(NEW_REPEAT,OLD_REPEAT).replace(NEW_ACTION,OLD_ACTION)
reverted=reverted.replace('Original Restoration V186','Original Restoration V185')
reverted=reverted.replace('ORIGINAL RULE RESTORATION · V186','ORIGINAL RULE RESTORATION · V185')
reverted=reverted.replace('モナークモナーク · v186','モナークモナーク · v185')
assert reverted==old,'V186 contains unrelated changes beyond funding-wait flow + version labels'

for name in ('STAGES','SOUND_DATA'):
    a=re.search(r'^const '+name+r'=(.*);$',old,re.M)
    b=re.search(r'^const '+name+r'=(.*);$',new,re.M)
    assert a and b and a.group(1)==b.group(1),f'{name} changed'

pat=re.compile(r'base64,([A-Za-z0-9+/=]+)')
a=pat.findall(old);b=pat.findall(new)
assert a==b,f'embedded base64 payloads changed: {len(a)} -> {len(b)}'
print(f'PASS V186 asset stability: exact reverse-patch equality; STAGES/SOUND_DATA; {len(a)} Base64 payloads')
