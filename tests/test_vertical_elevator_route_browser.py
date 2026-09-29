#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,re,sys
files=sys.argv[1:]
with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox'])
  for filename in files:
    html=Path(filename).read_text(encoding='utf8'); stripped=False
    if len(html)>10_000_000:
      html,n=re.subn(r'<script id="monarch-original-midi-playback">[\\s\\S]*?</script>','<script id="monarch-original-midi-playback"></script>',html,count=1);assert n==1;stripped=True
    page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html,wait_until='domcontentloaded',timeout=120000)
    result=page.evaluate("""() => {
      const T=__MONARCH_TEST__;loadStage(14);
      const u=T.makeTestSoldier(0,11,27,500,8);
      const p=T.route(u,11.5,27.5,16);
      return {path:p&&p.map(q=>({x:q.x,y:q.y,z:q.z,dir:q.dir})),tiles:Array.from({length:9},(_,i)=>T.tileAt(11,27,8+i)),runtimeErrors:window.__MONARCH_ERRORS__||[]};
    }""")
    result['pageErrors']=errors; result['browserHarnessMusicStripped']=stripped
    print(Path(filename).name,json.dumps(result,ensure_ascii=False),flush=True)
    assert result['tiles']==[120,123,123,123,123,123,122,122,121],result
    assert result['path'] is not None,result
    assert result['path'][0]['x']==11 and result['path'][0]['y']==27 and result['path'][0]['z']==9 and result['path'][0]['dir']==255,result
    assert result['path'][-1]['x']==11 and result['path'][-1]['y']==27 and result['path'][-1]['z']==16,result
    assert not result['runtimeErrors'] and not errors,result
    page.close()
  browser.close()
print('PASS V189 Chromium native M_014 vertical elevator route')
