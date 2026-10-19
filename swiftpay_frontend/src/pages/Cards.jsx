import { useState } from 'react';
import { Plus, Zap, Lock, Unlock, MoreHorizontal, TrendingUp, Shield } from 'lucide-react';

const cards = [
  {
    id: 1,
    last4: '4242',
    holder: 'SURJITH K',
    network: 'VISA',
    expiry: '12/28',
    gradient: 'from-indigo-600 via-indigo-700 to-blue-800',
    limit: 10000,
    available: 7340,
    label: 'Personal',
    transactions: [
      { name: 'NexusPay Subscription', amount: '-$50.00', date: 'Sep 11' },
      { name: 'Vercel Pro', amount: '-$20.00', date: 'Sep 8' },
      { name: 'Refund', amount: '+$85.00', date: 'Sep 7' },
      { name: 'AWS Invoice', amount: '-$340.00', date: 'Sep 5' },
    ],
  },
  {
    id: 2,
    last4: '7890',
    holder: 'SWIFTPAY BUSINESS',
    network: 'MC',
    expiry: '09/27',
    gradient: 'from-slate-700 via-slate-800 to-slate-900',
    limit: 50000,
    available: 43200,
    label: 'Business',
    transactions: [
      { name: 'Google Workspace', amount: '-$180.00', date: 'Sep 10' },
      { name: 'Stripe Fees', amount: '-$42.30', date: 'Sep 9' },
      { name: 'Client Payout', amount: '+$2,400.00', date: 'Sep 6' },
      { name: 'Office Supplies', amount: '-$78.50', date: 'Sep 3' },
    ],
  },
  {
    id: 3,
    last4: '1234',
    holder: 'EXPENSE CARD',
    network: 'VISA',
    expiry: '06/26',
    gradient: 'from-emerald-600 via-emerald-700 to-teal-800',
    limit: 5000,
    available: 4650,
    label: 'Expense',
    transactions: [
      { name: 'Lunch Meeting', amount: '-$84.00', date: 'Sep 11' },
      { name: 'Travel - Uber', amount: '-$24.50', date: 'Sep 10' },
      { name: 'Conference Fee', amount: '-$199.00', date: 'Sep 4' },
      { name: 'Hotel', amount: '-$342.00', date: 'Sep 1' },
    ],
  },
];

