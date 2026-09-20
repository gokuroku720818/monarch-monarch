// Regression gate: run the real V177 selection cleanup fragment shipped in HTML.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync(process.argv[2]||'index.html','utf8');
const start=html.indexOf('function refreshFactionElimination(dt=1){');
assert.ok(start>=0,'Original faction-defeat function not found');
const fragment=/let clearedKingSelection=false;selected\.forEach\(i=>\{if\(units\[i\]===k\)\{selected\.delete\(i\);clearedKingSelection=true\}\}\);if\(clearedKingSelection\)window\.__MONARCH_RECONCILE_SELECTION__\?\.\(true\)/;
const source=html.slice(start,start+4000).match(fragment)?.[0];
assert.ok(source,'Defeat branch must notify existing UI after deleting selected commander');
const run=new Function('selected','units','k','window',source);
const k={alive:false,type:'king'},units=[k,{alive:true,type:'soldier'}];
const selected=new Set([0,1]);let calls=0;
const window={__MONARCH_RECONCILE_SELECTION__:(force)=>{assert.equal(force,true);calls++}};
run(selected,units,k,window);
assert.deepEqual([...selected],[1],'Only defeated commander must be deselected');
assert.equal(calls,1,'Exactly one forced UI cleanup for selected commander');
run(selected,units,k,window);
assert.equal(calls,1,'Unselected commander must not close an unrelated troop command');
console.log('PASS: native commander defeat clears selected commander and obsolete command UI');
