import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  TrendingUp,
  TrendingDown,
  Clock,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight,
  CreditCard,
  FileText,
  Wallet,
  CheckCircle,
  MoreHorizontal,
  Activity,
  RefreshCw,
  AlertTriangle,
} from 'lucide-react';

const transactions = [
  { id: 'TXN-0041', name: 'NexusPay Subscription', amount: '-$50.00', date: 'Sep 11, 2026', status: 'success', type: 'debit' },
  { id: 'TXN-0040', name: 'Stripe Payout', amount: '+$1,200.00', date: 'Sep 10, 2026', status: 'success', type: 'credit' },
  { id: 'TXN-0039', name: 'AWS Invoice', amount: '-$340.00', date: 'Sep 9, 2026', status: 'pending', type: 'debit' },
  { id: 'TXN-0038', name: 'Vercel Pro Plan', amount: '-$20.00', date: 'Sep 8, 2026', status: 'success', type: 'debit' },
  { id: 'TXN-0037', name: 'Refund - Overpayment', amount: '+$85.00', date: 'Sep 7, 2026', status: 'success', type: 'credit' },
];

const statusBadge = (status) => {
  if (status === 'success') return <span className="inline-flex items-center gap-1 text-xs font-medium text-green-700 bg-green-50 border border-green-100 px-2 py-0.5 rounded-full"><CheckCircle className="w-3 h-3" /> Success</span>;
  if (status === 'pending') return <span className="inline-flex items-center gap-1 text-xs font-medium text-amber-700 bg-amber-50 border border-amber-100 px-2 py-0.5 rounded-full"><Clock className="w-3 h-3" /> Pending</span>;
  return <span className="inline-flex items-center text-xs font-medium text-red-700 bg-red-50 border border-red-100 px-2 py-0.5 rounded-full">Failed</span>;
};

const barData = [55, 75, 45, 90, 60, 80, 35, 70, 85, 50, 65, 95];
const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

