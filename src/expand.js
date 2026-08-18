function entryMap(lexicon) {
  if (!lexicon || typeof lexicon !== 'object' || !lexicon.entries || typeof lexicon.entries !== 'object') {
    return null;
  }
  return lexicon.entries;
}

function callsOf(entry) {
  return (entry?.expansion ?? []).filter((item) => item && typeof item === 'object' && 'call' in item);
}

export function validateLexicon(lexicon) {
  const errors = [];
  const entries = entryMap(lexicon);
  if (!entries) return { ok: false, errors: ['lexicon.entries must be an object'] };

  for (const [symbol, entry] of Object.entries(entries)) {
    if (!entry || typeof entry !== 'object') {
      errors.push(`${symbol}: entry must be an object`);
      continue;
    }
    if (!Array.isArray(entry.params)) errors.push(`${symbol}: params must be an array`);
    if (!Array.isArray(entry.expansion)) errors.push(`${symbol}: expansion must be an array`);
    if (Array.isArray(entry.params) && new Set(entry.params).size !== entry.params.length) {
      errors.push(`${symbol}: params must be unique`);
    }
    if (!Array.isArray(entry.expansion)) continue;
    for (const item of entry.expansion) {
      const isAtom = item && typeof item === 'object' && typeof item.atom === 'string';
      const isCall = item && typeof item === 'object' && typeof item.call === 'string' && Array.isArray(item.args);
      if (!isAtom && !isCall) {
        errors.push(`${symbol}: expansion items must be {atom} or {call,args}`);
        continue;
      }
      if (isCall) {
        const target = entries[item.call];
        if (!target) {
          errors.push(`${symbol}: unknown symbol ${item.call}`);
        } else if (Array.isArray(target.params) && item.args.length !== target.params.length) {
          errors.push(`${symbol}: ${item.call} expects ${target.params.length} args, got ${item.args.length}`);
        }
      }
    }
  }

  const state = new Map();
  const stack = [];
  const visit = (symbol) => {
    const s = state.get(symbol) ?? 0;
    if (s === 2) return;
    if (s === 1) {
      const start = stack.indexOf(symbol);
      const cycle = [...stack.slice(start), symbol].join(' -> ');
      errors.push(`cycle detected: ${cycle}`);
      return;
    }
    state.set(symbol, 1);
    stack.push(symbol);
    for (const call of callsOf(entries[symbol])) {
      if (entries[call.call]) visit(call.call);
    }
    stack.pop();
    state.set(symbol, 2);
  };
  for (const symbol of Object.keys(entries)) visit(symbol);

  return { ok: errors.length === 0, errors };
}

function substitute(text, env) {
  return text.replace(/\$([A-Za-z_][A-Za-z0-9_]*)/g, (_, name) => {
    if (!(name in env)) throw new Error(`unbound parameter $${name}`);
    return env[name];
  });
}

function normalizeCall(input) {
  if (typeof input === 'string') return { symbol: input, args: [] };
  if (input && typeof input === 'object' && typeof input.symbol === 'string' && Array.isArray(input.args)) {
    return input;
  }
  throw new TypeError('lexeme must be a symbol string or {symbol,args}');
}

export function expandLexeme(input, lexicon) {
  const validation = validateLexicon(lexicon);
  if (!validation.ok) throw new Error(`invalid lexicon: ${validation.errors.join('; ')}`);
  const entries = lexicon.entries;

  const expandCall = (call, parentEnv = {}) => {
    const entry = entries[call.symbol];
    if (!entry) throw new Error(`unknown symbol: ${call.symbol}`);
    if (call.args.length !== entry.params.length) {
      throw new Error(`${call.symbol} expects ${entry.params.length} args, got ${call.args.length}`);
    }
    const resolvedArgs = call.args.map((arg) => substitute(String(arg), parentEnv));
    const env = Object.fromEntries(entry.params.map((name, index) => [name, resolvedArgs[index]]));
    const atoms = [];
    for (const item of entry.expansion) {
      if (typeof item.atom === 'string') {
        atoms.push(substitute(item.atom, env));
      } else {
        const childArgs = item.args.map((arg) => substitute(String(arg), env));
        atoms.push(...expandCall({ symbol: item.call, args: childArgs }, {}));
      }
    }
    return atoms;
  };

  return expandCall(normalizeCall(input), {});
}
