#!/usr/bin/env python3
"""Bounded 75-stage browser stability/invariant smoke for the shipped LITE build."""
import json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

filename=sys.argv[1] if len(sys.argv)>1 else 'monarch_v184_lite.html'
html=Path(filename).read_text()
if len(html)>10_000_000:
    html,n=re.subn(r'<script id="monarch-original-midi-playback">[\s\S]*?</script>','<script id="monarch-original-midi-playback"></script>',html,count=1)
    assert n==1
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1100,'height':800}); page_errors=[]
    page.on('pageerror',lambda e:page_errors.append(str(e)))
    page.set_content(html,wait_until='domcontentloaded',timeout=120000)
    result=page.evaluate('''() => {
      const failures=[]; const T=window.__MONARCH_TEST__;
      const finite=n=>Number.isFinite(n);
      for(let i=0;i<STAGES.length;i++){
        loadStage(i); const before=ticks;
        for(let k=0;k<10&&!ended;k++)update(1);
        const resources=T.getResources();
        if(resources.some(v=>!Number.isFinite(v)||v<0))failures.push({i,id:STAGES[i].id,kind:'resources',resources});
        for(let s=0;s<units.length;s++){
          const u=units[s]; if(!u||(!u.alive&&!u.dying))continue;
          if(!finite(u.x)||!finite(u.y)||!finite(u.z)||u.x<0||u.x>=32||u.y<0||u.y>=32||u.z<0||u.z>=48)
             failures.push({i,id:STAGES[i].id,kind:'unit-bounds',slot:s,x:u.x,y:u.y,z:u.z});
        }
        for(const s of selected){const u=units[s];if(!u||!u.alive||u.f!==0)failures.push({i,id:STAGES[i].id,kind:'stale-selection',slot:s})}
        if(!paused&&!ended&&ticks<=before)failures.push({i,id:STAGES[i].id,kind:'non-advancing',before,after:ticks});
      }
      return {stages:STAGES.length,failures,runtimeErrors:window.__MONARCH_ERRORS__||[]};
    }''')
    result['pageErrors']=page_errors
    print(json.dumps(result,ensure_ascii=False))
    assert result['stages']==75,result
    assert not result['failures'] and not result['runtimeErrors'] and not page_errors,result
    browser.close()
