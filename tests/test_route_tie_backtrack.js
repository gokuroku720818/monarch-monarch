const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');

const htmlPath=process.argv[2]||'index.html';
const bytes=fs.readFileSync(htmlPath);
const gitBlob=crypto.createHash('sha1')
  .update(Buffer.from(`blob ${bytes.length}\0`,'utf8')).update(bytes).digest('hex');
assert.equal(gitBlob,'6acb643ee40954a53f2e71c86caea10969e986f8','V189 regression must run on exact tested lite blob');
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

const DIRS=[[-1,0],[-1,-1],[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1]];
const CARD=[0,2,4,6];
const blocked=new Set(['1,0,0']);
const vk=(x,y,z)=>`${x},${y},${z}`;
const resolveStep=(x,y,z)=>x>=0&&y>=0&&x<4&&y<4&&!blocked.has(vk(x,y,z))?z:null;
const commanderBlocksRoute=()=>false;
const helper=extractFunction('originalCardinalBacktrack');
assert.match(extractFunction('routeWithOriginalAiBlocks'),/originalCardinalBacktrack\(start,end,dist\)/);
assert.match(extractFunction('pathFromOriginalReachMap'),/originalCardinalBacktrack\(reach\.start,chosen\.end,reach\.dist\)/);
const route=new Function('DIRS','CARD','vk','resolveStep','commanderBlocksRoute',
  `${helper}\n${extractFunction('route')}; return route;`)(DIRS,CARD,vk,resolveStep,commanderBlocksRoute);

const u={x:.5,y:.5,z:0,f:0};
const actual=route(u,3.5,3.5,0).map(p=>[p.x,p.y,p.z,p.dir]);
const originalExeExpected=[
  [0,1,0,6],[0,2,0,6],[0,3,0,6],[1,3,0,4],[2,3,0,4],[3,3,0,4]
];
assert.deepEqual(actual,originalExeExpected,
  'V189 must reproduce lm_win.exe target-side CARD backtrack including forward direction bytes');
console.log('PASS V189 original target-side route tie break');
