from pathlib import Path
from playwright.sync_api import sync_playwright
import re,sys,json
if len(sys.argv)!=3: raise SystemExit('usage: V197 V198')
base,new=map(Path,sys.argv[1:])
def prep(p):
    h=p.read_text()
    if len(h)>10_000_000:
        h,n=re.subn(r'<script id="monarch-original-midi-playback">[\\s\\S]*?</script>','<script id="monarch-original-midi-playback"></script>',h,count=1);assert n==1
    return h
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox'])
    def run(p):
      page=b.new_page();errs=[];page.on('pageerror',lambda e:errs.append(str(e)));page.set_content(prep(p),wait_until='domcontentloaded',timeout=120000)
      r=page.evaluate('''() => {const T=__MONARCH_TEST__;loadStage(0);
        const a=T.makeTestSoldier(0,19,11,80,5), d=T.makeTestSoldier(1,20,11,100,4);
        const ret=T.exchange(a,d);
        return {ret,aStrength:a.strength,dStrength:d.strength,aAlive:a.alive,dAlive:d.alive,dFlags:d.originalFrameFlags||0,err:__MONARCH_ERRORS__||[]};}''')
      page.close();assert not errs and not r['err'],(errs,r);return r
    red=run(base);green=run(new);b.close()
print('RED',json.dumps(red)); print('GREEN',json.dumps(green))
# Native first strike: (80 + (5-4)*100)/80 = 2. Counter: (100 + (4-5)*100)/80 = 0.
assert red['aStrength']==79 and red['dStrength']==98 and red['ret']==4,red
assert green['aStrength']==80 and green['dStrength']==98 and green['ret']==4,green
print('PASS V198 exact-zero retaliation remains zero; first strike still minimum-one')
