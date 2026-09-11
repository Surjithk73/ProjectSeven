import { Radio, GitBranch, Lightbulb, Wrench, ShieldCheck, Bot, RefreshCw } from 'lucide-react';

const STAGES = [
  { id: 0, label: 'Monitor',  icon: Radio,        desc: 'oasdiff detects schema drift' },
  { id: 1, label: 'Analyze',  icon: GitBranch,    desc: 'SIG maps impact & intent' },
  { id: 2, label: 'Plan',     icon: Lightbulb,    desc: 'Gemini writes a targeted patch' },
  { id: 3, label: 'Execute',  icon: Wrench,       desc: 'MCP server applies the patch' },
  { id: 4, label: 'Validate', icon: ShieldCheck,  desc: 'Tests pass & IPS is scored' },
];

export default function AgentPipeline({ step, isRunning, agentStatus, onWake, log }) {
  const isDone = agentStatus === 'healed';

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center">
            <Bot className="w-5 h-5 text-indigo-600" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-gray-900">MAPE-K Agent Pipeline</h2>
            <p className="text-xs text-gray-500">Autonomous self-healing loop — 5 stages</p>
          </div>
        </div>
        <button
          onClick={onWake}
          disabled={isRunning}
          className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white text-sm font-semibold rounded-xl transition-all shadow-sm"
        >
          {isRunning
            ? <><RefreshCw className="w-4 h-4 animate-spin" /> Healing...</>
            : <><Bot className="w-4 h-4" /> Trigger Self-Healing</>}
        </button>
      </div>

      {/* Pipeline stages */}
      <div className="flex items-center gap-0 mb-5">
        {STAGES.map((stage, idx) => {
          const isActive = step === stage.id && isRunning;
          const isDoneStage = isDone || (step > stage.id);
          const isUpcoming = step < stage.id;
          const Icon = stage.icon;

          return (
            <div key={stage.id} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-all duration-500 ${
                  isDoneStage ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200' :
                  isActive     ? 'bg-amber-500 text-white shadow-md shadow-amber-200 ring-4 ring-amber-100' :
                                 'bg-gray-100 text-gray-400'
                }`}>
                  {isActive
                    ? <RefreshCw className="w-5 h-5 animate-spin" />
                    : <Icon className="w-5 h-5" />
                  }
                </div>
                <p className={`text-xs font-semibold ${isDoneStage ? 'text-indigo-700' : isActive ? 'text-amber-600' : 'text-gray-400'}`}>
                  {stage.label}
                </p>
                <p className={`text-xs text-center mt-0.5 max-w-[100px] ${isDoneStage ? 'text-indigo-400' : isActive ? 'text-amber-400' : 'text-gray-300'}`}>
                  {stage.desc}
                </p>
              </div>
              {idx < STAGES.length - 1 && (
                <div className={`h-0.5 flex-shrink-0 w-8 transition-all duration-700 ${isDoneStage || step > stage.id ? 'bg-indigo-400' : 'bg-gray-200'}`} />
              )}
            </div>
          );
        })}
      </div>

      {/* Log output */}
      {log && (
        <div className="bg-gray-950 rounded-xl p-4 font-mono text-xs text-emerald-400 max-h-36 overflow-y-auto">
          <div className="flex items-center gap-1.5 mb-2 text-gray-600 text-[10px]">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" />
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" />
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
            <span className="ml-1">agent_log</span>
          </div>
          <pre className="whitespace-pre-wrap">{log}</pre>
        </div>
      )}
    </div>
  );
}
