import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';



const residents=JSON.parse(execFileSync('python',['-c','import json; from world import HotelWorld; print(json.dumps(HotelWorld().residents))'],{encoding:'utf8'}));
const portraits=new Set();
assert.equal(new Set(residents.map(r=>r.character)).size,41);
assert.equal(new Set(residents.map(r=>r.appearance.preset)).size,10);
for(const r of residents)portraits.add(createHash('sha256').update(readFileSync(`assets/garden-${r.character}.png`)).digest('hex'));
assert.equal(portraits.size,41,'Resident portraits must reflect individual wardrobe choices');

console.log('41 Garden model portraits and 10 presets passed.');
