from pathlib import Path
from playwright.sync_api import sync_playwright
import re,sys,json
if len(sys.argv)!=3: raise SystemExit('usage V196 V197')
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
          const one=(which)=>{loadStage(0);const z=T.getSurface(19,11).z;
            const a=T.makeTestSoldier(0,19,11,100,z), d=T.makeTestSoldier(0,20,11,200,z);
            if(which==='actorType'){a.type='king';a.unitWord=(a.unitWord||0)&~0x0800;}
            if(which==='targetType'){d.type='king';d.unitWord=(d.unitWord||0)&~0x0800;}
            if(which==='nativeBit'){d.type='soldier';d.unitWord=(d.unitWord||0)|0x0800;}
            const ret=T.exchange(a,d);
            return {ret,aAlive:a.alive,dAlive:d.alive,aStrength:a.strength,dStrength:d.strength};};
          return {actorType:one('actorType'),targetType:one('targetType'),nativeBit:one('nativeBit'),err:__MONARCH_ERRORS__||[]};}''')
        page.close();assert not errs and not r['err'],(errs,r);return r
    red=run(base);green=run(new);b.close()
print('RED',json.dumps(red));print('GREEN',json.dumps(green))
for k in ('actorType','targetType'):
    assert red[k]['ret']==1 and red[k]['aAlive'] and red[k]['dAlive'],red
    assert green[k]['ret'] in (0,3) and (not green[k]['aAlive'] or not green[k]['dAlive']),green
assert red['nativeBit']['ret']==1 and green['nativeBit']['ret']==1,(red,green)
print('PASS V197 friendly-merge commander gate uses native 0x0800 bit only')
