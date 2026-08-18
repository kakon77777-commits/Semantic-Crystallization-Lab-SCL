import test from 'node:test';
import assert from 'node:assert/strict';
import { runExp0001 } from '../scripts/run-exp0001.js';

test('runner returns a reproducible result with full declared invariant recall', async () => {
  const result = await runExp0001({ write: false });
  assert.equal(result.schema, 'scl-exp-result/v0.1');
  assert.equal(result.experimentId, 'EXP-0001');
  assert.equal(result.terminalLexeme, 'qevra');
  assert.equal(result.semantic.invariantRecall, 1);
  assert.deepEqual(result.semantic.missingInvariants, []);
  assert.equal(result.antiPointer.sourceEmbeddedInLexicon, false);
  assert.equal(result.generativity.novelCompositionVerified, true);
  assert.equal(result.levels.length, 5);
  assert.equal(result.levels.at(-1).surface.codePoints, 5);
});
