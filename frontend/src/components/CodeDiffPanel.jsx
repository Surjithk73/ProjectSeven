import { Code, Minus, Plus } from 'lucide-react';

function renderDiff(before, after) {
  if (!before || !after) return [];
  const beforeLines = before.split('\n');
  const afterLines = after.split('\n');
  const result = [];

  // Find changed lines by comparing
  const maxLen = Math.max(beforeLines.length, afterLines.length);
  for (let i = 0; i < maxLen; i++) {
    const b = beforeLines[i];
    const a = afterLines[i];
    if (b === undefined) {
      result.push({ type: 'add', content: a, line: i + 1 });
    } else if (a === undefined) {
      result.push({ type: 'remove', content: b, line: i + 1 });
    } else if (b !== a) {
      result.push({ type: 'remove', content: b, line: i + 1 });
      result.push({ type: 'add', content: a, line: i + 1 });
    } else {
      result.push({ type: 'same', content: b, line: i + 1 });
    }
  }
  return result;
}

export default function CodeDiffPanel({ before, after }) {
  const hasDiff = before && after && before !== after;
  const diffLines = hasDiff ? renderDiff(before, after) : [];

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-lg bg-violet-100 flex items-center justify-center">
          <Code className="w-4 h-4 text-violet-600" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-gray-900">Code Diff</h3>
          <p className="text-xs text-gray-500">Agent-applied patch</p>
        </div>
      </div>

      <div className="flex-1 bg-gray-950 rounded-xl overflow-hidden">
        {!hasDiff ? (
          <div className="flex items-center justify-center h-32 text-gray-600 text-xs font-mono">
            Waiting for agent to run...
          </div>
        ) : (
          <div className="overflow-y-auto max-h-64 text-xs font-mono">
            {diffLines.map((line, i) => (
              <div
                key={i}
                className={`flex items-start gap-2 px-3 py-0.5 ${
                  line.type === 'add' ? 'bg-emerald-950/60 text-emerald-300' :
                  line.type === 'remove' ? 'bg-red-950/60 text-red-300' :
                  'text-gray-500'
                }`}
              >
                <span className="w-4 flex-shrink-0 opacity-50 text-right">
                  {line.type === 'add' ? <Plus className="w-3 h-3 inline" /> :
                   line.type === 'remove' ? <Minus className="w-3 h-3 inline" /> : ' '}
                </span>
                <pre className="whitespace-pre-wrap break-all">{line.content}</pre>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
