#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,re,sys

files=sys.argv[1:] or ['monarch_v189_lite.html']
expected=[[0,1,0,6],[0,2,0,6],[0,3,0,6],[1,3,0,4],[2,3,0,4],[3,3,0,4]]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox'])
    for filename in files:
        html=Path(filename).read_text(encoding='utf8'); stripped=False
        if len(html)>10_000_000:
            html,n=re.subn(r'<script id="monarch-original-midi-playback">[\s\S]*?</script>','<script id="monarch-original-midi-playback"></script>',html,count=1)
            assert n==1; stripped=True
        page=browser.new_page(); errors=[]; page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(html,wait_until='domcontentloaded',timeout=120000)
        result=page.evaluate('''() => {
          const T=__MONARCH_TEST__; loadStage(1);
          const sx=18,sy=25,z=1;
          const surface=[];
          for(let y=sy;y<sy+4;y++)for(let x=sx;x<sx+4;x++){
            const s=T.getSurface(x,y); surface.push([x-sx,y-sy,s.z,s.v,T.isOriginalPassableTile(s.v)]);
          }
          const u=T.makeTestSoldier(0,sx,sy,500,z);
          T.setWorldTile(sx+1,sy,z,41,0); T.setWorldTile(sx+1,sy,z+1,40,0);
          const path=T.route(u,sx+3.5,sy+3.5,z);
          return {surface,path:path&&path.map(q=>[q.x-sx,q.y-sy,q.z-z,q.dir]),runtimeErrors:window.__MONARCH_ERRORS__||[]};
        }''')
        result['pageErrors']=errors; result['browserHarnessMusicStripped']=stripped
        print(Path(filename).name,json.dumps(result,ensure_ascii=False),flush=True)
        assert all(q[2]==1 and q[4] for q in result['surface']),result
        assert result['path']==expected,result
        assert not result['runtimeErrors'] and not errors,result
        page.close()
    browser.close()
print('PASS V189 Chromium original target-side cardinal route backtrack')
