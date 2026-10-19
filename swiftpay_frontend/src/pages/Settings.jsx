import { useState } from 'react';
import {
  User,
  Lock,
  Bell,
  Key,
  CreditCard,
  CheckCircle,
  Eye,
  EyeOff,
  Copy,
  RefreshCw,
  ExternalLink,
  Loader2,
  Shield,
  Zap,
} from 'lucide-react';

const tabs = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'security', label: 'Security', icon: Lock },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'apikeys', label: 'API Keys', icon: Key },
  { id: 'billing', label: 'Billing', icon: CreditCard },
];

const BFF_URL = 'http://localhost:8003';

export default function Settings() {
  const [activeTab, setActiveTab] = useState('profile');
  const [showKey, setShowKey] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [toast, setToast] = useState(null);
  const [notifs, setNotifs] = useState({
    paymentSuccess: true,
    paymentFailed: true,
    apiDown: true,
    weeklyReport: false,
    marketing: false,
  });

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const testConnection = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await fetch(`${BFF_URL}/api/transactions`);
      if (res.ok) {
        setTestResult('healthy');
        showToast('NexusPay API connection verified — healthy');
      } else {
        setTestResult('error');
        showToast('Connection test failed — API returned error', 'error');
      }
    } catch {
      setTestResult('error');
      showToast('Cannot reach BFF — is it running on :8003?', 'error');
    } finally {
      setTesting(false);
    }
  };

  const copyKey = (key) => {
    navigator.clipboard.writeText(key);
    showToast('API key copied to clipboard');
  };

  return (
    <div className="min-h-full">
      {/* Toast */}
      {toast && (
        <div className={`fixed top-6 right-6 z-50 text-sm px-4 py-3 rounded-xl shadow-xl flex items-center gap-2 ${toast.type === 'error' ? 'bg-red-600 text-white' : 'bg-gray-900 text-white'}`}>
          <CheckCircle className="w-4 h-4 text-green-400" />
          {toast.msg}
        </div>
      )}

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 text-sm mt-1">Manage your account, security, and integrations</p>
      </div>

      <div className="flex gap-8">
        {/* Tab sidebar */}
        <div className="w-52 shrink-0">
          <nav className="space-y-0.5">
            {tabs.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  activeTab === id
                    ? 'bg-indigo-50 text-indigo-700 border border-indigo-100'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                {label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab content */}
        <div className="flex-1 max-w-2xl">
          {/* Profile tab */}
          {activeTab === 'profile' && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
              <h2 className="font-semibold text-gray-900 text-lg mb-6">Profile Information</h2>

              {/* Avatar */}
              <div className="flex items-center gap-5 mb-8 pb-8 border-b border-gray-100">
                <div className="w-20 h-20 rounded-full bg-indigo-600 flex items-center justify-center text-white text-3xl font-bold">S</div>
                <div>
                  <p className="font-medium text-gray-900 mb-1">Profile Photo</p>
                  <p className="text-sm text-gray-500 mb-3">JPG, GIF or PNG. Max 2MB.</p>
                  <button className="text-sm text-indigo-600 font-medium hover:text-indigo-700 border border-indigo-200 px-3 py-1.5 rounded-lg transition-colors">
                    Upload Photo
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-5">
                {[
                  { label: 'Full Name', value: 'Surjith K', type: 'text' },
                  { label: 'Email Address', value: 'surjith@swiftpay.io', type: 'email' },
                  { label: 'Phone Number', value: '+91 98765 43210', type: 'tel' },
                  { label: 'Company', value: 'SwiftPay Inc.', type: 'text' },
                ].map((field) => (
                  <div key={field.label}>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">{field.label}</label>
                    <input
                      type={field.type}
                      defaultValue={field.value}
                      className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                ))}
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Bio</label>
                  <textarea
                    defaultValue="Building SwiftPay — AI-powered payment infrastructure."
                    rows={3}
                    className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                  />
                </div>
              </div>

              <div className="flex justify-end mt-6 pt-6 border-t border-gray-50">
                <button
                  onClick={() => showToast('Profile saved successfully!')}
                  className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl transition-colors"
                >
                  Save Changes
                </button>
              </div>
            </div>
          )}

          {/* Security tab */}
          {activeTab === 'security' && (
            <div className="space-y-5">
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
                <h2 className="font-semibold text-gray-900 text-lg mb-6">Change Password</h2>
                <div className="space-y-4">
                  {['Current Password', 'New Password', 'Confirm New Password'].map((label) => (
                    <div key={label}>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">{label}</label>
                      <input
                        type="password"
                        placeholder="••••••••"
                        className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>
                  ))}
                  <button
                    onClick={() => showToast('Password updated!')}
                    className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl transition-colors mt-2"
                  >
                    Update Password
                  </button>
                </div>
              </div>
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">Two-Factor Authentication</h3>
                    <p className="text-sm text-gray-500 mt-1">Add an extra layer of security to your account</p>
                  </div>
                  <button className="px-4 py-2 border border-indigo-200 text-indigo-600 text-sm font-medium rounded-xl hover:bg-indigo-50 transition-colors">
                    Enable 2FA
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Notifications tab */}
          {activeTab === 'notifications' && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
              <h2 className="font-semibold text-gray-900 text-lg mb-6">Notification Preferences</h2>
              <div className="space-y-0">
                {[
                  { key: 'paymentSuccess', label: 'Payment Successful', desc: 'Get notified when a payment completes' },
                  { key: 'paymentFailed', label: 'Payment Failed', desc: 'Get notified when a payment fails or errors' },
                  { key: 'apiDown', label: 'API Health Alerts', desc: 'Alert when API status changes or healing triggers' },
                  { key: 'weeklyReport', label: 'Weekly Report', desc: 'Weekly summary of transactions and spending' },
                  { key: 'marketing', label: 'Product Updates', desc: 'News, announcements and feature releases' },
                ].map(({ key, label, desc }) => (
                  <div key={key} className="flex items-center justify-between py-5 border-b border-gray-50 last:border-0">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{label}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{desc}</p>
                    </div>
                    <button
                      onClick={() => setNotifs((n) => ({ ...n, [key]: !n[key] }))}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${notifs[key] ? 'bg-indigo-600' : 'bg-gray-200'}`}
                    >
                      <span className={`inline-block h-4 w-4 rounded-full bg-white shadow transition-transform ${notifs[key] ? 'translate-x-6' : 'translate-x-1'}`} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* API Keys tab */}
          {activeTab === 'apikeys' && (
            <div className="space-y-5">
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center">
                    <Zap className="w-5 h-5 text-indigo-600" />
                  </div>
                  <div>
                    <h2 className="font-semibold text-gray-900 text-lg">NexusPay Integration</h2>
                    <p className="text-sm text-gray-500">SwiftPay connects to NexusPay for payment processing</p>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-xl border border-gray-200 p-5 mb-5">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-500 mb-1 font-medium uppercase tracking-wider">API Endpoint</p>
                      <p className="text-sm font-mono text-gray-800">http://localhost:8003</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1 font-medium uppercase tracking-wider">API Version</p>
                      <span className="inline-flex items-center gap-1.5 text-sm font-mono text-indigo-700 bg-indigo-50 border border-indigo-200 px-2 py-0.5 rounded-md">
                        v1
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                      </span>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1 font-medium uppercase tracking-wider">Environment</p>
                      <span className="text-sm font-medium text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-md">Sandbox</span>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1 font-medium uppercase tracking-wider">Self-Healing</p>
                      <span className="text-sm font-medium text-green-700 bg-green-50 border border-green-200 px-2 py-0.5 rounded-md">Enabled</span>
                    </div>
                  </div>
                </div>

                {/* Test Connection */}
                <div className="flex items-center gap-3 mb-5">
                  <button
                    onClick={testConnection}
                    disabled={testing}
                    className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-70 text-white text-sm font-semibold rounded-xl transition-colors"
                  >
                    {testing ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                    {testing ? 'Testing...' : 'Test Connection'}
                  </button>
                  {testResult === 'healthy' && (
                    <div className="flex items-center gap-1.5 text-green-700 text-sm font-medium">
                      <CheckCircle className="w-4 h-4" />
                      Connected — API healthy
                    </div>
                  )}
                  {testResult === 'error' && (
                    <div className="flex items-center gap-1.5 text-red-600 text-sm font-medium">
                      Connection failed
                    </div>
                  )}
                </div>

                <a
                  href="http://localhost:5173/agent"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-700 font-medium border border-indigo-200 px-4 py-2 rounded-xl hover:bg-indigo-50 transition-colors"
                >
                  Open APIShield Dashboard <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>

              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
                <h2 className="font-semibold text-gray-900 mb-5">SwiftPay API Keys</h2>
                <div className="space-y-4">
                  {[
                    { label: 'Live Secret Key', key: 'sk_live_swiftpay_4xT9...mNk2', masked: true },
                    { label: 'Publishable Key', key: 'pk_live_swiftpay_7bY3...qWx8', masked: false },
                  ].map(({ label, key, masked }) => (
                    <div key={label}>
                      <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">{label}</label>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 flex items-center bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 gap-3">
                          <Shield className="w-4 h-4 text-gray-400 shrink-0" />
                          <span className="text-sm font-mono text-gray-700 flex-1">
                            {masked && !showKey ? '••••••••••••••••••••••••••••••' : key}
                          </span>
                          {masked && (
                            <button onClick={() => setShowKey(!showKey)} className="text-gray-400 hover:text-gray-600">
                              {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </button>
                          )}
                        </div>
                        <button
                          onClick={() => copyKey(key)}
                          className="p-2.5 border border-gray-200 rounded-xl hover:bg-gray-50 text-gray-500 hover:text-gray-700 transition-colors"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Billing tab */}
          {activeTab === 'billing' && (
            <div className="space-y-5">
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
                <h2 className="font-semibold text-gray-900 text-lg mb-6">Current Plan</h2>
                <div className="flex items-center justify-between p-5 bg-indigo-50 rounded-xl border border-indigo-100 mb-5">
                  <div>
                    <p className="font-bold text-indigo-900 text-lg">SwiftPay Enterprise</p>
                    <p className="text-indigo-600 text-sm mt-0.5">$299 / month · Billed annually</p>
                  </div>
                  <span className="bg-indigo-600 text-white text-xs font-semibold px-3 py-1 rounded-full">Active</span>
                </div>
                <div className="grid grid-cols-3 gap-3 mb-5">
                  {[
                    { label: 'API Calls', value: '2.4M / 10M' },
                    { label: 'Next Invoice', value: 'Oct 11, 2026' },
                    { label: 'Seats', value: '3 / 10 used' },
                  ].map((item) => (
                    <div key={item.label} className="bg-gray-50 rounded-xl p-4 border border-gray-100 text-center">
                      <p className="text-sm font-bold text-gray-900">{item.value}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{item.label}</p>
                    </div>
                  ))}
                </div>
                <button
                  onClick={() => showToast('Redirecting to billing portal...')}
                  className="w-full py-2.5 border border-gray-200 rounded-xl text-sm text-gray-700 hover:bg-gray-50 transition-colors font-medium"
                >
                  Manage Billing & Invoices
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
