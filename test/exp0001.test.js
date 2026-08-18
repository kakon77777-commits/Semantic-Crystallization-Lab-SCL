import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { expandLexeme } from '../src/expand.js';
import { evaluateInvariantRecall } from '../src/invariants.js';
import { measureText } from '../src/metrics.js';

const root = new URL('../experiments/EXP-0001/', import.meta.url);
const json = async (relative) => JSON.parse(await readFile(new URL(relative, root), 'utf8'));

test('qevra expands without source prose and recovers every declared invariant', async () => {
  const [lexicon, invariants, source] = await Promise.all([
    json('lexicon/lexicon.json'),
    json('semantic-ir/invariants.json'),
    readFile(new URL('source/source.zh.txt', root), 'utf8')
  ]);
  const atoms = expandLexeme('qevra', lexicon);
  const recovered = new Set();
  for (const atom of atoms) {
    for (const id of invariants.atomToInvariantIds[atom] ?? []) recovered.add(id);
  }
  const evaluation = evaluateInvariantRecall(invariants.expectedIds, [...recovered]);
  assert.equal(evaluation.recall, 1);
  assert.deepEqual(evaluation.missing, []);

  const lexiconText = JSON.stringify(lexicon);
  assert.equal(lexiconText.includes(source.trim()), false);
  assert.equal(lexiconText.includes(source.trim().slice(0, 40)), false);
});

test('checked-in levels shrink monotonically in surface code points', async () => {
  const levels = await json('chain/levels.json');
  const lengths = levels.levels.map((level) => measureText(level.text).codePoints);
  for (let i = 1; i < lengths.length; i += 1) {
    assert.ok(lengths[i] < lengths[i - 1], `${levels.levels[i].id} must be shorter than previous level: ${lengths.join(' > ')}`);
  }
});

test('composite lexemes are reusable in a novel code-oriented composition', async () => {
  const lexicon = await json('lexicon/lexicon.json');
  const narel = expandLexeme({ symbol: 'narel', args: ['codeA', 'codeB', 'sortMeaning', 'developer'] }, lexicon);
  const vesh = expandLexeme({ symbol: 'vesh', args: ['codeA', 'sortMeaning', 'computeBoundary'] }, lexicon);
  assert.deepEqual(narel, [
    'ISO(codeA,codeB,sortMeaning)',
    'PATH(codeA,sortMeaning,developer,path[codeA])',
    'PATH(codeB,sortMeaning,developer,path[codeB])',
    'DIFF(path[codeA],path[codeB])'
  ]);
  assert.deepEqual(vesh, [
    'MEAN(codeA,sortMeaning)',
    'BOUND(sortMeaning,computeBoundary)'
  ]);
});
