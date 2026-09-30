from pathlib import Path
from playwright.sync_api import sync_playwright
import re,sys,json
if len(sys.argv)!=3: raise SystemExit('usage V195 V196')
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
          const one=(sameFaction)=>{loadStage(0);const z=T.getSurface(19,11).z;
            const a=T.makeTestSoldier(0,19,11,100,z), d=T.makeTestSoldier(sameFaction?0:1,20,11,0,z);
            d.alive=false; d.dying=true; d.originalFrameFlags=(d.originalFrameFlags||0)|0x4;
            const contact=T.stepCellContact(a,{x:20,y:11,z});
            const ret=T.exchange(a,contact);
            return {found:contact===d,ret,aStrength:a.strength,dFlags:d.originalFrameFlags||0,dDying:!!d.dying};};
          return {enemy:one(false),friendly:one(true),err:__MONARCH_ERRORS__||[]};}''')
        page.close();assert not errs and not r['err'],(errs,r);return r
    red=run(base);green=run(new);b.close()
print('RED',json.dumps(red));print('GREEN',json.dumps(green))
assert red['enemy']['found'] and red['enemy']['ret']==0,red
assert green['enemy']['found'] and green['enemy']['ret']==5 and green['enemy']['aStrength']==100,green
assert red['friendly']['found'] and red['friendly']['ret']==0,red
assert green['friendly']['found'] and green['friendly']['ret']==5 and green['friendly']['aStrength']==100,green
print('PASS V196 dying occupied slot remains contact-blocking')
