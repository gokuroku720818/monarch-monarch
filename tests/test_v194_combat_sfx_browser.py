from pathlib import Path
from playwright.sync_api import sync_playwright
import re,sys,json
if len(sys.argv)!=3: raise SystemExit('usage V193 V194')
base,new=map(Path,sys.argv[1:])

def prep(p):
    h=p.read_text()
    if len(h)>10_000_000:
        h,n=re.subn(r'<script id="monarch-original-midi-playback">[\s\S]*?</script>','<script id="monarch-original-midi-playback"></script>',h,count=1); assert n==1
    shim='<script>window.__audioCalls=[];window.Audio=class{constructor(src){this.src=src;this.volume=0;window.__audioCalls.push(src)}play(){return Promise.resolve()}}</script>'
    return h.replace('<head>','<head>'+shim,1)

with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox'])
    def run(p):
        page=b.new_page(); errs=[]; page.on('pageerror',lambda e:errs.append(str(e)))
        page.set_content(prep(p),wait_until='domcontentloaded',timeout=120000)
        r=page.evaluate('''() => {const T=__MONARCH_TEST__;
          const sfxIds=[30,31,32,33,34];
          const decode=(src)=>{const payload=String(src).split('base64,')[1]||''; const id=sfxIds.find(i=>SOUND_DATA['LM'+String(i).padStart(4,'0')+'.WAV']===payload); return id==null?null:'LM'+String(id).padStart(4,'0')+'.WAV'};
          loadStage(0); let z=T.getSurface(19,11).z; window.__audioCalls.length=0;
          let a=T.makeTestSoldier(0,19,11,800,z), d=T.makeTestSoldier(1,20,11,10,z); T.exchange(a,d);
          const defenderDeath=window.__audioCalls.map(decode).filter(Boolean);
          loadStage(0); z=T.getSurface(19,11).z; window.__audioCalls.length=0;
          a=T.makeTestSoldier(0,19,11,10,z); d=T.makeTestSoldier(1,20,11,800,z); T.exchange(a,d);
          const actorDeath=window.__audioCalls.map(decode).filter(Boolean);
          return {defenderDeath,actorDeath,err:__MONARCH_ERRORS__||[]};}''')
        page.close(); assert not errs and not r['err'],(errs,r); return r
    red=run(base); green=run(new); b.close()

print('RED',json.dumps(red)); print('GREEN',json.dumps(green))
assert red['defenderDeath'][-1:] == ['LM0031.WAV'],red
assert green['defenderDeath'][-1:] == ['LM0030.WAV'],green
assert red['actorDeath'][-1:] == ['LM0030.WAV'],red
assert green['actorDeath'][-1:] == ['LM0031.WAV'],green
print('PASS V194 native killer-faction combat death SFX')
