"""V174: route touch drags through the same original-style mouse selection.

Gameplay simulation, original stage data, images and WAVs remain byte-identical.
"""
from pathlib import Path
import hashlib

ANCHOR = " window.addEventListener('blur',cancelAbandonedRange);"
ADAPTER = r'''
 // The native game uses a mouse marquee. Mobile browsers send touchmove rather
 // than mousemove during a drag, leaving the existing selection code uncalled.
 // Relay a single touch through the SAME original-style mouse handlers; do not
 // duplicate or alter troop selection, movement or command rules.
 game.style.touchAction='none';
 let marqueeTouchId=null;
 function relayMarqueeTouch(type,t){
   game.dispatchEvent(new MouseEvent(type,{
     bubbles:true,cancelable:true,clientX:t.clientX,clientY:t.clientY,
     button:0,buttons:type==='mouseup'?0:1
   }));
 }
 game.addEventListener('touchstart',e=>{
   if(e.touches.length!==1){
     if(marqueeTouchId!==null){marqueeTouchId=null;cancelAbandonedRange();e.preventDefault()}
     return;
   }
   if(marqueeTouchId!==null)return;
   const t=e.changedTouches[0];marqueeTouchId=t.identifier;
   relayMarqueeTouch('mousedown',t);
   // Suppress duplicate compatibility mouse events after the synthetic dispatch.
   e.preventDefault();
 },{passive:false});
 window.addEventListener('touchmove',e=>{
   if(marqueeTouchId===null)return;
   const t=Array.from(e.changedTouches).find(t=>t.identifier===marqueeTouchId);
   if(!t)return;
   relayMarqueeTouch('mousemove',t);e.preventDefault();
 },{passive:false});
 window.addEventListener('touchend',e=>{
   if(marqueeTouchId===null)return;
   const t=Array.from(e.changedTouches).find(t=>t.identifier===marqueeTouchId);
   if(!t)return;
   marqueeTouchId=null;
   const r=game.getBoundingClientRect();
   if(t.clientX<r.left||t.clientX>r.right||t.clientY<r.top||t.clientY>r.bottom)
     cancelAbandonedRange();
   else relayMarqueeTouch('mouseup',t);
   e.preventDefault();
 },{passive:false});
 window.addEventListener('touchcancel',e=>{
   if(marqueeTouchId===null)return;
   marqueeTouchId=null;cancelAbandonedRange();e.preventDefault();
 },{passive:false});
'''


def patch(src: str) -> str:
    assert src.count(ANCHOR)==1
    assert 'marqueeTouchId' not in src
    out=src.replace(ANCHOR,ANCHOR+ADAPTER,1)
    assert src.count('Original Restoration V173')==3
    out=out.replace('Original Restoration V173','Original Restoration V174')
    assert src.count('ORIGINAL RULE RESTORATION · V173')==1
    out=out.replace('ORIGINAL RULE RESTORATION · V173','ORIGINAL RULE RESTORATION · V174')
    assert src.count('モナークモナーク · v173')==1
    out=out.replace('モナークモナーク · v173','モナークモナーク · v174')
    return out


EXPECTED_BASE_BLOB = 'f0083859b63fe6f89f8daa3be021f8d548d4fb2b'


def main():
    source=Path('index.html')
    release=Path('monarch_v174_lite.html')
    raw=source.read_bytes()
    sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if sha==EXPECTED_BASE_BLOB:
        result=patch(raw.decode('utf-8')).encode('utf-8')
        source.write_bytes(result)
        release.write_bytes(result)
        print('V174 touch marquee patch applied to verified V173 Git blob')
    elif b'Original Restoration V174 LITE' in raw and b'marqueeTouchId' in raw:
        if release.exists():
            assert release.read_bytes()==raw,'Release and index diverged'
        else:release.write_bytes(raw)
        print('V174 already installed; no changes')
    else:
        raise RuntimeError(f'Unexpected game blob {sha}; refusing to change deployed game')
    assert source.read_bytes()==release.read_bytes()
    assert b'monarch-original-midi.js' not in source.read_bytes()
    assert source.read_bytes().count(b"addEventListener('touch")==4


if __name__=='__main__': main()
