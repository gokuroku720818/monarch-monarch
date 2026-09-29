#!/usr/bin/env python3
"""V190: native elevator vertical path markers and reach-map regression."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import hashlib,json,re,sys
files=sys.argv[1:] or ['monarch_v190_lite.html']
EXPECTED={'10601a1deb58462ab96f222dd7e152ee51dbaca2','348c5186362c94ebe4bef923c15a27be5e4300dc'}
def gitblob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox'])
    for filename in files:
        raw=Path(filename).read_bytes(); assert gitblob(raw) in EXPECTED,(filename,gitblob(raw))
        html=raw.decode('utf8')
        if len(html)>10_000_000:
            html,n=re.subn(r'<script id="monarch-original-midi-playback">[\s\S]*?</script>','<script id="monarch-original-midi-playback"></script>',html,count=1);assert n==1
        page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(html,wait_until='domcontentloaded',timeout=120000)
        result=page.evaluate('''() => {
          const T=__MONARCH_TEST__;loadStage(0);
          for(let y=25;y<=29;y++)for(let x=24;x<=30;x++)for(let z=0;z<=10;z++)T.setWorldTile(x,y,z,0,0);
          T.setWorldTile(26,27,3,1,0);T.setWorldTile(27,27,3,120,0);
          T.setWorldTile(27,27,4,122,0);T.setWorldTile(27,27,5,123,0);
          T.setWorldTile(27,27,6,122,0);T.setWorldTile(27,27,7,123,0);
          T.setWorldTile(27,27,8,121,0);T.setWorldTile(28,27,8,1,0);
          const u=T.makeTestSoldier(0,26,27,100,3),path=T.route(u,28.5,27.5,8);
          const reach=T.buildOriginalReachMap(u,20,new Set());
          return {path,distance:reach.dist.get('28,27,8')??null,hasUpper:reach.prev.has('28,27,8'),runtimeErrors:window.__MONARCH_ERRORS__||[]};
        }''')
        print(Path(filename).name,json.dumps(result,ensure_ascii=False),flush=True)
        assert not errors and not result['runtimeErrors'],(errors,result)
        assert result['distance']==7 and result['hasUpper'],result
        assert result['path'] and result['path'][0]=={'x':27,'y':27,'z':3,'dir':4},result['path']
        assert [q['dir'] for q in result['path']].count(0xfe)==5,result['path']
        assert result['path'][-1]=={'x':28,'y':27,'z':8,'dir':4},result['path']
        page.close()
    browser.close()
print('PASS V190 native elevator pathfinding')
