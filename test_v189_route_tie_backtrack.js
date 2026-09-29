const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');

const htmlPath=process.argv[2]||'index.html';
const bytes=fs.readFileSync(htmlPath);
const gitBlob=crypto.createHash('sha1')
  .update(Buffer.from(`blob ${bytes.length}\0`,'utf8')).update(bytes).digest('hex');
assert.equal(gitBlob,'dd5e3442c36bf4b7cd14377b8990379dfed534f7','RED must run on exact V188 lite blob');
const html=bytes.toString('utf8');

function extractFunction(name){
  const start=html.indexOf(`function ${name}(`);
  assert.notEqual(start,-1,`missing function ${name}`);
  const open=html.indexOf('{',start);let depth=0;
  for(let i=open;i<html.length;i++){
    if(html[i]==='{')depth++;
    else if(html[i]==='}'&&--depth===0)return html.slice(start,i+1);
  }
  assert.fail(`unterminated function ${name}`);
}

// lm_win.exe 0x43ef84 builds the distance field from the source.
// lm_win.exe 0x4427fb..0x442898 reconstructs from the destination and probes
// direction bytes 0,2,4,6 (west,north,east,south), accepting only a STRICTLY
// lower distance. Therefore equal shortest routes are resolved at the target
// side, not by the source-side discovery predecessor used by V188.
const DIRS=[[-1,0],[-1,-1],[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1]];
const CARD=[0,2,4,6];
const blocked=new Set(['1,0,0']);
const vk=(x,y,z)=>`${x},${y},${z}`;
const resolveStep=(x,y,z)=>x>=0&&y>=0&&x<4&&y<4&&!blocked.has(vk(x,y,z))?z:null;
const commanderBlocksRoute=()=>false;
const route=new Function('DIRS','CARD','vk','resolveStep','commanderBlocksRoute',
  `${extractFunction('route')}; return route;`)(DIRS,CARD,vk,resolveStep,commanderBlocksRoute);

const u={x:.5,y:.5,z:0,f:0};
const actual=route(u,3.5,3.5,0).map(p=>[p.x,p.y,p.z]);
const originalExeExpected=[
  [0,1,0],[0,2,0],[0,3,0],[1,3,0],[2,3,0],[3,3,0]
];
assert.deepEqual(actual,originalExeExpected,
  'V188 source-side predecessor tie break differs from lm_win.exe target-side CARD backtrack');
console.log('PASS original target-side route tie break');
