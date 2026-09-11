import { Server, CheckCircle, AlertTriangle } from 'lucide-react';

const schemaV1 = `POST /charge
{
  "amount": 5000,
  "user_id": "u_123"
}`;

const schemaV2 = `POST /charge
{
  "amount": {
    "value": 5000,
    "currency": "USD"
  },
  "user_id": "u_123"
}`;

export default function ProviderPanel({ version, onSwitch }) {
  const isV2 = version === 'v2';

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
      <div className="flex items-center gap-3 mb-5">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${isV2 ? 'bg-red-100' : 'bg-blue-100'}`}>
          <Server className={`w-5 h-5 ${isV2 ? 'text-red-600' : 'text-blue-600'}`} />
        </div>
        <div>
          <h2 className="text-base font-semibold text-gray-900">Upstream API Provider</h2>
          <p className="text-xs text-gray-500">FinTech Payment Gateway — controls the schema</p>
        </div>
      </div>

      {/* Version toggle */}
      <div className="flex gap-3 mb-5">
        <button
          onClick={() => onSwitch('v1')}
          className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-all ${!isV2 ? 'bg-blue-600 text-white shadow-md shadow-blue-200' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
        >
          V1 — Stable
        </button>
        <button
          onClick={() => onSwitch('v2')}
          className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-all ${isV2 ? 'bg-red-500 text-white shadow-md shadow-red-200' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
        >
          V2 — Deploy Breaking Change
        </button>
      </div>

      {/* Schema display */}
      <div className={`rounded-xl p-4 border ${isV2 ? 'bg-red-50 border-red-200' : 'bg-blue-50 border-blue-200'}`}>
        <div className="flex items-center gap-2 mb-2">
          {isV2 ? <AlertTriangle className="w-4 h-4 text-red-500" /> : <CheckCircle className="w-4 h-4 text-blue-500" />}
          <span className={`text-xs font-semibold ${isV2 ? 'text-red-600' : 'text-blue-600'}`}>
            {isV2 ? 'Breaking change: amount is now an object' : 'Stable schema: amount is a flat integer'}
          </span>
        </div>
        <pre className={`text-xs font-mono ${isV2 ? 'text-red-800' : 'text-blue-800'}`}>
          {isV2 ? schemaV2 : schemaV1}
        </pre>
      </div>
    </div>
  );
}
