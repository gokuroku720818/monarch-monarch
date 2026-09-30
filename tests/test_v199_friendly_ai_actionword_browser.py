from pathlib import Path
from playwright.sync_api import sync_playwright
import re,sys,json
if len(sys.argv)!=3: raise SystemExit('usage: V198 V199')
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
    target.actionCode=1;target.state=1;target.unitWord=(target.unitWord&0xff00)|2;
    const skip=T.findFriendlyMergeTarget(actor,3);
    loadStage(0);const z2=T.getSurface(19,11).z;
    const actor2=T.makeTestSoldier(1,19,11,100,z2), near=T.makeTestSoldier(1,20,11,200,z2), rally=T.makeTestSoldier(1,19,12,200,z2);
    actor2.actionCode=1;actor2.state=1;actor2.unitWord=(actor2.unitWord&0xff00)|1;
    near.actionCode=1;near.state=1;near.unitWord=(near.unitWord&0xff00)|1;
    rally.actionCode=1;rally.state=1;rally.unitWord=(rally.unitWord&0xff00)|16;
    const pref=T.findFriendlyMergeTarget(actor2,3);
    return {skipSlot:skip?.unit?.slot??null,targetSlot:target.slot,prefSlot:pref?.unit?.slot??null,rallySlot:rally.slot,nearSlot:near.slot,err:__MONARCH_ERRORS__||[]};}''')
  page.close();assert not errs and not r['err'],(errs,r);return r
 red=run(base);green=run(new);b.close()
print('RED',json.dumps(red));print('GREEN',json.dumps(green))
assert red['skipSlot']==red['targetSlot'],red
assert green['skipSlot'] is None,green
assert red['prefSlot']==red['nearSlot'],red
assert green['prefSlot']==green['rallySlot'],green
print('PASS V199 native action-word low byte controls friendly AI action-2 exclusion and action-16 priority')
