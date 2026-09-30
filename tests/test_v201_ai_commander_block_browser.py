from pathlib import Path
from playwright.sync_api import sync_playwright
import re,sys,json
if len(sys.argv)!=3: raise SystemExit('usage: V200 V201')
base,new=map(Path,sys.argv[1:])
def prep(p):
 h=p.read_text()
 if len(h)>10_000_000:
  h,n=re.subn(r'<script id="monarch-original-midi-playback">[\s\S]*?</script>','<script id="monarch-original-midi-playback"></script>',h,count=1);assert n==1
 return h
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox'])
 def run(p):
  page=b.new_page();errs=[];page.on('pageerror',lambda e:errs.append(str(e)));page.set_content(prep(p),wait_until='domcontentloaded',timeout=120000)
  r=page.evaluate('''() => {const T=__MONARCH_TEST__;loadStage(0);const z=T.getSurface(19,11).z;
    const actor=T.makeTestSoldier(1,19,11,100,z), target=T.makeTestSoldier(1,20,11,200,z);
    actor.actionCode=1;actor.state=1;actor.unitWord=(actor.unitWord&0xff00)|1;
    target.type='king';target.actionCode=1;target.state=1;target.unitWord=((target.unitWord&0xff00)|1)&~0x0800;
    const found=T.findFriendlyMergeTarget(actor,3);
    return {foundSlot:found?.unit?.slot??null,targetSlot:target.slot,err:__MONARCH_ERRORS__||[]};}''')
  page.close();assert not errs and not r['err'],(errs,r);return r
 red=run(base);green=run(new);b.close()
print('RED',json.dumps(red));print('GREEN',json.dumps(green))
assert red['foundSlot']!=red['targetSlot'],red
assert green['foundSlot']==green['targetSlot'],green
print('PASS V201 AI commander/block classification uses native 0x0800 bit only')
