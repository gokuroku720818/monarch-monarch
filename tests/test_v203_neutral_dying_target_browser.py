from pathlib import Path
from playwright.sync_api import sync_playwright
import re,sys,json

if len(sys.argv)!=3:
    raise SystemExit('usage: V202 V203')
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
          loadStage(0);
          for(const v of units){if(v){v.alive=false;v.dying=false;v.originalFrameFlags=0;}}
          const z=T.getSurface(19,11).z;
          const actor=T.makeTestSoldier(4,19,11,100,z);
          const target=T.makeTestSoldier(0,20,11,100,z);
          actor.actionCode=1;actor.state=1;actor.unitWord=0x1001;actor.neutralCounter=1;
          target.type='soldier';target.actionCode=1;target.state=1;target.unitWord=(target.unitWord&~0x0800)|1;
          target.alive=false;target.dying=true;target.originalFrameFlags=(target.originalFrameFlags||0)|0x5;
          T.setCastleHP(0,0);
          const planned=T.planOriginalNeutralSpecial(actor);
          return {
            planned,
            action:actor.actionCode,
            targetSlot:actor.actionTarget?.slot??null,
            dyingSlot:target.slot,
            targetAlive:target.alive,
            targetDying:target.dying,
            flags:target.originalFrameFlags,
            err:__MONARCH_ERRORS__||[]
          };
        }''')
        page.close()
        assert not errs and not r['err'],(errs,r)
        return r
    red=run(base);green=run(new);b.close()

print('RED',json.dumps(red))
print('GREEN',json.dumps(green))
assert red['targetDying'] and not red['targetAlive'] and red['targetSlot']!=red['dyingSlot'],red
assert green['planned'] and green['action']==3 and green['targetSlot']==green['dyingSlot'],green
print('PASS V203 neutral hunt preserves native occupied dying-slot target eligibility')
