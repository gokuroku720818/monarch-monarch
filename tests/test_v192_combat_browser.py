from pathlib import Path
from playwright.sync_api import sync_playwright
import re,sys,hashlib,json
if len(sys.argv)!=3: raise SystemExit('usage: V191 V192')
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
    loadStage(0);
    const z=T.getSurface(19,11).z;
    const a=T.makeTestSoldier(0,19,11,800,z), d=T.makeTestSoldier(1,20,11,10,z);
    const r1=T.exchange(a,d);
    const killDef={ret:r1,aStrength:a.strength,aAlive:a.alive,dStrength:d.strength,dAlive:d.alive,dDying:!!d.dying,dFlags:d.originalFrameFlags||0};
    loadStage(0);
    const z2=T.getSurface(19,11).z;
    const w=T.makeTestSoldier(0,19,11,10,z2), s=T.makeTestSoldier(1,20,11,800,z2);
    const r2=T.exchange(w,s);
    const killActor={ret:r2,aStrength:w.strength,aAlive:w.alive,aDying:!!w.dying,dStrength:s.strength,dAlive:s.alive};
    return {killDef,killActor,err:__MONARCH_ERRORS__||[]};}''')
  page.close();assert not errs and not r['err'],(errs,r);return r
 red=run(base);green=run(new);b.close()
print('RED',json.dumps(red)); print('GREEN',json.dumps(green))
assert red['killDef']['aStrength']==800 and red['killDef']['ret']==6,red
assert green['killDef']['aStrength']==799 and green['killDef']['ret']==4 and green['killDef']['dStrength']==0 and not green['killDef']['dAlive'],green
assert red['killActor']['aStrength']==0 and red['killActor']['ret']==4,red
assert green['killActor']['aStrength']==0 and green['killActor']['ret']==6 and not green['killActor']['aAlive'],green
print('PASS V192 RED/GREEN native simultaneous retaliation + actor-death return code')
