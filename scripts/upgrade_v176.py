#!/usr/bin/env python3
"""V176: close obsolete command UI when an allocated unit reuses a selected slot.

Original 64-slot allocation, rules, maps, sprites and sounds are unchanged.
Requires the exact V175 GitHub blob for release update.
"""
from pathlib import Path
import hashlib

EXPECTED_BASE_BLOB='88b953b3ffea7c00466d5db4a5820ad61590e431'
CALL_OLD='window.__MONARCH_RECONCILE_SELECTION__?.();'
CALL_NEW='window.__MONARCH_RECONCILE_SELECTION__?.(true);'
RECON_OLD='function reconcileSelection(){'
RECON_NEW='function reconcileSelection(force=false){'
GUARD_OLD='if(!changed&&!(commandPause&&!selected.size))return;'
GUARD_NEW='if(!force&&!changed&&!(commandPause&&!selected.size))return;'

def replace_exact(s, old, new, n=1):
    found=s.count(old)
    if found!=n:raise RuntimeError(f'Expected {n} copies, found {found}: {old[:80]}')
    return s.replace(old,new)

def git_blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def patch(raw):
    s=raw.decode('utf8')
    s=replace_exact(s,CALL_OLD,CALL_NEW)
    s=replace_exact(s,RECON_OLD,RECON_NEW)
    s=replace_exact(s,GUARD_OLD,GUARD_NEW)
    s=replace_exact(s,'Original Restoration V175','Original Restoration V176',3)
    s=replace_exact(s,'ORIGINAL RULE RESTORATION · V175','ORIGINAL RULE RESTORATION · V176')
    s=replace_exact(s,'モナークモナーク · v175','モナークモナーク · v176')
    return s.encode('utf8')

def main():
    index=Path('index.html');release=Path('monarch_v176_lite.html')
    raw=index.read_bytes();sha=git_blob(raw)
    if sha==EXPECTED_BASE_BLOB:
        result=patch(raw)
        index.write_bytes(result);release.write_bytes(result)
        print('V176 patched exact V175 Git blob; original game rules/assets unchanged')
    elif b'Original Restoration V176 LITE' in raw and CALL_NEW.encode() in raw and GUARD_NEW.encode() in raw:
        if release.exists():assert raw==release.read_bytes(),'V176 index/release mismatch'
        else:release.write_bytes(raw)
        print('V176 already current')
    else:raise RuntimeError('Unexpected HTML blob; refusing release: '+sha)
    assert index.read_bytes()==release.read_bytes()
    assert b'monarch-original-midi.js' not in index.read_bytes()
    print('V176 Git blob:',git_blob(index.read_bytes()))

if __name__=='__main__':main()
