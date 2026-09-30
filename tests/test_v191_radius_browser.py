#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright
import hashlib,sys,re

if len(sys.argv)!=3:
    raise SystemExit('usage: V190 V191')
base,new=map(Path,sys.argv[1:])

def blob(p):
    b=p.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

kind='full' if base.stat().st_size>10_000_000 else 'lite'
BASE={'lite':'101c44bbd5ca45ea805bfb344c9aae03adba5401','full':'2c97a97021f266d4f322bb71e1ac5c4ef2b767a6'}
TARGET={'lite':'8388cb9d5578c9f039d2050264ba3e00033c2f35','full':'3037c73761902aad41fde8d9c3555d6ba2b6bd9c'}
assert blob(base)==BASE[kind],(kind,blob(base))
assert blob(new)==TARGET[kind],(kind,blob(new))

def prep(p):
    h=p.read_text(encoding='utf8')
    if len(h)>10_000_000:
        h,n=re.subn(r'<script id="monarch-original-midi-playback">[\s\S]*?</script>','<script id="monarch-original-midi-playback"></script>',h,count=1)
        assert n==1
    return h

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox'])
    def run(p):
        page=browser.new_page()
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(prep(p),wait_until='domcontentloaded',timeout=120000)
        r=page.evaluate('''() => {
          const T=__MONARCH_TEST__;
          loadStage(0);
          const s=T.getSurface(19,11),u=T.makeTestSoldier(0,19,11,100,s.z);
          const reach=T.buildOriginalReachMap(u,3,new Set()),vals=[...reach.dist.values()];
          return {max:Math.max(...vals),n3:vals.filter(v=>v===3).length,n2:vals.filter(v=>v===2).length,err:__MONARCH_ERRORS__||[]};
        }''')
        page.close()
        assert not errors and not r['err'],(errors,r)
        return r
    red=run(base)
    green=run(new)
    browser.close()

assert red['max']==3 and red['n3']>0,red
assert green['max']==2 and green['n3']==0 and green['n2']>0,green
print(f'PASS V191 {kind} RED(V190 inclusive radius)/GREEN native strict radius cutoff',red,green)