export default function Cards() {
  const [selected, setSelected] = useState(0);
  const [frozen, setFrozen] = useState({});

  const card = cards[selected];
  const isFrozen = frozen[card.id];
  const spentPct = Math.round(((card.limit - card.available) / card.limit) * 100);

  return (
    <div className="min-h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Cards</h1>
          <p className="text-gray-500 text-sm mt-1">Manage your payment cards and spending limits</p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl transition-colors shadow-md shadow-indigo-100">
          <Plus className="w-4 h-4" />
          Add New Card
        </button>
      </div>

      {/* Card mockups */}
      <div className="grid grid-cols-3 gap-5 mb-8">
        {cards.map((c, i) => (
          <button
            key={c.id}
            onClick={() => setSelected(i)}
            className={`relative text-left rounded-2xl p-6 text-white bg-gradient-to-br ${c.gradient} shadow-lg transition-all duration-200 ${
              selected === i ? 'ring-2 ring-indigo-400 ring-offset-2 scale-105' : 'hover:scale-102 opacity-80 hover:opacity-100'
            } overflow-hidden`}
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-6">
                <div className="w-7 h-7 bg-white/20 rounded-lg flex items-center justify-center">
                  <Zap className="w-3.5 h-3.5 text-white" />
                </div>
                <div className="flex items-center gap-2">
                  {frozen[c.id] && <Lock className="w-3.5 h-3.5 text-white/60" />}
                  <span className="text-xs text-white/70 bg-white/10 px-2 py-0.5 rounded-full">{c.label}</span>
                </div>
              </div>
              <p className="text-white/60 text-xs tracking-[0.3em] mb-1">•••• •••• •••• {c.last4}</p>
              <div className="flex justify-between items-end mt-4">
                <div>
                  <p className="text-white/50 text-xs mb-0.5">Holder</p>
                  <p className="text-white font-semibold text-xs tracking-wider">{c.holder}</p>
                </div>
                <div className="text-right">
                  <p className="text-white/50 text-xs mb-0.5">Expires</p>
                  <p className="text-white font-semibold text-xs">{c.expiry}</p>
                </div>
              </div>
              <div className="flex justify-end mt-2">
                <span className="text-white/70 font-bold text-xs italic">{c.network}</span>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* Detail panel */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left — Card details */}
        <div className="col-span-2 space-y-5">
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="font-semibold text-gray-900 text-lg">{card.label} Card — ···· {card.last4}</h2>
                <p className="text-sm text-gray-500 mt-0.5">{card.holder} · Expires {card.expiry}</p>
              </div>
              <button className="p-2 rounded-lg hover:bg-gray-100 text-gray-400 transition-colors">
                <MoreHorizontal className="w-5 h-5" />
              </button>
            </div>

            {/* Spending limit bar */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-600">Spending Used</span>
                <span className="text-sm font-semibold text-gray-900">{spentPct}%</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2.5">
                <div
                  className="bg-indigo-600 h-2.5 rounded-full transition-all duration-300"
                  style={{ width: `${spentPct}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-gray-400 mt-1.5">
                <span>Spent: ${(card.limit - card.available).toLocaleString()}</span>
                <span>Limit: ${card.limit.toLocaleString()}</span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                <p className="text-xs text-gray-500 mb-1">Available Credit</p>
                <p className="text-xl font-bold text-gray-900">${card.available.toLocaleString()}</p>
              </div>
              <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                <p className="text-xs text-gray-500 mb-1">Credit Limit</p>
                <p className="text-xl font-bold text-gray-900">${card.limit.toLocaleString()}</p>
              </div>
              <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                <p className="text-xs text-gray-500 mb-1">Cashback Earned</p>
                <p className="text-xl font-bold text-green-600">$142.50</p>
              </div>
            </div>

            {/* Freeze toggle */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-100">
              <div className="flex items-center gap-3">
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${isFrozen ? 'bg-blue-100' : 'bg-gray-100'}`}>
                  {isFrozen ? <Lock className="w-4.5 h-4.5 text-blue-600" /> : <Unlock className="w-4.5 h-4.5 text-gray-500" />}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{isFrozen ? 'Card Frozen' : 'Card Active'}</p>
                  <p className="text-xs text-gray-500">{isFrozen ? 'All transactions blocked' : 'Transactions enabled'}</p>
                </div>
              </div>
              <button
                onClick={() => setFrozen((f) => ({ ...f, [card.id]: !f[card.id] }))}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${isFrozen ? 'bg-blue-600' : 'bg-gray-200'}`}
              >
                <span className={`inline-block h-4 w-4 rounded-full bg-white shadow transition-transform ${isFrozen ? 'translate-x-6' : 'translate-x-1'}`} />
              </button>
            </div>
          </div>

          {/* Security */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <div className="flex items-center gap-2 mb-4">
              <Shield className="w-4 h-4 text-indigo-600" />
              <h2 className="font-semibold text-gray-900">Security & Controls</h2>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {['Online Purchases', 'International Transactions', 'ATM Withdrawals', 'Contactless Payments'].map((ctrl) => (
                <div key={ctrl} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <span className="text-sm text-gray-700">{ctrl}</span>
                  <button className="relative inline-flex h-5 w-9 items-center rounded-full bg-indigo-600 transition-colors">
                    <span className="inline-block h-3.5 w-3.5 rounded-full bg-white shadow translate-x-4.5 transition-transform" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right — Recent transactions */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-semibold text-gray-900">Recent Charges</h2>
            <TrendingUp className="w-4 h-4 text-gray-400" />
          </div>
          <div className="space-y-3">
            {card.transactions.map((tx, i) => (
              <div key={i} className="flex items-center justify-between py-3 border-b border-gray-50 last:border-0">
                <div>
                  <p className="text-sm font-medium text-gray-900">{tx.name}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{tx.date}</p>
                </div>
                <span className={`text-sm font-semibold ${tx.amount.startsWith('+') ? 'text-green-600' : 'text-gray-900'}`}>
                  {tx.amount}
                </span>
              </div>
            ))}
          </div>
          <button className="w-full mt-4 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-600 hover:bg-gray-50 transition-colors font-medium">
            View All Transactions
          </button>
        </div>
      </div>
    </div>
  );
}
