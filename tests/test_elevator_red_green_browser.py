#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,re,sys,hashlib
if len(sys.argv)!=3: raise SystemExit('usage: V189 V190')
base,new=sys.argv[1:]
def git_blob(path):
    b=Path(path).read_bytes(); return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
assert git_blob(base)=='6acb643ee40954a53f2e71c86caea10969e986f8',f'RED must use exact V189 blob: {git_blob(base)}'
assert git_blob(new)=='101c44bbd5ca45ea805bfb344c9aae03adba5401',f'GREEN must use exact V190 blob: {git_blob(new)}'
def prep(path):
    html=Path(path).read_text(encoding='utf8')
    if len(html)>10_000_000:
        html,n=re.subn(r'<script id="monarch-original-midi-playback">[\s\S]*?</script>','<script id="monarch-original-midi-playback"></script>',html,count=1);assert n==1
    return html
with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox'])
  page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(prep(base),wait_until='domcontentloaded',timeout=120000)
  red=page.evaluate('''() => {const T=__MONARCH_TEST__;loadStage(14);const u={x:12.5,y:27.5,z:8,f:0,strength:100,alive:true,type:'soldier'};const p=T.route(u,10.5,27.5,16);return {hasApi:typeof T.tickOriginalElevators==='function',path:p&&p.map(q=>[q.x,q.y,q.z,q.dir]),err:__MONARCH_ERRORS__||[]};}''')
  assert not red['hasApi'] and red['path'] is None and not red['err'] and not errors,red;page.close()
  page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(prep(new),wait_until='domcontentloaded',timeout=120000)
  green=page.evaluate('''() => {const T=__MONARCH_TEST__;loadStage(14);const probe={x:12.5,y:27.5,z:8,f:0,strength:100,alive:true,type:'soldier'};const path=T.route(probe,10.5,27.5,16);const reach=T.buildOriginalReachMap(probe,40,new Set());const before={e:T.getElevators()[0],z8:[T.tileAt(11,27,8),T.effectiveElevatorTileAt(11,27,8)]};T.tickOriginalElevators();const after={e:T.getElevators()[0],z8:[T.tileAt(11,27,8),T.effectiveElevatorTileAt(11,27,8)],z9:[T.tileAt(11,27,9),T.effectiveElevatorTileAt(11,27,9)]};loadStage(14);const u=T.makeTestSoldier(0,12,27,100,8),rp=T.route(u,10.5,27.5,16);u.path=rp;u.pathPos=0;u.target={x:10.5,y:27.5,z:16};u.actionCode=0;u.manualOrder='standby';let rode=false,n=0;for(;n<250;n++){update(1);if(u.elevatorRide)rode=true;if(!u.path&&Math.floor(u.x)===10&&Math.floor(u.y)===27&&Math.round(u.z)===16)break}return {path:path&&path.map(q=>[q.x,q.y,q.z,q.dir]),reach:reach.dist.get('10,27,16')??null,before,after,rider:{rode,n:n+1,x:u.x,y:u.y,z:u.z,path:!!u.path,alive:u.alive,actionCode:u.actionCode},err:__MONARCH_ERRORS__||[]};}''')
  expected=[[11,27,8,0]]+[[11,27,z,0xfe] for z in range(9,17)]+[[10,27,16,0]]
  assert green['path']==expected,green
  assert green['reach']==10 and green['before']['z8']==[124,120],green
  assert green['after']['z8']==[120,120] and green['after']['z9']==[124,123],green
  r=green['rider'];assert r['rode'] and r['alive'] and not r['path'] and int(r['x'])==10 and int(r['y'])==27 and round(r['z'])==16 and r['actionCode']==0,green
  assert not green['err'] and not errors,(green,errors);page.close();browser.close()
print('PASS V190 RED(V189)/GREEN elevator route + moving platform + rider')
