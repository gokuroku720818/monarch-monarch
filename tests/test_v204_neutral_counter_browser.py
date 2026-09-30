from pathlib import Path
from playwright.sync_api import sync_playwright
import sys,json
if len(sys.argv)!=3: raise SystemExit('usage: V203 V204')
base,new=map(Path,sys.argv[1:])
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,args=['--no-sandbox'])
    def run(p,action):
        page=b.new_page();errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
        page.set_content(p.read_text(),wait_until='domcontentloaded',timeout=120000)
        r=page.evaluate("""(action) => {
          const T=__MONARCH_TEST__;loadStage(0);
          for(const v of units){if(v){v.alive=false;v.dying=false;v.originalFrameFlags=0;}}
          const z=T.getSurface(19,11).z;
          const u=T.makeTestSoldier(4,19,11,100,z);
          u.actionCode=action;u.state=action;u.unitWord=0x1000|action;u.neutralCounter=7;
          u.path=[{x:20,y:11,z,dir:4}];u.pathPos=0;u.target={x:20.5,y:11.5};
          const planned=T.planOriginalNeutralSpecial(u);
          return {planned,counter:u.neutralCounter,action:u.actionCode,pathLen:u.path?.length||0,err:__MONARCH_ERRORS__||[]};
        }""",action)
        page.close(); assert not errs and not r['err'],(errs,r); return r
    red15=run(base,15);green15=run(new,15);red1=run(base,1);green1=run(new,1);b.close()
print('RED15',json.dumps(red15));print('GREEN15',json.dumps(green15));print('RED1',json.dumps(red1));print('GREEN1',json.dumps(green1))
assert red15['counter']==8 and red1['counter']==8,(red15,red1)
assert green15['counter']==7 and green1['counter']==7,(green15,green1)
assert green15['planned'] and green1['planned']
print('PASS V204 neutral counter stays unchanged while native movement step is active')
