#!/usr/bin/env python3
"""Upgrade exact V177 HTML to V178, fixing water/deck height mismatch only.

This script is intentionally exact-blob gated. Never apply a global version
number substitution to embedded Base64 assets.
"""
from pathlib import Path
import hashlib
import sys

V177_LITE_BLOB = '8c4bcbbd2e52aa3356859d79fd9b8a9659da2b76'
V177_FULL_BLOB = '0469ce49788ca529bbfc368dc3ca3459e4f2222e'
OLD = '''if(!originalActionAdjacent(u,{x,y,z}))return false;
   let t=tileAt(x,y,z);if(t>=69&&t<=79)return repairBridge(u,target);'''
NEW = '''// A water bridge is built at z+1, so validate the future DECK, not the water below.
   // This is also the height validated by bridgeOrderStand() when issuing the command.
   const t=tileAt(x,y,z),workZ=(t>=83&&t<=110)?z+1:z;
   if(workZ>=48||!originalActionAdjacent(u,{x,y,z:workZ}))return false;
   if(t>=69&&t<=79)return repairBridge(u,target);'''

# The dispatcher must use the SAME deck level as both the command availability
# check and workBridge(). Otherwise it never calls workBridge() at all.
DISPATCH_OLD = 'else if(originalActionAdjacent(u,a)){if(!prepareOriginalWorkFacing(u,a))continue;/* EXE action dispatcher calls work every eligible pass; atk is visual only. */if(u.atk<=0)u.atk=18;const ok=workBridge(u,a);'
DISPATCH_NEW = 'else if(originalActionAdjacent(u,{x:a.x,y:a.y,z:(t>=83&&t<=110)?a.z+1:a.z})){if(!prepareOriginalWorkFacing(u,a))continue;/* EXE action dispatcher calls work every eligible pass; atk is visual only. */if(u.atk<=0)u.atk=18;const ok=workBridge(u,a);'

def blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def replace_exact(src, old, new, count=1):
    actual=src.count(old)
    if actual!=count:
        raise RuntimeError(f'Expected {count} matches, saw {actual}: {old[:80]!r}')
    return src.replace(old,new)

def patch(raw, full=False):
    expected=V177_FULL_BLOB if full else V177_LITE_BLOB
    if blob(raw)!=expected:
        raise RuntimeError(f'Refusing to edit unknown version: expected {expected}, got {blob(raw)}')
    s=raw.decode('utf-8')
    s=replace_exact(s,OLD,NEW)
    s=replace_exact(s,DISPATCH_OLD,DISPATCH_NEW)
    # Anchored human-visible labels only, not binary strings / embedded assets.
    s=replace_exact(s,'Original Restoration V177','Original Restoration V178',3)
    s=replace_exact(s,'ORIGINAL RULE RESTORATION · V177','ORIGINAL RULE RESTORATION · V178')
    s=replace_exact(s,'モナークモナーク · v177','モナークモナーク · v178')
    return s.encode('utf-8')

def main():
    # In the repository only the LITE page is published. The FULL asset-rich HTML
    # stays a downloadable conversation artifact and is patched with --full.
    if '--full' in sys.argv:
        src=Path(sys.argv[-2]);dst=Path(sys.argv[-1]);dst.write_bytes(patch(src.read_bytes(),full=True))
    elif len(sys.argv)==3:
        src=Path(sys.argv[1]);dst=Path(sys.argv[2]);dst.write_bytes(patch(src.read_bytes()))
    elif len(sys.argv)==1:
        index=Path('index.html');release=Path('monarch_v178_lite.html')
        raw=index.read_bytes()
        if blob(raw)==V177_LITE_BLOB:
            out=patch(raw);index.write_bytes(out);release.write_bytes(out)
        elif b'Original Restoration V178 LITE' in raw and NEW.encode() in raw:
            if release.exists() and release.read_bytes()!=raw:
                raise RuntimeError('V178 release and index differ')
            release.write_bytes(raw)
        else:
            raise RuntimeError('Unknown index version; refusing overwrite')
        assert index.read_bytes()==release.read_bytes()
        print('V178 release git blob:',blob(index.read_bytes()))
    else:
        raise SystemExit('Usage: upgrade_v178.py [<V177.html> <V178.html>] | [--full <in> <out>]')

if __name__=='__main__': main()
