import { useEffect, useState } from 'react';
import { Gauge } from 'lucide-react';
import { repairPresentation } from '../repair-state';

function CircularGauge({ score, isHealed }) {
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    if (!isHealed || score === 0) { setDisplayScore(0); return; }
    let current = 0;
    const step = Math.ceil(score / 40);
    const timer = setInterval(() => {
      current = Math.min(current + step, score);
      setDisplayScore(current);
      if (current >= score) clearInterval(timer);
    }, 40);
    return () => clearInterval(timer);
  }, [score, isHealed]);

  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const progress = (displayScore / 100) * circumference;
  const color = displayScore >= 80 ? '#10b981' : displayScore >= 50 ? '#f59e0b' : '#ef4444';

  return (
    <div className="flex flex-col items-center justify-center h-44">
      <svg viewBox="0 0 120 120" className="w-32 h-32">
        {/* Background circle */}
        <circle cx="60" cy="60" r={radius} fill="none" stroke="#f3f4f6" strokeWidth="10" />
        {/* Progress circle */}
        <circle
          cx="60" cy="60" r={radius} fill="none"
          stroke={isHealed ? color : '#e5e7eb'}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={`${isHealed ? progress : 0} ${circumference}`}
          transform="rotate(-90 60 60)"
          style={{ transition: 'stroke-dasharray 0.1s linear' }}
        />
        <text x="60" y="57" textAnchor="middle" fontSize="22" fontWeight="700" fill={isHealed ? color : '#9ca3af'}>
          {isHealed ? displayScore : '--'}
        </text>
        <text x="60" y="72" textAnchor="middle" fontSize="9" fill="#9ca3af">out of 100</text>
      </svg>
      <p className={`text-xs font-semibold mt-1 ${isHealed ? (displayScore >= 80 ? 'text-emerald-600' : 'text-amber-600') : 'text-gray-400'}`}>
        {isHealed ? (displayScore >= 80 ? 'High model confidence' : 'Review required') : 'Awaiting Agent Run'}
      </p>
    </div>
  );
}

export default function IpsScorePanel({ score, agentStatus }) {
  const isHealed = repairPresentation({agent_status: agentStatus, ips_score: score}).validated;

  return (
    <div className="flex flex-col p-5 max-w-sm w-full mx-auto items-center">
      <div className="flex items-center gap-2 mb-6 w-full justify-center">
        <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center">
          <Gauge className="w-4 h-4 text-emerald-600" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-gray-900">Intent Preservation Score</h3>
          <p className="text-xs text-gray-500">LLM-as-a-judge validation</p>
        </div>
      </div>

      {score === null || score === undefined ? (
        <p className="text-sm text-gray-500 py-12">Judge score unavailable. Consult the actual test results.</p>
      ) : <CircularGauge score={score} isHealed={isHealed} />}

      <div className="mt-6 space-y-2 text-xs text-gray-500 w-full flex flex-col items-center">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
          <span>80-100: High model confidence</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" />
          <span>50-79: Moderate model confidence</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-red-400 inline-block" />
          <span>0-49: Low model confidence</span>
        </div>
      </div>
    </div>
  );
}
