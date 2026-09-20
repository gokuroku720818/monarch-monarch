// Execute the production reconciliation function, not a rewritten mock.
// The HTML is read by CI from the generated GitHub release.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync(process.argv[2]||'index.html','utf8');
const begin=html.indexOf('  function reconcileSelection(');
const end=html.indexOf('  window.__MONARCH_RECONCILE_SELECTION__=',begin);
assert.ok(begin>=0&&end>begin,'Shipped selection reconciliation missing');
let phase='action',shown=true,pending={x:4},paused=false;
const selected=new Set(),units=[];
const context={selected,units,commandPause:false,window:{},
 hideCommands:()=>{shown=false;pending=null},
 setUiPhase:p=>{phase=p},
 setCommandPause:p=>{paused=p}
};
vm.createContext(context);
vm.runInContext(html.slice(begin,end),context);
context.reconcileSelection(true);
assert.equal(shown,false,'A recycled selected slot must close its old menu');
assert.equal(phase,'unit','No selected troops means unit-selection phase');
assert.equal(pending,null,'Old target must not be issued to a new troop');
assert.equal(paused,false,'Old command pause must be released');
assert.ok(html.includes('window.__MONARCH_RECONCILE_SELECTION__?.(true);'),
 'Recycled allocator must request forced UI cleanup after removing selection');
console.log('PASS: recycled selected slot forces obsolete command UI cleanup');
