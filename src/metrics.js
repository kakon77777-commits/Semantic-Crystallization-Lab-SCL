export function measureText(text) {
  const value = String(text);
  return {
    codePoints: [...value].length,
    utf8Bytes: Buffer.byteLength(value, 'utf8'),
  };
}

export function measureLevel(sourceText, levelText, dictionaryText = '') {
  const source = measureText(sourceText);
  const level = measureText(levelText);
  const dictionary = measureText(dictionaryText);
  const packageMeasure = {
    codePoints: level.codePoints + dictionary.codePoints,
    utf8Bytes: level.utf8Bytes + dictionary.utf8Bytes,
  };
  return {
    source,
    level,
    dictionary,
    package: packageMeasure,
    surfaceCompression: {
      codePoints: level.codePoints === 0 ? Infinity : source.codePoints / level.codePoints,
      utf8Bytes: level.utf8Bytes === 0 ? Infinity : source.utf8Bytes / level.utf8Bytes,
    },
    dictionaryAwareCompression: {
      codePoints: packageMeasure.codePoints === 0 ? Infinity : source.codePoints / packageMeasure.codePoints,
      utf8Bytes: packageMeasure.utf8Bytes === 0 ? Infinity : source.utf8Bytes / packageMeasure.utf8Bytes,
    },
  };
}
