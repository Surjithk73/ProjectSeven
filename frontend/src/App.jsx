import { useState, useEffect, useCallback } from 'react';
import { Server, Smartphone, Bot, Play, Zap, CheckCircle, XCircle, RefreshCw, AlertTriangle, Shield, Clock, Code } from 'lucide-react';
import ProviderPanel from './components/ProviderPanel';
import ClientPanel from './components/ClientPanel';
import AgentPipeline from './components/AgentPipeline';
import CodeDiffPanel from './components/CodeDiffPanel';
import SigGraphPanel from './components/SigGraphPanel';
import IpsScorePanel from './components/IpsScorePanel';
import StatusBar from './components/StatusBar';

const API = 'http://127.0.0.1:8002';

export default function App() {
  const [systemState, setSystemState] = useState({
    provider_version: 'v1',
    agent_status: 'idle',
    code_before: '',
    code_after: '',
    ips_score: 0,
    agent_log: '',
    sig_graph: {},
    current_code: '',
  });

  const [clientResult, setClientResult] = useState(null);
  const [isClientLoading, setIsClientLoading] = useState(false);
  const [isAgentRunning, setIsAgentRunning] = useState(false);
  const [agentPipelineStep, setAgentPipelineStep] = useState(-1); // -1=idle, 0-4=active step

  // Poll system state on mount
  useEffect(() => {
    fetch(`${API}/api/state`).then(r => r.json()).then(setSystemState).catch(console.error);
  }, []);

  const switchProvider = async (version) => {
    const res = await fetch(`${API}/api/provider/switch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ version }),
    });
    const data = await res.json();
    setSystemState(prev => ({ ...prev, provider_version: data.active_version, agent_status: data.agent_status }));
    setClientResult(null);
    setAgentPipelineStep(-1);
  };

  const processPayment = async () => {
    setIsClientLoading(true);
    setClientResult(null);
    try {
      const res = await fetch(`${API}/api/client/pay`, { method: 'POST' });
      const data = await res.json();
      setClientResult(data);
    } catch (e) {
      setClientResult({ status: 'error', output: 'Cannot reach backend server. Is dashboard_api.py running?' });
    }
    setIsClientLoading(false);
  };

  const wakeAgent = async () => {
    setIsAgentRunning(true);
    setAgentPipelineStep(0);
    
    // Animate through pipeline stages while waiting
    const stages = [0, 1, 2, 3, 4];
    for (let i = 0; i < stages.length - 1; i++) {
      await new Promise(r => setTimeout(r, 2500));
      setAgentPipelineStep(i + 1);
    }

    try {
      const res = await fetch(`${API}/api/agent/trigger`, { method: 'POST' });
      const data = await res.json();
      setSystemState(prev => ({
        ...prev,
        agent_status: data.status,
        code_before: data.code_before,
        code_after: data.code_after,
        ips_score: data.ips_score,
        agent_log: data.log,
        sig_graph: data.sig_graph,
      }));
      setAgentPipelineStep(data.status === 'healed' ? 5 : -1); // 5 = done
    } catch (e) {
      setAgentPipelineStep(-1);
    }
    setIsAgentRunning(false);
  };

  const systemStatus = systemState.agent_status === 'healed'
    ? 'healed'
    : systemState.provider_version === 'v2' && !isAgentRunning
    ? 'broken'
    : isAgentRunning
    ? 'healing'
    : 'healthy';

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-8 py-4 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">Self-Healing API Agent</h1>
              <p className="text-xs text-gray-500">Intent-Aware MAPE-K System</p>
            </div>
          </div>
          <StatusBar status={systemStatus} />
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-8 space-y-6">
        {/* Row 1: Provider + Client */}
        <div className="grid grid-cols-2 gap-6">
          <ProviderPanel
            version={systemState.provider_version}
            onSwitch={switchProvider}
          />
          <ClientPanel
            onPay={processPayment}
            isLoading={isClientLoading}
            result={clientResult}
            providerVersion={systemState.provider_version}
          />
        </div>

        {/* Row 2: MAPE-K Pipeline */}
        <AgentPipeline
          step={agentPipelineStep}
          isRunning={isAgentRunning}
          agentStatus={systemState.agent_status}
          onWake={wakeAgent}
          log={systemState.agent_log}
        />

        {/* Row 3: Detail panels */}
        <div className="grid grid-cols-3 gap-6">
          <CodeDiffPanel
            before={systemState.code_before}
            after={systemState.code_after}
          />
          <SigGraphPanel graph={systemState.sig_graph} />
          <IpsScorePanel
            score={systemState.ips_score}
            agentStatus={systemState.agent_status}
          />
        </div>
      </main>
    </div>
  );
}
