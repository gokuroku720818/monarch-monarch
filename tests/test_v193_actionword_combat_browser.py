from pathlib import Path
from playwright.sync_api import sync_playwright
import re,sys,json
if len(sys.argv)!=3: raise SystemExit('usage V192 V193')
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
  r=page.evaluate('''() => {const T=__MONARCH_TEST__; loadStage(0); const z=T.getSurface(19,11).z;
    const a=T.makeTestSoldier(0,19,11,100,z), d=T.makeTestSoldier(1,20,11,100,z);
    a.state=0x11; a.unitWord=(a.unitWord&0xff00)|1; const r1=T.exchange(a,d);
    const staleState={ret:r1,a:a.strength,d:d.strength};
    loadStage(0); const z2=T.getSurface(19,11).z;
    const x=T.makeTestSoldier(0,19,11,100,z2), y=T.makeTestSoldier(1,20,11,100,z2);
    x.state=1; x.unitWord=(x.unitWord&0xff00)|0x11; const r2=T.exchange(x,y);
    const nativeWord={ret:r2,a:x.strength,d:y.strength}; return {staleState,nativeWord,err:__MONARCH_ERRORS__||[]};}''')
  page.close();assert not errs and not r['err'],(errs,r);return r
 red=run(base);green=run(new);b.close()
print('RED',json.dumps(red));print('GREEN',json.dumps(green))
assert red['staleState']['ret']==5 and red['staleState']['a']==100 and red['staleState']['d']==100,red
assert green['staleState']['ret']==4 and green['staleState']['a']<100 and green['staleState']['d']<100,green
assert red['nativeWord']['ret']!=5 and (red['nativeWord']['a']<100 or red['nativeWord']['d']<100),red
assert green['nativeWord']['ret']==5 and green['nativeWord']['a']==100 and green['nativeWord']['d']==100,green
print('PASS V193 native combat action-word low-byte gate')
