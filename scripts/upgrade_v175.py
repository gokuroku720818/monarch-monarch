#!/usr/bin/env python3
"""V175: clear abandoned touch identifier when app loses window focus.

Keeps original selection handlers, map/audio/sprites and simulation unchanged.
Only patch the exact verified V174 GitHub file; never overwrite unknown changes.
"""
from pathlib import Path
import hashlib

EXPECTED_BASE_BLOB='8adf9f7067a978156084c3b29974a3754f0a75f4'
ANCHOR=' let marqueeTouchId=null;\n function relayMarqueeTouch(type,t){'
REPLACEMENT=''' let marqueeTouchId=null;
 // A backgrounded mobile tab can miss touchend; a stale id must not block the next drag.
 window.addEventListener('blur',()=>{marqueeTouchId=null;});
 function relayMarqueeTouch(type,t){'''

def change_once(s,old,new,expected=1):
    actual=s.count(old)
    if actual!=expected: raise RuntimeError(f'Unexpected occurrence {actual} vs {expected}: {old[:85]!r}')
    return s.replace(old,new)

def patch(src):
    s=src.decode('utf8')
    s=change_once(s,ANCHOR,REPLACEMENT)
    s=change_once(s,'Original Restoration V174','Original Restoration V175',3)
    s=change_once(s,'ORIGINAL RULE RESTORATION · V174','ORIGINAL RULE RESTORATION · V175')
    s=change_once(s,'モナークモナーク · v174','モナークモナーク · v175')
    return s.encode('utf8')

def git_blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()

def main():
    base=Path('index.html'); release=Path('monarch_v175_lite.html')
    raw=base.read_bytes();sha=git_blob(raw)
    if sha==EXPECTED_BASE_BLOB:
        updated=patch(raw)
        base.write_bytes(updated);release.write_bytes(updated)
        print('Patched original V174 Git blob into V175; no resource or gameplay edits')
    elif b'Original Restoration V175 LITE' in raw and REPLACEMENT.encode('utf8') in raw:
        if release.exists(): assert release.read_bytes()==raw,'index and release differ'
        else: release.write_bytes(raw)
        print('V175 already installed')
    else: raise RuntimeError('Unexpected deployed HTML blob; refusing overwrite: '+sha)
    assert base.read_bytes()==release.read_bytes()
    assert b'monarch-original-midi.js' not in base.read_bytes()
    print('V175 Git blob:',git_blob(base.read_bytes()))

if __name__=='__main__': main()
