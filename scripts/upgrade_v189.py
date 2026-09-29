#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys
BASE={
 'lite':'dd5e3442c36bf4b7cd14377b8990379dfed534f7',
 'full':'5a9e6081f43b8a0a8a7b85e4e82fc498b50afbdb',
}

def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def once(t,o,n,c=1):
    a=t.count(o)
    if a!=c: raise ValueError(f'expected {c}, found {a}: {o[:120]!r}')
    return t.replace(o,n)

OLD_ROUTE="""function route(u,tx,ty,targetZ=null){
   const sx=Math.floor(u.x),sy=Math.floor(u.y),sz=Math.round(u.z),gx=Math.floor(tx),gy=Math.floor(ty),gz=targetZ==null?null:Math.round(targetZ),start=vk(sx,sy,sz),q=[[sx,sy,sz]],prev=new Map([[start,null]]),how=new Map();let end=null,head=0;
   while(head<q.length&&q.length<45000){const [x,y,z]=q[head++];if(x===gx&&y===gy&&(gz===null||z===gz)){end=vk(x,y,z);break}
     // lm_win.exe 0x4427fb: horizontal route reconstruction tests direction bytes 0,2,4,6 only.
     for(const d of CARD){const [dx,dy]=DIRS[d],nx=x+dx,ny=y+dy,nz=resolveStep(nx,ny,z,gx,gy);if(nz==null)continue;
       if(commanderBlocksRoute(u,nx,ny,nz))continue;const k=vk(nx,ny,nz);if(prev.has(k))continue;prev.set(k,vk(x,y,z));how.set(k,d);q.push([nx,ny,nz])}}
   if(!end)return null;const out=[];let cur=end;while(cur!==start){const [x,y,z]=cur.split(',').map(Number);out.push({x,y,z,dir:how.get(cur)});cur=prev.get(cur);if(cur==null)return null}out.reverse();return out;
 }"""
NEW_ROUTE="""function route(u,tx,ty,targetZ=null){
   const sx=Math.floor(u.x),sy=Math.floor(u.y),sz=Math.round(u.z),gx=Math.floor(tx),gy=Math.floor(ty),gz=targetZ==null?null:Math.round(targetZ),start=vk(sx,sy,sz),q=[[sx,sy,sz]],dist=new Map([[start,0]]);let end=null,head=0;
   while(head<q.length&&q.length<45000){const [x,y,z]=q[head++],base=vk(x,y,z),d0=dist.get(base)||0;if(x===gx&&y===gy&&(gz===null||z===gz)){end=base;break}
     for(const d of CARD){const [dx,dy]=DIRS[d],nx=x+dx,ny=y+dy,nz=resolveStep(nx,ny,z,gx,gy);if(nz==null)continue;
       if(commanderBlocksRoute(u,nx,ny,nz))continue;const k=vk(nx,ny,nz);if(dist.has(k))continue;dist.set(k,d0+1);q.push([nx,ny,nz])}}
   return end?originalCardinalBacktrack(start,end,dist):null;
 }"""

OLD_AI_ROUTE="""function routeWithOriginalAiBlocks(u,tx,ty,blocked,targetZ=null){
   const sx=Math.floor(u.x),sy=Math.floor(u.y),sz=Math.round(u.z),gx=Math.floor(tx),gy=Math.floor(ty),start=vk(sx,sy,sz),q=[[sx,sy,sz]],prev=new Map([[start,null]]),how=new Map();let end=null,head=0;
   blocked=blocked||new Set();const gz=targetZ==null?null:Math.round(targetZ);
   while(head<q.length&&q.length<45000){const [x,y,z]=q[head++];if(x===gx&&y===gy&&(gz===null||z===gz)){end=vk(x,y,z);break}
     for(const d of CARD){const [dx,dy]=DIRS[d],nx=x+dx,ny=y+dy,nz=resolveStep(nx,ny,z,gx,gy);if(nz==null)continue;if(commanderBlocksRoute(u,nx,ny,nz))continue;const k=vk(nx,ny,nz);if(blocked.has(k)||prev.has(k))continue;prev.set(k,vk(x,y,z));how.set(k,d);q.push([nx,ny,nz])}}
   if(!end)return null;const out=[];let cur=end;while(cur!==start){const [x,y,z]=cur.split(',').map(Number);out.push({x,y,z,dir:how.get(cur)});cur=prev.get(cur);if(cur==null)return null}out.reverse();return out;
 }"""
