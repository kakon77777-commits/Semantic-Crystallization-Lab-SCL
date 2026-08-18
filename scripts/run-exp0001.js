import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { expandLexeme } from '../src/expand.js';
import { evaluateInvariantRecall } from '../src/invariants.js';
import { measureLevel, measureText } from '../src/metrics.js';

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, '..');
const expRoot = resolve(repoRoot, 'experiments', 'EXP-0001');

async function readJson(path) {
  return JSON.parse(await readFile(path, 'utf8'));
}

function stableJson(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function lexiconSubset(lexicon, symbols) {
  return {
    schema: lexicon.schema,
    namespace: lexicon.namespace,
    entries: Object.fromEntries(symbols.map((symbol) => [symbol, lexicon.entries[symbol]])),
  };
}

function dictionaryFor(mode, atoms, lexicon) {
  if (mode === 'none') return '';
  if (mode === 'base-atoms') return stableJson(atoms);
  if (mode === 'composites') {
    return stableJson({ atoms, lexicon: lexiconSubset(lexicon, ['narel', 'vek', 'vesh']) });
  }
  if (mode === 'full') return stableJson({ atoms, lexicon });
  throw new Error(`unknown dictionary mode: ${mode}`);
}

function breakEvenDocuments(sourceCodePoints, levelCodePoints, dictionaryCodePoints) {
  const savingPerDocument = sourceCodePoints - levelCodePoints;
  if (savingPerDocument <= 0) return null;
  if (dictionaryCodePoints === 0) return 1;
  return Math.floor(dictionaryCodePoints / savingPerDocument) + 1;
}

function markdownReport(result) {
  const rows = result.levels.map((level) => {
    const surface = level.surfaceCompression.codePoints.toFixed(3);
    const dictAware = level.dictionaryAwareCompression.codePoints.toFixed(3);
    return `| ${level.id} | ${level.kind} | ${level.surface.codePoints} | ${level.dictionary.codePoints} | ${level.package.codePoints} | ${surface}x | ${dictAware}x |`;
  }).join('\n');

  const terminal = result.levels.at(-1);
  return `# EXP-0001 Results — Finite Semantic Crystallization\n\n` +
`## Status\n\n` +
`The terminal lexeme \`${result.terminalLexeme}\` recursively expands to the complete declared semantic invariant set without embedding the original source prose in the lexicon. This is a finite engineering demonstration, not a proof of the source theory's stronger cardinality or ontological claims.\n\n` +
`## Surface chain\n\n` +
`${result.levels.map((level) => `- **${level.id}** (${level.kind}): ${level.surface.codePoints} code points`).join('\n')}\n\n` +
`The checked-in surface lengths are strictly decreasing: **${result.surfaceMonotonic ? 'yes' : 'no'}**.\n\n` +
`## Metrics\n\n` +
`| Level | Kind | Surface code points | Dictionary code points | Package code points | Surface compression | Dictionary-aware compression |\n` +
`|---|---|---:|---:|---:|---:|---:|\n${rows}\n\n` +
`For the terminal level, surface-only compression is **${terminal.surfaceCompression.codePoints.toFixed(3)}x**, while first-use dictionary-aware compression is **${terminal.dictionaryAwareCompression.codePoints.toFixed(3)}x**. The distinction is intentional: a new vocabulary may be expensive on first use.\n\n` +
`Under the simplified assumption that the same dictionary is reused across comparable documents, the terminal dictionary cost breaks even after **${terminal.breakEvenDocuments.codePoints ?? 'N/A'}** documents by code-point accounting. This is an amortization illustration, not yet a corpus result.\n\n` +
`## Semantic invariant recovery\n\n` +
`Declared invariants recovered: **${result.semantic.matchedInvariants.length}/${result.semantic.expectedInvariants.length}**.\n\n` +
`Recall: **${result.semantic.invariantRecall.toFixed(3)}**.\n\n` +
`Missing: ${result.semantic.missingInvariants.length ? result.semantic.missingInvariants.join(', ') : 'none'}.\n\n` +
`Expanded base semantic IR:\n\n\`\`\`text\n${result.semantic.expandedAtoms.join(';')}\n\`\`\`\n\n` +
`## Anti-pointer gate\n\n` +
`- Source prose embedded in lexicon: **${result.antiPointer.sourceEmbeddedInLexicon ? 'yes' : 'no'}**\n` +
`- Source prefix embedded in lexicon: **${result.antiPointer.sourcePrefixEmbeddedInLexicon ? 'yes' : 'no'}**\n` +
`- Expansion target: semantic IR atoms, not original prose.\n\n` +
`## Generativity gate\n\n` +
`A novel code-oriented composition was instantiated using \`narel\` and \`vesh\` without adding new lexicon definitions. Verified: **${result.generativity.novelCompositionVerified ? 'yes' : 'no'}**.\n\n` +
`\`narel(codeA,codeB,sortMeaning,developer)\` expands to:\n\n\`\`\`text\n${result.generativity.narelExpansion.join(';')}\n\`\`\`\n\n` +
`\`vesh(codeA,sortMeaning,computeBoundary)\` expands to:\n\n\`\`\`text\n${result.generativity.veshExpansion.join(';')}\n\`\`\`\n\n` +
`## Interpretation boundary\n\n` +
`EXP-0001 establishes only that a manually specified finite semantic structure can be hierarchically re-based into shorter reusable lexemes/operators under an explicit dictionary and expansion contract. It does not establish automatic semantic discovery, human comprehension of the new lexemes without learning, or the stronger infinite-space claims in the source papers.\n`;
}

export async function runExp0001({ write = true } = {}) {
  const sourcePath = resolve(expRoot, 'source', 'source.zh.txt');
  const [sourceRaw, levels, atoms, lexicon, invariants] = await Promise.all([
    readFile(sourcePath, 'utf8'),
    readJson(resolve(expRoot, 'chain', 'levels.json')),
    readJson(resolve(expRoot, 'semantic-ir', 'atoms.json')),
    readJson(resolve(expRoot, 'lexicon', 'lexicon.json')),
    readJson(resolve(expRoot, 'semantic-ir', 'invariants.json')),
  ]);
  const source = sourceRaw.trim();
  const expandedAtoms = expandLexeme(levels.terminal, lexicon);
  const recoveredIds = new Set();
  for (const atom of expandedAtoms) {
    for (const id of invariants.atomToInvariantIds[atom] ?? []) recoveredIds.add(id);
  }
  const invariantEvaluation = evaluateInvariantRecall(invariants.expectedIds, [...recoveredIds]);

  const measuredLevels = levels.levels.map((level) => {
    const dictionaryText = dictionaryFor(level.dictionaryMode, atoms, lexicon);
    const metrics = measureLevel(source, level.text, dictionaryText);
    return {
      id: level.id,
      kind: level.kind,
      dictionaryMode: level.dictionaryMode,
      surface: metrics.level,
      dictionary: metrics.dictionary,
      package: metrics.package,
      surfaceCompression: metrics.surfaceCompression,
      dictionaryAwareCompression: metrics.dictionaryAwareCompression,
      breakEvenDocuments: {
        codePoints: breakEvenDocuments(metrics.source.codePoints, metrics.level.codePoints, metrics.dictionary.codePoints),
        utf8Bytes: breakEvenDocuments(metrics.source.utf8Bytes, metrics.level.utf8Bytes, metrics.dictionary.utf8Bytes),
      },
    };
  });

  const surfaceLengths = measuredLevels.map((level) => level.surface.codePoints);
  const surfaceMonotonic = surfaceLengths.every((value, index) => index === 0 || value < surfaceLengths[index - 1]);
  const lexiconText = stableJson(lexicon);
  const novelNarel = expandLexeme({ symbol: 'narel', args: ['codeA', 'codeB', 'sortMeaning', 'developer'] }, lexicon);
  const novelVesh = expandLexeme({ symbol: 'vesh', args: ['codeA', 'sortMeaning', 'computeBoundary'] }, lexicon);

  const result = {
    schema: 'scl-exp-result/v0.1',
    experimentId: 'EXP-0001',
    source: {
      codePoints: measureText(source).codePoints,
      utf8Bytes: measureText(source).utf8Bytes,
      file: 'experiments/EXP-0001/source/source.zh.txt',
    },
    terminalLexeme: levels.terminal,
    surfaceMonotonic,
    levels: measuredLevels,
    semantic: {
      expectedInvariants: invariants.expectedIds,
      matchedInvariants: invariantEvaluation.matched,
      missingInvariants: invariantEvaluation.missing,
      extraInvariants: invariantEvaluation.extra,
      invariantRecall: invariantEvaluation.recall,
      expandedAtoms,
    },
    antiPointer: {
      sourceEmbeddedInLexicon: lexiconText.includes(source),
      sourcePrefixEmbeddedInLexicon: lexiconText.includes(source.slice(0, 40)),
      expansionTarget: 'semantic-ir',
    },
    generativity: {
      novelCompositionVerified: novelNarel.length > 0 && novelVesh.length > 0,
      narelExpansion: novelNarel,
      veshExpansion: novelVesh,
    },
  };

  if (write) {
    const resultsDir = resolve(expRoot, 'results');
    await mkdir(resultsDir, { recursive: true });
    await writeFile(resolve(resultsDir, 'metrics.json'), stableJson(result), 'utf8');
    await writeFile(resolve(resultsDir, 'report.md'), markdownReport(result), 'utf8');
  }
  return result;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const result = await runExp0001({ write: true });
  process.stdout.write(`${JSON.stringify({
    experimentId: result.experimentId,
    terminalLexeme: result.terminalLexeme,
    invariantRecall: result.semantic.invariantRecall,
    surfaceMonotonic: result.surfaceMonotonic,
    terminalSurfaceCompression: result.levels.at(-1).surfaceCompression.codePoints,
    terminalDictionaryAwareCompression: result.levels.at(-1).dictionaryAwareCompression.codePoints,
  }, null, 2)}\n`);
}
