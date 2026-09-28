#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, re, sys

files=sys.argv[1:] or ['monarch_v186_lite.html']
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
          for(let y=24;y<=30;y++)for(let x=24;x<=30;x++){
            for(let z=3;z<12;z++)T.setWorldTile(x,y,z,0,0);
            T.setWorldTile(x,y,2,1,0);
          }
          T.setResource(0,99);
          const u=T.makeTestSoldier(0,27,27,50,2);
          u.workMode='continue';u.workFamily='base';u.manualOrder='workContinue';u.actionCode=1;
          const found=T.findRepeatWorkTarget(u,'base');
          const assigned=T.assignNextManualWork(u,'base');
          const first={...u.actionTarget};
          update(1);
          const waiting={actionCode:u.actionCode,target:u.actionTarget?{...u.actionTarget}:null,resource:T.getResources()[0],strength:u.strength,tile:T.tileAt(first.x,first.y,first.z+1)};
          T.setResource(0,100);
          update(1);
          const after={actionCode:u.actionCode,target:u.actionTarget?{...u.actionTarget}:null,resource:T.getResources()[0],strength:u.strength,builtTile:T.tileAt(first.x,first.y,first.z+1),alive:u.alive};
          return {found,assigned,first,waiting,after,runtimeErrors:window.__MONARCH_ERRORS__||[]};
        }""")
        result['pageErrors']=errors
        result['browserHarnessMusicStripped']=stripped
        print(Path(filename).name,json.dumps(result,ensure_ascii=False),flush=True)
        assert result['found'] is not None and result['assigned'] is True,result
        assert result['waiting']['actionCode']==4 and result['waiting']['resource']==99 and result['waiting']['strength']==50,result
        assert result['waiting']['tile']==0,result
        assert result['after']['resource']==0,result
        assert 29 <= result['after']['builtTile'] <= 32,result
        assert result['after']['strength']<50,result
        assert result['after']['alive'] is True,result
        assert not result['runtimeErrors'] and not errors,result
        page.close()
    browser.close()
print('PASS V186 browser: 99 resource waits on Action 4; 100 builds and continue flow resumes')
