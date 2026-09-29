#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, re, sys

files=sys.argv[1:] or ['monarch_v187_lite.html']
with sync_playwright() as p:
    browser=p.chromium.launch(
        headless=True,
        executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,
        args=['--no-sandbox']
    )
    for filename in files:
        html=Path(filename).read_text(encoding='utf8')
        stripped=False
        if len(html)>10_000_000:
            html,n=re.subn(
                r'<script id="monarch-original-midi-playback">[\s\S]*?</script>',
                '<script id="monarch-original-midi-playback"></script>',
                html,count=1
            )
            assert n==1
            stripped=True
        page=browser.new_page()
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(html,wait_until='domcontentloaded',timeout=120000)
        result=page.evaluate("""() => {
          const T=__MONARCH_TEST__;
          loadStage(0);
          for(let y=8;y<=12;y++)for(let x=8;x<=12;x++){
            for(let z=3;z<12;z++)T.setWorldTile(x,y,z,0,0);
            T.setWorldTile(x,y,2,1,0);
          }
          T.setWorldTile(9,10,3,29,100);
          T.setWorldTile(11,10,3,30,100);
          const u=T.makeTestSoldier(0,10,10,100,2);
          const found=T.findRepeatWorkTarget(u,'destroyBase');
          return {
            found,
            own:T.tileAt(9,10,3),
            enemy:T.tileAt(11,10,3),
            runtimeErrors:window.__MONARCH_ERRORS__||[]
          };
        }""")
        result['pageErrors']=errors
        result['browserHarnessMusicStripped']=stripped
        print(Path(filename).name,json.dumps(result,ensure_ascii=False),flush=True)
        assert result['found'] is not None,result
        assert result['found']['action']==8,result
        assert result['found']['x']==11 and result['found']['y']==10,result
        assert result['own']==29 and result['enemy']==30,result
        assert not result['runtimeErrors'] and not errors,result
        page.close()
    browser.close()
print('PASS V187 browser: continue destroy-base skips own base and targets enemy base')
