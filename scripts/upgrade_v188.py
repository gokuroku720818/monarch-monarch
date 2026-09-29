#!/usr/bin/env python3
"""V187 -> V188: finish Action 10 in the same dispatcher pass that removes a DF0 fence core."""
from pathlib import Path
import hashlib,sys

BASE={'lite':'2e91307fbff652dcd1b2010691c7441e335b35ab','full':'b9b856a83bc07aa62d57d6d636b00568cdc707f7'}
OLD="""if(u.actionCode===10&&u.actionTarget){const a=u.actionTarget,ax=Math.floor(a.x),ay=Math.floor(a.y),az=Math.round(a.z),t=tileAt(ax,ay,az);if(!(t===41||t===43||t===45||t===47)){finishWorkAction(u)}else if(originalActionAdjacent(u,a)){if(!prepareOriginalWorkFacing(u,a))continue;/* lm_win.exe 0x43ba75 passes the stored +0x16 target directly to 0x434c57; do not retarget another z in the same x/y column. */if(u.atk<=0)u.atk=18;attackDestructible(u,a);continue}}"""
NEW="""if(u.actionCode===10&&u.actionTarget){const a=u.actionTarget,ax=Math.floor(a.x),ay=Math.floor(a.y),az=Math.round(a.z),t=tileAt(ax,ay,az);if(!(t===41||t===43||t===45||t===47)){finishWorkAction(u)}else if(originalActionAdjacent(u,a)){if(!prepareOriginalWorkFacing(u,a))continue;/* lm_win.exe 0x43ba75 passes the stored +0x16 target directly to 0x434c57; 0x434e4d returns 0 after DF0 removal, so 0x43ba8c finishes/continues the work in this same dispatcher pass. */if(u.atk<=0)u.atk=18;attackDestructible(u,a);if(tileAt(ax,ay,az)===0&&u.alive)finishWorkAction(u);continue}}"""

def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def once(text,old,new,count=1):
    n=text.count(old)
    if n!=count: raise ValueError(f'Expected {count}, found {n}: {old[:100]}')
    return text.replace(old,new)
def upgrade(raw,full=False):
    exp=BASE['full' if full else 'lite']; got=blob(raw)
    if got!=exp: raise ValueError(f'Unknown V187 Git blob; expected {exp}, found {got}')
    text=raw.decode('utf8')
    text=once(text,OLD,NEW)
    text=once(text,'Original Restoration V187','Original Restoration V188',3)
    text=once(text,'ORIGINAL RULE RESTORATION · V187','ORIGINAL RULE RESTORATION · V188')
    text=once(text,'モナークモナーク · v187','モナークモナーク · v188')
    return text.encode('utf8')
def main():
    if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
        src,dst=map(Path,sys.argv[2:]); out=upgrade(src.read_bytes(),True); dst.write_bytes(out); print('V188 full Git blob:',blob(out))
    elif len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]); out=upgrade(src.read_bytes()); dst.write_bytes(out); print('V188 lite Git blob:',blob(out))
    elif len(sys.argv)==1:
        index=Path('index.html'); archive=Path('monarch_v188_lite.html'); raw=index.read_bytes()
        if blob(raw)==BASE['lite']:
            out=upgrade(raw); index.write_bytes(out); archive.write_bytes(out)
        elif b'Original Restoration V188 LITE' in raw and NEW.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw: raise ValueError('Refuse mismatched V188 archive')
            archive.write_bytes(raw)
        else: raise ValueError('Unknown index version; refusing overwrite')
        assert index.read_bytes()==archive.read_bytes()
        print('PASS V188 index/archive blob',blob(index.read_bytes()))
    else: raise SystemExit('Usage: upgrade_v188.py [V187lite V188lite] | [--full V187full V188full]')
if __name__=='__main__': main()
