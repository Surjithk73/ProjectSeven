import { CheckCircle, AlertTriangle, Loader, Zap } from 'lucide-react';

const configs = {
  healthy:  { label: 'System Healthy',     color: 'bg-emerald-50 text-emerald-700 ring-emerald-200',  dot: 'bg-emerald-500', icon: CheckCircle },
  broken:   { label: 'Break Detected',     color: 'bg-red-50 text-red-700 ring-red-200',              dot: 'bg-red-500',     icon: AlertTriangle },
  healing:  { label: 'Agent Healing...',   color: 'bg-amber-50 text-amber-700 ring-amber-200',        dot: 'bg-amber-500',   icon: Loader },
  healed:   { label: 'Self-Healed!',       color: 'bg-indigo-50 text-indigo-700 ring-indigo-200',     dot: 'bg-indigo-500',  icon: Zap },
};

export default function StatusBar({ status }) {
  const cfg = configs[status] || configs.healthy;
  const Icon = cfg.icon;
  return (
    <div className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium ring-1 ${cfg.color}`}>
      <span className={`w-2 h-2 rounded-full ${cfg.dot} ${status === 'healing' ? 'animate-pulse' : ''}`} />
      <Icon className={`w-4 h-4 ${status === 'healing' ? 'animate-spin' : ''}`} />
      {cfg.label}
    </div>
  );
}
