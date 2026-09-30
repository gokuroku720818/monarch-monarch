from pathlib import Path
from playwright.sync_api import sync_playwright
import re,sys,json

if len(sys.argv)!=3:
    raise SystemExit('usage: V201 V202')
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
          target.type='king';target.actionCode=1;target.state=1;target.unitWord=((target.unitWord||1)|0x0800);
          T.setCastleHP(0,400);
          const planned=T.planOriginalNeutralSpecial(actor);
          return {
            planned,
            action:actor.actionCode,
            targetSlot:actor.actionTarget?.slot??null,
            nativeTargetSlot:target.slot,
            castleHP:T.getCastleHP(0),
            err:__MONARCH_ERRORS__||[]
          };
        }''')
        page.close()
        assert not errs and not r['err'],(errs,r)
        return r
    red=run(base);green=run(new);b.close()

print('RED',json.dumps(red))
print('GREEN',json.dumps(green))
assert red['castleHP']==400 and red['targetSlot']!=red['nativeTargetSlot'],red
assert green['planned'] and green['action']==3 and green['targetSlot']==green['nativeTargetSlot'],green
print('PASS V202 neutral hunt does not suppress reachable commander while castle HP remains')
