#!/usr/bin/env python3
"""V178 -> V179: prevent fence orders from choosing unreachable work stands.

Only exact known V178 Git blobs are accepted. Do not modify encoded original assets.
"""
from pathlib import Path
import hashlib
import sys

BASE = {'lite': 'c2ae56bba97734737aac730ad2a0674f9b490bb7',
        'full': 'ef276b2161a09d7303fcfde009f19eeb217bddf0'}
OLD_ORDER = "const stand=bestAdjacentRoute(u,cell);if(!stand)return false;const c={...cell,z};return armWork(u,6,c,mode,'fence',stand)"
NEW_ORDER = "const stand=bestAdjacentRoute(u,cell,true,p=>TEST.originalActionAdjacent&&TEST.originalActionAdjacent({x:p.x+.5,y:p.y+.5,z:p.z},{x:cell.x,y:cell.y,z}));if(!stand)return false;const c={...cell,z};return armWork(u,6,c,mode,'fence',stand)"
OLD_AVAIL = 'fence:!!((buildGround||fence)&&(buildGround?cardStand:workStand))'
NEW_AVAIL = 'fence:!!((buildGround||fence)&&bestAdjacentRoute(u,cell,true,stand=>TEST.originalActionAdjacent&&TEST.originalActionAdjacent({x:stand.x+.5,y:stand.y+.5,z:stand.z},{x:cell.x,y:cell.y,z:fenceZ})))'
OLD_RETURN = 'return{wait:destination'
NEW_RETURN = 'const fenceZ=fence&&!(t&1)&&cell.z>0?cell.z-1:buildGround?cell.z+1:cell.z;return{wait:destination'

def blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def replace_exact(text, old, new, count=1):
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f'Expected {count} matches, found {actual}: {old[:90]!r}')
    return text.replace(old,new)

def upgrade(raw, full=False):
    expected = BASE['full' if full else 'lite']
    if blob(raw) != expected:
        raise RuntimeError(f'Unknown V178 input; expected {expected}, got {blob(raw)}')
    text = raw.decode('utf-8')
    text = replace_exact(text, OLD_ORDER, NEW_ORDER)
    text = replace_exact(text, OLD_RETURN, NEW_RETURN)
    text = replace_exact(text, OLD_AVAIL, NEW_AVAIL)
    text = replace_exact(text, 'Original Restoration V178', 'Original Restoration V179', 3)
    text = replace_exact(text, 'ORIGINAL RULE RESTORATION · V178', 'ORIGINAL RULE RESTORATION · V179')
    text = replace_exact(text, 'モナークモナーク · v178', 'モナークモナーク · v179')
    return text.encode('utf-8')

def main():
    if '--full' in sys.argv:
        if len(sys.argv) != 4: raise SystemExit('Usage: upgrade_v179.py --full <V178full> <V179full>')
        src,dst=map(Path,sys.argv[2:]);dst.write_bytes(upgrade(src.read_bytes(),full=True))
    elif len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]);dst.write_bytes(upgrade(src.read_bytes()))
    elif len(sys.argv)==1:
        index=Path('index.html');release=Path('monarch_v179_lite.html')
        data=index.read_bytes()
        if blob(data)==BASE['lite']:
            updated=upgrade(data);index.write_bytes(updated);release.write_bytes(updated)
        elif b'Original Restoration V179 LITE' in data and NEW_ORDER.encode() in data and NEW_AVAIL.encode() in data:
            if release.exists() and release.read_bytes()!=data:raise RuntimeError('V179 index/release mismatch')
            release.write_bytes(data)
        else:raise RuntimeError('Unknown index version; refuse overwrite')
        assert index.read_bytes()==release.read_bytes()
        print('V179 Git blob:',blob(index.read_bytes()))
    else:raise SystemExit('Usage: upgrade_v179.py [<V178> <V179>] | [--full <V178full> <V179full>]')

if __name__=='__main__':main()
