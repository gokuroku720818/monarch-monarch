#!/usr/bin/env python3
"""Upgrade only byte-exact V180 assets, preserving all native data."""
from pathlib import Path
import hashlib,sys
BASE={'lite':'4ae885ab5a823847defd8b86cbeeeab1fe036a11','full':'f89933ce48f5c0fd379231082d0d0e87e4129b56'}
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def change(s,a,b,n=1):
    if s.count(a)!=n:raise ValueError(f'Expected {n} matches, got {s.count(a)} for {a[:90]}')
    return s.replace(a,b)
WORK='workStand=(anyBase||enemyFort||fence||intactBridge||brokenBridge||water||forest||vegetation||pit)?bestAdjacentRoute(u,cell,true):null'
NEW_WORK="workTargetZ=fence&&!(t&1)&&cell.z>0&&TEST.tileAt(cell.x,cell.y,cell.z-1)===t+1?cell.z-1:cell.z,workStand=(anyBase||enemyFort||fence||intactBridge||brokenBridge||water||forest||vegetation||pit)?bestAdjacentRoute(u,cell,true,stand=>TEST.originalActionAdjacent&&TEST.originalActionAdjacent({x:stand.x+.5,y:stand.y+.5,z:stand.z},{x:cell.x,y:cell.y,z:workTargetZ})):null"
OLD='const stand=bestAdjacentRoute(u,cell);if(!stand)return false;const t=cell.v|0;'
NEW="const t=cell.v|0,workZ=kind==='destroyFence'&&t>=40&&t<=47&&!(t&1)&&cell.z>0&&TEST.tileAt(cell.x,cell.y,cell.z-1)===t+1?cell.z-1:cell.z;const stand=bestAdjacentRoute(u,cell,true,c=>TEST.originalActionAdjacent&&TEST.originalActionAdjacent({x:c.x+.5,y:c.y+.5,z:c.z},{x:cell.x,y:cell.y,z:workZ}));if(!stand)return false;const workCell=workZ===cell.z?cell:{...cell,z:workZ,v:TEST.tileAt(cell.x,cell.y,workZ)};"
def upgrade(raw,full=False):
    want=BASE['full' if full else 'lite']
    if blob(raw)!=want:raise ValueError(f'Expected exact V180 Git blob {want}, got {blob(raw)}')
    s=raw.decode('utf8')
    s=change(s,WORK,NEW_WORK)
    s=change(s,OLD,NEW)
    s=change(s,"armWork(u,10,cell,mode,'destroyFence',stand)","armWork(u,10,workCell,mode,'destroyFence',stand)")
    s=change(s,'Original Restoration V180','Original Restoration V181',3)
    s=change(s,'ORIGINAL RULE RESTORATION · V180','ORIGINAL RULE RESTORATION · V181')
    s=change(s,'モナークモナーク · v180','モナークモナーク · v181')
    return s.encode('utf8')
def main():
    if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
        a,b=map(Path,sys.argv[2:]);b.write_bytes(upgrade(a.read_bytes(),True))
    elif len(sys.argv)==3:
        a,b=map(Path,sys.argv[1:]);b.write_bytes(upgrade(a.read_bytes()))
    elif len(sys.argv)==1:
        a=Path('index.html');b=Path('monarch_v181_lite.html');raw=a.read_bytes()
        if blob(raw)==BASE['lite']:
            updated=upgrade(raw);a.write_bytes(updated);b.write_bytes(updated)
        elif b'Original Restoration V181 LITE' in raw and NEW_WORK.encode() in raw and NEW.encode() in raw:
            if b.exists() and b.read_bytes()!=raw:raise ValueError('V181 release mismatch')
            b.write_bytes(raw)
        else:raise ValueError('Unknown index; refusing overwrite')
        assert a.read_bytes()==b.read_bytes();print('PASS V181',blob(a.read_bytes()))
    else:raise SystemExit('Usage: upgrade_v181.py [V180lite V181lite] | [--full V180full V181full]')
if __name__=='__main__':main()
