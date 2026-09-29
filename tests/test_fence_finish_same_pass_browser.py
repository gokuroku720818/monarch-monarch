#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,re,sys

files=sys.argv[1:] or ['monarch_v188_lite.html']
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox'])
    for filename in files:
        html=Path(filename).read_text(encoding='utf8')
        stripped=False
        if len(html)>10_000_000:
            html,n=re.subn(r'<script id="monarch-original-midi-playback">[\s\S]*?</script>','<script id="monarch-original-midi-playback"></script>',html,count=1)
            assert n==1
            stripped=True
        page=browser.new_page(); errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(html,wait_until='domcontentloaded',timeout=120000)
        result=page.evaluate("""() => {
          const T=__MONARCH_TEST__;
          loadStage(0);
          T.setWorldTile(27,27,3,41,0);
          T.setWorldTile(27,27,4,40,0);
          T.setCellPower(27,27,3,0);
          const u=T.makeTestSoldier(0,26,27,500,3);
          u.actionCode=10;u.actionTarget={x:27,y:27,z:3};u.target=null;u.path=null;u.pathPos=0;u.manualOrder='work';u.workMode='auto';u.workFamily='destroyFence';
          const passes=[];
          for(let i=0;i<4;i++){
            update(1);
            passes.push({pass:i+1,code:u.actionCode,target:u.actionTarget?{...u.actionTarget}:null,core:T.tileAt(27,27,3),cap:T.tileAt(27,27,4)});
            if(passes.at(-1).core===0)break;
          }
          return {passes,runtimeErrors:window.__MONARCH_ERRORS__||[]};
        }""")
        result['pageErrors']=errors;result['browserHarnessMusicStripped']=stripped
        print(Path(filename).name,json.dumps(result,ensure_ascii=False),flush=True)
        removed=next((q for q in result['passes'] if q['core']==0),None)
        assert removed is not None and removed['cap']==0,result
        assert removed['code']!=10 and removed['target'] is None,result
        assert not result['runtimeErrors'] and not errors,result
        page.close()
    browser.close()
print('PASS V188 browser: DF0 fence removal and Action 10 completion occur in the same update pass')
