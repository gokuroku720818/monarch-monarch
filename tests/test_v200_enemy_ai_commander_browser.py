from pathlib import Path
from playwright.sync_api import sync_playwright
import re,sys,json
if len(sys.argv)!=3: raise SystemExit('usage: V199 V200')
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
  r=page.evaluate('''() => {const T=__MONARCH_TEST__;
    loadStage(0);let z=T.getSurface(19,11).z;
    const a=T.makeTestSoldier(1,19,11,100,z), k=T.makeTestSoldier(2,20,11,100,z);
    k.type='king';k.unitWord=(k.unitWord|0x0800);T.setCastleHP(2,400);a.aiScan=0;const planned=T.planOriginalIdle(a);
    const castle={planned,action:a.actionCode,targetSlot:a.actionTarget?.slot??null,kingSlot:k.slot};
    loadStage(0);z=T.getSurface(19,11).z;
    const a2=T.makeTestSoldier(1,19,11,100,z), fake=T.makeTestSoldier(2,20,11,100,z), native=T.makeTestSoldier(3,19,12,100,z);
    fake.type='king';fake.unitWord=(fake.unitWord&~0x0800);native.type='soldier';native.unitWord=(native.unitWord|0x0800);T.setCastleHP(2,0);T.setCastleHP(3,0);a2.aiScan=0;
    const planned2=T.planOriginalIdle(a2);
    const bit={planned:planned2,targetSlot:a2.actionTarget?.slot??null,fakeSlot:fake.slot,nativeSlot:native.slot};
    return {castle,bit,err:__MONARCH_ERRORS__||[]};}''')
  page.close();assert not errs and not r['err'],(errs,r);return r
 red=run(base);green=run(new);b.close()
print('RED',json.dumps(red));print('GREEN',json.dumps(green))
assert red['castle']['targetSlot']!=red['castle']['kingSlot'],red
assert green['castle']['planned'] and green['castle']['action']==3 and green['castle']['targetSlot']==green['castle']['kingSlot'],green
assert red['bit']['targetSlot']==red['bit']['fakeSlot'],red
assert green['bit']['targetSlot']==green['bit']['nativeSlot'],green
print('PASS V200 enemy CPU scan ignores castle HP and breaks only on native 0x0800 commander bit')
