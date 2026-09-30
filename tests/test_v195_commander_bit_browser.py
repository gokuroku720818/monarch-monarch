from pathlib import Path
from playwright.sync_api import sync_playwright
import re,sys,json
if len(sys.argv)!=3: raise SystemExit('usage V194 V195')
base,new=map(Path,sys.argv[1:])
def prep(p):
    h=p.read_text()
    if len(h)>10_000_000:
        h,n=re.subn(r'<script id="monarch-original-midi-playback">[\s\S]*?</script>','<script id="monarch-original-midi-playback"></script>',h,count=1); assert n==1
    return h
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox'])
    def run(p):
        page=b.new_page(); errs=[]; page.on('pageerror',lambda e:errs.append(str(e))); page.set_content(prep(p),wait_until='domcontentloaded',timeout=120000)
        r=page.evaluate('''() => {const T=__MONARCH_TEST__; loadStage(0); const z=T.getSurface(19,11).z;
          const a=T.makeTestSoldier(0,19,11,800,z), d=T.makeTestSoldier(1,20,11,1000,z);
          d.type='king'; d.unitWord=(d.unitWord||0)&~0x0800; d.originalFrameFlags=(d.originalFrameFlags||0)|0x20;
          const r1=T.exchange(a,d); const staleType={ret:r1,a:a.strength,d:d.strength};
          loadStage(0); const z2=T.getSurface(19,11).z;
          const x=T.makeTestSoldier(0,19,11,800,z2), y=T.makeTestSoldier(1,20,11,1000,z2);
          y.type='soldier'; y.unitWord=(y.unitWord||0)|0x0800; y.originalFrameFlags=(y.originalFrameFlags||0)|0x20;
          const r2=T.exchange(x,y); const nativeBit={ret:r2,a:x.strength,d:y.strength};
          return {staleType,nativeBit,err:__MONARCH_ERRORS__||[]};}''')
        page.close(); assert not errs and not r['err'],(errs,r); return r
    red=run(base); green=run(new); b.close()
print('RED',json.dumps(red)); print('GREEN',json.dumps(green))
assert red['staleType']['d']==900,red
assert green['staleType']['d']==990,green
assert red['nativeBit']['d']==900 and green['nativeBit']['d']==900,(red,green)
print('PASS V195 native commander-bit first-strike override')
