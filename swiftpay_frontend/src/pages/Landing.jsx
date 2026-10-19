import { useNavigate } from 'react-router-dom';
import {
  Zap,
  Shield,
  Activity,
  Rocket,
  ArrowRight,
  CheckCircle,
  TrendingUp,
  Clock,
  Globe,
  ChevronRight,
} from 'lucide-react';

export default function Landing() {
  const navigate = useNavigate();

  const features = [
    {
      icon: Shield,
      title: 'Intent-Aware Healing',
      desc: 'Our AI understands the intent of every API call and automatically adapts to schema changes, preventing 422 errors before they reach your customers.',
      color: 'text-indigo-600',
      bg: 'bg-indigo-50',
    },
    {
      icon: Activity,
      title: 'Real-time API Monitoring',
      desc: 'Monitor every API endpoint in real time. Get instant alerts on schema drift, latency spikes, and breaking changes across all your integrations.',
      color: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      icon: Rocket,
      title: 'Zero-downtime Deployments',
      desc: 'Deploy new API versions without downtime. SwiftPay mediates between versions so your payment flows never break during migrations.',
      color: 'text-violet-600',
      bg: 'bg-violet-50',
    },
  ];

  const stats = [
    { value: '$2.4B', label: 'Processed' },
    { value: '99.99%', label: 'Uptime' },
    { value: '12ms', label: 'Avg Latency' },
    { value: '5,600+', label: 'Businesses' },
  ];

  return (
    <div className="min-h-screen bg-white font-sans">
      {/* Announcement bar */}
      <div className="bg-gradient-to-r from-indigo-600 to-blue-600 text-white text-center py-2.5 px-4 text-sm font-medium">
        <span className="opacity-90">🚀 SwiftPay — Now with AI-powered self-healing API resilience.</span>
        <span className="ml-1 font-semibold">No more 422 errors.</span>
        <button className="ml-3 text-white/80 hover:text-white inline-flex items-center gap-0.5 text-xs underline underline-offset-2">
          Learn more <ChevronRight className="w-3 h-3" />
        </button>
      </div>

      {/* Navbar */}
      <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-gray-100 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Zap className="w-4.5 h-4.5 text-white" strokeWidth={2.5} />
            </div>
            <span className="font-bold text-xl text-gray-900 tracking-tight">SwiftPay</span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            {['Features', 'Pricing', 'Docs', 'Blog'].map((item) => (
              <a key={item} href="#" className="text-sm text-gray-600 hover:text-gray-900 font-medium transition-colors">
                {item}
              </a>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-sm text-gray-700 hover:text-gray-900 font-medium px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              Log in
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="text-sm text-white font-medium px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 transition-colors shadow-sm shadow-indigo-200"
            >
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-6 pt-24 pb-20 text-center">
        <div className="inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 text-xs font-semibold px-3 py-1.5 rounded-full mb-6 border border-indigo-100">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse"></span>
          AI-Powered Payment Infrastructure
        </div>

        <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 tracking-tight leading-tight mb-6">
          Intelligent Payments.
          <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-blue-500">
            Self-Healing APIs.
          </span>
        </h1>

        <p className="text-xl text-gray-500 max-w-2xl mx-auto mb-10 leading-relaxed">
          SwiftPay's AI-powered infrastructure detects breaking API changes in real time and self-heals
          your payment flows — so your business never loses revenue to a 422 error again.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-5">
          <input
            type="email"
            placeholder="Enter your work email"
            className="w-full sm:w-72 px-4 py-3 rounded-xl border border-gray-200 text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent shadow-sm"
          />
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl transition-colors shadow-md shadow-indigo-200"
          >
            Start for Free
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center justify-center gap-2 text-sm text-gray-400">
          <CheckCircle className="w-4 h-4 text-green-500" />
          No credit card required — Free tier available
        </div>

        {/* Hero visual */}
        <div className="mt-16 relative">
          <div className="bg-gradient-to-b from-gray-900 to-slate-800 rounded-2xl p-6 shadow-2xl max-w-4xl mx-auto border border-gray-700">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-3 h-3 rounded-full bg-red-400"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
              <div className="w-3 h-3 rounded-full bg-green-400"></div>
              <span className="ml-3 text-gray-500 text-xs font-mono">swiftpay — payments dashboard</span>
            </div>
            <div className="grid grid-cols-4 gap-4 mb-6">
              {[
                { label: 'Total Volume', value: '$12,450', change: '+2.4%', color: 'text-green-400' },
                { label: 'Transactions', value: '1,284', change: '+12.1%', color: 'text-green-400' },
                { label: 'Success Rate', value: '99.8%', change: '+0.2%', color: 'text-green-400' },
                { label: 'API Errors', value: '0', change: 'Healed', color: 'text-indigo-400' },
              ].map((stat) => (
                <div key={stat.label} className="bg-slate-700/50 rounded-xl p-4 border border-slate-600">
                  <p className="text-slate-400 text-xs mb-1">{stat.label}</p>
                  <p className="text-white font-bold text-xl">{stat.value}</p>
                  <p className={`text-xs mt-1 ${stat.color}`}>{stat.change}</p>
                </div>
              ))}
            </div>
            <div className="bg-green-900/30 border border-green-700/50 rounded-lg px-4 py-2.5 flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
              <span className="text-green-300 text-xs font-medium">NexusPay API v1 — All systems operational. AI self-healing active.</span>
            </div>
          </div>
          <div className="absolute inset-0 bg-gradient-to-t from-white via-transparent to-transparent rounded-2xl pointer-events-none"></div>
        </div>
      </section>

      {/* Features */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Built for payment reliability</h2>
            <p className="text-gray-500 max-w-xl mx-auto">Three layers of AI-powered protection keep your payment infrastructure running — no matter what changes your API providers make.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((f) => (
              <div key={f.title} className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                <div className={`w-12 h-12 ${f.bg} rounded-xl flex items-center justify-center mb-5`}>
                  <f.icon className={`w-6 h-6 ${f.color}`} />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">{f.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 bg-white border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((s) => (
              <div key={s.label} className="text-center">
                <p className="text-4xl font-extrabold text-indigo-600 mb-1">{s.value}</p>
                <p className="text-gray-500 text-sm font-medium">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-indigo-600 py-20">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <TrendingUp className="w-10 h-10 text-indigo-200 mx-auto mb-5" />
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to eliminate API downtime?
          </h2>
          <p className="text-indigo-200 mb-8 max-w-xl mx-auto">
            Join 5,600+ businesses that trust SwiftPay to keep their payment flows running — even when their API providers break things.
          </p>
          <button
            onClick={() => navigate('/dashboard')}
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-indigo-600 font-semibold rounded-xl hover:bg-indigo-50 transition-colors shadow-lg"
          >
            Get Started Free
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 bg-indigo-500 rounded-lg flex items-center justify-center">
                <Zap className="w-4 h-4 text-white" strokeWidth={2.5} />
              </div>
              <span className="text-white font-bold text-base">SwiftPay</span>
            </div>
            <div className="flex items-center gap-6 text-sm">
              {['Privacy', 'Terms', 'Security', 'Status', 'Contact'].map((link) => (
                <a key={link} href="#" className="hover:text-white transition-colors">{link}</a>
              ))}
            </div>
            <p className="text-xs text-gray-600">© 2026 SwiftPay, Inc. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
