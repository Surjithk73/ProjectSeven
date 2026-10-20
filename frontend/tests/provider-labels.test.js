import test from 'node:test';
import assert from 'node:assert/strict';
import { projectDisplayName, repositoryGroups, contractDisplayTitle } from '../src/workspace.js';

test('a multi-provider client is one repository and two clearly labelled providers',()=>{
  const items=[{name:'cinemaflow',kind:'repository'},{name:'cinema-theatre',kind:'provider'},{name:'cinema-payment',kind:'provider'}];
  const groups=repositoryGroups(items);
  assert.deepEqual(groups.repositories.map(x=>x.name),['cinemaflow']);
  assert.deepEqual(groups.providers.map(x=>projectDisplayName(x.name)),['IMAX','GPay']);
  assert.equal(contractDisplayTitle('Grand Cinema theatre provider'),'IMAX theatre provider');
  assert.equal(contractDisplayTitle('CinemaPay simulated payment provider'),'GPay payment provider');
  assert.equal(contractDisplayTitle('Other API'),'Other API');
});
