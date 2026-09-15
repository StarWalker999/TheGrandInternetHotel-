import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import vm from 'node:vm';


const residents=JSON.parse(execFileSync('python',['-c','import json; from world import HotelWorld; print(json.dumps(HotelWorld().residents))'],{encoding:'utf8'}));
const portraits=new Set();
assert.equal(new Set(residents.map(r=>r.character)).size,41);
assert.equal(new Set(residents.map(r=>r.appearance.preset)).size,10);
for(const r of residents)portraits.add(createHash('sha256').update(readFileSync(`assets/garden-${r.character}.png`)).digest('hex'));
assert.equal(portraits.size,41,'Resident portraits must reflect individual wardrobe choices');

const ctx=vm.createContext({});vm.runInContext(readFileSync('simulation.js','utf8'),ctx);
const run=vm.runInContext('makePractice()',ctx);ctx.run=run;
const move=d=>{ctx.direction=d;vm.runInContext('practiceMove(run,direction)',ctx);};
move('up');assert.equal(run.blocked,1);assert.equal(run.steps,0);
// Visit the desk without the parcel: the task must not complete early.
for(let i=0;i<4;i++)move('down');assert.equal(run.done,false);
// Use the open lower corridor, collect the parcel, then return to reception.
for(let i=0;i<6;i++)move('right');for(let i=0;i<4;i++)move('up');assert.equal(run.parcel,true);assert.equal(run.done,false);
for(let i=0;i<4;i++)move('down');for(let i=0;i<6;i++)move('left');assert.equal(run.done,true);
const steps=run.steps;move('right');assert.equal(run.steps,steps);
assert.equal(vm.runInContext('makePractice().parcel',ctx),false);
console.log('41 Garden model portraits and 10 presets; parcel task collision, collection, delivery and completion checks passed.');