NEW_AI_ROUTE="""function originalCardinalBacktrack(start,end,dist){
   // lm_win.exe 0x4424e0/0x4427fb: the flood stores distance only. Path bytes are rebuilt
   // from target to source by probing 0,2,4,6 and accepting a strictly lower distance.
   const out=[];let cur=end;
   while(cur!==start){const [x,y,z]=cur.split(',').map(Number),curDist=dist.get(cur);if(curDist==null)return null;let prev=null,prevDir=-1,best=curDist;
     for(const d of CARD){const [dx,dy]=DIRS[d],nx=x+dx,ny=y+dy,nz=resolveStep(nx,ny,z,x,y);if(nz==null)continue;const k=vk(nx,ny,nz),nd=dist.get(k);if(nd!=null&&nd<best){best=nd;prev=k;prevDir=d}}
     if(prev==null)return null;out.push({x,y,z,dir:(prevDir+4)&7});cur=prev;
   }
   out.reverse();return out;
 }
 function routeWithOriginalAiBlocks(u,tx,ty,blocked,targetZ=null){
   const sx=Math.floor(u.x),sy=Math.floor(u.y),sz=Math.round(u.z),gx=Math.floor(tx),gy=Math.floor(ty),start=vk(sx,sy,sz),q=[[sx,sy,sz]],dist=new Map([[start,0]]);let end=null,head=0;
   blocked=blocked||new Set();const gz=targetZ==null?null:Math.round(targetZ);
   while(head<q.length&&q.length<45000){const [x,y,z]=q[head++],base=vk(x,y,z),d0=dist.get(base)||0;if(x===gx&&y===gy&&(gz===null||z===gz)){end=base;break}
     for(const d of CARD){const [dx,dy]=DIRS[d],nx=x+dx,ny=y+dy,nz=resolveStep(nx,ny,z,gx,gy);if(nz==null)continue;if(commanderBlocksRoute(u,nx,ny,nz))continue;const k=vk(nx,ny,nz);if(blocked.has(k)||dist.has(k))continue;dist.set(k,d0+1);q.push([nx,ny,nz])}}
   return end?originalCardinalBacktrack(start,end,dist):null;
 }"""

OLD_REACH_PATH="""function pathFromOriginalReachMap(reach,x,y,z,candidate=null){
   const chosen=candidate||originalReachCandidate(reach,x,y,z);
   if(!chosen)return null;
   const out=[];let cur=chosen.end;
   while(cur!==reach.start){const [px,py,pz]=cur.split(',').map(Number);
     out.push({x:px,y:py,z:pz,dir:reach.how.get(cur)});cur=reach.prev.get(cur);if(cur==null)return null}
   out.reverse();return out;
 }"""
NEW_REACH_PATH="""function pathFromOriginalReachMap(reach,x,y,z,candidate=null){
   const chosen=candidate||originalReachCandidate(reach,x,y,z);
   if(!chosen)return null;
   return originalCardinalBacktrack(reach.start,chosen.end,reach.dist);
 }"""

def upgrade(raw,full=False):
    exp=BASE['full' if full else 'lite']; act=blob(raw)
    if act!=exp: raise ValueError(f'Unknown V188 blob expected {exp} got {act}')
    t=raw.decode('utf8')
    t=once(t,OLD_AI_ROUTE,NEW_AI_ROUTE)
    t=once(t,OLD_REACH_PATH,NEW_REACH_PATH)
    t=once(t,OLD_ROUTE,NEW_ROUTE)
    t=once(t,'Original Restoration V188','Original Restoration V189',3)
    t=once(t,'ORIGINAL RULE RESTORATION · V188','ORIGINAL RULE RESTORATION · V189')
    t=once(t,'モナークモナーク · v188','モナークモナーク · v189')
    return t.encode()

TARGET={
 'lite':'6acb643ee40954a53f2e71c86caea10969e986f8',
 'full':'e778ce5baa7f39f7dcb7a229961089e9c1ea2632',
}

def main():
    if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
        src,dst=map(Path,sys.argv[2:]); out=upgrade(src.read_bytes(),True); dst.write_bytes(out); print('V189 full Git blob:',blob(out))
    elif len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]); out=upgrade(src.read_bytes(),False); dst.write_bytes(out); print('V189 lite Git blob:',blob(out))
    elif len(sys.argv)==1:
        index=Path('index.html'); archive=Path('monarch_v189_lite.html'); raw=index.read_bytes(); got=blob(raw)
        if got==BASE['lite']:
            out=upgrade(raw); index.write_bytes(out); archive.write_bytes(out)
        elif got==TARGET['lite'] and b'Original Restoration V189 LITE' in raw and b'function originalCardinalBacktrack(' in raw:
            if archive.exists() and archive.read_bytes()!=raw: raise ValueError('Refuse mismatched V189 archive')
            archive.write_bytes(raw)
        else:
            raise ValueError(f'Unknown index version; refusing overwrite: {got}')
        assert index.read_bytes()==archive.read_bytes()
        assert blob(index.read_bytes())==TARGET['lite']
        print('PASS V189 index/archive blob',blob(index.read_bytes()))
    else:
        raise SystemExit('Usage: upgrade_v189.py [V188lite V189lite] | [--full V188full V189full]')

if __name__=='__main__': main()
