"""Chromium regression: M_032 stacked fences must keep the exact Action 10 target z."""
import json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

files=sys.argv[1:] or ['monarch_v184_lite.html']
with sync_playwright() as playwright:
    browser=playwright.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for filename in files:
        page=browser.new_page(viewport={'width':1280,'height':900})
        errors=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        html=Path(filename).read_text()
        stripped_music=False
        if len(html)>10_000_000:
            html2,n=re.subn(r'<script id="monarch-original-midi-playback">[\s\S]*?</script>', '<script id="monarch-original-midi-playback"></script>', html, count=1)
            assert n==1,'full build music script not found for browser-test stripping'
            html=html2; stripped_music=True
        page.set_content(html,wait_until='domcontentloaded',timeout=120000)
        result=page.evaluate('''() => {
          const T=window.__MONARCH_TEST__,UI=window.__MONARCH_UI_TEST__,issues=[];
          const must=(condition,message)=>{if(!condition)issues.push(message)};
          loadStage(32);
          must(STAGES[32]?.id==='M_032','stage 32 is not M_032');
          must(T.tileAt(7,13,3)===41&&T.tileAt(7,13,4)===40,'M_032 low fence pair missing');
          must(T.tileAt(7,13,38)===41&&T.tileAt(7,13,39)===40,'M_032 high fence pair missing');
          const idx=UI.getOwnSoldierIndices()[0]; must(Number.isInteger(idx),'no player soldier');
          const u=units[idx];
          u.x=6.5;u.y=13.5;u.z=37;u.strength=Math.max(500,u.strength||0);u.target=null;u.path=null;u.pathPos=0;
          const highCap={x:7,y:13,z:39,v:40};
          const lowBefore=[T.tileAt(7,13,3),T.tileAt(7,13,4),T.getCellPower(7,13,3)];
          must(UI.issueSpecificWork(u,'destroyFence',highCap,'auto'),'high fence order rejected');
          must(u.actionCode===10&&u.actionTarget?.z===38,'high cap was not normalized to exact core z=38');
          T.setCellPower(7,13,38,0);
          let passes=0;
          while(passes++<20 && (T.tileAt(7,13,38)!==0||T.tileAt(7,13,39)!==0))update(1);
          must(T.tileAt(7,13,38)===0&&T.tileAt(7,13,39)===0,'high fence was not removed within 20 passes');
          update(1);
          must(u.actionCode!==10,'Action 10 remained active after exact target disappeared');
          must(!u.actionTarget,'Action 10 retained/retargeted a target after exact target disappeared');
          must(JSON.stringify([T.tileAt(7,13,3),T.tileAt(7,13,4),T.getCellPower(7,13,3)])===JSON.stringify(lowBefore),'low same-column fence changed');
          return {issues,stage:STAGES[32]?.id,low:[T.tileAt(7,13,3),T.tileAt(7,13,4)],high:[T.tileAt(7,13,38),T.tileAt(7,13,39)],actionCode:u.actionCode,target:u.actionTarget,errors:window.__MONARCH_ERRORS__||[]};
        }''')
        result['pageErrors']=errors
        result['browserHarnessMusicStripped']=stripped_music
        print(Path(filename).name,json.dumps(result,ensure_ascii=False),flush=True)
        assert not result['issues'] and not result['errors'] and not errors,result
        page.close()
    browser.close()
