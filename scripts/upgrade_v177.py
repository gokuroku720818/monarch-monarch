#!/usr/bin/env python3
"""V177: clear stale commander command menu at native zero-power defeat.

Requires exact released V176 Git blob, preserves all native assets and game rules.
"""
from pathlib import Path
import hashlib

BASE_BLOB='012c19c5505ac5a3f46b4dd73a0d9e965cae530a'
OLD='selected.forEach(i=>{if(units[i]===k)selected.delete(i)})'
NEW=('let clearedKingSelection=false;'
     'selected.forEach(i=>{if(units[i]===k){selected.delete(i);clearedKingSelection=true}});'
     'if(clearedKingSelection)window.__MONARCH_RECONCILE_SELECTION__?.(true)')

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def once(s,a,b,n=1):
    found=s.count(a)
    if found!=n:raise RuntimeError(f'Expected {n} occurrences of {a[:72]!r}, found {found}')
    return s.replace(a,b)

def patch(raw):
    s=raw.decode('utf-8')
    s=once(s,OLD,NEW)
    s=once(s,'Original Restoration V176','Original Restoration V177',3)
    s=once(s,'ORIGINAL RULE RESTORATION · V176','ORIGINAL RULE RESTORATION · V177')
    s=once(s,'モナークモナーク · v176','モナークモナーク · v177')
    return s.encode('utf-8')

def main():
    index=Path('index.html');release=Path('monarch_v177_lite.html')
    raw=index.read_bytes();current=blob(raw)
    if current==BASE_BLOB:
        new=patch(raw);index.write_bytes(new);release.write_bytes(new)
        print('V177: patched exact V176 repo blob')
    elif b'Original Restoration V177 LITE' in raw and NEW.encode() in raw:
        if release.exists():assert raw==release.read_bytes(),'V177 release/index mismatch'
        else:release.write_bytes(raw)
        print('V177: already current')
    else:raise RuntimeError('Unexpected index blob, refusing overwrite: '+current)
    assert index.read_bytes()==release.read_bytes()
    assert b'monarch-original-midi.js' not in index.read_bytes()
    print('V177 blob:',blob(index.read_bytes()))

if __name__=='__main__': main()
