#!/usr/bin/env python3
"""V182 -> V183: reject bridge work orders that the worker would refuse at DF100."""
from pathlib import Path
import hashlib, sys

BASE = {
    'lite': 'f655016b8c1c3b111311c81b53b4d287980affd0',
    'full': '415f3c484292173a00d591fbaf5d356f1ee39049',
}

OLD = """function bridgeOrderStand(u,cell){
   if(!u||!cell||!TEST.tileAt)return null;
   const t=TEST.tileAt(cell.x,cell.y,cell.z),water=t>=83&&t<=110,existing=(t>=58&&t<=80);
   if(!water&&!existing)return null;
   const targetZ=cell.z+(water?1:0),cost=water||t===80?20:5,resources=TEST.getResources?TEST.getResources():[];
   if(targetZ>=48||(resources[u.f]||0)<cost||(water&&TEST.tileAt(cell.x,cell.y,targetZ)!==0))return null;
   return bestAdjacentRoute(u,cell,true,stand=>TEST.originalActionAdjacent&&TEST.originalActionAdjacent({x:stand.x+.5,y:stand.y+.5,z:stand.z},{x:cell.x,y:cell.y,z:targetZ}));
 }"""
NEW = """function bridgeOrderStand(u,cell){
   if(!u||!cell||!TEST.tileAt)return null;
   const t=TEST.tileAt(cell.x,cell.y,cell.z),water=t>=83&&t<=110,existing=(t>=58&&t<=80),intact=t>=58&&t<=68;
   if(!water&&!existing)return null;
   const bridgePower=intact?Math.max(0,Math.trunc((TEST.getCellPower?TEST.getCellPower(cell.x,cell.y,cell.z):undefined)??100)):0;
   if(intact&&bridgePower>=100)return null;
   const targetZ=cell.z+(water?1:0),cost=water||t===80?20:5,resources=TEST.getResources?TEST.getResources():[];
   if(targetZ>=48||(resources[u.f]||0)<cost||(water&&TEST.tileAt(cell.x,cell.y,targetZ)!==0))return null;
   return bestAdjacentRoute(u,cell,true,stand=>TEST.originalActionAdjacent&&TEST.originalActionAdjacent({x:stand.x+.5,y:stand.y+.5,z:stand.z},{x:cell.x,y:cell.y,z:targetZ}));
 }"""

def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def once(text, old, new, count=1):
    found=text.count(old)
    if found!=count:
        raise ValueError(f'Expected {count} instances; found {found}: {old[:90]}')
    return text.replace(old,new)

def upgrade(raw, full=False):
    expected=BASE['full' if full else 'lite']
    if blob(raw)!=expected:
        raise ValueError(f'Unknown V182 Git blob; expected {expected}, found {blob(raw)}')
    text=raw.decode('utf-8')
    text=once(text,OLD,NEW)
    text=once(text,'Original Restoration V182','Original Restoration V183',3)
    text=once(text,'ORIGINAL RULE RESTORATION · V182','ORIGINAL RULE RESTORATION · V183')
    text=once(text,'モナークモナーク · v182','モナークモナーク · v183')
    return text.encode('utf-8')

def main():
    if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
        src,dst=map(Path,sys.argv[2:]); dst.write_bytes(upgrade(src.read_bytes(),True))
    elif len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]); dst.write_bytes(upgrade(src.read_bytes(),False))
    elif len(sys.argv)==1:
        index=Path('index.html'); archive=Path('monarch_v183_lite.html'); data=index.read_bytes()
        if blob(data)==BASE['lite']:
            data=upgrade(data); index.write_bytes(data); archive.write_bytes(data)
        elif b'Original Restoration V183 LITE' in data and NEW.encode() in data:
            if archive.exists() and archive.read_bytes()!=data: raise ValueError('Refuse mismatched V183 archive')
            archive.write_bytes(data)
        else: raise ValueError('Unknown index version; refusing overwrite')
        assert index.read_bytes()==archive.read_bytes()
        print('PASS V183 index/archive blob',blob(index.read_bytes()))
    else:
        raise SystemExit('Usage: upgrade_v183.py [V182lite V183lite] | [--full V182full V183full]')

if __name__=='__main__': main()
