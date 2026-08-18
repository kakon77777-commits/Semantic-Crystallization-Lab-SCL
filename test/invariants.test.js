import test from 'node:test';
import assert from 'node:assert/strict';
import { evaluateInvariantRecall } from '../src/invariants.js';

test('reports full recall when all declared invariants are recovered', () => {
  const result = evaluateInvariantRecall(['I1', 'I2', 'I3'], ['I3', 'I1', 'I2']);
  assert.equal(result.recall, 1);
  assert.deepEqual(result.missing, []);
  assert.deepEqual(result.extra, []);
  assert.deepEqual(result.matched, ['I1', 'I2', 'I3']);
});

test('reports missing and extra invariants explicitly', () => {
  const result = evaluateInvariantRecall(['I1', 'I2', 'I3'], ['I1', 'I3', 'IX']);
  assert.equal(result.recall, 2 / 3);
  assert.deepEqual(result.missing, ['I2']);
  assert.deepEqual(result.extra, ['IX']);
});
