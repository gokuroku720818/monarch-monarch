#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,re,sys

files=sys.argv[1:]
assert files,'usage: test_elevator_runtime_browser.py HTML...'
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
        result=page.evaluate('''() => {
          const T=__MONARCH_TEST__;
          loadStage(14);
          const probe={x:12.5,y:27.5,z:8,f:0,strength:100,alive:true,type:'soldier'};
          const path=T.route(probe,10.5,27.5,16);
          const reach=T.buildOriginalReachMap(probe,40,new Set());
          const before={lift:T.getElevators()[0],z8:[T.tileAt(11,27,8),T.effectiveElevatorTileAt(11,27,8)]};
          T.tickOriginalElevators();
          const after={lift:T.getElevators()[0],z8:[T.tileAt(11,27,8),T.effectiveElevatorTileAt(11,27,8)],z9:[T.tileAt(11,27,9),T.effectiveElevatorTileAt(11,27,9)]};
          loadStage(14);
          const u=T.makeTestSoldier(0,12,27,100,8),rp=T.route(u,10.5,27.5,16);
          u.path=rp;u.pathPos=0;u.target={x:10.5,y:27.5,z:16};u.actionCode=0;u.manualOrder='standby';
          let rode=false,n=0;
          for(;n<250;n++){update(1);if(u.elevatorRide)rode=true;if(!u.path&&Math.floor(u.x)===10&&Math.floor(u.y)===27&&Math.round(u.z)===16)break}
          return {path:path&&path.map(q=>[q.x,q.y,q.z,q.dir]),reach:reach.dist.get('10,27,16')??null,before,after,rider:{rode,n:n+1,x:u.x,y:u.y,z:u.z,path:!!u.path,alive:u.alive,actionCode:u.actionCode},err:__MONARCH_ERRORS__||[]};
        }''')
        expected=[[11,27,8,0],...Array.from({length:8},(_,i)=>[11,27,9+i,0xfe]),[10,27,16,0]]
        assert result['path']==expected,result
        assert result['reach']==10,result
        assert result['before']['z8']==[124,120],result
        assert result['after']['z8']==[120,120] and result['after']['z9']==[124,123],result
        r=result['rider']
        assert r['rode'] and r['alive'] and not r['path'] and int(r['x'])==10 and int(r['y'])==27 and round(r['z'])==16 and r['actionCode']==0,result
        assert not result['err'] and not errors,(result,errors)
        print(Path(filename).name,json.dumps(result,ensure_ascii=False),flush=True)
        page.close()
    browser.close()
print('PASS current Chromium original elevator path + moving platform + rider')
