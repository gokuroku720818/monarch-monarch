#!/usr/bin/env python3
"""V188 -> V189: restore original same-column elevator route edges."""
from pathlib import Path
import hashlib,sys
BASE={'lite':'dd5e3442c36bf4b7cd14377b8990379dfed534f7','full':'5a9e6081f43b8a0a8a7b85e4e82fc498b50afbdb'}
HELPER=""" function originalVerticalRouteSteps(x,y,z){
   // lm_win.exe 0x442606..0x4427f6: elevator-family route reconstruction considers same-column z edges before horizontal 0/2/4/6.
   const t=tileAt(x,y,z),out=[];
   const add=(nz,dir)=>{if(nz<0||nz>=48)return;const nt=tileAt(x,y,nz);if(nt>=120&&nt<=123)out.push({x,y,z:nz,dir})};
   if(t===120)add(z+1,0xff);
   else if(t===121)add(z-1,0xfe);
   else if(t===122||t===123){add(z+1,0xff);add(z-1,0xfe)}
   return out;
 }
"""
AI_OLD="""for(const d of CARD){const [dx,dy]=DIRS[d],nx=x+dx,ny=y+dy,nz=resolveStep(nx,ny,z,gx,gy);if(nz==null)continue;if(commanderBlocksRoute(u,nx,ny,nz))continue;const k=vk(nx,ny,nz);if(blocked.has(k)||prev.has(k))continue;prev.set(k,vk(x,y,z));how.set(k,d);q.push([nx,ny,nz])}"""
AI_NEW="""for(const v of originalVerticalRouteSteps(x,y,z)){const k=vk(v.x,v.y,v.z);if(blocked.has(k)||commanderBlocksRoute(u,v.x,v.y,v.z)||prev.has(k))continue;prev.set(k,vk(x,y,z));how.set(k,v.dir);q.push([v.x,v.y,v.z])}
     for(const d of CARD){const [dx,dy]=DIRS[d],nx=x+dx,ny=y+dy,nz=resolveStep(nx,ny,z,gx,gy);if(nz==null)continue;if(commanderBlocksRoute(u,nx,ny,nz))continue;const k=vk(nx,ny,nz);if(blocked.has(k)||prev.has(k))continue;prev.set(k,vk(x,y,z));how.set(k,d);q.push([nx,ny,nz])}"""
ROUTE_OLD="""// lm_win.exe 0x4427fb: horizontal route reconstruction tests direction bytes 0,2,4,6 only.
     for(const d of CARD){const [dx,dy]=DIRS[d],nx=x+dx,ny=y+dy,nz=resolveStep(nx,ny,z,gx,gy);if(nz==null)continue;"""
ROUTE_NEW="""// lm_win.exe 0x442606..0x4427f6 tests elevator z-neighbours first; 0x4427fb then tests horizontal 0,2,4,6.
     for(const v of originalVerticalRouteSteps(x,y,z)){const k=vk(v.x,v.y,v.z);if(commanderBlocksRoute(u,v.x,v.y,v.z)||prev.has(k))continue;prev.set(k,vk(x,y,z));how.set(k,v.dir);q.push([v.x,v.y,v.z])}
     for(const d of CARD){const [dx,dy]=DIRS[d],nx=x+dx,ny=y+dy,nz=resolveStep(nx,ny,z,gx,gy);if(nz==null)continue;"""
MOVE_OLD="const tx=p.x+.5,ty=p.y+.5,dx=tx-u.x,dy=ty-u.y,d=Math.hypot(dx,dy);u.dir=p.dir;if(d<.08)"
MOVE_NEW="const tx=p.x+.5,ty=p.y+.5,dx=tx-u.x,dy=ty-u.y,d=Math.hypot(dx,dy);if(p.dir>=0&&p.dir<8)u.dir=p.dir;if(d<.08)"
def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def once(s,a,b,n=1):
    if s.count(a)!=n: raise ValueError(f'Expected {n}, found {s.count(a)}: {a[:80]}')
    return s.replace(a,b,n)
def function_span(s,name):
    start=s.index('function '+name+'('); op=s.index('{',start); depth=0
    for i in range(op,len(s)):
        if s[i]=='{': depth+=1
        elif s[i]=='}':
            depth-=1
            if depth==0:return start,i+1
    raise ValueError('unterminated '+name)
def replace_in_function(s,name,a,b):
    lo,hi=function_span(s,name); f=s[lo:hi]; f=once(f,a,b); return s[:lo]+f+s[hi:]
def upgrade(raw,full=False):
    exp=BASE['full' if full else 'lite']; got=blob(raw)
    if got!=exp: raise ValueError(f'Unknown V188 Git blob; expected {exp}, found {got}')
    s=raw.decode('utf8')
    s=once(s,' function routeWithOriginalAiBlocks',HELPER+' function routeWithOriginalAiBlocks')
    s=replace_in_function(s,'routeWithOriginalAiBlocks',AI_OLD,AI_NEW)
    s=replace_in_function(s,'route',ROUTE_OLD,ROUTE_NEW)
    s=once(s,MOVE_OLD,MOVE_NEW)
    s=once(s,'Original Restoration V188','Original Restoration V189',3)
    s=once(s,'ORIGINAL RULE RESTORATION · V188','ORIGINAL RULE RESTORATION · V189')
    s=once(s,'モナークモナーク · v188','モナークモナーク · v189')
    return s.encode()
def main():
    if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
        src,dst=map(Path,sys.argv[2:]); out=upgrade(src.read_bytes(),True); dst.write_bytes(out); print('V189 full Git blob:',blob(out))
    elif len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]); out=upgrade(src.read_bytes()); dst.write_bytes(out); print('V189 lite Git blob:',blob(out))
    elif len(sys.argv)==1:
        index=Path('index.html'); archive=Path('monarch_v189_lite.html'); raw=index.read_bytes()
        if blob(raw)==BASE['lite']:
            out=upgrade(raw); index.write_bytes(out); archive.write_bytes(out)
        elif b'Original Restoration V189 LITE' in raw and HELPER.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw: raise ValueError('Refuse mismatched V189 archive')
            archive.write_bytes(raw)
        else: raise ValueError('Unknown index version; refusing overwrite')
        assert index.read_bytes()==archive.read_bytes(); print('PASS V189 index/archive blob',blob(index.read_bytes()))
    else: raise SystemExit('Usage: upgrade_v189.py [V188lite V189lite] | [--full V188full V189full]')
if __name__=='__main__': main()
