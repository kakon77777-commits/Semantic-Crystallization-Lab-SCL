import test from 'node:test';
import assert from 'node:assert/strict';
import { expandLexeme, validateLexicon } from '../src/expand.js';

const lexicon = {
  schema: 'scl-lexicon/v0.1',
  entries: {
    pair: {
      params: ['x', 'y'],
      expansion: [
        { atom: 'LEFT($x)' },
        { atom: 'RIGHT($y)' }
      ]
    },
    wrap: {
      params: ['a', 'b'],
      expansion: [
        { call: 'pair', args: ['$a', '$b'] },
        { atom: 'BOUND($a,$b)' }
      ]
    }
  }
};

test('recursively expands parameterized composite lexemes', () => {
  const result = expandLexeme({ symbol: 'wrap', args: ['A', 'B'] }, lexicon);
  assert.deepEqual(result, ['LEFT(A)', 'RIGHT(B)', 'BOUND(A,B)']);
});

test('rejects lexicon cycles', () => {
  const cyclic = {
    schema: 'scl-lexicon/v0.1',
    entries: {
      a: { params: [], expansion: [{ call: 'b', args: [] }] },
      b: { params: [], expansion: [{ call: 'a', args: [] }] }
    }
  };
  const result = validateLexicon(cyclic);
  assert.equal(result.ok, false);
  assert.match(result.errors.join('\n'), /cycle/i);
});

test('unknown symbol cannot expand', () => {
  assert.throws(() => expandLexeme('missing', lexicon), /unknown symbol/i);
});
