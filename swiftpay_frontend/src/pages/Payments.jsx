import { useState, useEffect, useCallback } from 'react';
import {
  CreditCard,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  ExternalLink,
  Loader2,
  Wifi,
  WifiOff,
  Clock,
  Zap,
} from 'lucide-react';

const BFF_URL = 'http://localhost:8003';

export default function Payments() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState('healthy');
  const [lastError, setLastError] = useState(null);
  const [fetchingTx, setFetchingTx] = useState(false);

  const fetchTransactions = useCallback(async () => {
    setFetchingTx(true);
    try {
      const res = await fetch(`${BFF_URL}/api/transactions`);
      if (res.ok) {
        const data = await res.json();
        const txList = Array.isArray(data) ? data : (data.transactions || []);
        setTransactions(txList.slice(0, 10));
      }
    } catch (e) {
      // silently ignore fetch errors for polling
    } finally {
      setFetchingTx(false);
    }
  }, []);

  // Poll every 2 seconds
  useEffect(() => {
    fetchTransactions();
    const interval = setInterval(fetchTransactions, 2000);
    return () => clearInterval(interval);
  }, [fetchTransactions]);

  const handlePay = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${BFF_URL}/api/pay`, { method: 'POST' });
      if (res.ok) {
        setApiStatus('healthy');
        setLastError(null);
      } else {
        setApiStatus('error');
        const data = await res.json().catch(() => ({}));
        setLastError(data.detail || '422 Schema Mismatch');
      }
      await fetchTransactions();
    } catch (e) {
      setApiStatus('error');
      setLastError('Connection refused — BFF unreachable');
    } finally {
      setLoading(false);
    }
  };

  const statusBadge = (status, errorCode) => {
    if (status === 'success' || status === 'completed') {
      return (
        <span className="inline-flex items-center gap-1 text-xs font-medium text-green-700 bg-green-50 border border-green-200 px-2 py-0.5 rounded-full">
          <CheckCircle className="w-3 h-3" /> Success
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 text-xs font-medium text-red-700 bg-red-50 border border-red-200 px-2 py-0.5 rounded-full">
        <XCircle className="w-3 h-3" /> Failed
      </span>
    );
  };

  const apiResponseCell = (tx) => {
    if (tx.status === 'success' || tx.status === 'completed') {
      return <span className="text-green-600 text-xs font-mono">200 OK</span>;
    }
    return (
      <span className="text-red-500 text-xs font-mono font-semibold">
        {tx.error || '422 - Schema Mismatch'}
      </span>
    );
  };

  const formatTime = (ts) => {
    if (!ts) return '—';
    try {
      return new Date(ts).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return ts;
    }
  };

  return (
    <div className="min-h-full">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Payments</h1>
        <p className="text-gray-500 text-sm mt-1">Manage subscriptions, pay invoices, and monitor API health</p>
      </div>

      {/* API Status Banner */}
      {apiStatus === 'healthy' ? (
        <div className="flex items-center justify-between bg-green-50 border border-green-200 rounded-xl px-5 py-3.5 mb-6">
          <div className="flex items-center gap-3">
            <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse shrink-0"></span>
            <div>
              <span className="text-sm font-semibold text-green-800">NexusPay API — Last checked operation succeeded</span>
              <span className="ml-2 text-xs text-green-600">· Self-healing active</span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-green-600 font-medium">
            <Wifi className="w-4 h-4" />
            Connected
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-between bg-red-50 border border-red-300 rounded-xl px-5 py-3.5 mb-6 animate-pulse">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 animate-none" />
            <div>
              <span className="text-sm font-bold text-red-800">
                ⚠️ NexusPay API BREAKING CHANGE DETECTED — Payments failing (422 Unprocessable Content).
              </span>
              <span className="ml-2 text-xs text-red-600">Visit APIShield to trigger self-healing.</span>
            </div>
          </div>
          <a
            href="http://localhost:5173/agent"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-xs font-semibold rounded-lg transition-colors animate-none shrink-0"
          >
            Open APIShield <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      )}

      {/* Main layout */}
      <div className="grid grid-cols-5 gap-6">
        {/* Left panel */}
        <div className="col-span-2 space-y-5">
          {/* Credit card mockup */}
          <div className="bg-gradient-to-br from-indigo-600 via-indigo-700 to-blue-800 rounded-2xl p-6 text-white shadow-xl shadow-indigo-200 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-40 h-40 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2"></div>
            <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2"></div>
            <div className="relative">
              <div className="flex justify-between items-start mb-8">
                <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                  <Zap className="w-4 h-4 text-white" />
                </div>
                <span className="text-white/80 font-bold text-sm italic tracking-wider">VISA</span>
              </div>
              <div className="mb-5">
                <div className="flex gap-2 mb-1">
                  <span className="text-white/60 text-xs tracking-[0.3em]">••••</span>
                  <span className="text-white/60 text-xs tracking-[0.3em]">••••</span>
                  <span className="text-white/60 text-xs tracking-[0.3em]">••••</span>
                  <span className="text-white font-mono text-xs tracking-[0.3em]">4242</span>
                </div>
              </div>
              <div className="flex justify-between items-end">
                <div>
                  <p className="text-white/50 text-xs uppercase tracking-wider mb-0.5">Card Holder</p>
                  <p className="text-white font-semibold text-sm tracking-widest">SURJITH K</p>
                </div>
                <div className="text-right">
                  <p className="text-white/50 text-xs uppercase tracking-wider mb-0.5">Expires</p>
                  <p className="text-white font-semibold text-sm">12/28</p>
                </div>
              </div>
            </div>
          </div>

          {/* Subscription details */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <div className="flex items-start justify-between mb-5">
              <div>
                <h3 className="font-semibold text-gray-900">NexusPay Monthly Subscription</h3>
                <p className="text-gray-500 text-xs mt-0.5">Enterprise API Access Plan</p>
              </div>
              <span className="bg-indigo-50 text-indigo-700 text-xs font-semibold px-2.5 py-1 rounded-full border border-indigo-100">Active</span>
            </div>

            <div className="space-y-3 mb-6">
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-500">Amount</span>
                <span className="font-bold text-gray-900">$50.00 / month</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-500">Billing Cycle</span>
                <span className="text-gray-700">Monthly · 11th of each month</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-500">Next Due</span>
                <span className="text-gray-700">Oct 11, 2026</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-500">Auto-pay</span>
                <span className="text-green-600 font-medium">Enabled</span>
              </div>
            </div>

            <div className="border-t border-gray-50 pt-5 space-y-3">
              <button
                onClick={handlePay}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2.5 py-3.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-70 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors shadow-md shadow-indigo-100 text-sm"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Processing Payment...
                  </>
                ) : (
                  <>
                    <CreditCard className="w-4 h-4" />
                    Pay $50.00
                  </>
                )}
              </button>

              <button
                onClick={async () => {
                  setLoading(true);
                  try {
                    const res = await fetch(`${BFF_URL}/api/refund`, { method: 'POST' });
                    if (res.ok) {
                      setApiStatus('healthy');
                      setLastError(null);
                    } else {
                      setApiStatus('error');
                      const data = await res.json().catch(() => ({}));
                      setLastError(data.detail || '404 Endpoint Not Found');
                    }
                    await fetchTransactions();
                  } catch (e) {
                    setApiStatus('error');
                    setLastError('Connection refused — BFF unreachable');
                  } finally {
                    setLoading(false);
                  }
                }}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2.5 py-3 bg-white hover:bg-gray-50 border border-gray-200 disabled:opacity-70 disabled:cursor-not-allowed text-gray-700 font-medium rounded-xl transition-colors text-sm"
              >
                <RefreshCw className="w-4 h-4 text-gray-400" />
                Process Refund
              </button>

              <div className="flex items-center justify-center gap-2 mt-3">
                <span className="text-gray-400 text-xs">Powered by</span>
                <span className="text-gray-600 text-xs font-semibold">NexusPay API</span>
                <span className="bg-gray-100 text-gray-500 text-xs font-mono px-1.5 py-0.5 rounded">v1</span>
              </div>
            </div>
          </div>

          {/* Last error */}
          {lastError && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <div className="flex items-start gap-2">
                <XCircle className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-red-800">Payment Failed</p>
                  <p className="text-xs text-red-600 mt-0.5 font-mono">{lastError}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right panel — Transaction history */}
        <div className="col-span-3 bg-white rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between px-6 py-5 border-b border-gray-50">
            <div>
              <h2 className="font-semibold text-gray-900">Transaction History</h2>
              <p className="text-xs text-gray-500 mt-0.5">Live — polling every 2s</p>
            </div>
            <div className="flex items-center gap-2">
              {fetchingTx && <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />}
              <button
                onClick={fetchTransactions}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-500 hover:text-gray-700"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50/70">
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Description</th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Amount</th>
                  <th className="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Time</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">API Response</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {transactions.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-16 text-gray-400">
                      <Clock className="w-8 h-8 mx-auto mb-3 opacity-30" />
                      <p className="text-sm">No transactions yet. Try paying a subscription.</p>
                    </td>
                  </tr>
                ) : (
                  transactions.map((tx) => (
                    <tr key={tx.id} className={`hover:bg-gray-50/50 transition-colors ${(tx.status === 'failed' || tx.status === 'error') ? 'bg-red-50/30' : ''}`}>
                      <td className="px-5 py-4">
                        <span className="text-xs font-mono text-gray-500">{tx.id || tx.transaction_id || '—'}</span>
                      </td>
                      <td className="px-4 py-4">
                        <span className="text-sm text-gray-700">{tx.description || tx.service || 'NexusPay Subscription'}</span>
                      </td>
                      <td className="px-4 py-4 text-right">
                        <span className="text-sm font-semibold text-gray-900">{tx.amount || '$50.00'}</span>
                      </td>
                      <td className="px-4 py-4 text-center">
                        {statusBadge(tx.status)}
                      </td>
                      <td className="px-4 py-4">
                        <span className="text-xs text-gray-500">{formatTime(tx.timestamp || tx.created_at)}</span>
                      </td>
                      <td className="px-4 py-4">
                        {apiResponseCell(tx)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
