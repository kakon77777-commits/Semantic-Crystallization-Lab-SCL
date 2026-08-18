export function evaluateInvariantRecall(expectedIds, recoveredIds) {
  const expected = [...new Set(expectedIds)].sort();
  const recovered = [...new Set(recoveredIds)].sort();
  const recoveredSet = new Set(recovered);
  const expectedSet = new Set(expected);
  const matched = expected.filter((id) => recoveredSet.has(id));
  const missing = expected.filter((id) => !recoveredSet.has(id));
  const extra = recovered.filter((id) => !expectedSet.has(id));
  return {
    matched,
    missing,
    extra,
    recall: expected.length === 0 ? 1 : matched.length / expected.length,
  };
}
