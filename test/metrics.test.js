import test from 'node:test';
import assert from 'node:assert/strict';
import { measureLevel, measureText } from '../src/metrics.js';

test('distinguishes Unicode code points from UTF-8 bytes', () => {
  assert.deepEqual(measureText('中A'), { codePoints: 2, utf8Bytes: 4 });
});

test('reports surface and dictionary-aware compression separately', () => {
  const result = measureLevel('abcdef', 'xy', '123');
  assert.equal(result.surfaceCompression.codePoints, 3);
  assert.equal(result.package.codePoints, 5);
  assert.equal(result.dictionaryAwareCompression.codePoints, 6 / 5);
  assert.equal(result.source.codePoints, 6);
  assert.equal(result.level.codePoints, 2);
  assert.equal(result.dictionary.codePoints, 3);
});