export default function Dashboard() {
  const navigate = useNavigate();
  const [apiStatus, setApiStatus] = useState('healthy');
  const [lastError, setLastError] = useState(null);
  const [fetchingHealth, setFetchingHealth] = useState(false);

  const checkApiHealth = useCallback(async () => {
    setFetchingHealth(true);
    try {
      const res = await fetch('http://localhost:8003/api/analytics/summary/u_123');
      if (res.ok) {
        setApiStatus('healthy');
        setLastError(null);
      } else {
        const data = await res.json().catch(() => ({}));
        setApiStatus('error');
        setLastError(data.detail || '422 Schema Mismatch');
      }
    } catch (e) {
      setApiStatus('error');
      setLastError('Connection refused');
    } finally {
      setFetchingHealth(false);
    }
  }, []);

  useEffect(() => {
    checkApiHealth();
    const interval = setInterval(checkApiHealth, 2000);
    return () => clearInterval(interval);
  }, [checkApiHealth]);

  const stats = [
    {
      label: 'Total Balance',
      value: '$12,450.00',
      change: '+2.4% this month',
      up: true,
      icon: TrendingUp,
      color: 'text-green-600',
      bg: 'bg-green-50',
      iconColor: 'text-green-600',
    },
    {
      label: 'Monthly Spend',
      value: '$2,840.00',
      change: '+8.1% vs last month',
      up: false,
      icon: TrendingDown,
      color: 'text-gray-600',
      bg: 'bg-gray-50',
      iconColor: 'text-gray-500',
    },
    {
      label: 'Pending',
      value: '$340.00',
      change: '2 transactions',
      up: null,
      icon: Clock,
      color: 'text-amber-600',
      bg: 'bg-amber-50',
      iconColor: 'text-amber-600',
    },
    {
      label: 'Saved via AI',
      value: '$0.00',
      change: 'Self-healing active',
      up: null,
      icon: Sparkles,
      color: 'text-purple-600',
      bg: 'bg-purple-50',
      iconColor: 'text-purple-600',
    },
  ];

  return (
    <div className="min-h-full">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Good morning, Surjith 👋</h1>
        <p className="text-gray-500 text-sm mt-1">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        {stats.map((s) => (
          <div key={s.label} className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
            <div className="flex items-start justify-between mb-4">
              <div className={`w-10 h-10 ${s.bg} rounded-xl flex items-center justify-center`}>
                <s.icon className={`w-5 h-5 ${s.iconColor}`} />
              </div>
              {s.up !== null && (
                <span className={`inline-flex items-center gap-0.5 text-xs font-medium ${s.up ? 'text-green-600' : 'text-red-500'}`}>
                  {s.up ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
                </span>
              )}
            </div>
            <p className="text-2xl font-bold text-gray-900 mb-1">{s.value}</p>
            <p className="text-xs text-gray-500">{s.label}</p>
            <p className={`text-xs mt-1 ${s.color} font-medium`}>{s.change}</p>
          </div>
        ))}
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-3 gap-6 mb-6">
        {/* Recent Transactions */}
        <div className="col-span-2 bg-white rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between px-6 py-5 border-b border-gray-50">
            <h2 className="font-semibold text-gray-900">Recent Transactions</h2>
            <button onClick={() => navigate('/payments')} className="text-indigo-600 text-sm font-medium hover:text-indigo-700 flex items-center gap-1">
              View all <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="divide-y divide-gray-50">
            {transactions.map((tx) => (
              <div key={tx.id} className="flex items-center justify-between px-6 py-4 hover:bg-gray-50/50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 bg-gray-100 rounded-full flex items-center justify-center">
                    <CreditCard className="w-4 h-4 text-gray-500" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{tx.name}</p>
                    <p className="text-xs text-gray-400">{tx.id} · {tx.date}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  {statusBadge(tx.status)}
                  <span className={`text-sm font-semibold ${tx.type === 'credit' ? 'text-green-600' : 'text-gray-900'}`}>
                    {tx.amount}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right panel */}
        <div className="space-y-5">
          {/* Quick Actions */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-2.5">
              <button
                onClick={() => navigate('/payments')}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium transition-colors"
              >
                <CreditCard className="w-4 h-4" />
                Pay Subscription
              </button>
              <button
                onClick={() => navigate('/invoices')}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-gray-50 hover:bg-gray-100 text-gray-700 text-sm font-medium transition-colors border border-gray-200"
              >
                <FileText className="w-4 h-4" />
                View Invoices
              </button>
              <button
                onClick={() => navigate('/cards')}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-gray-50 hover:bg-gray-100 text-gray-700 text-sm font-medium transition-colors border border-gray-200"
              >
                <Wallet className="w-4 h-4" />
                Manage Cards
              </button>
            </div>
          </div>

          {/* API Health */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-semibold text-gray-900">API Health</h2>
              <button onClick={checkApiHealth} className="p-1 rounded-lg hover:bg-gray-100 transition-colors">
                <RefreshCw className={`w-4 h-4 text-gray-400 ${fetchingHealth ? 'animate-spin' : ''}`} />
              </button>
            </div>
            
            {apiStatus === 'healthy' ? (
              <div className="flex items-center gap-2.5 p-3 bg-green-50 rounded-xl border border-green-100">
                <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse shrink-0"></span>
                <div>
                  <p className="text-xs font-semibold text-green-800">NexusPay API</p>
                  <p className="text-xs text-green-600">Last checked operation succeeded</p>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2.5 p-3 bg-red-50 rounded-xl border border-red-200">
                <AlertTriangle className="w-4 h-4 text-red-500 shrink-0" />
                <div>
                  <p className="text-xs font-semibold text-red-800">API Degraded</p>
                  <p className="text-[10px] text-red-600 font-mono mt-0.5">{lastError}</p>
                </div>
              </div>
            )}
            
            <div className="mt-3 grid grid-cols-2 gap-2">
              <div className="text-center p-2 bg-gray-50 rounded-lg">
                <p className="text-xs font-bold text-gray-900">12ms</p>
                <p className="text-xs text-gray-500">Latency</p>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded-lg">
                <p className="text-xs font-bold text-gray-900">99.9%</p>
                <p className="text-xs text-gray-500">Uptime</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-2 gap-6">
        {/* Spending bar chart */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-semibold text-gray-900">Spending Overview</h2>
            <span className="text-xs text-gray-500 bg-gray-50 px-3 py-1 rounded-full border border-gray-100">2026</span>
          </div>
          <div className="flex items-end gap-2 h-28">
            {barData.map((h, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <div
                  className={`w-full rounded-t-sm transition-all ${i === 8 ? 'bg-indigo-600' : 'bg-indigo-100'}`}
                  style={{ height: `${h}%` }}
                ></div>
                <span className="text-gray-400 text-xs">{months[i].charAt(0)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Payment Methods */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-semibold text-gray-900">Payment Methods</h2>
            <button onClick={() => navigate('/cards')} className="text-indigo-600 text-xs font-medium hover:text-indigo-700">Manage</button>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-4 bg-gradient-to-r from-indigo-600 to-blue-500 rounded-xl text-white">
              <div>
                <p className="text-xs text-indigo-200 mb-1">Primary Card</p>
                <p className="font-semibold text-sm">•••• •••• •••• 4242</p>
                <p className="text-xs text-indigo-200 mt-0.5">SURJITH K · 12/28</p>
              </div>
              <span className="text-white/80 font-bold text-sm italic">VISA</span>
            </div>
            <div className="flex items-center justify-between p-4 bg-slate-800 rounded-xl text-white">
              <div>
                <p className="text-xs text-slate-400 mb-1">Business Card</p>
                <p className="font-semibold text-sm">•••• •••• •••• 7890</p>
                <p className="text-xs text-slate-400 mt-0.5">SWIFTPAY BUSINESS · 09/27</p>
              </div>
              <span className="text-slate-300 font-bold text-sm">MC</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
