/** Regression executes the shipped command handlers + shipped simulation guard.
 * Run: node tests/test_command_pause.js index.html
 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync(process.argv[2]||'index.html','utf8');
const line=name=>{
  const match=html.match(new RegExp(`^ *function ${name}\\([^\\n]+$`,'m'));
  assert.ok(match,`missing shipped function ${name}`);
  return match[0];
};
const reconcile=html.match(/function reconcileSelection\(force=false\)\{[\s\S]*?\n  \}/);
assert.ok(reconcile,'missing shipped selection reconciliation');
const guard=html.match(/^\s*const _updateOriginalUI=update;let lastHudPaint=-1e9;update=function\(dt\)\{.*\};$/m);
assert.ok(guard,'missing shipped simulation guard');
const source=[line('setCommandPause'),line('showCommands'),line('showKingCommands'),line('backOneStep'),line('finishIssued'),reconcile[0],guard[0]].join('\n');
const ctx={
  commandPause:false,uiPhase:'unit',press:null,selected:new Set([0]),
  units:[{alive:true,f:0,type:'soldier',actionCode:1},{alive:true,f:0,type:'king',actionCode:1}],
  paused:false,ended:false,ticks:0,performance:{now:()=>0},
  follow:{classList:{contains:()=>false}},
  hideRangeBox(){},hideFollowup(){},hideCommands(keep){if(!keep)ctx.selected.clear()},
  selectedSoldiers(){return [...ctx.selected].map(idx=>({idx,u:ctx.units[idx]})).filter(q=>q.u.type==='soldier')},
  commandAvailability(){return {wait:true}},primaryKeys:['wait','cancel'],setVisibleCommand(){},
  placeCommandMenu(){},targetStatusText(){return ''},showHint(){},
  setUiPhase(phase){ctx.uiPhase=phase},
  updateOriginalHud(){},
  update(dt){if(!ctx.paused)ctx.ticks+=dt;}
};
vm.createContext(ctx);
vm.runInContext(source,ctx);
const api=ctx;
api.update(1);assert.equal(api.ticks,1,'unselected world advances');
api.showCommands({x:2,y:3,z:4});
assert.equal(api.commandPause,true,'command panel freezes world');
api.update(9);assert.equal(api.ticks,1,'pending action must not tick');
api.backOneStep();assert.equal(api.uiPhase,'destination');
assert.equal(api.commandPause,true,'return to destination keeps world frozen');
api.update(9);assert.equal(api.ticks,1);
api.backOneStep();assert.equal(api.uiPhase,'unit');assert.equal(api.commandPause,false);
api.update(1);assert.equal(api.ticks,2,'cancelling selection resumes');
api.selected.add(0);api.showCommands({x:2,y:3,z:4});
assert.equal(api.finishIssued({ok:false}),false);
assert.equal(api.commandPause,true,'failed order leaves selected unit frozen for retry');
assert.equal(api.uiPhase,'destination');
api.showCommands({x:2,y:3,z:4});
assert.equal(api.finishIssued({ok:true,count:1}),true);
assert.equal(api.commandPause,false,'successful order resumes');
api.selected.add(1);api.showKingCommands(1,{x:20,y:20});
assert.equal(api.commandPause,true,'king orders freeze');
api.update(9);assert.equal(api.ticks,2);
api.backOneStep();assert.equal(api.commandPause,false,'king cancel resumes');
api.paused=true;api.selected.add(0);api.showCommands({x:2,y:3,z:4});api.finishIssued({ok:true,count:1});
assert.equal(api.paused,true,'command completion may not override manual pause');
api.update(2);assert.equal(api.ticks,2,'manual pause still freezes');
api.paused=false;api.update(1);assert.equal(api.ticks,3,'manual resume works');
assert.match(html,/setCommandPause\(!!selected\.size\);setUiPhase\(selected\.size\?'destination':'unit'\);return selected\.size/,'programmatic unit selection follows same freeze rule');
console.log('PASS shipped command pause, cancel/retry, king, manual pause, simulation guard');
