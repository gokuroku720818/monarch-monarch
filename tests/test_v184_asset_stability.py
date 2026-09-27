#!/usr/bin/env python3
import hashlib, re, sys
from pathlib import Path

if len(sys.argv)!=3: raise SystemExit('Usage: test_v184_asset_stability.py V183 V184')
old_path,new_path=map(Path,sys.argv[1:])
old=old_path.read_text(encoding='utf-8'); new=new_path.read_text(encoding='utf-8')
OLD="if(u.actionCode===10&&u.actionTarget){const a=u.actionTarget,core=destructibleCoreAt(a.x,a.y);if(!core){finishWorkAction(u)}else{a.z=core.z;if(originalActionAdjacent(u,a)){if(!prepareOriginalWorkFacing(u,a))continue;/* EXE action dispatcher calls work every eligible pass; atk is visual only. */if(u.atk<=0)u.atk=18;attackDestructible(u,a);continue}}}"
NEW="if(u.actionCode===10&&u.actionTarget){const a=u.actionTarget,ax=Math.floor(a.x),ay=Math.floor(a.y),az=Math.round(a.z),t=tileAt(ax,ay,az);if(!(t===41||t===43||t===45||t===47)){finishWorkAction(u)}else if(originalActionAdjacent(u,a)){if(!prepareOriginalWorkFacing(u,a))continue;/* lm_win.exe 0x43ba75 passes the stored +0x16 target directly to 0x434c57; do not retarget another z in the same x/y column. */if(u.atk<=0)u.atk=18;attackDestructible(u,a);continue}}"
assert old.count(OLD)==1, 'V183 Action 10 baseline missing/duplicated'
assert new.count(NEW)==1, 'V184 Action 10 patch missing/duplicated'
reverted=new.replace(NEW,OLD)
reverted=reverted.replace('Original Restoration V184','Original Restoration V183')
reverted=reverted.replace('ORIGINAL RULE RESTORATION · V184','ORIGINAL RULE RESTORATION · V183')
reverted=reverted.replace('モナークモナーク · v184','モナークモナーク · v183')
assert reverted==old, 'V184 contains an unrelated byte/text change beyond Action 10 + version labels'
def assignment(text,name):
    m=re.search(rf'const {name}=',text); assert m, f'{name} missing'
    start=m.end(); end=text.find(';',start); assert end>start
    return text[start:end]
for name in ('STAGES','SOUND_DATA'):
    assert assignment(old,name)==assignment(new,name), f'{name} changed'
pat=re.compile(r'base64,([A-Za-z0-9+/=]+)')
a=pat.findall(old); b=pat.findall(new)
assert len(a)==len(b),f'base64 payload count changed {len(a)} -> {len(b)}'
assert [hashlib.sha256(x.encode()).hexdigest() for x in a]==[hashlib.sha256(x.encode()).hexdigest() for x in b],'embedded base64 payload changed'
print(f'PASS V184 asset stability: exact reverse-patch equality; STAGES/SOUND_DATA; {len(a)} base64 payloads')
