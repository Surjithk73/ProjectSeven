import { useState, useEffect } from 'react';
import { Shield, Play, Search, BrainCircuit, Code, Zap, CheckCircle, Target, Settings, ChevronDown, ChevronUp, Sun, Moon } from 'lucide-react';
import { API_URL } from '../App';
import D3SigGraph from '../components/D3SigGraph';
import CodeDiffPanel from '../components/CodeDiffPanel';
import IpsScorePanel from '../components/IpsScorePanel';
import { repairPresentation } from '../repair-state';

export default function ApiShield({ systemState }) {
  const [triggering, setTriggering] = useState(false);
  const [healingMode, setHealingMode] = useState('webhook');
  const [reasoningLogs, setReasoningLogs] = useState([]);
  const [bottomTab, setBottomTab] = useState('diff');
  const [useSigContext, setUseSigContext] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [showReasoningLog, setShowReasoningLog] = useState(false);
  const [logTheme, setLogTheme] = useState('dark'); // 'dark' | 'light'
  const [triggerError, setTriggerError] = useState('');
  const { validated, score: displayIps } = repairPresentation(systemState);

  useEffect(() => {
    let interval;
    if (triggering || systemState.agent_status !== 'idle') {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`${API_URL}/api/agent/reasoning`);
          if (res.ok) {
            const data = await res.json();
            const logs = data.logs || [];
            setReasoningLogs(logs);

          }
        } catch (e) {
          // ignore
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [triggering, systemState.agent_status]);

  const handleTrigger = async () => {
    setTriggering(true);
    setTriggerError('');
    try {
      const response = await fetch(`${API_URL}/api/agent/trigger`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ healing_mode: healingMode, use_sig_context: useSigContext })
      });
      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.detail || 'Repair could not start');
      }
    } catch (error) {
      setTriggerError(error.message);
    } finally {
      setTriggering(false);
    }
  };
  const isBroken = ['break_detected', 'running', 'failed', 'needs_input'].includes(systemState.agent_status);

  // Derive dynamic pipeline details from actual reasoning logs
  const getStageDetail = (stageId) => {
    const stageMap = { monitor: 'MONITOR', analyze: 'ANALYZE', plan: 'PLAN', execute: 'EXECUTE', validate: 'VALIDATE' };
    const tag = stageMap[stageId];
    const stageLogs = reasoningLogs.filter(l => l.stage === tag);
    if (stageLogs.length === 0) return null;
    // For each stage, build a human-readable summary from the key log entries
    if (stageId === 'monitor') {
      const detectedLog = stageLogs.find(l => l.message?.toLowerCase().includes('detected') || l.message?.toLowerCase().includes('breaking'));
      return detectedLog ? detectedLog.message : stageLogs[stageLogs.length - 1].message;
    }
    if (stageId === 'analyze') {
      const foundLog = stageLogs.find(l => l.message?.toLowerCase().includes('found') || l.message?.toLowerCase().includes('impacted'));
      if (foundLog) {
        const sites = foundLog.details?.sites;
        return sites ? `Found ${sites.length} impacted call site${sites.length !== 1 ? 's' : ''}: ${sites.join(', ')}` : foundLog.message;
      }
      return stageLogs[stageLogs.length - 1].message;
    }
    if (stageId === 'plan') {
      const patchLogs = stageLogs.filter(l => l.message?.toLowerCase().includes('generated patch'));
      return patchLogs.length > 0 ? `Generated ${patchLogs.length} patch${patchLogs.length > 1 ? 'es' : ''}. ${patchLogs.map(l => l.details?.plan?.file || '').filter(Boolean).join(', ')}` : stageLogs[stageLogs.length - 1].message;
    }
    if (stageId === 'execute') {
      const appliedLogs = stageLogs.filter(l => l.message?.toLowerCase().includes('applied patch'));
      return appliedLogs.length > 0 ? `Processed ${appliedLogs.length} patch${appliedLogs.length > 1 ? 'es' : ''} via ${healingMode.toUpperCase()} mode.` : stageLogs[stageLogs.length - 1].message;
    }
    if (stageId === 'validate') {
      const ipsLog = stageLogs.find(l => l.message?.toLowerCase().includes('intent preservation'));
      return ipsLog ? ipsLog.message : stageLogs[stageLogs.length - 1].message;
    }
    return stageLogs[stageLogs.length - 1].message;
  };

  const stages = [
    { id: 'monitor', icon: Search, name: 'Monitor', desc: 'Detect breaking schema changes', color: 'blue' },
    { id: 'analyze', icon: BrainCircuit, name: 'Analyze', desc: 'Query Semantic Intent Graph', color: 'purple' },
    { id: 'plan', icon: Target, name: 'Plan', desc: 'Generate targeted patch', color: 'amber' },
    { id: 'execute', icon: Code, name: 'Execute', desc: 'Apply patch via FastMCP', color: 'indigo' },
    { id: 'validate', icon: CheckCircle, name: 'Validate', desc: 'Run tests & score IPS', color: 'emerald' },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-purple-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-purple-200">
            <Shield size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">APIShield Control Center</h1>
            <p className="text-sm text-gray-500">Autonomous Intent-Aware Self-Healing</p>
          </div>
        </div>
        
        <div className="flex flex-col items-end space-y-3 relative">
          <div className="flex items-center space-x-3">
            {/* Settings Dropdown Button */}
            <button 
              onClick={() => setShowSettings(!showSettings)}
              className="px-3 py-2.5 rounded-lg border bg-white hover:bg-slate-50 text-slate-600 transition-colors shadow-sm"
            >
              <Settings size={18} />
            </button>

            {/* Dropdown Menu */}
            {showSettings && (
              <div className="absolute top-14 right-0 w-80 bg-white border rounded-xl shadow-xl z-50 overflow-hidden">
                <div className="p-4 bg-slate-50 border-b">
                  <h3 className="font-semibold text-slate-800">Advanced Settings</h3>
                </div>
                <div className="p-4 space-y-5">
                  <label className="flex items-center justify-between cursor-pointer">
                    <div>
                      <span className="font-medium text-gray-700 block text-sm">Auto-Heal</span>
                      <span className="text-xs text-gray-500">Automatically trigger on breaks</span>
                    </div>
                    <div 
                      className={`w-10 h-5 rounded-full relative transition-colors ${systemState.auto_heal_enabled ? 'bg-purple-500' : 'bg-gray-300'}`}
                      onClick={async () => {
                        await fetch(`${API_URL}/api/settings/auto-heal`, {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ enabled: !systemState.auto_heal_enabled })
                        });
                      }}
                    >
                      <div className={`absolute top-0.5 left-0.5 bg-white w-4 h-4 rounded-full transition-transform ${systemState.auto_heal_enabled ? 'translate-x-5' : 'translate-x-0'}`}></div>
                    </div>
                  </label>

                  <label className="flex items-center justify-between cursor-pointer">
                    <div>
                      <span className="font-medium text-gray-700 block text-sm">SIG Context</span>
                      <span className="text-xs text-gray-500">Intent-aware healing mode</span>
                    </div>
                    <div 
                      className={`w-10 h-5 rounded-full relative transition-colors ${useSigContext ? 'bg-purple-500' : 'bg-gray-300'}`}
                      onClick={() => setUseSigContext(!useSigContext)}
                    >
                      <div className={`absolute top-0.5 left-0.5 bg-white w-4 h-4 rounded-full transition-transform ${useSigContext ? 'translate-x-5' : 'translate-x-0'}`}></div>
                    </div>
                  </label>
                  
                  <div className="pt-2 border-t">
                    <span className="font-medium text-gray-700 block text-sm mb-2">Healing Mode</span>
                    <div className="flex bg-gray-100 p-1 rounded-lg">
                      <button 
                        onClick={() => setHealingMode('webhook')}
                        className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-colors ${healingMode === 'webhook' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500 hover:text-gray-700'}`}
                      >
                        Local demo repair
                      </button>
                      <button 
                        onClick={() => setHealingMode('github')}
                        className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-colors flex items-center justify-center ${healingMode === 'github' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500 hover:text-gray-700'}`}
                      >
                        <Code size={12} className="mr-1"/> GitHub PR
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <button 
              onClick={handleTrigger}
              disabled={
                triggering ||
                systemState.agent_status === 'running' ||
                (systemState.auto_heal_enabled && systemState.agent_status !== 'break_detected' && systemState.agent_status !== 'upgrade_available') ||
                systemState.auto_heal_enabled
              }
              className={`px-6 py-2.5 rounded-lg font-bold text-white shadow-lg flex items-center space-x-2 transition-all ${
                systemState.agent_status === 'running' || triggering
                  ? 'bg-purple-400 cursor-not-allowed animate-pulse'
                  : systemState.auto_heal_enabled && systemState.agent_status === 'idle'
                  ? 'bg-slate-600 cursor-not-allowed'
                  : systemState.auto_heal_enabled && (systemState.agent_status === 'break_detected' || systemState.agent_status === 'upgrade_available')
                  ? 'bg-amber-500 cursor-not-allowed animate-pulse'
                  : systemState.agent_status === 'upgrade_available'
                  ? 'bg-blue-600 hover:bg-blue-700 animate-pulse'
                  : 'bg-purple-600 hover:bg-purple-700 animate-pulse'
              }`}
            >
              {systemState.agent_status === 'running' || triggering
                ? <Zap className="animate-spin" size={18} />
                : systemState.auto_heal_enabled && systemState.agent_status === 'idle'
                ? <Search className="animate-pulse" size={18} />
                : systemState.auto_heal_enabled && (systemState.agent_status === 'break_detected' || systemState.agent_status === 'upgrade_available')
                ? <Zap className="animate-bounce" size={18} />
                : <Play size={18} />}
              <span>
                {systemState.agent_status === 'running' || triggering
                  ? 'Agent Running...'
                  : systemState.auto_heal_enabled && systemState.agent_status === 'idle'
                  ? 'Monitoring Errors...'
                  : systemState.auto_heal_enabled && systemState.agent_status === 'break_detected'
                  ? 'Auto-Healing Soon...'
                  : systemState.auto_heal_enabled && systemState.agent_status === 'upgrade_available'
                  ? 'Auto-Upgrading Soon...'
                  : systemState.agent_status === 'upgrade_available'
                  ? 'Review Proactive Upgrade'
                  : 'Trigger Self-Healing'}
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* Live Status Banner */}
      {systemState.agent_status === 'idle' && systemState.auto_heal_enabled && (
        <div className="flex items-center gap-3 px-4 py-3 bg-slate-800 text-white rounded-xl text-sm mb-2">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse shrink-0"></span>
          <span className="font-medium">Auto-Heal is Active</span>
          <span className="text-slate-400">— Polling provider versions for contract changes. Switch provider to V2 to trigger.</span>
        </div>
      )}
      {systemState.agent_status === 'break_detected' && systemState.auto_heal_enabled && (
        <div className="flex items-center gap-3 px-4 py-3 bg-amber-500 text-white rounded-xl text-sm mb-2 animate-pulse">
          <Zap size={16} className="shrink-0" />
          <span className="font-medium">Breaking Change Detected!</span>
          <span className="text-amber-100">— Auto-Heal will run on the next configured check.</span>
        </div>
      )}
      {systemState.agent_status === 'upgrade_available' && systemState.auto_heal_enabled && (
        <div className="flex items-center gap-3 px-4 py-3 bg-blue-500 text-white rounded-xl text-sm mb-2 animate-pulse">
          <Zap size={16} className="shrink-0" />
          <span className="font-medium">Proactive Upgrade Available!</span>
          <span className="text-blue-100">— Upgrade will run on the next configured check.</span>
        </div>
      )}
      {systemState.agent_status === 'upgrade_available' && !systemState.auto_heal_enabled && (
        <div className="flex items-center gap-3 px-4 py-3 bg-blue-100 text-blue-900 border border-blue-200 rounded-xl text-sm mb-2">
          <Target size={16} className="shrink-0 text-blue-600" />
          <span className="font-medium">💡 Proactive Upgrade Available</span>
          <span className="text-blue-700">— V3 API added a new 'send_email_receipt' feature to POST /charge. Click 'Review Proactive Upgrade' to auto-implement it.</span>
        </div>
      )}
      {systemState.agent_status === 'running' && (
        <div className="flex items-center gap-3 px-4 py-3 bg-purple-600 text-white rounded-xl text-sm mb-2">
          <Zap size={16} className="animate-spin shrink-0" />
          <span className="font-medium">Agent Running</span>
          <span className="text-purple-200">— MAPE-K pipeline active. Analyzing, patching, and validating...</span>
        </div>
      )}
      {validated && (
        <div className="flex items-center gap-3 px-4 py-3 bg-emerald-600 text-white rounded-xl text-sm mb-2">
          <CheckCircle size={16} className="shrink-0" />
          <span className="font-medium">Repair Validated</span>
          <span className="text-emerald-200">— Configured tests passed. Judge score: {displayIps ?? 'unavailable'}</span>
        </div>
      )}
      {triggerError && <div role="alert" className="p-4 bg-red-50 text-red-800 border rounded-xl">{triggerError}</div>}
      {!systemState.provider_available && <div role="alert" className="p-4 bg-amber-50 text-amber-800 border rounded-xl">NexusPay is unavailable. Start the provider on port 8001.</div>}
      {['failed', 'needs_input', 'no_change'].includes(systemState.agent_status) && (
        <div role="status" className="p-4 bg-slate-100 border rounded-xl">
          <strong>{systemState.agent_status === 'failed' ? 'Repair failed' : systemState.agent_status === 'needs_input' ? 'Developer input required' : 'No contract changes detected'}</strong>
          <p className="text-sm mt-2">{systemState.result?.error || systemState.result?.message || systemState.validation?.test_output || systemState.agent_log}</p>
        </div>
      )}
      {/* Horizontal MAPE-K Pipeline */}
      <div className="bg-white border rounded-xl shadow-sm flex flex-col lg:flex-row divide-y lg:divide-y-0 lg:divide-x">
        {stages.map((stage) => {
          const Icon = stage.icon;
          const dynamicDetail = getStageDetail(stage.id);
          
          let stageContent = null;
          let isRunning = false;
          let isUpcoming = false;
          
          if (validated) {
            stageContent = dynamicDetail;
          } else if (systemState.agent_status === 'running') {
            if (dynamicDetail) {
              stageContent = dynamicDetail;
              isRunning = stage.id !== 'validate';
            } else {
              isRunning = true;
            }
          } else if (systemState.agent_status === 'break_detected' || systemState.agent_status === 'upgrade_available') {
            if (dynamicDetail) {
              stageContent = dynamicDetail;
            } else if (stage.id !== 'monitor') {
              isUpcoming = true;
            }
          } else {
            // idle — show any cached log data, otherwise gray out non-monitor stages
            if (dynamicDetail) {
              stageContent = dynamicDetail;
            } else if (stage.id !== 'monitor') {
              isUpcoming = true;
            }
          }

          return (
            <div key={stage.id} className={`flex-1 p-4 flex flex-col justify-start transition-all duration-300 ${isUpcoming ? 'opacity-40 grayscale hover:opacity-60' : 'hover:bg-slate-50'}`}>
              <div className={`flex items-center space-x-3 transition-all ${stageContent ? 'mb-3' : ''}`}>
                <div className={`p-2 rounded-lg bg-slate-100 text-slate-600 shrink-0 ${isRunning ? 'animate-pulse' : ''}`}>
                  <Icon size={18} />
                </div>
                <div>
                  <p className="font-bold text-gray-900 text-sm">{stage.name}</p>
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider">{stage.desc}</p>
                </div>
              </div>
              {stageContent && (
                <div className={`text-[10px] font-mono p-2.5 rounded-lg border w-full overflow-hidden relative transition-all duration-500 ${isRunning ? 'bg-indigo-50 border-indigo-100 text-indigo-700 animate-pulse' : 'bg-slate-100/50 border-slate-100 text-slate-700'}`}>
                  <div className="line-clamp-3 w-full" title={stageContent}>
                    {stageContent}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Agent Reasoning Log — full width collapsible section */}
      <div className="flex flex-col space-y-2">
        {/* Header with toggle and theme switch */}
        <div className="flex items-center justify-between px-1">
          <button
            onClick={() => setShowReasoningLog(v => !v)}
            className="flex items-center space-x-2 group"
          >
            <h3 className="font-semibold text-gray-800 group-hover:text-purple-600 transition-colors">Agent Reasoning Log</h3>
            {showReasoningLog
              ? <ChevronUp size={16} className="text-gray-400 group-hover:text-purple-500" />
              : <ChevronDown size={16} className="text-gray-400 group-hover:text-purple-500" />}
          </button>
          {showReasoningLog && (
            <button
              onClick={() => setLogTheme(t => t === 'dark' ? 'light' : 'dark')}
              title="Toggle log theme"
              className="p-1.5 rounded-lg border bg-white hover:bg-slate-50 text-slate-500 transition-colors"
            >
              {logTheme === 'dark' ? <Sun size={14} /> : <Moon size={14} />}
            </button>
          )}
        </div>

        {showReasoningLog && (
          <div className={`rounded-xl shadow-inner border overflow-hidden flex flex-col h-[600px] transition-colors ${logTheme === 'dark' ? 'bg-slate-900 border-slate-700' : 'bg-white border-slate-200'}`}>
            <div className="flex-1 overflow-y-auto p-6 space-y-4 font-mono text-xs">
              {reasoningLogs.length === 0 ? (
                <div className={`h-full flex items-center justify-center italic ${logTheme === 'dark' ? 'text-slate-500' : 'text-slate-400'}`}>Waiting for agent to start...</div>
              ) : (
                reasoningLogs.map((log, i) => (
                  <div key={i} className="animate-fade-in flex space-x-3">
                    <div className={`shrink-0 w-20 font-bold ${
                      log.stage === 'MONITOR' ? 'text-blue-400' :
                      log.stage === 'ANALYZE' ? 'text-purple-400' :
                      log.stage === 'PLAN' ? 'text-amber-400' :
                      log.stage === 'EXECUTE' ? 'text-indigo-400' :
                      log.stage === 'VALIDATE' ? 'text-emerald-400' :
                      log.stage === 'GITHUB' ? 'text-sky-400' :
                      'text-slate-400'
                    }`}>
                      [{log.stage}]
                    </div>
                    <div className={`flex-1 ${logTheme === 'dark' ? 'text-slate-300' : 'text-slate-600'}`}>
                      <span className={`font-semibold ${logTheme === 'dark' ? 'text-slate-100' : 'text-slate-900'}`}>{log.message}</span>
                      {Object.keys(log.details).length > 0 && (
                        <pre className={`mt-1 text-[10px] p-2 rounded overflow-x-auto ${logTheme === 'dark' ? 'text-slate-400 bg-slate-950' : 'text-slate-500 bg-slate-100'}`}>
                          {JSON.stringify(log.details, null, 2)}
                        </pre>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>

      {/* SIG Graph — always full width */}
      <div className="bg-white border rounded-xl shadow-sm p-4 min-h-[500px] flex flex-col">
        <h3 className="font-semibold text-gray-800 mb-2">Semantic Intent Graph (SIG)</h3>
        <div className="flex-1 border rounded-lg overflow-hidden bg-slate-50">
          {systemState.sig_graph?.nodes ? (
            <D3SigGraph data={systemState.sig_graph} isBroken={isBroken} />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">Loading graph...</div>
          )}
        </div>
        <div className="flex items-center justify-center space-x-6 mt-3 text-xs text-gray-500">
          <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-emerald-500 mr-1"></div> Endpoint</span>
          <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-blue-500 mr-1"></div> Call Site</span>
          <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-purple-500 mr-1"></div> Intent</span>
          <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-red-500 mr-1"></div> Impacted</span>
        </div>
      </div>

      {/* Bottom Row - Diff & IPS (Tabs) Full Width */}
      <div className="bg-white border rounded-xl shadow-sm flex flex-col w-full">
        {/* Tab Header */}
        <div className="flex border-b">
              <button 
                onClick={() => setBottomTab('diff')} 
                className={`flex-1 py-3 text-sm font-semibold text-center transition-colors ${bottomTab === 'diff' ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50/30' : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'}`}
              >
                Code Patch Diff
              </button>
              <button 
                onClick={() => setBottomTab('ips')} 
                className={`flex-1 py-3 text-sm font-semibold text-center transition-colors ${bottomTab === 'ips' ? 'text-emerald-600 border-b-2 border-emerald-600 bg-emerald-50/30' : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'}`}
              >
                Validation IPS
              </button>
            </div>
            
            {/* Tab Content */}
            <div className="p-4 flex-1 flex flex-col min-h-[400px]">
              {bottomTab === 'diff' ? (
                systemState.code_before && systemState.code_after ? (
                  <div className="flex-1 flex flex-col">
                    <CodeDiffPanel before={systemState.code_before} after={systemState.code_after} />
                    {systemState.pr_url && (
                      <div className="mt-3 bg-blue-50 border border-blue-100 rounded-lg p-3 flex items-center justify-between">
                        <div className="flex items-center text-sm text-blue-900">
                          <Code size={16} className="mr-2" />
                          <span>Pull Request Created: <strong className="font-mono">#{systemState.pr_url.split('/').pop()}</strong></span>
                        </div>
                        <div className="flex space-x-2">
                          <a href={systemState.pr_url} target="_blank" rel="noreferrer" className="text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 px-3 py-1.5 rounded-md transition-colors">
                            View on GitHub
                          </a>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="h-full flex-1 flex items-center justify-center text-sm text-gray-400 border border-dashed rounded bg-gray-50">
                    No patch applied yet
                  </div>
                )
              ) : (
                <div className="h-full flex flex-col items-center justify-center relative w-full">
                  <IpsScorePanel score={displayIps} agentStatus={systemState.agent_status} />
                </div>
              )}
        </div>
      </div>
    </div>
  );
}
