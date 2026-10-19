import { useState } from 'react';
import {
  Search,
  Download,
  Eye,
  ChevronLeft,
  ChevronRight,
  Plus,
  Filter,
  CheckCircle,
  Clock,
  AlertCircle,
  FileText,
} from 'lucide-react';

const mockInvoices = [
  { id: 'INV-2026-0041', client: 'Acme Corp', amount: '$4,200.00', status: 'paid', date: 'Sep 1, 2026', due: 'Sep 15, 2026', email: 'finance@acme.com' },
  { id: 'INV-2026-0040', client: 'TechLaunch Ltd', amount: '$1,800.00', status: 'pending', date: 'Sep 3, 2026', due: 'Sep 17, 2026', email: 'billing@techlaunch.io' },
  { id: 'INV-2026-0039', client: 'Pixel Studio', amount: '$900.00', status: 'overdue', date: 'Aug 15, 2026', due: 'Aug 29, 2026', email: 'ops@pixelstudio.co' },
  { id: 'INV-2026-0038', client: 'CloudBridge Inc', amount: '$6,500.00', status: 'paid', date: 'Aug 10, 2026', due: 'Aug 24, 2026', email: 'ap@cloudbridge.com' },
  { id: 'INV-2026-0037', client: 'NovaTech Systems', amount: '$2,350.00', status: 'paid', date: 'Aug 5, 2026', due: 'Aug 19, 2026', email: 'accounts@novatech.io' },
  { id: 'INV-2026-0036', client: 'GrowthOps', amount: '$780.00', status: 'pending', date: 'Sep 8, 2026', due: 'Sep 22, 2026', email: 'pay@growthops.co' },
  { id: 'INV-2026-0035', client: 'BlueShift Analytics', amount: '$3,100.00', status: 'overdue', date: 'Jul 28, 2026', due: 'Aug 11, 2026', email: 'billing@blueshift.ai' },
  { id: 'INV-2026-0034', client: 'Orbital Labs', amount: '$12,000.00', status: 'paid', date: 'Jul 20, 2026', due: 'Aug 3, 2026', email: 'finance@orbitallabs.com' },
];

const statusConfig = {
  paid: { label: 'Paid', icon: CheckCircle, cls: 'text-green-700 bg-green-50 border-green-200' },
  pending: { label: 'Pending', icon: Clock, cls: 'text-amber-700 bg-amber-50 border-amber-200' },
  overdue: { label: 'Overdue', icon: AlertCircle, cls: 'text-red-700 bg-red-50 border-red-200' },
};

export default function Invoices() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [toast, setToast] = useState(null);
  const [billingAddress, setBillingAddress] = useState({street: '', city: '', country: ''});

  const filtered = mockInvoices.filter((inv) => {
    const matchSearch = inv.id.toLowerCase().includes(search.toLowerCase()) || inv.client.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === 'all' || inv.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  return (
    <div className="min-h-full">
      {/* Toast */}
      {toast && (
        <div className="fixed top-6 right-6 z-50 bg-gray-900 text-white text-sm px-4 py-3 rounded-xl shadow-xl flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-green-400" />
          {toast}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Invoices</h1>
          <p className="text-gray-500 text-sm mt-1">Manage and track all your invoices</p>
        </div>
        <button
          onClick={async () => {
            if (!Object.values(billingAddress).every(value => value.trim())) {
              showToast('Enter the customer street, city, and country before generating an invoice.');
              return;
            }
            try {
              const res = await fetch('http://localhost:8003/api/invoice/generate', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({billing_address: billingAddress}) });
              if (res.ok) {
                showToast('Invoice generation successful!');
              } else {
                const data = await res.json().catch(() => ({}));
                showToast(`Failed: ${data.detail || '422 Schema Mismatch'}`);
              }
            } catch (e) {
              showToast('Error: Could not connect to BFF');
            }
          }}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl transition-colors shadow-md shadow-indigo-100"
        >
          <Plus className="w-4 h-4" />
          Generate Invoice
        </button>
      </div>

      <div className="bg-white border rounded-xl p-4 mb-6">
        <p className="text-sm font-medium mb-3">Customer billing address for the new invoice</p>
        <div className="grid grid-cols-3 gap-3">
          {['street', 'city', 'country'].map(field => (
            <label key={field} className="text-sm capitalize">{field}
              <input required value={billingAddress[field]} onChange={event => setBillingAddress({...billingAddress, [field]: event.target.value})}
                className="block w-full border rounded-lg p-2 mt-1" />
            </label>
          ))}
        </div>
      </div>
      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Total Invoices', value: '8', color: 'text-gray-900' },
          { label: 'Paid', value: '4', color: 'text-green-600' },
          { label: 'Pending', value: '2', color: 'text-amber-600' },
          { label: 'Overdue', value: '2', color: 'text-red-600' },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
            <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Filter bar */}
      <div className="flex items-center gap-4 mb-5">
        <div className="relative flex-1 max-w-sm">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search invoices or clients..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="border border-gray-200 rounded-xl text-sm text-gray-700 px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
          >
            <option value="all">All Status</option>
            <option value="paid">Paid</option>
            <option value="pending">Pending</option>
            <option value="overdue">Overdue</option>
          </select>
        </div>
        <input
          type="date"
          className="border border-gray-200 rounded-xl text-sm text-gray-700 px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
        />
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50/80 border-b border-gray-100">
              <th className="text-left px-6 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wider">Invoice #</th>
              <th className="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wider">Client</th>
              <th className="text-right px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wider">Amount</th>
              <th className="text-center px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
              <th className="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wider">Issue Date</th>
              <th className="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wider">Due Date</th>
              <th className="text-center px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {filtered.map((inv) => {
              const { label, icon: Icon, cls } = statusConfig[inv.status];
              return (
                <tr key={inv.id} className="hover:bg-gray-50/50 transition-colors cursor-pointer">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2.5">
                      <FileText className="w-4 h-4 text-gray-400" />
                      <span className="text-sm font-mono text-gray-700">{inv.id}</span>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{inv.client}</p>
                      <p className="text-xs text-gray-400">{inv.email}</p>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-right">
                    <span className="text-sm font-bold text-gray-900">{inv.amount}</span>
                  </td>
                  <td className="px-4 py-4 text-center">
                    <span className={`inline-flex items-center gap-1 text-xs font-medium border px-2.5 py-0.5 rounded-full ${cls}`}>
                      <Icon className="w-3 h-3" />
                      {label}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-sm text-gray-600">{inv.date}</span>
                  </td>
                  <td className="px-4 py-4">
                    <span className={`text-sm ${inv.status === 'overdue' ? 'text-red-600 font-medium' : 'text-gray-600'}`}>{inv.due}</span>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center justify-center gap-2">
                      <button
                        onClick={() => showToast(`Viewing ${inv.id}`)}
                        className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-colors"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => showToast(`Downloading ${inv.id}`)}
                        className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-colors"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-gray-100 bg-gray-50/50">
          <p className="text-sm text-gray-500">Showing {filtered.length} of {mockInvoices.length} invoices</p>
          <div className="flex items-center gap-1">
            <button className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 disabled:opacity-40 transition-colors" disabled>
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button className="w-8 h-8 rounded-lg bg-indigo-600 text-white text-sm font-medium">1</button>
            <button className="w-8 h-8 rounded-lg hover:bg-gray-100 text-gray-700 text-sm font-medium transition-colors">2</button>
            <button className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
