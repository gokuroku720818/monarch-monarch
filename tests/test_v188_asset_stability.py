#!/usr/bin/env python3
import re,sys
from pathlib import Path

if len(sys.argv)!=3:
    raise SystemExit('Usage: test_v188_asset_stability.py V187 V188')
old_path,new_path=map(Path,sys.argv[1:])
old=old_path.read_text(encoding='utf-8')
new=new_path.read_text(encoding='utf-8')
OLD="""if(u.actionCode===10&&u.actionTarget){const a=u.actionTarget,ax=Math.floor(a.x),ay=Math.floor(a.y),az=Math.round(a.z),t=tileAt(ax,ay,az);if(!(t===41||t===43||t===45||t===47)){finishWorkAction(u)}else if(originalActionAdjacent(u,a)){if(!prepareOriginalWorkFacing(u,a))continue;/* lm_win.exe 0x43ba75 passes the stored +0x16 target directly to 0x434c57; do not retarget another z in the same x/y column. */if(u.atk<=0)u.atk=18;attackDestructible(u,a);continue}}"""
NEW="""if(u.actionCode===10&&u.actionTarget){const a=u.actionTarget,ax=Math.floor(a.x),ay=Math.floor(a.y),az=Math.round(a.z),t=tileAt(ax,ay,az);if(!(t===41||t===43||t===45||t===47)){finishWorkAction(u)}else if(originalActionAdjacent(u,a)){if(!prepareOriginalWorkFacing(u,a))continue;/* lm_win.exe 0x43ba75 passes the stored +0x16 target directly to 0x434c57; 0x434e4d returns 0 after DF0 removal, so 0x43ba8c finishes/continues the work in this same dispatcher pass. */if(u.atk<=0)u.atk=18;attackDestructible(u,a);if(tileAt(ax,ay,az)===0&&u.alive)finishWorkAction(u);continue}}"""
assert old.count(OLD)==1,'V187 baseline missing/duplicated'
assert new.count(NEW)==1,'V188 patch missing/duplicated'
reverted=new.replace(NEW,OLD)
reverted=reverted.replace('Original Restoration V188','Original Restoration V187')
reverted=reverted.replace('ORIGINAL RULE RESTORATION · V188','ORIGINAL RULE RESTORATION · V187')
reverted=reverted.replace('モナークモナーク · v188','モナークモナーク · v187')
assert reverted==old,'V188 contains unrelated changes beyond same-pass finish + version labels'
for name in ('STAGES','SOUND_DATA'):
    a=re.search(r'^const '+name+r'=(.*);$',old,re.M)
    b=re.search(r'^const '+name+r'=(.*);$',new,re.M)
    assert a and b and a.group(1)==b.group(1),f'{name} changed'
pat=re.compile(r'base64,([A-Za-z0-9+/=]+)')
a=pat.findall(old);b=pat.findall(new)
assert a==b,f'embedded Base64 changed: {len(a)} -> {len(b)}'
print(f'PASS V188 asset stability: exact reverse-patch equality; STAGES/SOUND_DATA; {len(a)} Base64 payloads')
