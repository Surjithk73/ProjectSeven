export function operationRows(overview) {
  const rows = new Map();
  for (const side of ["before", "after"])
    for (const op of overview?.[side]?.operations || []) {
      const key = `${op.method}:${op.endpoint}`;
      if (!rows.has(key))
        rows.set(key, {
          key,
          method: op.method,
          endpoint: op.endpoint,
          status: "unchanged",
        });
      rows.get(key)[side] = op;
    }
  for (const change of overview?.changes || []) {
    const key = `${change.method}:${change.endpoint}`;
    if (rows.has(key)) rows.get(key).status = change.status;
  }
  return [...rows.values()];
}

export function changeNotice(report) {
  if (report.operation !== 'compare' || report.status !== 'completed') return null;
  const changes = report.contract_overview?.changes || (report.comparison?.changed_operations || []).map(operation => ({...operation,status:'changed'}));
  const counts = {added:0,removed:0,changed:0};
  for (const change of changes) if (change.status in counts) counts[change.status]++;
  const affected = report.impacted_sites?.length || 0;
  return {title:changes.length ? 'API changes detected' : 'No API changes detected', changes, counts, affected,
    canAskAI:changes.length > 0 && affected > 0};
}

export function endpointPresentation(
  report,
  catalogOnly = report.operation === "scan",
) {
  const overview = report.contract_overview;
  if (!catalogOnly)
    return {
      comparing: true,
      rows: operationRows(overview),
      contract: overview?.before,
    };
  const consumed = new Set(
    (report.scan?.sites || []).map((site) => `${site.method}:${site.endpoint}`),
  );
  const contract = overview?.before;
  const rows = (contract?.operations || [])
    .filter((op) => consumed.has(`${op.method}:${op.endpoint}`))
    .map((op) => ({
      key: `${op.method}:${op.endpoint}`,
      method: op.method,
      endpoint: op.endpoint,
      before: op,
    }));
  return { comparing: false, rows, contract };
}
export function definitionSection(op, section, contract) {
  const definition = op.definition || op.operation || {};
  if (section === "request")
    return {
      parameters: [
        ...(op.path_settings?.parameters || []),
        ...(definition.parameters || []),
      ],
      requestBody: definition.requestBody || null,
    };
  if (section === "responses") return definition.responses || {};
  if (section === "schemas") return contract?.components || {};
  return { operation: definition, path_settings: op.path_settings || {} };
}

// Bounded line alignment preserves punctuation/duplicate lines while exposing edits.
export function pairedLines(before, after) {
  const a = before == null ? [] : JSON.stringify(before, null, 2).split("\n");
  const b = after == null ? [] : JSON.stringify(after, null, 2).split("\n");
  const left = [],
    right = [];
  const equal = (x, y) => x.replace(/,$/, "") === y.replace(/,$/, "");
  if (a.length * b.length > 400000) {
    let start = 0,
      end = 0;
    while (start < a.length && start < b.length && a[start] === b[start])
      start++;
    while (
      end < a.length - start &&
      end < b.length - start &&
      a[a.length - 1 - end] === b[b.length - 1 - end]
    )
      end++;
    return {
      before: a.map((text, i) => ({
        text,
        type: i < start || i >= a.length - end ? "same" : "removed",
      })),
      after: b.map((text, i) => ({
        text,
        type: i < start || i >= b.length - end ? "same" : "added",
      })),
    };
  }
  const table = Array.from(
    { length: a.length + 1 },
    () => new Uint32Array(b.length + 1),
  );
  for (let i = a.length - 1; i >= 0; i--)
    for (let j = b.length - 1; j >= 0; j--)
      table[i][j] = equal(a[i], b[j])
        ? 1 + table[i + 1][j + 1]
        : Math.max(table[i + 1][j], table[i][j + 1]);
  let i = 0,
    j = 0;
  while (i < a.length || j < b.length) {
    if (i < a.length && j < b.length && equal(a[i], b[j])) {
      left.push({ text: a[i++], type: "same" });
      right.push({ text: b[j++], type: "same" });
    } else if (
      i < a.length &&
      (j === b.length || table[i + 1][j] >= table[i][j + 1])
    )
      left.push({ text: a[i++], type: "removed" });
    else right.push({ text: b[j++], type: "added" });
  }
  return { before: left, after: right };
}
