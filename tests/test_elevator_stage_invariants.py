#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright
import re,sys
path=Path(sys.argv[1] if len(sys.argv)>1 else 'index.html');html=path.read_text()
if len(html)>10_000_000: html=re.sub(r'<script id="monarch-original-midi-playback">[\s\S]*?</script>','<script id="monarch-original-midi-playback"></script>',html,count=1)
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox']);page=b.new_page();errs=[];page.on('pageerror',lambda e:errs.append(str(e)));page.set_content(html,wait_until='domcontentloaded',timeout=120000)
 out=page.evaluate('''() => {const T=__MONARCH_TEST__,rows=[];for(let i=0;i<STAGES.length;i++){loadStage(i);const n=T.getElevators().length;for(let j=0;j<10;j++)update(1);let vis=0;for(let z=0;z<48;z++)for(let y=0;y<32;y++)for(let x=0;x<32;x++)if(T.tileAt(x,y,z)===124)vis++;rows.push([STAGES[i].id,n,vis]);if((__MONARCH_ERRORS__||[]).length)break}return {rows,err:__MONARCH_ERRORS__||[]};}''')
 bad=[r for r in out['rows'] if r[1]>4 or r[1]!=r[2]];assert len(out['rows'])==75 and not bad and not out['err'] and not errs,(bad,out['err'],errs);b.close()
print('PASS V190 75-stage x10-pass elevator invariant; max four native lift records; visible124==records')
