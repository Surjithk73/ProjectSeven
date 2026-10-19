import { useState, useEffect } from 'react';
import { Server, Terminal, UploadCloud, Database, Activity } from 'lucide-react';
import { API_URL } from '../App';

export default function NexusPay({ systemState }) {
  const [logs, setLogs] = useState([]);
  const [deploying, setDeploying] = useState(false);

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${API_URL}/api/provider/logs`);
      const data = await res.json();
      setLogs(data.logs || []);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleDeploy = async () => {
    setDeploying(true);
    await fetch(`${API_URL}/api/provider/switch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ version: 'v2' })
    });
    setTimeout(() => setDeploying(false), 1000);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-slate-800 rounded-xl flex items-center justify-center text-white">
            <Server size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">NexusPay API Dashboard</h1>
            <p className="text-sm text-gray-500">Developer Platform & Gateway</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="px-3 py-1 bg-slate-100 rounded-md text-sm font-medium border text-slate-700">
            Current: <span className="font-bold">{systemState.provider_version}.0.0</span>
          </div>
          <button 
            onClick={async () => {
              setDeploying(true);
              await fetch(`${API_URL}/api/provider/switch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ version: 'v1' })
              });
              setTimeout(() => setDeploying(false), 1000);
            }}
            disabled={deploying || systemState.provider_version === 'v1'}
            className={`px-3 py-1.5 rounded-md font-semibold text-sm transition-colors ${systemState.provider_version === 'v1' ? 'bg-slate-200 text-slate-400' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
          >
            v1
          </button>
          <button 
            onClick={async () => {
              setDeploying(true);
              await fetch(`${API_URL}/api/provider/switch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ version: 'v2' })
              });
              setTimeout(() => setDeploying(false), 1000);
            }}
            disabled={deploying || systemState.provider_version === 'v2'}
            className={`px-3 py-1.5 rounded-md font-semibold text-sm flex items-center transition-colors ${systemState.provider_version === 'v2' ? 'bg-slate-200 text-slate-400' : 'bg-slate-900 text-white hover:bg-slate-800 shadow-sm'}`}
          >
            {deploying && systemState.provider_version !== 'v2' ? <Activity className="animate-spin mr-1" size={14}/> : <UploadCloud className="mr-1" size={14} />}
            Deploy v2 (Break)
          </button>
          <button 
            onClick={async () => {
              setDeploying(true);
              await fetch(`${API_URL}/api/provider/switch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ version: 'v3' })
              });
              setTimeout(() => setDeploying(false), 1000);
            }}
            disabled={deploying || systemState.provider_version === 'v3'}
            className={`px-3 py-1.5 rounded-md font-semibold text-sm flex items-center transition-colors ${systemState.provider_version === 'v3' ? 'bg-blue-200 text-blue-400' : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'}`}
          >
            {deploying && systemState.provider_version !== 'v3' ? <Activity className="animate-spin mr-1" size={14}/> : <UploadCloud className="mr-1" size={14} />}
            Deploy v3 (Upgrade)
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
        {/* Left Col - Schema Details */}
        <div className="lg:col-span-1 space-y-6 flex flex-col h-full overflow-hidden">
          <div className="bg-white border rounded-xl shadow-sm p-4 flex flex-col flex-1 overflow-hidden">
            <div className="flex items-center space-x-2 mb-3 border-b pb-3 shrink-0">
              <Database size={18} className="text-slate-500"/>
              <h3 className="font-semibold text-slate-800">API Schema Versions</h3>
            </div>
            
            <div className="overflow-y-auto pr-2 space-y-6 flex-1 custom-scrollbar">
              
              {/* Endpoint 1: /charge */}
              <div>
                <h4 className="text-sm font-bold text-slate-700 mb-2 font-mono">POST /charge</h4>
                <div className="space-y-3">
                  {/* V1 */}
                  <div className={systemState.provider_version === 'v1' ? 'opacity-100' : 'opacity-60'}>
                    <p className={`text-[10px] font-bold uppercase tracking-wider mb-1 flex items-center ${systemState.provider_version === 'v1' ? 'text-indigo-600' : 'text-slate-500'}`}>
                      v1.0.0 ({systemState.provider_version === 'v1' ? 'Active' : 'Legacy'})
                      {systemState.provider_version === 'v1' && <span className="ml-2 px-1 py-0.5 bg-indigo-100 text-indigo-700 rounded text-[9px]">LIVE</span>}
                    </p>
                    <pre className={`p-2 rounded border text-[11px] font-mono ${systemState.provider_version === 'v1' ? 'bg-indigo-50 border-indigo-200 text-indigo-900' : 'bg-slate-50 text-slate-700'}`}>
{`{
  "user_id": "string",
  "amount": "integer"
}`}
                    </pre>
                  </div>
                  {/* V2 */}
                  <div className={systemState.provider_version === 'v2' ? 'opacity-100' : systemState.provider_version === 'v1' ? 'opacity-40' : 'opacity-60'}>
                    <p className={`text-[10px] font-bold uppercase tracking-wider mb-1 flex items-center ${systemState.provider_version === 'v2' ? 'text-indigo-600' : 'text-slate-500'}`}>
                      v2.0.0 ({systemState.provider_version === 'v2' ? 'Active' : systemState.provider_version === 'v1' ? 'Upcoming (Break)' : 'Legacy'})
                      {systemState.provider_version === 'v2' && <span className="ml-2 px-1 py-0.5 bg-indigo-100 text-indigo-700 rounded text-[9px]">LIVE</span>}
                    </p>
                    <pre className={`p-2 rounded border text-[11px] font-mono ${systemState.provider_version === 'v2' ? 'bg-indigo-50 border-indigo-200 text-indigo-900' : systemState.provider_version === 'v1' ? 'border-dashed bg-slate-50 text-slate-400' : 'bg-slate-50 text-slate-700'}`}>
{`{
  "user_id": "string",
  "amount": {
    "value": "integer",
    "currency": "string"
  }
}`}
                    </pre>
                  </div>
                  {/* V3 */}
                  <div className={systemState.provider_version === 'v3' ? 'opacity-100' : 'opacity-40'}>
                    <p className={`text-[10px] font-bold uppercase tracking-wider mb-1 flex items-center ${systemState.provider_version === 'v3' ? 'text-blue-600' : 'text-slate-500'}`}>
                      v3.0.0 ({systemState.provider_version === 'v3' ? 'Active' : 'Upcoming (Feature)'})
                      {systemState.provider_version === 'v3' && <span className="ml-2 px-1 py-0.5 bg-blue-100 text-blue-700 rounded text-[9px]">LIVE</span>}
                    </p>
                    <pre className={`p-2 rounded border text-[11px] font-mono ${systemState.provider_version === 'v3' ? 'bg-blue-50 border-blue-200 text-blue-900' : 'border-dashed bg-slate-50 text-slate-400'}`}>
{`{
  "user_id": "string",
  "amount": {
    "value": "integer",
    "currency": "string"
  },
  "send_email_receipt": "boolean" // ADDITIVE
}`}
                    </pre>
                  </div>
                </div>
              </div>

              <hr className="border-slate-100"/>

              {/* Endpoint 2: /invoice/generate */}
              <div>
                <h4 className="text-sm font-bold text-slate-700 mb-2 font-mono">POST /invoice/generate</h4>
                <div className="space-y-3">
                  <div className={systemState.provider_version === 'v1' ? 'opacity-100' : 'opacity-60'}>
                    <p className={`text-[10px] font-bold uppercase tracking-wider mb-1 flex items-center ${systemState.provider_version === 'v1' ? 'text-indigo-600' : 'text-slate-500'}`}>
                      v1.0.0 ({systemState.provider_version === 'v1' ? 'Active' : 'Legacy'})
                      {systemState.provider_version === 'v1' && <span className="ml-2 px-1 py-0.5 bg-indigo-100 text-indigo-700 rounded text-[9px]">LIVE</span>}
                    </p>
                    <pre className={`p-2 rounded border text-[11px] font-mono ${systemState.provider_version === 'v1' ? 'bg-indigo-50 border-indigo-200 text-indigo-900' : 'bg-slate-50 text-slate-700'}`}>
{`{
  "user_id": "string",
  "period": "string"
}`}
                    </pre>
                  </div>
                  <div className={systemState.provider_version !== 'v1' ? 'opacity-100' : 'opacity-40'}>
                    <p className={`text-[10px] font-bold uppercase tracking-wider mb-1 flex items-center ${systemState.provider_version !== 'v1' ? 'text-indigo-600' : 'text-slate-500'}`}>
                      v2.0.0 ({systemState.provider_version !== 'v1' ? 'Active' : 'Upcoming (Break)'})
                      {systemState.provider_version !== 'v1' && <span className="ml-2 px-1 py-0.5 bg-indigo-100 text-indigo-700 rounded text-[9px]">LIVE</span>}
                    </p>
                    <pre className={`p-2 rounded border text-[11px] font-mono ${systemState.provider_version !== 'v1' ? 'bg-indigo-50 border-indigo-200 text-indigo-900' : 'border-dashed bg-slate-50 text-slate-400'}`}>
{`{
  "user_id": "string",
  "period": "string",
  "billing_address": "object" // NEW
}`}
                    </pre>
                  </div>
                </div>
              </div>

              <hr className="border-slate-100"/>

              {/* Endpoint 3: /analytics/log */}
              <div>
                <h4 className="text-sm font-bold text-slate-700 mb-2 font-mono">POST /analytics/log (Response)</h4>
                <div className="space-y-3">
                  <div className={systemState.provider_version === 'v1' ? 'opacity-100' : 'opacity-60'}>
                    <p className={`text-[10px] font-bold uppercase tracking-wider mb-1 flex items-center ${systemState.provider_version === 'v1' ? 'text-indigo-600' : 'text-slate-500'}`}>
                      v1.0.0 ({systemState.provider_version === 'v1' ? 'Active' : 'Legacy'})
                      {systemState.provider_version === 'v1' && <span className="ml-2 px-1 py-0.5 bg-indigo-100 text-indigo-700 rounded text-[9px]">LIVE</span>}
                    </p>
                    <pre className={`p-2 rounded border text-[11px] font-mono ${systemState.provider_version === 'v1' ? 'bg-indigo-50 border-indigo-200 text-indigo-900' : 'bg-slate-50 text-slate-700'}`}>
{`{
  "status": "success",
  "event": "subscription_paid",
  "user_id": "customer_9",
  "metadata": {"amount": 5001}
}`}
                    </pre>
                  </div>
                  <div className={systemState.provider_version !== 'v1' ? 'opacity-100' : 'opacity-40'}>
                    <p className={`text-[10px] font-bold uppercase tracking-wider mb-1 flex items-center ${systemState.provider_version !== 'v1' ? 'text-indigo-600' : 'text-slate-500'}`}>
                      v2.0.0 ({systemState.provider_version !== 'v1' ? 'Active' : 'Upcoming (Break)'})
                      {systemState.provider_version !== 'v1' && <span className="ml-2 px-1 py-0.5 bg-indigo-100 text-indigo-700 rounded text-[9px]">LIVE</span>}
                    </p>
                    <pre className={`p-2 rounded border text-[11px] font-mono ${systemState.provider_version !== 'v1' ? 'bg-indigo-50 border-indigo-200 text-indigo-900' : 'border-dashed bg-slate-50 text-slate-400'}`}>
{`{
  "data": {
    "status": "success",
    "event": "subscription_paid",
    "user_id": "customer_9",
    "metadata": {"amount": 5001}
  }
}`}
                    </pre>
                  </div>
                </div>
              </div>

              <hr className="border-slate-100"/>

              {/* Endpoint 4: /refund */}
              <div>
                <h4 className="text-sm font-bold text-slate-700 mb-2 font-mono">POST /refund</h4>
                <div className="space-y-3">
                  <div className={systemState.provider_version === 'v1' ? 'opacity-100' : 'opacity-60'}>
                    <p className={`text-[10px] font-bold uppercase tracking-wider mb-1 flex items-center ${systemState.provider_version === 'v1' ? 'text-indigo-600' : 'text-slate-500'}`}>
                      v1.0.0 ({systemState.provider_version === 'v1' ? 'Active' : 'Legacy'})
                      {systemState.provider_version === 'v1' && <span className="ml-2 px-1 py-0.5 bg-indigo-100 text-indigo-700 rounded text-[9px]">LIVE</span>}
                    </p>
                    <pre className={`p-2 rounded border text-[11px] font-mono ${systemState.provider_version === 'v1' ? 'bg-indigo-50 border-indigo-200 text-indigo-900' : 'bg-slate-50 text-slate-700'}`}>
{`{
  "transaction_id": "string"
}`}
                    </pre>
                  </div>
                  <div className={systemState.provider_version !== 'v1' ? 'opacity-100' : 'opacity-40'}>
                    <p className={`text-[10px] font-bold uppercase tracking-wider mb-1 flex items-center ${systemState.provider_version !== 'v1' ? 'text-red-600' : 'text-slate-500'}`}>
                      v2.0.0 ({systemState.provider_version !== 'v1' ? 'Deprecated' : 'Upcoming (Deprecation)'})
                      {systemState.provider_version !== 'v1' && <span className="ml-2 px-1 py-0.5 bg-red-100 text-red-700 rounded text-[9px]">LIVE</span>}
                    </p>
                    <div className={`p-2 rounded border text-[11px] font-mono flex items-center ${systemState.provider_version !== 'v1' ? 'bg-red-50 border-red-200 text-red-900' : 'border-dashed bg-slate-50 text-slate-400'}`}>
                      <span className={`${systemState.provider_version !== 'v1' ? 'line-through' : ''} mr-2`}>Endpoint Removed</span>
                      (Use /refunds/create)
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>

        {/* Right Col - Live Request Log */}
        <div className="lg:col-span-2 bg-slate-900 rounded-xl shadow-lg flex flex-col overflow-hidden border border-slate-800">
          <div className="bg-slate-950 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center text-slate-400 space-x-2">
              <Terminal size={16} />
              <span className="text-sm font-mono tracking-wide">Live Gateway Logs</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-slate-500 uppercase">Listening...</span>
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-2 font-mono text-xs">
            {logs.length === 0 ? (
              <p className="text-slate-600 text-center mt-10">Waiting for requests...</p>
            ) : (
              logs.map((log, i) => (
                <div key={log.id || i} className="flex flex-col border-b border-slate-800/50 pb-2 mb-2">
                  <div className="flex items-center space-x-3 mb-1">
                    <span className="text-slate-500">{new Date(log.timestamp).toLocaleTimeString()}</span>
                    <span className={`font-bold ${log.method==='POST' ? 'text-amber-400' : 'text-blue-400'}`}>{log.method}</span>
                    <span className="text-slate-300">{log.path}</span>
                    <span className="flex-1"></span>
                    <span className={`px-2 py-0.5 rounded ${
                      log.status === 200 ? 'bg-emerald-900/50 text-emerald-400' : 
                      log.status === 422 ? 'bg-rose-900/50 text-rose-400' : 'text-slate-400'
                    }`}>{log.status}</span>
                  </div>
                  {log.payload && (
                    <div className="pl-20 text-slate-500 truncate">
                      {JSON.stringify(log.payload)}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
