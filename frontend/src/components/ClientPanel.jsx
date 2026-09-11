import { Smartphone, Play, RefreshCw, CheckCircle, XCircle } from 'lucide-react';

export default function ClientPanel({ onPay, isLoading, result, providerVersion }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
          <Smartphone className="w-5 h-5 text-emerald-600" />
        </div>
        <div>
          <h2 className="text-base font-semibold text-gray-900">Client Application</h2>
          <p className="text-xs text-gray-500">E-commerce checkout — calls the payment API</p>
        </div>
      </div>

      {/* Payment card mockup */}
      <div className="bg-gradient-to-br from-slate-700 to-slate-900 rounded-xl p-5 mb-5 text-white">
        <div className="flex justify-between items-start mb-8">
          <div>
            <p className="text-xs text-slate-400 uppercase tracking-wider">Monthly Plan</p>
            <p className="text-2xl font-bold mt-1">$50.00</p>
          </div>
          <div className={`px-2 py-1 rounded text-xs font-semibold ${providerVersion === 'v2' ? 'bg-red-500/30 text-red-300' : 'bg-emerald-500/30 text-emerald-300'}`}>
            {providerVersion === 'v2' ? 'Schema Mismatch' : 'Schema OK'}
          </div>
        </div>
        <div className="flex justify-between items-end">
          <p className="text-xs text-slate-400">user_id: u_123</p>
          <p className="text-xs text-slate-400">Endpoint: /charge</p>
        </div>
      </div>

      <button
        onClick={onPay}
        disabled={isLoading}
        className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-300 text-white rounded-xl font-semibold text-sm transition-all shadow-sm flex items-center justify-center gap-2"
      >
        {isLoading
          ? <><RefreshCw className="w-4 h-4 animate-spin" /> Processing...</>
          : <><Play className="w-4 h-4 fill-current" /> Send Payment Request</>
        }
      </button>

      {result && (
        <div className={`mt-4 rounded-xl p-4 border text-sm ${result.status === 'success'
          ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
          : 'bg-red-50 border-red-200 text-red-800'}`}>
          <div className="flex items-center gap-2 font-semibold mb-2">
            {result.status === 'success'
              ? <CheckCircle className="w-4 h-4 text-emerald-600" />
              : <XCircle className="w-4 h-4 text-red-600" />}
            {result.status === 'success' ? 'Payment Successful' : 'Payment Failed — 422 Error'}
          </div>
          <pre className="text-xs font-mono overflow-x-auto whitespace-pre-wrap">{result.output}</pre>
        </div>
      )}
    </div>
  );
}
