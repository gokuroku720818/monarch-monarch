from pathlib import Path
from playwright.sync_api import sync_playwright
import re,sys,json

if len(sys.argv)!=3: raise SystemExit('usage: V206 V207')
base,new=map(Path,sys.argv[1:])

def prep(p):
    h=p.read_text()
    if len(h)>10_000_000:
        h,n=re.subn(r'<script id="monarch-original-midi-playback">[\s\S]*?</script>','<script id="monarch-original-midi-playback"></script>',h,count=1)
        assert n==1
    return h

with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox'])
    def run(p):
        page=b.new_page();errs=[]
        page.on('pageerror',lambda e:errs.append(str(e)))
        page.set_content(prep(p),wait_until='domcontentloaded',timeout=120000)
        r=page.evaluate('''() => {
          const T=__MONARCH_TEST__;
          const scenario=(kind)=>{
            loadStage(0);
            for(const v of units){if(v){v.alive=false;v.dying=false;v.originalFrameFlags=0;}}
            const z=T.getSurface(19,11).z;
            const actor=T.makeTestSoldier(1,19,11,100,z);
            const target=T.makeTestSoldier(kind==='friendly'?1:2,20,11,100,z);
            const action=kind==='friendly'?2:3;
            actor.actionCode=action;actor.state=action;actor.unitWord=((actor.unitWord||0)&0xff00)|action;
            actor.actionTarget={slot:target.slot};actor.target={x:target.x,y:target.y,z:target.z,slot:target.slot};
            actor.trackX=Math.floor(target.x);actor.trackY=Math.floor(target.y);actor.trackZ=Math.round(target.z);
            actor.path=[{x:20,y:11,z,dir:4}];actor.pathPos=0;actor.manualOrder=null;
            if(kind==='friendly'){
              target.alive=false;target.dying=true;target.originalFrameFlags=(target.originalFrameFlags||0)|0x5;
            }else{
              target.type='king';target.unitWord=(target.unitWord||0)|0x0800;T.setCastleHP(2,400);
            }
            const route=T.trackedUnitRoute(actor,target,action);
            update(1);
            return {
              action:actor.actionCode,targetSlot:actor.actionTarget?.slot??null,nativeSlot:target.slot,
              route:route!==null,targetAlive:target.alive,targetDying:target.dying,
              castle:kind==='enemyKing'?T.getCastleHP(2):0
            };
          };
          return {friendly:scenario('friendly'),enemyKing:scenario('enemyKing'),err:__MONARCH_ERRORS__||[]};
        }''')
        page.close();assert not errs and not r['err'],(errs,r);return r
    red=run(base);green=run(new);b.close()

print('RED',json.dumps(red))
print('GREEN',json.dumps(green))
assert red['friendly']['targetDying'] and not red['friendly']['targetAlive'],red
assert red['friendly']['action']!=2 or red['friendly']['targetSlot']!=red['friendly']['nativeSlot'] or not red['friendly']['route'],red
assert green['friendly']['action']==2 and green['friendly']['targetSlot']==green['friendly']['nativeSlot'] and green['friendly']['route'],green
assert red['enemyKing']['castle']==400 and (red['enemyKing']['action']!=3 or red['enemyKing']['targetSlot']!=red['enemyKing']['nativeSlot'] or not red['enemyKing']['route']),red
assert green['enemyKing']['castle']==400 and green['enemyKing']['action']==3 and green['enemyKing']['targetSlot']==green['enemyKing']['nativeSlot'] and green['enemyKing']['route'],green
print('PASS V207 ongoing action 2/3 follows stored slot without browser live/faction/commander revalidation')
