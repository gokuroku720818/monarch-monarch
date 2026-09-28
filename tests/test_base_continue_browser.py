#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, re, sys

files=sys.argv[1:] or ['monarch_v185_lite.html']
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox'])
    for filename in files:
        html=Path(filename).read_text(encoding='utf8')
        stripped=False
        if len(html)>10_000_000:
            html,n=re.subn(r'<script id="monarch-original-midi-playback">[\s\S]*?</script>','<script id="monarch-original-midi-playback"></script>',html,count=1)
            assert n==1
            stripped=True
        page=browser.new_page()
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(html,wait_until='domcontentloaded',timeout=120000)
        result=page.evaluate("""() => {
          const T=__MONARCH_TEST__;
          loadStage(0);
          for(let y=25;y<=29;y++)for(let x=25;x<=29;x++){
            for(let z=3;z<12;z++)T.setWorldTile(x,y,z,0,0);
            T.setWorldTile(x,y,2,1,0);
          }
          T.setResource(0,1000);
          const u=T.makeTestSoldier(0,27,27,1,2);
          u.workMode='continue';u.workFamily='base';u.manualOrder='workContinue';u.actionCode=1;
          const found=T.findRepeatWorkTarget(u,'base');
          const assigned=T.assignNextManualWork(u,'base');
          return {found,assigned,strength:u.strength,actionCode:u.actionCode,target:u.actionTarget,manualOrder:u.manualOrder,resource:T.getResources()[0],runtimeErrors:window.__MONARCH_ERRORS__||[]};
        }""")
        result['pageErrors']=errors
        result['browserHarnessMusicStripped']=stripped
        print(Path(filename).name,json.dumps(result,ensure_ascii=False),flush=True)
        assert result['found'] is not None,result
        assert result['assigned'] is True,result
        assert result['actionCode']==4,result
        assert result['target'] is not None,result
        assert not result['runtimeErrors'] and not errors,result
        page.close()
    browser.close()
print('PASS V185 browser: strength-1 continue builder acquires one final base target')
